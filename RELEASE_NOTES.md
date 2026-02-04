# Release Notes - IPM v3.2.6 "Moonlight Edition"

## Resumen Ejecutivo
La versión **3.2.6** representa el salto más significativo en la madurez del **Influent Package Maker**. No solo optimizamos la creación de aplicaciones, sino que introducimos un guardián de la integridad: **MoonFix**, y expandimos nuestra frontera hacia los dispositivos móviles.

---

## 🛠 Cambios Técnicos Detallados (v3.2.6)

### 1. Sistema MoonFix (Cuerpo de Mantenimiento)
- **Escaneo Heurístico**: Detecta si faltan directorios críticos como `lib/`, `assets/` o `config/`.
- **Validador XML**: Analiza el archivo `details.xml` en busca de etiquetas malformadas o versiones con caracteres prohibidos (ej. "danenone", "knosthalij" en el string de versión).
- **Auto-Fix**: Capacidad de regenerar `README.md`, `LICENSE` y `docs/index.html` automáticamente utilizando plantillas inteligentes.

### 2. Infraestructura Web & Documentación
- **Remote-First Loading**: Se implementó una lógica de carga de activos que prioriza las URLs de GitHub. Esto soluciona problemas de CORS y bloqueos de disco cuando los usuarios previsualizan la documentación localmente.
- **Inyección de Metadatos Dynamica**: El motor de generación de documentación ahora lee el `autor` y el `app_id` del proyecto actual e inyecta estas variables directamente en el JavaScript del frontend generado en `docs/index.html`.

### 3. Interfaz Android (Web-App Replica)
- **Directorio `android/`**: Nueva réplica táctil diseñada para dispositivos móviles.
- **Tecnología**: HTML5/CSS3 con un enfoque en Micro-interacciones.
- **Transiciones**: Sistema de navegación por "vistas" con animaciones de `slide-in` y `exit`.
- **Garantía Visual**: Réplica exacta del esquema de colores e iconos de la versión de escritorio de LeviathanUI.

---

## 🔧 Requisitos del Sistema
- **Desktop**: Windows 10/11 o Linux con soporte para GTK/Qt.
- **Mobile**: Cualquier dispositivo Android capaz de ejecutar un navegador moderno para la vista previa (Chrome 90+ recomendado).
- **Development**: Python 3.9+ es altamente recomendado para la compatibilidad con los nuevos scripts de MoonFix.

## 🤝 Créditos
Liderado por **Jesus Quijada** con el apoyo del motor **FLARM**.
Integración visual por **Leviathan Library**.
