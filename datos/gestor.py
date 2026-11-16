import json
import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Detectar si estamos en modo local usando JSON o en producción con PostgreSQL
MODO_LOCAL = os.getenv("MODO_LOCAL", "False").lower() in ("true", "1", "t", "yes")

# Rutas para el modo local si está activado
DIR_ARCHIVO = os.path.join(os.path.dirname(__file__), "_archivo")


def _leer_json(nombre_archivo):
    ruta = os.path.join(DIR_ARCHIVO, nombre_archivo)
    if not os.path.exists(ruta):
        return [] if "usuarios" not in nombre_archivo else {}
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] if "usuarios" not in nombre_archivo else {}


def _escribir_json(nombre_archivo, datos):
    ruta = os.path.join(DIR_ARCHIVO, nombre_archivo)
    os.makedirs(DIR_ARCHIVO, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


class UsuarioConHistorialError(Exception):
    """Se lanza al intentar eliminar un usuario que tiene filas asociadas
    en otras tablas (logs, chat, promociones, entregas)."""
    pass


def _conectar():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def _filas_a_dicts(cur):
    columnas = [desc[0] for desc in cur.description]
    return [dict(zip(columnas, fila)) for fila in cur.fetchall()]


def _a_numero_o_none(valor):
    """Normaliza campos numéricos que en el JSON viejo podían ser 'N/A' o texto suelto."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


# --- USUARIOS ---

def cargar_usuarios():
    if MODO_LOCAL:
        return _leer_json("usuarios.json")
    
    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios")
        filas = _filas_a_dicts(cur)
        return {f["id"]: {k: v for k, v in f.items() if k != "id"} for f in filas}
    finally:
        conn.close()


def guardar_usuarios(datos):
    if MODO_LOCAL:
        _escribir_json("usuarios.json", datos)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        ids_actuales = list(datos.keys())
        if ids_actuales:
            cur.execute("DELETE FROM usuarios WHERE id != ALL(%s)", (ids_actuales,))
        else:
            cur.execute("DELETE FROM usuarios")

        for uid, u in datos.items():
            cur.execute(
                """
                INSERT INTO usuarios
                    (id, rol, nombre, correo, clave, telefono, puntos,
                     suspendido, motivo_suspension, justificacion_cliente,
                     pregunta_secreta, respuesta_secreta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    rol = EXCLUDED.rol,
                    nombre = EXCLUDED.nombre,
                    correo = EXCLUDED.correo,
                    clave = EXCLUDED.clave,
                    telefono = EXCLUDED.telefono,
                    puntos = EXCLUDED.puntos,
                    suspendido = EXCLUDED.suspendido,
                    motivo_suspension = EXCLUDED.motivo_suspension,
                    justificacion_cliente = EXCLUDED.justificacion_cliente,
                    pregunta_secreta = EXCLUDED.pregunta_secreta,
                    respuesta_secreta = EXCLUDED.respuesta_secreta
                """,
                (
                    uid,
                    u.get("rol"),
                    u.get("nombre"),
                    u.get("correo"),
                    u.get("clave"),
                    u.get("telefono"),
                    _a_numero_o_none(u.get("puntos")),
                    u.get("suspendido", False),
                    u.get("motivo_suspension", ""),
                    u.get("justificacion_cliente", ""),
                    u.get("pregunta_secreta"),
                    u.get("respuesta_secreta"),
                ),
            )
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation as e:
        conn.rollback()
        detalle = (e.diag.message_detail or "").strip()
        raise UsuarioConHistorialError(
            "No se puede eliminar: el usuario tiene historial de actividad registrado "
            "(compras, chats, promociones o entregas).\n" + detalle
        )
    finally:
        conn.close()


# --- FUNCIONES DE REGISTRO / AUDITORÍA ---

def registrar_accion_dev(id_dev, nombre_dev, accion, objetivo):
    if MODO_LOCAL:
        logs = _leer_json("log_desarrolladores.json")
        logs.append({"fecha": str(datetime.now()), "autor_id": id_dev, "autor_nombre": nombre_dev, "accion": accion, "objetivo": objetivo})
        _escribir_json("log_desarrolladores.json", logs)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO log_desarrolladores (fecha, autor_id, autor_nombre, accion, objetivo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (datetime.now(), id_dev, nombre_dev, accion, objetivo),
        )
        conn.commit()
    finally:
        conn.close()


def registrar_accion_tienda(id_tienda, nombre_tienda, dni_cliente, puntos_canjeados):
    if MODO_LOCAL:
        logs = _leer_json("log_tiendas.json")
        logs.append({"fecha": str(datetime.now()), "tienda_id": id_tienda, "tienda_nombre": nombre_tienda, "dni_cliente": dni_cliente, "puntos_descontados": puntos_canjeados})
        _escribir_json("log_tiendas.json", logs)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO log_tiendas (fecha, tienda_id, tienda_nombre, dni_cliente, puntos_descontados)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (datetime.now(), id_tienda, nombre_tienda, dni_cliente, puntos_canjeados),
        )
        conn.commit()
    finally:
        conn.close()


def registrar_accion_cliente(dni_cliente, tipo_operacion, puntos, detalle):
    if MODO_LOCAL:
        logs = _leer_json("log_clientes.json")
        logs.append({"fecha": str(datetime.now()), "dni_cliente": dni_cliente, "tipo": tipo_operacion, "puntos": puntos, "detalle": detalle})
        _escribir_json("log_clientes.json", logs)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO log_clientes (fecha, dni_cliente, tipo, puntos, detalle)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (datetime.now(), dni_cliente, tipo_operacion, puntos, detalle),
        )
        conn.commit()
    finally:
        conn.close()


def _cargar_tabla(nombre_tabla, orden="fecha"):
    if MODO_LOCAL:
        return _leer_json(f"{nombre_tabla}.json")

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {nombre_tabla} ORDER BY {orden}")
        return _filas_a_dicts(cur)
    finally:
        conn.close()


def cargar_log_devs():
    return _cargar_tabla("log_desarrolladores")


def cargar_log_tiendas():
    return _cargar_tabla("log_tiendas")


def cargar_log_clientes():
    return _cargar_tabla("log_clientes")


# --- PROMOCIONES ---

def cargar_promociones():
    return _cargar_tabla("promociones")


def guardar_promociones(lista_promos):
    if MODO_LOCAL:
        _escribir_json("promociones.json", lista_promos)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        ids_actuales = [p["id"] for p in lista_promos if p.get("id") is not None]
        if ids_actuales:
            cur.execute("DELETE FROM promociones WHERE id != ALL(%s)", (ids_actuales,))
        else:
            cur.execute("DELETE FROM promociones")

        for p in lista_promos:
            if p.get("id") is not None:
                cur.execute(
                    """
                    UPDATE promociones SET
                        tienda_id = %s, tienda_nombre = %s, titulo = %s, categoria = %s,
                        descripcion = %s, precio_soles = %s, puntos = %s, foto = %s, stock = %s
                    WHERE id = %s
                    """,
                    (
                        p.get("tienda_id"), p.get("tienda_nombre"), p.get("titulo"), p.get("categoria"),
                        p.get("descripcion"), p.get("precio_soles"), p.get("puntos"), p.get("foto"),
                        p.get("stock"), p["id"],
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO promociones
                        (tienda_id, tienda_nombre, titulo, categoria, descripcion, precio_soles, puntos, foto, stock)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        p.get("tienda_id"), p.get("tienda_nombre"), p.get("titulo"), p.get("categoria"),
                        p.get("descripcion"), p.get("precio_soles"), p.get("puntos"), p.get("foto"),
                        p.get("stock"),
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def eliminar_promocion_admin(id_promo, id_tienda, motivo, autor_admin):
    if MODO_LOCAL:
        promos = _leer_json("promociones.json")
        encontrada = None
        nuevas_promos = []
        for p in promos:
            if p.get("id") == id_promo:
                encontrada = p
            else:
                nuevas_promos.append(p)
        if not encontrada:
            return False
        _escribir_json("promociones.json", nuevas_promos)
        guardar_mensaje_chat(
            dni_cliente=str(id_tienda),
            autor_nombre=autor_admin,
            rol_autor="admin",
            mensaje=f"🚨 AVISO DE SISTEMA: Su oferta '{encontrada.get('titulo')}' ha sido ELIMINADA por administración.\nMotivo: {motivo}"
        )
        return True

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute("SELECT titulo FROM promociones WHERE id = %s", (id_promo,))
        fila = cur.fetchone()
        if not fila:
            return False
        titulo = fila[0]
        cur.execute("DELETE FROM promociones WHERE id = %s", (id_promo,))
        conn.commit()

        guardar_mensaje_chat(
            dni_cliente=str(id_tienda),
            autor_nombre=autor_admin,
            rol_autor="admin",
            mensaje=f"🚨 AVISO DE SISTEMA: Su oferta '{titulo}' ha sido ELIMINADA por administración.\nMotivo: {motivo}"
        )
        return True
    finally:
        conn.close()


# --- CHAT ---

def cargar_mensajes_chat():
    return _cargar_tabla("chat")


def guardar_mensaje_chat(dni_cliente, autor_nombre, rol_autor, mensaje):
    if MODO_LOCAL:
        chat = _leer_json("chat.json")
        chat.append({
            "fecha": str(datetime.now()),
            "dni_cliente": dni_cliente,
            "autor": autor_nombre,
            "rol": rol_autor,
            "mensaje": mensaje,
            "leido": False
        })
        _escribir_json("chat.json", chat)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chat (fecha, dni_cliente, autor, rol, mensaje, leido)
            VALUES (%s, %s, %s, %s, %s, FALSE)
            """,
            (datetime.now(), dni_cliente, autor_nombre, rol_autor, mensaje),
        )
        conn.commit()
    finally:
        conn.close()


def marcar_chat_como_leido(dni_cliente, rol_lector):
    if MODO_LOCAL:
        chat = _leer_json("chat.json")
        for m in chat:
            if m.get("dni_cliente") == dni_cliente:
                if rol_lector in ["admin", "desarrollador", "gestor de reciclaje", "gestor"] and m.get("rol") == "vecino":
                    m["leido"] = True
                elif rol_lector == "vecino" and m.get("rol") in ('admin', 'desarrollador', 'gestor de reciclaje', 'gestor'):
                    m["leido"] = True
        _escribir_json("chat.json", chat)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        if rol_lector in ["admin", "desarrollador", "gestor de reciclaje", "gestor"]:
            cur.execute(
                """
                UPDATE chat SET leido = TRUE
                WHERE dni_cliente = %s AND rol = 'vecino' AND leido = FALSE
                """,
                (dni_cliente,),
            )
        elif rol_lector == "vecino":
            cur.execute(
                """
                UPDATE chat SET leido = TRUE
                WHERE dni_cliente = %s AND rol IN ('admin', 'desarrollador', 'gestor de reciclaje', 'gestor') AND leido = FALSE
                """,
                (dni_cliente,),
            )
        conn.commit()
    finally:
        conn.close()


def obtener_puntos_recolectados_por_tienda(id_tienda):
    if MODO_LOCAL:
        logs = _leer_json("log_tiendas.json")
        total = sum(float(l.get("puntos_descontados", 0)) for l in logs if str(l.get("tienda_id")) == str(id_tienda))
        return round(float(total), 1)

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(SUM(puntos_descontados), 0) FROM log_tiendas WHERE tienda_id = %s",
            (str(id_tienda),),
        )
        total = cur.fetchone()[0]
        return round(float(total), 1)
    finally:
        conn.close()


# --- ENTREGAS DE RECICLAJE ---

def registrar_entrega_reciclaje(tienda_id, dni_cliente, material, peso_kg, puntos):
    if MODO_LOCAL:
        entregas = _leer_json("entregas.json")
        entregas.append({
            "fecha": str(datetime.now()),
            "tienda_id": str(tienda_id),
            "dni_cliente": str(dni_cliente),
            "material": str(material),
            "peso_kg": float(peso_kg),
            "puntos": int(puntos)
        })
        _escribir_json("entregas.json", entregas)
        return

    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO entregas (fecha, tienda_id, dni_cliente, material, peso_kg, puntos)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (datetime.now(), str(tienda_id), str(dni_cliente), str(material), float(peso_kg), int(puntos)),
        )
        conn.commit()
    finally:
        conn.close()


def cargar_entregas_reciclaje():
    return _cargar_tabla("entregas")


# --- CÁLCULO DE CO2 ---

CO2_POR_KG = {
    "Botellas PET (Agua/Gaseosas)": 1.53,
    "Tapas plásticas (PP/HDPE)": 1.40,
    "Cartón corrugado (Cajas)": 3.12,
    "Papel de cuaderno blanco": 2.85,
    "Cuadernos usados / Impresos": 2.85,
    "Papel periódico": 2.70,
    "Revistas (Papel couche/brillante)": 2.70,
    "Latas de aluminio (Gaseosas/Cerveza)": 9.11,
    "Latas de conservas (Hojalata/Fierro)": 1.81,
    "Cables viejos (Cobre/Plástico)": 4.50,
    "Componentes informáticos": 5.20
}


def calcular_co2_evitado_vecino(id_usuario):
    entregas = cargar_entregas_reciclaje()
    co2_total = 0.0

    for entrega in entregas:
        usr_id = str(entrega.get("id_usuario", entrega.get("dni_cliente", "")))
        if usr_id == str(id_usuario):
            material_reg = str(entrega.get("material", "")).strip()

            try:
                peso_kg = float(entrega.get("peso_kg", entrega.get("peso", 0.0)))
            except (ValueError, TypeError):
                peso_kg = 0.0

            factor = CO2_POR_KG.get(material_reg, None)
            if factor is None:
                for mat_clave, f_val in CO2_POR_KG.items():
                    if mat_clave.lower() in material_reg.lower() or material_reg.lower() in mat_clave.lower():
                        factor = f_val
                        break
                if factor is None:
                    factor = 1.5

            co2_total += peso_kg * factor

    return round(co2_total, 2)