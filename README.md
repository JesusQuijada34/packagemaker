# Package Maker

**Identidad del paquete:** `Influent.packagemaker.v3.2.7-26.05-20.13-AlphaCube`
**Autor:** `JesusQuijada34`
**Plataforma:** `AlphaCube`
**Descripción:** Estructura reparada por MoonFix

## Estructura PackageMaker 3.2.7

Este repositorio fue normalizado mediante **MoonFix**, usando la estructura de PackageMaker 3.2.7. El paquete público debe conservar `details.xml`, `version.res`, `autorun`, `autorun.bat`, `.storedetail`, `updater.py`, `config/settings.json`, los marcadores `.container` y los archivos de documentación correspondientes. El publisher conserva la capitalización de `details.xml` (`Influent`) y la versión pública incluye el sufijo canónico de plataforma (`Danenone`, `Knosthalij` o `AlphaCube`).

## Instalación y ejecución

Instala las dependencias declaradas en `lib/requirements.txt` cuando exista y ejecuta el entrypoint real del proyecto. En Linux, los comandos privilegiados son específicos de Danenone y no deben trasladarse a Windows. En proyectos AlphaCube, la validación Windows debe realizarse con el `buildthis` oficial de PackageMaker.

## Validación

La fuente debe pasar compilación sintáctica, pruebas funcionales disponibles, comprobación de identidad XML, protección contra traversal en ZIP y llamadas seguras a subprocess. Los artefactos `.iflapp` deben ser generados por PackageMaker; los paquetes Debian deben usar el nombre canónico `Influent.packagemaker.v3.2.7-26.05-20.13_ARCH.deb`.

## Release

El tag y el título del release deben ser exactamente `v3.2.7-26.05-20.13`. Los assets deben usar el nombre canónico del paquete y una extensión objetiva. No se permite publicar un release AlphaCube que contenga únicamente el build Linux.

## Referencia original

# 📦 Influent Package Maker - IDE Profesional para Python

**Influent Package Maker** es un entorno de desarrollo integrado (IDE) profesional para crear, empaquetar y distribuir aplicaciones Python con interfaces modernas estilo Windows 11.

> **Versión Actual**: v3.2.7-26.05-20.13 - Mejoras en la detección de editores, gestión de compilación y limpieza de artefactos.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5%2B-green)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-GNU%20GPL%20v3-yellow)](LICENSE)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/JesusQuijada34/packagemaker)](https://github.com/JesusQuijada34/packagemaker/releases/latest)
[![GitHub repo size](https://img.shields.io/github/repo-size/JesusQuijada34/packagemaker)](https://github.com/JesusQuijada34/packagemaker)
[![GitHub last commit](https://img.shields.io/github/last-commit/JesusQuijada34/packagemaker)](https://github.com/JesusQuijada34/packagemaker/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/JesusQuijada34/packagemaker?style=social)](https://github.com/JesusQuijada34/packagemaker/stargazers)

---

## 🌟 Características Principales

### 🎨 Interface Moderna Windows 11
- **Barra de título personalizada**: Basada en `Leviathan-UI` con diseño limpio
- **Efectos visuales**: Soporte para acrílico, mica y blur
- **Tema oscuro**: Paleta consistente #3a3f4b (fondo) / #ff5722 (acento)
- **Sin gradientes**: Interfaz limpia y consistente sin gradientes
- **Fondos sólidos**: Optimizados para evitar artifacts visuales

### 📦 Sistema de Compilación Avanzado
- **Detección automática**: Encuentra scripts candidatos (`if __name__ == '__main__'`)
- **Extracción de clases**: Separa automáticamente clases a `lib/_class/`
- **Gestión de dependencias**: Analiza e incluye imports necesarios
- **Minificación**: Reduce tamaño del código compilado
- **Integración con .gitignore**: Excluye automáticamente archivos y carpetas especificadas en `.gitignore` durante la compilación y empaquetado, incluyendo archivos de GitHub como `.github` y `.vscode`.
- **Limpieza Post-Compilación**: Elimina automáticamente los directorios `build/`, `dist/` y los archivos `.spec` generados por PyInstaller después de cada proceso de compilación.
- **Entrega y limpieza segura**: Una vez validado el `.iflapp` generado fuera del directorio fuente, elimina el paquete temporal. Esta protección se aplica a GUI, TUI, `compile`, `--buildthis` y `scripts/build_headless.py`; conserva las fuentes por defecto y solo permite eliminarlas mediante una autorización explícita.

### 🔒 Métodos de Blindado
| Método | Descripción | Seguridad |
|--------|-------------|----------|
| **Simple Blind** | Empaqueta todo en `.iflappb` | 🔒🔒 |
| **Super Blind** | Clases separadas por script + encriptación | 🔒🔒🔒🔒 |

### 📱 Multi-Plataforma
- **Windows**: Ejecutables `.exe` con PyInstaller
- **Android**: APK generable vía Buildozer
- **Linux**: AppImage y paquetes nativos con renderizado de iconos mejorado.

---

## 🎉 Novedades en v3.2.7-26.05-20.13

### 🚀 Mejoras en la Experiencia de Desarrollo

- **Más Editores Soportados**: El diálogo "Abrir con" ahora detecta y permite abrir proyectos con una gama más amplia de editores de código, incluyendo **Zed**, **Fleet**, **Emacs**, **Geany**, **Kate** y **Gedit**. Esto proporciona mayor flexibilidad a los desarrolladores para usar su herramienta preferida.
- **Renderizado de Iconos en Linux**: Se ha mejorado la detección y el renderizado de iconos para editores en entornos Linux (Ubuntu, etc.), asegurando que los iconos se muestren correctamente en el diálogo "Abrir con" y en el sistema.
- **Exclusión de Archivos con .gitignore**: El proceso de compilación ahora respeta el archivo `.gitignore` del proyecto, excluyendo automáticamente los archivos y directorios listados. Esto incluye archivos relacionados con el control de versiones (`.git`, `.github`) y configuraciones de IDE (`.vscode`, `.idea`), evitando que se incluyan en el paquete final.
- **Limpieza Automática de Artefactos de Compilación**: Después de cada compilación y empaquetado, el sistema ahora limpia automáticamente los archivos temporales y directorios generados por PyInstaller (`build/`, `dist/`, `.spec`). Esto se aplica tanto a la compilación a través de la GUI como a las invocaciones por línea de comandos (`compile` y `--buildthis`), garantizando un directorio de proyecto ordenado.

### 🐛 Correcciones y Optimizaciones

- **Error en EditorInfo - TypeError**: Corregido un `TypeError` en `lib/openWithDialog.py` al inicializar `EditorInfo` para `pmCodeEditor`, asegurando que el campo `executable` se pase correctamente.
- **Bug de Fondo Blanco al Maximizar**: Solucionado el problema de fondos blancos al maximizar la ventana, asegurando una consistencia visual con el tema oscuro en todo momento.
- **Iconos de Editores - Gradiente Radial**: Eliminado un gradiente radial innecesario en los iconos de los editores en `lib/openWithDialog.py`, resultando en una apariencia más limpia y moderna.

---

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker

# Instalar dependencias
pip install -r lib/requirements.txt

# Ejecutar IDE
python packagemaker.py
```

### Requisitos
- **Python 3.8+** 🐍
- **PyQt6 6.5+** 🎨
- **Windows 10/11** (Linux/macOS parcial) 💻

---

## 🎯 Uso Básico

### 1️⃣ Crear Nuevo Proyecto
```
Archivo → Nuevo Proyecto → Seleccionar carpeta
```

### 2️⃣ Configurar Compilación
- **Modo Bundle**: Switch para cambiar entre "Empaquetar" y "Compilar Bundle"
- **Método de Blindado**: Simple vs Super Blind
- **Opciones adicionales**: Firma digital, compresión, icono personalizado

### 3️⃣ Compilar
```
Click en "Compilar" (verde) o "Compilar Bundle y Firmar" (azul)
```

### 4️⃣ Distribuir
- Output en `releases/` (o la ruta configurada)
- Listo para subir a GitHub Releases

### Compilar el proyecto actual con `--buildthis`

```bash
python packagemaker.py --buildthis /ruta/al/proyecto
```

El proyecto debe contener `details.xml` y su script principal. La salida se crea en `~/Documents/Packagemaker Projects/Compiled`, salvo que se especifique `--output`. El nombre del directorio y del archivo sigue la convención exacta `Publisher.appname.vX.x[.z]-YY.MM-HH.MM-Platform`, usando `Danenone`, `Knosthalij` o `AlphaCube` como plataforma. El empaquetador respeta `.gitignore`, por lo que excluye `.git`, `.github`, `.vscode` y demás patrones declarados. El proyecto fuente se conserva por defecto; cualquier eliminación requiere autorización explícita del llamador y solo se permite después de validar un `.iflapp` externo.

---

## 🛠️ EditorDetector y OpenWithDialog

### Flujo de Detección Mejorado
El sistema ahora busca ejecutables de editores en rutas estándar de Linux y utiliza un mapeo de nombres para encontrar iconos relevantes, mejorando la experiencia en sistemas operativos basados en Linux.

### Colores y Estilos (lib/openWithDialog.py)

```css
/* Contenedor del diálogo (línea 215-222) */
QFrame {
    background-color: #252526;
    border: none;
    border-radius: 8px;
}

/* Header (línea 228-236) */
background-color: rgba(255, 255, 255, 0.02);
border-bottom: 1px solid rgba(255, 255, 255, 0.08);

/* Item pmCodeEditor seleccionado (línea 524-529) */
background-color: rgba(255, 87, 34, 0.12);
border: 1px solid rgba(255, 87, 34, 0.55);

/* Botones (línea 374-394) */
#0078d4 (background)
#006cbd (hover)
#005a9e (pressed)
```

---

## 🔄 Flujo de Compilación Detallado

Cuando compilas un proyecto, Packagemaker:

1. **Análisis**: Lee scripts candidatos y detecta clases
2. **Exclusión de Archivos**: Aplica patrones de `.gitignore` para ignorar archivos y directorios no deseados.
3. **Extracción**: Mueve clases a `lib/_class/ScriptName/`
4. **Modificación**: Actualiza imports en scripts originales
5. **Generación**: Crea `lib/__init__.py` con imports consolidados
6. **Minificación**: Reduce tamaño de código
7. **Empaquetado**: Genera un archivo `.iflapp` con nombre canónico.
8. **Firma**: Opcionalmente firma el paquete.
9. **Limpieza**: Elimina artefactos de compilación (`build/`, `dist/`, `.spec`), el paquete temporal y, tras validar el `.iflapp` externo, la carpeta de proyecto procesada.

---

## 🤝 Integración con Leviathan-UI

Packagemaker utiliza **Leviathan-UI** como base visual:

| Componente | Uso | Versión |
|------------|-----|----------|
| `CustomTitleBar` | Barra de título unificada | ✅ |
| `WipeWindow` | Efectos visuales consistentes | ✅ |
| `LeviathanProgressBar` | Indicadores de progreso | ✅ |
| `InmersiveSplash` | Pantallas de carga | ✅ |

---

## 📚 Documentación

- `docs/getting-started.md` - Guía de inicio rápido
- `docs/build-system.md` - Sistema de compilación
- `docs/android-deployment.md` - Despliegue Android
- `FAQ.md` - Preguntas frecuentes
- `CHANGELOG.md` - Historial de cambios
- `RELEASE_NOTES.md` - Notas de versión

---

## 📝 Licencia

GNU GPL v3 - Libre para uso personal y comercial.

---

**Desarrollado con ❤️ usando Python + PyQt6 + Leviathan-UI**

[GitHub](https://github.com/JesusQuijada34/packagemaker) | [Issues](https://github.com/JesusQuijada34/packagemaker/issues) | [Releases](https://github.com/JesusQuijada34/packagemaker/releases)
