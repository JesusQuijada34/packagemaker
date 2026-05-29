# 📝 Changelog - Packagemaker

## [3.2.7] - 2026-05-28: Versión de Estabilidad Visual

### 🎨 Mejoras de Interface
- **Eliminación de gradientes**: Removidos todos los gradientes (qlineargradient, qradialgradient) para una apariencia más limpia y consistente
- **Fondos sólidos optimizados**: Cambiados fondos transparentes a color sólido #3a3f4b para evitar el bug de fondo blanco al maximizar
- **Botones transparentes**: Todos los estilos de botones ahora usan fondos transparentes para mejor integración visual
- **Consistencia visual**: Mejorada la consistencia de fondos en todos los widgets y componentes

### 🐛 Correcciones Críticas
- **Bug de fondo blanco al maximizar**: Corregido el problema donde aparecía un área blanca al maximizar la ventana
- **Error en EditorInfo**: Corregido TypeError al crear instancias de EditorInfo faltando el argumento 'executable'
- **Iconos de editores**: Eliminado gradiente radial en iconos por defecto de editores

### 🔧 Optimizaciones
- **Central widget**: Fondo cambiado de transparente a #3a3f4b
- **Content container**: Fondo cambiado de transparente a #3a3f4b
- **Sidebar**: Fondo cambiado de transparente a #3a3f4b
- **Stack**: Fondo cambiado de transparente a #3a3f4b
- **Titlebar**: Fondo cambiado de transparente a #3a3f4b
- **apply_theme**: Base background cambiado de transparente a #3a3f4b

### 📝 Cambios en Código
- **packagemaker.py**: 
  - Eliminados gradientes en BTN_STYLES (default, success, danger, warning, info, best)
  - Cambiados fondos de widgets principales a sólidos
  - Optimizados estilos de QListWidget, QLineEdit, QTextEdit
- **lib/openWithDialog.py**:
  - Corregido error en EditorInfo agregando argumento 'executable'
  - Eliminado gradiente radial en icon_label

---

**Nota de Versión**: v3.2.7 es la versión actual estable lista para uso en producción.

[Ver todos los releases](../../releases)
