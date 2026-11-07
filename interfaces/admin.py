import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import (
    cargar_usuarios, guardar_usuarios, registrar_accion_dev, 
    cargar_log_devs, cargar_log_tiendas, cargar_log_clientes, registrar_accion_cliente,
    cargar_promociones, guardar_promociones, cargar_mensajes_chat, guardar_mensaje_chat, marcar_chat_como_leido, 
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
# PALETA DE COLORES - TONOS AZULES
# ==========================================
COLOR_FONDO_APP      = "#F0F4F8"  # Azul Hielo Muy Suave (Fondo General)
COLOR_TEXTO_MAIN     = "#0F2537"  # Azul Marino Oscuro Profundo (Reemplazo de negro)
COLOR_AZUL_HEADER    = "#1A365D"  # Azul Noche / Ejecutivo (Header Principal)
COLOR_PRIMARIO_AZUL  = "#2563EB"  # Azul Cobalto Vivo (Botones / Acciones Clave)
COLOR_SECUNDARIO_AZUL= "#3B82F6"  # Azul Real / Bordes Activos
COLOR_ACENTO_CIAN    = "#0891B2"  # Azul Cian / Resaltados
COLOR_BLANCO         = "#FFFFFF"  # Blanco Puro para tarjetas e inputs
COLOR_ROJO_ALERTA    = "#DC2626"  # Rojo para suspensiones y eliminaciones
COLOR_GRIS_BOTON     = "#64748B"  # Gris Pizarra para cerrar sesión / cancelar

class VentanaAdmin:
    def __init__(self, root, id_usuario, cerrar_sesion_cb):
        self.root = root
        self.id_usuario = id_usuario
        self.cerrar_sesion_cb = cerrar_sesion_cb
        
        usuarios = cargar_usuarios()
        self.datos_sesion = usuarios.get(id_usuario, {})
        self.es_admin_supremo = (self.datos_sesion.get("rol") == "admin")

        titulo_rol = "ADMINISTRADOR" if self.es_admin_supremo else "GESTOR DE RECICLAJE"
        self.root.title(f"EcoPuntos - Panel de {titulo_rol}")
        self.root.geometry("1020x740")
        self.root.resizable(False, False)

        self.aplicar_icono()

        # 1. IMAGEN DE FONDO
        ruta_fondo = os.path.join("img", "fondo_interfaz_admin.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error al cargar imagen de fondo admin: {e}")

        self.aplicar_estilos_ttk()

        # 2. HEADER AZUL
        color_header = COLOR_AZUL_HEADER if self.es_admin_supremo else "#1E3A8A"
        frame_header = tk.Frame(self.root, bg=color_header)
        frame_header.pack(fill="x")
        
        tk.Label(
            frame_header, 
            text=f"👑 {titulo_rol}: {self.datos_sesion.get('nombre')} | Correo: {self.datos_sesion.get('correo', '-')}", 
            font=("Arial", 11, "bold"), 
            fg=COLOR_BLANCO, 
            bg=color_header, 
            pady=10
        ).pack(side="left", padx=15)

        # 3. BOTONES DE ACCIÓN DE GESTIÓN
        frame_acciones = tk.LabelFrame(
            self.root, 
            text=" Acciones de Gestión ", 
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

        # Botones de Acción en Tonos Azules y Alertas
        tk.Button(btn_box, text="➕ Crear Cuenta", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_crear_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="❌ Eliminar Cuenta", bg=COLOR_ROJO_ALERTA, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_eliminar_cuenta, cursor="hand2").pack(side="left", padx=3, pady=2)
        
        self.btn_suspender = tk.Button(btn_box, text="🛑 Suspender Cuenta", bg="#B91C1C", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_suspender_cuenta, cursor="hand2")
        self.btn_suspender.pack(side="left", padx=3, pady=2)

        tk.Button(btn_box, text="✅ Levantar Suspensión", bg="#059669", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_levantar_suspension, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="♻️ Sumar Puntos", bg=COLOR_ACENTO_CIAN, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_registrar_reciclaje, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="➖ Restar Puntos", bg="#9333EA", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_reducir_puntos, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="🔑 Renovar Clave", bg="#D97706", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_cambiar_clave, cursor="hand2").pack(side="left", padx=3, pady=2)
        tk.Button(btn_box, text="✏️ Editar Datos", bg="#0284C7", fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), relief="flat", command=self.dialogo_editar_datos, cursor="hand2").pack(side="left", padx=3, pady=2)

        tk.Button(
            btn_box, 
            text="🔄 Toggle Reciclaje", 
            bg="#10B981", 
            fg=COLOR_BLANCO, 
            activeforeground=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), 
            relief="flat", 
            command=self.toggle_reciclaje_negocio, 
            cursor="hand2"
        ).pack(side="left", padx=3, pady=2)
        
        # 4. CONTROL DE PESTAÑAS PRINCIPALES CON NAVEGACIÓN Y SCROLLBAR
        frame_nav = tk.Frame(self.root, bg=COLOR_FONDO_APP)
        frame_nav.pack(fill="x", padx=15, pady=(5, 2))

        canvas_tabs = tk.Canvas(frame_nav, bg=COLOR_FONDO_APP, height=38, highlightthickness=0)
        scroll_tabs = ttk.Scrollbar(frame_nav, orient="horizontal", command=canvas_tabs.xview)
        
        box_tabs = tk.Frame(canvas_tabs, bg=COLOR_FONDO_APP)
        box_tabs.bind("<Configure>", lambda e: canvas_tabs.configure(scrollregion=canvas_tabs.bbox("all")))

        canvas_tabs.create_window((0, 0), window=box_tabs, anchor="nw")
        canvas_tabs.configure(xscrollcommand=scroll_tabs.set)

        canvas_tabs.pack(fill="x", expand=True)
        scroll_tabs.pack(fill="x", pady=(2, 0))

        frame_vistas = tk.Frame(self.root, bg=COLOR_FONDO_APP)
        frame_vistas.pack(fill="both", expand=True, padx=15, pady=5)

        tab_usuarios = ttk.Frame(frame_vistas)
        tab_promos = ttk.Frame(frame_vistas)
        tab_stats = ttk.Frame(frame_vistas)
        tab_log_tiendas = ttk.Frame(frame_vistas)
        tab_log_clientes = ttk.Frame(frame_vistas)
        tab_soporte_general = ttk.Frame(frame_vistas)

        vistas = {
            "👥 Cuentas y Suspensiones": tab_usuarios,
            "🛍️ Promociones Activas": tab_promos,
            "📊 Estadísticas Globales": tab_stats,
            "🏪 Actividad Tiendas": tab_log_tiendas,
            "👤 Actividad Clientes": tab_log_clientes,
            "🔔 Soporte (Bandeja)": tab_soporte_general
        }

        if self.es_admin_supremo:
            self.tab_log_devs = ttk.Frame(frame_vistas)
            vistas["🕵️ Actividad Gestores / Admins"] = self.tab_log_devs

        botones_tabs = {}

        def cambiar_vista(nombre_tab):
            for nom, frame in vistas.items():
                if nom == nombre_tab:
                    frame.pack(fill="both", expand=True)
                    botones_tabs[nom].config(bg=COLOR_BLANCO, fg=COLOR_PRIMARIO_AZUL, relief="solid", bd=1)
                else:
                    frame.pack_forget()
                    botones_tabs[nom].config(bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", bd=0)

        for nombre in vistas.keys():
            btn = tk.Button(
                box_tabs, 
                text=nombre, 
                font=("Arial", 9, "bold"), 
                bg=COLOR_FONDO_APP, 
                fg=COLOR_TEXTO_MAIN, 
                relief="flat", 
                padx=12, 
                pady=5, 
                cursor="hand2",
                command=lambda n=nombre: cambiar_vista(n)
            )
            btn.pack(side="left", padx=3)
            botones_tabs[nombre] = btn

        cambiar_vista("👥 Cuentas y Suspensiones")

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

            tabla.tag_configure("suspendido", foreground=COLOR_ROJO_ALERTA, background="#FEE2E2")
            tabla.tag_configure("activo", foreground="#047857")

            for col, text, width in configuracion_columnas:
                tabla.heading(col, text=text)
                anchor_val = "w" if col in ["fecha", "detalle", "comentario"] else "center" if col in ["puntos", "rol", "estado", "estrellas"] else "w"
                tabla.column(col, width=width, minwidth=80, stretch=True, anchor=anchor_val)

            return tabla

        # 5. SUB-PESTAÑAS DE CUENTAS
        sub_notebook_usuarios = ttk.Notebook(tab_usuarios)
        sub_notebook_usuarios.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_usr_vecinos = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_negocios = ttk.Frame(sub_notebook_usuarios)
        self.tab_usr_devs = ttk.Frame(sub_notebook_usuarios)

        sub_notebook_usuarios.add(self.tab_usr_vecinos, text="👤 Vecinos")
        sub_notebook_usuarios.add(self.tab_usr_negocios, text="🏪 Negocios")
        sub_notebook_usuarios.add(self.tab_usr_devs, text="♻️ Gestores de Reciclaje / Admins")

        # Columnas y configuración para Vecinos y Gestores/Admins
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

        # Columnas y configuración para Negocios (Recolectados, Comisión 10%, Total)
        cols_usr_negocio = ("id", "nombre", "rol", "estado", "reciclaje", "pts_recolectados", "comision", "total_pts", "justificacion")
        config_usr_negocio = [
            ("id", "ID Comercio", 90),
            ("nombre", "Nombre Comercio", 150),
            ("rol", "Rol", 70),
            ("estado", "Estado", 100),
            ("reciclaje", "Módulo Reciclaje", 130),
            ("pts_recolectados", "Pts Recolectados", 140),
            ("comision", "Comisión (10%)", 150),
            ("total_pts", "Total Pts", 130),
            ("justificacion", "Justificación", 120)
        ]

        # Creación de tablas
        self.tabla_usr_vecinos = crear_tabla_con_scroll(self.tab_usr_vecinos, cols_usr_vecino, config_usr_vecino)
        self.tabla_usr_negocios = crear_tabla_con_scroll(self.tab_usr_negocios, cols_usr_negocio, config_usr_negocio)
        self.tabla_usr_devs = crear_tabla_con_scroll(self.tab_usr_devs, cols_usr_vecino, config_usr_vecino)

        
        # PROMOCIONES ACTIVAS
        tk.Button(
            tab_promos, 
            text="🖼️ Panel de promociones", 
            bg=COLOR_PRIMARIO_AZUL, 
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

        # PESTAÑA: ESTADÍSTICAS GLOBALES CON GRÁFICO DE DONA Y RESEÑA
        frame_stats_box = tk.Frame(tab_stats, bg=COLOR_BLANCO, padx=15, pady=15)
        frame_stats_box.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            frame_stats_box,
            text="📈 Resumen Global de Reciclaje (Puntos de recepción y Bodegas)",
            font=("Arial", 12, "bold"),
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO_MAIN
        ).pack(anchor="w", pady=(0, 10))

        frame_grafico_container = tk.Frame(frame_stats_box, bg=COLOR_BLANCO, bd=1, relief="solid", highlightbackground=COLOR_SECUNDARIO_AZUL)
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

            # CONTENEDOR 2 COLUMNAS
            frame_grafico_izq = tk.Frame(frame_grafico_container, bg=COLOR_BLANCO)
            frame_grafico_izq.pack(side="left", fill="both", expand=True, padx=(5, 0))

            frame_resena_der = tk.Frame(
                frame_grafico_container, 
                bg=COLOR_FONDO_APP, 
                bd=1, 
                relief="solid", 
                highlightbackground=COLOR_SECUNDARIO_AZUL if hasattr(self, 'es_admin_supremo') else "#52B788"
            )
            frame_resena_der.pack(side="right", fill="both", expand=False, padx=10, pady=10)

            # --- PARTE 1: DONA CON LEYENDA A LA IZQUIERDA Y Z-ORDER ELEVADO ---
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

                # Anillo interior para la dona
                centre_circle = plt.Circle((0, 0), 0.45, fc=COLOR_BLANCO, zorder=2)
                ax.add_patch(centre_circle)

                ax.set_title("Proporción por Material (%)", fontsize=10, fontweight="bold", color=COLOR_TEXTO_MAIN, pad=10)

                # LEYENDA A LA IZQUIERDA FUERA DEL GRÁFICO
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

                # Ajuste de márgenes para la leyenda izquierda
                plt.subplots_adjust(left=0.42, right=0.98, top=0.88, bottom=0.08)

                canvas_grafico = FigureCanvasTkAgg(fig, master=frame_grafico_izq)
                canvas_grafico.draw()
                canvas_widget = canvas_grafico.get_tk_widget()
                canvas_widget.pack(fill="both", expand=True)

                # HOVER: EXPANSIÓN, ZORDER ELEVADO Y RECTÁNGULO DE FONDO QUE CUBRE A LOS DEMÁS NÚMEROS
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
                                
                                # Eleva la capa zorder del texto y su recuadro por encima de todos los elementos
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

            # --- PARTE 2: RESEÑA DERECHA ---
            lbl_header_color = COLOR_AZUL_HEADER if hasattr(self, 'es_admin_supremo') else COLOR_PRIMARIO_AZUL
            tk.Label(
                frame_resena_der, 
                text="📋 Resumen Operativo", 
                font=("Arial", 10, "bold"), 
                bg=lbl_header_color, 
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

            p_color = COLOR_PRIMARIO_AZUL if hasattr(self, 'es_admin_supremo') else COLOR_PRIMARIO_AZUL
            tk.Label(
                box_resena, 
                text=f"⚖️ Total Recolectado: {total_general_kg:.2f} kg", 
                font=("Arial", 9, "bold"), 
                fg=p_color, 
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

        # LOG TIENDAS
        cols_tnd = ("fecha", "tienda_id", "tienda_nombre", "dni_cliente", "puntos")
        config_tnd = [
            ("fecha", "Fecha / Hora", 200),
            ("tienda_id", "ID Tienda", 110),
            ("tienda_nombre", "Nombre Comercio", 180),
            ("dni_cliente", "DNI Cliente / Ref", 140),
            ("puntos", "Pts / Detalle", 160)
        ]
        self.tabla_tnd = crear_tabla_con_scroll(tab_log_tiendas, cols_tnd, config_tnd)

        # SUB-PESTAÑAS EN ACTIVIDAD CLIENTES
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

        if self.es_admin_supremo:
            cols_dev = ("fecha", "autor_id", "autor_nombre", "accion", "objetivo")
            config_dev = [
                ("fecha", "Fecha / Hora", 200),
                ("autor_id", "ID Gestor/Admin", 120),
                ("autor_nombre", "Nombre Autor", 180),
                ("accion", "Acción Ejecutada", 160),
                ("objetivo", "Usuario / Cuenta Afectada", 250)
            ]
            self.tabla_dev = crear_tabla_con_scroll(self.tab_log_devs, cols_dev, config_dev)

        # 6. SUB-PESTAÑAS DE SOPORTE
        sub_notebook_soporte = ttk.Notebook(tab_soporte_general)
        sub_notebook_soporte.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_chat_vecinos = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_negocios = ttk.Frame(sub_notebook_soporte)
        self.tab_chat_devs = ttk.Frame(sub_notebook_soporte)

        sub_notebook_soporte.add(self.tab_chat_vecinos, text="👤 Vecinos")
        sub_notebook_soporte.add(self.tab_chat_negocios, text="🏪 Negocios")
        sub_notebook_soporte.add(self.tab_chat_devs, text="♻️ Gestores de Reciclaje")

        self.chats_ui = {}

        for rol_tipo, tab_widget in [("vecino", self.tab_chat_vecinos), ("negocio", self.tab_chat_negocios), ("gestor de reciclaje", self.tab_chat_devs)]:
            frame_box = tk.Frame(tab_widget, bg=COLOR_BLANCO, padx=10, pady=10)
            frame_box.pack(fill="both", expand=True)

            frame_top = tk.Frame(frame_box, bg=COLOR_BLANCO)
            frame_top.pack(fill="x", pady=(0, 5))

            tk.Label(frame_top, text="✉️ Seleccionar:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(side="left", padx=5)
            
            cb = ttk.Combobox(frame_top, font=("Arial", 10), width=38, state="readonly")
            cb.pack(side="left", padx=5)
            cb.bind("<<ComboboxSelected>>", lambda e, r=rol_tipo: self.cargar_chat_seleccionado(r))

            tk.Button(
                frame_top, text="🔄 Actualizar", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, 
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

            ent = tk.Entry(frame_input, font=("Arial", 10), bg=COLOR_FONDO_APP, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL)
            ent.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=3)
            ent.bind("<Return>", lambda e, r=rol_tipo: self.responder_chat_por_rol(r))

            tk.Button(
                frame_input, text="Responder ✉️", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, 
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
        self.verificar_mensajes_nuevos_al_iniciar()

    def toggle_reciclaje_negocio(self):
        """Activa o desactiva la función de punto de recepción de reciclaje para un negocio."""
        uid = self.pedir_texto_custom("Toggle Reciclaje", "Ingrese ID/DNI del negocio:")
        if not uid: return

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
            self.datos_sesion.get("nombre", "Admin"), 
            "TOGGLE_RECICLAJE", 
            f"Cambió punto de recepción a '{txt_estado}' para negocio {uid}"
        )

        self.actualizar_tablas()
        messagebox.showinfo("Éxito", f"Se ha {txt_estado.lower()} la recepción de reciclaje para {usuarios[uid].get('nombre', 'el negocio')}.")

    def aplicar_estilos_ttk(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_FONDO_APP, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 10, "bold"), padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_BLANCO)], foreground=[("selected", COLOR_PRIMARIO_AZUL)])
        
        style.configure("Treeview", background=COLOR_BLANCO, foreground=COLOR_TEXTO_MAIN, fieldbackground=COLOR_BLANCO, rowheight=25)
        style.configure("Treeview.Heading", background=COLOR_FONDO_APP, foreground=COLOR_TEXTO_MAIN, font=("Arial", 9, "bold"))

    def verificar_estado_seleccionado(self, event):
        widget_actual = event.widget
        seleccion = widget_actual.selection()
        if not seleccion: return

        item_values = widget_actual.item(seleccion[0], "values")
        if len(item_values) > 3:
            estado_texto = str(item_values[3])
            if "SUSPENDIDO" in estado_texto:
                self.btn_suspender.config(bg="#7F1D1D", text="🛑 CUENTA SUSPENDIDA")
            else:
                self.btn_suspender.config(bg="#B91C1C", text="🛑 Suspender Cuenta")

    def obtener_rango_vecino(self, puntos):
        try:
            pts = int(float(puntos))
        except (ValueError, TypeError):
            pts = 0

        if pts > 300:
            return "👑 Leyenda Suprema"
        elif pts > 150:
            return "🌳 Guerrero Verde"
        elif pts > 50:
            return "🌿 Reciclador Activo"
        else:
            return "🌱 Eco-Novato"

    def llenar_todos_los_combos(self):
        for rol in ["vecino", "negocio", "gestor de reciclaje"]:
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
            rol_usuario = datos.get("rol", "")
            es_match = (rol_usuario == rol_tipo) or (rol_tipo == "gestor de reciclaje" and rol_usuario in ["admin", "gestor de reciclaje", "desarrollador"])
            
            if es_match:
                if uid == self.id_usuario:
                    continue

                nombre_usuario = datos.get("nombre", "Usuario")
                tiene_pendientes = any(m.get("dni_cliente") == uid and m.get("rol") == rol_usuario and not m.get("leido", True) for m in mensajes)
                
                icono_alerta = "🔔 [NUEVO] " if tiene_pendientes else "💬 "
                texto_item = f"{icono_alerta}{nombre_usuario} (ID: {uid})"
                
                opciones.append(texto_item)
                mapeo[texto_item] = uid

        cb['values'] = opciones
        if opciones:
            cb.current(0)
            self.cargar_chat_seleccionado(rol_tipo)
        else:
            cb.set(f"No hay usuarios registrados")
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

        rol_lector = "admin" if self.es_admin_supremo else "gestor de reciclaje"
        marcar_chat_como_leido(dni, rol_lector)

        txt = ui["txt"]
        txt.config(state="normal")
        txt.delete("1.0", tk.END)

        mensajes = cargar_mensajes_chat()
        msg_cliente = [m for m in mensajes if m.get("dni_cliente") == dni]

        if not msg_cliente:
            txt.insert(tk.END, f"💬 No hay mensajes previos con este usuario. Escribe abajo para iniciar la conversación.\n\n")
        else:
            for m in msg_cliente:
                autor = m.get("autor", "Usuario")
                rol = m.get("rol", "").upper()
                texto = m.get("mensaje", "")
                fecha = m.get("fecha", "")
                leido = m.get("leido", True)

                check_leido = " (✓ Leído)" if leido else " (🔔 Nuevo)"
                etiqueta = f"[{fecha}] {autor} ({rol}){check_leido}:\n"
                txt.insert(tk.END, etiqueta)
                txt.insert(tk.END, f"{texto}\n\n")

        txt.see(tk.END)
        txt.config(state="disabled")

    def responder_chat_por_rol(self, rol_tipo):
        ui = self.chats_ui[rol_tipo]
        seleccion = ui["cb"].get()
        if not seleccion or "No hay" in seleccion:
            messagebox.showwarning("Atención", "Seleccione una conversación válida de la bandeja primero.")
            return

        dni = ui["mapeo"].get(seleccion)
        texto = ui["ent"].get().strip()
        if not texto: return

        rol_autor = "admin" if self.es_admin_supremo else "gestor de reciclaje"
        guardar_mensaje_chat(
            dni_cliente=dni,
            autor_nombre=self.datos_sesion.get("nombre", "Soporte"),
            rol_autor=rol_autor,
            mensaje=texto
        )

        ui["ent"].delete(0, tk.END)
        self.cargar_chat_seleccionado(rol_tipo)
        self.llenar_combo_chats_por_rol(rol_tipo)

    def verificar_mensajes_nuevos_al_iniciar(self):
        mensajes = cargar_mensajes_chat()
        hay_nuevos = any(m.get("rol") in ["vecino", "negocio"] and not m.get("leido", True) for m in mensajes)
        if hay_nuevos:
            messagebox.showwarning(
                "💬 Nuevos Mensajes", 
                "¡Tienes mensajes nuevos pendientes por leer y responder en la pestaña 'Soporte (Bandeja)'!"
            )

    def aplicar_icono(self):
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception:
            pass

    def pedir_texto_custom(self, titulo, mensaje):
        win = tk.Toplevel(self.root)
        win.config(bg=COLOR_FONDO_APP)
        win.title(titulo)
        win.geometry("380x180")
        win.resizable(False, False)
        win.grab_set()

        if hasattr(self.root, 'icon_img'):
            win.iconphoto(False, self.root.icon_img)

        container = tk.Frame(win, bg=COLOR_FONDO_APP, padx=15, pady=15)
        container.pack(fill="both", expand=True)

        lbl_msg = tk.Label(
            container, 
            text=mensaje, 
            font=("Arial", 9, "bold"), 
            fg=COLOR_TEXTO_MAIN, 
            bg=COLOR_FONDO_APP,
            wraplength=340,
            justify="center"
        )
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

        def cancelar():
            win.destroy()

        frame_btn = tk.Frame(container, bg=COLOR_FONDO_APP)
        frame_btn.pack(pady=10)

        tk.Button(
            frame_btn, text="Aceptar", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), width=10, relief="flat", cursor="hand2", command=confirmar
        ).pack(side="left", padx=5)

        tk.Button(
            frame_btn, text="Cancelar", bg=COLOR_GRIS_BOTON, fg=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), width=10, relief="flat", cursor="hand2", command=cancelar
        ).pack(side="left", padx=5)

        win.bind("<Return>", lambda e: confirmar())
        win.bind("<Escape>", lambda e: cancelar())

        self.root.wait_window(win)
        return resultado["texto"]

    def actualizar_tablas(self):
        # Limpiar filas existentes antes de recargar
        for item in self.tabla_usr_vecinos.get_children():
            self.tabla_usr_vecinos.delete(item)
        for item in self.tabla_usr_negocios.get_children():
            self.tabla_usr_negocios.delete(item)
        for item in self.tabla_usr_devs.get_children():
            self.tabla_usr_devs.delete(item)

        # Alineación a la izquierda para la columna Puntos (columna 5)
        self.tabla_usr_vecinos.column("#5", anchor="w")

        # 2. Carga de datos
        usuarios = cargar_usuarios()
        logs_tiendas = cargar_log_tiendas()

        # 3. Llenado de tablas de Usuarios
        for uid, datos in usuarios.items():
            suspendido = datos.get("suspendido", False)
            rol = str(datos.get("rol", "")).lower().strip()

            if suspendido:
                motivo = datos.get("motivo_suspension", "Anómalo")
                estado_txt = f"● SUSPENDIDO ({motivo})"
                tag_fila = "suspendido"
            else:
                estado_txt = "● ACTIVO"
                tag_fila = "activo"

            justif_txt = datos.get("justificacion_cliente", "-") or "-"

            if rol == "vecino":
                pts = datos.get("puntos", 0)
                rango_txt = self.obtener_rango_vecino(pts) if hasattr(self, 'obtener_rango_vecino') else "Estándar"
                
                tupla_vecinos = (
                    uid,
                    datos.get("nombre", "-"),
                    "VECINO",
                    estado_txt,
                    f"{pts} PTS",
                    rango_txt,
                    justif_txt
                )
                self.tabla_usr_vecinos.insert("", "end", values=tupla_vecinos, tags=(tag_fila,))

            elif rol == "negocio":
                # 1. Obtener puntos recolectados por reciclaje
                try:
                    pts_reciclaje = float(obtener_puntos_recolectados_por_tienda(uid))
                except (ValueError, TypeError):
                    pts_reciclaje = 0.0
                
                # 2. Obtener puntos por ventas / canjes realizados en la tienda
                pts_ventas = 0.0
                for log in logs_tiendas:
                    if str(log.get("tienda_id")) == str(uid):
                        try:
                            pts_ventas += float(log.get("puntos_descontados", 0))
                        except (ValueError, TypeError):
                            pass

                # 3. Puntos directo desde el JSON del usuario (convertido de forma segura)
                try:
                    pts_comercio_json = float(datos.get("puntos", 0))
                except (ValueError, TypeError):
                    pts_comercio_json = 0.0

                # 4. Suma total de puntos acumulados por la tienda
                pts_recolectados = round(pts_reciclaje + pts_ventas + pts_comercio_json, 1)

                # 5. Cálculo de Comisión (10%) y Total Pts
                comision_10_pts = round(pts_recolectados * 0.10, 1)
                total_pts = round(pts_recolectados + comision_10_pts, 1)
                
                # Convertir el Total Pts a Soles (multiplicando por 0.10 o tu factor de conversión)
                total_soles = round(total_pts * 0.10, 2)

                rec_activo = datos.get("reciclaje_activo", True)
                txt_reciclaje = "● HABILITADO" if rec_activo else "● DESHABILITADO"
                justif_txt = datos.get("justificacion_cliente", "-") or "-"

                tupla_negocio = (
                    uid,
                    datos.get("nombre", "-"),
                    "NEGOCIO",
                    estado_txt,
                    txt_reciclaje,
                    f"{pts_recolectados} PTS",
                    f"{comision_10_pts} PTS", 
                    f"{total_pts} PTS - (S/ {total_soles:.2f})",  # Total Pts con conversión a Soles
                    justif_txt
                )

                self.tabla_usr_negocios.insert("", "end", values=tupla_negocio, tags=(tag_fila,))

            # TABLA 3: GESTORES Y ADMINISTRADORES
            elif any(r in rol for r in ["gestor", "admin", "dev", "desarrollador"]):
                tupla_staff = (
                    uid,
                    datos.get("nombre", "-"),
                    str(datos.get("rol", "-")).upper(),
                    estado_txt,  # <-- Agregada la coma aquí
                    "N/A",
                    "Personal Staff",
                    justif_txt
                )
                self.tabla_usr_devs.insert("", "end", values=tupla_staff, tags=(tag_fila,))

                
        # 4. Llenado de Promociones Activas
        for p in cargar_promociones():
            try:
                pts_oferta = int(float(p.get('puntos', 0)))
            except (ValueError, TypeError):
                pts_oferta = 0

            self.tabla_promos.insert("", "end", values=(
                p.get("tienda_nombre", "Tienda"), 
                p.get("titulo", "-"), 
                f"S/ {float(p.get('precio_soles', 0)):.2f}", 
                f"{pts_oferta} PTS", 
                p.get("descripcion", "-")
            ))

        # 5. Llenado del Log de Tiendas
        for log in reversed(logs_tiendas):
            self.tabla_tnd.insert("", "end", values=(
                log.get("fecha"), 
                log.get("tienda_id"), 
                log.get("tienda_nombre"), 
                log.get("dni_cliente"), 
                log.get("puntos_descontados")
            ))

        # 6. Llenado de Actividad de Clientes
        tablas_cli = [
            self.tabla_cli_todos, 
            self.tabla_cli_abonos, 
            self.tabla_cli_canjes, 
            self.tabla_cli_entregas, 
            self.tabla_cli_resenas
        ]
        for t in tablas_cli:
            for item in t.get_children():
                t.delete(item)

        for log in reversed(cargar_log_clientes()):
            fecha = log.get("fecha", "-")
            dni = log.get("dni_cliente", "-")
            tipo = log.get("tipo", "")
            
            try:
                puntos = int(float(log.get("puntos", 0)))
            except (ValueError, TypeError):
                puntos = 0

            detalle = log.get("detalle", "")
            valores = (fecha, dni, tipo, puntos, detalle)

            self.tabla_cli_todos.insert("", "end", values=valores)

            if tipo in ["ABONO_RECICLAJE", "SUMA_ADMIN"]:
                self.tabla_cli_abonos.insert("", "end", values=valores)
            elif tipo in ["CANJE_OFERTA", "CANJE_TIENDA", "REDUCCION_ADMIN"]:
                self.tabla_cli_canjes.insert("", "end", values=valores)
            elif tipo in ["ENTREGA_OFERTA"]:
                self.tabla_cli_entregas.insert("", "end", values=valores)
            elif tipo in ["RESEÑA_TIENDA"]:
                estrellas_str = "⭐ (Sin calificación)"
                comentario_str = detalle

                if "Calificación:" in detalle:
                    partes = detalle.split("Calificación:")
                    if len(partes) > 1:
                        subpartes = partes[1].split("|")
                        estrellas_str = subpartes[0].strip()
                        if len(subpartes) > 1:
                            comentario_str = subpartes[1].replace("Reseña:", "").strip()

                valores_resena = (fecha, dni, estrellas_str, comentario_str)
                self.tabla_cli_resenas.insert("", "end", values=valores_resena)

        if self.es_admin_supremo:
            for item in self.tabla_dev.get_children(): self.tabla_dev.delete(item)
            for log in reversed(cargar_log_devs()):
                self.tabla_dev.insert("", "end", values=(log.get("fecha"), log.get("autor_id"), log.get("autor_nombre"), log.get("accion"), log.get("objetivo")))
                
    def dialogo_suspender_cuenta(self):
        uid = self.pedir_texto_custom("Suspender Cuenta", "Ingrese DNI / ID del usuario a suspender:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe en el sistema.")
            return

        motivo = self.pedir_texto_custom("Motivo de Suspensión", f"Ingrese el motivo para {usuarios[uid]['nombre']}:")
        if not motivo: return

        usuarios[uid]["suspendido"] = True
        usuarios[uid]["motivo_suspension"] = motivo
        guardar_usuarios(usuarios)

        rol_autor = "admin" if self.es_admin_supremo else "gestor de reciclaje"
        guardar_mensaje_chat(
            dni_cliente=uid,
            autor_nombre=self.datos_sesion.get("nombre", "Administración"),
            rol_autor=rol_autor,
            mensaje=f"🚨 AVISO DE SISTEMA: Su cuenta ha sido SUSPENDIDA. Motivo: {motivo}"
        )

        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUSPENDER_CUENTA", f"Suspendió al usuario {uid}. Motivo: {motivo}")
        self.actualizar_tablas()
        self.llenar_todos_los_combos()
        messagebox.showinfo("Éxito", f"La cuenta de {usuarios[uid]['nombre']} ha sido suspendida correctamente.")

    def dialogo_levantar_suspension(self):
        uid = self.pedir_texto_custom("Levantar Suspensión", "Ingrese DNI / ID del usuario a reactivar:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe.")
            return

        if not usuarios[uid].get("suspendido", False):
            messagebox.showinfo("Información", "Esta cuenta ya se encuentra activa.")
            return

        motivo_reactivacion = self.pedir_texto_custom(
            "Motivo de Reactivación", 
            f"Ingrese el motivo por el cual levanta la suspensión a {usuarios[uid]['nombre']}:"
        )
        if not motivo_reactivacion:
            messagebox.showwarning("Atención", "Debe ingresar un motivo para reactivar la cuenta.")
            return

        usuarios[uid]["suspendido"] = False
        usuarios[uid]["motivo_suspension"] = ""
        usuarios[uid]["justificacion_cliente"] = ""
        guardar_usuarios(usuarios)

        rol_autor = "admin" if self.es_admin_supremo else "gestor de reciclaje"
        guardar_mensaje_chat(
            dni_cliente=uid,
            autor_nombre=self.datos_sesion.get("nombre", "Administración"),
            rol_autor=rol_autor,
            mensaje=f"✅ AVISO DE SISTEMA: Se ha levantado la suspensión de su cuenta. Motivo de anulación: {motivo_reactivacion}"
        )

        registrar_accion_dev(
            self.id_usuario, 
            self.datos_sesion.get("nombre"), 
            "ACTIVAR_CUENTA", 
            f"Levantó suspensión a {uid}. Motivo Admin: {motivo_reactivacion}"
        )

        self.actualizar_tablas()
        self.llenar_todos_los_combos()
        messagebox.showinfo("Éxito", f"Se ha levantado la suspensión de {usuarios[uid]['nombre']}.\nMotivo: {motivo_reactivacion}")

    def dialogo_crear_cuenta(self):
        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Crear Nueva Cuenta")
        win_modal.geometry("340x380")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text="Seleccione Tipo de Cuenta:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        
        roles_disponibles = ["vecino", "negocio","gestor de reciclaje"]

        cb_rol = ttk.Combobox(win_modal, values=roles_disponibles, state="readonly")
        cb_rol.pack(pady=5)
        cb_rol.current(0)

        tk.Label(win_modal, text="DNI / Código de Cuenta:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_uid = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_uid.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Nombre / Razón Social:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_nom = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_nom.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Correo Electrónico:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_correo = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_correo.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Teléfono / Celular:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_tel = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_tel.pack(pady=2, ipady=2)

        tk.Label(win_modal, text="Contraseña Inicial:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_clave = tk.Entry(win_modal, show="*", bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_clave.pack(pady=2, ipady=2)

        def guardar():
            uid = ent_uid.get().strip()
            nom = ent_nom.get().strip()
            rol_raw = cb_rol.get().strip()
            correo = ent_correo.get().strip()
            tel = ent_tel.get().strip()
            clave = ent_clave.get().strip()

            if not uid or not nom or not clave:
                messagebox.showerror("Error", "Complete los campos obligatorios.", parent=win_modal)
                return

            usuarios = cargar_usuarios()
            if uid in usuarios:
                messagebox.showerror("Error", "El ID/DNI ya existe.", parent=win_modal)
                return

            # Normalizar el rol para guardar la clave correcta en usuarios.json
            rol_lower = rol_raw.lower()
            if "gestor" in rol_lower:
                rol_final = "gestor_reciclaje"
            elif "admin" in rol_lower:
                rol_final = "admin"
            elif "negocio" in rol_lower or "tienda" in rol_lower:
                rol_final = "negocio"
            else:
                rol_final = "vecino"

            usuarios[uid] = {
                "rol": rol_final,
                "nombre": nom,
                "correo": correo or "-",
                "telefono": tel or "-",
                "clave": clave,
                "puntos": 0,
                "suspendido": False,
                "motivo_suspension": "",
                "justificacion_cliente": ""
            }
            
            guardar_usuarios(usuarios)
            
            if hasattr(self, 'id_usuario'):
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre", "Admin"), "CREAR_CUENTA", f"Creó cuenta {uid} ({rol_final.upper()})")

            self.actualizar_tablas()
            if hasattr(self, 'llenar_todos_los_combos'):
                self.llenar_todos_los_combos()
                
            win_modal.destroy()
            messagebox.showinfo("Éxito", f"Cuenta de tipo '{rol_final.upper()}' creada correctamente.")

        tk.Button(win_modal, text="Guardar Cuenta", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), command=guardar, relief="flat", cursor="hand2", pady=5).pack(pady=15)

    def dialogo_eliminar_cuenta(self):
        uid = self.pedir_texto_custom("Eliminar Cuenta", "Ingrese DNI / ID a eliminar:")
        if not uid: return

        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "La cuenta no existe.")
            return

        rol_obj = usuarios[uid]["rol"]
        if rol_obj in ["admin", "gestor de reciclaje", "desarrollador"] and not self.es_admin_supremo:
            messagebox.showerror("Acceso Denegado", "Solo el Administrador puede eliminar a otros administradores o gestores.")
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente la cuenta de {usuarios[uid]['nombre']}?"):
            nom_removido = usuarios[uid]['nombre']
            del usuarios[uid]
            guardar_usuarios(usuarios)
            registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "ELIMINAR_CUENTA", f"Eliminó la cuenta {uid} ({nom_removido})")
            self.actualizar_tablas()
            self.llenar_todos_los_combos()
            messagebox.showinfo("Éxito", "Cuenta eliminada.")

    def dialogo_registrar_reciclaje(self):
        dni = self.pedir_texto_custom("Sumar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "DNI no corresponde a un vecino.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden sumar puntos. La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA."
            )
            return

        win_modal = tk.Toplevel(self.root)
        win_modal.config(bg=COLOR_FONDO_APP)
        win_modal.title("Sumar Puntos")
        win_modal.geometry("320x230")
        win_modal.resizable(False, False)
        win_modal.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_modal.iconphoto(False, self.root.icon_img)

        tk.Label(win_modal, text=f"Vecino: {usuarios[dni]['nombre']}", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=5)
        cb_mat = ttk.Combobox(win_modal, values=list(Material.TASAS.keys()), state="readonly"); cb_mat.pack(pady=5); cb_mat.current(0)
        tk.Label(win_modal, text="Peso en KG:", fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_kg = tk.Entry(win_modal, bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, relief="flat", highlightthickness=1, highlightbackground=COLOR_SECUNDARIO_AZUL); ent_kg.pack(pady=5, ipady=2)

        def procesar():
            raw_input_kg = ent_kg.get().strip()
            if not raw_input_kg.isdigit():
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)
                return

            try:
                peso = int(raw_input_kg)
                mat = cb_mat.get()
                puntos_calculados = Material.calcular_puntos(mat, float(peso))
                puntos_a_abonar_bruto = int(round(puntos_calculados))
                
                try:
                    puntos_actuales_user = int(float(usuarios[dni].get("puntos", 0)))
                except (ValueError, TypeError):
                    puntos_actuales_user = 0

                # BLINDAJE ESTRICTO DE TOPE MÁXIMO DE 2,000 PUNTOS (ADMINISTRACIÓN)
                nuevo_total_tentativo = puntos_actuales_user + puntos_a_abonar_bruto
                if nuevo_total_tentativo > 2000:
                    puntos = max(0, 2000 - puntos_actuales_user)
                    messagebox.showwarning("Tope Máximo", f"El vecino alcanzaría más de 2,000 puntos. Se ajustará al tope máximo permitido (se abonarán solo {puntos} PTS).", parent=win_modal)
                    nuevo_saldo = 2000
                else:
                    puntos = puntos_a_abonar_bruto
                    nuevo_saldo = nuevo_total_tentativo
                
                usuarios[dni]["puntos"] = nuevo_saldo
                guardar_usuarios(usuarios)
                
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "SUMAR_PUNTOS", f"Abonó {puntos} pts a {dni} por {mat}")
                registrar_accion_cliente(dni, "ABONO_RECICLAJE", puntos, f"Reciclaje de {mat} ({peso} kg)")
                
                self.actualizar_tablas()
                win_modal.destroy()
                messagebox.showinfo("Éxito", f"Se sumaron {puntos} puntos.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros", parent=win_modal)

        tk.Button(win_modal, text="Sumar Puntos", bg=COLOR_PRIMARIO_AZUL, fg=COLOR_BLANCO, activeforeground=COLOR_BLANCO, font=("Arial", 9, "bold"), command=procesar, relief="flat", cursor="hand2", pady=5).pack(pady=10)

    def dialogo_reducir_puntos(self):
        dni = self.pedir_texto_custom("Restar Puntos", "Ingrese DNI del vecino:")
        if not dni: return
        usuarios = cargar_usuarios()
        if dni not in usuarios or usuarios[dni]["rol"] != "vecino":
            messagebox.showerror("Error", "Vecino no encontrado.")
            return

        if usuarios[dni].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden restar puntos. La cuenta de {usuarios[dni]['nombre']} se encuentra SUSPENDIDA."
            )
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
                    registrar_accion_cliente(dni, "REDUCCION_ADMIN", -pts, "Ajuste manual de administración")
                    self.actualizar_tablas()
                    messagebox.showinfo("Éxito", f"Se restaron {pts} puntos.")
                else:
                    messagebox.showerror("Error", "Puntos insuficientes o cantidad inválida.")
            except ValueError:
                messagebox.showerror("Error", "Solamente números enteros")

    def dialogo_cambiar_clave(self):
        uid = self.pedir_texto_custom("Renovar Clave", "Ingrese DNI/ID de la cuenta:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid in usuarios:
            nueva = self.pedir_texto_custom("Renovar Clave", f"Nueva contraseña para {usuarios[uid]['nombre']}:")
            if nueva:
                usuarios[uid]["clave"] = nueva
                guardar_usuarios(usuarios)
                registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "CAMBIO_CLAVE", f"Modificó la clave de {uid}")
                messagebox.showinfo("Éxito", "Contraseña renovada correctamente.")
        else:
            messagebox.showerror("Error", "Usuario no encontrado.")

    def dialogo_editar_datos(self):
        uid = self.pedir_texto_custom("Editar Datos", "Ingrese DNI/ID:")
        if not uid: return
        usuarios = cargar_usuarios()
        if uid not in usuarios:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        if usuarios[uid].get("suspendido", False):
            messagebox.showwarning(
                "Cuenta Suspendida", 
                f"No se pueden editar los datos. La cuenta de {usuarios[uid]['nombre']} se encuentra SUSPENDIDA."
            )
            return

        nuevo_nom = self.pedir_texto_custom("Editar", "Nuevo Nombre:")
        nuevo_correo = self.pedir_texto_custom("Editar", "Nuevo Correo:")
        nuevo_tel = self.pedir_texto_custom("Editar", "Nuevo Celular:")
        
        if nuevo_nom: usuarios[uid]["nombre"] = nuevo_nom
        if nuevo_correo: usuarios[uid]["correo"] = nuevo_correo
        if nuevo_tel: usuarios[uid]["telefono"] = nuevo_tel

        guardar_usuarios(usuarios)
        registrar_accion_dev(self.id_usuario, self.datos_sesion.get("nombre"), "EDITAR_DATOS", f"Actualizó datos personales de {uid}")
        self.actualizar_tablas()
        messagebox.showinfo("Éxito", "Datos actualizados.")

    def dialogo_ver_promociones_con_foto(self):
        """Muestra el panel de promociones con 3 columnas, fondo fijo e ilustración floral visible."""
        win_promos = tk.Toplevel(self.root)
        win_promos.title("Panel de Promociones")
        win_promos.geometry("720x540")
        win_promos.resizable(False, False)
        win_promos.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_promos.iconphoto(False, self.root.icon_img)

        # 1. Label con la imagen estática de fondo
        nombres_archivos = ["fondo_ofertas_admin.png", "fondo_ofertas_admin.jpg"]
        ruta_encontrada = next((os.path.join("img", n) for n in nombres_archivos if os.path.exists(os.path.join("img", n))), None)

        if ruta_encontrada:
            try:
                from PIL import Image, ImageTk
                img_pil = Image.open(ruta_encontrada).convert("RGBA").resize((720, 540), Image.Resampling.LANCZOS)
                win_promos.bg_img = ImageTk.PhotoImage(img_pil)
                
                # Imagen fija pegada a la ventana con place
                lbl_bg = tk.Label(win_promos, image=win_promos.bg_img, bd=0)
                lbl_bg.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Aviso imagen de fondo: {e}")

        # 1. Canvas con fondo blanco puro (o sin borde)
        canvas = tk.Canvas(win_promos, bg="#FFFFFF", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(win_promos, orient="vertical", command=canvas.yview)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Dibujar imagen de fondo fija dentro del Canvas
        bg_canvas_id = None
        if hasattr(win_promos, 'bg_img'):
            bg_canvas_id = canvas.create_image(0, 0, image=win_promos.bg_img, anchor="nw")

        # 2. Contenedor de tarjetas (frame_grid) con bg="#FFFFFF" en lugar de plomo
        frame_grid = tk.Frame(canvas, bg="#FFFFFF")
        window_id = canvas.create_window((15, 15), window=frame_grid, anchor="nw")

        def _actualizar_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame_grid.bind("<Configure>", _actualizar_scrollregion)

        # Mantiene la imagen fija al hacer Scroll
        def _al_hacer_scroll(*args):
            if bg_canvas_id:
                y_pos = canvas.canvasy(0)
                canvas.coords(bg_canvas_id, 0, y_pos)

        canvas.configure(yscrollcommand=lambda first, last: (scrollbar.set(first, last), _al_hacer_scroll()))

        # Modal para el desglose completo de la descripción
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

            btn_color = COLOR_PRIMARIO_AZUL
            tk.Button(
                win_desc, 
                text="Cerrar", 
                bg=btn_color, 
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

            # AHORA 3 COLUMNAS PARA APROVECHAR EL ESPACIO A LA DERECHA
            cols = 3
            LIMITE_CARACTERES = 28

            for idx, p in enumerate(promos):
                row = idx // cols
                col = idx % cols

                # Tarjeta compacta de 210x165 px con bordes limpios
                border_color = COLOR_SECUNDARIO_AZUL if hasattr(self, 'es_admin_supremo') else "#52B788"
                card = tk.Frame(
                    frame_grid, 
                    bg=COLOR_BLANCO, 
                    bd=1, 
                    relief="solid", 
                    highlightbackground=border_color, 
                    highlightthickness=1,
                    padx=8, 
                    pady=8,
                    width=210,
                    height=165
                )
                # Separación de 10px entre recuadros en todas las direcciones
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

                # Manejo de eliminación
                if hasattr(self, 'es_admin_supremo'):
                    def eliminar_con_motivo(i=idx, tienda_id=p.get('tienda_id'), titulo=titulo_oferta):
                        motivo = self.pedir_texto_custom("Eliminar Oferta", f"Motivo de eliminación para '{titulo}':")
                        if not motivo:
                            messagebox.showwarning("Requerido", "Debe ingresar una justificación para eliminar la oferta.")
                            return

                        if messagebox.askyesno("Confirmar", f"¿Eliminar definitivamente la oferta '{titulo}'?"):
                            if eliminar_promocion_admin(i, tienda_id, motivo, self.datos_sesion.get("nombre", "Administración")):
                                registrar_accion_dev(
                                    self.id_usuario, 
                                    self.datos_sesion.get("nombre"), 
                                    "ELIMINAR_OFERTA", 
                                    f"Eliminó oferta '{titulo}' de la tienda {tienda_id}. Motivo: {motivo}"
                                )
                                messagebox.showinfo("Éxito", "La oferta ha sido eliminada y la tienda notificada.")
                                self.actualizar_tablas()
                                refrescar_grid()

                    btn_eliminar = tk.Button(
                        card, 
                        text="🗑️ Eliminar Oferta", 
                        bg=COLOR_ROJO_ALERTA, 
                        fg=COLOR_BLANCO, 
                        activeforeground=COLOR_BLANCO, 
                        font=("Arial", 8, "bold"), 
                        relief="flat", 
                        command=eliminar_con_motivo, 
                        cursor="hand2", 
                        pady=2
                    )
                else:
                    def eliminar_propia(idx_a_borrar=idx, titulo=titulo_oferta):
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