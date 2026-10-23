import os
import tkinter as tk

def obtener_imagen_miniatura(ruta_img, ancho=70, alto=70):
    """Carga y muestra imágenes nativas con Tkinter sin depender de PIL/Pillow."""
    if ruta_img and os.path.exists(ruta_img):
        try:
            # Soporta formatos nativos PNG, GIF, PPM/PGM
            img = tk.PhotoImage(file=ruta_img)
            
            # Reducción de escala aproximada para ajustar el tamaño en píxeles
            w, h = img.width(), img.height()
            factor_sub = max(1, int(max(w / ancho, h / alto)))
            if factor_sub > 1:
                img = img.subsample(factor_sub)
                
            return img
        except Exception as e:
            print(f"Error procesando imagen {ruta_img}: {e}")
    return None