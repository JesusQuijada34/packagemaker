# Spotify Notifier v2.0

Spotify Notifier es una herramienta de escritorio diseñada para mejorar la experiencia de reproducción de música en Windows, proporcionando notificaciones elegantes y un reproductor minimalista (Workbench) con efectos visuales avanzados.

## Características Principales

El sistema ha sido rediseñado para ofrecer una estabilidad superior y una estética profesional:

| Característica | Descripción |
| :--- | :--- |
| **GhostBlur (Acrylic)** | Efecto de desenfoque nativo de Windows aplicado a las ventanas para una integración visual perfecta con el sistema operativo. |
| **Workbench Nativo** | Un reproductor compacto con controles de reproducción, barra de progreso y visualización de metadatos. |
| **Motor VLC** | Integración de `python-vlc` para una gestión de audio robusta y profesional. |
| **Notificaciones Inteligentes** | Sistema de notificaciones apilables con animaciones suaves y auto-cierre inteligente. |

## Requisitos del Sistema

Para el correcto funcionamiento de Spotify Notifier, se requieren los siguientes componentes:

*   **Python 3.8+**
*   **PyQt5**: Para la interfaz gráfica de usuario.
*   **python-vlc**: Para el motor de reproducción de audio.
*   **VLC Media Player**: Debe estar instalado en el sistema para que la librería `python-vlc` funcione correctamente.
*   **Requests**: Para la descarga de carátulas de álbumes.

## Instalación y Uso

1.  Asegúrate de tener instalado VLC Media Player en tu sistema.
2.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecuta la aplicación principal:
    ```bash
    python src/main.py
    ```

## Estructura del Proyecto

El proyecto mantiene una organización profesional de archivos:

*   `src/`: Contiene el código fuente principal, incluyendo la lógica de la UI y el motor de audio.
*   `src/assets/`: Almacena recursos estáticos como logotipos e iconos.
*   `docs/`: Documentación detallada y registro de cambios (Changelog).

---
*Desarrollado con un enfoque en la robustez y la estética nativa.*
