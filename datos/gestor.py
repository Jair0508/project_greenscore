import json
import os
from datetime import datetime

RUTA_USUARIOS = os.path.join("datos", "usuarios.json")
RUTA_LOG_DEVS = os.path.join("datos", "log_desarrolladores.json")
RUTA_LOG_TIENDAS = os.path.join("datos", "log_tiendas.json")
RUTA_LOG_CLIENTES = os.path.join("datos", "log_clientes.json")
RUTA_PROMOCIONES = os.path.join("datos", "promociones.json")
RUTA_CHAT = os.path.join("datos", "chat.json")



def cargar_usuarios():
    if not os.path.exists(RUTA_USUARIOS):
        return {}
    with open(RUTA_USUARIOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_usuarios(datos):
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def _cargar_log(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def _guardar_log(ruta, lista_log):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista_log, f, indent=4, ensure_ascii=False)

# --- FUNCIONES DE REGISTRO / AUDITORÍA ---

def registrar_accion_dev(id_dev, nombre_dev, accion, objetivo):
    """Guarda acciones realizadas por administradores / desarrolladores"""
    logs = _cargar_log(RUTA_LOG_DEVS)
    logs.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autor_id": id_dev,
        "autor_nombre": nombre_dev,
        "accion": accion,
        "objetivo": objetivo
    })
    _guardar_log(RUTA_LOG_DEVS, logs)

def registrar_accion_tienda(id_tienda, nombre_tienda, dni_cliente, puntos_canjeados):
    """Guarda canjes procesados por tiendas"""
    logs = _cargar_log(RUTA_LOG_TIENDAS)
    logs.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tienda_id": id_tienda,
        "tienda_nombre": nombre_tienda,
        "dni_cliente": dni_cliente,
        "puntos_descontados": puntos_canjeados
    })
    _guardar_log(RUTA_LOG_TIENDAS, logs)

def registrar_accion_cliente(dni_cliente, tipo_operacion, puntos, detalle):
    """Guarda actividad de clientes/vecinos (Abonos por reciclaje, compras, etc)"""
    logs = _cargar_log(RUTA_LOG_CLIENTES)
    logs.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dni_cliente": dni_cliente,
        "tipo": tipo_operacion,
        "puntos": puntos,
        "detalle": detalle
    })
    _guardar_log(RUTA_LOG_CLIENTES, logs)

# Carga de Logs para la Interfaz
def cargar_log_devs():
    return _cargar_log(RUTA_LOG_DEVS)

def cargar_log_tiendas():
    return _cargar_log(RUTA_LOG_TIENDAS)

def cargar_log_clientes():
    return _cargar_log(RUTA_LOG_CLIENTES)




#PROMOCIONES
def cargar_promociones():
    if not os.path.exists(RUTA_PROMOCIONES):
        return []
    try:
        with open(RUTA_PROMOCIONES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_promociones(lista_promos):
    with open(RUTA_PROMOCIONES, "w", encoding="utf-8") as f:
        json.dump(lista_promos, f, ensure_ascii=False, indent=4)

def eliminar_promocion(index_promo, tienda_id, tienda_nombre):
    promos = cargar_promociones()
    if 0 <= index_promo < len(promos):
        promo_removida = promos.pop(index_promo)
        guardar_promociones(promos)
        
        # Registrar auditoría para Administradores y Desarrolladores
        try:
            from datos.gestor import registrar_accion_tienda
            registrar_accion_tienda(
                tienda_id, 
                tienda_nombre, 
                "SISTEMA", 
                0, 
                f"ELIMINAR_PROMO: '{promo_removida.get('titulo')}'"
            )
        except Exception:
            pass
        return True
    return False


#CHAT USUARIO A DESARROLLADORES
def cargar_mensajes_chat():
    if not os.path.exists(RUTA_CHAT):
        return []
    try:
        with open(RUTA_CHAT, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_mensaje_chat(dni_cliente, autor_nombre, rol_autor, mensaje):
    from datetime import datetime
    mensajes = cargar_mensajes_chat()
    nuevo_msg = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dni_cliente": dni_cliente,
        "autor": autor_nombre,
        "rol": rol_autor,
        "mensaje": mensaje
    }
    mensajes.append(nuevo_msg)
    with open(RUTA_CHAT, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=4)
