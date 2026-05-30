<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/fd69a347-88c6-42ce-a767-68e42c4052d0" />

# 🚀 Notas de Publicación - Packagemaker v3.2.7 Surface Edition

## 🎉 Versión de Estabilidad Visual

Packagemaker v3.2.7 es una actualización importante enfocada en la estabilidad visual y corrección de bugs críticos. Esta versión mejora significativamente la experiencia de usuario con una interfaz más limpia y consistente.

---

## ✨ Novedades Principales

### 🎨 Interface Visual Mejorada
- **Eliminación total de gradientes**: Removidos todos los gradientes (qlineargradient, qradialgradient) para una apariencia más moderna y limpia
- **Fondos sólidos optimizados**: Implementación de color sólido #3a3f4b en todos los widgets principales para evitar el bug de fondo blanco
- **Botones transparentes**: Todos los estilos de botones ahora usan fondos transparentes para mejor integración con el tema oscuro
- **Consistencia visual mejorada**: Unificación de fondos en toda la aplicación para una experiencia más cohesiva

### 🐛 Correcciones Críticas

#### Bug de Fondo Blanco al Maximizar
- **Problema**: Al maximizar la ventana, aparecía un área blanca indeseada en la interfaz
- **Causa**: Fondos transparentes en widgets principales permitían que el fondo blanco predeterminado de Qt se mostrara
- **Solución**: Cambiados todos los fondos de widgets principales a color sólido #3a3f4b
- **Impacto**: Ventana maximizable sin artifacts visuales

#### Error en EditorInfo
- **Problema**: TypeError al abrir proyectos con editor externo
- **Causa**: Falta del argumento 'executable' en instancias de EditorInfo
- **Solución**: Agregado argumento 'executable' en todas las llamadas a EditorInfo
- **Archivos afectados**: lib/openWithDialog.py (líneas 417 y 610)

#### Iconos de Editores
- **Problema**: Gradiente radial en iconos por defecto de editores
- **Solución**: Eliminado gradiente radial, ahora usan fondo transparente
- **Impacto**: Apariencia más limpia y consistente

### 🔧 Optimizaciones Técnicas

#### Widgets Principales
- **Central widget**: Fondo cambiado de transparente a #3a3f4b
- **Content container**: Fondo cambiado de transparente a #3a3f4b
- **Sidebar**: Fondo cambiado de transparente a #3a3f4b
- **Stack**: Fondo cambiado de transparente a #3a3f4b
- **Titlebar**: Fondo cambiado de transparente a #3a3f4b
- **apply_theme**: Base background cambiado de transparente a #3a3f4b

#### Estilos de Componentes
- **BTN_STYLES**: Eliminados gradientes en default, success, danger, warning, info, best
- **QListWidget**: Fondos optimizados para hover y selected
- **QLineEdit**: Fondos transparentes para mejor integración
- **QTextEdit**: Fondos transparentes en todas las instancias
- **QScrollBar**: Handles optimizados

### 📝 Cambios en Código

#### packagemaker.py
- Eliminados gradientes en BTN_STYLES (default, success, danger, warning, info, best)
- Cambiados fondos de widgets principales a sólidos
- Optimizados estilos de QListWidget, QLineEdit, QTextEdit
- Eliminados gradientes en central widget, content_container, sidebar, stack
- Actualizado apply_theme para usar fondo sólido

#### lib/openWithDialog.py
- Corregido error en EditorInfo agregando argumento 'executable' (líneas 417 y 610)
- Eliminado gradiente radial en icon_label

##   Mejoras de Experiencia de Usuario

### Visual
- Interfaz más limpia sin gradientes
- Consistencia de colores en toda la aplicación
- Mejor integración con tema oscuro
- Reducción de distracciones visuales

### Estabilidad
- Eliminación de bugs visuales al maximizar
- Corrección de errores al abrir proyectos
- Mejor manejo de editores externos
- Mayor robustez en la interfaz

---

## 🐛 Bugs Conocidos Resueltos

- ✅ Fondo blanco al maximizar ventana
- ✅ TypeError al abrir proyectos con editor externo
- ✅ Gradientes inconsistentes en botones
- ✅ Fondos transparentes causando artifacts visuales

---

## 📚 Documentación

La documentación ha sido actualizada para reflejar los cambios:
- `CHANGELOG.md` - Historial completo de cambios
- `RELEASE_NOTES.md` - Esta documento
- `README.md` - Guía de inicio actualizada

---

## 🙏 Agradecimientos

Esta versión fue posible gracias a:
- **Comunidad** - Feedback y reportes de bugs
- **Leviathan-UI** - Framework visual base
- **PyQt6** - Bindings Qt para Python
