# GreenScore

Aplicación de escritorio (Tkinter) para gestión de puntos ecológicos: paneles de administrador, negocio y vecino.

## Requisitos

- Python 3.14 (recomendado usar la misma versión entre todo el equipo)
- Pip

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar el entorno virtual
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / Mac

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Ejecutar la aplicación

```bash
python main.py
```

## Notas para el equipo

- No subir cambios en `requirements.txt` sin avisar al equipo (puede romper el entorno de otros).
- Los archivos `__pycache__/` y `*.pyc` ya no se versionan (ver `.gitignore`); si los ves en `git status`, es que tu entorno los sigue generando localmente, es normal e ignorable.
