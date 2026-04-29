#!/usr/bin/env python3
"""
Crea el ícono y el acceso directo en el escritorio.
Ejecutar UNA sola vez después de instalar la aplicación.

    python crear_acceso_directo.py
"""

import os
import sys
import subprocess
from pathlib import Path

CARPETA = Path(__file__).parent.resolve()


def detectar_escritorio() -> Path:
    """Detecta la carpeta del escritorio, incluyendo el caso de OneDrive."""
    # 1. Preguntarle a Windows directamente vía PowerShell (lo más confiable)
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[Environment]::GetFolderPath('Desktop')"],
            capture_output=True, text=True, timeout=10
        )
        ruta = result.stdout.strip()
        if ruta and Path(ruta).exists():
            return Path(ruta)
    except Exception:
        pass

    # 2. Probar candidatos comunes
    home = Path.home()
    candidatos = [
        home / "OneDrive" / "Escritorio",
        home / "OneDrive" / "Desktop",
        home / "Desktop",
        home / "Escritorio",
    ]
    for c in candidatos:
        if c.exists():
            return c

    return home / "Desktop"


ESCRITORIO = detectar_escritorio()


# ============================================================
# 1. ÍCONO
# ============================================================

def crear_icono() -> Path:
    """Genera logo.ico con una lupa sobre fondo azul."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("  Instalando Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
        from PIL import Image, ImageDraw

    sizes = [256, 128, 64, 48, 32, 16]
    frames = []

    for s in sizes:
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)

        pad = max(2, s // 20)

        # Fondo circular azul oscuro
        d.ellipse([pad, pad, s - pad, s - pad], fill=(26, 58, 92, 255))

        # Lupa — círculo exterior
        cx, cy = int(s * 0.40), int(s * 0.40)
        r  = int(s * 0.245)
        lw = max(2, s // 16)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(255, 255, 255, 255), width=lw)

        # Lupa — reflejo interior
        ri = max(1, int(r * 0.5))
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri],
                  fill=(255, 255, 255, 40))

        # Lupa — mango
        x1 = int(cx + r * 0.68)
        y1 = int(cy + r * 0.68)
        x2 = int(s * 0.84)
        y2 = int(s * 0.84)
        d.line([x1, y1, x2, y2], fill=(255, 255, 255, 255), width=lw)

        frames.append(img)

    ico_path = CARPETA / "logo.ico"
    frames[0].save(
        ico_path, format="ICO",
        append_images=frames[1:],
        sizes=[(s, s) for s in sizes]
    )

    # También guarda PNG para uso en otros contextos
    frames[0].save(CARPETA / "logo.png", format="PNG")

    print(f"  ✅ Ícono guardado en: {ico_path}")
    return ico_path


# ============================================================
# 2. LAUNCHER (VBScript — abre sin ventana de consola)
# ============================================================

def crear_launcher() -> Path:
    """Crea el .bat que lanza Streamlit. Usa rutas absolutas (no depende del PATH)."""

    python_exe = sys.executable
    app_path   = CARPETA / "app_inubicables.py"
    log_path   = CARPETA / "lanzador.log"

    bat_path = CARPETA / "LANZAR_INUBICABLES.bat"
    bat_path.write_text(
        f"@echo off\r\n"
        f"title Buscador de Inubicables\r\n"
        f'cd /d "{CARPETA}"\r\n'
        f"echo Iniciando Buscador de Inubicables...\r\n"
        f"echo (Esperá unos segundos hasta que se abra el navegador)\r\n"
        f"echo.\r\n"
        f'"{python_exe}" -m streamlit run "{app_path}" --browser.gatherUsageStats=false > "{log_path}" 2>&1\r\n'
        f"if errorlevel 1 (\r\n"
        f"    echo.\r\n"
        f"    echo ERROR: revisar el archivo lanzador.log\r\n"
        f"    pause\r\n"
        f")\r\n",
        encoding="utf-8"
    )

    print(f"  ✅ Launcher creado en: {bat_path}")
    print(f"  📝 Python detectado: {python_exe}")
    return bat_path


# ============================================================
# 3. ACCESO DIRECTO EN EL ESCRITORIO
# ============================================================

def crear_acceso_directo(bat_path: Path, ico_path: Path) -> None:
    """Crea el .lnk apuntando DIRECTO a pythonw.exe (sin ventana de consola)."""
    lnk_path = ESCRITORIO / "Inubicables.lnk"
    lnk_path.unlink(missing_ok=True)

    # pythonw.exe corre Python sin abrir consola — ideal para apps GUI/web
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if not pythonw.exists():
        pythonw = Path(sys.executable)  # fallback a python.exe normal

    app_path = CARPETA / "app_inubicables.py"

    ps_path = CARPETA / "_tmp_shortcut.ps1"
    ps_path.write_text(
        f'$ws  = New-Object -ComObject WScript.Shell\r\n'
        f'$lnk = $ws.CreateShortcut("{lnk_path}")\r\n'
        f'$lnk.TargetPath       = "{pythonw}"\r\n'
        f'$lnk.Arguments        = \'-m streamlit run "{app_path}" '
        f'--browser.gatherUsageStats=false --server.headless=false\'\r\n'
        f'$lnk.WorkingDirectory = "{CARPETA}"\r\n'
        f'$lnk.IconLocation     = "{ico_path},0"\r\n'
        f'$lnk.Description      = "Buscador de Inubicables"\r\n'
        f'$lnk.Save()\r\n'
        f'ie4uinit.exe -ClearIconCache 2>$null\r\n',
        encoding="utf-8"
    )

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)],
        capture_output=True, text=True
    )
    ps_path.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"  ✅ Acceso directo creado en: {lnk_path}")
        print(f"  🎯 Apuntando a: {pythonw}")
    else:
        print(f"  ❌ Error al crear acceso directo:")
        print(f"     {result.stderr.strip()}")


# ============================================================
# MAIN
# ============================================================

def verificar_streamlit():
    """Verifica que streamlit esté instalado, si no lo instala."""
    try:
        import streamlit  # noqa: F401
        print("  ✅ Streamlit ya está instalado")
    except ImportError:
        print("  ⚠️  Streamlit no encontrado, instalando...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "streamlit", "pandas", "openpyxl", "-q"]
        )
        print("  ✅ Streamlit instalado")


def configurar_streamlit():
    """Saltea el prompt de bienvenida (email) y desactiva telemetría."""
    config_dir = Path.home() / ".streamlit"
    config_dir.mkdir(exist_ok=True)

    # credentials.toml — saltea el prompt de email
    (config_dir / "credentials.toml").write_text(
        '[general]\nemail = ""\n', encoding="utf-8"
    )

    # config.toml — desactiva telemetría y prompt
    (config_dir / "config.toml").write_text(
        '[browser]\ngatherUsageStats = false\n\n'
        '[global]\ndisableWatchdogWarning = true\n',
        encoding="utf-8"
    )

    print(f"  ✅ Streamlit configurado en: {config_dir}")


def main():
    print()
    print("=" * 60)
    print("  INSTALADOR — BUSCADOR DE INUBICABLES")
    print("=" * 60)

    print("\n[1/4] Verificando dependencias...")
    verificar_streamlit()
    configurar_streamlit()

    print("\n[2/4] Creando ícono...")
    ico_path = crear_icono()

    print("\n[3/4] Creando launcher...")
    vbs_path = crear_launcher()

    print(f"\n[4/4] Creando acceso directo en: {ESCRITORIO}")
    crear_acceso_directo(vbs_path, ico_path)

    print()
    print("=" * 60)
    print("  ✨ ¡Listo!")
    print()
    print("  Encontrá el ícono 'Inubicables' en tu escritorio.")
    print("  Hacé doble clic para abrir la aplicación.")
    print()
    print("  Si la app no abre, usá el archivo:")
    print(f"  {CARPETA / 'LANZAR_INUBICABLES.bat'}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
