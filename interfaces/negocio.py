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

# ==========================================
# PALETA DE COLORES "ECO-GESTIÓN" (SIN NEGRO)
# ==========================================
COLOR_FONDO_APP      = "#F4F9F4"  # Blanco Menta Suave (Fondo general)
COLOR_TEXTO_MAIN     = "#1B4332"  # Verde Bosque Profundo (Reemplazo de negro)
COLOR_PRIMARIO       = "#40916C"  # Verde Hoja (Headers / Acciones principales)
COLOR_SECUNDARIO     = "#52B788"  # Verde Claro Fresco (Bordes / Elementos activos)
COLOR_ACENTO_CANJE   = "#E76F51"  # Terracota Suave (Recompensas, Puntos y Alertas)
COLOR_BLANCO         = "#FFFFFF"  # Blanco puro para tarjetas e inputs
COLOR_ROJO_ELIMINAR  = "#C62828"  # Rojo para el botón de eliminar

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

            # 1. CARGA DE IMAGEN DE FONDO (Dimensiones requeridas: 980x740 px)
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

            # Botón único de Canje Presencial (Acento Terracota)
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
        if not self.vecino_actual:
            return

        usuarios = cargar_usuarios()
        saldo_actual = int(usuarios.get(self.vecino_actual, {}).get("puntos", 0))

        if saldo_actual <= 0:
            messagebox.showerror("Saldo Insuficiente", "El vecino no cuenta con puntos para canjear.")
            return

        promos = cargar_promociones()
        mis_promos = [p for p in promos if str(p.get("tienda_id")) == str(self.id_usuario)]

        if not mis_promos:
            messagebox.showwarning("Sin Ofertas", "Este comercio no tiene ofertas o promociones publicadas actualmente.")
            return

        win_cobro = tk.Toplevel(self.root)
        win_cobro.config(bg=COLOR_FONDO_APP)
        win_cobro.title("Canje de Ofertas en Caja")
        win_cobro.geometry("480x450")
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
            text="Seleccione una o varias ofertas a canjear:", 
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

        vars_promos = []
        for p in mis_promos:
            var = tk.BooleanVar()
            costo = int(float(p.get("puntos", 0)))
            titulo = p.get("titulo", "Oferta")
            stock = p.get("stock", "10")
            texto_chk = f"{titulo} — Costo: {costo} PTS (Stock: {stock})"
            
            chk = tk.Checkbutton(
                scroll_frame, 
                text=texto_chk, 
                variable=var, 
                bg=COLOR_BLANCO, 
                fg=COLOR_TEXTO_MAIN,
                activebackground=COLOR_BLANCO,
                activeforeground=COLOR_TEXTO_MAIN,
                font=("Arial", 9), 
                anchor="w"
            )
            chk.pack(fill="x", padx=10, pady=4, anchor="w")
            vars_promos.append((var, costo, titulo))

        frame_btns = tk.Frame(win_cobro, bg=COLOR_FONDO_APP)
        frame_btns.pack(pady=15)

        def procesar_canje_seleccionado():
            puntos_totales = 0
            ofertas_canjeadas = []

            for var, costo, titulo in vars_promos:
                if var.get():
                    puntos_totales += costo
                    ofertas_canjeadas.append(titulo)

            if puntos_totales == 0:
                messagebox.showwarning("Atención", "Debe seleccionar al menos una oferta para canjear.")
                return

            if puntos_totales > saldo_actual:
                messagebox.showerror(
                    "Error de Saldo", 
                    f"El total seleccionado ({puntos_totales} PTS) supera el saldo disponible del vecino ({saldo_actual} PTS)."
                )
                return

            usuarios[self.vecino_actual]["puntos"] -= puntos_totales
            guardar_usuarios(usuarios)

            try:
                registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, puntos_totales)
                registrar_accion_cliente(
                    self.vecino_actual, 
                    "CANJE_TIENDA", 
                    -puntos_totales, 
                    f"Canje de ofertas: {', '.join(ofertas_canjeadas)}"
                )
            except Exception as e:
                print(f"Aviso log: {e}")

            messagebox.showinfo("Éxito", f"¡Canje completado! Se han descontado {puntos_totales} PTS en total.")
            win_cobro.destroy()
            self.consultar_vecino()

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
        win_promo = tk.Toplevel(self.root)
        win_promo.config(bg=COLOR_FONDO_APP)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("380x380")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        tk.Label(win_promo, text="Título de Promoción (Máx 25 caract.):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_titulo.pack(fill="x", padx=20)

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

        tk.Label(win_promo, text="Descripción:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        ent_desc = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_desc.pack(fill="x", padx=20)

        def guardar_promo():
            titulo = ent_titulo.get().strip()
            desc = ent_desc.get().strip()
            precio_str = ent_precio.get().strip()

            if len(titulo) == 0 or len(titulo) > 25:
                messagebox.showerror("Error", "El título es obligatorio y debe tener como máximo 25 caracteres.")
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
                "descripcion": desc,
                "precio_soles": precio_soles,
                "puntos": pts_requeridos,
                "stock": 10,
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
            "• Toda transacción de puntos, entrega de productos ofertados o descuentos en caja debe realizarse de forma estrictamente presencial mediante la validación del DNI del vecino en esta terminal.\n\n"
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
        """Lista las promociones utilizando una imagen personalizada para el contenedor interno."""
        win_list = tk.Toplevel(self.root)
        win_list.title("Mis Ofertas Publicadas - Gestión")
        win_list.geometry("640x480")
        win_list.resizable(False, False)
        win_list.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_list.iconphoto(False, self.root.icon_img)

        # 1. Fondo de la ventana modal completa (640x480 px)
        ruta_fondo_modal = os.path.join("img", "fondo_mis_ofertas.png")
        if not os.path.exists(ruta_fondo_modal):
            ruta_fondo_modal = os.path.join("img", "fondo_negocio.png")

        padre_ui = win_list
        if os.path.exists(ruta_fondo_modal):
            try:
                win_list.bg_img = tk.PhotoImage(file=ruta_fondo_modal)
                lbl_fondo = tk.Label(win_list, image=win_list.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
                padre_ui = lbl_fondo
            except Exception as e:
                print(f"Aviso imagen de fondo modal: {e}")

        # 2. Imagen contenedora central (590x430 px) en reemplazo del recuadro gris
        ruta_tarjeta = os.path.join("img", "tarjeta_contenedor.png")
        if os.path.exists(ruta_tarjeta):
            try:
                win_list.img_tarjeta = tk.PhotoImage(file=ruta_tarjeta)
                lbl_tarjeta = tk.Label(padre_ui, image=win_list.img_tarjeta, bg=COLOR_FONDO_APP)
                lbl_tarjeta.pack(fill="both", expand=True, padx=25, pady=25)
                frame_container = lbl_tarjeta
            except Exception:
                frame_container = tk.Frame(padre_ui, bg=COLOR_FONDO_APP)
                frame_container.pack(fill="both", expand=True, padx=25, pady=25)
        else:
            # Si no hay imagen asignada, usa transparencia nativa
            frame_container = tk.Frame(padre_ui, bg=COLOR_FONDO_APP)
            frame_container.pack(fill="both", expand=True, padx=25, pady=25)

        def refrescar():
            for w in frame_container.winfo_children(): 
                w.destroy()
            promos = cargar_promociones()
            mis_promos = [(i, p) for i, p in enumerate(promos) if str(p.get("tienda_id")) == str(self.id_usuario)]

            if not mis_promos:
                lbl_vacio = tk.Label(frame_container, text="No tienes ofertas publicadas actualmente.", font=("Arial", 11, "italic"), fg="#757575", bg=COLOR_BLANCO)
                lbl_vacio.pack(pady=50)
                return

            # Título
            lbl_titulo = tk.Label(
                frame_container, 
                text=f"Total de ofertas publicadas: {len(mis_promos)}", 
                font=("Arial", 11, "bold"), 
                fg=COLOR_TEXTO_MAIN,
                bg=COLOR_BLANCO
            )
            lbl_titulo.pack(anchor="w", padx=15, pady=(15, 10))

            for idx, p in mis_promos:
                # TARJETA BLANCA DE CADA OFERTA
                card = tk.Frame(
                    frame_container, 
                    bg=COLOR_BLANCO, 
                    bd=1, 
                    relief="solid", 
                    highlightbackground=COLOR_SECUNDARIO, 
                    highlightthickness=1,
                    padx=15, 
                    pady=12
                )
                card.pack(fill="x", padx=15, pady=6)

                stock_disp = p.get("stock", "10")
                puntos_int = int(float(p.get('puntos', 0)))
                txt_info = f"📌 {p.get('titulo', 'Oferta')} (Costo: {puntos_int} PTS / S/ {p.get('precio_soles', 0):.2f})\n📦 Stock Disponible: {stock_disp}\n📝 {p.get('descripcion', '')}"
                
                tk.Label(
                    card, 
                    text=txt_info, 
                    font=("Arial", 9, "bold"), 
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
                    text="🗑️ Eliminar", 
                    bg=COLOR_ROJO_ELIMINAR, 
                    fg=COLOR_BLANCO, 
                    activeforeground=COLOR_BLANCO, 
                    font=("Arial", 9, "bold"), 
                    relief="flat", 
                    command=borrar, 
                    cursor="hand2", 
                    padx=12, 
                    pady=6
                ).pack(side="right", padx=5)

        refrescar()