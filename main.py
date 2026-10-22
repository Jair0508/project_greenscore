import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from datos.gestor import cargar_usuarios, guardar_usuarios, registrar_accion_cliente
from interfaces.admin import VentanaAdmin
from interfaces.negocio import VentanaNegocio
from interfaces.vecino import VentanaVecino

# Color de Fondo Global de la aplicación
COLOR_FONDO_APP = "#ECEFF1"

class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.aplicar_estilos_base()
        self.mostrar_login()

    def aplicar_estilos_base(self):
        self.root.config(bg=COLOR_FONDO_APP)
        # Carga el ícono directamente desde la carpeta img/
        ruta_png = os.path.join("img", "logo.png")
        try:
            if os.path.exists(ruta_png):
                # Es recomendable guardar una referencia de la imagen para evitar que el recolector de basura la elimine
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
        self.root.geometry("400x450")
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

        # 2. MARCO CONTENEDOR SUTIL
        frame_box = tk.Frame(
            self.root, 
            bg="#FFFFFF", 
            bd=1, 
            relief="solid", 
            padx=20, 
            pady=20
        )
        frame_box.pack(pady=40, padx=30, fill="both")

        tk.Label(
            frame_box, 
            text="Acceso al Sistema", 
            font=("Arial", 12, "bold"), 
            fg="#2E7D32", 
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(frame_box, text="Usuario / DNI:", font=("Arial", 10, "bold"), fg="#37474F", bg="#FFFFFF").pack(anchor="w", pady=(5, 2))
        self.ent_user = tk.Entry(frame_box, font=("Arial", 11), bg="#F5F5F5", relief="flat", highlightthickness=1, highlightbackground="#CCCCCC")
        self.ent_user.pack(fill="x", pady=(0, 12), ipady=3)

        tk.Label(frame_box, text="Contraseña:", font=("Arial", 10, "bold"), fg="#37474F", bg="#FFFFFF").pack(anchor="w", pady=(5, 2))
        self.ent_pass = tk.Entry(frame_box, show="*", font=("Arial", 11), bg="#F5F5F5", relief="flat", highlightthickness=1, highlightbackground="#CCCCCC")
        self.ent_pass.pack(fill="x", pady=(0, 18), ipady=3)

        btn_ingresar = tk.Button(
            frame_box, 
            text="🔑 Ingresar", 
            bg="#2E7D32", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=self.validar_login,
            cursor="hand2",
            relief="flat",
            pady=6
        )
        btn_ingresar.pack(fill="x", pady=(0, 10))

        btn_registro = tk.Button(
            frame_box, 
            text="📝 ¿Eres nuevo vecino? Regístrate", 
            bg="#1976D2", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self.registrar_nuevo_usuario,
            cursor="hand2",
            relief="flat",
            pady=5
        )
        btn_registro.pack(fill="x")


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

        clave = simpledialog.askstring("Registro de Vecino", "Cree una Contraseña:", show="*", parent=self.root)
        if not clave: return

        usuarios[dni] = {
            "rol": "vecino",
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "clave": clave,
            "puntos": 0
        }
        guardar_usuarios(usuarios)
        registrar_accion_cliente(dni, "REGISTRO", 0, "Cuenta creada voluntariamente por cliente")
        messagebox.showinfo("¡Registro Exitoso!", f"Bienvenido(a) {nombre}. Tu cuenta ha sido creada.")

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