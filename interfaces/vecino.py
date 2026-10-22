import tkinter as tk
from tkinter import ttk
import os
from datos.gestor import cargar_usuarios, cargar_log_clientes

COLOR_FONDO_VECINO = "#E8F5E9"

class VentanaVecino:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        self.root.config(bg=COLOR_FONDO_VECINO)
        self.root.title("EcoPuntos - Mi Cuenta Vecinal")
        self.root.geometry("620x520")

        self.aplicar_icono()

        usuarios = cargar_usuarios()
        datos = usuarios.get(id_usuario, {})

        # Header
        frame_top = tk.Frame(root, bg="#2E7D32")
        frame_top.pack(fill="x")
        tk.Label(frame_top, text=f"👤 Hola, {datos.get('nombre', 'Vecino')}", font=("Arial", 13, "bold"), fg="white", bg="#2E7D32", py=8).pack()

        # Tarjeta Saldo
        frame_card = tk.LabelFrame(root, text="Tarjeta de Puntos Ecológicos", font=("Arial", 10, "bold"), padx=15, pady=10, bg=COLOR_FONDO_VECINO)
        frame_card.pack(fill="x", padx=15, pady=10)

        self.lbl_puntos = tk.Label(frame_card, text=f"{datos.get('puntos', 0)} PTS", font=("Arial", 28, "bold"), fg="#2E7D32", bg=COLOR_FONDO_VECINO)
        self.lbl_puntos.pack(side="left", padx=10)

        btn_refresh = tk.Button(frame_card, text="🔄 Actualizar", bg="#1976D2", fg="white", relief="flat", command=self.actualizar_todo)
        btn_refresh.pack(side="right", padx=10)

        # Historial
        frame_hist = tk.LabelFrame(root, text="Mi Historial de Movimientos", font=("Arial", 10, "bold"), padx=10, pady=10, bg=COLOR_FONDO_VECINO)
        frame_hist.pack(fill="both", expand=True, padx=15, pady=5)

        columnas = ("fecha", "tipo", "puntos", "detalle")
        self.tabla = ttk.Treeview(frame_hist, columns=columnas, show="headings")
        self.tabla.heading("fecha", text="Fecha / Hora")
        self.tabla.heading("tipo", text="Operación")
        self.tabla.heading("puntos", text="Puntos (+/-)")
        self.tabla.heading("detalle", text="Detalle")

        self.tabla.column("fecha", width=140)
        self.tabla.column("tipo", width=110)
        self.tabla.column("puntos", width=80)
        self.tabla.column("detalle", width=200)

        self.tabla.pack(fill="both", expand=True)

        self.actualizar_todo()

        tk.Button(root, text="🚪 Cerrar Sesión", relief="flat", command=self.cerrar_sesion_cb).pack(pady=10)

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception as e:
            print(f"Error al cargar ícono: {e}")

    def actualizar_todo(self):
        usuarios = cargar_usuarios()
        pts = usuarios.get(self.id_usuario, {}).get("puntos", 0)
        self.lbl_puntos.config(text=f"{pts} PTS")

        for item in self.tabla.get_children(): self.tabla.delete(item)

        historial = cargar_log_clientes()
        for reg in reversed(historial):
            if reg.get("dni_cliente") == self.id_usuario:
                self.tabla.insert("", "end", values=(reg.get("fecha"), reg.get("tipo"), reg.get("puntos"), reg.get("detalle")))


    #Catálogo de tarjetas de promoción
    def cargar_catalogo_promociones(self, frame_contenedor):
        from datos.gestor import cargar_promociones
        promos = cargar_promociones()

        if not promos:
            tk.Label(frame_contenedor, text="No hay promociones disponibles en este momento.", font=("Arial", 10, "italic"), bg="white").pack(pady=20)
            return

        for promo in promos:
            card = tk.Frame(frame_contenedor, bg="#FFF8E1", bd=1, relief="solid", padx=10, pady=10)
            card.pack(fill="x", pady=5, padx=5)

            tk.Label(card, text=f"🏪 {promo['tienda_nombre']}", font=("Arial", 8, "bold"), fg="#E65100", bg="#FFF8E1").pack(anchor="w")
            tk.Label(card, text=promo["titulo"], font=("Arial", 11, "bold"), bg="#FFF8E1").pack(anchor="w")
            tk.Label(card, text=promo["descripcion"], font=("Arial", 9), fg="#424242", bg="#FFF8E1").pack(anchor="w")
            
            # Muestra costo en S/ y en PTS
            tk.Label(
                card, 
                text=f"Precio: S/ {promo['precio_soles']:.2f}  ➔  {promo['puntos']} PTS", 
                font=("Arial", 10, "bold"), 
                fg="#2E7D32", 
                bg="#FFF8E1"
            ).pack(anchor="w", pady=(4, 0))