import tkinter as tk
from tkinter import ttk, messagebox
import os
from datos.gestor import cargar_usuarios, cargar_log_clientes, cargar_mensajes_chat, guardar_mensaje_chat

COLOR_FONDO_VECINO = "#E8F5E9"

class VentanaVecino:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        self.root.config(bg=COLOR_FONDO_VECINO)
        self.root.title("EcoPuntos - Mi Cuenta Vecinal")
        self.root.geometry("950x680")
        self.root.resizable(False, False)

        self.aplicar_icono()

        # Cargar Fondo
        ruta_fondo = os.path.join("img", "fondo_vecino.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Aviso fondo vecino: {e}")

        usuarios = cargar_usuarios()
        self.datos = usuarios.get(id_usuario, {})

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

        # Balance Principal
        frame_card = tk.Frame(self.root, bg="white", bd=1, relief="solid", padx=20, pady=10)
        frame_card.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_card, text="Saldo Disponible:", font=("Arial", 10, "bold"), bg="white", fg="#555555").pack(side="left")
        self.lbl_puntos = tk.Label(frame_card, text=f"{self.datos.get('puntos', 0)} PTS", font=("Arial", 22, "bold"), fg="#2E7D32", bg="white")
        self.lbl_puntos.pack(side="left", padx=15)

        tk.Button(frame_card, text="🔄 Actualizar", bg="#1976D2", fg="white", font=("Arial", 9, "bold"), relief="flat", command=self.actualizar_todo, cursor="hand2").pack(side="right")

        # Control de Pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=5)

        tab_reciclaje = ttk.Frame(notebook)
        tab_movimientos = ttk.Frame(notebook)
        tab_chat = ttk.Frame(notebook)

        notebook.add(tab_reciclaje, text="♻️ Historial de Reciclaje (Detallado)")
        notebook.add(tab_movimientos, text="📊 Movimientos de Puntos (+ / -)")
        notebook.add(tab_chat, text="💬 Soporte / Chat con Devs y Admin")

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

        # 1. TABLA DETALLADA DE RECICLAJE
        cols_rec = ("fecha", "material", "peso", "puntos")
        config_rec = [
            ("fecha", "Fecha / Hora", 160),
            ("material", "Material Reciclado", 280),
            ("peso", "Peso Entregado (kg)", 140),
            ("puntos", "Puntos Obt.", 120)
        ]
        self.tabla_reciclaje = crear_tabla_scroll(tab_reciclaje, cols_rec, config_rec)

        # 2. TABLA DE MOVIMIENTOS
        cols_mov = ("fecha", "tipo", "puntos", "detalle")
        config_mov = [
            ("fecha", "Fecha / Hora", 160),
            ("tipo", "Tipo Operación", 150),
            ("puntos", "Puntos (+ / -)", 120),
            ("detalle", "Detalle / Concepto", 300)
        ]
        self.tabla_movimientos = crear_tabla_scroll(tab_movimientos, cols_mov, config_mov)

        # 3. CANAL DE CHAT CON DEVS Y ADMIN
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

        self.actualizar_todo()

        # Botón Cerrar Sesión
        tk.Button(self.root, text="🚪 Cerrar Sesión", bg="#757575", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.cerrar_sesion_cb, cursor="hand2", pady=4).pack(pady=8)

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception:
            pass

    def actualizar_todo(self):
        # Actualizar Saldo
        usuarios = cargar_usuarios()
        self.datos = usuarios.get(self.id_usuario, {})
        self.lbl_puntos.config(text=f"{self.datos.get('puntos', 0)} PTS")

        # Limpiar Tablas
        for item in self.tabla_reciclaje.get_children(): self.tabla_reciclaje.delete(item)
        for item in self.tabla_movimientos.get_children(): self.tabla_movimientos.delete(item)

        historial = cargar_log_clientes()
        for reg in reversed(historial):
            if reg.get("dni_cliente") == self.id_usuario:
                tipo = reg.get("tipo", "")
                puntos = reg.get("puntos", 0)
                fecha = reg.get("fecha", "-")
                detalle = reg.get("detalle", "")

                # Insertar en movimientos generales
                self.tabla_movimientos.insert("", "end", values=(fecha, tipo, puntos, detalle))

                # Parsear e insertar en historial de reciclaje si corresponde
                if tipo == "ABONO_RECICLAJE" and "Reciclaje de" in detalle:
                    try:
                        # Extraer material y peso desde detalle: "Reciclaje de Material (X.X kg)"
                        info = detalle.replace("Reciclaje de ", "").replace(" kg)", "")
                        partes = info.split(" (")
                        material = partes[0]
                        peso = partes[1] if len(partes) > 1 else "-"
                    except Exception:
                        material, peso = detalle, "-"
                    
                    self.tabla_reciclaje.insert("", "end", values=(fecha, material, peso, puntos))

        # Cargar Chat
        self.cargar_chat()

    def cargar_chat(self):
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

                etiqueta = f"[{fecha}] {autor} ({rol}):\n"
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