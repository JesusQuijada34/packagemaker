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
import subprocess
import platform
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict

from lib.projectNameFormatter import ProjectNameFormatter
from lib.i18n import tr
from lib.platform_detect import detect_platform_info
from lib.project_locator import list_projects

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


def _safe_exists(path: Path | str) -> bool:
    """``Path.exists()`` que no propaga ``PermissionError`` (Python 3.13)."""
    try:
        return Path(path).exists()
    except OSError:
        return False


def _banner() -> None:
    """Cabecera de la app."""
    print()
    print(orange("█") * 2 + bold(orange("  Influent Package Maker")) + gray("  v" + _get_version()))
    print(_hr())


def _get_version() -> str:
    details = Path(os.getcwd()) / "details.xml"
    if _safe_exists(details):
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


def _print_menu(title: str, options: List[str], back_label: str = "") -> None:
    back_label = back_label or tr("tui.back")
    """Imprime un menú numerado."""
    print(bold(cyan(f"\n  {title}")))
    print(_hr())
    for i, opt in enumerate(options, 1):
        print(f"  {bold(str(i))}.  {opt}")
    print(f"  {bold('0')}.  {dim(back_label)}")
    print(f"  {dim('q/b')}.  {dim(tr('tui.quit_back'))}")
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


def _select_menu(prompt: str, allow_back: bool = True) -> int:
    """
    Lee un número del menú; retorna -1 en error/interrupción.
    
    Args:
        prompt: Texto del prompt
        allow_back: Si True, permite regresar con 'q', 'b' o '0'
    
    Returns:
        int: Número seleccionado o -1 si se cancela
    """
    back_hint = tr("tui.select_back_hint") if allow_back else ""
    try:
        raw = input(f"\n  {cyan('›')} {prompt}:{back_hint} ").strip().lower()
        if allow_back and raw in ('q', 'b', 'quit', 'back'):
            return -1
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
        input(f"\n  {dim(tr('tui.press_enter'))}")
    except (KeyboardInterrupt, EOFError):
        pass

# ─── Platform detection ───────────────────────────────────────────────────────

def _detect_platform() -> str:
    """Plataforma canonica del detector autoritativo (Knosthalij/Danenone)."""
    return detect_platform_info().platform


def _base_dir() -> Path:
    try:
        return Path(detect_platform_info().base_dir)
    except Exception:
        if sys.platform.startswith("win"):
            up = os.environ.get("USERPROFILE", "")
            for sub in ("Documentos", "Documents"):
                d = Path(up) / sub
                if _safe_exists(d):
                    return d / "Packagemaker Projects"
            return Path(up) / "Documents" / "Packagemaker Projects"
        return Path.home() / "Documents" / "Packagemaker Projects"


def _list_projects(base: Path) -> List[Path]:
    """Proyectos fuente ordenados por fecha, sin artefactos de compilación."""
    try:
        projects = list_projects(base)
    except OSError:
        return []
    stamped = []
    for project in projects:
        try:
            stamped.append((project.stat().st_mtime, project))
        except OSError:
            continue
    stamped.sort(key=lambda item: item[0], reverse=True)
    return [project for _, project in stamped]


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
        _err(tr("tui.command_not_found").format(error=exc))
        return 1
    except KeyboardInterrupt:
        _warn(tr("tui.interrupted"))
        return 130

# ─── Screen: Crear Proyecto ───────────────────────────────────────────────────

def _screen_create() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.create_title"))))
    print(_hr())

    empresa   = _prompt(tr("tui.empresa"), "influent")
    slug      = _prompt(tr("tui.slug"), "my-app-tool")
    nombre    = _prompt(tr("tui.visible_name"), slug.replace("-", " ").title())
    version   = _prompt(tr("tui.initial_version"), "1.0.0")
    autor     = _prompt(tr("tui.author"), "")
    icon_path = _prompt(tr("tui.icon_opt"), "")

    print(f"\n  {bold(tr('tui.target_platform'))}")
    plat_idx = _prompt_choice(tr("tui.select_platform"), [
        tr("tui.platform_windows"),
        tr("tui.platform_linux"),
        tr("tui.platform_multi"),
    ], default=0)
    plat_map = {0: "win", 1: "linux", 2: "all"}
    plataforma = plat_map[plat_idx]

    # Para el resumen visual
    plat_display = {"win": "Knosthalij (Windows)", "linux": "Danenone (Linux)", "all": "AlphaCube (Multi)"}
    plataforma_display = plat_display[plataforma]

    sandbox = _prompt_bool(tr("tui.sandbox_secure"), True)

    print()
    print(_hr())
    print(bold("  " + tr("tui.summary")))
    _info(f"{tr('tui.publisher_col')} : {orange(empresa)}")
    _info(f"{tr('tui.slug_col')}      : {orange(slug)}")
    _info(f"{tr('tui.name_col')}    : {orange(nombre)}")
    _info(f"{tr('tui.version_col')}   : {orange(version)}")
    _info(f"{tr('tui.author_col')}     : {orange(autor) if autor else gray(tr('tui.no_author'))}")
    _info(f"{tr('tui.platform_col')}: {orange(plataforma_display)}")
    _info(f"{tr('tui.sandbox_col')}   : {green(tr('tui.yes')) if sandbox else red(tr('tui.no'))}")
    if icon_path:
        _info(f"{tr('tui.icon_col')}     : {orange(icon_path)}")
    print(_hr())

    if not _prompt_bool(tr("tui.confirm_create"), True):
        _warn(tr("tui.cancelled"))
        _pause()
        return

    if not autor:
        _err(tr("tui.author_required"))
        _pause()
        return

    # Construir el comando CLI headless
    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    cmd = [
        py, str(entry), "create",
        "--name", nombre,
        "--shortname", slug,
        "--author", autor,
        "--publisher", empresa,
        "--version", version,
        "--platform", plataforma,
        "--headless",
    ]

    print()
    rc = _run_live(cmd)
    if rc == 0:
        # Mapear de código técnico a nombre real para la visualización
        real_platform_map = {"win": "Knosthalij", "linux": "Danenone", "all": "AlphaCube"}
        real_platform = real_platform_map.get(plataforma, plataforma)
        
        # El formatter es la única autoridad del nombre: recibe los mismos
        # valores que la CLI (sin reescribir mayúsculas) y la versión se
        # completa con ``normalize_version_base``, porque un ``2`` suelto
        # hacía que ``format_project_folder`` lanzara ValueError y mataba
        # el TUI después de haber creado el proyecto.
        version_base = ProjectNameFormatter.normalize_version_base(version)
        try:
            folder_name = ProjectNameFormatter.format_project_folder(
                empresa, slug, version_base, real_platform
            )
        except ValueError as exc:
            _warn(str(exc))
        else:
            _ok(tr("tui.project_created").format(path=_base_dir() / folder_name))
    else:
        _err(tr("tui.failed_code").format(rc=rc))
    _pause()

# ─── Screen: Construir Paquete ────────────────────────────────────────────────

def _screen_build() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.build_title"))))
    print(_hr())

    # Opción: seleccionar proyecto existente o ruta manual
    base = _base_dir()
    projects: List[Path] = _list_projects(base)

    project_path_str = ""
    manual_mode = False
    if projects:
        print(f"\n  {bold(tr('tui.recent_projects'))}")
        display = [p.name for p in projects[:10]]
        display.append(tr("tui.enter_manual_path"))
        idx = _prompt_choice(tr("tui.select_project"), display, default=0)
        if idx < len(projects):
            project_path_str = str(projects[idx])
        else:
            project_path_str = _prompt(tr("tui.project_path"), "")
            manual_mode = True
    else:
        project_path_str = _prompt(tr("tui.project_path"), "")
        manual_mode = True

    if not project_path_str or not _safe_exists(project_path_str):
        _err(tr("tui.invalid_project_path"))
        _pause()
        return

    # Leer details.xml para obtener metadatos
    details_xml = Path(project_path_str) / "details.xml"
    empresa, nombre, version_val = "influent", "mycoolapp", "1.0"
    if _safe_exists(details_xml):
        try:
            root = ET.parse(details_xml).getroot()
            empresa     = root.findtext("publisher") or root.findtext("empresa") or empresa
            nombre      = root.findtext("app") or root.findtext("name") or nombre
            version_val = (root.findtext("version") or version_val).lstrip("v").split("-")[0]
        except Exception:
            pass

    detected = _detect_platform()

    # Si es modo manual, pedir confirmación de datos
    if manual_mode:
        print()
        print(bold("  " + tr("tui.package_data")))
        empresa     = _prompt(tr("tui.manufacturer"), empresa)
        nombre      = _prompt(tr("tui.internal_name"), nombre)
        version_val = _prompt(tr("tui.version_col"), version_val)

        _info(tr("tui.detected_env").format(env=orange(detected)))

        print(f"\n  {bold(tr('tui.build_mode'))}")
        mode_idx = _prompt_choice(tr("tui.mode"), [tr("tui.mode_portable"), tr("tui.mode_lite")], default=0)
        build_mode = "portable" if mode_idx == 0 else "lite"

        output_dir = _prompt(tr("tui.output_dir"), str(Path(project_path_str).parent / "dist"))

        print()
        print(_hr())
        print(bold("  " + tr("tui.summary")))
        _info(f"{tr('tui.project_col')}  : {orange(project_path_str)}")
        _info(f"{tr('tui.manufacturer_col')}: {orange(empresa)}")
        _info(f"{tr('tui.app_col')}       : {orange(nombre)}")
        _info(f"{tr('tui.version_col')}   : {orange(version_val)}")
        _info(f"{tr('tui.mode_col')}      : {orange(build_mode)}")
        _info(f"{tr('tui.output_col')}    : {orange(output_dir)}")
        _info(f"{tr('tui.platform_col')}: {orange(detected)}")
        print(_hr())

        if not _prompt_bool(tr("tui.confirm_build"), True):
            _warn(tr("tui.cancelled"))
            _pause()
            return
    else:
        # Modo automático: compilar directamente con metadatos del proyecto
        print()
        print(_hr())
        print(bold("  " + tr("tui.compiling_selected")))
        _info(f"{tr('tui.project_col')}  : {orange(Path(project_path_str).name)}")
        _info(f"{tr('tui.manufacturer_col')}: {orange(empresa)}")
        _info(f"{tr('tui.app_col')}       : {orange(nombre)}")
        _info(f"{tr('tui.version_col')}   : {orange(version_val)}")
        _info(f"{tr('tui.platform_col')}: {orange(detected)}")
        print(_hr())
        _info(tr("tui.starting_build"))
        print()

    cmd = _build_project_command(Path(project_path_str))

    rc = _run_live(cmd)
    if rc == 0:
        _ok(tr("tui.build_success"))
    else:
        _err(tr("tui.failed_code").format(rc=rc))
    _pause()

# ─── Screen: Gestor de Apps ───────────────────────────────────────────────────

def _screen_manager() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.manager_title"))))
    print(_hr())

    base = _base_dir()
    if not _safe_exists(base):
        _warn(tr("tui.projects_folder_missing").format(path=base))
        _pause()
        return

    projects = _list_projects(base)

    if not projects:
        _warn(tr("tui.no_projects"))
        _pause()
        return

    while True:
        _clear()
        _banner()
        print(bold(white("  " + tr("tui.manager_title"))))
        print(_hr())
        names = [p.name for p in projects]
        _print_menu(tr("tui.select_project"), names, back_label=tr("tui.back_main_menu"))
        choice = _select_menu(tr("tui.option"), allow_back=True)

        if choice == 0 or choice == -1:
            return
        if not (1 <= choice <= len(projects)):
            continue

        proj = projects[choice - 1]
        _project_actions(proj)

        # Refrescar lista tras posibles cambios
        projects = _list_projects(base)


def _project_actions(proj: Path) -> None:
    """Submenú de acciones para un proyecto seleccionado."""
    # Leer metadatos
    meta: Dict[str, str] = {}
    details = proj / "details.xml"
    if _safe_exists(details):
        try:
            root = ET.parse(details).getroot()
            meta = {
                tr("tui.publisher_col").strip(): root.findtext("publisher") or "",
                tr("tui.app_col").strip():       root.findtext("app") or "",
                tr("tui.version_col").strip():   root.findtext("version") or "",
                tr("tui.platform_col").strip():  root.findtext("platform") or "",
                tr("tui.author_col").strip():    root.findtext("author") or root.findtext("autor") or "",
            }
        except Exception:
            pass

    while True:
        _clear()
        _banner()
        print(bold(white(f"  {tr('tui.project_header')}: {orange(proj.name)}")))
        print(_hr())
        if meta:
            for k, v in meta.items():
                if v:
                    _info(f"{k:12}: {cyan(v)}")
        print(_hr())
        _print_menu(tr("tui.actions"), [
            tr("tui.action_build"),
            tr("tui.action_moonfix"),
            tr("tui.action_open_folder"),
            tr("tui.action_view_details"),
        ], back_label=tr("tui.back_project_list"))
        choice = _select_menu(tr("tui.option"), allow_back=True)

        if choice == 0 or choice == -1:
            return
        elif choice == 1:
            _build_project_direct(proj)
        elif choice == 2:
            _moonfix_project_direct(proj)
        elif choice == 3:
            _open_folder(proj)
        elif choice == 4:
            _show_details_xml(proj)


def _build_project_command(proj: Path, python_exe: Optional[str] = None) -> List[str]:
    """Construye el comando de compilación para un proyecto concreto."""
    py = python_exe or _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"
    return [py, str(entry), "--buildthis", str(proj)]


def _build_project_direct(proj: Path) -> None:
    """Lanza compilación sobre un proyecto del gestor."""
    detected = _detect_platform()
    print()
    _info(tr("tui.compiling_for").format(name=orange(proj.name), platform=orange(detected)))
    cmd = _build_project_command(proj)
    rc = _run_live(cmd)
    if rc == 0:
        _ok(tr("tui.build_success"))
    else:
        _err(tr("tui.failed_code").format(rc=rc))
    _pause()


def _moonfix_project_direct(proj: Path) -> None:
    py = _find_python()
    entry = Path(os.getcwd()) / "packagemaker.py"

    # El CLI de MoonFix selecciona el proyecto desde BASE_DIR usando sus
    # metadatos; no acepta una ruta posicional ni las antiguas opciones de
    # verificación. Construir los argumentos desde details.xml evita reparar
    # accidentalmente otro proyecto con el mismo directorio base.
    metadata = {
        "publisher": "Influent",
        "app": proj.name,
        "name": proj.name,
        "author": "Unknown",
        "version": "1.0.0",
    }
    details = proj / "details.xml"
    try:
        root = ET.parse(details).getroot()
        metadata["publisher"] = (root.findtext("publisher") or root.findtext("empresa") or metadata["publisher"]).strip()
        metadata["app"] = (root.findtext("app") or root.findtext("shortname") or metadata["app"]).strip()
        metadata["name"] = (root.findtext("name") or metadata["name"]).strip()
        metadata["author"] = (root.findtext("author") or root.findtext("autor") or metadata["author"]).strip()
        metadata["version"] = (root.findtext("version") or metadata["version"]).strip()
    except Exception as exc:
        _warn(tr("tui.details_read_failed").format(error=exc))

    cmd = [
        py, str(entry), "--headless", "moonfix",
        "--name", metadata["name"],
        "--shortname", metadata["app"],
        "--publisher", metadata["publisher"],
        "--author", metadata["author"],
        "--version", metadata["version"],
    ]
    print()
    _info(tr("tui.running_moonfix").format(name=orange(proj.name)))
    rc = _run_live(cmd)
    if rc == 0:
        _ok(tr("tui.moonfix_done"))
    else:
        _err(tr("tui.failed_code").format(rc=rc))
    _pause()


def _open_folder(proj: Path) -> None:
    """Abre una carpeta con el explorador nativo sin invocar un shell."""
    try:
        target = str(proj.resolve())
        if sys.platform.startswith("win"):
            os.startfile(target)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", target], close_fds=True)
        else:
            subprocess.Popen(["xdg-open", target], close_fds=True)
    except OSError as exc:
        # Sin abridor instalado (xdg-open ausente en un sistema mínimo) la
        # acción debe avisar, no tumbar la TUI con un traceback.
        _err(f"{tr('manager.open_folder_failed_title')}: {exc}")
        _pause()
        return
    _ok(tr("tui.opening").format(name=proj.name))
    _pause()


def _show_details_xml(proj: Path) -> None:
    details = proj / "details.xml"
    if not _safe_exists(details):
        _err(tr("tui.details_not_found"))
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
    print(bold(white("  " + tr("tui.moonfix_title"))))
    print(_hr())

    base = _base_dir()
    projects: List[Path] = []
    if _safe_exists(base):
        projects = _list_projects(base)

    project_path_str = ""
    if projects:
        display = [p.name for p in projects[:10]]
        display.append(tr("tui.enter_manual_path"))
        idx = _prompt_choice(tr("tui.select_project_repair"), display, default=0)
        if idx < len(projects):
            project_path_str = str(projects[idx])
        else:
            project_path_str = _prompt(tr("tui.project_path"), "")
    else:
        project_path_str = _prompt(tr("tui.project_path"), "")

    if not project_path_str or not _safe_exists(project_path_str):
        _err(tr("tui.invalid_path"))
        _pause()
        return

    print(f"\n  {bold(tr('tui.moonfix_repair_header'))}")
    _info(tr("tui.moonfix_explain"))
    if not _prompt_bool(tr("tui.confirm_moonfix"), True):
        _warn(tr("tui.cancelled"))
        _pause()
        return

    # Reutilizar la misma ruta que usa el gestor de proyectos. La CLI actual
    # recibe metadatos (--name/--shortname/...) y selecciona el proyecto por
    # details.xml; no acepta una ruta posicional ni los antiguos flags de
    # verificación que construía esta pantalla.
    _moonfix_project_direct(Path(project_path_str))


# ─── Screen: Configuración ────────────────────────────────────────────────────

def _screen_config() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.config_title"))))
    print(_hr())

    # Leer config actual
    try:
        from lib.pm_data import get_pm_data
        store = get_pm_data()
        base_dir = store.get_user("base_dir") or str(_base_dir())
        lang = store.get_user("language") or "es"
    except Exception:
        base_dir = str(_base_dir())
        lang = "es"

    _info(tr("tui.projects_folder").format(path=cyan(base_dir)))
    _info(tr("tui.current_language").format(lang=cyan(lang)))
    print(_hr())

    action = _prompt_choice(
        tr("tui.action"),
        [tr("tui.action_edit_config"), tr("tui.action_reset_config")],
        default=0,
    )

    if action == 1:
        if not _prompt_bool(tr("tui.confirm_reset_config"), False):
            _warn(tr("tui.reset_cancelled"))
            _pause()
            return
        try:
            from lib.pm_data import get_pm_data
            if get_pm_data().reset_user_configuration():
                _ok(tr("tui.config_reset_ok"))
            else:
                _err(tr("tui.config_reset_failed"))
        except Exception as e:
            _err(tr("tui.config_reset_failed_detail").format(error=e))
        _pause()
        return

    new_base = _prompt(tr("tui.new_projects_folder"), base_dir)
    try:
        from lib.i18n import get_available_languages

        lang_options = get_available_languages()
    except Exception:
        lang_options = [("es", "Español"), ("en", "English")]
    lang_names = [name for _code, name in lang_options]
    lang_idx = _prompt_choice(tr("tui.language"), lang_names, default=0)
    new_lang = lang_options[lang_idx][0] if 0 <= lang_idx < len(lang_options) else "es"

    if not _prompt_bool(tr("tui.confirm_save"), True):
        _warn(tr("tui.cancelled"))
        _pause()
        return

    try:
        from lib.pm_data import get_pm_data
        store = get_pm_data()
        store.set_user("base_dir", new_base)
        store.set_user("language", new_lang)
        if store.save():
            _ok(tr("tui.config_saved"))
        else:
            _err(tr("tui.config_save_failed"))
    except Exception as e:
        _err(tr("tui.config_save_failed_detail").format(error=e))
    _pause()

# ─── Screen: Acerca de ────────────────────────────────────────────────────────

def _screen_about() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.about_title"))))
    print(_hr())
    _info(f"{tr('tui.about_version')} : {cyan(_get_version())}")
    _info(f"{tr('tui.about_system')} : {cyan(detect_platform_info().platform)} {platform.release()}")
    _info(f"{tr('tui.about_python')} : {cyan(sys.version.split()[0])}")
    _info(f"{tr('tui.about_dir')} : {cyan(os.getcwd())}")
    _info(f"{tr('tui.about_projects')} : {cyan(str(_base_dir()))}")
    print(_hr())
    print(f"  {gray(tr('tui.about_tagline'))}")
    print(f"  {gray('https://github.com/Influent-PackageMaker')}")
    print()
    _pause()


# ─── Screen: Ayuda ───────────────────────────────────────────────────────────

def _screen_help() -> None:
    _clear()
    _banner()
    print(bold(white("  " + tr("tui.help_title"))))
    print(_hr())
    print()
    print(bold(cyan("  " + tr("tui.help_welcome"))))
    print()
    for _line in tr("tui.help_intro").split("\n"):
        print(dim("  " + _line))
    print()
    print(_hr())
    print(bold(cyan("  " + tr("tui.help_menu_options"))))
    print(_hr())
    print()
    for _line in tr("tui.help_body").split("\n"):
        if not _line:
            print()
        elif _line.startswith("  ") and _line.strip()[0].isdigit():
            print(bold(_line))
        else:
            print(_line)
    print()
    _pause()


# ─── Menú principal ───────────────────────────────────────────────────────────

_MAIN_MENU = [
    ("tui.menu_create",  _screen_create),
    ("tui.menu_build",   _screen_build),
    ("tui.menu_manager", _screen_manager),
    ("tui.menu_moonfix", _screen_moonfix),
    ("tui.menu_config",  _screen_config),
    ("tui.menu_about",   _screen_about),
    ("tui.menu_help",    _screen_help),
]


def run_tui() -> None:
    """
    Punto de entrada del TUI.
    Llamar desde packagemaker.py cuando se pasa --tui o no hay display.
    """
    while True:
        _clear()
        _banner()
        print(bold(white("  " + tr("tui.main_menu"))))
        print(_hr())
        for i, (label, _) in enumerate(_MAIN_MENU, 1):
            print(f"  {bold(orange(str(i)))}  {tr(label)}")
        print(f"  {bold('0')}  {dim(tr('tui.exit'))}")
        print(f"  {dim('q')}  {dim(tr('tui.exit_no_confirm'))}")
        print(_hr())

        choice = _select_menu(tr("tui.option"), allow_back=True)

        if choice == 0 or choice == -1:
            _clear()
            print(f"\n  {orange(tr('tui.bye'))}\n")
            sys.exit(0)
        if 1 <= choice <= len(_MAIN_MENU):
            _, fn = _MAIN_MENU[choice - 1]
            try:
                fn()
            except KeyboardInterrupt:
                _warn(tr("tui.action_cancelled"))
                _pause()
