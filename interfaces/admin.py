import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, guardar_usuarios, registrar_accion_dev, 
    cargar_log_devs, cargar_log_tiendas, cargar_log_clientes, registrar_accion_cliente,
    cargar_promociones, cargar_mensajes_chat, guardar_mensaje_chat
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
        self.root.geometry("950x680")
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
        ).pack()

        # 3. BOTONES DE ACCIÓN DE GESTIÓN
        frame_acciones = tk.LabelFrame(
            self.root, 
            text=" Acciones de Gestión ", 
            font=("Arial", 10, "bold"), 
            padx=10, 
            pady=6, 
            bg="white"
        )
        frame_acciones.pack(fill="x", padx=15, pady=6)

        btn_box = tk.Frame(frame_acciones, bg="white")
        btn_box.pack(fill="x")

        tk.Button(btn_box, text="➕ Crear Cuenta", bg="#2E7D32", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_crear_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="❌ Eliminar Cuenta", bg="#C62828", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_eliminar_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="♻️ Sumar Puntos", bg="#1976D2", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_registrar_reciclaje, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="➖ Restar Puntos", bg="#D32F2F", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_reducir_puntos, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔑 Renovar Clave", bg="#F57C00", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_cambiar_clave, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✏️ Editar Datos", bg="#00897B", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_editar_datos, cursor="hand2").pack(side="left", padx=3, pady=2)

        # 4. CONTROL DE PESTAÑAS
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=5)

        tab_usuarios = ttk.Frame(notebook)
        tab_promos = ttk.Frame(notebook)
        tab_log_tiendas = ttk.Frame(notebook)
        tab_log_clientes = ttk.Frame(notebook)
        tab_chat = ttk.Frame(notebook)

        notebook.add(tab_usuarios, text="👥 Cuentas")
        notebook.add(tab_promos, text="🛍️ Promociones Activas")
        notebook.add(tab_log_tiendas, text="🏪 Actividad Tiendas")
        notebook.add(tab_log_clientes, text="♻️ Actividad Clientes")
        notebook.add(tab_chat, text="💬 Soporte Vecinal")

        if self.es_admin_supremo:
            self.tab_log_devs = ttk.Frame(notebook)
            notebook.add(self.tab_log_devs, text="🕵️ Actividad Devs (Solo Admin)")

        # FUNCIÓN AUXILIAR DE TABLAS
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
                tabla.column(col, width=width, minwidth=80, stretch=True)

            return tabla

        # 1. TABLA USUARIOS
        cols_usr = ("id", "nombre", "rol", "telefono", "correo", "puntos")
        config_usr = [
            ("id", "DNI / ID", 110),
            ("nombre", "Nombre / Comercio", 200),
            ("rol", "Rol", 90),
            ("telefono", "Celular", 110),
            ("correo", "Correo Electrónico", 220),
            ("puntos", "Puntos", 80)
        ]
        self.tabla_usr = crear_tabla_con_scroll(tab_usuarios, cols_usr, config_usr)


# --- PESTAÑA: PROMOCIONES ACTIVAS ---
        # 1. Botón superior para abrir la vista visual con fotos
        tk.Button(
            tab_promos, 
            text="🖼️ Abrir Vista Visual con Fotos", 
            bg="#1976D2", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            relief="flat", 
            command=self.dialogo_ver_promociones_con_foto, 
            cursor="hand2",
            padx=10,
            pady=4
        ).pack(anchor="e", padx=5, pady=(5, 0))

        # 2. Configuración y creación de la tabla
        cols_pr = ("tienda", "titulo", "precio_soles", "puntos", "descripcion")
        config_pr = [
            ("tienda", "Comercio / Tienda", 180),
            ("titulo", "Título Oferta", 180),
            ("precio_soles", "Precio (S/)", 100),
            ("puntos", "Costo (PTS)", 100),
            ("descripcion", "Descripción", 250)
        ]
        self.tabla_promos = crear_tabla_con_scroll(tab_promos, cols_pr, config_pr)



        # 3. TABLA LOG TIENDAS
        cols_tnd = ("fecha", "tienda_id", "tienda_nombre", "dni_cliente", "puntos")
        config_tnd = [
            ("fecha", "Fecha / Hora", 150),
            ("tienda_id", "ID Tienda", 100),
            ("tienda_nombre", "Nombre Comercio", 180),
            ("dni_cliente", "DNI Cliente / Ref", 130),
            ("puntos", "Pts / Detalle", 140)
        ]
        self.tabla_tnd = crear_tabla_con_scroll(tab_log_tiendas, cols_tnd, config_tnd)

        # 4. TABLA LOG CLIENTES
        cols_cli = ("fecha", "dni_cliente", "tipo", "puntos", "detalle")
        config_cli = [
            ("fecha", "Fecha / Hora", 150),
            ("dni_cliente", "DNI Cliente", 110),
            ("tipo", "Tipo Operación", 130),
            ("puntos", "Puntos (+/-)", 100),
            ("detalle", "Detalle de Operación", 280)
        ]
        self.tabla_cli = crear_tabla_con_scroll(tab_log_clientes, cols_cli, config_cli)

        # 5. TABLA LOG DEVS (Solo Admin)
        if self.es_admin_supremo:
            cols_dev = ("fecha", "autor_id", "autor_nombre", "accion", "objetivo")
            config_dev = [
                ("fecha", "Fecha / Hora", 150),
                ("autor_id", "ID Dev/Admin", 110),
                ("autor_nombre", "Nombre Dev", 160),
                ("accion", "Acción Ejecutada", 150),
                ("objetivo", "Usuario / Cuenta Afectada", 230)
            ]
            self.tabla_dev = crear_tabla_con_scroll(self.tab_log_devs, cols_dev, config_dev)

        # 6. CANAL DE CHAT CON VECINOS
        frame_chat_box = tk.Frame(tab_chat, bg="white", padx=10, pady=10)
        frame_chat_box.pack(fill="both", expand=True)

        frame_top_chat = tk.Frame(frame_chat_box, bg="white")
        frame_top_chat.pack(fill="x", pady=(0, 5))

        tk.Label(frame_top_chat, text="Seleccionar Vecino por DNI:", font=("Arial", 9, "bold"), bg="white").pack(side="left", padx=5)
        self.ent_dni_chat = tk.Entry(frame_top_chat, font=("Arial", 10), width=15)
        self.ent_dni_chat.pack(side="left", padx=5)
        
        tk.Button(frame_top_chat, text="🔍 Cargar Chat", bg="#1976D2", fg="white", font=("Arial", 8, "bold"), relief="flat", command=self.cargar_chat_vecino).pack(side="left", padx=5)

        self.txt_chat = tk.Text(frame_chat_box, state="disabled", font=("Arial", 10), bg="#F9F9F9", wrap="word")
        self.txt_chat.pack(fill="both", expand=True, pady=5)

        frame_input_chat = tk.Frame(frame_chat_box, bg="white")
        frame_input_chat.pack(fill="x")

        self.ent_msg_admin = tk.Entry(frame_input_chat, font=("Arial", 10), bg="#F0F0F0")
        self.ent_msg_admin.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
        self.ent_msg_admin.bind("<Return>", lambda e: self.responder_chat_vecino())

        tk.Button(frame_input_chat, text="Responder ✉️", bg="#2E7D32", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.responder_chat_vecino).pack(side="right")

        self.actualizar_tablas()

        tk.Button(self.root, text="🚪 Cerrar Sesión", bg="#757575", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.cerrar_sesion_cb, cursor="hand2", pady=4).pack(pady=6)

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
        
        tk.Button(frame_btn, text="Aceptar", bg="#2E7D32", fg="white", width=10, command=aceptar).pack(side="left", padx=5)
        tk.Button(frame_btn, text="Cancelar", bg="#757575", fg="white", width=10, command=cancelar).pack(side="left", padx=5)

        self.root.wait_window(win)
        return resultado["valor"]

    def actualizar_tablas(self):
        # 1. Usuarios
        for item in self.tabla_usr.get_children(): self.tabla_usr.delete(item)
        usuarios = cargar_usuarios()
        for uid, datos in usuarios.items():
            self.tabla_usr.insert("", "end", values=(uid, datos.get("nombre", "-"), datos.get("rol", "-").upper(), datos.get("telefono", "-"), datos.get("correo", "-"), datos.get("puntos", "N/A")))

        # 2. Promociones Activas
        for item in self.tabla_promos.get_children(): self.tabla_promos.delete(item)
        for p in cargar_promociones():
            self.tabla_promos.insert("", "end", values=(
                p.get("tienda_nombre", "Tienda"), 
                p.get("titulo", "-"), 
                f"S/ {p.get('precio_soles', 0):.2f}", 
                f"{p.get('puntos', 0)} PTS", 
                p.get("descripcion", "-")
            ))

        # 3. Log Tiendas
        for item in self.tabla_tnd.get_children(): self.tabla_tnd.delete(item)
        for log in reversed(cargar_log_tiendas()):
            self.tabla_tnd.insert("", "end", values=(log.get("fecha"), log.get("tienda_id"), log.get("tienda_nombre"), log.get("dni_cliente"), log.get("puntos_descontados")))

        # 4. Log Clientes
        for item in self.tabla_cli.get_children(): self.tabla_cli.delete(item)
        for log in reversed(cargar_log_clientes()):
            self.tabla_cli.insert("", "end", values=(log.get("fecha"), log.get("dni_cliente"), log.get("tipo"), log.get("puntos"), log.get("detalle")))

        # 5. Log Devs
        if self.es_admin_supremo:
            for item in self.tabla_dev.get_children(): self.tabla_dev.delete(item)
            for log in reversed(cargar_log_devs()):
                self.tabla_dev.insert("", "end", values=(log.get("fecha"), log.get("autor_id"), log.get("autor_nombre"), log.get("accion"), log.get("objetivo")))

    def cargar_chat_vecino(self):
        dni = self.ent_dni_chat.get().strip()
        if not dni:
            messagebox.showwarning("Atención", "Ingrese el DNI del vecino para cargar su conversación.")
            return

        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == dni]

        if not msg_cliente:
            self.txt_chat.insert(tk.END, f"💬 No hay mensajes registrados con el DNI {dni}.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")

                etiqueta = f"[{fecha}] {autor} ({rol}):\n"
                self.txt_chat.insert(tk.END, etiqueta)
                self.txt_chat.insert(tk.END, f"{texto}\n\n")

        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def responder_chat_vecino(self):
        dni = self.ent_dni_chat.get().strip()
        texto = self.ent_msg_admin.get().strip()

        if not dni:
            messagebox.showwarning("Atención", "Ingrese el DNI del vecino antes de enviar el mensaje.")
            return
        if not texto: return

        rol_autor = "admin" if self.es_admin_supremo else "desarrollador"
        guardar_mensaje_chat(
            dni_cliente=dni,
            autor_nombre=self.datos_sesion.get("nombre", "Soporte"),
            rol_autor=rol_autor,
            mensaje=texto
        )

        self.ent_msg_admin.delete(0, tk.END)
        self.cargar_chat_vecino()

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
                "rol": rol, "nombre": nom, "correo": correo or "-", "telefono": tel or "-", "clave": clave, "puntos": 0 if rol == "vecino" else "N/A"
            }
            guardar_usuarios(usuarios)
            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CREAR_CUENTA", f"Creó cuenta {uid} ({rol.upper()})")
            
            self.actualizar_tablas()
            win_modal.destroy()
            messagebox.showinfo("Éxito", f"Cuenta de tipo '{rol.upper()}' creada.")

        tk.Button(win_modal, text="Guardar Cuenta", bg="#2E7D32", fg="white", command=guardar).pack(pady=15)

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
            messagebox.showinfo("Éxito", "Cuenta eliminada.")

    def dialogo_registrar_reciclaje(self):
        dni = self.pedir_texto_custom("Sumar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "DNI no corresponde a un vecino.")
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

        tk.Button(win_modal, text="Sumar Puntos", bg="#2E7D32", fg="white", command=procesar).pack(pady=10)

    def dialogo_reducir_puntos(self):
        dni = self.pedir_texto_custom("Restar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "Vecino no encontrado.")
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
        if uid in usuarios:
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
        else:
            messagebox.showerror("Error", "Usuario no encontrado.")


    #Ver promociones con foto
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

            # Foto
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
                tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#E0E0E0", width=8, height=4).pack(side="left", padx=(0, 10))

            info_text = f"🏪 Tienda: {p.get('tienda_nombre')} (ID: {p.get('tienda_id')})\n📌 Título: {p.get('titulo')}\n📝 Detalle: {p.get('descripcion')}\n💰 Precio: S/ {p.get('precio_soles', 0):.2f} ➔ {p.get('puntos', 0)} PTS"
            tk.Label(card, text=info_text, font=("Arial", 9), bg="#F5F5F5", justify="left").pack(side="left", anchor="w")