# Desglose Técnico: Influent Package Maker (IPM) v3.2.6

## 1. Conceptos Fundamentales
*   **Definición:** Estándar de abstracción y empaquetado para **Influent OS**.
*   **Objetivo:** Transformar scripts de Python en aplicaciones distribuidas profesionales.
*   **Gestión:** Administra dependencias, estructuras de archivos e integridad del sistema.

## 🏗️ Estructura del Proyecto Generado
Cada proyecto creado con IPM sigue una jerarquía estricta para garantizar la compatibilidad y el correcto funcionamiento dentro del ecosistema:

*   **`app/`**: Contiene el núcleo de la lógica y recursos críticos del sistema, incluyendo el icono principal (`app-icon.ico`) que identifica la aplicación en el lanzador.
*   **`assets/`**: Carpeta dedicada al almacenamiento de recursos estáticos como imágenes, sonidos, fuentes y hojas de estilo CSS.
*   **`lib/`**: Directorio de entorno aislado donde se alojan las librerías externas instaladas a través de `requirements.txt`, garantizando que no existan conflictos de dependencias globales.
*   **`config/`**: Espacio reservado para archivos de configuración local (JSON, YAML, etc.), permitiendo que la aplicación mantenga su estado y preferencias de usuario.
*   **`docs/`**: Contiene un `index.html` autogenerado, facilitando la previsualización web y la documentación técnica rápida del proyecto.
*   **`details.xml`**: El cerebro del paquete. Este archivo maestro define los metadatos esenciales: nombre, versión, autor, parámetros de ejecución y el **Correlation ID**.
*   **`[app_name].py`**: El punto de entrada principal (entry point). **Requisito:** El nombre de este archivo debe ser idéntico al ID del paquete para que el cargador de Influent OS lo ejecute correctamente.

## 3. MoonFix: Sistema de Resiliencia y Mantenimiento
Suite integrada para la estabilidad reactiva del software.

*   **Recuperación de Activos:** Sincronización automática con respaldos remotos si fallan los punteros locales.
*   **Reparación de Metadatos:** Reconstrucción de `details.xml` manteniendo el **Correlation ID**.
*   **Limpieza de Distribución:** Eliminación de strings experimentales (ej. "Knosthalij", "Danenone") para asegurar un acabado profesional.

## 4. Capacidades Multiplataforma (Móvil)
*   **Directorio `android/`**: Permite extender la funcionalidad a dispositivos móviles.
*   **Interfaz:** Basada en `android/index.html`.
*   **Casos de Uso:** Monitoreo remoto, paneles de control WebView y gestión de procesos en segundo plano.

## 5. Ciclo de Vida de Compilación (.iflapp)
Flujo de validación en cuatro etapas para generar el binario ejecutable:

1.  **Validación de ID:** Verificación de coincidencia entre el ID interno y el nombre del directorio raíz.
2.  **Empaquetado Portable:** Inclusión de todas las librerías de `/lib` dentro del binario.
3.  **Compilación:** Unificación de scripts y recursos en un único archivo `.iflapp`.
4.  **Firma Digital:** Aplicación de sellos de seguridad para el ecosistema Influent.

## 6. Protocolos de Seguridad y Redundancia

### 6.1. Identidad y Verificación
*   **Correlation ID:** Hash SHA-256 vinculado a la **Fluthin Store**.
*   **Protección:** Bloquea cualquier actualización o inyección de código que no coincida con el hash original.

### 6.2. Continuidad de Servicio (Fallback)
Sistema diseñado para evadir restricciones de acceso a archivos locales en navegadores:
*   **Detección:** Identifica bloqueos de seguridad (CORS/Local Access).
*   **Acción:** Redirección automática al repositorio de GitHub vinculado.
*   **Resultado:** Carga de recursos vía HTTPS para garantizar que la aplicación no se detenga.
