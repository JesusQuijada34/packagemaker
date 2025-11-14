# 📦 Packagemaker: Herramienta Modular para Creación y Gestión de Paquetes de Software Distribuible

**Packagemaker** (anteriormente conocido como Influent Package Maker - IPM) es una **herramienta modular todo-en-uno** diseñada para **simplificar y estandarizar el proceso de empaquetado y distribución de software** multiplataforma. Permite a los desarrolladores crear paquetes de aplicación robustos y estéticos, con un enfoque en la compatibilidad y la autonomía.

---

## 🌟 Características Principales

*   **Doble Formato de Paquete:** Soporte para dos estructuras de empaquetado optimizadas:
    *   **Paquete Normal (`.iflapp`):** Ideal para aplicaciones completas y modulares.
    *   **Paquete Bundle (`.iflappb`):** Estructura avanzada centrada en recursos y actividades, similar a formatos modernos como AppX.
*   **Interfaz Dual:** Ofrece una **Interfaz Gráfica de Usuario (GUI)** intuitiva construida con **PyQt5** y una **Interfaz de Línea de Comandos (CLI)** para automatización y uso en terminal.
*   **Multiplataforma:** Diseñado para funcionar de manera consistente en **Linux** y **Windows**, con lanzadores dedicados para cada sistema operativo.
*   **Arquitectura Consolidada:** La versión 3.1.0+ presenta una arquitectura "Todo en Uno" que consolida la lógica de creación y gestión de paquetes, eliminando la necesidad de múltiples scripts externos.

---

## 🚀 Arquitectura Modular (v3.1.0 - Consolidada)

El proyecto ha sido refactorizado para consolidar las herramientas principales en versiones "Todo en Uno", mejorando la mantenibilidad y la experiencia del desarrollador.

| Herramienta | Formato de Salida | Interfaz | Responsabilidad Principal |
| :--- | :--- | :--- | :--- |
| **Packagemaker** | `.iflapp` | GUI (PyQt5) & CLI (Terminal) | Creación, construcción y gestión de **Paquetes Normales**. |
| **Bundlemaker** | `.iflappb` | GUI (PyQt5) & CLI (Terminal) | Creación, construcción y gestión de **Bundles Avanzados**. |

---

## 🛠️ Estructura de Paquetes

### Paquete Normal (`.iflapp`)
El formato `.iflapp` mantiene una estructura de proyecto modular, ideal para aplicaciones completas:
`app/`, `assets/`, `config/`, `docs/`, `lib/`, `source/`, `details.xml`, `LICENSE`, `{nombre}.py`.

### Paquete Bundle (`.iflappb`)
El formato `.iflappb` sigue una estructura más cercana a los paquetes modernos, centrándose en actividades y recursos:
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

La forma recomendada de iniciar la aplicación es a través de los lanzadores, que ofrecen un menú interactivo:

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

---

## 💡 Contribución y Licencia

**Packagemaker** se construye sobre la **Legibilidad**, **Modularidad** y **Automatización Inteligente**. ¡Le invitamos a contribuir y explorar las posibilidades del empaquetado modular!

*   **Creador:** [Jesús Quijada](https://github.com/JesusQuijada34)
*   **Licencia:** GNU/MIT.
*   **Palabras clave SEO:** `packagemaker`, `bundlemaker`, `creación de paquetes`, `distribución de software`, `PyQt5`, `Python`, `aplicaciones multiplataforma`, `iflapp`, `iflappb`.
