import tkinter as tk
from tkinter import ttk, messagebox
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

# ==========================================
# PALETA DE COLORES "ECO-GESTIÓN" (SIN NEGRO)
# ==========================================
COLOR_FONDO_APP      = "#F4F9F4"  # Blanco Menta Suave
COLOR_TEXTO_MAIN     = "#1B4332"  # Verde Bosque Profundo
COLOR_PRIMARIO       = "#40916C"  # Verde Hoja
COLOR_SECUNDARIO     = "#52B788"  # Verde Claro Fresco
COLOR_ACENTO_CANJE   = "#E76F51"  # Terracota Suave
COLOR_BLANCO         = "#FFFFFF"  # Blanco puro
COLOR_ROJO_ELIMINAR  = "#C62828"  # Rojo para eliminar

# Categorías específicas e independientes para Bodega
CATEGORIAS_BODEGA = [
    "Abarrotes y Despensa",
    "Bebidas y Gaseosas",
    "Licores y Cervezas",
    "Dulces, Biscochos y Snacks",
    "Limpieza del Hogar",
    "Cuidado Personal y Aseo",
    "Utensilios de Cocina / Hogar"
]

class VentanaNegocio:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        self.vecino_actual = None
        
        try:
            self.root.config(bg=COLOR_FONDO_APP)
            self.root.title("EcoPuntos - Terminal de Cobro Negocios")
            self.root.geometry("980x740")
            self.root.resizable(False, False)

            self.aplicar_icono()

            # Imagen de Fondo (980x740 px)
            ruta_fondo = os.path.join("img", "fondo_negocio.png")
            if os.path.exists(ruta_fondo):
                try:
                    self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                    lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                    lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
                except Exception as e:
                    print(f"Aviso imagen de fondo: {e}")

            self.aplicar_estilos_ttk()

            usuarios = cargar_usuarios()
            self.nombre_negocio = usuarios.get(id_usuario, {}).get("nombre", "Comercio")

            # Header Principal
            frame_top = tk.Frame(self.root, bg=COLOR_PRIMARIO)
            frame_top.pack(fill="x")
            
            tk.Label(
                frame_top, 
                text=f"🏪 Terminal de Bodega: {self.nombre_negocio}", 
                font=("Arial", 14, "bold"), 
                fg=COLOR_BLANCO, 
                bg=COLOR_PRIMARIO, 
                pady=12
            ).pack(side="left", padx=20)

            # Botón de Términos y Condiciones
            tk.Button(
                frame_top,
                text="📄! Términos de Bodega",
                bg=COLOR_SECUNDARIO,
                fg=COLOR_BLANCO,
                font=("Arial", 9, "bold"),
                relief="flat",
                command=self.mostrar_terminos_negocio,
                cursor="hand2",
                padx=10,
                pady=5
            ).pack(side="right", padx=20)

            # BOTÓN CERRAR SESIÓN (Fijo Abajo)
            tk.Button(
                self.root, 
                text="🚪 Cerrar Sesión", 
                bg="#757575", 
                fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO,
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
            frame_central = tk.Frame(tab_terminal, bg=COLOR_BLANCO, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO, padx=25, pady=20)
            frame_central.pack(fill="both", expand=True, padx=15, pady=15)

            # 1. Buscador de Vecino
            frame_busca = tk.LabelFrame(
                frame_central, 
                text=" 1. Consultar Cuenta del Vecino (Presencial) ", 
                font=("Arial", 11, "bold"), 
                padx=15, 
                pady=10, 
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO_MAIN
            )
            frame_busca.pack(fill="x", pady=(0, 15))

            tk.Label(frame_busca, text="Ingrese DNI del Vecino:", font=("Arial", 11), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(side="left", padx=10)
            self.ent_dni = tk.Entry(frame_busca, font=("Arial", 12), width=18, bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
            self.ent_dni.pack(side="left", padx=10, ipady=3)
            self.ent_dni.bind("<Return>", lambda event: self.consultar_vecino())

            tk.Button(
                frame_busca, 
                text="🔍 Buscar Cuenta", 
                bg=COLOR_PRIMARIO, 
                fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO,
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
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO_MAIN
            )
            self.frame_info.pack(fill="both", expand=True, pady=(0, 15))

            self.lbl_nombre = tk.Label(
                self.frame_info, 
                text="Vecino: Ninguno seleccionado", 
                font=("Arial", 11, "bold"), 
                fg=COLOR_TEXTO_MAIN,
                bg=COLOR_BLANCO
            )
            self.lbl_nombre.pack(anchor="w", pady=(2, 5))

            self.lbl_saldo = tk.Label(
                self.frame_info, 
                text="Saldo Disponible: 0 PTS", 
                font=("Arial", 18, "bold"), 
                fg=COLOR_ACENTO_CANJE, 
                bg=COLOR_BLANCO
            )
            self.lbl_saldo.pack(anchor="w", pady=5)

            # Botón único de Canje Presencial
            self.btn_canjear = tk.Button(
                frame_central, 
                text="💳 Canje de Ofertas en Caja", 
                bg=COLOR_ACENTO_CANJE, 
                fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO,
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
                bg=COLOR_PRIMARIO, 
                fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO,
                font=("Arial", 11, "bold"), 
                relief="flat", 
                command=self.dialogo_publicar_promocion,
                pady=8,
                cursor="hand2"
            ).pack(fill="x")

            # ==========================================
            # PESTAÑA 2: HISTORIAL Y GESTIÓN DE OFERTAS
            # ==========================================
            frame_hist_box = tk.Frame(tab_historial, bg=COLOR_BLANCO, padx=15, pady=15)
            frame_hist_box.pack(fill="both", expand=True, padx=15, pady=15)

            tk.Button(
                frame_hist_box, 
                text="📋 Ver, Gestionar y Eliminar Mis Ofertas Publicadas", 
                bg=COLOR_PRIMARIO, 
                fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO,
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
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO_MAIN
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
            frame_res_box = tk.Frame(tab_resenas, bg=COLOR_BLANCO, padx=15, pady=15)
            frame_res_box.pack(fill="both", expand=True, padx=15, pady=15)

            frame_stats = tk.Frame(frame_res_box, bg=COLOR_FONDO_APP, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO, padx=15, pady=12)
            frame_stats.pack(fill="x", pady=(0, 15))

            self.lbl_promedio_estrellas = tk.Label(
                frame_stats, 
                text="⭐ Calificación Promedio: Calculando...", 
                font=("Arial", 13, "bold"), 
                fg=COLOR_TEXTO_MAIN, 
                bg=COLOR_FONDO_APP
            )
            self.lbl_promedio_estrellas.pack(anchor="w")

            self.lbl_total_resenas = tk.Label(
                frame_stats, 
                text="📊 Total de Opiniones Recibidas: 0", 
                font=("Arial", 10), 
                fg=COLOR_TEXTO_MAIN, 
                bg=COLOR_FONDO_APP
            )
            self.lbl_total_resenas.pack(anchor="w", pady=(3, 0))

            tk.Label(
                frame_res_box, 
                text="💬 Opiniones y Reseñas de los Vecinos:", 
                font=("Arial", 11, "bold"), 
                bg=COLOR_BLANCO,
                fg=COLOR_TEXTO_MAIN
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

            self.actualizar_historial_tienda()
            self.actualizar_resenas_negocio()

        except Exception as e:
            messagebox.showerror("Error de Interfaz", f"Detalle al cargar Tienda: {str(e)}")

    def aplicar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_FONDO_APP, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 10, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_BLANCO)], foreground=[("selected", COLOR_PRIMARIO)])
        
        style.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_TEXTO_MAIN, fieldbackground=COLOR_BLANCO, rowheight=25)
        style.configure("Treeview.Heading", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 9, "bold"))

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
            self.lbl_nombre.config(text=f"Vecino: {usuarios[dni].get('nombre', 'Sin nombre')} (DNI: {dni})")
            self.lbl_saldo.config(text=f"Saldo Disponible: {usuarios[dni].get('puntos', 0)} PTS")
            self.btn_canjear.config(state="normal")
        else:
            self.vecino_actual = None
            self.lbl_nombre.config(text="Vecino no encontrado")
            self.lbl_saldo.config(text="Saldo Disponible: 0 PTS")
            self.btn_canjear.config(state="disabled")
            messagebox.showwarning("No Encontrado", "El DNI ingresado no pertenece a un vecino registrado.")

    def abrir_cuadro_canje(self):
        """Muestra las ofertas disponibles y descuenta automáticamente el stock según las unidades canjeadas."""
        if not self.vecino_actual:
            return

        usuarios = cargar_usuarios()
        saldo_actual = int(usuarios.get(self.vecino_actual, {}).get("puntos", 0))

        if saldo_actual <= 0:
            messagebox.showerror("Saldo Insuficiente", "El vecino no cuenta con puntos para canjear.")
            return

        promos = cargar_promociones()
        mis_promos = [(i, p) for i, p in enumerate(promos) if str(p.get("tienda_id")) == str(self.id_usuario) and int(p.get("stock", 0)) > 0]

        if not mis_promos:
            messagebox.showwarning("Sin Ofertas Disponibles", "Este comercio no tiene ofertas con stock disponible en este momento.")
            return

        win_cobro = tk.Toplevel(self.root)
        win_cobro.config(bg=COLOR_FONDO_APP)
        win_cobro.title("Canje de Ofertas en Caja")
        win_cobro.geometry("520x480")
        win_cobro.resizable(False, False)
        win_cobro.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_cobro.iconphoto(False, self.root.icon_img)

        nombre_vecino = usuarios.get(self.vecino_actual, {}).get("nombre", "Cliente")
        tk.Label(
            win_cobro, 
            text=f"Vecino: {nombre_vecino} | Saldo: {saldo_actual} PTS", 
            font=("Arial", 11, "bold"), 
            fg=COLOR_TEXTO_MAIN,
            bg=COLOR_FONDO_APP
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tk.Label(
            win_cobro, 
            text="Seleccione las ofertas y la cantidad a canjear:", 
            font=("Arial", 9, "bold"),
            fg=COLOR_TEXTO_MAIN,
            bg=COLOR_FONDO_APP
        ).pack(anchor="w", padx=20, pady=(5, 5))

        frame_scroll_container = tk.Frame(win_cobro, bg=COLOR_BLANCO, bd=1, relief="solid")
        frame_scroll_container.pack(fill="both", expand=True, padx=20, pady=5)

        canvas = tk.Canvas(frame_scroll_container, bg=COLOR_BLANCO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_scroll_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_BLANCO)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        items_canje = []
        for idx_promo, p in mis_promos:
            row_frame = tk.Frame(scroll_frame, bg=COLOR_BLANCO)
            row_frame.pack(fill="x", padx=10, pady=5)

            var_chk = tk.BooleanVar()
            costo = int(float(p.get("puntos", 0)))
            titulo = p.get("titulo", "Oferta")
            stock_max = int(p.get("stock", 0))

            chk = tk.Checkbutton(
                row_frame, 
                text=f"{titulo} ({costo} PTS) - Stock: {stock_max}", 
                variable=var_chk, 
                bg=COLOR_BLANCO, 
                fg=COLOR_TEXTO_MAIN,
                font=("Arial", 9, "bold"), 
                anchor="w"
            )
            chk.pack(side="left", fill="x", expand=True)

            tk.Label(row_frame, text="Cant:", font=("Arial", 9), bg=COLOR_BLANCO).pack(side="left", padx=(5, 2))
            spin_cant = tk.Spinbox(row_frame, from_=1, to=stock_max, width=4, font=("Arial", 9))
            spin_cant.pack(side="right", padx=5)

            items_canje.append((idx_promo, var_chk, spin_cant, costo, titulo, stock_max))

        frame_btns = tk.Frame(win_cobro, bg=COLOR_FONDO_APP)
        frame_btns.pack(pady=15)

        def procesar_canje_seleccionado():
            puntos_totales = 0
            ofertas_canjeadas = []
            operaciones_stock = []

            for idx_promo, var, spin, costo, titulo, stock_max in items_canje:
                if var.get():
                    try:
                        cant = int(spin.get())
                        if cant <= 0:
                            continue
                        if cant > stock_max:
                            messagebox.showerror("Error de Stock", f"La cantidad solicitada de '{titulo}' excede el stock disponible ({stock_max}).")
                            return
                        
                        subtotal = costo * cant
                        puntos_totales += subtotal
                        ofertas_canjeadas.append(f"{cant}x {titulo}")
                        operaciones_stock.append((idx_promo, cant))
                    except ValueError:
                        messagebox.showerror("Error", f"Ingrese una cantidad válida para '{titulo}'.")
                        return

            if puntos_totales == 0:
                messagebox.showwarning("Atención", "Debe seleccionar al menos una oferta para canjear.")
                return

            if puntos_totales > saldo_actual:
                messagebox.showerror(
                    "Error de Saldo", 
                    f"El total seleccionado ({puntos_totales} PTS) supera el saldo disponible del vecino ({saldo_actual} PTS)."
                )
                return

            # 1. Descontar Puntos al Vecino
            usuarios[self.vecino_actual]["puntos"] -= puntos_totales
            guardar_usuarios(usuarios)

            # 2. Descontar Stock de las Ofertas en promociones.json
            promos_actuales = cargar_promociones()
            for idx_p, cant_descontar in operaciones_stock:
                if idx_p < len(promos_actuales):
                    stock_prev = int(promos_actuales[idx_p].get("stock", 0))
                    nuevo_stock = max(0, stock_prev - cant_descontar)
                    promos_actuales[idx_p]["stock"] = nuevo_stock
            guardar_promociones(promos_actuales)

            # 3. Registrar Transacción en Logs (tanto en tienda como en cliente)
            try:
                registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, puntos_totales)
                registrar_accion_cliente(
                    self.vecino_actual, 
                    "CANJE_TIENDA", 
                    -puntos_totales, 
                    f"Canje de ofertas: {', '.join(ofertas_canjeadas)} en {self.nombre_negocio}"
                )
            except Exception as e:
                print(f"Aviso log: {e}")

            messagebox.showinfo("Éxito", f"¡Canje completado!\nSe han descontado {puntos_totales} PTS y actualizado el stock de productos.")
            win_cobro.destroy()
            self.consultar_vecino()
            self.actualizar_historial_tienda()

        tk.Button(
            frame_btns, 
            text="Aceptar / Canjear Seleccionadas", 
            bg=COLOR_ACENTO_CANJE, 
            fg=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), 
            command=procesar_canje_seleccionado, 
            relief="flat", 
            padx=10, 
            pady=5, 
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btns, 
            text="Cancelar", 
            bg="#757575", 
            fg=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), 
            command=win_cobro.destroy, 
            relief="flat", 
            padx=10, 
            pady=5, 
            cursor="hand2"
        ).pack(side="left", padx=5)

    def dialogo_publicar_promocion(self):
        """Permite publicar una oferta especificando categoría clara y cantidad inicial en stock."""
        win_promo = tk.Toplevel(self.root)
        win_promo.config(bg=COLOR_FONDO_APP)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("420x500")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        # Título
        tk.Label(win_promo, text="Título de Promoción (Máx 25 caract.):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_titulo.pack(fill="x", padx=20)

        # Categoría
        tk.Label(win_promo, text="Categoría de la Oferta:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        combo_categoria = ttk.Combobox(
            win_promo, 
            state="readonly", 
            values=CATEGORIAS_BODEGA, 
            font=("Arial", 10)
        )
        combo_categoria.pack(fill="x", padx=20)
        combo_categoria.set("Abarrotes y Despensa")

        # Cantidad en Stock Inicial
        tk.Label(win_promo, text="Cantidad Inicial en Stock (Unidades):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        ent_stock = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_stock.pack(fill="x", padx=20)
        ent_stock.insert(0, "10")

        # Precio en Soles
        tk.Label(win_promo, text="Precio Normal en Soles (S/):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        ent_precio = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_precio.pack(fill="x", padx=20)

        lbl_pts_equiv = tk.Label(win_promo, text="Equivalente: 0.0 PTS", font=("Arial", 10, "bold"), fg=COLOR_PRIMARIO, bg=COLOR_FONDO_APP)
        lbl_pts_equiv.pack(anchor="w", padx=20, pady=4)

        def calcular_pts_event(event=None):
            try:
                monto_soles = float(ent_precio.get().strip())
                pts = round(monto_soles / 0.10, 1)
                lbl_pts_equiv.config(text=f"Equivalente: {pts} PTS")
            except ValueError:
                lbl_pts_equiv.config(text="Equivalente: 0.0 PTS")

        ent_precio.bind("<KeyRelease>", calcular_pts_event)

        # Descripción
        tk.Label(win_promo, text="Descripción:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        ent_desc = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_desc.pack(fill="x", padx=20)

        def guardar_promo():
            titulo = ent_titulo.get().strip()
            categoria = combo_categoria.get()
            stock_str = ent_stock.get().strip()
            desc = ent_desc.get().strip()
            precio_str = ent_precio.get().strip()

            if len(titulo) == 0 or len(titulo) > 25:
                messagebox.showerror("Error", "El título es obligatorio y debe tener como máximo 25 caracteres.")
                return

            try:
                stock_val = int(stock_str)
                if stock_val <= 0:
                    messagebox.showerror("Error", "El stock inicial debe ser mayor a 0.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número entero válido para el stock.")
                return

            if len(desc) == 0 or len(desc) > 100:
                messagebox.showerror("Error", "La descripción es obligatoria y debe tener como máximo 100 caracteres.")
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
                "categoria": categoria,
                "descripcion": desc,
                "precio_soles": precio_soles,
                "puntos": pts_requeridos,
                "stock": stock_val,
                "foto": ""
            })
            guardar_promociones(promos)

            messagebox.showinfo("Éxito", "¡Promoción publicada correctamente!")
            win_promo.destroy()

        tk.Button(win_promo, text="💾 Publicar Oferta", bg=COLOR_PRIMARIO, fg=COLOR_BLANCO, font=("Arial", 10, "bold"), command=guardar_promo, relief="flat", pady=6, cursor="hand2").pack(pady=20)

    def mostrar_terminos_negocio(self):
        win_tyc = tk.Toplevel(self.root)
        win_tyc.config(bg=COLOR_FONDO_APP)
        win_tyc.title("📜 Términos y Condiciones — Bodegas EcoPuntos")
        win_tyc.geometry("520x460")
        win_tyc.resizable(False, False)
        win_tyc.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_tyc.iconphoto(False, self.root.icon_img)

        tk.Label(win_tyc, text="📜 Términos y Condiciones (Negocios / Bodegas)", font=("Arial", 12, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=(15, 10))

        frame_txt = tk.Frame(win_tyc, padx=15, pady=5, bg=COLOR_FONDO_APP)
        frame_txt.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_txt)
        scrollbar.pack(side="right", fill="y")

        txt_box = tk.Text(
            frame_txt, 
            wrap="word", 
            yscrollcommand=scrollbar.set, 
            font=("Arial", 10), 
            bg=COLOR_BLANCO, 
            fg=COLOR_TEXTO_MAIN, 
            padx=10, 
            pady=10
        )
        txt_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt_box.yview)

        contenido = (
            "REGLAS DE OPERACIÓN PARA BODEGAS Y COMERCIOS — ECOPUNTOS\n\n"
            "1. GESTIÓN DE CANJES Y VENTAS PRESENCIALES\n"
            "• Toda transacción de puntos, entrega de productos ofertados o descuentos en caja debe realizarse de forma presencial mediante la validación del DNI del vecino en esta terminal.\n\n"
            "2. LÍMITE DE PUNTOS POR CLIENTE\n"
            "• Ningún vecino podrá acumular más de 2,000 puntos (S/ 200.00) en su saldo activo. Si un cliente alcanza el tope, se le exhortará a realizar canjes antes de recibir nuevos abonos por reciclaje.\n\n"
            "3. CONTROL DE INVENTARIO Y STOCK\n"
            "• El comercio es responsable de mantener actualizado el stock y los precios de sus ofertas publicadas. Cada entrega validada descuenta la unidad correspondiente del sistema.\n\n"
            "Al operar como comercio afiliado, usted acepta cumplir estas normativas."
        )

        txt_box.insert("1.0", contenido)
        txt_box.config(state="disabled")

        tk.Button(win_tyc, text="Entendido 👍", bg=COLOR_PRIMARIO, fg=COLOR_BLANCO, font=("Arial", 10, "bold"), command=win_tyc.destroy, padx=20, pady=8, cursor="hand2").pack(pady=12)

    def actualizar_historial_tienda(self):
        """Lee directamente de los registros de la tienda para mostrar las entregas al instante."""
        for item in self.tabla_historial_tienda.get_children():
            self.tabla_historial_tienda.delete(item)

        logs = cargar_log_tiendas()
        for log in reversed(logs):
            if str(log.get("tienda_id")) == str(self.id_usuario):
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
        """Filtra y muestra exclusivamente las reseñas y calificaciones dirigidas a este negocio."""
        for item in self.tabla_resenas_negocio.get_children():
            self.tabla_resenas_negocio.delete(item)

        logs = cargar_log_clientes()
        mis_resenas = []
        suma_calificaciones = 0
        nombre_lower = self.nombre_negocio.strip().lower()

        for log in reversed(logs):
            tipo = log.get("tipo", "")
            detalle = log.get("detalle", "").strip()
            
            # Validamos que sea un log de tipo reseña y que mencione explícitamente el nombre de este negocio
            if "RESEÑA" in tipo or "Reseña para" in detalle:
                detalle_lower = detalle.lower()
                if nombre_lower in detalle_lower:
                    fecha = log.get("fecha", "-")
                    dni = log.get("dni_cliente", "-")
                    
                    estrellas_str = "⭐ (Sin calificación)"
                    comentario_str = detalle
                    valor_numerico = 5  # Valor por defecto

                    if "Calificación:" in detalle:
                        try:
                            partes = detalle.split("Calificación:")
                            if len(partes) > 1:
                                subpartes = partes[1].split("|")
                                estrellas_str = subpartes[0].strip()
                                if len(subpartes) > 1:
                                    comentario_str = subpartes[1].replace("Reseña:", "").strip()
                                
                                if "(" in estrellas_str:
                                    num_extraido = estrellas_str.split("(")[1].split("/")[0].strip()
                                    valor_numerico = int(num_extraido)
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
        """Muestra de forma robusta las ofertas agrupadas por secciones sin congelar el lienzo."""
        win_list = tk.Toplevel(self.root)
        win_list.title("Mis Ofertas Publicadas - Gestión")
        win_list.geometry("680x540")
        win_list.resizable(False, False)
        win_list.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_list.iconphoto(False, self.root.icon_img)

        # Contenedor principal con canvas y scroll
        canvas = tk.Canvas(win_list, bg=COLOR_BLANCO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win_list, orient="vertical", command=canvas.yview)
        frame_container = tk.Frame(canvas, bg=COLOR_BLANCO)

        def actualizar_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_container.bind("<Configure>", actualizar_scroll)
        canvas_window = canvas.create_window((0, 0), window=frame_container, anchor="nw")

        def ajustar_ancho_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', ajustar_ancho_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def refrescar():
            for w in frame_container.winfo_children(): 
                w.destroy()
                
            promos = cargar_promociones()
            mis_promos = [(i, p) for i, p in enumerate(promos) if str(p.get("tienda_id")) == str(self.id_usuario)]

            if not mis_promos:
                lbl_vacio = tk.Label(
                    frame_container, 
                    text="No tienes ofertas publicadas actualmente.\n¡Usa el botón de 'Publicar Nueva Oferta' para agregar productos!", 
                    font=("Arial", 11, "italic"), 
                    fg="#757575", 
                    bg=COLOR_BLANCO,
                    justify="center"
                )
                lbl_vacio.pack(pady=80, padx=50)
                return

            # Título general
            lbl_titulo = tk.Label(
                frame_container, 
                text=f"Total de Ofertas Publicadas: {len(mis_promos)}", 
                font=("Arial", 12, "bold"), 
                fg=COLOR_TEXTO_MAIN,
                bg=COLOR_BLANCO
            )
            lbl_titulo.pack(anchor="w", padx=20, pady=(15, 10))

            # Agrupar ofertas por categorías definidas
            categorias_dict = {cat: [] for cat in CATEGORIAS_BODEGA}
            for idx, p in mis_promos:
                cat = p.get("categoria", "Abarrotes y Despensa")
                if cat in categorias_dict:
                    categorias_dict[cat].append((idx, p))
                else:
                    categorias_dict["Abarrotes y Despensa"].append((idx, p))

            # Renderizar Secciones
            for cat_nombre, lista_items in categorias_dict.items():
                if not lista_items:
                    continue

                # Header de Sección
                lbl_sec = tk.Label(
                    frame_container, 
                    text=f"📂 {cat_nombre.upper()}", 
                    font=("Arial", 10, "bold"), 
                    bg=COLOR_FONDO_APP, 
                    fg=COLOR_TEXTO_MAIN, 
                    anchor="w",
                    padx=10,
                    pady=6
                )
                lbl_sec.pack(fill="x", padx=20, pady=(12, 6))

                for idx, p in lista_items:
                    card = tk.Frame(
                        frame_container, 
                        bg=COLOR_BLANCO, 
                        bd=1, 
                        relief="solid", 
                        highlightbackground=COLOR_SECUNDARIO, 
                        highlightthickness=1,
                        padx=15, 
                        pady=10
                    )
                    card.pack(fill="x", padx=20, pady=4)

                    stock_disp = p.get("stock", "0")
                    puntos_int = int(float(p.get('puntos', 0)))
                    txt_info = f"• {p.get('titulo', 'Oferta')}  |  Costo: {puntos_int} PTS  |  S/ {p.get('precio_soles', 0):.2f}\n  Stock Disponible: {stock_disp} unids.  —  {p.get('descripcion', '')}"
                    
                    tk.Label(
                        card, 
                        text=txt_info, 
                        font=("Arial", 9), 
                        bg=COLOR_BLANCO, 
                        fg=COLOR_TEXTO_MAIN, 
                        justify="left"
                    ).pack(side="left", anchor="w", expand=True)

                    def borrar(i=idx):
                        if messagebox.askyesno("Eliminar Promoción", "¿Deseas eliminar permanentemente esta oferta del sistema?"):
                            if eliminar_promocion(i, self.id_usuario, self.nombre_negocio):
                                messagebox.showinfo("Éxito", "La oferta ha sido eliminada correctamente.")
                                refrescar()

                    tk.Button(
                        card, 
                        text="Eliminar", 
                        bg=COLOR_ROJO_ELIMINAR, 
                        fg=COLOR_BLANCO, 
                        activeforeground=COLOR_BLANCO, 
                        font=("Arial", 9, "bold"), 
                        relief="flat", 
                        command=borrar, 
                        cursor="hand2", 
                        padx=10, 
                        pady=5
                    ).pack(side="right", padx=5)

            win_list.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        refrescar()