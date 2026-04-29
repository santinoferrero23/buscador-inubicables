# 🔍 Buscador de Inubicables

Aplicación web interna de la **Procuraduría Fiscal** para localizar
contactos alternativos de contribuyentes inubicables (sin mail ni teléfono),
cruzando la base de datos municipal por apellido y dirección.

---

## ✨ Características

- 🔐 **Login con contraseña** (PBKDF2-SHA256 + salt único por usuario)
- 👤 **Búsqueda individual** — encontrá una persona y mirá sus relacionados
- 📋 **Procesamiento en lote** — procesá todos los inubicables de una
- 📊 **Estadísticas** — métricas y top deudores
- 📥 **Export Excel** con 20 columnas listas para llamar
- 📂 **Subida de archivos** desde el navegador (no hace falta servidor)

---

## 🚀 Modo de uso

### En la nube (recomendado)
Vía Streamlit Cloud — los usuarios entran a una URL y listo.
Ver instrucciones detalladas en [`DEPLOY.md`](DEPLOY.md).

### Local
```bash
pip install -r requirements.txt
python crear_usuario.py     # crear primer usuario
streamlit run app_inubicables.py
```

---

## 📁 Estructura del proyecto

```
.
├── app_inubicables.py          # App principal (Streamlit)
├── auth.py                     # Login y hash de contraseñas
├── crear_usuario.py            # CLI para crear/borrar/listar usuarios
├── exportar_secrets.py         # Convierte users.json a formato Streamlit Cloud
├── buscador_alternativas.py    # Script standalone de procesamiento
├── crear_acceso_directo.py     # Crea ícono en el escritorio (uso local)
├── requirements.txt            # Dependencias Python
├── .streamlit/
│   ├── config.toml             # Configuración de tema
│   └── secrets.toml.example    # Plantilla de usuarios para deploy
├── README.md                   # Este archivo
└── DEPLOY.md                   # Guía de deployment
```

> ⚠️ Los archivos `users.json`, `*.xlsx` y `.streamlit/secrets.toml`
> están en `.gitignore` y **nunca** se suben al repo.

---

## 🔧 Gestión de usuarios

Crear, listar, cambiar contraseña o borrar usuarios:
```bash
python crear_usuario.py
```

Después de modificar usuarios, regenerar el TOML para Streamlit Cloud:
```bash
python exportar_secrets.py
```

---

## 📋 Flujo de trabajo

1. **Subir** el archivo "detalle total de objetos" (obligatorio)
2. *(Opcional)* Subir el archivo de inubicables
3. **Procesar datos** desde la barra lateral
4. Buscar una persona o **generar relacionados** en lote
5. **Descargar Excel** con todas las relaciones encontradas

### Tipos de relación detectados

| Relación | Confianza | Significado |
|---|---|---|
| Mismo contribuyente | 1.0 | Mismo CUIT en la base |
| Mismo apellido + misma dirección | 0.9 | Familiar conviviente |
| Mismo apellido | 0.7 | Probable familiar |
| Misma dirección | 0.5 | Vecino / colindante |

---

## 🔒 Seguridad

- Contraseñas almacenadas con **PBKDF2-HMAC-SHA256** (100.000 iteraciones, salt único)
- En cloud, las credenciales viven en **Streamlit Secrets** (variables encriptadas)
- El repo no contiene datos sensibles ni archivos Excel reales
- Acceso restringido — solo personas con cuenta pueden entrar

---

## 📞 Soporte

Para reportar problemas o pedir cambios, contactá al administrador del sistema.

---

*Procuraduría Fiscal — Sistema de gestión de inubicables — Uso interno*
