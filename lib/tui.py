# -*- coding: utf-8 -*-
"""
TUI — Interfaz de texto para Influent Package Maker.
Funciona en terminales sin display (SSH, CI, WSL sin X).
No requiere dependencias externas más allá de la stdlib.
"""

from __future__ import annotations

import os
import sys
import shutil
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict

# ─── ANSI helpers ────────────────────────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty() and os.name != "nt" or (
    os.name == "nt" and os.environ.get("TERM") is not None
)

# Windows: habilitar VT100 si es posible
if os.name == "nt":
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
        _USE_COLOR = True
    except Exception:
        _USE_COLOR = False


def _c(code: str, text: str) -> str:
    """Envuelve texto con código ANSI si el terminal lo soporta."""
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(t):   return _c("1", t)
def dim(t):    return _c("2", t)
def red(t):    return _c("31", t)
def green(t):  return _c("32", t)
def yellow(t): return _c("33", t)
def blue(t):   return _c("34", t)
def cyan(t):   return _c("36", t)
def white(t):  return _c("37", t)
def orange(t): return _c("38;5;208", t)
def gray(t):   return _c("90", t)

# ─── Layout helpers ───────────────────────────────────────────────────────────

def _cols() -> int:
    """Ancho de la terminal, con fallback a 80."""
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80


def _hr(char: str = "─") -> str:
    return dim(char * min(_cols(), 80))


def _banner() -> None:
    """Cabecera de la app."""
    w = min(_cols(), 80)
    print()
    print(orange("█") * 2 + bold(orange("  Influent Package Maker")) + gray("  v" + _get_version()))
    print(_hr())


def _get_version() -> str:
    details = Path(os.getcwd()) / "details.xml"
    if details.exists():
        try:
            root = ET.parse(details).getroot()
            v = (root.findtext("version") or "").strip().lstrip("v")
            if v:
                return v
        except Exception:
            pass
    return "3.x"


def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _print_menu(title: str, options: List[str], back_label: str = "Volver") -> None:
    """Imprime un menú numerado."""
    print(bold(cyan(f"\n  {title}")))
    print(_hr())
    for i, opt in enumerate(options, 1):
        print(f"  {bold(str(i))}.  {opt}")
    print(f"  {bold('0')}.  {dim(back_label)}")
    print(_hr())


def _prompt(label: str, default: str = "") -> str:
    """Input con prompt coloreado y soporte para valor por defecto."""
    dflt = gray(f"  [{default}]") if default else ""
    try:
        val = input(f"  {cyan('›')} {label}{dflt}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return default
    return val if val else default


def _prompt_bool(label: str, default: bool = True) -> bool:
    hint = gray("S/n" if default else "s/N")
    try:
        val = input(f"  {cyan('›')} {label} [{hint}]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return default
    if val in ("s", "si", "sí", "y", "yes"):
        return True
    if val in ("n", "no"):
        return False
    return default


def _prompt_choice(label: str, choices: List[str], default: int = 0) -> int:
    """Menú inline retorna índice 0-based. default es índice."""
    for i, c in enumerate(choices):
        marker = orange("●") if i == default else gray("○")
        print(f"    {marker} {bold(str(i + 1))}. {c}")
    try:
        raw = input(f"  {cyan('›')} {label} [{default + 1}]: ").strip()
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return idx
    except (ValueError, KeyboardInterrupt, EOFError):
        pass
    return default


def _select_menu(prompt: str) -> int:
    """Lee un número del menú; retorna -1 en error/interrupción."""
    try:
        raw = input(f"\n  {cyan('›')} {prompt}: ").strip()
        return int(raw)
    except (ValueError, KeyboardInterrupt, EOFError):
        return -1


def _ok(msg: str) -> None:
    print(f"\n  {green('✔')} {msg}")


def _err(msg: str) -> None:
    print(f"\n  {red('✖')} {msg}")


def _warn(msg: str) -> None:
    print(f"\n  {yellow('⚠')} {msg}")


def _info(msg: str) -> None:
    print(f"  {blue('ℹ')} {msg}")


def _pause() -> None:
    try:
        input(f"\n  {dim('Presiona Enter para continuar...')}")
    except (KeyboardInterrupt, EOFError):
        pass

# ─── Platform detection ───────────────────────────────────────────────────────

def _detect_platform() -> str:
    """Windows → Knosthalij, Linux → Danenone."""
    if sys.platform.startswith("win"):
        return "Windows"
    return "Linux"


def _base_dir() -> Path:
    if sys.platform.startswith("win"):
        up = os.environ.get("USERPROFILE", "")
        for sub in ("Documentos", "Documents"):
            d = Path(up) / sub
            if d.exists():
                return d / "Packagemaker Projects"
        return Path(up) / "Documents" / "Packagemaker Projects"
    return Path.home() / "Documents" / "Packagemaker Projects"


def _find_python() -> str:
    if getattr(sys, "frozen", False):
        for name in ("python", "python3"):
            exe = shutil.which(name)
            if exe:
                return exe
        return "python"
    return sys.executable


# ─── Live log runner ──────────────────────────────────────────────────────────

def _run_live(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """
    Ejecuta un comando mostrando output en tiempo real con colores.
    Retorna el código de salida.
    """
    import subprocess
    print(_hr("·"))
    print(gray(f"  $ {' '.join(str(c) for c in cmd)}"))
    print(_hr("·"))
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(cwd) if cwd else None,
        )
        for line in proc.stdout:  # type: ignore[union-attr]
            line = line.rstrip()
            if any(tag in line for tag in ("[ERROR]", "Error", "FAILED", "X", "XX")):
                print(f"  {red(line)}")
            elif any(tag in line for tag in ("[OK]", "[INFO]", "OK", "OK", "INFO")):
                print(f"  {green(line)}")
            elif any(tag in line for tag in ("[WARN]", "Warning", "WARN")):
                print(f"  {yellow(line)}")
            else:
                print(f"  {line}")
        proc.wait()
        return proc.returncode
    except FileNotFoundError as exc:
        _err(f"Comando no encontrado: {exc}")
        return 1
    except KeyboardInterrupt:
        _warn("Interrumpido por el usuario.")
        return 130

# ─── Screen: Crear Proyecto ───────────────────────────────────────────────────

def _screen_create() -> None:
    _clear()
    _banner()
    print(bold(white("  Crear Nuevo Proyecto")))
    print(_hr())

    empresa   = _prompt("Empresa / Publisher", "influent")
    slug      = _prompt("ID Interno (Slug)",   "my-app-tool")
    nombre    = _prompt("Nombre Visible",       slug.replace("-", " ").title())
    version   = _prompt("Versión Inicial",      "1.0.0")
    autor     = _prompt("Autor (GitHub User)",  "")
    icon_path = _prompt("Icono (.ico) [opcional]", "")

    print(f"\n  {bold('Plataforma objetivo:')}")
    plat_idx = _prompt_choice("Seleccionar plataforma", [
        "Windows (Knosthalij)",
        "Linux (Danenone)",
        "Multiplataforma (AlphaCube)",
    ], default=0)
    plat_map = {0: "Knosthalij", 1: "Danenone", 2: "AlphaCube"}
    plataforma = plat_map[plat_idx]

    sandbox = _prompt_bool("Sandbox seguro", True)

    print()
    print(_hr())
    print(bold("  Resumen:"))
    _info(f"Publisher : {orange(empresa)}")
    _info(f"Slug      : {orange(slug)}")
    _info(f"Nombre    : {orange(nombre)}")
    _info(f"Versión   : {orange(version)}")
    _info(f"Autor     : {orange(autor) if autor else gray('(sin autor)')}")
    _info(f"Plataforma: {orange(plataforma)}")
    _info(f"Sandbox   : {green('Sí') if sandbox else red('No')}")
    if icon_path:
        _info(f"Icono     : {orange(icon_path)}")
    print(_hr())

    if not _prompt_bool("¿Crear proyecto?", True):
        _warn("Cancelado.")
        _pause()
        return

    if not autor:
        _err("El campo Autor es obligatorio (debe ser un username válido de GitHub).")
        _pause()
        return

    # Construir el comando CLI headless
    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [
        py, str(entry), "create", str(_base_dir()),
        "--name", nombre,
        "--author", autor,
        "--publisher", empresa,
        "--project-version", version,
        "--project-platform", plataforma,
        "--headless",
    ]
    if not sandbox:
        cmd.append("--no-sandbox")

    print()
    rc = _run_live(cmd)
    if rc == 0:
        _ok(f"Proyecto creado en: {_base_dir() / f'{empresa}.{slug}'}")
    else:
        _err(f"Falló con código {rc}")
    _pause()

# ─── Screen: Construir Paquete ────────────────────────────────────────────────

def _screen_build() -> None:
    _clear()
    _banner()
    print(bold(white("  Construir Paquete")))
    print(_hr())

    # Opción: seleccionar proyecto existente o ruta manual
    base = _base_dir()
    projects: List[Path] = []
    if base.exists():
        projects = sorted(
            [p for p in base.iterdir() if p.is_dir() and (p / "details.xml").exists()],
            key=lambda p: p.stat().st_mtime, reverse=True,
        )

    project_path_str = ""
    if projects:
        print(f"\n  {bold('Proyectos recientes:')}")
        display = [p.name for p in projects[:10]]
        display.append("Ingresar ruta manualmente…")
        idx = _prompt_choice("Seleccionar proyecto", display, default=0)
        if idx < len(projects):
            project_path_str = str(projects[idx])
        else:
            project_path_str = _prompt("Ruta al proyecto", "")
    else:
        project_path_str = _prompt("Ruta al proyecto", "")

    if not project_path_str or not Path(project_path_str).exists():
        _err("Ruta de proyecto inválida o no existe.")
        _pause()
        return

    # Leer details.xml para prellenar campos
    details_xml = Path(project_path_str) / "details.xml"
    empresa, nombre, version_val = "influent", "mycoolapp", "1.0"
    if details_xml.exists():
        try:
            root = ET.parse(details_xml).getroot()
            empresa     = root.findtext("publisher") or root.findtext("empresa") or empresa
            nombre      = root.findtext("app") or root.findtext("name") or nombre
            version_val = (root.findtext("version") or version_val).lstrip("v").split("-")[0]
        except Exception:
            pass

    print()
    print(bold("  Datos del paquete:"))
    empresa     = _prompt("Fabricante",      empresa)
    nombre      = _prompt("Nombre interno",  nombre)
    version_val = _prompt("Versión",         version_val)

    detected = _detect_platform()
    _info(f"Entorno de compilación detectado: {orange(detected)}")

    print(f"\n  {bold('Modo de compilación:')}")
    mode_idx = _prompt_choice("Modo", ["Portable (All-in-one)", "Lite (Single File)"], default=0)
    build_mode = "portable" if mode_idx == 0 else "lite"

    output_dir = _prompt("Carpeta de salida", str(Path(project_path_str).parent / "dist"))

    print()
    print(_hr())
    print(bold("  Resumen:"))
    _info(f"Proyecto  : {orange(project_path_str)}")
    _info(f"Fabricante: {orange(empresa)}")
    _info(f"App       : {orange(nombre)}")
    _info(f"Versión   : {orange(version_val)}")
    _info(f"Modo      : {orange(build_mode)}")
    _info(f"Salida    : {orange(output_dir)}")
    _info(f"Plataforma: {orange(detected)}")
    print(_hr())

    if not _prompt_bool("¿Construir paquete?", True):
        _warn("Cancelado.")
        _pause()
        return

    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [
        py, str(entry), "compile", project_path_str,
        "--output", output_dir,
        "--target", detected,
        "--headless",
    ]

    print()
    rc = _run_live(cmd)
    if rc == 0:
        _ok("Paquete construido con éxito.")
    else:
        _err(f"Falló con código {rc}")
    _pause()

# ─── Screen: Gestor de Apps ───────────────────────────────────────────────────

def _screen_manager() -> None:
    _clear()
    _banner()
    print(bold(white("  Gestor de Aplicaciones")))
    print(_hr())

    base = _base_dir()
    if not base.exists():
        _warn(f"Carpeta de proyectos no encontrada: {base}")
        _pause()
        return

    projects = sorted(
        [p for p in base.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime, reverse=True,
    )

    if not projects:
        _warn("No hay proyectos en la carpeta de proyectos.")
        _pause()
        return

    while True:
        _clear()
        _banner()
        print(bold(white("  Gestor de Aplicaciones")))
        print(_hr())
        names = [p.name for p in projects]
        _print_menu("Seleccionar proyecto", names, back_label="Volver al menú principal")
        choice = _select_menu("Opción")

        if choice == 0:
            return
        if not (1 <= choice <= len(projects)):
            continue

        proj = projects[choice - 1]
        _project_actions(proj)

        # Refrescar lista tras posibles cambios
        projects = sorted(
            [p for p in base.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime, reverse=True,
        )


def _project_actions(proj: Path) -> None:
    """Submenú de acciones para un proyecto seleccionado."""
    # Leer metadatos
    meta: Dict[str, str] = {}
    details = proj / "details.xml"
    if details.exists():
        try:
            root = ET.parse(details).getroot()
            meta = {
                "Publisher": root.findtext("publisher") or "",
                "App":       root.findtext("app") or "",
                "Versión":   root.findtext("version") or "",
                "Plataforma":root.findtext("platform") or "",
                "Autor":     root.findtext("author") or root.findtext("autor") or "",
            }
        except Exception:
            pass

    while True:
        _clear()
        _banner()
        print(bold(white(f"  Proyecto: {orange(proj.name)}")))
        print(_hr())
        if meta:
            for k, v in meta.items():
                if v:
                    _info(f"{k:12}: {cyan(v)}")
        print(_hr())
        _print_menu("Acciones", [
            "Compilar / Construir paquete",
            "Reparar con MoonFix",
            "Abrir en explorador de archivos",
            "Ver detalles (details.xml)",
        ], back_label="Volver a la lista de proyectos")
        choice = _select_menu("Opción")

        if choice == 0:
            return
        elif choice == 1:
            _build_project_direct(proj)
        elif choice == 2:
            _moonfix_project_direct(proj)
        elif choice == 3:
            _open_folder(proj)
        elif choice == 4:
            _show_details_xml(proj)


def _build_project_direct(proj: Path) -> None:
    """Lanza compilación sobre un proyecto del gestor."""
    output_dir = str(proj.parent / "dist")
    detected = _detect_platform()
    print()
    _info(f"Compilando {orange(proj.name)} para {orange(detected)}…")
    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [py, str(entry), "compile", str(proj), "--output", output_dir, "--target", detected, "--headless"]
    rc = _run_live(cmd)
    if rc == 0:
        _ok("Paquete construido con éxito.")
    else:
        _err(f"Falló con código {rc}")
    _pause()


def _moonfix_project_direct(proj: Path) -> None:
    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [py, str(entry), "moonfix", str(proj), "--headless",
           "--verify-files", "--update-config", "--repair-structure"]
    print()
    _info(f"Ejecutando MoonFix sobre {orange(proj.name)}…")
    rc = _run_live(cmd)
    if rc == 0:
        _ok("MoonFix completado.")
    else:
        _err(f"Falló con código {rc}")
    _pause()


def _open_folder(proj: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(proj))  # type: ignore[attr-defined]
    elif sys.platform.startswith("linux"):
        os.system(f'xdg-open "{proj}" &')
    else:
        os.system(f'open "{proj}"')
    _ok(f"Abriendo {proj.name}")
    _pause()


def _show_details_xml(proj: Path) -> None:
    details = proj / "details.xml"
    if not details.exists():
        _err("details.xml no encontrado.")
        _pause()
        return
    print(_hr())
    try:
        print(details.read_text(encoding="utf-8"))
    except Exception as e:
        _err(str(e))
    print(_hr())
    _pause()

# ─── Screen: MoonFix ──────────────────────────────────────────────────────────

def _screen_moonfix() -> None:
    _clear()
    _banner()
    print(bold(white("  MoonFix — Reparar Proyecto")))
    print(_hr())

    base = _base_dir()
    projects: List[Path] = []
    if base.exists():
        projects = sorted(
            [p for p in base.iterdir() if p.is_dir()],
            key=lambda p: p.stat().st_mtime, reverse=True,
        )

    project_path_str = ""
    if projects:
        display = [p.name for p in projects[:10]]
        display.append("Ingresar ruta manualmente…")
        idx = _prompt_choice("Seleccionar proyecto a reparar", display, default=0)
        if idx < len(projects):
            project_path_str = str(projects[idx])
        else:
            project_path_str = _prompt("Ruta al proyecto", "")
    else:
        project_path_str = _prompt("Ruta al proyecto", "")

    if not project_path_str or not Path(project_path_str).exists():
        _err("Ruta inválida.")
        _pause()
        return

    print(f"\n  {bold('Opciones de reparación:')}")
    verify    = _prompt_bool("Verificar archivos faltantes",      True)
    update    = _prompt_bool("Actualizar configuraciones antiguas", True)
    repair    = _prompt_bool("Reparar estructura de carpetas",      True)
    check_dep = _prompt_bool("Verificar dependencias",             False)

    print(f"\n  {bold('Plataforma objetivo (dejar vacío = auto):')}")
    plat_idx = _prompt_choice("Plataforma", [
        "Auto (leer desde details.xml)",
        "Windows (Knosthalij)",
        "Linux (Danenone)",
    ], default=0)
    plat_flag = ["", "Windows", "Linux"][plat_idx]

    print()
    if not _prompt_bool("¿Iniciar MoonFix?", True):
        _warn("Cancelado.")
        _pause()
        return

    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [py, str(entry), "moonfix", project_path_str, "--headless"]
    if verify:    cmd.append("--verify-files")
    if update:    cmd.append("--update-config")
    if repair:    cmd.append("--repair-structure")
    if check_dep: cmd.append("--check-deps")
    if plat_flag: cmd += ["--platform", plat_flag]

    rc = _run_live(cmd)
    if rc == 0:
        _ok("MoonFix completado con éxito.")
    else:
        _err(f"Falló con código {rc}")
    _pause()


# ─── Screen: Configuración ────────────────────────────────────────────────────

def _screen_config() -> None:
    _clear()
    _banner()
    print(bold(white("  Configuración")))
    print(_hr())

    # Leer config actual
    try:
        from lib.pm_data import get_pm_data
        store = get_pm_data()
        base_dir = store.get_user("BASE_DIR") or str(_base_dir())
        lang = store.get_user("LANGUAGE") or "es"
    except Exception:
        base_dir = str(_base_dir())
        lang = "es"

    _info(f"Carpeta de proyectos: {cyan(base_dir)}")
    _info(f"Idioma actual        : {cyan(lang)}")
    print(_hr())

    new_base = _prompt("Nueva carpeta de proyectos (Enter = sin cambios)", base_dir)
    lang_idx = _prompt_choice("Idioma", ["Español", "English", "Português"], default=0)
    lang_map = {0: "es", 1: "en", 2: "pt"}
    new_lang = lang_map[lang_idx]

    if not _prompt_bool("¿Guardar cambios?", True):
        _warn("Cancelado.")
        _pause()
        return

    try:
        from lib.pm_data import get_pm_data
        store = get_pm_data()
        store.set_user("BASE_DIR", new_base)
        store.set_user("LANGUAGE", new_lang)
        _ok("Configuración guardada.")
    except Exception as e:
        _err(f"No se pudo guardar: {e}")
    _pause()

# ─── Screen: Acerca de ────────────────────────────────────────────────────────

def _screen_about() -> None:
    _clear()
    _banner()
    print(bold(white("  Acerca de Influent Package Maker")))
    print(_hr())
    _info(f"Versión       : {cyan(_get_version())}")
    _info(f"Sistema       : {cyan(platform.system())} {platform.release()}")
    _info(f"Python        : {cyan(sys.version.split()[0])}")
    _info(f"Directorio    : {cyan(os.getcwd())}")
    _info(f"Proyectos     : {cyan(str(_base_dir()))}")
    print(_hr())
    print(f"  {gray('Influent Package Maker — Sistema de gestión de paquetes Fluthin')}")
    print(f"  {gray('https://github.com/Influent-PackageMaker')}")
    print()
    _pause()


# ─── Menú principal ───────────────────────────────────────────────────────────

_MAIN_MENU = [
    ("Crear Proyecto",        _screen_create),
    ("Construir Paquete",     _screen_build),
    ("Gestor de Aplicaciones",_screen_manager),
    ("MoonFix — Reparar",     _screen_moonfix),
    ("Configuración",         _screen_config),
    ("Acerca de",             _screen_about),
]


def run_tui() -> None:
    """
    Punto de entrada del TUI.
    Llamar desde packagemaker.py cuando se pasa --tui o no hay display.
    """
    while True:
        _clear()
        _banner()
        print(bold(white("  Menú Principal")))
        print(_hr())
        for i, (label, _) in enumerate(_MAIN_MENU, 1):
            print(f"  {bold(orange(str(i)))}  {label}")
        print(f"  {bold('0')}  {dim('Salir')}")
        print(_hr())

        choice = _select_menu("Opción")

        if choice == 0:
            _clear()
            print(f"\n  {orange('Hasta pronto.')}\n")
            sys.exit(0)
        if 1 <= choice <= len(_MAIN_MENU):
            _, fn = _MAIN_MENU[choice - 1]
            try:
                fn()
            except KeyboardInterrupt:
                _warn("Acción cancelada.")
                _pause()
