import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()


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
    conn = _conectar()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios")
        filas = _filas_a_dicts(cur)
        return {f["id"]: {k: v for k, v in f.items() if k != "id"} for f in filas}
    finally:
        conn.close()


def guardar_usuarios(datos):
    """Reemplaza el estado completo de usuarios: upsert de todos los presentes
    en 'datos' y elimina los que ya no estan (igual que el guardado por
    sobre-escritura total que se hacia antes con el .json).

    Lanza UsuarioConHistorialError si se intenta eliminar un usuario que
    todavia tiene filas asociadas en otras tablas (logs, chat, promociones,
    entregas) — Postgres lo bloquea por llave foranea en vez de dejar
    registros huerfanos sueltos como hacia el JSON."""
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
    """Guarda acciones realizadas por administradores"""
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
    """Guarda canjes procesados por tiendas"""
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
    """Guarda actividad de clientes/vecinos (Abonos por reciclaje, compras, etc)"""
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
    return _cargar_tabla("promociones", orden="id")


def guardar_promociones(lista_promos):
    """Reemplaza el estado completo de promociones: upsert de cada item
    presente (si trae 'id' se actualiza esa fila, si no, se inserta una
    nueva) y elimina las que ya no estan en la lista — igual semantica de
    sobre-escritura total que 'guardar_usuarios', necesaria porque
    negocio.py depende de que una promo agotada o borrada desaparezca de
    verdad de la tabla, no solo de la lista en memoria."""
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
    """Elimina una promoción desde el panel de administración y notifica a la tienda."""
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


# --- CHAT USUARIO A DESARROLLADORES/ADMINS ---

def cargar_mensajes_chat():
    return _cargar_tabla("chat")


def guardar_mensaje_chat(dni_cliente, autor_nombre, rol_autor, mensaje):
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
    """Marca como leídos los mensajes pendientes según quién los esté leyendo."""
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
    """Calcula el total de puntos extraidos/canjeados por una tienda especifica."""
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


# --- FUNCIONES DE REGISTRO DE ENTREGAS DE RECICLAJE ---

def registrar_entrega_reciclaje(tienda_id, dni_cliente, material, peso_kg, puntos):
    """Registra una entrega física de reciclaje en la tabla entregas."""
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
    """Carga todas las entregas de reciclaje registradas."""
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
    """
    Calcula dinámicamente el total de CO2 evitado sumando las entregas registradas
    del vecino según los factores WARM de la EPA.
    """
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
