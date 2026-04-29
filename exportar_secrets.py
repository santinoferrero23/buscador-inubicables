#!/usr/bin/env python3
"""
Convierte users.json a formato TOML para pegar en Streamlit Cloud.
Uso:  python exportar_secrets.py
"""

import auth
from pathlib import Path


def main():
    users = auth.load_users()
    if not users:
        print("\n  ⚠️  No hay usuarios. Creá al menos uno con: python crear_usuario.py\n")
        return

    print()
    print("═" * 70)
    print("  COPIÁ EL TEXTO DE ABAJO Y PEGALO EN:")
    print("  Streamlit Cloud → App settings → Secrets")
    print("═" * 70)
    print()

    salida = []
    for username, info in users.items():
        salida.append(f"[users.{username}]")
        salida.append(f'name = "{info.get("name", username)}"')
        salida.append(f'role = "{info.get("role", "user")}"')
        salida.append(f'password_hash = "{info["password_hash"]}"')
        salida.append(f'salt = "{info["salt"]}"')
        salida.append("")

    texto = "\n".join(salida)
    print(texto)

    # Guardar también a un archivo local (para tu referencia, NO subir a Git)
    out_file = Path(__file__).parent / ".streamlit" / "secrets.toml"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(texto, encoding="utf-8")

    print("═" * 70)
    print(f"  📄 También se guardó en: {out_file}")
    print(f"  ⚠️  ESTE ARCHIVO YA ESTÁ EN .gitignore — NO subirlo a GitHub")
    print("═" * 70)
    print()


if __name__ == "__main__":
    main()
