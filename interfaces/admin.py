import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, guardar_usuarios, registrar_accion_dev, 
    cargar_log_devs, cargar_log_tiendas, cargar_log_clientes, registrar_accion_cliente,
    cargar_promociones, cargar_mensajes_chat, guardar_mensaje_chat, marcar_chat_como_leido
)
from logica.modelos import Material

class VentanaAdmin:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        usuarios = cargar_usuarios()
        self.datos_sesion = usuarios.get(id_usuario, {})
        self.es_admin_supremo = (self.datos_sesion.get("rol") == "admin")

        titulo_rol = "SUPER ADMINISTRADOR" if self.es_admin_supremo else "DESARROLLADOR"
        self.root.title(f"EcoPuntos - Panel de {titulo_rol}")
        self.root.geometry("1020x740")
        self.root.resizable(False, False)

        self.aplicar_icono()

        # 1. IMAGEN DE FONDO
        ruta_fondo = os.path.join("img", "fondo_interfaz_admin.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error al cargar imagen de fondo admin: {e}")

        # 2. HEADER
        color_header = "#1B5E20" if self.es_admin_supremo else "#0D47A1"
        frame_header = tk.Frame(self.root, bg=color_header)
        frame_header.pack(fill="x")
        
        tk.Label(
            frame_header, 
            text=f"👑 {titulo_rol}: {self.datos_sesion.get('nombre')} | Correo: {self.datos_sesion.get('correo', '-')}", 
            font=("Arial", 11, "bold"), 
            fg="white", 
            bg=color_header, 
            pady=10
        ).pack(side="left", padx=15)

        # 3. BOTONES DE ACCIÓN DE GESTIÓN
        frame_acciones = tk.LabelFrame(
            self.root, 
            text=" Acciones de Gestión ", 
            font=("Arial", 10, "bold"), 
            padx=5, 
            pady=4, 
            bg="white"
        )
        frame_acciones.pack(fill="x", padx=15, pady=6)

        canvas_btn = tk.Canvas(frame_acciones, bg="white", height=38, highlightthickness=0)
        scroll_btn = ttk.Scrollbar(frame_acciones, orient="horizontal", command=canvas_btn.xview)
        
        btn_box = tk.Frame(canvas_btn, bg="white")
        btn_box.bind("<Configure>", lambda e: canvas_btn.configure(scrollregion=canvas_btn.bbox("all")))

        canvas_btn.create_window((0, 0), window=btn_box, anchor="nw")
        canvas_btn.configure(xscrollcommand=scroll_btn.set)

        canvas_btn.pack(fill="x", expand=True)
        scroll_btn.pack(fill="x")

        # Botones de Acción
        tk.Button(btn_box, text="➕ Crear Cuenta", bg="#2E7D32", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_crear_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="❌ Eliminar Cuenta", bg="#C62828", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_eliminar_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🛑 Suspender Cuenta", bg="#D32F2F", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_suspender_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✅ Levantar Suspensión", bg="#28A745", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_levantar_suspension, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="♻️ Sumar Puntos", bg="#1976D2", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_registrar_reciclaje, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="➖ Restar Puntos", bg="#C2185B", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_reducir_puntos, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔑 Renovar Clave", bg="#F57C00", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_cambiar_clave, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✏️ Editar Datos", bg="#00897B", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_editar_datos, cursor="hand2").pack(side="left", padx=3, pady=2)

        # 4. CONTROL DE PESTAÑAS PRINCIPALES
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=(5, 2))

        tab_usuarios = ttk.Frame(notebook)
        tab_promos = ttk.Frame(notebook)
        tab_log_tiendas = ttk.Frame(notebook)
        tab_log_clientes = ttk.Frame(notebook)
        tab_soporte_general = ttk.Frame(notebook)

        notebook.add(tab_usuarios, text="👥 Cuentas y Suspensiones")
        notebook.add(tab_promos, text="🛍️ Promociones Activas")
        notebook.add(tab_log_tiendas, text="🏪 Actividad Tiendas")
        notebook.add(tab_log_clientes, text="👤 Actividad Clientes")
        notebook.add(tab_soporte_general, text="🔔 Soporte (Bandeja)")

        if self.es_admin_supremo:
            self.tab_log_devs = ttk.Frame(notebook)
            notebook.add(self.tab_log_devs, text="🕵️ Actividad Devs (Solo Admin)")

        # FUNCIÓN AUXILIAR DE TABLAS CON DOBLE SCROLL Y ANCHOS AMPLIOS
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

            for col, text, width in configuracion_columnas:
                tabla.heading(col, text=text)
                anchor_val = "w" if col in ["fecha", "detalle", "comentario"] else "center" if col in ["puntos", "rol", "estado", "estrellas"] else "w"
                tabla.column(col, width=width, minwidth=80, stretch=True, anchor=anchor_val)

            return tabla

        # =========================================================================
        # 5. SUB-PESTAÑAS DE CUENTAS (VECINOS, NEGOCIOS, DESARROLLADORES)
        # =========================================================================
        sub_notebook_usuarios = ttk.Notebook(tab_usuarios)
        sub_notebook_usuarios.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_usr_vecinos = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_negocios = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_devs = ttk.Frame(sub_notebook_usuarios)

        sub_notebook_usuarios.add(self.tab_usr_vecinos, text="👤 Vecinos")
        sub_notebook_usuarios.add(self.tab_usr_negocios, text="🏪 Negocios")
        sub_notebook_usuarios.add(self.tab_usr_devs, text="💻 Desarrolladores / Admins")

        cols_usr = ("id", "nombre", "rol", "estado", "puntos", "rango", "justificacion")
        config_usr = [
            ("id", "DNI / ID", 110),
            ("nombre", "Nombre / Comercio", 180),
            ("rol", "Rol", 90),
            ("estado", "Estado / Motivo", 160),
            ("puntos", "Puntos", 80),
            ("rango", "Rango Ecológico", 170),
            ("justificacion", "Justificación Cliente", 200)
        ]

        self.tabla_usr_vecinos = crear_tabla_con_scroll(self.tab_usr_vecinos, cols_usr, config_usr)
        self.tabla_usr_negocios = crear_tabla_con_scroll(self.tab_usr_negocios, cols_usr, config_usr)
        self.tabla_usr_devs = crear_tabla_con_scroll(self.tab_usr_devs, cols_usr, config_usr)

        # PROMOCIONES ACTIVAS
        tk.Button(
            tab_promos, 
            text="🖼️ Abrir Vista Visual con Fotos", 
            bg="#1976D2", 
            fg="white", 
            activeforeground="white",
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

        # LOG TIENDAS
        cols_tnd = ("fecha", "tienda_id", "tienda_nombre", "dni_cliente", "puntos")
        config_tnd = [
            ("fecha", "Fecha / Hora", 200),
            ("tienda_id", "ID Tienda", 110),
            ("tienda_nombre", "Nombre Comercio", 180),
            ("dni_cliente", "DNI Cliente / Ref", 140),
            ("puntos", "Pts / Detalle", 160)
        ]
        self.tabla_tnd = crear_tabla_con_scroll(tab_log_tiendas, cols_tnd, config_tnd)

        # =========================================================================
        # SUB-PESTAÑAS EN ACTIVIDAD CLIENTES (RESEÑAS SEPARADAS EN ESTRELLAS Y COMENTARIO)
        # =========================================================================
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

        # TABLA ESPECIAL PARA RESEÑAS CON COLUMNAS SEPARADAS
        cols_resenas = ("fecha", "dni_cliente", "estrellas", "comentario")
        config_resenas = [
            ("fecha", "Fecha / Hora", 180),
            ("dni_cliente", "DNI Cliente", 130),
            ("estrellas", "⭐ Calificación", 180),
            ("comentario", "💬 Reseña / Comentario del Vecino", 480)
        ]
        self.tabla_cli_resenas = crear_tabla_con_scroll(tab_cli_resenas, cols_resenas, config_resenas)

        # LOG DEVS (Solo Admin)
        if self.es_admin_supremo:
            cols_dev = ("fecha", "autor_id", "autor_nombre", "accion", "objetivo")
            config_dev = [
                ("fecha", "Fecha / Hora", 200),
                ("autor_id", "ID Dev/Admin", 120),
                ("autor_nombre", "Nombre Dev", 180),
                ("accion", "Acción Ejecutada", 160),
                ("objetivo", "Usuario / Cuenta Afectada", 250)
            ]
            self.tabla_dev = crear_tabla_con_scroll(self.tab_log_devs, cols_dev, config_dev)

        # =========================================================================
        # 6. SUB-PESTAÑAS DE SOPORTE (VECINOS, NEGOCIOS, DESARROLLADORES)
        # =========================================================================
        sub_notebook_soporte = ttk.Notebook(tab_soporte_general)
        sub_notebook_soporte.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_chat_vecinos = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_negocios = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_devs = ttk.Frame(sub_notebook_soporte)

        sub_notebook_soporte.add(self.tab_chat_vecinos, text="👤 Vecinos")
        sub_notebook_soporte.add(self.tab_chat_negocios, text="🏪 Negocios")
        sub_notebook_soporte.add(self.tab_chat_devs, text="💻 Desarrolladores")

        self.chats_ui = {}

        for rol_tipo, tab_widget in [("vecino", self.tab_chat_vecinos), ("negocio", self.tab_chat_negocios), ("desarrollador", self.tab_chat_devs)]:
            frame_box = tk.Frame(tab_widget, bg="white", padx=10, pady=10)
            frame_box.pack(fill="both", expand=True)

            frame_top = tk.Frame(frame_box, bg="white")
            frame_top.pack(fill="x", pady=(0, 5))

            tk.Label(frame_top, text="✉️ Seleccionar:", font=("Arial", 9, "bold"), bg="white").pack(side="left", padx=5)
            
            cb = ttk.Combobox(frame_top, font=("Arial", 10), width=38, state="readonly")
            cb.pack(side="left", padx=5)
            cb.bind("<<ComboboxSelected>>", lambda e, r=rol_tipo: self.cargar_chat_seleccionado(r))

            tk.Button(
                frame_top, text="🔄 Actualizar", bg="#1976D2", fg="white", 
                activeforeground="white", font=("Arial", 8, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.llenar_combo_chats_por_rol(r), cursor="hand2"
            ).pack(side="left", padx=5)

            frame_txt = tk.Frame(frame_box, bg="white")
            frame_txt.pack(fill="both", expand=True, pady=5)

            scroll_txt = ttk.Scrollbar(frame_txt, orient="vertical")
            scroll_txt.pack(side="right", fill="y")

            txt = tk.Text(frame_txt, state="disabled", font=("Arial", 10), bg="#F9F9F9", wrap="word", yscrollcommand=scroll_txt.set)
            txt.pack(side="left", fill="both", expand=True)
            scroll_txt.config(command=txt.yview)

            frame_input = tk.Frame(frame_box, bg="white")
            frame_input.pack(fill="x", pady=(5, 0))

            ent = tk.Entry(frame_input, font=("Arial", 10), bg="#F0F0F0")
            ent.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
            ent.bind("<Return>", lambda e, r=rol_tipo: self.responder_chat_por_rol(r))

            tk.Button(
                frame_input, text="Responder ✉️", bg="#2E7D32", fg="white", 
                activeforeground="white", font=("Arial", 9, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.responder_chat_por_rol(r), cursor="hand2"
            ).pack(side="right")

            self.chats_ui[rol_tipo] = {
                "cb": cb,
                "txt": txt,
                "ent": ent,
                "mapeo": {}
            }

        # 7. BOTÓN COMPACTO DE CERRAR SESIÓN EN PARALELO
        tk.Button(
            self.root, 
            text="🚪 Cerrar Sesión", 
            bg="#757575", 
            fg="white", 
            activeforeground="white",
            font=("Arial", 10, "bold"), 
            relief="flat", 
            command=self.cerrar_sesion_cb, 
            cursor="hand2", 
            pady=4,
            padx=15
        ).pack(side="bottom", pady=8)

        self.actualizar_tablas()
        self.llenar_todos_los_combos()
        self.verificar_mensajes_nuevos_al_iniciar()

    def obtener_rango_vecino(self, puntos):
        try:
            pts = float(puntos)
        except (ValueError, TypeError):
            pts = 0.0

        if pts > 300:
            return "👑 Leyenda Suprema"
        elif pts > 150:
            return "🌳 Guerrero Verde"
        elif pts > 50:
            return "🌿 Reciclador Activo"
        else:
            return "🌱 Eco-Novato"

    def llenar_todos_los_combos(self):
        for rol in ["vecino", "negocio", "desarrollador"]:
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
            rol_usuario = datos.get("rol", "")
            if rol_usuario == rol_tipo or (rol_tipo == "desarrollador" and rol_usuario in ["admin", "desarrollador"]):
                if uid == self.id_usuario:
                    continue

                nombre_usuario = datos.get("nombre", "Usuario")
                tiene_pendientes = any(m.get("dni_cliente") == uid and m.get("rol") == rol_usuario and not m.get("leido", True) for m in mensajes)
                
                icono_alerta = "🔔 [NUEVO] " if tiene_pendientes else "💬 "
                texto_item = f"{icono_alerta}{nombre_usuario} (ID: {uid})"
                
                opciones.append(texto_item)
                mapeo[texto_item] = uid

        cb['values'] = opciones
        if opciones:
            cb.current(0)
            self.cargar_chat_seleccionado(rol_tipo)
        else:
            cb.set(f"No hay usuarios registrados en {rol_tipo.capitalize()}")
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

        rol_lector = "admin" if self.es_admin_supremo else "desarrollador"
        marcar_chat_como_leido(dni, rol_lector)

        txt = ui["txt"]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == dni]

        if not msg_cliente:
            txt.insert(tk.END, f"💬 No hay mensajes previos con este usuario. Escribe abajo para iniciar la conversación.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")
                leido = m.get("leido", True)

                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"
                etiqueta = f"[{fecha}] {autor} ({rol}){check_leido}:\n"
                txt.insert(tk.END, etiqueta)
                txt.insert(tk.END, f"{texto}\n\n")

        txt.see(tk.END)
        txt.config(state="disabled")

    def responder_chat_por_rol(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion:
            messagebox.showwarning("Atención", "Seleccione una conversación válida de la bandeja primero.")
            return

        dni = ui["mapeo"].get(seleccion)
        texto = ui["ent"].get().strip()
        if not texto: return

        rol_autor = "admin" if self.es_admin_supremo else "desarrollador"
        guardar_mensaje_chat(
            dni_cliente=dni,
            autor_nombre=self.datos_sesion.get("nombre", "Soporte"),
            rol_autor=rol_autor,
            mensaje=texto
        )

        ui["ent"].delete(0, tk.END)
        self.cargar_chat_seleccionado(rol_tipo)
        self.llenar_combo_chats_por_rol(rol_tipo)

    def verificar_mensajes_nuevos_al_iniciar(self):
        mensajes = cargar_mensajes_chat()
        hay_nuevos = any(m.get("rol") in ["vecino", "negocio"] and not m.get("leido", True) for m in mensajes)
        if hay_nuevos:
            messagebox.showwarning(
                "💬 Nuevos Mensajes", 
                "¡Tienes mensajes nuevos pendientes por leer y responder en la pestaña 'Soporte (Bandeja)'!"
            )

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception:
            pass

    def pedir_texto_custom(self, titulo, mensaje):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("320x150")
        win.resizable(False, False)
        win.grab_set()

        if hasattr(self.root, 'icon_img'):
            win.iconphoto(False, self.root.icon_img)

        tk.Label(win, text=mensaje, font=("Arial", 10), pady=10).pack()
        ent = tk.Entry(win, font=("Arial", 10), width=25)
        ent.pack(pady=5)
        ent.focus_set()

        resultado = {"valor": None}

        def aceptar():
            resultado["valor"] = ent.get().strip()
            win.destroy()

        def cancelar():
            win.destroy()

        frame_btn = tk.Frame(win)
        frame_btn.pack(pady=10)
        
        tk.Button(frame_btn, text="Aceptar", bg="#2E7D32", fg="white", activeforeground="white", width=10, command=aceptar).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Cancelar", bg="#757575", fg="white", activeforeground="white", width=10, command=cancelar).pack(side="left", padx=5)

        self.root.wait_window(win)
        return resultado["valor"]

    def actualizar_tablas(self):
        for item in self.tabla_usr_vecinos.get_children(): self.tabla_usr_vecinos.delete(item)
        for item in self.tabla_usr_negocios.get_children(): self.tabla_usr_negocios.delete(item)
        for item in self.tabla_usr_devs.get_children(): self.tabla_usr_devs.delete(item)

        usuarios = cargar_usuarios()
        for uid, datos in usuarios.items():
            suspendido = datos.get("suspendido", False)
            if suspendido:
                motivo = datos.get("motivo_suspension", "Anómalo")
                estado_txt = f"🔴 Suspendido: {motivo}"
            else:
                estado_txt = "🟢 Activo"

            rol = datos.get("rol", "-")
            puntos = datos.get("puntos", "N/A")
            rango_txt = self.obtener_rango_vecino(puntos) if rol == "vecino" else "N/A (Personal)"
            justificacion = datos.get("justificacion_cliente", "")
            justif_txt = justificacion if justificacion else "-"

            tupla_datos = (
                uid, 
                datos.get("nombre", "-"), 
                rol.upper(), 
                estado_txt, 
                puntos,
                rango_txt,
                justif_txt
            )

            if rol == "vecino":
                self.tabla_usr_vecinos.insert("", "end", values=tupla_datos)
            elif rol == "negocio":
                self.tabla_usr_negocios.insert("", "end", values=tupla_datos)
            elif rol in ["admin", "desarrollador"]:
                self.tabla_usr_devs.insert("", "end", values=tupla_datos)

        for item in self.tabla_promos.get_children(): self.tabla_promos.delete(item)
        for p in cargar_promociones():
            self.tabla_promos.insert("", "end", values=(
                p.get("tienda_nombre", "Tienda"), 
                p.get("titulo", "-"), 
                f"S/ {p.get('precio_soles', 0):.2f}", 
                f"{p.get('puntos', 0)} PTS", 
                p.get("descripcion", "-")
            ))

        for item in self.tabla_tnd.get_children(): self.tabla_tnd.delete(item)
        for log in reversed(cargar_log_tiendas()):
            self.tabla_tnd.insert("", "end", values=(log.get("fecha"), log.get("tienda_id"), log.get("tienda_nombre"), log.get("dni_cliente"), log.get("puntos_descontados")))

        # CARGAR Y CLASIFICAR REGISTROS DE ACTIVIDAD CLIENTES
        tablas_cli = [
            self.tabla_cli_todos, 
            self.tabla_cli_abonos, 
            self.tabla_cli_canjes, 
            self.tabla_cli_entregas, 
            self.tabla_cli_resenas
        ]
        for t in tablas_cli:
            for item in t.get_children():
                t.delete(item)

        for log in reversed(cargar_log_clientes()):
            fecha = log.get("fecha", "-")
            dni = log.get("dni_cliente", "-")
            tipo = log.get("tipo", "")
            puntos = log.get("puntos", 0)
            detalle = log.get("detalle", "")

            valores = (fecha, dni, tipo, puntos, detalle)

            # 1. Todos los registros
            self.tabla_cli_todos.insert("", "end", values=valores)

            # 2. Sub-clasificaciones específicas
            if tipo in ["ABONO_RECICLAJE", "SUMA_ADMIN"]:
                self.tabla_cli_abonos.insert("", "end", values=valores)

            elif tipo in ["CANJE_OFERTA", "CANJE_TIENDA", "REDUCCION_ADMIN"]:
                self.tabla_cli_canjes.insert("", "end", values=valores)

            elif tipo in ["ENTREGA_OFERTA"]:
                self.tabla_cli_entregas.insert("", "end", values=valores)

            elif tipo in ["RESEÑA_TIENDA"]:
                # Separar el detalle de reseña en Estrellas y Comentario limpiamente
                estrellas_str = "⭐ (Sin calificación)"
                comentario_str = detalle

                if "Calificación:" in detalle:
                    partes = detalle.split("Calificación:")
                    if len(partes) > 1:
                        subpartes = partes[1].split("|")
                        estrellas_str = subpartes[0].strip()
                        if len(subpartes) > 1:
                            comentario_str = subpartes[1].replace("Reseña:", "").strip()

                valores_resena = (fecha, dni, estrellas_str, comentario_str)
                self.tabla_cli_resenas.insert("", "end", values=valores_resena)

        if self.es_admin_supremo:
            for item in self.tabla_dev.get_children(): self.tabla_dev.delete(item)
            for log in reversed(cargar_log_devs()):
                self.tabla_dev.insert("", "end", values=(log.get("fecha"), log.get("autor_id"), log.get("autor_nombre"), log.get("accion"), log.get("objetivo")))

    def dialogo_suspender_cuenta(self):
        uid = self.pedir_texto_custom("Suspender Cuenta", "Ingrese DNI / ID del usuario a suspender:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe en el sistema.")
            return

        motivo = self.pedir_texto_custom("Motivo de Suspensión", f"Ingrese el motivo para {usuarios[uid]['nombre']}:")
        if not motivo: return

        usuarios[uid]["suspendido"] = True
        usuarios[uid]["motivo_suspension"] = motivo
        guardar_usuarios(usuarios)

        rol_autor = "admin" if self.es_admin_supremo else "desarrollador"
        guardar_mensaje_chat(
            dni_cliente=uid,
            autor_nombre=self.datos_sesion.get("nombre", "Administración"),
            rol_autor=rol_autor,
            mensaje=f"🚨 AVISO DE SISTEMA: Su cuenta ha sido SUSPENDIDA. Motivo: {motivo}"
        )

        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUSPENDER_CUENTA", f"Suspendió al usuario {uid}. Motivo: {motivo}")
        self.actualizar_tablas()
        self.llenar_todos_los_combos()
        messagebox.showinfo("Éxito", f"La cuenta de {usuarios[uid]['nombre']} ha sido suspendida correctamente.")

    def dialogo_levantar_suspension(self):
        uid = self.pedir_texto_custom("Levantar Suspensión", "Ingrese DNI / ID del usuario a reactivar:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe.")
            return

        if not usuarios[uid].get("suspendido", False):
            messagebox.showinfo("Información", "Esta cuenta ya se encuentra activa.")
            return

        motivo_reactivacion = self.pedir_texto_custom(
            "Motivo de Reactivación", 
            f"Ingrese el motivo por el cual levanta la suspensión a {usuarios[uid]['nombre']}:"
        )
        if not motivo_reactivacion:
            messagebox.showwarning("Atención", "Debe ingresar un motivo para reactivar la cuenta.")
            return

        usuarios[uid]["suspendido"] = False
        usuarios[uid]["motivo_suspension"] = ""
        usuarios[uid]["justificacion_cliente"] = ""
        guardar_usuarios(usuarios)

        rol_autor = "admin" if self.es_admin_supremo else "desarrollador"
        guardar_mensaje_chat(
            dni_cliente=uid,
            autor_nombre=self.datos_sesion.get("nombre", "Administración"),
            rol_autor=rol_autor,
            mensaje=f"✅ AVISO DE SISTEMA: Se ha levantado la suspensión de su cuenta. Motivo de anulación: {motivo_reactivacion}"
        )

        registrar_accion_dev(
            self.id_usuario, 
            self.datos_sesion.get("nombre"), 
            "ACTIVAR_CUENTA", 
            f"Levantó suspensión a {uid}. Motivo Admin: {motivo_reactivacion}"
        )

        self.actualizar_tablas()
        self.llenar_todos_los_combos()
        messagebox.showinfo("Éxito", f"Se ha levantado la suspensión de {usuarios[uid]['nombre']}.\nMotivo: {motivo_reactivacion}")

    def dialogo_crear_cuenta(self):
        win_modal = tk.Toplevel(self.root)
        win_modal.title("Crear Nueva Cuenta")
        win_modal.geometry("340x360")
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text="Seleccione Tipo de Cuenta:", font=("Arial", 10, "bold")).pack(pady=5)
        roles_disponibles = ["vecino", "negocio"]
        if self.es_admin_supremo: roles_disponibles.append("desarrollador")

        cb_rol = ttk.Combobox(win_modal, values=roles_disponibles, state="readonly")
        cb_rol.pack(pady=5); cb_rol.current(0)

        tk.Label(win_modal, text="DNI / Código de Cuenta:").pack()
        ent_uid = tk.Entry(win_modal); ent_uid.pack(pady=2)

        tk.Label(win_modal, text="Nombre / Razón Social:").pack()
        ent_nom = tk.Entry(win_modal); ent_nom.pack(pady=2)

        tk.Label(win_modal, text="Correo Electrónico:").pack()
        ent_correo = tk.Entry(win_modal); ent_correo.pack(pady=2)

        tk.Label(win_modal, text="Teléfono / Celular:").pack()
        ent_tel = tk.Entry(win_modal); ent_tel.pack(pady=2)

        tk.Label(win_modal, text="Contraseña Inicial:").pack()
        ent_clave = tk.Entry(win_modal, show="*"); ent_clave.pack(pady=2)

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

        tk.Button(win_modal, text="Guardar Cuenta", bg="#2E7D32", fg="white", activeforeground="white", command=guardar).pack(pady=15)

    def dialogo_eliminar_cuenta(self):
        uid = self.pedir_texto_custom("Eliminar Cuenta", "Ingrese DNI / ID a eliminar:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe.")
            return

        rol_obj = usuarios[uid]["rol"]
        if rol_obj in ["admin", "desarrollador"] and not self.es_admin_supremo:
            messagebox.showerror("Acceso Denegado", "Solo el Admin Supremo puede eliminar a Desarrolladores o Admins.")
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente la cuenta de {usuarios[uid]['nombre']}?"):
            nom_removido = usuarios[uid]['nombre']
            del usuarios[uid]
            guardar_usuarios(usuarios)
            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "ELIMINAR_CUENTA", f"Eliminó la cuenta {uid} ({nom_removido})")
            self.actualizar_tablas()
            self.llenar_todos_los_combos()
            messagebox.showinfo("Éxito", "Cuenta eliminada.")

    def dialogo_registrar_reciclaje(self):
        dni = self.pedir_texto_custom("Sumar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "DNI no corresponde a un vecino.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden sumar puntos. La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA."
            )
            return

        win_modal = tk.Toplevel(self.root)
        win_modal.title("Sumar Puntos")
        win_modal.geometry("320x230")
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text=f"Vecino: {usuarios[dni]['nombre']}", font=("Arial", 10, "bold")).pack(pady=5)
        cb_mat = ttk.Combobox(win_modal, values=list(Material.TASAS.keys()), state="readonly"); cb_mat.pack(pady=5); cb_mat.current(0)
        tk.Label(win_modal, text="Peso en KG:").pack()
        ent_kg = tk.Entry(win_modal); ent_kg.pack(pady=5)

        def procesar():
            try:
                peso = float(ent_kg.get())
                mat = cb_mat.get()
                puntos = Material.calcular_puntos(mat, peso)
                
                usuarios[dni]["puntos"] = round(usuarios[dni]["puntos"] + puntos, 1)
                guardar_usuarios(usuarios)
                
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUMAR_PUNTOS", f"Abonó {puntos} pts a {dni} por {mat}")
                registrar_accion_cliente(dni, "ABONO_RECICLAJE", puntos, f"Reciclaje de {mat} ({peso} kg)")
                
                self.actualizar_tablas()
                win_modal.destroy()
                messagebox.showinfo("Éxito", f"Se sumaron {puntos} puntos.")
            except ValueError:
                messagebox.showerror("Error", "Ingrese un peso válido.")

        tk.Button(win_modal, text="Sumar Puntos", bg="#2E7D32", fg="white", activeforeground="white", command=procesar).pack(pady=10)

    def dialogo_reducir_puntos(self):
        dni = self.pedir_texto_custom("Restar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "Vecino no encontrado.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden restar puntos. La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA."
            )
            return
            
        pts_str = self.pedir_texto_custom("Restar Puntos", f"Puntos actuales: {usuarios[dni]['puntos']}\nCantidad a restar:")
        if pts_str:
            try:
                pts = float(pts_str)
                if pts > 0 and usuarios[dni]["puntos"] >= pts:
                    usuarios[dni]["puntos"] = round(usuarios[dni]["puntos"] - pts, 1)
                    guardar_usuarios(usuarios)
                    registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "RESTAR_PUNTOS", f"Restó {pts} pts a {dni}")
                    registrar_accion_cliente(dni, "REDUCCION_ADMIN", -pts, "Ajuste manual de administración")
                    self.actualizar_tablas()
                    messagebox.showinfo("Éxito", f"Se restaron {pts} puntos.")
                else:
                    messagebox.showerror("Error", "Puntos insuficientes o cantidad inválida.")
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad numérica válida.")

    def dialogo_cambiar_clave(self):
        uid = self.pedir_texto_custom("Renovar Clave", "Ingrese DNI/ID de la cuenta:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid in usuarios:
            nueva = self.pedir_texto_custom("Renovar Clave", f"Nueva contraseña para {usuarios[uid]['nombre']}:")
            if nueva:
                usuarios[uid]["clave"] = nueva
                guardar_usuarios(usuarios)
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CAMBIO_CLAVE", f"Modificó la clave de {uid}")
                messagebox.showinfo("Éxito", "Contraseña renovada correctamente.")
        else:
            messagebox.showerror("Error", "Usuario no encontrado.")

    def dialogo_editar_datos(self):
        uid = self.pedir_texto_custom("Editar Datos", "Ingrese DNI/ID:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        if usuarios[uid].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden editar los datos. La cuenta de {usuarios[uid]['nombre']} se encuentra SUSPENDIDA."
            )
            return

        nuevo_nom = self.pedir_texto_custom("Editar", "Nuevo Nombre:")
        nuevo_correo = self.pedir_texto_custom("Editar", "Nuevo Correo:")
        nuevo_tel = self.pedir_texto_custom("Editar", "Nuevo Celular:")
        
        if nuevo_nom: usuarios[uid]["nombre"] = nuevo_nom
        if nuevo_correo: usuarios[uid]["correo"] = nuevo_correo
        if nuevo_tel: usuarios[uid]["telefono"] = nuevo_tel

        guardar_usuarios(usuarios)
        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "EDITAR_DATOS", f"Actualizó datos personales de {uid}")
        self.actualizar_tablas()
        messagebox.showinfo("Éxito", "Datos actualizados.")

    def dialogo_ver_promociones_con_foto(self):
        win_promos = tk.Toplevel(self.root)
        win_promos.title("Vista Detallada de Ofertas en Sistema")
        win_promos.geometry("620x500")
        win_promos.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promos.iconphoto(False, self.root.icon_img)

        frame_main = tk.Frame(win_promos, bg="white")
        frame_main.pack(fill="both", expand=True, padx=10, pady=10)

        win_promos.referencias_img = []
        promos = cargar_promociones()

        if not promos:
            tk.Label(frame_main, text="No hay promociones registradas en el sistema.", font=("Arial", 11, "italic"), bg="white").pack(pady=40)
            return

        for p in promos:
            card = tk.Frame(frame_main, bg="#F5F5F5", bd=1, relief="solid", padx=10, pady=8)
            card.pack(fill="x", pady=5)

            ruta_foto = p.get("foto", "")
            if ruta_foto and os.path.exists(ruta_foto):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(ruta_foto).resize((65, 65), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    win_promos.referencias_img.append(img_tk)
                    tk.Label(card, image=img_tk, bg="#F5F5F5").pack(side="left", padx=(0, 10))
                except Exception:
                    tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#E0E0E0", width=8, height=4).pack(side="left", padx=(0, 10))
            else:
                tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#E0E0E0", width=8, height=4).pack(side="left", padx=10)

            info_text = f"🏪 Tienda: {p.get('tienda_nombre')} (ID: {p.get('tienda_id')})\n📌 Título: {p.get('titulo')}\n📝 Detalle: {p.get('descripcion')}\n💰 Precio: S/ {p.get('precio_soles', 0):.2f} ➔ {p.get('puntos', 0)} PTS"
            tk.Label(card, text=info_text, font=("Arial", 9), bg="#F5F5F5", justify="left").pack(side="left", anchor="w")