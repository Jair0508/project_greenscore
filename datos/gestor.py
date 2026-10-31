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

def eliminar_promocion(indice_promo, id_tienda, nombre_tienda):
    """Elimina una promoción perteneciendo al comercio especificado."""
    promos = cargar_promociones()
    if 0 <= indice_promo < len(promos):
        promo = promos[indice_promo]
        if str(promo.get("tienda_id")) == str(id_tienda):
            promos.pop(indice_promo)
            guardar_promociones(promos)
            return True
    return False

def eliminar_promocion_admin(indice_promo, id_tienda, motivo, autor_admin):
    """Elimina una promoción desde el panel de administración y notifica a la tienda."""
    promos = cargar_promociones()
    if 0 <= indice_promo < len(promos):
        promo_eliminada = promos.pop(indice_promo)
        guardar_promociones(promos)
        
        # Envia mensaje de notificación automática
        guardar_mensaje_chat(
            dni_cliente=str(id_tienda),
            autor_nombre=autor_admin,
            rol_autor="admin",
            mensaje=f"🚨 AVISO DE SISTEMA: Su oferta '{promo_eliminada.get('titulo')}' ha sido ELIMINADA por administración.\nMotivo: {motivo}"
        )
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
        "mensaje": mensaje,
        "leido": False  # <--- NUEVO: Inicializa el mensaje como no leído
    }
    mensajes.append(nuevo_msg)
    with open(RUTA_CHAT, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=4)

def marcar_chat_como_leido(dni_cliente, rol_lector):
    """Marca como leídos los mensajes pendientes según quién los esté leyendo."""
    if not os.path.exists(RUTA_CHAT):
        return
    mensajes = cargar_mensajes_chat()
    modificado = False
    
    for m in mensajes:
        if m.get("dni_cliente") == dni_cliente:
            # Si lee el admin/dev, marcamos como leídos los mensajes enviados por el vecino
            if rol_lector in ["admin", "desarrollador"] and m.get("rol") == "vecino" and not m.get("leido", True):
                m["leido"] = True
                modificado = True
            # Si lee el vecino, marcamos como leídos los mensajes enviados por el admin/dev
            elif rol_lector == "vecino" and m.get("rol") in ["admin", "desarrollador"] and not m.get("leido", True):
                m["leido"] = True
                modificado = True
                
    if modificado:
        try:
            with open(RUTA_CHAT, "w", encoding="utf-8") as f:
                json.dump(mensajes, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

def obtener_puntos_recolectados_por_tienda(id_tienda):
    """Calcula el total de puntos extraidos/canjeados por una tienda especifica."""
    log_tiendas = cargar_log_tiendas()
    total_pts = 0
    for reg in log_tiendas:
        if str(reg.get("id_tienda", "")) == str(id_tienda):
            total_pts += float(reg.get("puntos", 0))
    return round(total_pts, 1)