"""
Módulo de autenticación para el Buscador de Inubicables.
Maneja login, hash de contraseñas (PBKDF2-SHA256) y persistencia en JSON.
"""

import hashlib
import secrets
import json
from pathlib import Path
from datetime import datetime
import streamlit as st

USERS_FILE = Path(__file__).parent / "users.json"
ITERATIONS = 100_000


# ============================================================
# Hash de contraseñas
# ============================================================

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashea una contraseña usando PBKDF2-HMAC-SHA256.
    Devuelve (hash_hex, salt_hex)."""
    if salt is None:
        salt_bytes = secrets.token_bytes(16)
    else:
        salt_bytes = bytes.fromhex(salt)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, ITERATIONS)
    return dk.hex(), salt_bytes.hex()


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    h, _ = hash_password(password, salt)
    return secrets.compare_digest(h, stored_hash)


# ============================================================
# Persistencia
# ============================================================

def load_users() -> dict:
    # 1) En Streamlit Cloud: usuarios definidos en st.secrets["users"]
    try:
        if hasattr(st, "secrets") and "users" in st.secrets:
            # st.secrets devuelve un AttrDict — convertir a dict normal
            return {k: dict(v) for k, v in st.secrets["users"].items()}
    except Exception:
        pass
    # 2) Local: archivo users.json
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    return {}


def save_users(users: dict) -> None:
    USERS_FILE.write_text(
        json.dumps(users, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def create_user(username: str, password: str, name: str, role: str = "user") -> None:
    users = load_users()
    h, salt = hash_password(password)
    users[username.lower()] = {
        "name": name,
        "role": role,
        "password_hash": h,
        "salt": salt,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_users(users)


def delete_user(username: str) -> bool:
    users = load_users()
    if username.lower() in users:
        del users[username.lower()]
        save_users(users)
        return True
    return False


def authenticate(username: str, password: str) -> dict | None:
    users = load_users()
    user = users.get(username.lower())
    if user and verify_password(password, user["password_hash"], user["salt"]):
        return {
            "username": username.lower(),
            "name": user["name"],
            "role": user.get("role", "user"),
        }
    return None


# ============================================================
# UI de Login
# ============================================================

LOGIN_CSS = """
<style>
/* Esconder chrome de Streamlit */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.block-container { padding-top: 2rem; }

.login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
}
.login-card {
    background: white;
    padding: 36px 40px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(26, 58, 92, 0.15);
    border: 1px solid #e5e7eb;
    width: 100%;
    max-width: 420px;
    text-align: center;
}
.login-logo {
    background: linear-gradient(120deg, #1a3a5c 0%, #2e6db4 100%);
    width: 80px; height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 20px;
    box-shadow: 0 4px 12px rgba(26, 58, 92, 0.3);
}
.login-card h2 {
    color: #1a3a5c;
    margin: 0 0 6px;
    font-size: 1.4rem;
    font-weight: 700;
}
.login-card .subtitle {
    color: #6b7280;
    font-size: 0.85rem;
    margin: 0 0 28px;
}
.login-foot {
    text-align: center;
    color: #9ca3af;
    font-size: 0.7rem;
    margin-top: 20px;
}
</style>
"""

LOGIN_LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 100 100">'
    '<circle cx="41" cy="41" r="23" fill="none" stroke="white" stroke-width="9"/>'
    '<line x1="57" y1="57" x2="77" y2="77" stroke="white" stroke-width="9" stroke-linecap="round"/>'
    '</svg>'
)


def login_screen() -> dict | None:
    """Muestra la pantalla de login. Devuelve el usuario autenticado o None."""

    # Si ya está autenticado, devolver directo
    if st.session_state.get("auth_user"):
        return st.session_state["auth_user"]

    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    # Layout centrado con tres columnas
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.markdown(
            f'<div class="login-wrapper"><div class="login-card">'
            f'<div class="login-logo">{LOGIN_LOGO}</div>'
            f'<h2>Buscador de Inubicables</h2>'
            f'<p class="subtitle">Procuraduría Fiscal</p>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            usuario = st.text_input(
                "Usuario", placeholder="ej: santino",
                autocomplete="username"
            )
            clave = st.text_input(
                "Contraseña", type="password",
                autocomplete="current-password"
            )
            submit = st.form_submit_button(
                "🔐 Iniciar sesión",
                use_container_width=True,
                type="primary",
            )

            if submit:
                if not usuario or not clave:
                    st.error("Completá usuario y contraseña.")
                    return None

                if not USERS_FILE.exists() or len(load_users()) == 0:
                    st.error(
                        "No hay usuarios creados. Pedile al administrador "
                        "que ejecute `python crear_usuario.py`."
                    )
                    return None

                user = authenticate(usuario, clave)
                if user:
                    st.session_state["auth_user"] = user
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
                    return None

        st.markdown(
            '<div class="login-foot">Acceso restringido — uso interno</div>',
            unsafe_allow_html=True,
        )

    return None


def logout():
    """Cierra la sesión actual."""
    for k in ["auth_user", "df_inub", "df_cruce", "relacionados"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def require_login() -> dict:
    """Bloquea la app hasta que haya un usuario autenticado.
    Devuelve el dict del usuario autenticado."""
    user = login_screen()
    if user is None:
        st.stop()
    return user
