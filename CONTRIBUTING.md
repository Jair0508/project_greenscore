# 🛠️ Guía para Desarrolladores — GreenScore

Este documento explica **qué cambió en el repo, por qué, y qué debes hacer tú** para traer esos cambios a tu propia rama sin romper nada. Léelo antes de hacer tu próximo `git pull`.

---

## 🎯 ¿Por qué este documento?

Tuvimos varios dolores de cabeza al mergear ramas:

- Conflictos de merge en archivos `.pyc` (binarios, imposibles de resolver "a mano")
- Riesgo de que cada quien tenga una versión distinta de **Pillow** instalada y le truene algo que a otro no
- Nombres de rama sin un criterio claro (`rama_sebas`, `pam-features`, `pame-feat`...)

Esta guía resuelve eso. Son cambios de **infraestructura del proyecto**, no de funcionalidad — no tocan tu código.

---

## 📋 ¿Qué cambió y por qué?

| Cambio | Problema que resuelve | Qué significa para ti |
|---|---|---|
| ✅ `requirements.txt` | Cada quien tenía la versión de Pillow que se le ocurrió instalar | Instala exactamente lo que dice el archivo, no "lo último" |
| ✅ `.gitignore` | Los `.pyc` de `__pycache__/` se commiteaban y generaban conflictos binarios en cada PR | Esos archivos dejan de aparecer en tu `git status`, es normal |
| ✅ `readme.md` actualizado | No había forma estándar de levantar el proyecto | Sigue los pasos ahí para tu entorno (venv) |
| ✅ Migración a PostgreSQL (Supabase) | Cada quien tenía su propia "base de datos" en archivos `.json` locales — causa de casi todos los conflictos de merge que tuvimos | Ahora todos leen/escriben la **misma base de datos compartida en la nube**. Ver sección de abajo. |

---

## 🔄 Cómo traer estos cambios a TU rama (en orden)

> ⚠️ Haz esto **después de que `jair-features` se mergee a `main`**. Mientras tanto, estos cambios no existen todavía en tu rama ni en `main`.

```bash
# 1. Guarda o commitea lo que tengas pendiente en tu rama ANTES de tocar nada
git status
git add .
git commit -m "wip: mi avance antes de actualizar"

# 2. Trae la info más reciente del remoto
git fetch origin

# 3. Párate en tu propia rama
git checkout tu-rama

# 4. Trae los cambios de main hacia tu rama
git merge origin/main
```

Si te marca conflicto en algún `.pyc` → ignóralo sin pensar, ya no deberían existir después de este merge:
```bash
git rm --cached ruta/al/archivo.pyc
```

### 🧹 Después del merge: limpia lo que ya no se trackea

Los `.pyc` que tenías en tu copia local van a seguir generándose cuando corras Python (eso es normal), pero ya no deben subirse. Si `git status` te los sigue mostrando como "nuevos" en vez de ignorarlos, es porque **Python aún no los regeneró** con la nueva estructura — no te preocupes, en cuanto corras `main.py` otra vez se regeneran y el `.gitignore` los ignora solo.

### 🐍 Instala las dependencias fijas

```bash
pip install -r requirements.txt
```

---

## ⚠️ importante: `.gitignore` NO ignora archivos que YA estaban trackeados

Este es el error más común y confuso con Git. Si un archivo **ya fue commiteado alguna vez**, agregarlo al `.gitignore` **no hace que Git deje de vigilarlo**. Vas a seguir viendo cambios en `git status` como si el `.gitignore` no existiera.

**Solución:** si te pasa con algún archivo que nosotros no hayamos destrackeado ya, avísanos o corre:
```bash
git rm --cached nombre-del-archivo
git commit -m "dejar de trackear nombre-del-archivo"
```
Eso saca el archivo del control de versiones **sin borrarlo de tu disco**. A partir de ahí sí lo ignora.

---

## 🗄️ Base de datos (PostgreSQL en Supabase)

**Los `datos/*.json` ya NO son la base de datos.** Se archivaron en `datos/_archivo/` solo como respaldo histórico — el código ya no los lee ni los escribe. Ahora todo pasa por una base de datos PostgreSQL compartida (gratis, en Supabase), a través del mismo `datos/gestor.py` de siempre (mismas funciones, mismos nombres — tus interfaces no cambian en nada).

**Qué significa esto para ti:**
- ✅ Se acabó el problema de "cada quien con su propio `usuarios.json`" — todos ven los mismos datos en tiempo real.
- ⚠️ **Ahora necesitas internet para correr la app.** Antes podías trabajar sin conexión, ya no.
- ⚠️ Necesitas un archivo `.env` local con las credenciales de conexión (NUNCA se sube a GitHub, ya está en `.gitignore`).

**Setup (una sola vez):**
1. Pídele a Jair las credenciales de la base (host, usuario, contraseña).
2. Copia `.env.example` como `.env` en la raíz del proyecto:
   ```bash
   cp .env.example .env
   ```
3. Completa los valores reales en `.env` (el archivo que te quedó de copiar el ejemplo).
4. Instala las dependencias nuevas (ya están en `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```
5. Corre la app normalmente: `python main.py`

**Si te sale un error de conexión** (`could not translate host name` o similar): probablemente tu red no tiene IPv6. Pídele a Jair la cadena de conexión del **"Session pooler"** de Supabase (no la de "Direct connection") — es compatible con cualquier red.

---

## 🙈 ¿Tienes archivos locales que NO quieres subir, pero tampoco son para todo el equipo?

Con la base de datos en Postgres ya no debería pasarte esto con `datos/*.json` (ya no existen como "base de datos"), pero el consejo sigue siendo útil para cualquier otro archivo de prueba/config personal que no quieras subir.

**No edites el `.gitignore` compartido para esto** — ese archivo es para reglas que aplican a *todo el equipo* (como `__pycache__/`). Si cada quien agrega ahí sus cosas personales, se vuelve un desorden y además generaría conflictos entre ustedes al mergear el propio `.gitignore`.

**La solución correcta es un ignore *local y privado*, que nunca se sube a GitHub:**

```bash
# Edita este archivo (no es .gitignore, y NO se versiona ni se comparte):
notepad .git/info/exclude
```

Agrega ahí la ruta del archivo que quieras ignorar solo tú. Git lo ignorará **solo en tu copia local**, nadie más lo ve, no se pushea, no genera conflictos con el equipo.

> 💡 Recuerda: si el archivo **ya está trackeado**, primero necesitas `git rm --cached` para que el ignore (sea `.gitignore` o `.git/info/exclude`) empiece a funcionar.

---

## 🌿 Convención de nombres de rama (desde ahora)

Usa este formato para que sepamos qué es cada rama de un vistazo:

```
feature/nombre-corto-de-la-funcionalidad
fix/nombre-corto-del-bug
```

Ejemplos:
- `feature/chat-soporte`
- `feature/recuperacion-clave`
- `fix/error-carga-vecino`

---

## ✅ Checklist antes de empezar a programar cada día

- [ ] `git fetch origin`
- [ ] `git merge origin/main` (o `git pull origin main` si estás parado en `main`)
- [ ] `pip install -r requirements.txt` (por si cambió algo)
- [ ] Revisar este archivo si hubo cambios de infraestructura recientes

---

¿Dudas? Pregúntale a Jair antes de forzar algo con `git push --force` o `git reset --hard` 🙏
