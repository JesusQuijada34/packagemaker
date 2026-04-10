# 📝 Changelog - Packagemaker

## [1.0.0] - 2026-04-09: IDE Profesional v1.0 Release

### 🎨 Interface Moderna
- **Barra de título unificada**: Integración con `Leviathan-UI` v1.0.5
- **Fondo transparente**: `CustomTitleBar` con `background-color: transparent`
- **Layout responsive**: Adaptación automática a diferentes resoluciones
- **Sidebar mejorado**: Navegación por proyectos con descripciones contextuales

### 📦 Sistema de Compilación v1.0
- **Detección inteligente**: Scripts candidatos con `if __name__ == '__main__'`
- **Extracción de clases**: Automatización completa de separación de código
- **Gestión de imports**: Generación automática de `__init__.py` consolidado
- **Minificación**: Reducción de tamaño de código compilado

### 🔒 Sistema de Blindado
- **Simple Blind**: Empaquetado en archivo `.iflappb` cifrado
- **Super Blind**: Separación por carpetas de script + estructura de bundle avanzada
- **Integridad**: Verificación automática de paquetes

### 🛠️ Mejoras de UX
- **Switches visuales**: Cambio de modo de compilación con animación de color
- **Terminal integrada**: Salida de compilación en tiempo real
- **Indicadores de progreso**: `LeviathanProgressBar` para operaciones largas
- **Validación de entradas**: Prevención de errores antes de compilar

### 🐛 Correcciones
- **TitleBar transparente**: Consistencia visual con `Leviathan-UI`
- **Fondos sólidos**: Eliminados bordes azules de Windows (#121822)
- **Redimensionamiento**: Ventana maximizable sin artifacts visuales
- **Gestión de memoria**: Liberación de recursos al cerrar pestañas

### 📚 Documentación
- README completo con ejemplos
- FAQ con solución de problemas comunes
- Guía de compilación avanzada

---

## [0.9.0] - 2026-03-15: Beta Release

### 🚀 Features Beta
- Sistema de compilación básico
- Detección de proyectos Python
- Integración inicial con Leviathan-UI
- Soporte para Android (experimental)

### 🛠️ Mejoras
- Performance de carga de proyectos
- Cache de análisis de código
- Mejoras en terminal de salida

### 🐛 Bug Fixes
- Corrección de paths en Windows
- Manejo de errores en compilación
- Estabilidad de UI

---

## [0.8.0] - 2026-02-01: Alpha Release

### ✨ Features Iniciales
- IDE básico con PyQt6
- Editor de código integrado
- Navegador de archivos
- Sistema de plugins básico

---

**Nota de Versión**: Esta es la primera versión estable (v1.0.0) lista para uso en producción.

[Ver todos los releases](../../releases)
