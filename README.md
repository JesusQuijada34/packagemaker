# 📦 Influent Package Maker (IPM)

**Herramienta modular todo-en-uno para crear, empaquetar y gestionar proyectos Influent.**

Influent Package Maker (IPM), diseñado por Jesús Quijada, es un sistema para **simplificar y estandarizar el desarrollo de software distribuible**, con un enfoque en la estética, la compatibilidad multiplataforma y la autonomía del desarrollador.

---

## 🚀 Arquitectura Modular (v3.1.0 - Consolidada)

El proyecto ha sido refactorizado para consolidar las herramientas principales en versiones "Todo en Uno", eliminando la necesidad de múltiples scripts de administración y la lógica de asociación de archivos separada.

| Herramienta | Formato | Interfaz | Responsabilidad Principal |
| :--- | :--- | :--- | :--- |
| **Packagemaker** | `.iflapp` | GUI (PyQt5) & CLI (Terminal) | Creación, construcción y gestión de **Paquetes Normales**. |
| **Bundlemaker** | `.iflappb` | GUI (PyQt5) & CLI (Terminal) | Creación, construcción y gestión de **Bundles Avanzados**. |

---

## 🛠️ Estructura de Paquetes

### Paquete Normal (`.iflapp`)
El formato `.iflapp` mantiene la estructura de proyecto modular de IPM, ideal para aplicaciones completas:
`app/`, `assets/`, `config/`, `docs/`, `lib/`, `source/`, `details.xml`, `LICENSE`, `{nombre}.py`.

### Paquete Bundle (`.iflappb`)
El formato `.iflappb` sigue una estructura más cercana a los paquetes modernos (como AppX o Android Bundles), centrándose en actividades y recursos:
`res/`, `data/`, `code/`, `manifest/manifest.json`, `activity/`, `theme/`, `blob/`, `details.xml`.

---

## 💻 Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **GUI** | Python, `PyQt5` | Interfaz gráfica de usuario para todas las herramientas. |
| **CLI** | Python, `tqdm`, `ANSI` | Interfaz de terminal interactiva con barras de progreso y colores. |
| **Empaquetado** | Python (`zipfile`, `shutil`), `xml.etree.ElementTree`, `json` | Lógica de creación de paquetes `.iflapp` y `.iflappb`. |

---

## 🚀 Instalación y Uso

### Requisitos
Asegúrese de tener **Python 3.10+** instalado.

### Dependencias
Instale las dependencias de Python necesarias:
```bash
pip install -r lib/requirements.txt
```

### Ejecución de Herramientas

La forma recomendada de iniciar la aplicación es a través de los lanzadores:

| Sistema Operativo | Comando de Ejecución | Descripción |
| :--- | :--- | :--- |
| **Linux** | `./launcher.sh` | Abre un menú interactivo para seleccionar la herramienta (GUI o CLI). |
| **Windows** | `launcher.bat` | Abre un menú interactivo para seleccionar la herramienta (GUI o CLI). |

**Ejecución Directa (Python):**

| Herramienta | Interfaz | Comando de Ejecución |
| :--- | :--- | :--- |
| **Packagemaker** | GUI | `python packagemaker.py` |
| **Packagemaker CLI** | Terminal | `python packagemaker-term.py` |
| **Bundlemaker** | GUI | `python bundlemaker.py` |
| **Bundlemaker CLI** | Terminal | `python bundlemaker-term.py` |

**Ejecución Directa (Ejecutables Linux):**

Los ejecutables se encuentran en la carpeta `dist/linux/` y pueden ejecutarse directamente.

---

## 💡 Filosofía y Futuro

IPM se construye sobre la **Legibilidad**, **Modularidad** y **Automatización Inteligente**. La refactorización a la **Arquitectura Modular v3.1.0** consolida las herramientas principales, haciendo el ecosistema más fácil de mantener y expandir.

**¡Contribuya y explore las posibilidades del empaquetado modular!**
Creador: [Jesús Quijada](https://github.com/JesusQuijada34)
Licencia: GNU/MIT.

