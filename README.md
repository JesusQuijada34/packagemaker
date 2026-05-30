# 📦 Influent Package Maker - IDE Profesional para Python

**Influent Package Maker** es un entorno de desarrollo integrado (IDE) profesional para crear, empaquetar y distribuir aplicaciones Python con interfaces modernas estilo Windows 11.

> **Versión Actual**: v3.2.7 - Versión de Estabilidad Visual con interfaz mejorada y correcciones críticas.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5%2B-green)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-GNU%20GPL%20v3-yellow)](LICENSE)

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

### 🔒 Métodos de Blindado
| Método | Descripción | Seguridad |
|--------|-------------|----------|
| **Simple Blind** | Empaqueta todo en `.iflappb` | 🔒🔒 |
| **Super Blind** | Clases separadas por script + encriptación | 🔒🔒🔒🔒 |

### 📱 Multi-Plataforma
- **Windows**: Ejecutables `.exe` con PyInstaller
- **Android**: APK generable vía Buildozer
- **Linux**: AppImage y paquetes nativos

---

## 🎉 Novedades en v3.2.7

### 🎨 Mejoras Visuales

**EditorListItem Widget (lib/openWithDialog.py líneas 78-183):**
- Icono del editor: 40x40 px con escalado suave (`Qt.AspectRatioMode.KeepAspectRatio`)
- Nombre del editor: Fuente Segoe UI 12px, peso Medium, color blanco
- Indicador "Predeterminado": Etiqueta verde #4CAF50 (línea 134)
- Radio button visual: Círculo de selección interactivo (○/●)
- Estilos de hover y selected integrados (líneas 456-469)

**Cambios en packagemaker.py:**
```python
# Línea ~615-620: Central Widget
self.central.setStyleSheet("background: #3a3f4b;")  # Antes: transparent

# Línea ~640-645: Content Container
self.content_container.setStyleSheet("background: #3a3f4b;")  # Antes: transparent

# Línea ~735-740: Stack
self.stack.setStyleSheet("background: #3a3f4b;")  # Antes: transparent

# Línea ~628-635: Titlebar
self.titlebar.setStyleSheet("background-color: #3a3f4b; border: none;")

# BTN_STYLES - Eliminación de gradientes (línea ~126-194)
BTN_STYLES = {
    'default': (
        "background-color: transparent;"
        "color: rgba(32,33,36,0.96);"
        "border: 1px solid rgba(209,215,224,0.65);"
    ),
    # ... más estilos
}
```

- ✅ **Eliminación de gradientes**: Interfaz más limpia y consistente sin gradientes
- ✅ **Fondos sólidos optimizados**: Color #3a3f4b en todos los widgets principales
- ✅ **Botones transparentes**: Mejor integración con el tema oscuro
- ✅ **Consistencia visual**: Unificación de fondos en toda la aplicación

### 🐛 Correcciones Críticas

**1. Error en EditorInfo - TypeError**
```python
# lib/openWithDialog.py - Línea 417-423 (OpenWithDialog._detect_editors)
# ANTES:
pm_info = EditorInfo(
    name=pm_editor.name,
    display_name=pm_editor.display_name,
    # ❌ FALTA: executable=pm_editor.exe_path
    icon_path=pm_editor.icon_path,
    priority=200,
)

# DESPUÉS:
pm_info = EditorInfo(
    name=pm_editor.name,
    display_name=pm_editor.display_name,
    executable=pm_editor.exe_path,  # ✅ AGREGADO
    icon_path=pm_editor.icon_path,
    priority=200,
)
```

**2. Bug de Fondo Blanco al Maximizar**
- **Causa**: Fondos transparentes permitían que el fondo blanco predeterminado de Qt se mostrara
- **Solución**: Cambiados todos los fondos de widgets principales a color sólido `#3a3f4b`
- **Impacto**: Ventana maximizable sin artifacts visuales

**3. Iconos de Editores - Gradiente Radial**
```python
# lib/openWithDialog.py - Línea 96-99 (EditorListItem._setup_ui)
# ANTES:
self.icon_label.setStyleSheet("""
    background: qradialgradient(...);  # ❌ Gradiente innecesario
    border: none;
""")

# DESPUÉS:
self.icon_label.setStyleSheet("""
    background-color: transparent;  # ✅ Sin gradiente
    border: none;
""")
```

### 🔧 Optimizaciones Técnicas

| Componente | Antes | Después |
|-----------|-------|----------|
| **Central Widget** | transparent | **#3a3f4b** |
| **Content Container** | transparent | **#3a3f4b** |
| **Sidebar** | transparent | **transparent + border** |
| **Stack** | transparent | **#3a3f4b** |
| **Titlebar** | transparent | **#3a3f4b** |

---

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker

# Instalar dependencias
pip install -r requirements.txt

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
- Output en `dist/`
- Listo para subir a GitHub Releases

---

## 🛠️ EditorDetector y OpenWithDialog

### Flujo de Detección (lib/openWithDialog.py líneas 28-75)

```python
class PackageMakerEditor:
    """Editor integrado pmCodeEditor (siempre disponible)."""
    
    def __init__(self):
        self.name = "pmcodeeditor"
        self.display_name = "pmCodeEditor"
        self.icon_path = self._find_icon()
        self.exe_path = self._find_executable()
    
    def _find_icon(self) -> str:
        """Busca el icono del editor en la carpeta app/."""
        possible_paths = [
            Path(__file__).parent.parent / "app" / "pmCodeEditor-icon.ico",
            Path(__file__).parent.parent / "assets" / "pmCodeEditor-icon.ico",
            Path(__file__).parent.parent / "pmCodeEditor-icon.ico",
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return ""
```

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
2. **Extracción**: Mueve clases a `lib/_class/ScriptName/`
3. **Modificación**: Actualiza imports en scripts originales
4. **Generación**: Crea `lib/__init__.py` con imports consolidados
5. **Minificación**: Reduce tamaño de código
6. **Empaquetado**: Genera `.iflappb` (Simple Blind) o estructura separada (Super Blind)
7. **Firma**: Opcionalmente firma el paquete

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