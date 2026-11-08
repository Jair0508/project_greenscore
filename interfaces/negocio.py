import tkinter as tk
from tkinter import ttk, messagebox
import os
from logica.modelos import Material
from datos.gestor import (
    cargar_usuarios, 
    guardar_usuarios, 
    registrar_accion_tienda, 
    registrar_accion_cliente,
    cargar_promociones, 
    guardar_promociones,
    eliminar_promocion,
    cargar_log_tiendas,
    cargar_log_clientes,
    registrar_entrega_reciclaje,
    cargar_entregas_reciclaje
)

# Importamos matplotlib para generar gráficos estadísticos profesionales
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

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
            datos_tienda = usuarios.get(str(id_usuario), {})
            self.nombre_negocio = datos_tienda.get("nombre", "Comercio")
            reciclaje_permitido = datos_tienda.get("reciclaje_activo", True)

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
                text="📄 Términos de Bodega",
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

            # SOLO SI TIENE ACTIVADA LA OPCIÓN SE AÑADEN LAS PESTAÑAS DE RECICLAJE Y GRÁFICOS
            if reciclaje_permitido:
                tab_reciclaje = ttk.Frame(notebook_negocio)
                tab_stats = ttk.Frame(notebook_negocio)

                notebook_negocio.add(tab_reciclaje, text="♻️ Recibir Reciclaje")
                notebook_negocio.add(tab_stats, text="📊 Estadísticas y Gráficos")

                # PESTAÑA: RECIBIR RECICLAJE
                frame_rec_box = tk.Frame(tab_reciclaje, bg=COLOR_BLANCO, padx=15, pady=15)
                frame_rec_box.pack(fill="both", expand=True, padx=15, pady=15)

                frame_form_rec = tk.LabelFrame(
                    frame_rec_box,
                    text=" Registrar Pesaje de Material Reciclado ",
                    font=("Arial", 11, "bold"),
                    padx=15,
                    pady=10,
                    bg=COLOR_BLANCO,
                    fg=COLOR_TEXTO_MAIN
                )
                frame_form_rec.pack(fill="x", pady=(0, 15))

                f_dni = tk.Frame(frame_form_rec, bg=COLOR_BLANCO)
                f_dni.pack(fill="x", pady=5)
                tk.Label(f_dni, text="DNI del Vecino:", font=("Arial", 10), width=15, anchor="w", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN).pack(side="left")
                self.ent_dni_rec = tk.Entry(f_dni, font=("Arial", 11), width=15, bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
                self.ent_dni_rec.pack(side="left", padx=5, ipady=2)
                
                self.lbl_nombre_vecino_rec = tk.Label(f_dni, text="Vecino: No verificado", font=("Arial", 10, "bold"), bg=COLOR_BLANCO, fg=COLOR_PRIMARIO)
                self.lbl_nombre_vecino_rec.pack(side="left", padx=15)

                def verificar_vecino_reciclaje(event=None):
                    dni_val = self.ent_dni_rec.get().strip()
                    usrs = cargar_usuarios()
                    if dni_val in usrs and usrs[dni_val].get("rol") == "vecino":
                        nom = usrs[dni_val].get("nombre", "Vecino")
                        self.lbl_nombre_vecino_rec.config(text=f"Vecino: {nom}")
                    else:
                        self.lbl_nombre_vecino_rec.config(text="Vecino: No encontrado")

                self.ent_dni_rec.bind("<KeyRelease>", verificar_vecino_reciclaje)

                f_mat = tk.Frame(frame_form_rec, bg=COLOR_BLANCO)
                f_mat.pack(fill="x", pady=5)
                tk.Label(f_mat, text="Material:", font=("Arial", 10), width=15, anchor="w", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN).pack(side="left")
                
                self.cb_material = ttk.Combobox(
                    f_mat,
                    values=list(Material.TASAS.keys()),
                    state="readonly",
                    font=("Arial", 10),
                    width=25
                )
                self.cb_material.pack(side="left", padx=5)
                if Material.TASAS:
                    self.cb_material.set(list(Material.TASAS.keys())[0])

                f_peso = tk.Frame(frame_form_rec, bg=COLOR_BLANCO)
                f_peso.pack(fill="x", pady=5)
                tk.Label(f_peso, text="Peso (kg):", font=("Arial", 10), width=15, anchor="w", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN).pack(side="left")
                self.ent_peso = tk.Entry(f_peso, font=("Arial", 11), width=15, bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
                self.ent_peso.pack(side="left", padx=5, ipady=2)

                self.lbl_calculo_pts = tk.Label(f_peso, text="Puntos a abonar: 0 PTS", font=("Arial", 10, "bold"), bg=COLOR_BLANCO, fg=COLOR_ACENTO_CANJE)
                self.lbl_calculo_pts.pack(side="left", padx=15)

                def calcular_puntos_live(event=None):
                    try:
                        mat = self.cb_material.get()
                        peso_val = float(self.ent_peso.get().strip())
                        if peso_val > 0:
                            pts_calc = Material.calcular_puntos(mat, peso_val)
                            # Validar visualmente en vivo si excede el tope de 2000
                            dni_val = self.ent_dni_rec.get().strip()
                            usrs = cargar_usuarios()
                            if dni_val in usrs and usrs[dni_val].get("rol") == "vecino":
                                saldo_actual = float(usrs[dni_val].get("puntos", 0))
                                if saldo_actual + pts_calc > 2000:
                                    pts_calc = max(0.0, 2000.0 - saldo_actual)
                            self.lbl_calculo_pts.config(text=f"Puntos a abonar: {pts_calc} PTS")
                        else:
                            self.lbl_calculo_pts.config(text="Puntos a abonar: 0 PTS")
                    except ValueError:
                        self.lbl_calculo_pts.config(text="Puntos a abonar: 0 PTS")

                self.ent_peso.bind("<KeyRelease>", calcular_puntos_live)
                self.cb_material.bind("<<ComboboxSelected>>", calcular_puntos_live)

                def procesar_pesaje():
                    dni = self.ent_dni_rec.get().strip()
                    mat = self.cb_material.get()
                    peso_str = self.ent_peso.get().strip()

                    usrs = cargar_usuarios()
                    if dni not in usrs or usrs[dni].get("rol") != "vecino":
                        messagebox.showerror("Error", "Debe ingresar el DNI de un vecino registrado.")
                        return

                    try:
                        peso = float(peso_str)
                    except ValueError:
                        messagebox.showerror("Error", "Ingrese un valor numérico válido para el peso en kg.")
                        return

                    if peso <= 0:
                        messagebox.showerror("Error", "No se aceptan pesos de 0 o negativos.")
                        return
                    if peso > 50:
                        messagebox.showerror("Error", "El límite máximo por una sola entrega es de 50 kg.")
                        return

                    puntos_calculados = Material.calcular_puntos(mat, peso)
                    nombre_vecino = usrs[dni].get("nombre", "Vecino")
                    try:
                        saldo_actual = float(usrs[dni].get("puntos", 0))
                    except (ValueError, TypeError):
                        saldo_actual = 0.0

                    # BLINDAJE ESTRICTO DE TOPE DE 2000 PUNTOS (EVITA PUNTOS FANTASMAS)
                    nuevo_total_tentativo = saldo_actual + puntos_calculados
                    if nuevo_total_tentativo > 2000:
                        puntos_ganados = max(0.0, 2000.0 - saldo_actual)
                        messagebox.showwarning("Tope Máximo", f"El vecino alcanzaría más de 2,000 puntos. Se ajustará al tope máximo permitido (se abonarán solo {puntos_ganados} PTS).")
                        nuevo_saldo = 2000.0
                    else:
                        puntos_ganados = puntos_calculados
                        nuevo_saldo = nuevo_total_tentativo

                    if messagebox.askyesno("Confirmar Abono", f"¿Abonar {puntos_ganados} puntos a {nombre_vecino} por {peso} kg de {mat}?"):
                        usrs[dni]["puntos"] = nuevo_saldo
                        guardar_usuarios(usrs)

                        registrar_entrega_reciclaje(self.id_usuario, dni, mat, peso, puntos_ganados)

                        registrar_accion_cliente(
                            dni,
                            "RECICLAJE_RECIBIDO",
                            puntos_ganados,
                            f"Entrega de {peso}kg de {mat} en {self.nombre_negocio} (+{puntos_ganados} PTS)"
                        )

                        messagebox.showinfo("Éxito", f"¡Se han abonado {puntos_ganados} puntos correctamente al vecino!")
                        self.ent_dni_rec.delete(0, tk.END)
                        self.ent_peso.delete(0, tk.END)
                        self.lbl_nombre_vecino_rec.config(text="Vecino: No verificado")
                        self.lbl_calculo_pts.config(text="Puntos a abonar: 0 PTS")
                        actualizar_tabla_entregas()
                        actualizar_panel_estadisticas()

                tk.Button(
                    frame_form_rec,
                    text="💾 Confirmar y Abonar Puntos al Vecino",
                    bg=COLOR_PRIMARIO,
                    fg=COLOR_BLANCO,
                    font=("Arial", 10, "bold"),
                    relief="flat",
                    command=procesar_pesaje,
                    pady=6,
                    cursor="hand2"
                ).pack(anchor="e", pady=(10, 0))

                tk.Label(
                    frame_rec_box,
                    text="📊 Historial de Entregas Recibidas (Esta Bodega):",
                    font=("Arial", 11, "bold"),
                    bg=COLOR_BLANCO,
                    fg=COLOR_TEXTO_MAIN
                ).pack(anchor="w", pady=(10, 5))

                cols_ent = ("fecha", "dni", "material", "peso", "puntos")
                frame_t_ent = ttk.Frame(frame_rec_box)
                frame_t_ent.pack(fill="both", expand=True, pady=5)

                sy_ent = ttk.Scrollbar(frame_t_ent, orient="vertical")
                self.tabla_entregas = ttk.Treeview(frame_t_ent, columns=cols_ent, show="headings", yscrollcommand=sy_ent.set)
                sy_ent.config(command=self.tabla_entregas.yview)
                sy_ent.pack(side="right", fill="y")
                self.tabla_entregas.pack(side="left", fill="both", expand=True)

                config_cols_ent = [
                    ("fecha", "Fecha / Hora", 160),
                    ("dni", "DNI Vecino", 110),
                    ("material", "Material", 150),
                    ("peso", "Peso (kg)", 90),
                    ("puntos", "Puntos Abonados", 130)
                ]
                for col, txt, w in config_cols_ent:
                    self.tabla_entregas.heading(col, text=txt)
                    self.tabla_entregas.column(col, width=w, stretch=True)

                def actualizar_tabla_entregas():
                    for item in self.tabla_entregas.get_children():
                        self.tabla_entregas.delete(item)
                    
                    todas_entregas = cargar_entregas_reciclaje()
                    for ent in reversed(todas_entregas):
                        if str(ent.get("tienda_id")) == str(self.id_usuario):
                            self.tabla_entregas.insert(
                                "",
                                "end",
                                values=(
                                    ent.get("fecha", "-"),
                                    ent.get("dni_cliente", "-"),
                                    ent.get("material", "-"),
                                    f"{ent.get('peso_kg', 0)} kg",
                                    f"+{ent.get('puntos', 0)} PTS"
                                )
                            )

                actualizar_tabla_entregas()

                # PESTAÑA: ESTADÍSTICAS Y GRÁFICOS
                frame_stats_box = tk.Frame(tab_stats, bg=COLOR_BLANCO, padx=15, pady=15)
                frame_stats_box.pack(fill="both", expand=True, padx=15, pady=15)

                tk.Label(
                    frame_stats_box,
                    text="📈 Resumen de Kilogramos Reciclados por Material (Esta Bodega)",
                    font=("Arial", 12, "bold"),
                    bg=COLOR_BLANCO,
                    fg=COLOR_TEXTO_MAIN
                ).pack(anchor="w", pady=(0, 10))

                frame_grafico_container = tk.Frame(frame_stats_box, bg=COLOR_BLANCO, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO)
                frame_grafico_container.pack(fill="both", expand=True)

                def actualizar_panel_estadisticas():
                    for w in frame_grafico_container.winfo_children():
                        w.destroy()

                    todas_entregas = cargar_entregas_reciclaje()
                    mis_entregas = [e for e in todas_entregas if str(e.get("tienda_id")) == str(self.id_usuario)]

                    totales_material = {}
                    total_general_kg = 0.0
                    for ent in mis_entregas:
                        mat = ent.get("material", "Desconocido")
                        peso = float(ent.get("peso_kg", 0))
                        totales_material[mat] = totales_material.get(mat, 0.0) + peso
                        total_general_kg += peso

                    if not mis_entregas or not totales_material:
                        tk.Label(
                            frame_grafico_container,
                            text="No hay registros de reciclaje suficientes para mostrar estadísticas.",
                            font=("Arial", 11, "italic"),
                            fg="#757575",
                            bg=COLOR_BLANCO
                        ).pack(pady=100)
                        return

                    frame_grafico_izq = tk.Frame(frame_grafico_container, bg=COLOR_BLANCO)
                    frame_grafico_izq.pack(side="left", fill="both", expand=True, padx=(5, 0))

                    frame_resena_der = tk.Frame(
                        frame_grafico_container, 
                        bg=COLOR_FONDO_APP, 
                        bd=1, 
                        relief="solid", 
                        highlightbackground=COLOR_SECUNDARIO
                    )
                    frame_resena_der.pack(side="right", fill="both", expand=False, padx=10, pady=10)

                    if MATPLOTLIB_DISPONIBLE:
                        import numpy as np
                        fig, ax = plt.subplots(figsize=(5.2, 3.8), dpi=100)
                        fig.patch.set_facecolor(COLOR_BLANCO)
                        ax.set_facecolor(COLOR_BLANCO)

                        materiales = list(totales_material.keys())
                        kilos = list(totales_material.values())

                        colores_vivos = [
                            "#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653", 
                            "#E63946", "#457B9D", "#1D3557", "#9b5de5", "#f15bb5", "#00bbf9"
                        ]
                        colores_usados = [colores_vivos[i % len(colores_vivos)] for i in range(len(materiales))]

                        wedges, texts, autotexts = ax.pie(
                            kilos, 
                            labels=None, 
                            autopct='%1.1f%%', 
                            startangle=140, 
                            colors=colores_usados,
                            pctdistance=0.72,
                            textprops=dict(color="white", weight="bold", fontsize=8)
                        )

                        centre_circle = plt.Circle((0, 0), 0.45, fc=COLOR_BLANCO, zorder=2)
                        ax.add_patch(centre_circle)

                        ax.set_title("Proporción Recolectada por Material (%)", fontsize=10, fontweight="bold", color=COLOR_TEXTO_MAIN, pad=10)

                        ax.legend(
                            wedges, 
                            materiales, 
                            title="Materiales", 
                            loc="center left", 
                            bbox_to_anchor=(-0.78, 0.5),
                            fontsize=7.5,
                            title_fontsize=8.5,
                            frameon=True,
                            facecolor=COLOR_FONDO_APP,
                            edgecolor="#CBD5E1"
                        )

                        plt.subplots_adjust(left=0.42, right=0.98, top=0.88, bottom=0.08)

                        canvas_grafico = FigureCanvasTkAgg(fig, master=frame_grafico_izq)
                        canvas_grafico.draw()
                        canvas_widget = canvas_grafico.get_tk_widget()
                        canvas_widget.pack(fill="both", expand=True)

                        def on_hover(event):
                            if event.inaxes == ax:
                                contiene_alguno = False
                                for i, wedge in enumerate(wedges):
                                    contiene, _ = wedge.contains(event)
                                    if contiene:
                                        contiene_alguno = True
                                        theta = (wedge.theta1 + wedge.theta2) / 2.0
                                        theta_rad = np.deg2rad(theta)
                                        wedge.set_center((0.35 * np.cos(theta_rad), 0.35 * np.sin(theta_rad)))
                                        wedge.set_zorder(10)
                                        
                                        color_porcion = colores_usados[i]
                                        autotexts[i].set_fontsize(11)
                                        autotexts[i].set_color("#FFFFFF")
                                        autotexts[i].set_zorder(20)
                                        autotexts[i].set_bbox(dict(boxstyle="round,pad=0.35", fc=color_porcion, ec="#FFFFFF", lw=1.5))
                                    else:
                                        wedge.set_center((0, 0))
                                        wedge.set_zorder(1)
                                        autotexts[i].set_fontsize(8)
                                        autotexts[i].set_zorder(3)
                                        autotexts[i].set_bbox(None)

                                if contiene_alguno:
                                    canvas_grafico.draw_idle()
                                else:
                                    for i, wedge in enumerate(wedges):
                                        wedge.set_center((0, 0))
                                        wedge.set_zorder(1)
                                        autotexts[i].set_fontsize(8)
                                        autotexts[i].set_zorder(3)
                                        autotexts[i].set_bbox(None)
                                    canvas_grafico.draw_idle()

                        canvas_grafico.mpl_connect("motion_notify_event", on_hover)

                    tk.Label(frame_resena_der, text="📋 Resumen Bodega", font=("Arial", 10, "bold"), bg=COLOR_PRIMARIO, fg=COLOR_BLANCO, pady=6).pack(fill="x")
                    
                    box_resena = tk.Frame(frame_resena_der, bg=COLOR_FONDO_APP, padx=8, pady=8)
                    box_resena.pack(fill="both", expand=True)

                    tk.Label(box_resena, text=f"⚖️ Total: {total_general_kg:.2f} kg", font=("Arial", 9, "bold"), fg=COLOR_PRIMARIO, bg=COLOR_FONDO_APP, anchor="w").pack(fill="x", pady=(0, 4))
                    tk.Label(box_resena, text=f"📦 Operaciones: {len(mis_entregas)}", font=("Arial", 8, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP, anchor="w").pack(fill="x", pady=(0, 8))
                    
                    tk.Frame(box_resena, height=1, bg="#CBD5E1").pack(fill="x", pady=4)
                    
                    for mat, kg in sorted(totales_material.items(), key=lambda x: x[1], reverse=True):
                        porcentaje = (kg / total_general_kg) * 100 if total_general_kg > 0 else 0
                        tk.Label(box_resena, text=f"• {mat}\n   └─ {kg:.2f} kg ({porcentaje:.1f}%)", font=("Arial", 8), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP, justify="left", anchor="w").pack(fill="x", pady=2)

                actualizar_panel_estadisticas()

            notebook_negocio.add(tab_historial, text="📜 Historial y Gestión de Ofertas")
            notebook_negocio.add(tab_resenas, text="⭐ Mis Reseñas y Calificación")

            # PESTAÑA 1: TERMINAL Y PUBLICACIÓN
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
                text=" 2. Estado de Cuenta del Vecino ", 
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

            # PESTAÑA: HISTORIAL Y GESTIÓN DE OFERTAS
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
                command=self.dialogo_mis_ofertas,
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

            # PESTAÑA: RESEÑAS Y CALIFICACIONES DEL NEGOCIO
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
            spin_cant.delete(0, tk.END)
            spin_cant.insert(0, "1")
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

            usuarios[self.vecino_actual]["puntos"] -= puntos_totales
            guardar_usuarios(usuarios)

            # Actualizar stock o eliminar si llega a 0
            promos_actuales = cargar_promociones()
            operaciones_ordenadas = sorted(operaciones_stock, key=lambda x: x[0], reverse=True)
            
            for idx_p, cant_descontar in operaciones_ordenadas:
                if idx_p < len(promos_actuales):
                    stock_prev = int(promos_actuales[idx_p].get("stock", 0))
                    nuevo_stock = stock_prev - cant_descontar
                    if nuevo_stock <= 0:
                        promos_actuales.pop(idx_p)
                    else:
                        promos_actuales[idx_p]["stock"] = nuevo_stock
            guardar_promociones(promos_actuales)

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

            messagebox.showinfo("Éxito", f"¡Canje completado!\nSe han descontado {puntos_totales} PTS y actualizado el inventario.")
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
        win_promo = tk.Toplevel(self.root)
        win_promo.config(bg=COLOR_FONDO_APP)
        win_promo.title("Publicar Oferta / Promoción")
        win_promo.geometry("420x500")
        win_promo.resizable(False, False)
        win_promo.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promo.iconphoto(False, self.root.icon_img)

        tk.Label(win_promo, text="Título de Promoción (Máx 25 caract.):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(15, 2))
        ent_titulo = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_titulo.pack(fill="x", padx=20)

        tk.Label(win_promo, text="Categoría de la Oferta:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        combo_categoria = ttk.Combobox(
            win_promo, 
            state="readonly", 
            values=CATEGORIAS_BODEGA, 
            font=("Arial", 10)
        )
        combo_categoria.pack(fill="x", padx=20)
        combo_categoria.set("Abarrotes y Despensa")

        tk.Label(win_promo, text="Cantidad Inicial en Stock (Unidades):", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", padx=20, pady=(10, 2))
        ent_stock = tk.Entry(win_promo, font=("Arial", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO)
        ent_stock.pack(fill="x", padx=20)
        ent_stock.insert(0, "10")

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
        for item in self.tabla_resenas_negocio.get_children():
            self.tabla_resenas_negocio.delete(item)

        logs = cargar_log_clientes()
        mis_resenas = []
        suma_calificaciones = 0
        nombre_lower = self.nombre_negocio.strip().lower()

        for log in reversed(logs):
            tipo = log.get("tipo", "")
            detalle = log.get("detalle", "").strip()
            
            if "RESEÑA" in tipo or "Reseña para" in detalle:
                detalle_lower = detalle.lower()
                if nombre_lower in detalle_lower:
                    fecha = log.get("fecha", "-")
                    dni = log.get("dni_cliente", "-")
                    
                    estrellas_str = "⭐ (Sin calificación)"
                    comentario_str = detalle
                    valor_numerico = 5

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

    def dialogo_mis_ofertas(self):
        """Muestra el panel de promociones con fondo floral estático y tarjetas rectangulares."""
        win_promos = tk.Toplevel(self.root)
        win_promos.title("Panel de Promociones")
        win_promos.geometry("720x540")
        win_promos.resizable(False, False)
        win_promos.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promos.iconphoto(False, self.root.icon_img)

        # 1. Cargar la imagen de fondo estática
        nombres_archivos = ["fondo_ofertas_admin.png", "fondo_ofertas_admin.jpg"]
        ruta_encontrada = next((os.path.join("img", n) for n in nombres_archivos if os.path.exists(os.path.join("img", n))), None)

        if ruta_encontrada:
            try:
                from PIL import Image, ImageTk
                img_pil = Image.open(ruta_encontrada).convert("RGBA").resize((720, 540), Image.Resampling.LANCZOS)
                win_promos.bg_img = ImageTk.PhotoImage(img_pil)
                lbl_bg = tk.Label(win_promos, image=win_promos.bg_img, bd=0)
                lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Aviso imagen de fondo: {e}")

        # 2. Canvas y Scrollbar
        canvas = tk.Canvas(win_promos, bg=COLOR_BLANCO, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(win_promos, orient="vertical", command=canvas.yview)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dibujar la imagen sobre el Canvas para congelar las coordenadas al desplazar scroll
        bg_canvas_id = None
        if hasattr(win_promos, 'bg_img'):
            bg_canvas_id = canvas.create_image(0, 0, image=win_promos.bg_img, anchor="nw")

        # 3. Contenedor principal para las ofertas
        frame_grid = tk.Frame(canvas, bg=COLOR_BLANCO)
        window_id = canvas.create_window((15, 15), window=frame_grid, anchor="nw")

        def _actualizar_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_grid.bind("<Configure>", _actualizar_scrollregion)

        # Reposiciona dinámicamente el fondo para que no se mueva con el scroll
        def _al_hacer_scroll(*args):
            scrollbar.set(*args)
            if bg_canvas_id:
                y_pos = canvas.canvasy(0)
                canvas.coords(bg_canvas_id, 0, y_pos)

        canvas.configure(yscrollcommand=_al_hacer_scroll)

        def mostrar_descripcion_completa(titulo, descripcion):
            win_desc = tk.Toplevel(win_promos)
            win_desc.config(bg=COLOR_FONDO_APP)
            win_desc.title(f"Detalle: {titulo}")
            win_desc.geometry("380x220")
            win_desc.resizable(False, False)
            win_desc.grab_set()

            if hasattr(self.root, 'icon_img'):
                win_desc.iconphoto(False, self.root.icon_img)

            tk.Label(
                win_desc, 
                text=f"📌 {titulo}", 
                font=("Arial", 11, "bold"), 
                fg=COLOR_TEXTO_MAIN, 
                bg=COLOR_FONDO_APP
            ).pack(anchor="w", padx=15, pady=(15, 5))

            frame_txt = tk.Frame(win_desc, bg=COLOR_BLANCO, bd=1, relief="solid")
            frame_txt.pack(fill="both", expand=True, padx=15, pady=5)

            txt_box = tk.Text(frame_txt, font=("Arial", 9), wrap="word", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat")
            txt_box.pack(fill="both", expand=True, padx=5, pady=5)
            txt_box.insert("1.0", descripcion)
            txt_box.config(state="disabled")

            tk.Button(
                win_desc, 
                text="Cerrar", 
                bg=COLOR_PRIMARIO, 
                fg=COLOR_BLANCO, 
                font=("Arial", 9, "bold"), 
                command=win_desc.destroy, 
                relief="flat", 
                padx=15, 
                pady=3,
                cursor="hand2"
            ).pack(pady=10)

        def refrescar_grid():
            for w in frame_grid.winfo_children():
                w.destroy()

            todas_promos = cargar_promociones()
            promos_propias = [
                (idx, p) for idx, p in enumerate(todas_promos) 
                if str(p.get("tienda_id")) == str(self.id_usuario) and int(p.get("stock", 0)) > 0
            ]

            if not promos_propias:
                tk.Label(
                    frame_grid, 
                    text="No tienes ofertas con stock disponible en este momento.", 
                    font=("Arial", 11, "italic"), 
                    fg="#64748B", 
                    bg=COLOR_BLANCO
                ).pack(pady=50, padx=20)
                return

            cols = 3
            LIMITE_CARACTERES = 35

            for i, (idx_global, p) in enumerate(promos_propias):
                row, col = i // cols, i % cols
                
                # Rectángulo Vertical compacto (180x220px)
                card = tk.Frame(
                    frame_grid, 
                    bg=COLOR_BLANCO, 
                    bd=1, 
                    relief="solid", 
                    highlightbackground=COLOR_SECUNDARIO, 
                    highlightthickness=1, 
                    padx=10, 
                    pady=10, 
                    width=180, 
                    height=220
                )
                card.grid(row=row, column=col, padx=8, pady=10, sticky="nw")
                card.grid_propagate(False)
                card.pack_propagate(False)

                pts_oferta = int(float(p.get('puntos', 0)))
                titulo_oferta = p.get('titulo', 'Oferta')
                categoria_oferta = p.get('categoria', 'General')
                stock_oferta = p.get('stock', 0)
                precio_soles = float(p.get('precio_soles', 0))
                desc_original = str(p.get('descripcion', '-'))

                # Nombre del Producto destacado
                lbl_titulo = tk.Label(
                    card, 
                    text=f"📌 {titulo_oferta}", 
                    font=("Arial", 10, "bold"), 
                    fg=COLOR_TEXTO_MAIN, 
                    bg=COLOR_BLANCO, 
                    justify="left", 
                    anchor="nw",
                    wraplength=155
                )
                lbl_titulo.pack(anchor="w", fill="x", pady=(0, 2))

                # Información del negocio y stock
                txt_detalles = (
                    f"🏪 {p.get('tienda_nombre', 'Mi Tienda')} | Stock: {stock_oferta}\n"
                    f"📂 {categoria_oferta}\n"
                    f"💰 S/ {precio_soles:.2f} ➔ {pts_oferta} PTS"
                )
                lbl_detalles = tk.Label(
                    card, 
                    text=txt_detalles, 
                    font=("Arial", 8, "bold"), 
                    fg="#0284C7", 
                    bg=COLOR_BLANCO, 
                    justify="left", 
                    anchor="nw"
                )
                lbl_detalles.pack(anchor="w", fill="x", pady=(0, 4))

                # Separador horizontal sutil
                tk.Frame(card, height=1, bg="#E2E8F0").pack(fill="x", pady=(0, 4))

                # Descripción del producto
                es_larga = len(desc_original) > LIMITE_CARACTERES
                desc_mostrar = (desc_original[:LIMITE_CARACTERES].strip() + "...") if es_larga else desc_original

                frame_desc = tk.Frame(card, bg=COLOR_BLANCO, height=42, width=160)
                frame_desc.pack(anchor="w", fill="x")
                frame_desc.pack_propagate(False)

                lbl_desc = tk.Label(
                    frame_desc, 
                    text=f"📝 {desc_mostrar}", 
                    font=("Arial", 8), 
                    fg="#475569", 
                    bg=COLOR_BLANCO, 
                    justify="left", 
                    anchor="nw",
                    wraplength=150
                )
                lbl_desc.pack(side="left", anchor="nw")

                if es_larga:
                    btn_ver_mas = tk.Button(
                        frame_desc, 
                        text="ver más", 
                        font=("Arial", 7, "bold", "underline"), 
                        fg="#0284C7", 
                        bg=COLOR_BLANCO, 
                        bd=0, 
                        activebackground=COLOR_BLANCO, 
                        activeforeground="#0369A1",
                        cursor="hand2",
                        command=lambda t=titulo_oferta, d=desc_original: mostrar_descripcion_completa(t, d)
                    )
                    btn_ver_mas.pack(side="left", anchor="nw", padx=(2, 0))

                def eliminar_propia(idx_a_borrar=idx_global, titulo=titulo_oferta):
                    if messagebox.askyesno("Confirmar", f"¿Deseas eliminar tu oferta '{titulo}'?"):
                        promos = cargar_promociones()
                        if 0 <= idx_a_borrar < len(promos):
                            promos.pop(idx_a_borrar)
                            guardar_promociones(promos)
                            messagebox.showinfo("Éxito", "La oferta ha sido eliminada.")
                            refrescar_grid()

                btn_eliminar = tk.Button(
                    card, 
                    text="🗑️ Eliminar Oferta", 
                    bg="#DC2626", 
                    fg=COLOR_BLANCO, 
                    font=("Arial", 8, "bold"), 
                    relief="flat", 
                    command=eliminar_propia, 
                    cursor="hand2", 
                    pady=2
                )
                btn_eliminar.pack(fill="x", side="bottom")

        
        refrescar_grid()