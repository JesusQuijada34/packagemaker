import os
import sys
import ctypes
from PIL import Image, ImageDraw, ImageFont

import difflib

class InmojiTrx:
    """
    ✨ InmojiTrx: Convierte Emojis o Imágenes en iconos reales.
    ¡Ahora con auto-sugerencia de comandos si te equivocas!
    """
    def __getattr__(self, name):
        """Sugerencia de comandos tipo interprete de Python."""
        valid_methods = [m for m in dir(self) if m.startswith('set_') or m in ['save', 'apply']]
        suggestions = difflib.get_close_matches(name, valid_methods)
        
        def error_handler(*args, **kwargs):
            msg = f"❌ Error: El comando '{name}' no existe en InmojiTrx."
            if suggestions:
                msg += f"\n🤔 ¿Quisiste decir: '{suggestions[0]}'? Check it out!"
            raise AttributeError(msg)
        return error_handler

    def __init__(self, source="🐉"):
        self._source = source
        self._output = "app_icon.ico"
        self._size = 256
        self._app_id = None

    def set_source(self, source):
        """Define el emoji o ruta de imagen."""
        self._source = source
        return self

    def set_output(self, path):
        """Define la ruta de guardado del .ico."""
        self._output = path
        return self

    def set_size(self, size):
        """Define el tamaño del icono."""
        self._size = size
        return self

    def set_app_id(self, app_id):
        """Define el AppUserModelID para Windows."""
        self._app_id = app_id
        return self

    def save(self):
        """Genera el archivo .ico y devuelve la ruta."""
        self.generate_ico(self._source, self._output, self._size)
        return self

    def apply(self, obj):
        """Aplica el icono y devuelve el objeto QIcon."""
        return self.apply_to_app(obj, self._source, self._app_id)

    def start(self, obj):
        """Alias de apply()."""
        return self.apply(obj)

    @staticmethod
    def generate_ico(source, output_path="icon.ico", size=256):
        """Genera un ICO de alta calidad con centrado matemático perfecto."""
        # Lienzo transparente 256x256 por defecto para Windows
        canvas = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        
        if os.path.exists(source):
            try:
                img = Image.open(source).convert("RGBA")
                inner_size = int(size * 0.85) # Margen de seguridad del 15%
                img.thumbnail((inner_size, inner_size), Image.Resampling.LANCZOS)
                offset = ((size - img.width) // 2, (size - img.height) // 2)
                canvas.alpha_composite(img, offset)
            except Exception as e:
                print(f"❌ Error cargando imagen: {e}")
                return None
        else:
            # MODO EMOJI: Máxima resolución y centrado
            draw = ImageDraw.Draw(canvas)
            font_paths = ["C:\\Windows\\Fonts\\seguiemj.ttf", "/System/Library/Fonts/Apple Color Emoji.ttc"]
            font = None
            font_size = int(size * 0.75) # 75% del canvas para que no toque los bordes
            
            for path in font_paths:
                if os.path.exists(path):
                    try: font = ImageFont.truetype(path, font_size, encoding="unic"); break
                    except: continue
            if not font: font = ImageFont.load_default()
            
            # Centrado matemático usando el bounding box del glifo
            try:
                # Pillow 9.2.0+ textbbox
                left, top, right, bottom = draw.textbbox((0, 0), source, font=font, embedded_color=True)
                w, h = right - left, bottom - top
                # Ajuste de posición: el anchor por defecto es 'la' (left-ascent)
                x = (size - w) // 2 - left
                y = (size - h) // 2 - top
            except:
                w, h = draw.textsize(source, font=font)
                x, y = (size - w) // 2, (size - h) // 2 - int(size * 0.1)

            draw.text((x, y), source, font=font, embedded_color=True)

        # Exportar con múltiples capas para que Windows escoja la mejor según el tamaño de la barra
        canvas.save(output_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        return os.path.abspath(output_path)

    @staticmethod
    def apply_to_app(obj, source, app_id=None):
        """Aplica el icono a una QApplication o QWidget."""
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication, QWidget
        
        # 1. Registro forzoso de AppID para la barra de tareas
        if sys.platform == "win32":
            if not app_id: 
                app_id = f"leviathan_ui.app.{os.path.basename(sys.argv[0]) or 'default'}"
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p(app_id))
            except: pass
        
        # 2. Generación/Carga del icono con ruta absoluta
        icon_path = source
        if not (os.path.exists(source) and source.lower().endswith(('.ico', '.png'))):
            # Usamos el directorio de la app para el icono temporal
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            temp_ico = os.path.join(base_dir, "app_icon_res.ico")
            icon_path = InmojiTrx.generate_ico(source, temp_ico)
            
        icon = QIcon(icon_path)
        
        # 3. Aplicación dual: a la App y al Widget (indispensable para frameless)
        if isinstance(obj, QApplication):
            obj.setWindowIcon(icon)
        elif isinstance(obj, QWidget):
            obj.setWindowIcon(icon)
            
        return icon

def start_icon(source="🐉"):
    """Iniciador fluido para iconos."""
    return InmojiTrx(source)

# Alias para facilidad de uso
set_app_emoji = InmojiTrx.apply_to_app
