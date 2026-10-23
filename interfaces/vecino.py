import tkinter as tk
from tkinter import ttk, messagebox
import os
from datos.gestor import (
    cargar_usuarios, 
    cargar_log_clientes, 
    cargar_mensajes_chat, 
    guardar_mensaje_chat,
    cargar_promociones,
    guardar_usuarios,
    marcar_chat_como_leido
)

COLOR_FONDO_VECINO = "#E8F5E9"

class VentanaVecino:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        # --- 1. CARGAR DATOS Y VALIDAR ESTADO DE SUSPENSIÓN ---
        usuarios = cargar_usuarios()
        self.datos = usuarios.get(id_usuario, {})

        if self.datos.get("suspendido", False):
            self.mostrar_pantalla_suspendido()
            return  # Detiene la carga normal del panel si está suspendido

        # --- 2. CONFIGURACIÓN NORMAL DE LA VENTANA ---
        self.root.config(bg=COLOR_FONDO_VECINO)
        self.root.title("EcoPuntos - Mi Cuenta Vecinal")
        self.root.geometry("950x680")
        self.root.resizable(False, False)

        self.aplicar_icono()

        # Cargar Imagen de Fondo (Fondo_vecino.png)
        ruta_fondo = os.path.join("img", "fondo_vecino.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Aviso fondo vecino: {e}")

        # Header Superior
        frame_top = tk.Frame(self.root, bg="#2E7D32")
        frame_top.pack(fill="x")
        
        tk.Label(
            frame_top, 
            text=f"👤 Panel del Vecino: {self.datos.get('nombre', 'Cliente')} | DNI: {self.id_usuario}", 
            font=("Arial", 12, "bold"), 
            fg="white", 
            bg="#2E7D32", 
            pady=10
        ).pack()

        # Balance Principal y Gamificación (Insignias y Rangos)
        frame_card = tk.Frame(self.root, bg="white", bd=1, relief="solid", padx=20, pady=10)
        frame_card.pack(fill="x", padx=15, pady=10)

        # Izquierda: Puntos y Rango
        frame_info_saldo = tk.Frame(frame_card, bg="white")
        frame_info_saldo.pack(side="left")

        tk.Label(frame_info_saldo, text="Saldo Disponible:", font=("Arial", 9, "bold"), bg="white", fg="#555555").pack(anchor="w")
        
        row_pts_rango = tk.Frame(frame_info_saldo, bg="white")
        row_pts_rango.pack(anchor="w", pady=2)

        self.lbl_puntos = tk.Label(row_pts_rango, text=f"{self.datos.get('puntos', 0)} PTS", font=("Arial", 20, "bold"), fg="#2E7D32", bg="white")
        self.lbl_puntos.pack(side="left", padx=(0, 15))

        # Etiqueta de Rango / Insignia
        rango_actual = self.obtener_rango_vecino(self.datos.get('puntos', 0))
        self.lbl_rango = tk.Label(row_pts_rango, text=f"Rango: {rango_actual}", font=("Arial", 10, "bold"), fg="#E65100", bg="#FFF8E1", padx=8, relief="solid", bd=1)
        self.lbl_rango.pack(side="left")

        tk.Button(frame_card, text="🔄 Actualizar", bg="#1976D2", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.actualizar_todo, cursor="hand2").pack(side="right")

        # Control de Pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=5)

        tab_promos = ttk.Frame(notebook)
        tab_reciclaje = ttk.Frame(notebook)
        tab_movimientos = ttk.Frame(notebook)
        tab_chat = ttk.Frame(notebook)
        tab_seguridad = ttk.Frame(notebook)  # <--- NUEVA PESTAÑA

        notebook.add(tab_promos, text="🛍️ Catálogo de Ofertas")
        notebook.add(tab_reciclaje, text="♻️ Historial de Reciclaje (Detallado)")
        notebook.add(tab_movimientos, text="📊 Movimientos de Puntos (+ / -)")
        notebook.add(tab_chat, text="💬 Soporte / Chat con Devs y Admin")
        notebook.add(tab_seguridad, text="🔐 Seguridad y Recuperación")  # <--- AGREGADA

        # --- 1. CATÁLOGO DE PROMOCIONES / OFERTAS ---
        self.frame_promos_scroll = tk.Frame(tab_promos, bg="white")
        self.frame_promos_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # --- FUNCIÓN AUXILIAR DE TABLAS ---
        def crear_tabla_scroll(parent, cols, config):
            frame = ttk.Frame(parent)
            frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            sy = ttk.Scrollbar(frame, orient="vertical")
            sx = ttk.Scrollbar(frame, orient="horizontal")
            
            tabla = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=sy.set, xscrollcommand=sx.set)
            sy.config(command=tabla.yview)
            sx.config(command=tabla.xview)
            
            sy.pack(side="right", fill="y")
            sx.pack(side="bottom", fill="x")
            tabla.pack(side="left", fill="both", expand=True)

            for col, txt, w in config:
                tabla.heading(col, text=txt)
                tabla.column(col, width=w, minwidth=70, stretch=True)
            return tabla

        # 2. TABLA DETALLADA DE RECICLAJE
        cols_rec = ("fecha", "material", "peso", "puntos")
        config_rec = [
            ("fecha", "Fecha / Hora", 160),
            ("material", "Material Reciclado", 280),
            ("peso", "Peso Entregado (kg)", 140),
            ("puntos", "Puntos Obt.", 120)
        ]
        self.tabla_reciclaje = crear_tabla_scroll(tab_reciclaje, cols_rec, config_rec)

        # 3. TABLA DE MOVIMIENTOS
        cols_mov = ("fecha", "tipo", "puntos", "detalle")
        config_mov = [
            ("fecha", "Fecha / Hora", 160),
            ("tipo", "Tipo Operación", 150),
            ("puntos", "Puntos (+ / -)", 120),
            ("detalle", "Detalle / Concepto", 300)
        ]
        self.tabla_movimientos = crear_tabla_scroll(tab_movimientos, cols_mov, config_mov)

        # 4. CANAL DE CHAT CON DEVS Y ADMIN
        frame_chat_box = tk.Frame(tab_chat, bg="white", padx=10, pady=10)
        frame_chat_box.pack(fill="both", expand=True, padx=5, pady=5)

        self.txt_chat = tk.Text(frame_chat_box, state="disabled", font=("Arial", 10), bg="#F9F9F9", wrap="word")
        self.txt_chat.pack(fill="both", expand=True, pady=(0, 10))

        frame_input = tk.Frame(frame_chat_box, bg="white")
        frame_input.pack(fill="x")

        self.ent_msg = tk.Entry(frame_input, font=("Arial", 10), bg="#F0F0F0")
        self.ent_msg.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        self.ent_msg.bind("<Return>", lambda event: self.enviar_mensaje())

        tk.Button(frame_input, text="Enviar ✉️", bg="#2E7D32", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.enviar_mensaje, cursor="hand2", padx=15).pack(side="right")

        # --- 5. PESTAÑA DE SEGURIDAD Y RECUPERACIÓN ---
        frame_seg_box = tk.Frame(tab_seguridad, bg="white", padx=20, pady=20)
        frame_seg_box.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(
            frame_seg_box, 
            text="🔐 Configuración de Recuperación de Cuenta", 
            font=("Arial", 12, "bold"), 
            fg="#2E7D32", 
            bg="white"
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            frame_seg_box, 
            text="Establezca una pregunta y respuesta secreta. Esto le permitirá recuperar su contraseña de forma autónoma si llega a olvidarla.", 
            font=("Arial", 10), 
            fg="#555555", 
            bg="white",
            wraplength=850,
            justify="left"
        ).pack(anchor="w", pady=(0, 15))

        tk.Label(frame_seg_box, text="Pregunta Secreta actual:", font=("Arial", 9, "bold"), bg="white").pack(anchor="w")
        self.lbl_pregunta_actual = tk.Label(
            frame_seg_box, 
            text=f"\"{self.datos.get('pregunta_secreta', 'No configurada')}\"", 
            font=("Arial", 10, "italic"), 
            fg="#1976D2", 
            bg="white"
        )
        self.lbl_pregunta_actual.pack(anchor="w", pady=(2, 15))

        tk.Label(frame_seg_box, text="Nueva Pregunta Secreta (ej: ¿Nombre de tu primera mascota?):", font=("Arial", 9, "bold"), bg="white").pack(anchor="w")
        self.ent_nueva_pregunta = tk.Entry(frame_seg_box, font=("Arial", 10), width=50, bg="#F0F0F0")
        self.ent_nueva_pregunta.pack(anchor="w", pady=(2, 10), ipady=3)

        tk.Label(frame_seg_box, text="Nueva Respuesta Secreta:", font=("Arial", 9, "bold"), bg="white").pack(anchor="w")
        self.ent_nueva_respuesta = tk.Entry(frame_seg_box, font=("Arial", 10), width=50, bg="#F0F0F0", show="*")
        self.ent_nueva_respuesta.pack(anchor="w", pady=(2, 15), ipady=3)

        def guardar_seguridad_vecino():
            nueva_p = self.ent_nueva_pregunta.get().strip()
            nueva_r = self.ent_nueva_respuesta.get().strip()

            if not nueva_p or not nueva_r:
                messagebox.showwarning("Atención", "Por favor complete ambos campos para actualizar su seguridad.")
                return

            usuarios = cargar_usuarios()
            if self.id_usuario in usuarios:
                usuarios[self.id_usuario]["pregunta_secreta"] = nueva_p
                usuarios[self.id_usuario]["respuesta_secreta"] = nueva_r.lower()
                guardar_usuarios(usuarios)
                
                # Actualizar datos locales y etiqueta visual
                self.datos = usuarios[self.id_usuario]
                self.lbl_pregunta_actual.config(text=f"\"{nueva_p}\"")
                
                self.ent_nueva_pregunta.delete(0, tk.END)
                self.ent_nueva_respuesta.delete(0, tk.END)
                
                messagebox.showinfo("Éxito", "¡Su contraseña de recuperación ha sido actualizada correctamente!")
            else:
                messagebox.showerror("Error", "No se encontró el usuario en la base de datos.")

        tk.Button(
            frame_seg_box, 
            text="💾 Guardar Pregunta de Recuperación", 
            bg="#2E7D32", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            relief="flat",
            command=guardar_seguridad_vecino,
            cursor="hand2",
            padx=10,
            pady=5
        ).pack(anchor="w")

        self.actualizar_todo()

        # 🔔 Verificar si hay respuestas nuevas del admin/dev al iniciar sesión
        self.verificar_mensajes_nuevos_vecino()

        # Botón Cerrar Sesión
        tk.Button(self.root, text="🚪 Cerrar Sesión", bg="#757575", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.cerrar_sesion_cb, cursor="hand2", pady=4).pack(pady=8)

    def obtener_rango_vecino(self, puntos):
        """Calcula el rango/insignia ecológico según los puntos acumulados."""
        try:
            pts = float(puntos)
        except (ValueError, TypeError):
            pts = 0.0

        if pts > 300:
            return "👑 Leyenda Ecológica Suprema"
        elif pts > 150:
            return "🌳 Guerrero Verde"
        elif pts > 50:
            return "🌿 Reciclador Activo"
        else:
            return "🌱 Eco-Novato"

    def verificar_mensajes_nuevos_vecino(self):
        """Verifica si el admin/dev ha respondido al vecino y hay mensajes sin leer."""
        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == self.id_usuario]
        hay_nuevos = any(m.get("rol") in ["admin", "desarrollador"] and not m.get("leido", False) for m in msg_cliente)
        
        if hay_nuevos:
            messagebox.showinfo(
                "💬 Respuesta de Soporte", 
                "¡Tienes nuevas respuestas de la administración o soporte en tu chat!"
            )

    def mostrar_pantalla_suspendido(self):
        """Muestra una interfaz de bloqueo si la cuenta se encuentra suspendida."""
        self.root.config(bg="#F8D7DA")
        self.root.title("Cuenta Suspendida - EcoPuntos")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        frame_aviso = tk.Frame(self.root, bg="#F8D7DA", padx=20, pady=20)
        frame_aviso.pack(fill="both", expand=True)

        tk.Label(
            frame_aviso, 
            text="⚠️ CUENTA SUSPENDIDA TEMPORALMENTE", 
            font=("Arial", 15, "bold"), 
            fg="#721C24", 
            bg="#F8D7DA"
        ).pack(pady=10)

        motivo = self.datos.get("motivo_suspension", "Actividad anómala detectada en puntos o canje de promociones.")
        tk.Label(
            frame_aviso, 
            text=f"Motivo del Administrador:\n{motivo}", 
            font=("Arial", 10), 
            fg="#721C24", 
            bg="#F8D7DA",
            justify="center",
            wraplength=550
        ).pack(pady=10)

        tk.Label(
            frame_aviso, 
            text="Si consideras que esto es un error, redacta una justificación para el administrador:", 
            font=("Arial", 10, "bold"), 
            fg="#333333", 
            bg="#F8D7DA"
        ).pack(anchor="w", padx=20, pady=(10, 0))

        txt_justificacion = tk.Text(frame_aviso, width=70, height=6, font=("Arial", 10))
        txt_justificacion.pack(pady=5)
        
        justificacion_previa = self.datos.get("justificacion_cliente", "")
        if justificacion_previa:
            txt_justificacion.insert("1.0", justificacion_previa)

        def enviar_justificacion():
            texto = txt_justificacion.get("1.0", tk.END).strip()
            if not texto:
                messagebox.showwarning("Atención", "Por favor ingresa una justificación antes de enviar.")
                return

            usuarios = cargar_usuarios()
            if self.id_usuario in usuarios:
                usuarios[self.id_usuario]["justificacion_cliente"] = texto
                guardar_usuarios(usuarios)
                messagebox.showinfo("Enviado", "Tu justificación ha sido enviada al administrador correctamente.")
            else:
                messagebox.showerror("Error", "No se encontró el usuario en la base de datos.")

        tk.Button(
            frame_aviso, 
            text="Enviar Justificación al Admin 📤", 
            bg="#28A745", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            relief="flat",
            command=enviar_justificacion,
            cursor="hand2"
        ).pack(pady=10)

        tk.Button(
            frame_aviso, 
            text="🚪 Cerrar Sesión", 
            bg="#757575", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            relief="flat", 
            command=self.cerrar_sesion_cb, 
            cursor="hand2"
        ).pack(pady=5)

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception:
            pass

    def actualizar_todo(self):
        usuarios = cargar_usuarios()
        self.datos = usuarios.get(self.id_usuario, {})
        
        puntos_actuales = self.datos.get('puntos', 0)
        self.lbl_puntos.config(text=f"{puntos_actuales} PTS")
        
        # Actualizar insignia/rango dinámicamente
        nuevo_rango = self.obtener_rango_vecino(puntos_actuales)
        self.lbl_rango.config(text=f"Rango: {nuevo_rango}")

        self.cargar_catalogo_promociones()

        for item in self.tabla_reciclaje.get_children(): self.tabla_reciclaje.delete(item)
        for item in self.tabla_movimientos.get_children(): self.tabla_movimientos.delete(item)

        historial = cargar_log_clientes()
        for reg in reversed(historial):
            if reg.get("dni_cliente") == self.id_usuario:
                tipo = reg.get("tipo", "")
                puntos = reg.get("puntos", 0)
                fecha = reg.get("fecha", "-")
                detalle = reg.get("detalle", "")

                self.tabla_movimientos.insert("", "end", values=(fecha, tipo, puntos, detalle))

                if tipo == "ABONO_RECICLAJE" and "Reciclaje de" in detalle:
                    try:
                        info = detalle.replace("Reciclaje de ", "").replace(" kg)", "")
                        partes = info.split(" (")
                        material = partes[0]
                        peso = partes[1] if len(partes) > 1 else "-"
                    except Exception:
                        material, peso = detalle, "-"
                    
                    self.tabla_reciclaje.insert("", "end", values=(fecha, material, peso, puntos))

        self.cargar_chat()

    def cargar_catalogo_promociones(self):
            for w in self.frame_promos_scroll.winfo_children():
                w.destroy()

            promos = cargar_promociones()
            if not promos:
                tk.Label(
                    self.frame_promos_scroll, 
                    text="🛍️ No hay promociones disponibles en este momento.", 
                    font=("Arial", 11, "italic"), 
                    bg="white", 
                    fg="#757575"
                ).pack(pady=40)
                return

            self.referencias_img_vecino = []

            from interfaces.utils import obtener_imagen_miniatura

            for p in promos:
                card = tk.Frame(self.frame_promos_scroll, bg="#FFF8E1", bd=1, relief="solid", padx=10, pady=10)
                card.pack(fill="x", pady=5, padx=5)

                ruta_foto = p.get("foto", "")
                img_tk = obtener_imagen_miniatura(ruta_foto, ancho=75, alto=75)

                if img_tk:
                    self.referencias_img_vecino.append(img_tk)
                    lbl_img = tk.Label(card, image=img_tk, bg="#FFF8E1")
                    lbl_img.pack(side="left", padx=(0, 12))
                else:
                    lbl_no_img = tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#FFE0B2", width=10, height=4)
                    lbl_no_img.pack(side="left", padx=(0, 12))

                frame_info = tk.Frame(card, bg="#FFF8E1")
                frame_info.pack(side="left", fill="both", expand=True)

                tk.Label(frame_info, text=f"🏪 {p.get('tienda_nombre', 'Tienda Afiliada')}", font=("Arial", 9, "bold"), fg="#E65100", bg="#FFF8E1").pack(anchor="w")
                tk.Label(frame_info, text=f"📌 {p.get('titulo', 'Oferta')}", font=("Arial", 11, "bold"), bg="#FFF8E1").pack(anchor="w", pady=(2, 0))
                tk.Label(frame_info, text=f"📝 {p.get('descripcion', '')}", font=("Arial", 9), fg="#424242", bg="#FFF8E1").pack(anchor="w")
                
                tk.Label(
                    frame_info, 
                    text=f"Precio Normal: S/ {p.get('precio_soles', 0):.2f}  ➔  Costo: {p.get('puntos', 0)} PTS", 
                    font=("Arial", 10, "bold"), 
                    fg="#2E7D32", 
                    bg="#FFF8E1"
                ).pack(anchor="w", pady=(4, 0))

    def cargar_chat(self):
        marcar_chat_como_leido(self.id_usuario, "vecino")

        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == self.id_usuario]

        if not msg_cliente:
            self.txt_chat.insert(tk.END, "💬 Inicia una conversación con el equipo de soporte, administradores o desarrolladores.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")
                leido = m.get("leido", True)

                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"

                etiqueta = f"[{fecha}] {autor} ({rol}){check_leido}:\n"
                self.txt_chat.insert(tk.END, etiqueta)
                self.txt_chat.insert(tk.END, f"{texto}\n\n")

        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def enviar_mensaje(self):
        texto = self.ent_msg.get().strip()
        if not texto: return

        guardar_mensaje_chat(
            dni_cliente=self.id_usuario,
            autor_nombre=self.datos.get("nombre", "Vecino"),
            rol_autor="vecino",
            mensaje=texto
        )

        self.ent_msg.delete(0, tk.END)
        self.cargar_chat()