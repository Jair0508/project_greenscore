import tkinter as tk
from tkinter import ttk, messagebox
import os
from datos.gestor import (
    cargar_usuarios, guardar_usuarios, registrar_accion_dev, 
    cargar_log_tiendas, cargar_log_clientes, registrar_accion_cliente,
    cargar_promociones, cargar_mensajes_chat, guardar_mensaje_chat, marcar_chat_como_leido, 
    obtener_puntos_recolectados_por_tienda, eliminar_promocion_admin
)
from logica.modelos import Material

# ==========================================
# PALETA DE COLORES - GESTOR (CELESTE OSCURO / OCÉANO)
# ==========================================
COLOR_FONDO_APP        = "#F0F9FF"
COLOR_TEXTO_MAIN       = "#0F172A"
COLOR_HEADER_GESTOR    = "#0369A1"
COLOR_PRIMARIO_CELESTE = "#0284C7"
COLOR_SECUNDARIO_CELESTE = "#38BDF8"
COLOR_ACENTO_TURQUESA  = "#0D9488"
COLOR_BLANCO           = "#FFFFFF"
COLOR_GRIS_BOTON       = "#64748B"

class VentanaGestorReciclaje:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        usuarios = cargar_usuarios()
        self.datos_sesion = usuarios.get(id_usuario, {})

        self.root.title("EcoPuntos - Panel de GESTOR DE RECICLAJE")
        self.root.geometry("1020x740")
        self.root.resizable(False, False)

        self.aplicar_icono()

        ruta_fondo = os.path.join("img", "fondo_interfaz_admin.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error al cargar fondo gestor: {e}")

        self.aplicar_estilos_ttk()

        frame_header = tk.Frame(self.root, bg=COLOR_HEADER_GESTOR)
        frame_header.pack(fill="x")
        
        tk.Label(
            frame_header, 
            text=f"♻️ GESTOR DE RECICLAJE: {self.datos_sesion.get('nombre')} | Correo: {self.datos_sesion.get('correo', '-')}", 
            font=("Arial", 11, "bold"), 
            fg=COLOR_BLANCO, 
            bg=COLOR_HEADER_GESTOR, 
            pady=10
        ).pack(side="left", padx=15)

        frame_acciones = tk.LabelFrame(
            self.root, 
            text=" Operaciones de Gestión ", 
            font=("Arial", 10, "bold"), 
            padx=5, 
            pady=4, 
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_MAIN
        )
        frame_acciones.pack(fill="x", padx=15, pady=6)

        canvas_btn = tk.Canvas(frame_acciones, bg=COLOR_BLANCO, height=38, highlightthickness=0)
        scroll_btn = ttk.Scrollbar(frame_acciones, orient="horizontal", command=canvas_btn.xview)
        
        btn_box = tk.Frame(canvas_btn, bg=COLOR_BLANCO)
        btn_box.bind("<Configure>", lambda e: canvas_btn.configure(scrollregion=canvas_btn.bbox("all")))

        canvas_btn.create_window((0, 0), window=btn_box, anchor="nw")
        canvas_btn.configure(xscrollcommand=scroll_btn.set)

        canvas_btn.pack(fill="x", expand=True)
        scroll_btn.pack(fill="x")

        tk.Button(btn_box, text="➕ Crear Cuenta", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_crear_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="♻️ Sumar Puntos", bg=COLOR_ACENTO_TURQUESA, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_registrar_reciclaje, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="➖ Restar Puntos", bg="#8B5CF6", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_reducir_puntos, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔑 Renovar Clave", bg="#D97706", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_cambiar_clave, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✏️ Editar Datos", bg="#0284C7", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_editar_datos, cursor="hand2").pack(side="left", padx=3, pady=2)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=(5, 2))

        tab_usuarios = ttk.Frame(notebook)
        tab_promos = ttk.Frame(notebook)
        tab_log_tiendas = ttk.Frame(notebook)
        tab_log_clientes = ttk.Frame(notebook)
        tab_soporte_general = ttk.Frame(notebook)

        notebook.add(tab_usuarios, text="👥 Cuentas Registradas")
        notebook.add(tab_promos, text="🛍️ Promociones Activas")
        notebook.add(tab_log_tiendas, text="🏪 Actividad Tiendas")
        notebook.add(tab_log_clientes, text="👤 Actividad Clientes")
        notebook.add(tab_soporte_general, text="🔔 Soporte (Bandeja)")

        def crear_tabla_con_scroll(parent, columnas, configuracion_columnas):
            frame_tabla = ttk.Frame(parent)
            frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

            scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
            scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")

            tabla = ttk.Treeview(
                frame_tabla, 
                columns=columnas, 
                show="headings",
                yscrollcommand=scroll_y.set,
                xscrollcommand=scroll_x.set
            )

            scroll_y.config(command=tabla.yview)
            scroll_x.config(command=tabla.xview)

            scroll_y.pack(side="right", fill="y")
            scroll_x.pack(side="bottom", fill="x")
            tabla.pack(side="left", fill="both", expand=True)

            tabla.tag_configure("suspendido", foreground="#DC2626", background="#FEE2E2")
            tabla.tag_configure("activo", foreground="#047857")

            for col, text, width in configuracion_columnas:
                tabla.heading(col, text=text)
                anchor_val = "w" if col in ["fecha", "detalle", "comentario"] else "center" if col in ["puntos", "rol", "estado", "estrellas"] else "w"
                tabla.column(col, width=width, minwidth=80, stretch=True, anchor=anchor_val)

            return tabla

        sub_notebook_usuarios = ttk.Notebook(tab_usuarios)
        sub_notebook_usuarios.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_usr_vecinos = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_negocios = ttk.Frame(sub_notebook_usuarios)

        sub_notebook_usuarios.add(self.tab_usr_vecinos, text="👤 Vecinos")
        sub_notebook_usuarios.add(self.tab_usr_negocios, text="🏪 Negocios")

        cols_usr = ("id", "nombre", "rol", "estado", "puntos", "rango", "justificacion")
        config_usr = [
            ("id", "DNI / ID", 110),
            ("nombre", "Nombre / Comercio", 180),
            ("rol", "Rol", 90),
            ("estado", "Estado / Indicador", 160),
            ("puntos", "Puntos", 80),
            ("rango", "Rango Ecológico", 170),
            ("justificacion", "Justificación Cliente", 200)
        ]

        self.tabla_usr_vecinos = crear_tabla_con_scroll(self.tab_usr_vecinos, cols_usr, config_usr)
        self.tabla_usr_negocios = crear_tabla_con_scroll(self.tab_usr_negocios, cols_usr, config_usr)

        tk.Button(
            tab_promos, 
            text="🖼️ Panel de promociones", 
            bg=COLOR_PRIMARIO_CELESTE, 
            fg=COLOR_BLANCO, 
            activeforeground=COLOR_BLANCO,
            font=("Arial", 9, "bold"), 
            relief="flat", 
            command=self.dialogo_ver_promociones_con_foto, 
            cursor="hand2",
            padx=10,
            pady=4
        ).pack(anchor="e", padx=5, pady=(5, 0))

        cols_pr = ("tienda", "titulo", "precio_soles", "puntos", "descripcion")
        config_pr = [
            ("tienda", "Comercio / Tienda", 180),
            ("titulo", "Título Oferta", 180),
            ("precio_soles", "Precio (S/)", 100),
            ("puntos", "Costo (PTS)", 100),
            ("descripcion", "Descripción", 280)
        ]
        self.tabla_promos = crear_tabla_con_scroll(tab_promos, cols_pr, config_pr)

        cols_tnd = ("fecha", "tienda_id", "tienda_nombre", "dni_cliente", "puntos")
        config_tnd = [
            ("fecha", "Fecha / Hora", 200),
            ("tienda_id", "ID Tienda", 110),
            ("tienda_nombre", "Nombre Comercio", 180),
            ("dni_cliente", "DNI Cliente / Ref", 140),
            ("puntos", "Pts / Detalle", 160)
        ]
        self.tabla_tnd = crear_tabla_con_scroll(tab_log_tiendas, cols_tnd, config_tnd)

        sub_notebook_cli = ttk.Notebook(tab_log_clientes)
        sub_notebook_cli.pack(fill="both", expand=True, padx=5, pady=5)

        tab_cli_todos = ttk.Frame(sub_notebook_cli)
        tab_cli_abonos = ttk.Frame(sub_notebook_cli)
        tab_cli_canjes = ttk.Frame(sub_notebook_cli)
        tab_cli_entregas = ttk.Frame(sub_notebook_cli)
        tab_cli_resenas = ttk.Frame(sub_notebook_cli)

        sub_notebook_cli.add(tab_cli_todos, text="📋 Todos")
        sub_notebook_cli.add(tab_cli_abonos, text="♻️ Abonos / Reciclaje")
        sub_notebook_cli.add(tab_cli_canjes, text="🛍️ Canjes de Puntos")
        sub_notebook_cli.add(tab_cli_entregas, text="📦 Entregas Validadas")
        sub_notebook_cli.add(tab_cli_resenas, text="⭐ Reseñas y Estrellas")

        cols_cli = ("fecha", "dni_cliente", "tipo", "puntos", "detalle")
        config_cli = [
            ("fecha", "Fecha / Hora", 200),
            ("dni_cliente", "DNI Cliente", 130),
            ("tipo", "Tipo Operación", 150),
            ("puntos", "Puntos (+/-)", 110),
            ("detalle", "Detalle de Operación", 450)
        ]
        self.tabla_cli_todos = crear_tabla_con_scroll(tab_cli_todos, cols_cli, config_cli)
        self.tabla_cli_abonos = crear_tabla_con_scroll(tab_cli_abonos, cols_cli, config_cli)
        self.tabla_cli_canjes = crear_tabla_con_scroll(tab_cli_canjes, cols_cli, config_cli)
        self.tabla_cli_entregas = crear_tabla_con_scroll(tab_cli_entregas, cols_cli, config_cli)

        cols_resenas = ("fecha", "dni_cliente", "estrellas", "comentario")
        config_resenas = [
            ("fecha", "Fecha / Hora", 180),
            ("dni_cliente", "DNI Cliente", 130),
            ("estrellas", "⭐ Calificación", 180),
            ("comentario", "💬 Reseña / Comentario del Vecino", 480)
        ]
        self.tabla_cli_resenas = crear_tabla_con_scroll(tab_cli_resenas, cols_resenas, config_resenas)

        sub_notebook_soporte = ttk.Notebook(tab_soporte_general)
        sub_notebook_soporte.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_chat_vecinos = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_negocios = ttk.Frame(sub_notebook_soporte)

        sub_notebook_soporte.add(self.tab_chat_vecinos, text="👤 Vecinos")
        sub_notebook_soporte.add(self.tab_chat_negocios, text="🏪 Negocios")

        self.chats_ui = {}

        for rol_tipo, tab_widget in [("vecino", self.tab_chat_vecinos), ("negocio", self.tab_chat_negocios)]:
            frame_box = tk.Frame(tab_widget, bg=COLOR_BLANCO, padx=10, pady=10)
            frame_box.pack(fill="both", expand=True)

            frame_top = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_top.pack(fill="x", pady=(0, 5))

            tk.Label(frame_top, text="✉️ Seleccionar:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(side="left", padx=5)
            
            cb = ttk.Combobox(frame_top, font=("Arial", 10), width=38, state="readonly")
            cb.pack(side="left", padx=5)
            cb.bind("<<ComboboxSelected>>", lambda e, r=rol_tipo: self.cargar_chat_seleccionado(r))

            tk.Button(
                frame_top, text="🔄 Actualizar", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO, font=("Arial", 8, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.llenar_combo_chats_por_rol(r), cursor="hand2"
            ).pack(side="left", padx=5)

            frame_txt = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_txt.pack(fill="both", expand=True, pady=5)

            scroll_txt = ttk.Scrollbar(frame_txt, orient="vertical")
            scroll_txt.pack(side="right", fill="y")

            txt = tk.Text(frame_txt, state="disabled", font=("Arial", 10), bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, wrap="word", yscrollcommand=scroll_txt.set)
            txt.pack(side="left", fill="both", expand=True)
            scroll_txt.config(command=txt.yview)

            frame_input = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_input.pack(fill="x", pady=(5, 0))

            ent = tk.Entry(frame_input, font=("Arial", 10), bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE)
            ent.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
            ent.bind("<Return>", lambda e, r=rol_tipo: self.responder_chat_por_rol(r))

            tk.Button(
                frame_input, text="Responder ✉️", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.responder_chat_por_rol(r), cursor="hand2"
            ).pack(side="right")

            self.chats_ui[rol_tipo] = {
                "cb": cb,
                "txt": txt,
                "ent": ent,
                "mapeo": {}
            }

        tk.Button(
            self.root, 
            text="🚪 Cerrar Sesión", 
            bg=COLOR_GRIS_BOTON, 
            fg=COLOR_BLANCO, 
            activeforeground=COLOR_BLANCO,
            font=("Arial", 10, "bold"), 
            relief="flat", 
            command=self.cerrar_sesion_cb, 
            cursor="hand2", 
            pady=4,
            padx=15
        ).pack(side="bottom", pady=8)

        self.actualizar_tablas()
        self.llenar_todos_los_combos()

    def aplicar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_FONDO_APP, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 10, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_BLANCO)], foreground=[("selected", COLOR_PRIMARIO_CELESTE)])
        
        style.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_TEXTO_MAIN, fieldbackground=COLOR_BLANCO, rowheight=25)
        style.configure("Treeview.Heading", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 9, "bold"))

    def obtener_rango_vecino(self, puntos):
        try:
            pts = int(float(puntos))
        except (ValueError, TypeError):
            pts = 0

        if pts > 300: return "👑 Leyenda Suprema"
        elif pts > 150: return "🌳 Guerrero Verde"
        elif pts > 50: return "🌿 Reciclador Activo"
        else: return "🌱 Eco-Novato"

    def llenar_todos_los_combos(self):
        for rol in ["vecino", "negocio"]:
            self.llenar_combo_chats_por_rol(rol)

    def llenar_combo_chats_por_rol(self, rol_tipo):
        mensajes = cargar_mensajes_chat()
        usuarios = cargar_usuarios()
        
        ui = self.chats_ui[rol_tipo]
        cb = ui["cb"]
        mapeo = ui["mapeo"]
        
        opciones = []
        mapeo.clear()

        for uid, datos in usuarios.items():
            if datos.get("rol") == rol_tipo:
                nombre_usuario = datos.get("nombre", "Usuario")
                tiene_pendientes = any(m.get("dni_cliente") == uid and not m.get("leido", True) for m in mensajes)
                icono_alerta = "🔔 [NUEVO] " if tiene_pendientes else "💬 "
                texto_item = f"{icono_alerta}{nombre_usuario} (ID: {uid})"
                opciones.append(texto_item)
                mapeo[texto_item] = uid

        cb['values'] = opciones
        if opciones:
            cb.current(0)
            self.cargar_chat_seleccionado(rol_tipo)
        else:
            cb.set("No hay usuarios registrados")
            ui["txt"].config(state="normal")
            ui["txt"].delete("1.0", tk.END)
            ui["txt"].insert(tk.END, "💬 No hay registros disponibles.\n")
            ui["txt"].config(state="disabled")

    def cargar_chat_seleccionado(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion: return
        
        dni = ui["mapeo"].get(seleccion)
        if not dni: return

        marcar_chat_como_leido(dni, "gestor")

        txt = ui["txt"]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == dni]

        if not msg_cliente:
            txt.insert(tk.END, "💬 No hay mensajes previos con este usuario. Escribe abajo para responder.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")
                leido = m.get("leido", True)

                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"
                txt.insert(tk.END, f"[{fecha}] {autor} ({rol}){check_leido}:\n{texto}\n\n")

        txt.see(tk.END)
        txt.config(state="disabled")

    def responder_chat_por_rol(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion: return

        dni = ui["mapeo"].get(seleccion)
        texto = ui["ent"].get().strip()
        if not texto: return

        guardar_mensaje_chat(
            dni_cliente=dni,
            autor_nombre=self.datos_sesion.get("nombre", "Gestor de Reciclaje"),
            rol_autor="gestor",
            mensaje=texto
        )

        ui["ent"].delete(0, tk.END)
        self.cargar_chat_seleccionado(rol_tipo)

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception: pass

    def pedir_texto_custom(self, titulo, mensaje):
        win = tk.Toplevel(self.root)
        win.config(bg=COLOR_FONDO_APP)
        win.title(titulo)
        win.geometry("380x180")
        win.resizable(False, False)
        win.grab_set()

        if hasattr(self.root, 'icon_img'): win.iconphoto(False, self.root.icon_img)

        container = tk.Frame(win, bg=COLOR_FONDO_APP, padx=15, pady=15)
        container.pack(fill="both", expand=True)

        lbl_msg = tk.Label(container, text=mensaje, font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP, wraplength=340, justify="center")
        lbl_msg.pack(pady=(0, 10))

        entry_var = tk.StringVar()
        entry = tk.Entry(container, textvariable=entry_var, font=("Arial", 10), width=35, bd=1, relief="solid")
        entry.pack(pady=5)
        entry.focus_set()

        resultado = {"texto": None}
        def confirmar():
            txt = entry_var.get().strip()
            if txt:
                resultado["texto"] = txt
                win.destroy()

        def cancelar(): win.destroy()

        frame_btn = tk.Frame(container, bg=COLOR_FONDO_APP)
        frame_btn.pack(pady=10)
        tk.Button(frame_btn, text="Aceptar", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), width=10, relief="flat", cursor="hand2", command=confirmar).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Cancelar", bg=COLOR_GRIS_BOTON, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), width=10, relief="flat", cursor="hand2", command=cancelar).pack(side="left", padx=5)

        win.bind("<Return>", lambda e: confirmar())
        win.bind("<Escape>", lambda e: cancelar())
        self.root.wait_window(win)
        return resultado["texto"]

    def actualizar_tablas(self):
        for item in self.tabla_usr_vecinos.get_children(): self.tabla_usr_vecinos.delete(item)
        for item in self.tabla_usr_negocios.get_children(): self.tabla_usr_negocios.delete(item)

        usuarios = cargar_usuarios()
        for uid, datos in usuarios.items():
            suspendido = datos.get("suspendido", False)
            estado_txt = f"🔴 SUSPENDIDO ({datos.get('motivo_suspension', '')})" if suspendido else "🟢 ACTIVO"
            tag_fila = "suspendido" if suspendido else "activo"

            rol = datos.get("rol", "-")
            puntos_raw = datos.get("puntos", 0)
            puntos = int(float(puntos_raw)) if rol == "vecino" else "N/A"
            rango_txt = self.obtener_rango_vecino(puntos) if rol == "vecino" else "N/A (Personal)"
            justif_txt = datos.get("justificacion_cliente", "-") or "-"

            tupla_datos = (uid, datos.get("nombre", "-"), rol.upper(), estado_txt, puntos, rango_txt, justif_txt)

            if rol == "vecino":
                self.tabla_usr_vecinos.insert("", "end", values=tupla_datos, tags=(tag_fila,))
            elif rol == "negocio":
                pts_recolectados = obtener_puntos_recolectados_por_tienda(uid)
                comision_pts = round(pts_recolectados * 0.10, 1)
                comision_soles = round(comision_pts * 0.10, 2)
                
                tupla_negocio = (uid, datos.get("nombre", "-"), rol.upper(), estado_txt, f"{pts_recolectados} PTS", f"{comision_pts} PTS (S/ {comision_soles:.2f})", justif_txt)
                self.tabla_usr_negocios.insert("", "end", values=tupla_negocio, tags=(tag_fila,))

        for item in self.tabla_promos.get_children(): self.tabla_promos.delete(item)
        for p in cargar_promociones():
            pts_oferta = int(float(p.get('puntos', 0)))
            self.tabla_promos.insert("", "end", values=(p.get("tienda_nombre", "Tienda"), p.get("titulo", "-"), f"S/ {p.get('precio_soles', 0):.2f}", f"{pts_oferta} PTS", p.get("descripcion", "-")))

        for item in self.tabla_tnd.get_children(): self.tabla_tnd.delete(item)
        for log in reversed(cargar_log_tiendas()):
            self.tabla_tnd.insert("", "end", values=(log.get("fecha"), log.get("tienda_id"), log.get("tienda_nombre"), log.get("dni_cliente"), log.get("puntos_descontados")))

        tablas_cli = [self.tabla_cli_todos, self.tabla_cli_abonos, self.tabla_cli_canjes, self.tabla_cli_entregas, self.tabla_cli_resenas]
        for t in tablas_cli:
            for item in t.get_children(): t.delete(item)

        for log in reversed(cargar_log_clientes()):
            fecha = log.get("fecha", "-"); dni = log.get("dni_cliente", "-"); tipo = log.get("tipo", "")
            puntos = int(float(log.get("puntos", 0)))
            detalle = log.get("detalle", "")
            valores = (fecha, dni, tipo, puntos, detalle)

            self.tabla_cli_todos.insert("", "end", values=valores)
            if tipo in ["ABONO_RECICLAJE", "SUMA_ADMIN"]: self.tabla_cli_abonos.insert("", "end", values=valores)
            elif tipo in ["CANJE_OFERTA", "CANJE_TIENDA", "REDUCCION_ADMIN"]: self.tabla_cli_canjes.insert("", "end", values=valores)
            elif tipo in ["ENTREGA_OFERTA"]: self.tabla_cli_entregas.insert("", "end", values=valores)
            elif tipo in ["RESEÑA_TIENDA"]: self.tabla_cli_resenas.insert("", "end", values=(fecha, dni, "⭐ Reseña", detalle))

    def dialogo_crear_cuenta(self):
        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Crear Cuenta (Vecino / Negocio)")
        win_modal.geometry("340x360")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'): win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text="Seleccione Tipo de Cuenta:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        cb_rol = ttk.Combobox(win_modal, values=["vecino", "negocio"], state="readonly")
        cb_rol.pack(pady=5); cb_rol.current(0)

        tk.Label(win_modal, text="DNI / Código de Cuenta:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_uid = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_uid.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Nombre / Razón Social:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_nom = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_nom.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Correo Electrónico:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_correo = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_correo.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Teléfono / Celular:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_tel = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_tel.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Contraseña Inicial:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_clave = tk.Entry(win_modal, show="*", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_clave.pack(pady=2, ipady=2)

        def guardar():
            uid = ent_uid.get().strip(); nom = ent_nom.get().strip(); rol = cb_rol.get()
            correo = ent_correo.get().strip(); tel = ent_tel.get().strip(); clave = ent_clave.get().strip()

            if not uid or not nom or not clave:
                messagebox.showerror("Error", "Complete los campos obligatorios.")
                return

            usuarios = cargar_usuarios()
            if uid in usuarios:
                messagebox.showerror("Error", "El ID/DNI ya existe.")
                return

            usuarios[uid] = {
                "rol": rol, "nombre": nom, "correo": correo or "-", "telefono": tel or "-", "clave": clave, "puntos": 0 if rol == "vecino" else "N/A",
                "suspendido": False, "motivo_suspension": "", "justificacion_cliente": ""
            }
            guardar_usuarios(usuarios)
            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CREAR_CUENTA", f"Creó cuenta {uid} ({rol.upper()})")
            
            self.actualizar_tablas()
            self.llenar_todos_los_combos()
            win_modal.destroy()
            messagebox.showinfo("Éxito", f"Cuenta de tipo '{rol.upper()}' creada.")

        tk.Button(win_modal, text="Guardar Cuenta", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), command=guardar, relief="flat", cursor="hand2", pady=5).pack(pady=15)

    def dialogo_registrar_reciclaje(self):
        dni = self.pedir_texto_custom("Sumar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "DNI no corresponde a un vecino.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA.")
            return

        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Sumar Puntos por Reciclaje")
        win_modal.geometry("320x230")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'): win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text=f"Vecino: {usuarios[dni]['nombre']}", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        cb_mat = ttk.Combobox(win_modal, values=list(Material.TASAS.keys()), state="readonly"); cb_mat.pack(pady=5); cb_mat.current(0)
        tk.Label(win_modal, text="Peso en KG:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_kg = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_kg.pack(pady=5, ipady=2)

        def procesar():
            raw_input_kg = ent_kg.get().strip()
            if not raw_input_kg.isdigit():
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)
                return

            try:
                peso = int(raw_input_kg)
                mat = cb_mat.get()
                puntos_calculados = Material.calcular_puntos(mat, float(peso))
                puntos = int(round(puntos_calculados))
                puntos_actuales_user = int(float(usuarios[dni].get("puntos", 0)))
                
                usuarios[dni]["puntos"] = puntos_actuales_user + puntos
                guardar_usuarios(usuarios)
                
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUMAR_PUNTOS", f"Abonó {puntos} pts a {dni} por {mat}")
                registrar_accion_cliente(dni, "ABONO_RECICLAJE", puntos, f"Reciclaje de {mat} ({peso} kg)")
                
                self.actualizar_tablas()
                win_modal.destroy()
                messagebox.showinfo("Éxito", f"Se sumaron {puntos} puntos.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)

        tk.Button(win_modal, text="Sumar Puntos", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), command=procesar, relief="flat", cursor="hand2", pady=5).pack(pady=10)

    def dialogo_reducir_puntos(self):
        dni = self.pedir_texto_custom("Restar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "Vecino no encontrado.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[dni]['nombre']} está SUSPENDIDA.")
            return
            
        puntos_actuales_user = int(float(usuarios[dni].get("puntos", 0)))
        pts_str = self.pedir_texto_custom("Restar Puntos", f"Puntos actuales: {puntos_actuales_user}\nCantidad a restar:")
        
        if pts_str:
            if not pts_str.isdigit():
                messagebox.showerror("Error", "Solamente números enteros")
                return

            try:
                pts = int(pts_str)
                if pts > 0 and puntos_actuales_user >= pts:
                    usuarios[dni]["puntos"] = puntos_actuales_user - pts
                    guardar_usuarios(usuarios)
                    registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "RESTAR_PUNTOS", f"Restó {pts} pts a {dni}")
                    registrar_accion_cliente(dni, "REDUCCION_ADMIN", -pts, "Ajuste manual del gestor")
                    self.actualizar_tablas()
                    messagebox.showinfo("Éxito", f"Se restaron {pts} puntos.")
                else:
                    messagebox.showerror("Error", "Puntos insuficientes.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros")

    def dialogo_cambiar_clave(self):
        uid = self.pedir_texto_custom("Renovar Clave", "Ingrese DNI/ID del vecino o negocio:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid in usuarios and usuarios[uid]["rol"] in ["vecino", "negocio"]:
            nueva = self.pedir_texto_custom("Renovar Clave", f"Nueva contraseña para {usuarios[uid]['nombre']}:")
            if nueva:
                usuarios[uid]["clave"] = nueva
                guardar_usuarios(usuarios)
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CAMBIO_CLAVE", f"Modificó clave de {uid}")
                messagebox.showinfo("Éxito", "Contraseña renovada.")
        else:
            messagebox.showerror("Error", "Usuario no encontrado o no permitido.")

    def dialogo_editar_datos(self):
        uid = self.pedir_texto_custom("Editar Datos", "Ingrese DNI/ID:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid not in usuarios or usuarios[uid]["rol"] not in ["vecino", "negocio"]:
            messagebox.showerror("Error", "Usuario no encontrado o no permitido.")
            return

        if usuarios[uid].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[uid]['nombre']} se encuentra SUSPENDIDA.")
            return

        nuevo_nom = self.pedir_texto_custom("Editar", "Nuevo Nombre:")
        nuevo_correo = self.pedir_texto_custom("Editar", "Nuevo Correo:")
        nuevo_tel = self.pedir_texto_custom("Editar", "Nuevo Celular:")
        
        if nuevo_nom: usuarios[uid]["nombre"] = nuevo_nom
        if nuevo_correo: usuarios[uid]["correo"] = nuevo_correo
        if nuevo_tel: usuarios[uid]["telefono"] = nuevo_tel

        guardar_usuarios(usuarios)
        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "EDITAR_DATOS", f"Actualizó datos de {uid}")
        self.actualizar_tablas()
        messagebox.showinfo("Éxito", "Datos actualizados.")

    def dialogo_ver_promociones_con_foto(self):
        win_promos = tk.Toplevel(self.root)
        win_promos.config(bg=COLOR_BLANCO)
        win_promos.title("Gestión de Ofertas en Cuadrícula")
        win_promos.geometry("720x540")
        win_promos.resizable(False, False)
        win_promos.grab_set()

        if hasattr(self.root, 'icon_img'): win_promos.iconphoto(False, self.root.icon_img)

        canvas = tk.Canvas(win_promos, bg=COLOR_BLANCO, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(win_promos, orient="vertical", command=canvas.yview)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        nombres_archivos = ["fondo_ofertas_admin.png", "fondo_ofertas_admin.jpg"]
        ruta_encontrada = next((os.path.join("img", n) for n in nombres_archivos if os.path.exists(os.path.join("img", n))), None)

        if ruta_encontrada:
            try:
                from PIL import Image, ImageTk
                img_pil = Image.open(ruta_encontrada).convert("RGBA").resize((720, 540), Image.Resampling.LANCZOS)
                win_promos.bg_img = ImageTk.PhotoImage(img_pil)
                img_id = canvas.create_image(0, 0, image=win_promos.bg_img, anchor="nw")
                canvas.tag_lower(img_id)
            except Exception: pass

        frame_grid = tk.Frame(canvas, bg="")
        frame_grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_grid, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def refrescar_grid():
            for w in frame_grid.winfo_children(): w.destroy()
            promos = cargar_promociones()
            if not promos:
                tk.Label(frame_grid, text="No hay promociones registradas.", font=("Arial", 11, "italic"), fg=COLOR_GRIS_BOTON, bg=COLOR_BLANCO).pack(pady=50)
                return

            cols = 2
            for idx, p in enumerate(promos):
                row, col = idx // cols, idx % cols
                card = tk.Frame(frame_grid, bg=COLOR_BLANCO, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO_CELESTE, highlightthickness=1, padx=12, pady=12, width=240, height=240)
                card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
                card.grid_propagate(False)

                pts_oferta = int(float(p.get('puntos', 0)))
                txt_info = f"🏪 {p.get('tienda_nombre')}\n(ID: {p.get('tienda_id')})\n\n📌 {p.get('titulo')}\n💰 S/ {p.get('precio_soles', 0):.2f} ➔ {pts_oferta} PTS\n\n📝 {p.get('descripcion')}"
                tk.Label(card, text=txt_info, font=("Arial", 8, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO, justify="left", wraplength=210).pack(anchor="w", expand=True)

                def eliminar_con_motivo(i=idx, tienda_id=p.get('tienda_id'), titulo=p.get('titulo')):
                    motivo = self.pedir_texto_custom("Eliminar Oferta", f"Motivo de eliminación para '{titulo}':")
                    if not motivo: return

                    if messagebox.askyesno("Confirmar", f"¿Eliminar la oferta '{titulo}'?"):
                        if eliminar_promocion_admin(i, tienda_id, motivo, self.datos_sesion.get("nombre", "Gestor")):
                            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "ELIMINAR_OFERTA", f"Eliminó oferta '{titulo}'. Motivo: {motivo}")
                            messagebox.showinfo("Éxito", "La oferta ha sido eliminada.")
                            self.actualizar_tablas()
                            refrescar_grid()

                tk.Button(card, text="🗑️ Eliminar Oferta", bg="#DC2626", fg=COLOR_BLANCO, font=("Arial", 8, "bold"), relief="flat", command=eliminar_con_motivo, cursor="hand2", pady=4).pack(fill="x", side="bottom")

        refrescar_grid()