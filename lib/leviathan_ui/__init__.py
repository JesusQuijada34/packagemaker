"""
Leviathan-UI - Framework Premium para PyQt6

Módulos disponibles:
- InmersiveSplash: Pantallas de carga inmersivas
- CustomTitleBar: Barra de título estilo Windows 11
- InmojiTrx: Gestión de iconos y emojis
- WipeWindow: Efectos de ventana (polished, ghost, ghostBlur, mica)
- LightsOff: Efectos de iluminación interactiva
- LeviathanDialog: Diálogos modernos personalizados
- LeviathanProgressBar: Barras de progreso animadas
- LeviScript: Motor de scripting para instaladores
- LeviathanDebugger: Herramientas de depuración
- TouchScreen: Soporte para pantallas táctiles
"""

from .splash import InmersiveSplash
from .title_bar import CustomTitleBar, get_accent_color, is_icon_file
from .inmojiTrx import InmojiTrx, start_icon, set_app_emoji
from .wipeWindow import WipeWindow
from .lightsOff import LightsOff, illuminate_item
from .dialogs import LeviathanDialog
from .progress_bar import LeviathanProgressBar
from .Script import LeviScript, LeviLexer, LeviParser
from .debug import LeviathanDebugger, install_debugger
from .touchscreen import TouchScreen
from .fixLights import FixLights

__version__ = "1.0.5"
__author__ = "Jesus Quijada"
__license__ = "MIT"

__all__ = [
    'InmersiveSplash',
    'CustomTitleBar',
    'get_accent_color',
    'is_icon_file',
    'InmojiTrx',
    'start_icon',
    'set_app_emoji',
    'WipeWindow',
    'LightsOff',
    'illuminate_item',
    'LeviathanDialog',
    'LeviathanProgressBar',
    'LeviScript',
    'LeviLexer',
    'LeviParser',
    'LeviathanDebugger',
    'install_debugger',
    'TouchScreen',
    'FixLights',
]
