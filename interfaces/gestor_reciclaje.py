import tkinter as tk
from tkinter import ttk, messagebox
import os
from datos.gestor import (
    cargar_usuarios, guardar_usuarios, registrar_accion_dev, 
    cargar_log_tiendas, cargar_log_clientes, registrar_accion_cliente,
    cargar_promociones, cargar_mensajes_chat, guardar_mensaje_chat, marcar_chat_como_leido, 
    obtener_puntos_recolectados_por_tienda, eliminar_promocion_admin, cargar_entregas_reciclaje
)
from logica.modelos import Material

# Importación de matplotlib para renderizar el gráfico estadístico global
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

# ==========================================
# PALETA DE COLORES - GESTOR (CELESTE OSCURO / OCÉANO)
# ==========================================
COLOR_FONDO_APP        = "#F0F9FF"
COLOR_TEXTO_MAIN       = "#0F172A"
COLOR_HEADER_GESTOR    = "#0369A1"
COLOR_PRIMARIO_CELESTE = "#0284C7"
COLOR_SECUNDARIO_CELESTE = "#38BDF8"
COLOR_ACENTO_TURQUESA  = "#0D9488"
COLOR_BLANCO           = "#FFFFFF"
COLOR_GRIS_BOTON       = "#64748B"

class VentanaGestorReciclaje:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        usuarios = cargar_usuarios()
        self.datos_sesion = usuarios.get(id_usuario, {})

        self.root.title("EcoPuntos - Panel de GESTOR DE RECICLAJE")
        self.root.geometry("1020x740")
        self.root.resizable(False, False)

        self.aplicar_icono()

        ruta_fondo = os.path.join("img", "fondo_interfaz_admin.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error al cargar fondo gestor: {e}")

        self.aplicar_estilos_ttk()

        frame_header = tk.Frame(self.root, bg=COLOR_HEADER_GESTOR)
        frame_header.pack(fill="x")
        
        tk.Label(
            frame_header, 
            text=f"♻️ GESTOR DE RECICLAJE: {self.datos_sesion.get('nombre')} | Correo: {self.datos_sesion.get('correo', '-')}", 
            font=("Arial", 11, "bold"), 
            fg=COLOR_BLANCO, 
            bg=COLOR_HEADER_GESTOR, 
            pady=10
        ).pack(side="left", padx=15)

        frame_acciones = tk.LabelFrame(
            self.root, 
            text=" Operaciones de Gestión ", 
            font=("Arial", 10, "bold"), 
            padx=5, 
            pady=4, 
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_MAIN
        )
        frame_acciones.pack(fill="x", padx=15, pady=6)

        canvas_btn = tk.Canvas(frame_acciones, bg=COLOR_BLANCO, height=38, highlightthickness=0)
        scroll_btn = ttk.Scrollbar(frame_acciones, orient="horizontal", command=canvas_btn.xview)
        
        btn_box = tk.Frame(canvas_btn, bg=COLOR_BLANCO)
        btn_box.bind("<Configure>", lambda e: canvas_btn.configure(scrollregion=canvas_btn.bbox("all")))

        canvas_btn.create_window((0, 0), window=btn_box, anchor="nw")
        canvas_btn.configure(xscrollcommand=scroll_btn.set)

        canvas_btn.pack(fill="x", expand=True)
        scroll_btn.pack(fill="x")

        tk.Button(btn_box, text="➕ Crear Cuenta", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_crear_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="♻️ Sumar Puntos", bg=COLOR_ACENTO_TURQUESA, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_registrar_reciclaje, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔄 Toggle Reciclaje", bg="#10B981", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.toggle_reciclaje_negocio, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="➖ Restar Puntos", bg="#8B5CF6", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_reducir_puntos, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔑 Renovar Clave", bg="#D97706", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_cambiar_clave, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✏️ Editar Datos", bg="#0284C7", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_editar_datos, cursor="hand2").pack(side="left", padx=3, pady=2)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=(5, 2))

        tab_usuarios = ttk.Frame(notebook)
        tab_promos = ttk.Frame(notebook)
        tab_stats = ttk.Frame(notebook)
        tab_log_tiendas = ttk.Frame(notebook)
        tab_log_clientes = ttk.Frame(notebook)
        tab_soporte_general = ttk.Frame(notebook)

        notebook.add(tab_usuarios, text="👥 Cuentas Registradas")
        notebook.add(tab_promos, text="🛍️ Promociones Activas")
        notebook.add(tab_stats, text="📊 Estadísticas Globales")
        notebook.add(tab_log_tiendas, text="🏪 Actividad Tiendas")
        notebook.add(tab_log_clientes, text="👤 Actividad Clientes")
        notebook.add(tab_soporte_general, text="🔔 Soporte (Bandeja)")

        def crear_tabla_con_scroll(parent, columnas, configuracion_columnas):
            frame_tabla = ttk.Frame(parent)
            frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

            scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
            scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")

            tabla = ttk.Treeview(
                frame_tabla, 
                columns=columnas, 
                show="headings",
                yscrollcommand=scroll_y.set,
                xscrollcommand=scroll_x.set
            )

            scroll_y.config(command=tabla.yview)
            scroll_x.config(command=tabla.xview)

            scroll_y.pack(side="right", fill="y")
            scroll_x.pack(side="bottom", fill="x")
            tabla.pack(side="left", fill="both", expand=True)

            tabla.tag_configure("suspendido", foreground="#DC2626", background="#FEE2E2")
            tabla.tag_configure("activo", foreground="#047857")

            for col, text, width in configuracion_columnas:
                tabla.heading(col, text=text)
                anchor_val = "w" if col in ["fecha", "detalle", "comentario"] else "center" if col in ["puntos", "rol", "estado", "estrellas", "reciclaje"] else "w"
                tabla.column(col, width=width, minwidth=80, stretch=True, anchor=anchor_val)

            return tabla

        sub_notebook_usuarios = ttk.Notebook(tab_usuarios)
        sub_notebook_usuarios.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_usr_vecinos = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_negocios = ttk.Frame(sub_notebook_usuarios)

        sub_notebook_usuarios.add(self.tab_usr_vecinos, text="👤 Vecinos")
        sub_notebook_usuarios.add(self.tab_usr_negocios, text="🏪 Negocios")

        cols_usr_vecino = ("id", "nombre", "rol", "estado", "puntos", "rango", "justificacion")
        config_usr_vecino = [
            ("id", "DNI / ID", 110),
            ("nombre", "Nombre / Vecino", 180),
            ("rol", "Rol", 90),
            ("estado", "Estado / Indicador", 160),
            ("puntos", "Puntos", 80),
            ("rango", "Rango Ecológico", 170),
            ("justificacion", "Justificación Cliente", 200)
        ]

        cols_usr_negocio = ("id", "nombre", "rol", "estado", "reciclaje", "puntos", "comision", "justificacion")
        config_usr_negocio = [
            ("id", "ID Comercio", 100),
            ("nombre", "Nombre Comercio", 160),
            ("rol", "Rol", 80),
            ("estado", "Estado", 120),
            ("reciclaje", "Módulo Reciclaje", 140),
            ("puntos", "Pts Recolectados", 120),
            ("comision", "Comisión Generada", 150),
            ("justificacion", "Justificación", 160)
        ]

        self.tabla_usr_vecinos = crear_tabla_con_scroll(self.tab_usr_vecinos, cols_usr_vecino, config_usr_vecino)
        self.tabla_usr_negocios = crear_tabla_con_scroll(self.tab_usr_negocios, cols_usr_negocio, config_usr_negocio)

        tk.Button(
            tab_promos, 
            text="🖼️ Panel de promociones", 
            bg=COLOR_PRIMARIO_CELESTE, 
            fg=COLOR_BLANCO, 
            activeforeground=COLOR_BLANCO,
            font=("Arial", 9, "bold"), 
            relief="flat", 
            command=self.dialogo_ver_promociones_con_foto, 
            cursor="hand2",
            padx=10,
            pady=4
        ).pack(anchor="e", padx=5, pady=(5, 0))

        cols_pr = ("tienda", "titulo", "precio_soles", "puntos", "descripcion")
        config_pr = [
            ("tienda", "Comercio / Tienda", 180),
            ("titulo", "Título Oferta", 180),
            ("precio_soles", "Precio (S/)", 100),
            ("puntos", "Costo (PTS)", 100),
            ("descripcion", "Descripción", 280)
        ]
        self.tabla_promos = crear_tabla_con_scroll(tab_promos, cols_pr, config_pr)

        # PESTAÑA: ESTADÍSTICAS GLOBALES
        frame_stats_box = tk.Frame(tab_stats, bg=COLOR_BLANCO, padx=15, pady=15)
        frame_stats_box.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame_stats_box,
            text="📈 Resumen Global de Reciclaje (Todas las Puntos y Bodegas)",
            font=("Arial", 12, "bold"),
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_MAIN
        ).pack(anchor="w", pady=(0, 10))

        frame_grafico_container = tk.Frame(frame_stats_box, bg=COLOR_BLANCO, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO_CELESTE)
        frame_grafico_container.pack(fill="both", expand=True)

        def actualizar_panel_estadisticas_globales():
            for w in frame_grafico_container.winfo_children():
                w.destroy()

            todas_entregas = cargar_entregas_reciclaje()
            totales_material = {}
            total_general_kg = 0.0

            for ent in todas_entregas:
                mat = ent.get("material", "Desconocido")
                peso = float(ent.get("peso_kg", 0))
                totales_material[mat] = totales_material.get(mat, 0.0) + peso
                total_general_kg += peso

            if not todas_entregas or not totales_material:
                tk.Label(
                    frame_grafico_container,
                    text="No hay registros de reciclaje registrados en el sistema.",
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
                highlightbackground=COLOR_SECUNDARIO_CELESTE
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

                ax.set_title("Proporción por Material (%)", fontsize=10, fontweight="bold", color=COLOR_TEXTO_MAIN, pad=10)

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
                                autotexts[i].set_bbox(dict(
                                    boxstyle="round,pad=0.35", 
                                    fc=color_porcion, 
                                    ec="#FFFFFF", 
                                    lw=1.5
                                ))
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

            tk.Label(
                frame_resena_der, 
                text="📋 Resumen Operativo", 
                font=("Arial", 10, "bold"), 
                bg=COLOR_HEADER_GESTOR, 
                fg=COLOR_BLANCO, 
                pady=6
            ).pack(fill="x")

            canvas_resena = tk.Canvas(frame_resena_der, bg=COLOR_FONDO_APP, width=250, highlightthickness=0)
            scroll_resena = ttk.Scrollbar(frame_resena_der, orient="vertical", command=canvas_resena.yview)
            
            box_resena = tk.Frame(canvas_resena, bg=COLOR_FONDO_APP, padx=8, pady=8)
            box_resena.bind("<Configure>", lambda e: canvas_resena.configure(scrollregion=canvas_resena.bbox("all")))

            canvas_resena.create_window((0, 0), window=box_resena, anchor="nw")
            canvas_resena.configure(yscrollcommand=scroll_resena.set)

            canvas_resena.pack(side="left", fill="both", expand=True)
            scroll_resena.pack(side="right", fill="y")

            tk.Label(
                box_resena, 
                text=f"⚖️ Total Recolectado: {total_general_kg:.2f} kg", 
                font=("Arial", 9, "bold"), 
                fg=COLOR_PRIMARIO_CELESTE, 
                bg=COLOR_FONDO_APP,
                anchor="w"
            ).pack(fill="x", pady=(0, 4))

            tk.Label(
                box_resena, 
                text=f"📦 Operaciones Registradas: {len(todas_entregas)}", 
                font=("Arial", 8, "bold"), 
                fg=COLOR_TEXTO_MAIN, 
                bg=COLOR_FONDO_APP,
                anchor="w"
            ).pack(fill="x", pady=(0, 8))

            tk.Frame(box_resena, height=1, bg="#CBD5E1").pack(fill="x", pady=4)
            tk.Label(box_resena, text="Desglose por Material:", font=("Arial", 8, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(anchor="w", pady=2)

            totales_ordenados = sorted(totales_material.items(), key=lambda x: x[1], reverse=True)
            for mat, kg in totales_ordenados:
                porcentaje = (kg / total_general_kg) * 100 if total_general_kg > 0 else 0
                txt_item = f"• {mat}\n   └─ {kg:.2f} kg ({porcentaje:.1f}%)"
                tk.Label(
                    box_resena, 
                    text=txt_item, 
                    font=("Arial", 8), 
                    fg=COLOR_TEXTO_MAIN, 
                    bg=COLOR_FONDO_APP, 
                    justify="left",
                    anchor="w"
                ).pack(fill="x", pady=2)

        actualizar_panel_estadisticas_globales()

        cols_tnd = ("fecha", "tienda_id", "tienda_nombre", "dni_cliente", "puntos")
        config_tnd = [
            ("fecha", "Fecha / Hora", 200),
            ("tienda_id", "ID Tienda", 110),
            ("tienda_nombre", "Nombre Comercio", 180),
            ("dni_cliente", "DNI Cliente / Ref", 140),
            ("puntos", "Pts / Detalle", 160)
        ]
        self.tabla_tnd = crear_tabla_con_scroll(tab_log_tiendas, cols_tnd, config_tnd)

        sub_notebook_cli = ttk.Notebook(tab_log_clientes)
        sub_notebook_cli.pack(fill="both", expand=True, padx=5, pady=5)

        tab_cli_todos = ttk.Frame(sub_notebook_cli)
        tab_cli_abonos = ttk.Frame(sub_notebook_cli)
        tab_cli_canjes = ttk.Frame(sub_notebook_cli)
        tab_cli_entregas = ttk.Frame(sub_notebook_cli)
        tab_cli_resenas = ttk.Frame(sub_notebook_cli)

        sub_notebook_cli.add(tab_cli_todos, text="📋 Todos")
        sub_notebook_cli.add(tab_cli_abonos, text="♻️ Abonos / Reciclaje")
        sub_notebook_cli.add(tab_cli_canjes, text="🛍️ Canjes de Puntos")
        sub_notebook_cli.add(tab_cli_entregas, text="📦 Entregas Validadas")
        sub_notebook_cli.add(tab_cli_resenas, text="⭐ Reseñas y Estrellas")

        cols_cli = ("fecha", "dni_cliente", "tipo", "puntos", "detalle")
        config_cli = [
            ("fecha", "Fecha / Hora", 200),
            ("dni_cliente", "DNI Cliente", 130),
            ("tipo", "Tipo Operación", 150),
            ("puntos", "Puntos (+/-)", 110),
            ("detalle", "Detalle de Operación", 450)
        ]
        self.tabla_cli_todos = crear_tabla_con_scroll(tab_cli_todos, cols_cli, config_cli)
        self.tabla_cli_abonos = crear_tabla_con_scroll(tab_cli_abonos, cols_cli, config_cli)
        self.tabla_cli_canjes = crear_tabla_con_scroll(tab_cli_canjes, cols_cli, config_cli)
        self.tabla_cli_entregas = crear_tabla_con_scroll(tab_cli_entregas, cols_cli, config_cli)

        cols_resenas = ("fecha", "dni_cliente", "estrellas", "comentario")
        config_resenas = [
            ("fecha", "Fecha / Hora", 180),
            ("dni_cliente", "DNI Cliente", 130),
            ("estrellas", "⭐ Calificación", 180),
            ("comentario", "💬 Reseña / Comentario del Vecino", 480)
        ]
        self.tabla_cli_resenas = crear_tabla_con_scroll(tab_cli_resenas, cols_resenas, config_resenas)

        sub_notebook_soporte = ttk.Notebook(tab_soporte_general)
        sub_notebook_soporte.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_chat_vecinos = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_negocios = ttk.Frame(sub_notebook_soporte)

        sub_notebook_soporte.add(self.tab_chat_vecinos, text="👤 Vecinos")
        sub_notebook_soporte.add(self.tab_chat_negocios, text="🏪 Negocios")

        self.chats_ui = {}

        for rol_tipo, tab_widget in [("vecino", self.tab_chat_vecinos), ("negocio", self.tab_chat_negocios)]:
            frame_box = tk.Frame(tab_widget, bg=COLOR_BLANCO, padx=10, pady=10)
            frame_box.pack(fill="both", expand=True)

            frame_top = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_top.pack(fill="x", pady=(0, 5))

            tk.Label(frame_top, text="✉️ Seleccionar:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(side="left", padx=5)
            
            cb = ttk.Combobox(frame_top, font=("Arial", 10), width=38, state="readonly")
            cb.pack(side="left", padx=5)
            cb.bind("<<ComboboxSelected>>", lambda e, r=rol_tipo: self.cargar_chat_seleccionado(r))

            tk.Button(
                frame_top, text="🔄 Actualizar", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO, font=("Arial", 8, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.llenar_combo_chats_por_rol(r), cursor="hand2"
            ).pack(side="left", padx=5)

            frame_txt = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_txt.pack(fill="both", expand=True, pady=5)

            scroll_txt = ttk.Scrollbar(frame_txt, orient="vertical")
            scroll_txt.pack(side="right", fill="y")

            txt = tk.Text(frame_txt, state="disabled", font=("Arial", 10), bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, wrap="word", yscrollcommand=scroll_txt.set)
            txt.pack(side="left", fill="both", expand=True)
            scroll_txt.config(command=txt.yview)

            frame_input = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_input.pack(fill="x", pady=(5, 0))

            ent = tk.Entry(frame_input, font=("Arial", 10), bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE)
            ent.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
            ent.bind("<Return>", lambda e, r=rol_tipo: self.responder_chat_por_rol(r))

            tk.Button(
                frame_input, text="Responder ✉️", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, 
                activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", 
                command=lambda r=rol_tipo: self.responder_chat_por_rol(r), cursor="hand2"
            ).pack(side="right")

            self.chats_ui[rol_tipo] = {
                "cb": cb,
                "txt": txt,
                "ent": ent,
                "mapeo": {}
            }

        tk.Button(
            self.root, 
            text="🚪 Cerrar Sesión", 
            bg=COLOR_GRIS_BOTON, 
            fg=COLOR_BLANCO, 
            activeforeground=COLOR_BLANCO,
            font=("Arial", 10, "bold"), 
            relief="flat", 
            command=self.cerrar_sesion_cb, 
            cursor="hand2", 
            pady=4,
            padx=15
        ).pack(side="bottom", pady=8)

        self.actualizar_tablas()
        self.llenar_todos_los_combos()

    def aplicar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_FONDO_APP, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 10, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_BLANCO)], foreground=[("selected", COLOR_PRIMARIO_CELESTE)])
        
        style.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_TEXTO_MAIN, fieldbackground=COLOR_BLANCO, rowheight=25)
        style.configure("Treeview.Heading", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 9, "bold"))

    def obtener_rango_vecino(self, puntos):
        try:
            pts = int(float(puntos))
        except (ValueError, TypeError):
            pts = 0

        if pts > 300: return "👑 Leyenda Suprema"
        elif pts > 150: return "🌳 Guerrero Verde"
        elif pts > 50: return "🌿 Reciclador Activo"
        else: return "🌱 Eco-Novato"

    def llenar_todos_los_combos(self):
        for rol in ["vecino", "negocio"]:
            self.llenar_combo_chats_por_rol(rol)

    def llenar_combo_chats_por_rol(self, rol_tipo):
        mensajes = cargar_mensajes_chat()
        usuarios = cargar_usuarios()
        
        ui = self.chats_ui[rol_tipo]
        cb = ui["cb"]
        mapeo = ui["mapeo"]
        
        opciones = []
        mapeo.clear()

        for uid, datos in usuarios.items():
            if datos.get("rol") == rol_tipo:
                nombre_usuario = datos.get("nombre", "Usuario")
                tiene_pendientes = any(m.get("dni_cliente") == uid and not m.get("leido", True) for m in mensajes)
                icono_alerta = "🔔 [NUEVO] " if tiene_pendientes else "💬 "
                texto_item = f"{icono_alerta}{nombre_usuario} (ID: {uid})"
                opciones.append(texto_item)
                mapeo[texto_item] = uid

        cb['values'] = opciones
        if opciones:
            cb.current(0)
            self.cargar_chat_seleccionado(rol_tipo)
        else:
            cb.set("No hay usuarios registrados")
            ui["txt"].config(state="normal")
            ui["txt"].delete("1.0", tk.END)
            ui["txt"].insert(tk.END, "💬 No hay registros disponibles.\n")
            ui["txt"].config(state="disabled")

    def cargar_chat_seleccionado(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion: return
        
        dni = ui["mapeo"].get(seleccion)
        if not dni: return

        marcar_chat_como_leido(dni, "gestor")

        txt = ui["txt"]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == dni]

        if not msg_cliente:
            txt.insert(tk.END, "💬 No hay mensajes previos con este usuario. Escribe abajo para responder.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")
                leido = m.get("leido", True)

                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"
                txt.insert(tk.END, f"[{fecha}] {autor} ({rol}){check_leido}:\n{texto}\n\n")

        txt.see(tk.END)
        txt.config(state="disabled")

    def responder_chat_por_rol(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion: return

        dni = ui["mapeo"].get(seleccion)
        texto = ui["ent"].get().strip()
        if not texto: return

        guardar_mensaje_chat(
            dni_cliente=dni,
            autor_nombre=self.datos_sesion.get("nombre", "Gestor de Reciclaje"),
            rol_autor="gestor",
            mensaje=texto
        )

        ui["ent"].delete(0, tk.END)
        self.cargar_chat_seleccionado(rol_tipo)

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception: pass

    def pedir_texto_custom(self, titulo, mensaje):
        win = tk.Toplevel(self.root)
        win.config(bg=COLOR_FONDO_APP)
        win.title(titulo)
        win.geometry("380x180")
        win.resizable(False, False)
        win.grab_set()

        if hasattr(self.root, 'icon_img'): win.iconphoto(False, self.root.icon_img)

        container = tk.Frame(win, bg=COLOR_FONDO_APP, padx=15, pady=15)
        container.pack(fill="both", expand=True)

        lbl_msg = tk.Label(container, text=mensaje, font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP, wraplength=340, justify="center")
        lbl_msg.pack(pady=(0, 10))

        entry_var = tk.StringVar()
        entry = tk.Entry(container, textvariable=entry_var, font=("Arial", 10), width=35, bd=1, relief="solid")
        entry.pack(pady=5)
        entry.focus_set()

        resultado = {"texto": None}
        def confirmar():
            txt = entry_var.get().strip()
            if txt:
                resultado["texto"] = txt
                win.destroy()

        def cancelar(): win.destroy()

        win.bind("<Return>", lambda e: confirmar())
        win.bind("<Escape>", lambda e: cancelar())
        self.root.wait_window(win)
        return resultado["texto"]

    def toggle_reciclaje_negocio(self):
        """Activa o desactiva el módulo de recepción de reciclaje y estadísticas para una bodega."""
        uid = self.pedir_texto_custom("Toggle Reciclaje", "Ingrese ID/DNI del negocio:")
        if not uid:
            return

        usuarios = cargar_usuarios()
        if uid not in usuarios or usuarios[uid].get("rol") != "negocio":
            messagebox.showerror("Error", "El ID ingresado no pertenece a un negocio registrado.")
            return

        estado_actual = usuarios[uid].get("reciclaje_activo", True)
        nuevo_estado = not estado_actual
        usuarios[uid]["reciclaje_activo"] = nuevo_estado
        guardar_usuarios(usuarios)

        txt_estado = "HABILITADO" if nuevo_estado else "DESHABILITADO"
        registrar_accion_dev(
            self.id_usuario,
            self.datos_sesion.get("nombre"),
            "TOGGLE_RECICLAJE",
            f"Cambió recepción de reciclaje a '{txt_estado}' para negocio {uid}"
        )

        self.actualizar_tablas()
        messagebox.showinfo("Éxito", f"Se ha {txt_estado.lower()} el módulo de reciclaje para {usuarios[uid].get('nombre', 'el negocio')}.")

    def actualizar_tablas(self):
        for item in self.tabla_usr_vecinos.get_children(): self.tabla_usr_vecinos.delete(item)
        for item in self.tabla_usr_negocios.get_children(): self.tabla_usr_negocios.delete(item)

        usuarios = cargar_usuarios()
        for uid, datos in usuarios.items():
            suspendido = datos.get("suspendido", False)
            estado_txt = f"🔴 SUSPENDIDO ({datos.get('motivo_suspension', '')})" if suspendido else "🟢 ACTIVO"
            tag_fila = "suspendido" if suspendido else "activo"

            rol = datos.get("rol", "-")
            puntos_raw = datos.get("puntos", 0)
            puntos = int(float(puntos_raw)) if rol == "vecino" else "N/A"
            rango_txt = self.obtener_rango_vecino(puntos) if rol == "vecino" else "N/A (Personal)"
            justif_txt = datos.get("justificacion_cliente", "-") or "-"

            if rol == "vecino":
                tupla_datos = (uid, datos.get("nombre", "-"), rol.upper(), estado_txt, puntos, rango_txt, justif_txt)
                self.tabla_usr_vecinos.insert("", "end", values=tupla_datos, tags=(tag_fila,))
            elif rol == "negocio":
                pts_recolectados = obtener_puntos_recolectados_por_tienda(uid)
                comision_pts = round(pts_recolectados * 0.10, 1)
                comision_soles = round(comision_pts * 0.10, 2)
                
                rec_activo = datos.get("reciclaje_activo", True)
                txt_reciclaje = "🟢 HABILITADO" if rec_activo else "🔴 DESHABILITADO"

                tupla_negocio = (
                    uid, 
                    datos.get("nombre", "-"), 
                    rol.upper(), 
                    estado_txt, 
                    txt_reciclaje,
                    f"{pts_recolectados} PTS", 
                    f"{comision_pts} PTS (S/ {comision_soles:.2f})", 
                    justif_txt
                )
                self.tabla_usr_negocios.insert("", "end", values=tupla_negocio, tags=(tag_fila,))

        for item in self.tabla_promos.get_children(): self.tabla_promos.delete(item)
        for p in cargar_promociones():
            pts_oferta = int(float(p.get('puntos', 0)))
            self.tabla_promos.insert("", "end", values=(p.get("tienda_nombre", "Tienda"), p.get("titulo", "-"), f"S/ {p.get('precio_soles', 0):.2f}", f"{pts_oferta} PTS", p.get("descripcion", "-")))

        for item in self.tabla_tnd.get_children(): self.tabla_tnd.delete(item)
        for log in reversed(cargar_log_tiendas()):
            self.tabla_tnd.insert("", "end", values=(log.get("fecha"), log.get("tienda_id"), log.get("tienda_nombre"), log.get("dni_cliente"), log.get("puntos_descontados")))

        tablas_cli = [self.tabla_cli_todos, self.tabla_cli_abonos, self.tabla_cli_canjes, self.tabla_cli_entregas, self.tabla_cli_resenas]
        for t in tablas_cli:
            for item in t.get_children(): t.delete(item)

        for log in reversed(cargar_log_clientes()):
            fecha = log.get("fecha", "-"); dni = log.get("dni_cliente", "-"); tipo = log.get("tipo", "")
            puntos = int(float(log.get("puntos", 0)))
            detalle = log.get("detalle", "")
            valores = (fecha, dni, tipo, puntos, detalle)

            self.tabla_cli_todos.insert("", "end", values=valores)
            if tipo in ["ABONO_RECICLAJE", "SUMA_ADMIN"]: self.tabla_cli_abonos.insert("", "end", values=valores)
            elif tipo in ["CANJE_OFERTA", "CANJE_TIENDA", "REDUCCION_ADMIN"]: self.tabla_cli_canjes.insert("", "end", values=valores)
            elif tipo in ["ENTREGA_OFERTA"]: self.tabla_cli_entregas.insert("", "end", values=valores)
            elif tipo in ["RESEÑA_TIENDA"]: self.tabla_cli_resenas.insert("", "end", values=(fecha, dni, "⭐ Reseña", detalle))

    def dialogo_crear_cuenta(self):
        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Crear Cuenta (Vecino / Negocio)")
        win_modal.geometry("340x360")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'): win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text="Seleccione Tipo de Cuenta:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        cb_rol = ttk.Combobox(win_modal, values=["vecino", "negocio"], state="readonly")
        cb_rol.pack(pady=5); cb_rol.current(0)

        tk.Label(win_modal, text="DNI / Código de Cuenta:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_uid = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_uid.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Nombre / Razón Social:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_nom = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_nom.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Correo Electrónico:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_correo = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_correo.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Teléfono / Celular:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_tel = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_tel.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Contraseña Inicial:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_clave = tk.Entry(win_modal, show="*", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_clave.pack(pady=2, ipady=2)

        def guardar():
            uid = ent_uid.get().strip(); nom = ent_nom.get().strip(); rol = cb_rol.get()
            correo = ent_correo.get().strip(); tel = ent_tel.get().strip(); clave = ent_clave.get().strip()

            if not uid or not nom or not clave:
                messagebox.showerror("Error", "Complete los campos obligatorios.")
                return

            usuarios = cargar_usuarios()
            if uid in usuarios:
                messagebox.showerror("Error", "El ID/DNI ya existe.")
                return

            usuarios[uid] = {
                "rol": rol, "nombre": nom, "correo": correo or "-", "telefono": tel or "-", "clave": clave, "puntos": 0 if rol == "vecino" else "N/A",
                "suspendido": False, "motivo_suspension": "", "justificacion_cliente": "", "reciclaje_activo": True
            }
            guardar_usuarios(usuarios)
            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CREAR_CUENTA", f"Creó cuenta {uid} ({rol.upper()})")
            
            self.actualizar_tablas()
            self.llenar_todos_los_combos()
            win_modal.destroy()
            messagebox.showinfo("Éxito", f"Cuenta de tipo '{rol.upper()}' creada.")

        tk.Button(win_modal, text="Guardar Cuenta", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), command=guardar, relief="flat", cursor="hand2", pady=5).pack(pady=15)

    def dialogo_registrar_reciclaje(self):
        dni = self.pedir_texto_custom("Sumar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "DNI no corresponde a un vecino.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA.")
            return

        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Sumar Puntos por Reciclaje")
        win_modal.geometry("320x230")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'): win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text=f"Vecino: {usuarios[dni]['nombre']}", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        cb_mat = ttk.Combobox(win_modal, values=list(Material.TASAS.keys()), state="readonly"); cb_mat.pack(pady=5); cb_mat.current(0)
        tk.Label(win_modal, text="Peso en KG:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_kg = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_CELESTE); ent_kg.pack(pady=5, ipady=2)

        def procesar():
            raw_input_kg = ent_kg.get().strip()
            if not raw_input_kg.isdigit():
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)
                return

            try:
                peso = int(raw_input_kg)
                mat = cb_mat.get()
                puntos_calculados = Material.calcular_puntos(mat, float(peso))
                puntos = int(round(puntos_calculados))
                puntos_actuales_user = int(float(usuarios[dni].get("puntos", 0)))
                
                usuarios[dni]["puntos"] = puntos_actuales_user + puntos
                guardar_usuarios(usuarios)
                
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUMAR_PUNTOS", f"Abonó {puntos} pts a {dni} por {mat}")
                registrar_accion_cliente(dni, "ABONO_RECICLAJE", puntos, f"Reciclaje de {mat} ({peso} kg)")
                
                self.actualizar_tablas()
                win_modal.destroy()
                messagebox.showinfo("Éxito", f"Se sumaron {puntos} puntos.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)

        tk.Button(win_modal, text="Sumar Puntos", bg=COLOR_PRIMARIO_CELESTE, fg=COLOR_BLANCO, font=("Arial", 9, "bold"), command=procesar, relief="flat", cursor="hand2", pady=5).pack(pady=10)

    def dialogo_reducir_puntos(self):
        dni = self.pedir_texto_custom("Restar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "Vecino no encontrado.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[dni]['nombre']} está SUSPENDIDA.")
            return
            
        puntos_actuales_user = int(float(usuarios[dni].get("puntos", 0)))
        pts_str = self.pedir_texto_custom("Restar Puntos", f"Puntos actuales: {puntos_actuales_user}\nCantidad a restar:")
        
        if pts_str:
            if not pts_str.isdigit():
                messagebox.showerror("Error", "Solamente números enteros")
                return

            try:
                pts = int(pts_str)
                if pts > 0 and puntos_actuales_user >= pts:
                    usuarios[dni]["puntos"] = puntos_actuales_user - pts
                    guardar_usuarios(usuarios)
                    registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "RESTAR_PUNTOS", f"Restó {pts} pts a {dni}")
                    registrar_accion_cliente(dni, "REDUCCION_ADMIN", -pts, "Ajuste manual del gestor")
                    self.actualizar_tablas()
                    messagebox.showinfo("Éxito", f"Se restaron {pts} puntos.")
                else:
                    messagebox.showerror("Error", "Puntos insuficientes.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros")

    def dialogo_cambiar_clave(self):
        uid = self.pedir_texto_custom("Renovar Clave", "Ingrese DNI/ID del vecino o negocio:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid in usuarios and usuarios[uid]["rol"] in ["vecino", "negocio"]:
            nueva = self.pedir_texto_custom("Renovar Clave", f"Nueva contraseña para {usuarios[uid]['nombre']}:")
            if nueva:
                usuarios[uid]["clave"] = nueva
                guardar_usuarios(usuarios)
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CAMBIO_CLAVE", f"Modificó clave de {uid}")
                messagebox.showinfo("Éxito", "Contraseña renovada.")
        else:
            messagebox.showerror("Error", "Usuario no encontrado o no permitido.")

    def dialogo_editar_datos(self):
        uid = self.pedir_texto_custom("Editar Datos", "Ingrese DNI/ID:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid not in usuarios or usuarios[uid]["rol"] not in ["vecino", "negocio"]:
            messagebox.showerror("Error", "Usuario no encontrado o no permitido.")
            return

        if usuarios[uid].get("suspendido", False):
            messagebox.showwarning("Cuenta Suspendida", f"La cuenta de {usuarios[uid]['nombre']} se encuentra SUSPENDIDA.")
            return

        nuevo_nom = self.pedir_texto_custom("Editar", "Nuevo Nombre:")
        nuevo_correo = self.pedir_texto_custom("Editar", "Nuevo Correo:")
        nuevo_tel = self.pedir_texto_custom("Editar", "Nuevo Celular:")
        
        if nuevo_nom: usuarios[uid]["nombre"] = nuevo_nom
        if nuevo_correo: usuarios[uid]["correo"] = nuevo_correo
        if nuevo_tel: usuarios[uid]["telefono"] = nuevo_tel

        guardar_usuarios(usuarios)
        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "EDITAR_DATOS", f"Actualizó datos de {uid}")
        self.actualizar_tablas()
        messagebox.showinfo("Éxito", "Datos actualizados.")

    def dialogo_ver_promociones_con_foto(self):
        win_promos = tk.Toplevel(self.root)
        win_promos.config(bg=COLOR_BLANCO)
        win_promos.title("Panel de Promociones")
        win_promos.geometry("720x540")
        win_promos.resizable(False, False)
        win_promos.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promos.iconphoto(False, self.root.icon_img)

        canvas = tk.Canvas(win_promos, bg=COLOR_BLANCO, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(win_promos, orient="vertical", command=canvas.yview)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        nombres_archivos = ["fondo_ofertas_admin.png", "fondo_ofertas_admin.jpg"]
        ruta_encontrada = next((os.path.join("img", n) for n in nombres_archivos if os.path.exists(os.path.join("img", n))), None)

        if ruta_encontrada:
            try:
                from PIL import Image, ImageTk
                img_pil = Image.open(ruta_encontrada).convert("RGBA").resize((720, 540), Image.Resampling.LANCZOS)
                win_promos.bg_img = ImageTk.PhotoImage(img_pil)
                canvas.create_image(0, 0, image=win_promos.bg_img, anchor="nw")
            except Exception as e:
                print(f"Aviso imagen de fondo: {e}")

        frame_grid = tk.Frame(canvas, bg="")
        canvas.create_window((15, 15), window=frame_grid, anchor="nw")

        def _actualizar_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_grid.bind("<Configure>", _actualizar_scrollregion)
        canvas.configure(yscrollcommand=scrollbar.set)

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
                bg=COLOR_PRIMARIO_CELESTE, 
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

            promos = cargar_promociones()
            if not promos:
                tk.Label(
                    frame_grid, 
                    text="No hay promociones registradas actualmente.", 
                    font=("Arial", 11, "italic"), 
                    fg=COLOR_GRIS_BOTON,
                    bg=COLOR_BLANCO
                ).pack(pady=50, padx=20)
                return

            cols = 3
            LIMITE_CARACTERES = 28

            for idx, p in enumerate(promos):
                row = idx // cols
                col = idx % cols

                card = tk.Frame(
                    frame_grid, 
                    bg=COLOR_BLANCO, 
                    bd=1, 
                    relief="solid", 
                    highlightbackground=COLOR_SECUNDARIO_CELESTE, 
                    highlightthickness=1,
                    padx=8, 
                    pady=8,
                    width=210,
                    height=165
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                card.grid_propagate(False)

                pts_oferta = int(float(p.get('puntos', 0)))
                titulo_oferta = p.get('titulo', 'Oferta')
                desc_original = str(p.get('descripcion', '-'))

                txt_cabecera = (
                    f"🏪 {p.get('tienda_nombre')}\n(ID: {p.get('tienda_id')})\n\n"
                    f"📌 {titulo_oferta}\n"
                    f"💰 S/ {float(p.get('precio_soles', 0)):.2f} ➔ {pts_oferta} PTS\n\n"
                    f"📝 "
                )

                lbl_cabecera = tk.Label(
                    card, 
                    text=txt_cabecera, 
                    font=("Arial", 8, "bold"), 
                    fg=COLOR_TEXTO_MAIN, 
                    bg=COLOR_BLANCO, 
                    justify="left",
                    anchor="nw"
                )
                lbl_cabecera.pack(anchor="w", fill="x")

                es_larga = len(desc_original) > LIMITE_CARACTERES
                desc_mostrar = (desc_original[:LIMITE_CARACTERES].strip() + "...") if es_larga else desc_original

                frame_desc = tk.Frame(card, bg=COLOR_BLANCO)
                frame_desc.pack(anchor="w", fill="x")

                lbl_desc = tk.Label(
                    frame_desc, 
                    text=desc_mostrar, 
                    font=("Arial", 8), 
                    fg=COLOR_TEXTO_MAIN, 
                    bg=COLOR_BLANCO, 
                    justify="left", 
                    anchor="nw",
                    wraplength=180
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

                def eliminar_con_motivo(i=idx, tienda_id=p.get('tienda_id'), titulo=titulo_oferta):
                    motivo = self.pedir_texto_custom("Eliminar Oferta", f"Motivo de eliminación para '{titulo}':")
                    if not motivo:
                        messagebox.showwarning("Requerido", "Debe ingresar una justificación para eliminar la oferta.")
                        return

                    if messagebox.askyesno("Confirmar", f"¿Eliminar definitivamente la oferta '{titulo}'?"):
                        if eliminar_promocion_admin(i, tienda_id, motivo, self.datos_sesion.get("nombre", "Gestor")):
                            registrar_accion_dev(
                                self.id_usuario, 
                                self.datos_sesion.get("nombre"), 
                                "ELIMINAR_OFERTA", 
                                f"Eliminó oferta '{titulo}' de la tienda {tienda_id}. Motivo: {motivo}"
                            )
                            messagebox.showinfo("Éxito", "La oferta ha sido eliminada.")
                            self.actualizar_tablas()
                            refrescar_grid()

                btn_eliminar = tk.Button(
                    card, 
                    text="🗑️ Eliminar Oferta", 
                    bg="#DC2626", 
                    fg=COLOR_BLANCO, 
                    activeforeground=COLOR_BLANCO, 
                    font=("Arial", 8, "bold"), 
                    relief="flat", 
                    command=eliminar_con_motivo, 
                    cursor="hand2", 
                    pady=2
                )
                btn_eliminar.pack(fill="x", side="bottom")

        refrescar_grid()