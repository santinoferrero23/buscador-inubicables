#!/usr/bin/env python3
"""
Gestión de usuarios para el Buscador de Inubicables.
Uso:  python crear_usuario.py
"""

import getpass
import sys
import auth


def pedir_password(prompt: str) -> str:
    """Pide una contraseña. Intenta ocultarla; si falla, la muestra."""
    try:
        # Forma normal: oculta lo que tipeás (no se ven asteriscos por diseño)
        return getpass.getpass(prompt)
    except Exception:
        # Fallback: input visible
        print("  (no se pudo ocultar la contraseña, se mostrará en pantalla)")
        return input(prompt)


def listar():
    users = auth.load_users()
    if not users:
        print("\n  (No hay usuarios creados)\n")
        return
    print(f"\n  USUARIOS ({len(users)}):")
    print("  " + "─" * 60)
    for u, info in users.items():
        rol = info.get("role", "user")
        nombre = info.get("name", "-")
        creado = info.get("created_at", "-")[:10]
        print(f"  • {u:<15} {nombre:<25} [{rol}]  {creado}")
    print()


def crear():
    print("\n  Crear nuevo usuario")
    print("  " + "─" * 60)
    usuario = input("  Usuario (sin espacios):  ").strip()
    if not usuario:
        print("  ❌ Cancelado.")
        return

    if usuario.lower() in auth.load_users():
        rep = input(f"  '{usuario}' ya existe. ¿Sobreescribir? [s/N]: ").strip().lower()
        if rep != "s":
            print("  ❌ Cancelado.")
            return

    nombre = input("  Nombre completo:         ").strip() or usuario
    print("  💡 Tip: la contraseña no se muestra mientras la escribís — es normal.")
    while True:
        clave1 = pedir_password("  Contraseña:              ")
        if len(clave1) < 6:
            print("  ⚠️  Mínimo 6 caracteres.")
            continue
        clave2 = pedir_password("  Confirmar contraseña:    ")
        if clave1 != clave2:
            print("  ⚠️  No coinciden, volvé a intentar.")
            continue
        break

    rol = input("  Rol [admin/user] (user): ").strip().lower() or "user"
    if rol not in ("admin", "user"):
        rol = "user"

    auth.create_user(usuario, clave1, nombre, rol)
    print(f"\n  ✅ Usuario '{usuario}' creado correctamente.\n")


def borrar():
    listar()
    usuario = input("  Usuario a borrar:        ").strip()
    if not usuario:
        return
    confirm = input(f"  ¿Confirmás borrar '{usuario}'? [s/N]: ").strip().lower()
    if confirm == "s":
        if auth.delete_user(usuario):
            print(f"  ✅ '{usuario}' borrado.\n")
        else:
            print(f"  ⚠️  '{usuario}' no existe.\n")


def cambiar_clave():
    listar()
    usuario = input("  Usuario:                 ").strip()
    if not usuario or usuario.lower() not in auth.load_users():
        print("  ❌ Usuario no existe.\n")
        return
    print("  💡 Tip: la contraseña no se muestra mientras la escribís — es normal.")
    while True:
        clave1 = pedir_password("  Nueva contraseña:        ")
        if len(clave1) < 6:
            print("  ⚠️  Mínimo 6 caracteres.")
            continue
        clave2 = pedir_password("  Confirmar:               ")
        if clave1 == clave2:
            break
        print("  ⚠️  No coinciden.")

    users = auth.load_users()
    info = users[usuario.lower()]
    auth.create_user(usuario, clave1, info.get("name", usuario), info.get("role", "user"))
    print(f"  ✅ Contraseña actualizada para '{usuario}'.\n")


def main():
    print("\n" + "═" * 64)
    print("  GESTIÓN DE USUARIOS — Buscador de Inubicables")
    print("═" * 64)

    while True:
        print()
        print("  1. Listar usuarios")
        print("  2. Crear usuario")
        print("  3. Cambiar contraseña")
        print("  4. Borrar usuario")
        print("  5. Salir")
        opt = input("\n  Opción: ").strip()

        if opt == "1":
            listar()
        elif opt == "2":
            crear()
        elif opt == "3":
            cambiar_clave()
        elif opt == "4":
            borrar()
        elif opt == "5" or opt == "":
            print("\n  Hasta luego.\n")
            sys.exit(0)
        else:
            print("  ❌ Opción inválida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Cancelado.\n")
        sys.exit(0)
