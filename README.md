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
|--------|-------------|-----------|
| **Simple Blind** | Empaqueta todo en `.iflappb` | 🔒🔒 |
| **Super Blind** | Clases separadas por script + encriptación | 🔒🔒🔒🔒 |

### 📱 Multi-Plataforma
- **Windows**: Ejecutables `.exe` con PyInstaller
- **Android**: APK generable vía Buildozer
- **Linux**: AppImage y paquetes nativos

---

## 🎉 Novedades en v3.2.7

### 🎨 Mejoras Visuales
- **Eliminación de gradientes**: Interfaz más limpia y consistente sin gradientes
- **Fondos sólidos optimizados**: Color #3a3f4b en todos los widgets principales
- **Botones transparentes**: Mejor integración con el tema oscuro
- **Consistencia visual**: Unificación de fondos en toda la aplicación

### 🐛 Correcciones Críticas
- **Bug de fondo blanco al maximizar**: Corregido el problema donde aparecía un área blanca al maximizar
- **Error en EditorInfo**: Corregido TypeError al abrir proyectos con editor externo
- **Iconos de editores**: Eliminado gradiente radial en iconos por defecto

### 🔧 Optimizaciones
- Central widget, content container, sidebar, stack y titlebar con fondos sólidos
- Estilos de QListWidget, QLineEdit, QTextEdit optimizados
- Mejor manejo de editores externos

Para más detalles, ver [CHANGELOG.md](CHANGELOG.md) y [RELEASE_NOTES.md](RELEASE_NOTES.md).

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
- Python 3.8+
- PyQt6 6.5+
- Windows 10/11 (Linux/macOS parcial)

---

## 🎯 Uso Básico

### 1. Crear Nuevo Proyecto
```
Archivo → Nuevo Proyecto → Seleccionar carpeta
```

### 2. Configurar Compilación
- **Modo Bundle**: Switch para cambiar entre "Empaquetar" y "Compilar Bundle"
- **Método de Blindado**: Simple vs Super Blind
- **Opciones adicionales**: Firma digital, compresión, icono personalizado

### 3. Compilar
```
Click en "Compilar" (verde) o "Compilar Bundle y Firmar" (azul)
```

### 4. Distribuir
- Output en `dist/`
- Listo para subir a GitHub Releases

---

## 🛠️ Flujo de Compilación Detallado

Cuando compilas un proyecto, Packagemaker:

1. **Análisis**: Lee scripts candidatos y detecta clases
2. **Extracción**: Mueve clases a `lib/_class/ScriptName/`
3. **Modificación**: Actualiza imports en scripts originales
4. **Generación**: Crea `lib/__init__.py` con imports consolidados
5. **Minificación**: Reduce tamaño de código
6. **Empaquetado**: Genera `.iflappb` (Simple Blind) o estructura separada (Super Blind)
7. **Firma**: Opcionalmente firma el paquete

---

## 🔧 Configuración Avanzada

### manifest.yaml
```yaml
project:
  name: "Mi Aplicación"
  version: "1.0.0"
  author: "Tu Nombre"
  
build:
  mode: "bundle"              # o "standalone"
  blind_method: "simple"      # o "super"
  compress: true
  sign: true
  
android:
  api_level: 33
  permissions:
    - INTERNET
    - STORAGE
```

---

## 🐛 Solución de Problemas

### "No se detectan scripts candidatos"
Asegúrate de que tus scripts tengan el bloque:
```python
if __name__ == '__main__':
    main()
```

### "Error al extraer clases"
Verifica que las clases estén definidas en el nivel superior del archivo, no dentro de funciones.

### "El bundle no ejecuta"
Revisa que `lib/__init__.py` incluya todos los imports necesarios sin duplicados.

---

## 🤝 Integración con Leviathan-UI

Packagemaker utiliza **Leviathan-UI** como base visual:

| Componente | Uso |
|------------|-----|
| `CustomTitleBar` | Barra de título unificada |
| `WipeWindow` | Efectos visuales consistentes |
| `LeviathanProgressBar` | Indicadores de progreso |
| `InmersiveSplash` | Pantallas de carga |

---

## 📚 Documentación

- `docs/getting-started.md` - Guía de inicio rápido
- `docs/build-system.md` - Sistema de compilación
- `docs/android-deployment.md` - Despliegue Android
- `FAQ.md` - Preguntas frecuentes

---

## 📝 Licencia

MIT License - Libre para uso personal y comercial.

---

**Desarrollado con ❤️ usando Python + PyQt6 + Leviathan-UI**

[GitHub](https://github.com/JesusQuijada34/packagemaker) | [Issues](https://github.com/JesusQuijada34/packagemaker/issues) | [Releases](https://github.com/JesusQuijada34/packagemaker/releases)
