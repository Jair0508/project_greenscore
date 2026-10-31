import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datos.gestor import cargar_usuarios, guardar_usuarios, registrar_accion_cliente
from interfaces.admin import VentanaAdmin
from interfaces.negocio import VentanaNegocio
from interfaces.vecino import VentanaVecino

# ==========================================
# PALETA DE COLORES "ECO-GESTIÓN" (SIN NEGRO)
# ==========================================
COLOR_FONDO_APP      = "#F4F9F4"  # Blanco Menta Suave
COLOR_TEXTO_MAIN     = "#1B4332"  # Verde Bosque Profundo (Reemplazo de negro)
COLOR_PRIMARIO       = "#40916C"  # Verde Hoja (Acciones principales / Login)
COLOR_SECUNDARIO     = "#52B788"  # Verde Claro Fresco (Bordes / Focus)
COLOR_ACENTO_REGISTRO= "#E76F51"  # Terracota Suave (Botón Registro / Destacados)
COLOR_BLANCO         = "#FFFFFF"  # Blanco puro para la tarjeta central
COLOR_ROJO_ALERTA    = "#C62828"  # Rojo suave para recuperación de clave

class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.aplicar_estilos_base()
        self.mostrar_login()

    def aplicar_estilos_base(self):
        self.root.config(bg=COLOR_FONDO_APP)
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                self.root.icon_img = tk.PhotoImage(file=ruta_png)
                self.root.iconphoto(False, self.root.icon_img)
        except Exception as e:
            print(f"Error al cargar ícono: {e}")

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_pantalla()
        self.root.title("EcoPuntos - Inicio de Sesión")
        self.root.geometry("420x510")
        self.root.resizable(False, False)

        # 1. CARGAR IMAGEN DE FONDO (fondo_ingreso.png)
        ruta_fondo = os.path.join("img", "fondo_ingreso.png")
        if os.path.exists(ruta_fondo):
            try:
                self.root.bg_img = tk.PhotoImage(file=ruta_fondo)
                lbl_fondo = tk.Label(self.root, image=self.root.bg_img)
                lbl_fondo.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Error al cargar imagen de fondo: {e}")

        # 2. MARCO CONTENEDOR (Tarjeta Blanca con Borde Verde Claro)
        frame_box = tk.Frame(
            self.root, 
            bg=COLOR_BLANCO, 
            bd=1, 
            relief="solid", 
            highlightbackground=COLOR_SECUNDARIO,
            highlightthickness=1,
            padx=20, 
            pady=20
        )
        frame_box.pack(pady=30, padx=30, fill="both")

        # Título "Acceso al Sistema"
        tk.Label(
            frame_box, 
            text="Acceso al Sistema", 
            font=("Arial", 12, "bold"), 
            fg=COLOR_TEXTO_MAIN, 
            bg=COLOR_BLANCO
        ).pack(anchor="w", pady=(0, 10))

        # Usuario / DNI
        tk.Label(frame_box, text="Usuario / DNI:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(anchor="w", pady=(5, 2))
        self.ent_user = tk.Entry(
            frame_box, 
            font=("Arial", 11), 
            bg=COLOR_FONDO_APP, 
            fg=COLOR_TEXTO_MAIN,
            relief="flat", 
            highlightthickness=1, 
            highlightbackground=COLOR_SECUNDARIO
        )
        self.ent_user.pack(fill="x", pady=(0, 10), ipady=3)

        # Contraseña
        tk.Label(frame_box, text="Contraseña:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_BLANCO).pack(anchor="w", pady=(5, 2))
        self.ent_pass = tk.Entry(
            frame_box, 
            show="*", 
            font=("Arial", 11), 
            bg=COLOR_FONDO_APP, 
            fg=COLOR_TEXTO_MAIN,
            relief="flat", 
            highlightthickness=1, 
            highlightbackground=COLOR_SECUNDARIO
        )
        self.ent_pass.pack(fill="x", pady=(0, 14), ipady=3)

        # Botón Ingresar (Verde Hoja Principal)
        btn_ingresar = tk.Button(
            frame_box, 
            text="🔑 Ingresar", 
            bg=COLOR_PRIMARIO, 
            fg=COLOR_BLANCO, 
            activebackground=COLOR_PRIMARIO,
            activeforeground=COLOR_BLANCO,
            font=("Arial", 10, "bold"), 
            command=self.validar_login,
            cursor="hand2",
            relief="flat",
            pady=6
        )
        btn_ingresar.pack(fill="x", pady=(0, 8))

        # Botón Registro (Terracota Suave)
        btn_registro = tk.Button(
            frame_box, 
            text="📝 ¿Eres nuevo vecino? Regístrate", 
            bg=COLOR_ACENTO_REGISTRO, 
            fg=COLOR_BLANCO, 
            activebackground=COLOR_ACENTO_REGISTRO,
            activeforeground=COLOR_BLANCO,
            font=("Arial", 9, "bold"), 
            command=self.registrar_nuevo_usuario,
            cursor="hand2",
            relief="flat",
            pady=5
        )
        btn_registro.pack(fill="x", pady=(0, 6))

        # Botón de Recuperación de Contraseña
        btn_olvido = tk.Button(
            frame_box,
            text="❓ ¿Olvidaste tu contraseña?",
            bg=COLOR_BLANCO,
            fg=COLOR_ROJO_ALERTA,
            activebackground=COLOR_BLANCO,
            activeforeground=COLOR_ROJO_ALERTA,
            font=("Arial", 8, "bold"),
            command=self.dialogo_recuperar_clave,
            cursor="hand2",
            relief="flat"
        )
        btn_olvido.pack(fill="x")

    def registrar_nuevo_usuario(self):
        dni = simpledialog.askstring("Registro de Vecino", "Ingrese su DNI (Usuario):", parent=self.root)
        if not dni: return
        
        usuarios = cargar_usuarios()
        if dni in usuarios:
            messagebox.showerror("Error", "Este DNI ya se encuentra registrado.")
            return

        nombre = simpledialog.askstring("Registro de Vecino", "Ingrese su Nombre Completo:", parent=self.root)
        if not nombre: return

        correo = simpledialog.askstring("Registro de Vecino", "Ingrese su Correo Electrónico Personal:", parent=self.root)
        if not correo: return

        telefono = simpledialog.askstring("Registro de Vecino", "Ingrese su Número de Celular:", parent=self.root)
        if not telefono: return

        pregunta = simpledialog.askstring("Seguridad", "Pregunta Secreta (ej: ¿Nombre de tu primera mascota?):", parent=self.root)
        if not pregunta: return

        respuesta = simpledialog.askstring("Seguridad", "Respuesta a tu pregunta secreta:", parent=self.root)
        if not respuesta: return

        clave = simpledialog.askstring("Registro de Vecino", "Cree una Contraseña:", show="*", parent=self.root)
        if not clave: return

        usuarios[dni] = {
            "rol": "vecino",
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "clave": clave,
            "puntos": 0,
            "pregunta_secreta": pregunta,
            "respuesta_secreta": respuesta.strip().lower()
        }
        guardar_usuarios(usuarios)
        registrar_accion_cliente(dni, "REGISTRO", 0, "Cuenta creada voluntariamente por cliente")
        messagebox.showinfo("¡Registro Exitoso!", f"Bienvenido(a) {nombre}. Tu cuenta ha sido creada.")

    def dialogo_recuperar_clave(self):
        dni = simpledialog.askstring("Recuperar Contraseña", "Ingrese su DNI / Usuario:", parent=self.root)
        if not dni: return

        usuarios = cargar_usuarios()
        if dni not in usuarios:
            messagebox.showerror("Error", "El DNI ingresado no está registrado en el sistema.")
            return

        user_data = usuarios[dni]
        pregunta = user_data.get("pregunta_secreta", "")
        respuesta_correcta = user_data.get("respuesta_secreta", "")

        if not pregunta or not respuesta_correcta:
            messagebox.showwarning(
                "Seguridad", 
                "Su cuenta no tiene configurada una pregunta secreta.\nPor favor contacte al administrador a través del chat de soporte."
            )
            return

        # Modal para responder la pregunta secreta
        win_rec = tk.Toplevel(self.root)
        win_rec.config(bg=COLOR_FONDO_APP)
        win_rec.title("Verificación de Seguridad")
        win_rec.geometry("380x230")
        win_rec.resizable(False, False)
        win_rec.grab_set()

        if hasattr(self.root, 'icon_img'):
            win_rec.iconphoto(False, self.root.icon_img)

        tk.Label(win_rec, text="Pregunta de Seguridad:", font=("Arial", 10, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack(pady=(15, 2))
        tk.Label(win_rec, text=f"\"{pregunta}\"", font=("Arial", 10, "italic"), fg=COLOR_PRIMARIO, bg=COLOR_FONDO_APP, wraplength=340).pack(pady=(0, 10))

        tk.Label(win_rec, text="Su Respuesta:", font=("Arial", 9, "bold"), fg=COLOR_TEXTO_MAIN, bg=COLOR_FONDO_APP).pack()
        ent_resp = tk.Entry(
            win_rec, 
            font=("Arial", 10), 
            width=30, 
            bg=COLOR_BLANCO, 
            fg=COLOR_TEXTO_MAIN, 
            relief="flat", 
            highlightthickness=1, 
            highlightbackground=COLOR_SECUNDARIO
        )
        ent_resp.pack(pady=4, ipady=2)
        ent_resp.focus_set()

        def verificar_y_restablecer():
            resp_user = ent_resp.get().strip().lower()
            if resp_user != respuesta_correcta:
                messagebox.showerror("Error de Seguridad", "Respuesta incorrecta. No se puede restablecer la contraseña.")
                return

            nueva_clave = simpledialog.askstring("Nueva Contraseña", "Ingrese su nueva contraseña:", show="*", parent=win_rec)
            if not nueva_clave: return

            usuarios[dni]["clave"] = nueva_clave
            guardar_usuarios(usuarios)
            win_rec.destroy()
            messagebox.showinfo("Éxito", "¡Su contraseña ha sido actualizada correctamente! Ya puede iniciar sesión.")

        tk.Button(
            win_rec, 
            text="Validar y Cambiar Clave", 
            bg=COLOR_PRIMARIO, 
            fg=COLOR_BLANCO, 
            font=("Arial", 9, "bold"), 
            command=verificar_y_restablecer, 
            relief="flat", 
            pady=4,
            cursor="hand2"
        ).pack(pady=15)

    def validar_login(self):
        usuario = self.ent_user.get().strip()
        clave = self.ent_pass.get().strip()
        usuarios = cargar_usuarios()

        if usuario in usuarios and usuarios[usuario]["clave"] == clave:
            rol = usuarios[usuario]["rol"]
            self.limpiar_pantalla()

            if rol in ["admin", "desarrollador"]:
                VentanaAdmin(self.root, usuario, self.mostrar_login)
            elif rol == "negocio":
                VentanaNegocio(self.root, usuario, self.mostrar_login)
            elif rol == "vecino":
                VentanaVecino(self.root, usuario, self.mostrar_login)
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppPrincipal(root)
    root.mainloop()