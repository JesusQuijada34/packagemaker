"""
Hooks y optimizaciones para PyInstaller en Linux.
Resuelve problemas de "looking for python shared library"
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List


def find_python_shared_library() -> Optional[str]:
    """
    Encuentra la librería compartida de Python en el sistema.
    Esto resuelve el problema de "looking for python shared library".
    """
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Rutas comunes donde buscar libpython
    search_paths = [
        Path(sys.prefix) / "lib",
        Path(sys.prefix) / "lib" / f"python{python_version}",
        Path("/usr/lib"),
        Path("/usr/lib64"),
        Path("/usr/local/lib"),
        Path("/usr/local/lib64"),
        Path("/opt/python/lib"),
    ]
    
    # Agregar ruta específica del venv si está activo
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_lib = Path(sys.prefix) / "lib"
        if venv_lib not in search_paths:
            search_paths.insert(0, venv_lib)
    
    # Agregar rutas multiarch de Debian/Ubuntu
    if sys.platform.startswith("linux"):
        import sysconfig
        try:
            # Obtener la arquitectura multiarch de Debian/Ubuntu
            result = subprocess.run(
                ["dpkg-architecture", "-qDEB_HOST_MULTIARCH"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                multiarch = result.stdout.strip()
                search_paths.insert(0, Path("/usr/lib") / multiarch)
        except Exception:
            pass
    
    # Buscar libpython
    for lib_dir in search_paths:
        if not lib_dir.exists():
            continue
        
        # Buscar .so files
        for pattern in [
            f"libpython{python_version}*.so*",
            f"libpython{python_version}*.so.1*",
            "libpython*.so*",
        ]:
            try:
                matches = list(lib_dir.glob(pattern))
                if matches:
                    # Retornar el primer .so (no symlink)
                    for match in sorted(matches):
                        if match.is_file() and not match.is_symlink():
                            return str(match)
                        elif match.is_symlink():
                            # Si es symlink, intentar resolverlo
                            try:
                                resolved = match.resolve()
                                if resolved.is_file():
                                    return str(resolved)
                            except Exception:
                                pass
            except Exception:
                pass
    
    return None


def get_pyinstaller_linux_optimizations() -> dict:
    """
    Retorna un diccionario con optimizaciones para PyInstaller en Linux.
    """
    return {
        "excluded_modules": [
            "matplotlib",
            "numpy",
            "scipy",
            "pandas",
            "sklearn",
            "tensorflow",
            "torch",
            "keras",
            "IPython",
            "pytest",
            "distutils",
            "setuptools",
            "pip",
            "wheel",
            "virtualenv",
        ],
        "hidden_imports": [
            "PyQt6",
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
        ],
        "collect_data": {
            "PyQt6": "PyQt6",
        }
    }


def get_pyinstaller_args_for_linux() -> List[str]:
    """
    Retorna argumentos adicionales recomendados para PyInstaller en Linux.
    """
    args = [
        "--bootloader-ignore-signals",
        "--noarchive",  # Desactiva archiving para acelerar
    ]
    
    # Buscar libpython y agregarlo como runtime hook
    pylib = find_python_shared_library()
    if pylib:
        args.extend(["--collect-binary", f"{pylib}:_runtime"])
    
    return args


def create_runtime_hooks() -> dict:
    """
    Crea hooks de runtime para resolver problemas de libpython.
    """
    return {
        "rthooks": [
            {
                "name": "rh_libpython.py",
                "content": f"""
# Hook de runtime para libpython
import sys
import os
python_version = f"{{sys.version_info.major}}.{{sys.version_info.minor}}"

# Intentar agregar ruta de libpython
libpython_paths = [
    os.path.join(sys.base_prefix, "lib"),
    "/usr/lib",
    "/usr/lib64",
    "/usr/local/lib",
]

for path in libpython_paths:
    if os.path.exists(path):
        if path not in sys.path:
            sys.path.insert(0, path)
"""
            }
        ]
    }


def ensure_python_dev_libs_installed() -> bool:
    """
    Verifica e intenta instalar python3-dev si es necesario (en sistemas Debian/Ubuntu).
    Retorna True si está disponible.
    """
    if not sys.platform.startswith("linux"):
        return True
    
    # Verificar si ya existe libpython
    if find_python_shared_library():
        return True
    
    # Intentar detectar el gestor de paquetes
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    dev_package = f"python{python_version}-dev"
    
    # Checks para Debian/Ubuntu
    if os.path.exists("/etc/debian_version"):
        try:
            result = subprocess.run(
                ["dpkg", "-l", f"*python{python_version}*"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"[INFO] Instalando {dev_package}...")
                subprocess.run(
                    ["sudo", "apt-get", "install", "-y", dev_package],
                    timeout=60
                )
                return True
        except Exception as e:
            print(f"[WARNING] No se pudo instalar {dev_package}: {e}")
    
    return True
