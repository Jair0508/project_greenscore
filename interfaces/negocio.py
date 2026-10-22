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