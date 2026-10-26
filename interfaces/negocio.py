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
                text=f"🏪 Terminal de Canje: {self.nombre_negocio}", 
                font=("Arial", 14, "bold"), 
                fg="white", 
                bg="#E65100", 
                pady=12
            ).pack()

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
                text=" 1. Consultar Cuenta del Vecino ", 
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
                text=" 2. Estado de Cuenta ", 
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

            # Botones de Operación (Con contraste de texto corregido)
            frame_botones_accion = tk.Frame(frame_central, bg="white")
            frame_botones_accion.pack(fill="x", pady=(0, 10))

            self.btn_validar_oferta = tk.Button(
                frame_botones_accion, 
                text="📦 Validar y Entregar Oferta (0 Puntos)", 
                bg="#2E7D32", 
                fg="white", 
                activeforeground="white",
                disabledforeground="#E0E0E0",
                font=("Arial", 10, "bold"), 
                state="disabled", 
                relief="flat", 
                command=self.validar_entrega_oferta,
                pady=8,
                cursor="hand2"
            )
            self.btn_validar_oferta.pack(side="left", fill="x", expand=True, padx=(0, 5))

            self.btn_canjear = tk.Button(
                frame_botones_accion, 
                text="💳 Descuento Libre en Caja", 
                bg="#E65100", 
                fg="white", 
                activeforeground="white",
                disabledforeground="#E0E0E0",
                font=("Arial", 10, "bold"), 
                state="disabled", 
                relief="flat", 
                command=self.abrir_cuadro_canje,
                pady=8,
                cursor="hand2"
            )
            self.btn_canjear.pack(side="right", fill="x", expand=True, padx=(5, 0))

            # Botón Publicar Promoción
            tk.Button(
                frame_central, 
                text="📢 Publicar Nueva Promoción / Oferta", 
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
                text="📜 Historial de Canjes Realizados a Clientes:", 
                font=("Arial", 11, "bold"), 
                bg="white",
                fg="#333333"
            ).pack(anchor="w", pady=(0, 5))

            cols_log = ("fecha", "dni_cliente", "puntos")
            config_log = [
                ("fecha", "Fecha / Hora", 200),
                ("dni_cliente", "DNI del Cliente", 180),
                ("puntos", "Puntos Descontados", 160)
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

    def actualizar_historial_tienda(self):
        for item in self.tabla_historial_tienda.get_children():
            self.tabla_historial_tienda.delete(item)

        logs = cargar_log_tiendas()
        for log in reversed(logs):
            if log.get("tienda_id") == self.id_usuario:
                self.tabla_historial_tienda.insert(
                    "", 
                    "end", 
                    values=(
                        log.get("fecha", "-"), 
                        log.get("dni_cliente", "-"), 
                        f"-{log.get('puntos_descontados', 0)} PTS"
                    )
                )

    def actualizar_resenas_negocio(self):
        """Filtra y calcula las calificaciones de este negocio específico desde el log de clientes."""
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
                tk.Label(frame_container, text="No tienes promociones activas actualmente.", font=("Arial", 11, "italic"), bg="white", fg="#757575").pack(pady=50)
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
                txt_info = f"📌 {p['titulo']} (Costo: {p['puntos']} PTS / S/ {p['precio_soles']:.2f})\n📦 Stock Disponible: {stock_disp}\n📝 {p['descripcion']}"
                tk.Label(card, text=txt_info, font=("Arial", 9), bg="#FFF8E1", justify="left").pack(side="left", anchor="w", expand=True)

                def borrar(i=idx):
                    if messagebox.askyesno("Eliminar Promoción", "¿Deseas eliminar permanentemente esta oferta del sistema?"):
                        if eliminar_promocion(i, self.id_usuario, self.nombre_negocio):
                            messagebox.showinfo("Éxito", "La promoción ha sido eliminada correctamente.")
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
            self.lbl_nombre.config(text=f"Vecino: {usuarios[dni].get('nombre', 'Sin nombre')} (DNI: {dni})")
            self.lbl_saldo.config(text=f"Saldo Disponible: {usuarios[dni].get('puntos', 0)} PTS")
            self.btn_canjear.config(state="normal")
            self.btn_validar_oferta.config(state="normal")
        else:
            self.vecino_actual = None
            self.lbl_nombre.config(text="Vecino no encontrado")
            self.lbl_saldo.config(text="Saldo Disponible: 0 PTS")
            self.btn_canjear.config(state="disabled")
            self.btn_validar_oferta.config(state="disabled")
            messagebox.showwarning("No Encontrado", "El DNI ingresado no pertenece a un vecino registrado.")

    def validar_entrega_oferta(self):
        if not self.vecino_actual: return

        usuarios = cargar_usuarios()
        nombre_vecino = usuarios[self.vecino_actual].get('nombre', 'Cliente')

        if messagebox.askyesno("Confirmar Entrega de Oferta", f"¿Confirmar la entrega del producto canjeado al vecino {nombre_vecino}?\n\nEsta operación valida el cupón con 0 puntos adicionales."):
            try:
                registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, 0)
                registrar_accion_cliente(self.vecino_actual, "ENTREGA_OFERTA", 0, f"Retiro de producto canjeado en {self.nombre_negocio}")
            except Exception as e:
                print(f"Aviso log entrega: {e}")

            messagebox.showinfo("¡Entrega Exitosa!", f"Se ha validado la entrega del producto a {nombre_vecino}.")
            self.consultar_vecino()
            self.actualizar_historial_tienda()

    def abrir_cuadro_canje(self):
        if not self.vecino_actual: return
        
        usuarios = cargar_usuarios()
        saldo_actual = usuarios[self.vecino_actual].get("puntos", 0)

        if saldo_actual <= 0:
            messagebox.showerror("Saldo Insuficiente", "El vecino no cuenta con puntos para canjear.")
            return

        pts_canje = simpledialog.askinteger(
            "Confirmar Canje", 
            f"Vecino: {usuarios[self.vecino_actual]['nombre']}\nSaldo actual: {saldo_actual} PTS\n\n¿Cuántos puntos desea descontar?",
            parent=self.root, 
            minvalue=1, 
            maxvalue=saldo_actual
        )

        if pts_canje and messagebox.askyesno("Confirmar Operación", f"¿Descontar {pts_canje} puntos?"):
            usuarios[self.vecino_actual]["puntos"] = round(usuarios[self.vecino_actual]["puntos"] - pts_canje, 1)
            guardar_usuarios(usuarios)

            try:
                registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, pts_canje)
                registrar_accion_cliente(self.vecino_actual, "CANJE_TIENDA", -pts_canje, f"Compra/Canje en {self.nombre_negocio}")
            except Exception as e:
                print(f"Aviso log: {e}")

            messagebox.showinfo("Éxito", "El canje se ha registrado correctamente.")
            self.consultar_vecino()
            self.actualizar_historial_tienda()

    def dialogo_publicar_promocion(self):
        win_promo = tk.Toplevel(self.root)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("380x520")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        tk.Label(win_promo, text="Título de Promoción:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10))
        ent_titulo.pack(fill="x", padx=20)

        tk.Label(win_promo, text="Precio Normal en Soles (S/):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_precio = tk.Entry(win_promo, font=("Arial", 10))
        ent_precio.pack(fill="x", padx=20)

        lbl_pts_equiv = tk.Label(win_promo, text="Equivalente: 0.0 PTS", font=("Arial", 10, "bold"), fg="#2E7D32")
        lbl_pts_equiv.pack(anchor="w", padx=20, pady=4)

        def calcular_pts_event(event=None):
            try:
                monto_soles = float(ent_precio.get().strip())
                pts = round(monto_soles / 0.10, 1)
                lbl_pts_equiv.config(text=f"Equivalente: {pts} PTS")
            except ValueError:
                lbl_pts_equiv.config(text="Equivalente: 0.0 PTS")

        ent_precio.bind("<KeyRelease>", calcular_pts_event)

        tk.Label(win_promo, text="Stock / Cantidad Disponible:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_stock = tk.Entry(win_promo, font=("Arial", 10))
        ent_stock.pack(fill="x", padx=20)
        ent_stock.insert(0, "10")

        tk.Label(win_promo, text="Descripción Corta:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_desc = tk.Entry(win_promo, font=("Arial", 10))
        ent_desc.pack(fill="x", padx=20)

        ruta_foto = {"path": ""}
        lbl_foto_estado = tk.Label(win_promo, text="Imagen: No seleccionada", font=("Arial", 8, "italic"), fg="#757575")
        
        def seleccionar_imagen():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Seleccionar foto del producto",
                filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
            )
            if file_path:
                ruta_foto["path"] = file_path
                lbl_foto_estado.config(text=f"Imagen: {os.path.basename(file_path)}", fg="#2E7D32")

        tk.Button(win_promo, text="📷 Subir Foto (Opcional)", bg="#1976D2", fg="white", activeforeground="white", command=seleccionar_imagen, relief="flat").pack(pady=(10, 2))
        lbl_foto_estado.pack()

        def guardar_promo():
            titulo = ent_titulo.get().strip()
            desc = ent_desc.get().strip()
            precio_str = ent_precio.get().strip()
            stock_str = ent_stock.get().strip()

            if len(titulo) == 0 or len(titulo) > 100:
                messagebox.showerror("Error", "El título es obligatorio y no puede superar los 100 caracteres.")
                return

            if len(desc) == 0 or len(desc) > 100:
                messagebox.showerror("Error", "La descripción es obligatoria y no puede superar los 100 caracteres.")
                return

            try:
                precio_soles = float(precio_str)
                pts_requeridos = round(precio_soles / 0.10, 1)
                stock = int(stock_str)
                if stock <= 0: raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un precio válido y un stock numérico mayor a 0.")
                return

            promos = cargar_promociones()
            promos.append({
                "tienda_id": self.id_usuario,
                "tienda_nombre": self.nombre_negocio,
                "titulo": titulo,
                "descripcion": desc,
                "precio_soles": precio_soles,
                "puntos": pts_requeridos,
                "stock": stock,
                "foto": ruta_foto["path"]
            })
            guardar_promociones(promos)

            messagebox.showinfo("Éxito", "¡Promoción publicada correctamente!")
            win_promo.destroy()

        tk.Button(win_promo, text="💾 Publicar Oferta", bg="#2E7D32", fg="white", activeforeground="white", font=("Arial", 10, "bold"), command=guardar_promo, relief="flat", pady=6).pack(pady=15)