import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, 
    guardar_usuarios, 
    registrar_accion_tienda, 
    registrar_accion_cliente,
    cargar_promociones, 
    guardar_promociones,
    eliminar_promocion,
    cargar_log_tiendas,
    cargar_log_clientes
)

COLOR_FONDO_TIENDA = "#FFF3E0"

class VentanaNegocio:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        try:
            self.root.config(bg=COLOR_FONDO_TIENDA)
            self.root.title("EcoPuntos - Terminal de Cobro Negocios")
            self.root.geometry("980x740")
            self.root.resizable(False, False)

            self.aplicar_icono()

            # Fondo Opcional
            ruta_fondo = os.path.join("img", "fondo_negocio.png")
            if os.path.exists(ruta_fondo):
                try:
                    self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                    lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                    lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
                except Exception as e:
                    print(f"Aviso imagen de fondo: {e}")

            usuarios = cargar_usuarios()
            self.nombre_negocio = usuarios.get(id_usuario, {}).get("nombre", "Comercio")

            # Header
            frame_top = tk.Frame(self.root, bg="#E65100")
            frame_top.pack(fill="x")
            
            tk.Label(
                frame_top, 
                text=f"🏪 Terminal de Bodega: {self.nombre_negocio}", 
                font=("Arial", 14, "bold"), 
                fg="white", 
                bg="#E65100", 
                pady=12
            ).pack(side="left", padx=20)

            # Botón de Términos y Condiciones de la Bodega
            tk.Button(
                frame_top,
                text="📄! Términos de Bodega",
                bg="#BF360C",
                fg="white",
                font=("Arial", 9, "bold"),
                relief="flat",
                command=self.mostrar_terminos_negocio,
                cursor="hand2",
                padx=10,
                pady=5
            ).pack(side="right", padx=20)

            # BOTÓN DE CERRAR SESIÓN FIJO ABAJO
            tk.Button(
                self.root, 
                text="🚪 Cerrar Sesión", 
                bg="#757575", 
                fg="white", 
                activeforeground="white",
                font=("Arial", 10, "bold"),
                relief="flat", 
                command=self.cerrar_sesion_cb,
                pady=4,
                padx=15,
                cursor="hand2"
            ).pack(side="bottom", pady=10)

            # NOTEBOOK DE PESTAÑAS PRINCIPALES
            notebook_negocio = ttk.Notebook(self.root)
            notebook_negocio.pack(fill="both", expand=True, padx=15, pady=10)

            tab_terminal = ttk.Frame(notebook_negocio)
            tab_historial = ttk.Frame(notebook_negocio)
            tab_resenas = ttk.Frame(notebook_negocio)

            notebook_negocio.add(tab_terminal, text="💳 Terminal y Publicación")
            notebook_negocio.add(tab_historial, text="📜 Historial y Gestión de Ofertas")
            notebook_negocio.add(tab_resenas, text="⭐ Mis Reseñas y Calificación")

            # ==========================================
            # PESTAÑA 1: TERMINAL Y PUBLICACIÓN
            # ==========================================
            frame_central = tk.Frame(tab_terminal, bg="white", bd=1, relief="solid", padx=25, pady=20)
            frame_central.pack(fill="both", expand=True, padx=15, pady=15)

            # 1. Buscador de Vecino
            frame_busca = tk.LabelFrame(
                frame_central, 
                text=" 1. Consultar Cuenta del Vecino (Presencial) ", 
                font=("Arial", 11, "bold"), 
                padx=15, 
                pady=10, 
                bg="white",
                fg="#E65100"
            )
            frame_busca.pack(fill="x", pady=(0, 15))

            tk.Label(frame_busca, text="Ingrese DNI del Vecino:", font=("Arial", 11), bg="white").pack(side="left", padx=10)
            self.ent_dni = tk.Entry(frame_busca, font=("Arial", 12), width=18, bg="#F5F5F5", relief="flat", highlightthickness=1)
            self.ent_dni.pack(side="left", padx=10, ipady=3)
            self.ent_dni.bind("<Return>", lambda event: self.consultar_vecino())

            tk.Button(
                frame_busca, 
                text="🔍 Buscar Cuenta", 
                bg="#1976D2", 
                fg="white", 
                activeforeground="white",
                font=("Arial", 10, "bold"),
                relief="flat", 
                command=self.consultar_vecino,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side="left", padx=10)

            # 2. Estado de Cuenta
            self.frame_info = tk.LabelFrame(
                frame_central, 
                text=" 2. Estado de Cuenta del Vecino (Máx. 2000 PTS) ", 
                font=("Arial", 11, "bold"), 
                padx=15, 
                pady=10, 
                bg="white",
                fg="#2E7D32"
            )
            self.frame_info.pack(fill="both", expand=True, pady=(0, 15))

            self.lbl_nombre = tk.Label(
                self.frame_info, 
                text="Vecino: Ninguno seleccionado", 
                font=("Arial", 11, "bold"), 
                fg="#37474F",
                bg="white"
            )
            self.lbl_nombre.pack(anchor="w", pady=(2, 5))

            self.lbl_saldo = tk.Label(
                self.frame_info, 
                text="Saldo Disponible: 0 PTS", 
                font=("Arial", 18, "bold"), 
                fg="#2E7D32", 
                bg="white"
            )
            self.lbl_saldo.pack(anchor="w", pady=5)

            # Botón único de Cobro / Canje Presencial (Texto limpio sin la palabra múltiple)
            self.btn_canjear = tk.Button(
                frame_central, 
                text="💳 Canje de Ofertas en Caja", 
                bg="#E65100", 
                fg="white", 
                activeforeground="white",
                disabledforeground="#E0E0E0",
                font=("Arial", 11, "bold"), 
                state="disabled", 
                relief="flat", 
                command=self.abrir_cuadro_canje,
                pady=10,
                cursor="hand2"
            )
            self.btn_canjear.pack(fill="x", pady=(0, 10))

            # Botón Publicar Promoción
            tk.Button(
                frame_central, 
                text="📢 Publicar Nueva Oferta / Promoción", 
                bg="#1976D2", 
                fg="white", 
                activeforeground="white",
                font=("Arial", 11, "bold"), 
                relief="flat", 
                command=self.dialogo_publicar_promocion,
                pady=8,
                cursor="hand2"
            ).pack(fill="x")

            # ==========================================
            # PESTAÑA 2: HISTORIAL Y GESTIÓN DE OFERTAS
            # ==========================================
            frame_hist_box = tk.Frame(tab_historial, bg="white", padx=15, pady=15)
            frame_hist_box.pack(fill="both", expand=True, padx=15, pady=15)

            tk.Button(
                frame_hist_box, 
                text="📋 Ver, Gestionar y Eliminar Mis Ofertas Publicadas", 
                bg="#00897B", 
                fg="white", 
                activeforeground="white",
                font=("Arial", 10, "bold"), 
                relief="flat", 
                command=self.dialogo_mis_promociones,
                padx=15,
                pady=8,
                cursor="hand2"
            ).pack(anchor="w", pady=(0, 15))

            tk.Label(
                frame_hist_box, 
                text="📜 Historial de Canjes y Entregas Presenciales Realizadas:", 
                font=("Arial", 11, "bold"), 
                bg="white",
                fg="#333333"
            ).pack(anchor="w", pady=(0, 5))

            cols_log = ("fecha", "dni_cliente", "puntos")
            config_log = [
                ("fecha", "Fecha / Hora", 200),
                ("dni_cliente", "DNI del Cliente", 180),
                ("puntos", "Puntos / Operación", 160)
            ]

            frame_tabla = ttk.Frame(frame_hist_box)
            frame_tabla.pack(fill="both", expand=True, pady=5)

            sy = ttk.Scrollbar(frame_tabla, orient="vertical")
            sx = ttk.Scrollbar(frame_tabla, orient="horizontal")

            self.tabla_historial_tienda = ttk.Treeview(
                frame_tabla, 
                columns=cols_log, 
                show="headings", 
                yscrollcommand=sy.set, 
                xscrollcommand=sx.set
            )
            sy.config(command=self.tabla_historial_tienda.yview)
            sx.config(command=self.tabla_historial_tienda.xview)

            sy.pack(side="right", fill="y")
            sx.pack(side="bottom", fill="x")
            self.tabla_historial_tienda.pack(side="left", fill="both", expand=True)

            for col, txt, w in config_log:
                self.tabla_historial_tienda.heading(col, text=txt)
                self.tabla_historial_tienda.column(col, width=w, minwidth=80, stretch=True)

            # ==========================================
            # PESTAÑA 3: RESEÑAS Y CALIFICACIONES DEL NEGOCIO
            # ==========================================
            frame_res_box = tk.Frame(tab_resenas, bg="white", padx=15, pady=15)
            frame_res_box.pack(fill="both", expand=True, padx=15, pady=15)

            # Tarjeta de Estadísticas (Promedio de Estrellas)
            frame_stats = tk.Frame(frame_res_box, bg="#FFF8E1", bd=1, relief="solid", padx=15, pady=12)
            frame_stats.pack(fill="x", pady=(0, 15))

            self.lbl_promedio_estrellas = tk.Label(
                frame_stats, 
                text="⭐ Calificación Promedio: Calculando...", 
                font=("Arial", 13, "bold"), 
                fg="#E65100", 
                bg="#FFF8E1"
            )
            self.lbl_promedio_estrellas.pack(anchor="w")

            self.lbl_total_resenas = tk.Label(
                frame_stats, 
                text="📊 Total de Opiniones Recibidas: 0", 
                font=("Arial", 10), 
                fg="#37474F", 
                bg="#FFF8E1"
            )
            self.lbl_total_resenas.pack(anchor="w", pady=(3, 0))

            tk.Label(
                frame_res_box, 
                text="💬 Opiniones y Reseñas de los Vecinos:", 
                font=("Arial", 11, "bold"), 
                bg="white",
                fg="#333333"
            ).pack(anchor="w", pady=(0, 5))

            cols_res = ("fecha", "dni", "estrellas", "comentario")
            config_res = [
                ("fecha", "Fecha / Hora", 180),
                ("dni", "DNI Vecino", 130),
                ("estrellas", "⭐ Calificación", 180),
                ("comentario", "💬 Reseña / Comentario", 430)
            ]

            frame_tabla_res = ttk.Frame(frame_res_box)
            frame_tabla_res.pack(fill="both", expand=True, pady=5)

            sy_res = ttk.Scrollbar(frame_tabla_res, orient="vertical")
            sx_res = ttk.Scrollbar(frame_tabla_res, orient="horizontal")

            self.tabla_resenas_negocio = ttk.Treeview(
                frame_tabla_res, 
                columns=cols_res, 
                show="headings", 
                yscrollcommand=sy_res.set, 
                xscrollcommand=sx_res.set
            )
            sy_res.config(command=self.tabla_resenas_negocio.yview)
            sx_res.config(command=self.tabla_resenas_negocio.xview)

            sy_res.pack(side="right", fill="y")
            sx_res.pack(side="bottom", fill="x")
            self.tabla_resenas_negocio.pack(side="left", fill="both", expand=True)

            for col, txt, w in config_res:
                self.tabla_resenas_negocio.heading(col, text=txt)
                anchor_val = "center" if col == "estrellas" else "w"
                self.tabla_resenas_negocio.column(col, width=w, minwidth=80, stretch=True, anchor=anchor_val)

            self.vecino_actual = None
            self.actualizar_historial_tienda()
            self.actualizar_resenas_negocio()

        except Exception as e:
            messagebox.showerror("Error de Interfaz", f"Detalle al cargar Tienda: {str(e)}")

    def mostrar_terminos_negocio(self):
        """Muestra los Términos y Condiciones específicos para la Bodega / Negocio."""
        win_tyc = tk.Toplevel(self.root)
        win_tyc.title("📜 Términos y Condiciones — Bodegas EcoPuntos")
        win_tyc.geometry("520x460")
        win_tyc.resizable(False, False)
        win_tyc.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_tyc.iconphoto(False, self.root.icon_img)

        tk.Label(win_tyc, text="📜 Términos y Condiciones (Negocios / Bodegas)", font=("Arial", 12, "bold"), fg="#E65100").pack(pady=(15, 10))

        frame_txt = tk.Frame(win_tyc, padx=15, pady=5)
        frame_txt.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_txt)
        scrollbar.pack(side="right", fill="y")

        txt_box = tk.Text(
            frame_txt, 
            wrap="word", 
            yscrollcommand=scrollbar.set, 
            font=("Arial", 10), 
            bg="#FFFFFF", 
            fg="#222222", 
            padx=10, 
            pady=10
        )
        txt_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt_box.yview)

        contenido = (
            "REGLAS DE OPERACIÓN PARA BODEGAS Y COMERCIOS — ECOPUNTOS\n\n"
            "1. GESTIÓN DE CANJES Y VENTAS PRESENCIALES\n"
            "• Toda transacción de puntos, entrega de productos ofertados o descuentos en caja debe realizarse de forma estrictamente presencial mediante la validación del DNI del vecino en esta terminal.\n\n"
            "2. LÍMITE DE PUNTOS POR CLIENTE\n"
            "• Ningún vecino podrá acumular más de 2,000 puntos (S/ 200.00) en su saldo activo. Si un cliente alcanza el tope, se le exhortará a realizar canjes antes de recibir nuevos abonos por reciclaje.\n\n"
            "3. CONTROL DE INVENTARIO Y STOCK\n"
            "• El comercio es responsable de mantener actualizado el stock y los precios de sus ofertas publicadas. Cada entrega validada descuenta la unidad correspondiente del sistema.\n\n"
            "Al operar como comercio afiliado, usted acepta cumplir estas normativas."
        )

        txt_box.insert("1.0", contenido)
        txt_box.config(state="disabled")

        tk.Button(win_tyc, text="Entendido 👍", bg="#E65100", fg="white", font=("Arial", 10, "bold"), command=win_tyc.destroy, padx=20, pady=8, cursor="hand2").pack(pady=12)

    def actualizar_historial_tienda(self):
        for item in self.tabla_historial_tienda.get_children():
            self.tabla_historial_tienda.delete(item)

        logs = cargar_log_tiendas()
        for log in reversed(logs):
            if log.get("tienda_id") == self.id_usuario:
                puntos_int = int(float(log.get('puntos_descontados', 0)))
                puntos_txt = f"{puntos_int} PTS" if puntos_int == 0 else f"-{puntos_int} PTS"
                self.tabla_historial_tienda.insert(
                    "", 
                    "end", 
                    values=(
                        log.get("fecha", "-"), 
                        log.get("dni_cliente", "-"), 
                        puntos_txt
                    )
                )

    def actualizar_resenas_negocio(self):
        for item in self.tabla_resenas_negocio.get_children():
            self.tabla_resenas_negocio.delete(item)

        logs = cargar_log_clientes()
        
        mis_resenas = []
        suma_calificaciones = 0

        for log in reversed(logs):
            if log.get("tipo") == "RESEÑA_TIENDA":
                detalle = log.get("detalle", "")
                if self.nombre_negocio.lower() in detalle.lower():
                    fecha = log.get("fecha", "-")
                    dni = log.get("dni_cliente", "-")
                    
                    estrellas_str = "⭐ (Sin calificación)"
                    comentario_str = detalle
                    valor_numerico = 0

                    if "Calificación:" in detalle:
                        partes = detalle.split("Calificación:")
                        if len(partes) > 1:
                            subpartes = partes[1].split("|")
                            estrellas_str = subpartes[0].strip()
                            if len(subpartes) > 1:
                                comentario_str = subpartes[1].replace("Reseña:", "").strip()

                            try:
                                valor_numerico = int(estrellas_str.split("/")[0].replace("(", "").strip())
                            except Exception:
                                valor_numerico = 5

                    suma_calificaciones += valor_numerico
                    mis_resenas.append((fecha, dni, estrellas_str, comentario_str))
                    self.tabla_resenas_negocio.insert("", "end", values=(fecha, dni, estrellas_str, comentario_str))

        total = len(mis_resenas)
        if total > 0:
            promedio = round(suma_calificaciones / total, 1)
            self.lbl_promedio_estrellas.config(text=f"⭐ Calificación Promedio: {promedio} / 5.0")
            self.lbl_total_resenas.config(text=f"📊 Total de Opiniones Recibidas: {total} reseñas")
        else:
            self.lbl_promedio_estrellas.config(text="⭐ Calificación Promedio: Sin calificaciones aún")
            self.lbl_total_resenas.config(text="📊 Total de Opiniones Recibidas: 0 reseñas")

    def dialogo_mis_promociones(self):
        win_list = tk.Toplevel(self.root)
        win_list.title("Mis Ofertas Publicadas - Gestión")
        win_list.geometry("640x480")
        win_list.resizable(False, False)
        win_list.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_list.iconphoto(False, self.root.icon_img)

        frame_container = tk.Frame(win_list, bg="white", padx=10, pady=10)
        frame_container.pack(fill="both", expand=True)

        win_list.referencias_img = []

        def refrescar():
            for w in frame_container.winfo_children(): w.destroy()
            win_list.referencias_img.clear()
            promos = cargar_promociones()
            mis_promos = [(i, p) for i, p in enumerate(promos) if p.get("tienda_id") == self.id_usuario]

            if not mis_promos:
                tk.Label(frame_container, text="No tienes ofertas publicadas actualmente.", font=("Arial", 11, "italic"), bg="white", fg="#757575").pack(pady=50)
                return

            tk.Label(frame_container, text=f"Total de ofertas publicadas: {len(mis_promos)}", font=("Arial", 10, "bold"), bg="white", fg="#E65100").pack(anchor="w", pady=(0, 10))

            for idx, p in mis_promos:
                card = tk.Frame(frame_container, bg="#FFF8E1", bd=1, relief="solid", padx=10, pady=8)
                card.pack(fill="x", pady=4)

                ruta_foto = p.get("foto", "")
                if ruta_foto and os.path.exists(ruta_foto):
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(ruta_foto).resize((60, 60), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        win_list.referencias_img.append(img_tk)
                        tk.Label(card, image=img_tk, bg="#FFF8E1").pack(side="left", padx=(0, 10))
                    except Exception:
                        tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#FFE0B2", width=8, height=3).pack(side="left", padx=(0, 10))
                else:
                    tk.Label(card, text="📷\nSin Foto", font=("Arial", 8), bg="#FFE0B2", width=8, height=3).pack(side="left", padx=(0, 10))

                stock_disp = p.get("stock", "Ilimitado")
                puntos_int = int(float(p['puntos']))
                txt_info = f"📌 {p['titulo']} (Costo: {puntos_int} PTS / S/ {p['precio_soles']:.2f})\n📦 Stock Disponible: {stock_disp}\n📝 {p['descripcion']}"
                tk.Label(card, text=txt_info, font=("Arial", 9), bg="#FFF8E1", justify="left").pack(side="left", anchor="w", expand=True)

                def borrar(i=idx):
                    if messagebox.askyesno("Eliminar Promoción", "¿Deseas eliminar permanentemente esta oferta del sistema?"):
                        if eliminar_promocion(i, self.id_usuario, self.nombre_negocio):
                            messagebox.showinfo("Éxito", "La oferta ha sido eliminada correctamente.")
                            refrescar()

                tk.Button(card, text="🗑️ Eliminar", bg="#C62828", fg="white", activeforeground="white", font=("Arial", 9, "bold"), relief="flat", command=borrar, cursor="hand2", padx=8, pady=4).pack(side="right", padx=5)

        refrescar()

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception:
            pass

    def consultar_vecino(self):
        dni = self.ent_dni.get().strip()
        usuarios = cargar_usuarios()

        if dni in usuarios and usuarios[dni].get("rol") == "vecino":
            self.vecino_actual = dni
            puntos_enteros = int(float(usuarios[dni].get('puntos', 0)))
            self.lbl_nombre.config(text=f"Vecino: {usuarios[dni].get('nombre', 'Sin nombre')} (DNI: {dni})")
            self.lbl_saldo.config(text=f"Saldo Disponible: {puntos_enteros} PTS")
            self.btn_canjear.config(state="normal")
        else:
            self.vecino_actual = None
            self.lbl_nombre.config(text="Vecino no encontrado")
            self.lbl_saldo.config(text="Saldo Disponible: 0 PTS")
            self.btn_canjear.config(state="disabled")
            messagebox.showwarning("No Encontrado", "El DNI ingresado no pertenece a un vecino registrado.")

    def abrir_cuadro_canje(self):
        if not self.vecino_actual: return
        
        usuarios = cargar_usuarios()
        saldo_actual = int(float(usuarios[self.vecino_actual].get("puntos", 0)))

        if saldo_actual <= 0:
            messagebox.showerror("Saldo Insuficiente", "El vecino no cuenta con puntos para canjear.")
            return

        # Cargar promociones activas de ESTE negocio
        promos = cargar_promociones()
        mis_promos = [(idx, p) for idx, p in enumerate(promos) if p.get("tienda_id") == self.id_usuario]

        if not mis_promos:
            messagebox.showwarning("Sin Ofertas", "Este comercio no tiene ofertas o promociones publicadas actualmente.")
            return

        # Ventana personalizada con título limpio (sin mención múltiple)
        win_cobro = tk.Toplevel(self.root)
        win_cobro.title("Canje de Ofertas en Caja")
        win_cobro.geometry("480x450")
        win_cobro.resizable(False, False)
        win_cobro.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_cobro.iconphoto(False, self.root.icon_img)

        tk.Label(
            win_cobro, 
            text=f"Vecino: {usuarios[self.vecino_actual].get('nombre', 'Cliente')} | Saldo: {saldo_actual} PTS", 
            font=("Arial", 11, "bold"), 
            fg="#E65100"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Label(win_cobro, text="Seleccione una o varias ofertas a canjear:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(5, 5))

        # Contenedor con scroll para las casillas de verificación
        frame_scroll_container = tk.Frame(win_cobro, bg="white", bd=1, relief="solid")
        frame_scroll_container.pack(fill="both", expand=True, padx=20, pady=5)

        canvas = tk.Canvas(frame_scroll_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_scroll_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white", padx=10, pady=5)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Diccionario para almacenar las variables de los Checkbuttons
        vars_promos = {}

        for orig_idx, p in mis_promos:
            titulo = p.get('titulo', 'Oferta')
            costo_pts = int(float(p.get('puntos', 0)))
            stock_disp = p.get('stock', 10)
            
            var = tk.IntVar()
            vars_promos[orig_idx] = (var, p)
            
            texto_chk = f"{titulo} — Costo: {costo_pts} PTS (Stock: {stock_disp})"
            chk = tk.Checkbutton(scroll_frame, text=texto_chk, variable=var, font=("Arial", 9), bg="white", anchor="w")
            chk.pack(anchor="w", fill="x", pady=3)

        def procesar_canjes_multiples():
            seleccionadas = []
            total_puntos_requeridos = 0

            for orig_idx, (var, promo) in vars_promos.items():
                if var.get() == 1:
                    costo = int(float(promo.get('puntos', 0)))
                    stock = promo.get('stock', 10)
                    
                    if isinstance(stock, int) and stock <= 0:
                        messagebox.showwarning("Agotado", f"La oferta '{promo['titulo']}' ya no tiene stock disponible.", parent=win_cobro)
                        return
                    
                    seleccionadas.append((orig_idx, promo, costo))
                    total_puntos_requeridos += costo

            if not seleccionadas:
                messagebox.showwarning("Atención", "Debe seleccionar al menos una promoción para canjear.", parent=win_cobro)
                return

            # Validación estricta de puntos insuficientes
            if total_puntos_requeridos > saldo_actual:
                messagebox.showerror(
                    "Puntos Insuficientes", 
                    f"El vecino no cuenta con suficientes puntos.\n\nTotal requerido: {total_puntos_requeridos} PTS\nSaldo disponible: {saldo_actual} PTS", 
                    parent=win_cobro
                )
                return

            # Mensaje de confirmación
            nombres_ofertas = ", ".join([f"'{p['titulo']}'" for _, p, _ in seleccionadas])
            if not messagebox.askyesno("Confirmación", f"¿Confirmas promoción {nombres_ofertas} por {total_puntos_requeridos} PTS?", parent=win_cobro):
                return

            # Descontar puntos al vecino (enteros puros)
            usuarios[self.vecino_actual]["puntos"] = int(saldo_actual - total_puntos_requeridos)
            guardar_usuarios(usuarios)

            # Actualizar stocks y registrar logs por cada oferta seleccionada
            promos_actualizadas = cargar_promociones()
            for orig_idx, promo, costo in seleccionadas:
                for g_idx, gp in enumerate(promos_actualizadas):
                    if gp.get("tienda_id") == self.id_usuario and gp.get("titulo") == promo.get("titulo") and gp.get("puntos") == promo.get("puntos"):
                        stk = gp.get("stock", 10)
                        if isinstance(stk, int):
                            gp["stock"] = stk - 1
                            if gp["stock"] <= 0:
                                promos_actualizadas.pop(g_idx)
                        break
                
                try:
                    registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, costo)
                    registrar_accion_cliente(self.vecino_actual, "ENTREGA_OFERTA", -costo, f"Canje presencial de '{promo['titulo']}' en {self.nombre_negocio}")
                except Exception as e:
                    print(f"Aviso log multiple: {e}")

            guardar_promociones(promos_actualizadas)

            messagebox.showinfo("Éxito", f"¡Canje completado! Se han descontado {total_puntos_requeridos} PTS en total.", parent=win_cobro)
            win_cobro.destroy()
            self.consultar_vecino()
            self.actualizar_historial_tienda()

        # Botones de acción
        frame_btns = tk.Frame(win_cobro)
        frame_btns.pack(pady=15)

        tk.Button(frame_btns, text="Aceptar / Canjear Seleccionadas", bg="#E65100", fg="white", font=("Arial", 10, "bold"), width=25, command=procesar_canjes_multiples, relief="flat", cursor="hand2").pack(side="left", padx=5)
        tk.Button(frame_btns, text="Cancelar", bg="#757575", fg="white", font=("Arial", 10, "bold"), width=12, command=win_cobro.destroy, relief="flat", cursor="hand2").pack(side="right", padx=5)

def dialogo_publicar_promocion(self):
        win_promo = tk.Toplevel(self.root)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("380x380")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        # 1. Título (Máx 25 caracteres)
        tk.Label(win_promo, text="Título de Promoción (Máx 25 caract.):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10))
        ent_titulo.pack(fill="x", padx=20)

        # 2. Precio en Soles y cálculo de puntos
        tk.Label(win_promo, text="Precio Normal en Soles (S/):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_precio = tk.Entry(win_promo, font=("Arial", 10))
        ent_precio.pack(fill="x", padx=20)

        lbl_pts_equiv = tk.Label(win_promo, text="Equivalente: 0.0 PTS", font=("Arial", 10, "bold"), fg="#2E7D32")
        lbl_pts_equiv.pack(anchor="w", padx=20, pady=4)

        def calcular_pts_event(event=None):
            try:
                monto_soles = float(ent_precio.get().strip())
                pts = round(monto_soles / 0.10, 1)  # 1 PTS = S/ 0.10
                lbl_pts_equiv.config(text=f"Equivalente: {pts} PTS")
            except ValueError:
                lbl_pts_equiv.config(text="Equivalente: 0.0 PTS")

        ent_precio.bind("<KeyRelease>", calcular_pts_event)

        # 3. Descripción (Máx 25 caracteres)
        tk.Label(win_promo, text="Descripción Corta (Máx 25 caract.):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_desc = tk.Entry(win_promo, font=("Arial", 10))
        ent_desc.pack(fill="x", padx=20)

        # Guardar en promociones.json
        def guardar_promo():
            titulo = ent_titulo.get().strip()
            desc = ent_desc.get().strip()
            precio_str = ent_precio.get().strip()

            if len(titulo) == 0 or len(titulo) > 25:
                messagebox.showerror("Error", "El título es obligatorio y debe tener como máximo 25 caracteres.")
                return

            if len(desc) == 0 or len(desc) > 25:
                messagebox.showerror("Error", "La descripción es obligatoria y debe tener como máximo 25 caracteres.")
                return

            try:
                precio_soles = float(precio_str)
                pts_requeridos = round(precio_soles / 0.10, 1)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un precio válido en soles.")
                return

            promos = cargar_promociones()
            promos.append({
                "tienda_id": self.id_usuario,
                "tienda_nombre": self.nombre_negocio,
                "titulo": titulo,
                "descripcion": desc,
                "precio_soles": precio_soles,
                "puntos": pts_requeridos,
                "foto": ""  # Se guarda vacío sin opción a subir foto
            })
            guardar_promociones(promos)

            messagebox.showinfo("Éxito", "¡Promoción publicada correctamente!")
            win_promo.destroy()

        tk.Button(win_promo, text="💾 Publicar Oferta", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), command=guardar_promo, relief="flat", pady=6).pack(pady=20)