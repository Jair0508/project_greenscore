import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, 
    guardar_usuarios, 
    registrar_accion_tienda, 
    registrar_accion_cliente,
    cargar_promociones, 
    guardar_promociones,
    eliminar_promocion
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
            self.root.geometry("950x680")
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

            # CONTENEDOR CENTRAL (Definición obligatoria)
            frame_central = tk.Frame(self.root, bg="white", bd=1, relief="solid", padx=25, pady=20)
            frame_central.pack(pady=30, padx=50, fill="both", expand=True)

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

            tk.Button(
                frame_busca, 
                text="🔍 Buscar Cuenta", 
                bg="#1976D2", 
                fg="white", 
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

            # Botón Procesar Canje
            self.btn_canjear = tk.Button(
                frame_central, 
                text="💳 Procesar Descuento / Canje de Puntos", 
                bg="#E65100", 
                fg="white", 
                font=("Arial", 11, "bold"), 
                state="disabled", 
                relief="flat", 
                command=self.abrir_cuadro_canje,
                pady=8,
                cursor="hand2"
            )
            self.btn_canjear.pack(fill="x", pady=(0, 10))

            # Botón Publicar Promoción
            tk.Button(
                frame_central, 
                text="📢 Publicar Nueva Promoción / Oferta", 
                bg="#1976D2", 
                fg="white", 
                font=("Arial", 11, "bold"), 
                relief="flat", 
                command=self.dialogo_publicar_promocion,
                pady=8,
                cursor="hand2"
            ).pack(fill="x")

            # Cerrar Sesión
            tk.Button(
                self.root, 
                text="🚪 Cerrar Sesión", 
                bg="#757575", 
                fg="white", 
                font=("Arial", 10, "bold"),
                relief="flat", 
                command=self.cerrar_sesion_cb,
                pady=4,
                cursor="hand2"
            ).pack(pady=10)
            
            self.vecino_actual = None

        except Exception as e:
            messagebox.showerror("Error de Interfaz", f"Detalle al cargar Tienda: {str(e)}")

    def dialogo_mis_promociones(self):
            win_list = tk.Toplevel(self.root)
            win_list.title("Mis Ofertas Publicadas")
            win_list.geometry("580x450")
            win_list.resizable(False, False)
            win_list.grab_set()

            if hasattr(self.root, 'icon_img'):
                win_list.iconphoto(False, self.root.icon_img)

            frame_container = tk.Frame(win_list, bg="white")
            frame_container.pack(fill="both", expand=True, padx=10, pady=10)

            win_list.referencias_img = []

            def refrescar():
                for w in frame_container.winfo_children(): w.destroy()
                win_list.referencias_img.clear()
                promos = cargar_promociones()
                mis_promos = [(i, p) for i, p in enumerate(promos) if p.get("tienda_id") == self.id_usuario]

                if not mis_promos:
                    tk.Label(frame_container, text="No tienes promociones activas actualmente.", font=("Arial", 10, "italic"), bg="white").pack(pady=40)
                    return

                for idx, p in mis_promos:
                    card = tk.Frame(frame_container, bg="#FFF8E1", bd=1, relief="solid", padx=10, pady=8)
                    card.pack(fill="x", pady=4)

                    # Foto
                    ruta_foto = p.get("foto", "")
                    if ruta_foto and os.path.exists(ruta_foto):
                        try:
                            from PIL import Image, ImageTk
                            img = Image.open(ruta_foto).resize((60, 60), Image.Resampling.LANCZOS)
                            img_tk = ImageTk.PhotoImage(img)
                            win_list.referencias_img.append(img_tk)
                            tk.Label(card, image=img_tk, bg="#FFF8E1").pack(side="left", padx=(0, 10))
                        except Exception:
                            tk.Label(card, text="📷", font=("Arial", 12), bg="#FFE0B2", width=5, height=3).pack(side="left", padx=(0, 10))
                    else:
                        tk.Label(card, text="📷", font=("Arial", 12), bg="#FFE0B2", width=5, height=3).pack(side="left", padx=(0, 10))

                    txt_info = f"📌 {p['titulo']} ({p['puntos']} PTS / S/ {p['precio_soles']:.2f})\n📝 {p['descripcion']}"
                    tk.Label(card, text=txt_info, font=("Arial", 9, "bold"), bg="#FFF8E1", justify="left").pack(side="left", anchor="w")

                    def borrar(i=idx):
                        if messagebox.askyesno("Eliminar Promoción", "¿Deseas eliminar permanentemente esta oferta?"):
                            if eliminar_promocion(i, self.id_usuario, self.nombre_negocio):
                                messagebox.showinfo("Éxito", "La promoción ha sido eliminada.")
                                refrescar()

                    tk.Button(card, text="🗑️ Eliminar", bg="#C62828", fg="white", font=("Arial", 8, "bold"), relief="flat", command=borrar, cursor="hand2").pack(side="right", padx=5)

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
        else:
            self.vecino_actual = None
            self.lbl_nombre.config(text="Vecino no encontrado")
            self.lbl_saldo.config(text="Saldo Disponible: 0 PTS")
            self.btn_canjear.config(state="disabled")
            messagebox.showwarning("No Encontrado", "El DNI ingresado no pertenece a un vecino registrado.")

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
            usuarios[self.vecino_actual]["puntos"] -= pts_canje
            guardar_usuarios(usuarios)

            try:
                registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, pts_canje)
                registrar_accion_cliente(self.vecino_actual, "CANJE_TIENDA", -pts_canje, f"Compra/Canje en {self.nombre_negocio}")
            except Exception as e:
                print(f"Aviso log: {e}")

            messagebox.showinfo("Éxito", "El canje se ha registrado correctamente.")
            self.consultar_vecino()

    def dialogo_publicar_promocion(self):
        win_promo = tk.Toplevel(self.root)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("380x440")
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

        # 4. Imagen Opcional
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

        tk.Button(win_promo, text="📷 Subir Foto (Opcional)", bg="#1976D2", fg="white", command=seleccionar_imagen, relief="flat").pack(pady=(10, 2))
        lbl_foto_estado.pack()

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
                "foto": ruta_foto["path"]
            })
            guardar_promociones(promos)

            messagebox.showinfo("Éxito", "¡Promoción publicada correctamente!")
            win_promo.destroy()

        tk.Button(win_promo, text="💾 Publicar Oferta", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), command=guardar_promo, relief="flat", pady=6).pack(pady=15)