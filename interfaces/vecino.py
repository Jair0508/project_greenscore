import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, 
    cargar_log_clientes, 
    cargar_mensajes_chat, 
    guardar_mensaje_chat,
    cargar_promociones,
    guardar_promociones,
    guardar_usuarios,
    marcar_chat_como_leido,
    registrar_accion_tienda,
    registrar_accion_cliente
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

        # Botón de Actualizar y Guía
        tk.Button(frame_card, text="🔄 Actualizar", bg="#1976D2", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.actualizar_todo, cursor="hand2").pack(side="right")
        
        tk.Button(
            frame_card, 
            text="📋 Guía de Entrega", 
            bg="#0288D1", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            relief="flat", 
            command=self.mostrar_guia_condiciones, 
            cursor="hand2",
            padx=8
        ).pack(side="right", padx=(0, 8))

        # Control de Pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=5)

        tab_promos = ttk.Frame(notebook)
        tab_reciclaje = ttk.Frame(notebook)
        tab_movimientos = ttk.Frame(notebook)
        tab_chat = ttk.Frame(notebook)
        tab_seguridad = ttk.Frame(notebook)

        notebook.add(tab_promos, text="🛍️ Catálogo de Ofertas")
        notebook.add(tab_reciclaje, text="♻️ Historial de Reciclaje (Detallado)")
        notebook.add(tab_movimientos, text="📊 Movimientos de Puntos (+ / -)")
        notebook.add(tab_chat, text="💬 Soporte / Chat con Devs y Admin")
        notebook.add(tab_seguridad, text="🔐 Seguridad y Recuperación")

        # --- 1. CATÁLOGO DE PROMOCIONES / OFERTAS CON CANJE Y ESTRELLAS ---
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
        self.verificar_mensajes_nuevos_vecino()

        # Botón Cerrar Sesión
        tk.Button(self.root, text="🚪 Cerrar Sesión", bg="#757575", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.cerrar_sesion_cb, cursor="hand2", pady=4).pack(pady=8)

    def canjear_oferta(self, promo_index):
        """Procesa el canje de la oferta, descuenta puntos, reduce stock y abre reseña con estrellas."""
        promos = cargar_promociones()
        if promo_index < 0 or promo_index >= len(promos):
            messagebox.showerror("Error", "La promoción ya no está disponible.")
            return

        promo = promos[promo_index]
        costo_pts = promo.get("puntos", 0)
        stock_actual = promo.get("stock", 10)
        tienda_id = promo.get("tienda_id")
        tienda_nombre = promo.get("tienda_nombre", "Bodega")

        usuarios = cargar_usuarios()
        saldo_vecino = usuarios.get(self.id_usuario, {}).get("puntos", 0.0)

        if saldo_vecino < costo_pts:
            messagebox.showerror("Puntos Insuficientes", f"No tienes suficientes puntos.\nNecesitas {costo_pts} PTS y tienes {saldo_vecino} PTS.")
            return

        if isinstance(stock_actual, int) and stock_actual <= 0:
            messagebox.showwarning("Agotado", "Lo sentimos, esta oferta ya no tiene stock disponible.")
            return

        if not messagebox.askyesno("Confirmar Canje", f"¿Canjear '{promo['titulo']}' por {costo_pts} PTS en {tienda_nombre}?"):
            return

        # 1. Descontar puntos al vecino
        usuarios[self.id_usuario]["puntos"] = round(saldo_vecino - costo_pts, 1)
        guardar_usuarios(usuarios)

        # 2. Reducir stock o eliminar si llega a 0
        if isinstance(stock_actual, int):
            promo["stock"] = stock_actual - 1
            if promo["stock"] <= 0:
                promos.pop(promo_index)
            else:
                promos[promo_index] = promo
            guardar_promociones(promos)

        # 3. Registrar logs
        try:
            registrar_accion_tienda(tienda_id, tienda_nombre, self.id_usuario, costo_pts)
            registrar_accion_cliente(self.id_usuario, "CANJE_OFERTA", -costo_pts, f"Canje de '{promo['titulo']}' en {tienda_nombre}")
        except Exception as e:
            print(f"Error registrando logs de canje: {e}")

        messagebox.showinfo("¡Canje Exitoso!", f"Has adquirido '{promo['titulo']}' correctamente.\n\nTus puntos han sido descontados. ¡Preséntate en {tienda_nombre} con tu DNI para reclamarlo!")
        
        # 4. Abrir ventana de calificación con estrellas
        self.dialogo_calificar_tienda(tienda_id, tienda_nombre)
        self.actualizar_todo()

    def dialogo_calificar_tienda(self, tienda_id, tienda_nombre):
        """Muestra una ventana modal para que el vecino califique con estrellas y reseña."""
        win_cal = tk.Toplevel(self.root)
        win_cal.title(f"Calificar a {tienda_nombre}")
        win_cal.geometry("380x360")
        win_cal.resizable(False, False)
        win_cal.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_cal.iconphoto(False, self.root.icon_img)

        tk.Label(win_cal, text=f"⭐ Califica tu experiencia ⭐", font=("Arial", 12, "bold"), fg="#E65100").pack(pady=(15, 5))
        tk.Label(win_cal, text=f"¿Qué tal te pareció la atención en {tienda_nombre}?", font=("Arial", 9), fg="#555").pack(pady=(0, 10))

        tk.Label(win_cal, text="Selecciona Estrellas:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20)
        cb_estrellas = ttk.Combobox(win_cal, values=["⭐⭐⭐⭐⭐ (5/5 - Excelente)", "⭐⭐⭐⭐ (4/5 - Muy Bueno)", "⭐⭐⭐ (3/5 - Bueno)", "⭐⭐ (2/5 - Regular)", "⭐ (1/5 - Malo)"], state="readonly", width=35)
        cb_estrellas.pack(padx=20, pady=5)
        cb_estrellas.current(0)

        tk.Label(win_cal, text="Deja un comentario o reseña:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        txt_comentario = tk.Text(win_cal, width=40, height=4, font=("Arial", 9))
        txt_comentario.pack(padx=20, pady=5)

        def enviar_calificacion():
            comentario = txt_comentario.get("1.0", tk.END).strip()
            estrellas_str = cb_estrellas.get()

            # Guardar la reseña en un log del cliente o enviar mensaje al chat de la tienda
            detalle_resena = f"Calificación: {estrellas_str} | Reseña: {comentario if comentario else 'Sin comentarios'}"
            registrar_accion_cliente(self.id_usuario, "RESEÑA_TIENDA", 0, f"Reseña para {tienda_nombre}: {detalle_resena}")
            
            messagebox.showinfo("Gracias", "¡Tu calificación y reseña han sido enviadas con éxito!")
            win_cal.destroy()

        tk.Button(win_cal, text="Enviar Calificación 📤", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), command=enviar_calificacion, relief="flat", pady=6).pack(pady=15)

    def mostrar_guia_condiciones(self):
        ventana_guia = tk.Toplevel(self.root)
        ventana_guia.title("📋 Condiciones para Entregar tus Materiales - EcoPuntos")
        ventana_guia.geometry("580x520")
        ventana_guia.resizable(False, False)
        ventana_guia.grab_set()

        frame_head = tk.Frame(ventana_guia, bg="#2E7D32", pady=12)
        frame_head.pack(fill="x")
        tk.Label(frame_head, text="🌱 Requisitos para Validar tus Puntos", font=("Arial", 13, "bold"), fg="white", bg="#2E7D32").pack()
        tk.Label(frame_head, text="Asegúrate de cumplir con estos estándares para evitar rechazos en el centro de acopio.", font=("Arial", 9), fg="#E8F5E9", bg="#2E7D32").pack()

        canvas = tk.Canvas(ventana_guia, bg="#F5F5F5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(ventana_guia, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#F5F5F5", padx=15, pady=10)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        materiales_info = [
            {"titulo": "🧴 PLÁSTICO (PET / PEAD - Botellas y Envases)", "color": "#1E88E5", "puntos": ["✔️ Limpios y 100% secos.", "✔️ Aplastados o compactados.", "✔️ Sin tapas ni etiquetas pesadas."]},
            {"titulo": "📦 CARTÓN Y PAPEL", "color": "#F57C00", "puntos": ["✔️ Completamente secos.", "✔️ Desarmados y plegados.", "✔️ Sin cintas ni broches."]},
            {"titulo": "🍾 VIDRIO", "color": "#388E3C", "puntos": ["✔️ Enjuagados y sin tapas.", "✔️ Botellas ENTERAS.", "⚠️ NO vidrios rotos."]},
            {"titulo": "🥫 METAL Y LATAS", "color": "#7B1FA2", "puntos": ["✔️ Sin restos de comida.", "✔️ Latas aplastadas.", "✔️ Libres de tóxicos."]}
        ]

        for mat in materiales_info:
            card = tk.LabelFrame(scroll_frame, text=f" {mat['titulo']} ", font=("Arial", 10, "bold"), fg=mat["color"], bg="white", bd=1, relief="solid", padx=10, pady=8)
            card.pack(fill="x", pady=6)
            for p in mat["puntos"]:
                tk.Label(card, text=p, font=("Arial", 9), bg="white", anchor="w", justify="left").pack(fill="x", anchor="w", pady=2)

        tk.Button(ventana_guia, text="Entendido 👍", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), relief="flat", command=ventana_guia.destroy, cursor="hand2", pady=6).pack(fill="x", padx=15, pady=8)

    def obtener_rango_vecino(self, puntos):
        try:
            pts = float(puntos)
        except (ValueError, TypeError):
            pts = 0.0

        if pts > 300: return "👑 Leyenda Ecológica Suprema"
        elif pts > 150: return "🌳 Guerrero Verde"
        elif pts > 50: return "🌿 Reciclador Activo"
        else: return "🌱 Eco-Novato"

    def verificar_mensajes_nuevos_vecino(self):
        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == self.id_usuario]
        if any(m.get("rol") in ["admin", "desarrollador"] and not m.get("leido", False) for m in msg_cliente):
            messagebox.showinfo("💬 Respuesta de Soporte", "¡Tienes nuevas respuestas de la administración o soporte en tu chat!")

    def mostrar_pantalla_suspendido(self):
        self.root.config(bg="#F8D7DA")
        self.root.title("Cuenta Suspendida - EcoPuntos")
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        frame_aviso = tk.Frame(self.root, bg="#F8D7DA", padx=20, pady=20)
        frame_aviso.pack(fill="both", expand=True)

        tk.Label(frame_aviso, text="⚠️ CUENTA SUSPENDIDA TEMPORALMENTE", font=("Arial", 15, "bold"), fg="#721C24", bg="#F8D7DA").pack(pady=10)
        motivo = self.datos.get("motivo_suspension", "Actividad anómala detectada.")
        tk.Label(frame_aviso, text=f"Motivo del Administrador:\n{motivo}", font=("Arial", 10), fg="#721C24", bg="#F8D7DA", justify="center", wraplength=550).pack(pady=10)

        tk.Label(frame_aviso, text="Redacta una justificación para el administrador:", font=("Arial", 10, "bold"), fg="#333333", bg="#F8D7DA").pack(anchor="w", padx=20, pady=(10, 0))
        txt_justificacion = tk.Text(frame_aviso, width=70, height=6, font=("Arial", 10))
        txt_justificacion.pack(pady=5)
        
        if self.datos.get("justificacion_cliente", ""):
            txt_justificacion.insert("1.0", self.datos.get("justificacion_cliente", ""))

        def enviar_justificacion():
            texto = txt_justificacion.get("1.0", tk.END).strip()
            if not texto:
                messagebox.showwarning("Atención", "Por favor ingresa una justificación.")
                return
            usuarios = cargar_usuarios()
            if self.id_usuario in usuarios:
                usuarios[self.id_usuario]["justificacion_cliente"] = texto
                guardar_usuarios(usuarios)
                messagebox.showinfo("Enviado", "Tu justificación ha sido enviada al administrador.")

        tk.Button(frame_aviso, text="Enviar Justificación al Admin 📤", bg="#28A745", fg="white", font=("Arial", 10, "bold"), relief="flat", command=enviar_justificacion, cursor="hand2").pack(pady=10)
        tk.Button(frame_aviso, text="🚪 Cerrar Sesión", bg="#757575", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.cerrar_sesion_cb, cursor="hand2").pack(pady=5)

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
        self.lbl_rango.config(text=f"Rango: {self.obtener_rango_vecino(puntos_actuales)}")

        self.cargar_catalogo_promociones()

        for item in self.tabla_reciclaje.get_children(): self.tabla_reciclaje.delete(item)
        for item in self.tabla_movimientos.get_children(): self.tabla_movimientos.delete(item)

        for reg in reversed(cargar_log_clientes()):
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
                        material, peso = partes[0], partes[1] if len(partes) > 1 else "-"
                    except Exception:
                        material, peso = detalle, "-"
                    self.tabla_reciclaje.insert("", "end", values=(fecha, material, peso, puntos))

        self.cargar_chat()

    def cargar_catalogo_promociones(self):
        for w in self.frame_promos_scroll.winfo_children():
            w.destroy()

        promos = cargar_promociones()
        if not promos:
            tk.Label(self.frame_promos_scroll, text="🛍️ No hay promociones disponibles en este momento.", font=("Arial", 11, "italic"), bg="white", fg="#757575").pack(pady=40)
            return

        self.referencias_img_vecino = []
        from interfaces.utils import obtener_imagen_miniatura

        for index, p in enumerate(promos):
            card = tk.Frame(self.frame_promos_scroll, bg="#FFF8E1", bd=1, relief="solid", padx=10, pady=10)
            card.pack(fill="x", pady=5, padx=5)

            ruta_foto = p.get("foto", "")
            img_tk = obtener_imagen_miniatura(ruta_foto, ancho=75, alto=75)

            if img_tk:
                self.referencias_img_vecino.append(img_tk)
                tk.Label(card, image=img_tk, bg="#FFF8E1").pack(side="left", padx=(0, 12))
            else:
                tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#FFE0B2", width=10, height=4).pack(side="left", padx=(0, 12))

            frame_info = tk.Frame(card, bg="#FFF8E1")
            frame_info.pack(side="left", fill="both", expand=True)

            stock_text = f" | 📦 Stock: {p.get('stock', 'Ilimitado')}" if 'stock' in p else ""
            tk.Label(frame_info, text=f"🏪 {p.get('tienda_nombre', 'Tienda')}{stock_text}", font=("Arial", 9, "bold"), fg="#E65100", bg="#FFF8E1").pack(anchor="w")
            tk.Label(frame_info, text=f"📌 {p.get('titulo', 'Oferta')}", font=("Arial", 11, "bold"), bg="#FFF8E1").pack(anchor="w", pady=(2, 0))
            tk.Label(frame_info, text=f"📝 {p.get('descripcion', '')}", font=("Arial", 9), fg="#424242", bg="#FFF8E1").pack(anchor="w")
            
            tk.Label(frame_info, text=f"Precio: S/ {p.get('precio_soles', 0):.2f}  ➔  Costo: {p.get('puntos', 0)} PTS", font=("Arial", 10, "bold"), fg="#2E7D32", bg="#FFF8E1").pack(anchor="w", pady=(4, 0))

            # Botón de Canje para el Vecino
            tk.Button(
                card, 
                text="🎟️ Canjear Oferta", 
                bg="#2E7D32", 
                fg="white", 
                font=("Arial", 9, "bold"), 
                relief="flat", 
                command=lambda idx=index: self.canjear_oferta(idx),
                cursor="hand2",
                padx=10,
                pady=5
            ).pack(side="right", padx=10)

    def cargar_chat(self):
        marcar_chat_como_leido(self.id_usuario, "vecino")
        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == self.id_usuario]

        if not msg_cliente:
            self.txt_chat.insert(tk.END, "💬 Inicia una conversación con el equipo de soporte o administración.\n\n")
        else:
            for m in msg_cliente:
                autor, rol, texto, fecha, leido = m.get("autor", "Usuario"), m.get("rol", "").upper(), m.get("mensaje", ""), m.get("fecha", ""), m.get("leido", True)
                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"
                self.txt_chat.insert(tk.END, f"[{fecha}] {autor} ({rol}){check_leido}:\n{texto}\n\n")

        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def enviar_mensaje(self):
        texto = self.ent_msg.get().strip()
        if not texto: return
        guardar_mensaje_chat(dni_cliente=self.id_usuario, autor_nombre=self.datos.get("nombre", "Vecino"), rol_autor="vecino", mensaje=texto)
        self.ent_msg.delete(0, tk.END)
        self.cargar_chat()