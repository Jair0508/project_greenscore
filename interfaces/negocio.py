import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from datos.gestor import cargar_usuarios, guardar_usuarios, registrar_accion_tienda, registrar_accion_cliente

COLOR_FONDO_TIENDA = "#FFF3E0"

class VentanaNegocio:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        self.root.config(bg=COLOR_FONDO_TIENDA)
        self.root.title("EcoPuntos - Terminal de Cobro Negocios")
        self.root.geometry("450x450")

        self.aplicar_icono()

        usuarios = cargar_usuarios()
        self.nombre_negocio = usuarios.get(id_usuario, {}).get("nombre", "Comercio")

        # Header
        frame_top = tk.Frame(root, bg="#E65100")
        frame_top.pack(fill="x")
        tk.Label(frame_top, text=f"🏪 {self.nombre_negocio}", font=("Arial", 14, "bold"), fg="white", bg="#E65100", py=10).pack()

        # Búsqueda
        frame_busca = tk.LabelFrame(root, text="1. Consultar Vecino", font=("Arial", 10, "bold"), padx=10, pady=10, bg=COLOR_FONDO_TIENDA)
        frame_busca.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_busca, text="DNI del Vecino:", bg=COLOR_FONDO_TIENDA).pack(side="left", padx=5)
        self.ent_dni = tk.Entry(frame_busca, font=("Arial", 11))
        self.ent_dni.pack(side="left", padx=5)

        tk.Button(frame_busca, text="🔍 Buscar", bg="#1976D2", fg="white", relief="flat", command=self.consultar_vecino).pack(side="left", padx=5)

        # Detalle
        self.frame_info = tk.LabelFrame(root, text="2. Detalle de Cuenta", font=("Arial", 10, "bold"), padx=10, pady=10, bg=COLOR_FONDO_TIENDA)
        self.frame_info.pack(fill="x", padx=20, pady=5)

        self.lbl_nombre = tk.Label(self.frame_info, text="Vecino: Ninguno seleccionado", font=("Arial", 10), bg=COLOR_FONDO_TIENDA)
        self.lbl_nombre.pack(anchor="w")

        self.lbl_saldo = tk.Label(self.frame_info, text="Saldo Disponible: 0 PTS", font=("Arial", 14, "bold"), fg="#2E7D32", bg=COLOR_FONDO_TIENDA)
        self.lbl_saldo.pack(anchor="w", pady=5)

        self.btn_canjear = tk.Button(root, text="💳 Procesar Descuento / Canje", bg="#E65100", fg="white", font=("Arial", 11, "bold"), state="disabled", relief="flat", command=self.abrir_cuadro_canje)
        self.btn_canjear.pack(fill="x", padx=20, pady=15)

        tk.Button(root, text="🚪 Cerrar Sesión", relief="flat", command=self.cerrar_sesion_cb).pack(pady=5)
        self.vecino_actual = None

    def aplicar_icono(self):
        ruta_ico = os.path.join("datos", "logo.ico")
        ruta_png = os.path.join("datos", "logo.png")
        try:
            if os.path.exists(ruta_ico): self.root.iconbitmap(ruta_ico)
            elif os.path.exists(ruta_png): self.root.iconphoto(False, tk.PhotoImage(file=ruta_png))
        except Exception: pass

    def consultar_vecino(self):
        dni = self.ent_dni.get().strip()
        usuarios = cargar_usuarios()

        if dni in usuarios and usuarios[dni]["rol"] == "vecino":
            self.vecino_actual = dni
            self.lbl_nombre.config(text=f"Vecino: {usuarios[dni]['nombre']} (DNI: {dni})")
            self.lbl_saldo.config(text=f"Saldo Disponible: {usuarios[dni]['puntos']} PTS")
            self.btn_canjear.config(state="normal")
        else:
            self.vecino_actual = None
            self.lbl_nombre.config(text="Vecino no encontrado")
            self.lbl_saldo.config(text="Saldo Disponible: 0 PTS")
            self.btn_canjear.config(state="disabled")
            messagebox.showwarning("No Encontrado", "El DNI ingresado no pertenece a un vecino.")

    def abrir_cuadro_canje(self):
        if not self.vecino_actual: return
        usuarios = cargar_usuarios()
        saldo_actual = usuarios[self.vecino_actual]["puntos"]

        pts_canje = simpledialog.askinteger(
            "Confirmar Canje", 
            f"Vecino: {usuarios[self.vecino_actual]['nombre']}\nSaldo actual: {saldo_actual} PTS\n\n¿Cuántos puntos desea descontar?",
            parent=self.root, minvalue=1, maxvalue=saldo_actual
        )

        if pts_canje and messagebox.askyesno("Confirmar", f"¿Descontar {pts_canje} puntos?"):
            usuarios[self.vecino_actual]["puntos"] -= pts_canje
            guardar_usuarios(usuarios)

            # REGISTRO DUAL DE AUDITORÍA (En Log de Tienda y en Log del Cliente)
            registrar_accion_tienda(self.id_usuario, self.nombre_negocio, self.vecino_actual, pts_canje)
            registrar_accion_cliente(self.vecino_actual, "CANJE_TIENDA", -pts_canje, f"Compra/Canje en {self.nombre_negocio}")

            messagebox.showinfo("Éxito", "El canje se ha registrado correctamente.")
            self.consultar_vecino()

    #Añadimos el formulario de promociones
    def dialogo_publicar_promocion(self):
        win_promo = tk.Toplevel(self.root)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("380x420")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        # 1. Título (Máx 25 caracteres)
        tk.Label(win_promo, text="Título de Promoción (Máx 25 caract.):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10))
        ent_titulo.pack(fill="x", padx=20)

        # 2. Precio en Soles + Conversión a Puntos
        tk.Label(win_promo, text="Precio Normal en Soles (S/):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_precio = tk.Entry(win_promo, font=("Arial", 10))
        ent_precio.pack(fill="x", padx=20)

        lbl_pts_equiv = tk.Label(win_promo, text="Equivalente: 0.0 PTS", font=("Arial", 10, "bold"), fg="#2E7D32")
        lbl_pts_equiv.pack(anchor="w", padx=20, pady=4)

        # Cálculo dinámico de puntos
        def calcular_pts_event(event=None):
            try:
                monto_soles = float(ent_precio.get().strip())
                pts = round(monto_soles / 0.10, 1) # 1 PTS = S/ 0.10
                lbl_pts_equiv.config(text=f"Equivalente: {pts} PTS")
            except ValueError:
                lbl_pts_equiv.config(text="Equivalente: 0.0 PTS")

        ent_precio.bind("<KeyRelease>", calcular_pts_event)

        # 3. Descripción (Máx 25 caracteres)
        tk.Label(win_promo, text="Descripción Corta (Máx 25 caract.):", font=("Arial", 9, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        ent_desc = tk.Entry(win_promo, font=("Arial", 10))
        ent_desc.pack(fill="x", padx=20)

        # 4. Imagen (Opcional)
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

        # Guardar Promoción con Validaciones
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

            # Cargar y guardar en JSON
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