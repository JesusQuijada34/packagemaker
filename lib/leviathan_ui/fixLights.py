class FixLights:
    """
    🛠️ fixLights: Debugger especializado para el sistema de iluminación.
    Verifica si los widgets tienen efectos aplicados y si las animaciones están listas.
    """
    @staticmethod
    def audit(widget):
        """Revisa la salud visual de un widget."""
        has_effect = widget.graphicsEffect() is not None
        status = "✅ OK" if has_effect else "❌ NO LIGHTS"
        print(f"Audit [{widget.objectName() or 'Widget'}]: {status}")
        return has_effect

    @staticmethod
    def fix_all(app):
        """Intenta reaplicar efectos a todos los hijos de la app si fallan."""
        from .lightsOff import light_up
        for widget in app.allWidgets():
            if not widget.graphicsEffect():
                light_up(widget)
        print("🛠️ fixLights: Iluminación restaurada en todos los controles.")
