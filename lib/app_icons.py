# -*- coding: utf-8 -*-
"""Iconos SVG a medida para PackageMaker."""

try:
    from PyQt6.QtCore import Qt, QByteArray, QSize
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtGui import QIcon, QPixmap, QPainter
    from PyQt6.QtSvg import QSvgRenderer
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QIcon:
        def __init__(self, *args, **kwargs): pass
    class QPixmap:
        def __init__(self, *args, **kwargs): pass
    class QPushButton:
        def __init__(self, *args, **kwargs): pass

ACCENT = "#ff5722"
ACCENT_LIGHT = "#ff8a65"
WIN_ACCENT = "#0078D4"
MUTED = "#9aa4b2"

ICONS_SVG = {
    "crear": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="{ACCENT}" stroke-width="1.6"/>
  <path d="M12 9v6M9 12h6" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M8 5V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v1" stroke="{MUTED}" stroke-width="1.2"/>
</svg>""",
    "construir": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M4 18h16M7 18l2-9 3 4 2-6 3 11" stroke="{ACCENT}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="5" y="4" width="14" height="3" rx="1" fill="{ACCENT_LIGHT}" opacity="0.35"/>
</svg>""",
    "gestor": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect x="3" y="4" width="8" height="7" rx="1.5" stroke="{ACCENT}" stroke-width="1.5"/>
  <rect x="13" y="4" width="8" height="7" rx="1.5" stroke="{MUTED}" stroke-width="1.5"/>
  <rect x="3" y="13" width="8" height="7" rx="1.5" stroke="{MUTED}" stroke-width="1.5"/>
  <rect x="13" y="13" width="8" height="7" rx="1.5" stroke="{ACCENT}" stroke-width="1.5"/>
</svg>""",
    "config": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <circle cx="12" cy="12" r="3" stroke="white" stroke-width="1.6"/>
  <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4l1.4-1.4M17 7l1.4-1.4" stroke="{ACCENT}" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",
    "moonfix": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M14 4a6 6 0 1 0 6 10.5A8 8 0 1 1 8.5 4 6.5 6.5 0 0 0 14 4z" fill="{ACCENT_LIGHT}" opacity="0.25" stroke="{ACCENT}" stroke-width="1.5"/>
  <path d="M10 14l2 2 4-5" stroke="#7ee787" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "about": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <circle cx="12" cy="12" r="9" stroke="{ACCENT}" stroke-width="1.6"/>
  <path d="M12 10v6M12 7h.01" stroke="white" stroke-width="2" stroke-linecap="round"/>
</svg>""",
    "instalar": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M12 4v10M8 10l4 4 4-4" stroke="{ACCENT}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 18h14" stroke="white" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",
    "desinstalar": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M9 6h6M10 6V5h4v1M7 6l1 13h8l1-13" stroke="#f44336" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 8h14" stroke="{MUTED}" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",
    "refresh": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M20 12a8 8 0 1 1-2.3-5.7M20 4v6h-6" stroke="{WIN_ACCENT}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "open_with": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M14 3h7v7M10 14 21 3" stroke="{WIN_ACCENT}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 12h8M5 8h5M5 16h6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",
    "pmcodeeditor": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect x="3" y="4" width="18" height="16" rx="2" stroke="{WIN_ACCENT}" stroke-width="1.8"/>
  <rect x="3" y="4" width="18" height="5" rx="2" fill="{ACCENT}" opacity="0.85"/>
  <path d="M7 14h4M7 17h7" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
  <circle cx="17" cy="16" r="2" fill="{ACCENT}"/>
</svg>""",
    "folder": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M4 8h16v11H4V8z" stroke="{WIN_ACCENT}" stroke-width="1.6"/>
  <path d="M4 8l2-3h6l2 3" stroke="{ACCENT}" stroke-width="1.6" stroke-linejoin="round"/>
</svg>""",
    "save": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M6 4h10l4 4v13H6V4z" stroke="{WIN_ACCENT}" stroke-width="1.6"/>
  <path d="M8 17h8M8 13h8M8 4v5h8" stroke="white" stroke-width="1.4"/>
  <rect x="8" y="4" width="8" height="5" fill="{ACCENT}" opacity="0.35"/>
</svg>""",
    "language": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <circle cx="12" cy="12" r="9" stroke="{WIN_ACCENT}" stroke-width="1.6"/>
  <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" stroke="{ACCENT}" stroke-width="1.3"/>
</svg>""",
    "restart": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M12 4v3M12 4a8 8 0 1 1-5.7 2.3M12 4L9 7" stroke="#7ee787" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "dpi": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect x="3" y="5" width="18" height="12" rx="2" stroke="{WIN_ACCENT}" stroke-width="1.6"/>
  <path d="M8 15h8M12 9v6" stroke="{ACCENT}" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",
    "palette": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <circle cx="8" cy="10" r="2.5" fill="{ACCENT}"/>
  <circle cx="15" cy="8" r="2.5" fill="{WIN_ACCENT}"/>
  <circle cx="17" cy="15" r="2.5" fill="#7ee787"/>
  <path d="M4 18c2-4 6-6 10-5" stroke="white" stroke-width="1.4"/>
</svg>""",
    "display": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect x="3" y="5" width="18" height="12" rx="2" stroke="{WIN_ACCENT}" stroke-width="1.6"/>
  <path d="M8 20h8" stroke="{ACCENT}" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",
    "touch": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <path d="M12 4v12M9 13l3 3 3-3" stroke="{ACCENT}" stroke-width="1.6" stroke-linecap="round"/>
  <circle cx="12" cy="9" r="3" stroke="white" stroke-width="1.5"/>
</svg>""",
    "blur": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <circle cx="12" cy="12" r="4" fill="{ACCENT}" opacity="0.5"/>
  <circle cx="12" cy="12" r="8" stroke="{WIN_ACCENT}" stroke-width="1.2" opacity="0.5"/>
  <circle cx="12" cy="12" r="10" stroke="{WIN_ACCENT}" stroke-width="1" opacity="0.25"/>
</svg>""",
}


def icon_button(btn, key: str, size: int = 18) -> None:
    """Asigna icono a un QPushButton."""
    btn.setIcon(get_icon(key, size))
    btn.setIconSize(QSize(size, size))


def svg_to_pixmap(svg_data: str, size: int = 24) -> 'QPixmap':
    try:
        renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
    except Exception as e:
        print(f"Warning: Could not create pixmap from SVG: {e}")
        # Retornar un pixmap vacío como fallback
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap


def svg_to_icon(svg_data: str, size: int = 24) -> 'QIcon':
    try:
        return QIcon(svg_to_pixmap(svg_data, size))
    except Exception as e:
        print(f"Warning: Could not create icon from SVG: {e}")
        return QIcon()


def get_sidebar_icon(key: str, size: int = 24) -> 'QIcon':
    svg = ICONS_SVG.get(key, ICONS_SVG["about"])
    return svg_to_icon(svg, size)


def get_icon(key: str, size: int = 24) -> 'QIcon':
    return get_sidebar_icon(key, size)
