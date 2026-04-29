# Deploy a Streamlit Cloud

Guía paso a paso para que la app esté disponible online en una URL pública
(tipo `https://procuradoria-inubicables.streamlit.app`) y tus compañeros
puedan usarla desde sus casas.

---

## ⏱️ Tiempo estimado: 30 minutos

## Lo que vas a necesitar

- Cuenta de **GitHub** (gratis): https://github.com/signup
- Cuenta de **Streamlit Cloud** (gratis, con tu GitHub): https://share.streamlit.io
- Git instalado en tu compu: https://git-scm.com/download/win

---

## PASO 1 — Crear los usuarios localmente

Antes de subir, creá los usuarios de tus compañeros:

```powershell
python crear_usuario.py
```

Creá uno por compañero. Después generá el TOML de secrets:

```powershell
python exportar_secrets.py
```

Copiá la salida (el texto que empieza con `[users.santino]`...). **Lo vas
a necesitar más adelante.**

---

## PASO 2 — Crear el repo en GitHub

1. Andá a https://github.com/new
2. Nombre del repo: **`buscador-inubicables`** (o el que prefieras)
3. Marcalo como **Privado** (para que no lo vea cualquiera)
4. **No marques** "Add a README" (ya tenemos uno)
5. Hacé clic en **Create repository**

GitHub te va a mostrar la URL del repo, algo como:
`https://github.com/tu-usuario/buscador-inubicables.git`

---

## PASO 3 — Subir el código

Abrí PowerShell en la carpeta `outputs` y ejecutá:

```powershell
git init
git add app_inubicables.py auth.py crear_usuario.py exportar_secrets.py
git add buscador_alternativas.py crear_acceso_directo.py
git add requirements.txt .gitignore .streamlit/config.toml .streamlit/secrets.toml.example
git add DEPLOY.md README.md
git commit -m "Versión inicial — Buscador de Inubicables"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/buscador-inubicables.git
git push -u origin main
```

Reemplazá `TU-USUARIO` por tu usuario de GitHub.

> ⚠️ **Antes de pushear**, asegurate de que `users.json` y los `.xlsx` NO
> aparezcan en `git status`. Si aparecen, revisá `.gitignore`.

---

## PASO 4 — Conectar con Streamlit Cloud

1. Andá a https://share.streamlit.io
2. Iniciá sesión con tu cuenta de GitHub
3. Hacé clic en **"New app"**
4. Completá:
   - **Repository**: `tu-usuario/buscador-inubicables`
   - **Branch**: `main`
   - **Main file path**: `app_inubicables.py`
   - **App URL** (custom): elegí algo tipo `procuradoria-inubicables`
5. Hacé clic en **"Advanced settings"** → **"Secrets"**
6. **Pegá el contenido del paso 1** (el output de `exportar_secrets.py`)
7. Hacé clic en **Deploy!**

Esperá 2-3 minutos. Cuando termine, vas a tener la URL final:
**`https://procuradoria-inubicables.streamlit.app`**

---

## PASO 5 — Compartir con tus compañeros

Mandales un mensaje con:

```
🔍 Buscador de Inubicables — Procuraduría Fiscal

Link:    https://procuradoria-inubicables.streamlit.app
Usuario: [el que les creaste]
Clave:   [la que les pasaste por canal seguro]

Cualquier duda, escribime.
```

---

## 🔄 Actualizar la app más adelante

Cuando hagas cambios al código:

```powershell
git add .
git commit -m "Descripción del cambio"
git push
```

Streamlit Cloud detecta el push y redespliega automáticamente en ~2 minutos.

## 👥 Agregar / borrar usuarios después

1. Ejecutá `python crear_usuario.py` localmente para agregar
2. Ejecutá `python exportar_secrets.py` para regenerar el TOML
3. Andá a Streamlit Cloud → tu app → **⚙ Settings → Secrets**
4. Reemplazá el TOML viejo por el nuevo
5. Streamlit recarga la app automáticamente

---

## ❓ Problemas comunes

**"My app is sleeping"**
> Streamlit Cloud Free duerme la app después de varios días sin uso. La
> primera persona que entre la despierta (~30 segundos). Para que no se
> duerma, podés pasarte a Streamlit Cloud Pro (10 USD/mes).

**"Permission denied" al hacer git push**
> Configurá un Personal Access Token en GitHub:
> Settings → Developer settings → Personal access tokens → Generate new token

**Los compañeros no pueden entrar**
> Verificá: (1) que les pasaste el usuario correcto en minúsculas,
> (2) que el TOML de secrets esté bien copiado, (3) que la app esté
> "Running" (verde) en Streamlit Cloud.
