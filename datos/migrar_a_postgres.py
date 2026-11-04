"""
Script de migracion UNICA (one-shot): lee los JSON archivados en
datos/_archivo/ (el estado de los datos justo antes de migrar a Postgres) y
los inserta en las tablas creadas con datos/schema.sql.

Ya se corrio una vez contra la base de produccion del equipo. Se deja aqui
como referencia y por si hace falta recrear la base desde cero
(por ejemplo, en un proyecto nuevo de Supabase):
    python datos/migrar_a_postgres.py

No se importa desde ninguna interfaz de la app.
"""
import json
import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()

RUTA_DATOS = os.path.join(os.path.dirname(__file__), "_archivo")


def conectar():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def cargar_json(nombre):
    ruta = os.path.join(RUTA_DATOS, nombre)
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def a_fecha(valor):
    return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")


def a_numero_o_none(valor):
    """Normaliza 'puntos' en usuarios.json: puede ser int, float, 'N/A' o estar ausente."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None  # cubre el caso "N/A"


def tabla_vacia(cur, nombre_tabla):
    cur.execute(f"SELECT COUNT(*) FROM {nombre_tabla};")
    return cur.fetchone()[0] == 0


def migrar_usuarios(cur):
    usuarios = cargar_json("usuarios.json")
    for uid, u in usuarios.items():
        cur.execute(
            """
            INSERT INTO usuarios
                (id, rol, nombre, correo, clave, telefono, puntos,
                 suspendido, motivo_suspension, justificacion_cliente,
                 pregunta_secreta, respuesta_secreta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uid,
                u["rol"],
                u["nombre"],
                u.get("correo"),
                u["clave"],
                u.get("telefono"),
                a_numero_o_none(u.get("puntos")),
                u.get("suspendido", False),
                u.get("motivo_suspension", ""),
                u.get("justificacion_cliente", ""),
                u.get("pregunta_secreta"),
                u.get("respuesta_secreta"),
            ),
        )
    print(f"usuarios: {len(usuarios)} filas insertadas")


def migrar_log_clientes(cur):
    registros = cargar_json("log_clientes.json")
    for r in registros:
        cur.execute(
            """
            INSERT INTO log_clientes (fecha, dni_cliente, tipo, puntos, detalle)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (a_fecha(r["fecha"]), r["dni_cliente"], r["tipo"], r["puntos"], r.get("detalle")),
        )
    print(f"log_clientes: {len(registros)} filas insertadas")


def migrar_log_desarrolladores(cur):
    registros = cargar_json("log_desarrolladores.json")
    for r in registros:
        cur.execute(
            """
            INSERT INTO log_desarrolladores (fecha, autor_id, autor_nombre, accion, objetivo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (a_fecha(r["fecha"]), r["autor_id"], r["autor_nombre"], r["accion"], r.get("objetivo")),
        )
    print(f"log_desarrolladores: {len(registros)} filas insertadas")


def migrar_log_tiendas(cur):
    registros = cargar_json("log_tiendas.json")
    for r in registros:
        cur.execute(
            """
            INSERT INTO log_tiendas (fecha, tienda_id, tienda_nombre, dni_cliente, puntos_descontados)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (a_fecha(r["fecha"]), r["tienda_id"], r["tienda_nombre"], r["dni_cliente"], r["puntos_descontados"]),
        )
    print(f"log_tiendas: {len(registros)} filas insertadas")


def migrar_promociones(cur):
    registros = cargar_json("promociones.json")
    for r in registros:
        cur.execute(
            """
            INSERT INTO promociones
                (tienda_id, tienda_nombre, titulo, categoria, descripcion, precio_soles, puntos, foto, stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                r["tienda_id"],
                r["tienda_nombre"],
                r["titulo"],
                r.get("categoria"),
                r.get("descripcion"),
                r["precio_soles"],
                r["puntos"],
                r.get("foto"),
                r.get("stock"),
            ),
        )
    print(f"promociones: {len(registros)} filas insertadas")


def migrar_entregas(cur):
    registros = cargar_json("entregas.json")
    for r in registros:
        cur.execute(
            """
            INSERT INTO entregas (fecha, tienda_id, dni_cliente, material, peso_kg, puntos)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (a_fecha(r["fecha"]), r["tienda_id"], r["dni_cliente"], r["material"], r["peso_kg"], r["puntos"]),
        )
    print(f"entregas: {len(registros)} filas insertadas")


def migrar_chat(cur):
    registros = cargar_json("chat.json")
    for r in registros:
        # Mensajes antiguos (de antes de que existiera el campo "leido") se marcan
        # como ya leidos, para no generar notificaciones de "no leido" falsas.
        leido = r.get("leido", True)
        cur.execute(
            """
            INSERT INTO chat (fecha, dni_cliente, autor, rol, mensaje, leido)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (a_fecha(r["fecha"]), r["dni_cliente"], r["autor"], r["rol"], r["mensaje"], leido),
        )
    print(f"chat: {len(registros)} filas insertadas")


def main():
    conn = conectar()
    cur = conn.cursor()

    tablas_y_funciones = [
        ("usuarios", migrar_usuarios),
        ("log_clientes", migrar_log_clientes),
        ("log_desarrolladores", migrar_log_desarrolladores),
        ("log_tiendas", migrar_log_tiendas),
        ("promociones", migrar_promociones),
        ("entregas", migrar_entregas),
        ("chat", migrar_chat),
    ]

    for nombre_tabla, funcion in tablas_y_funciones:
        if not tabla_vacia(cur, nombre_tabla):
            print(f"AVISO: la tabla '{nombre_tabla}' ya tiene datos, se omite para no duplicar.")
            continue
        funcion(cur)

    conn.commit()
    cur.close()
    conn.close()
    print("Migracion completa.")


if __name__ == "__main__":
    main()
