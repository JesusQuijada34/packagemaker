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

ACCENT = "#ffffff"
ACCENT_LIGHT = "#ff8a65"
WIN_ACCENT = "#0078D4"
MUTED = "#9aa4b2"

ICONS_SVG = {
    "crear": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6 12H12M18 12H12M12 12V6M12 12V18" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "construir": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M20 5.99999L20 18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V6C4 4.89543 4.89543 4 6 4H18C19.1045 4 19.9999 4.89543 20 5.99999Z" stroke="{ACCENT}"   stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 9V4" stroke="{ACCENT}"   stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "gestor": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 11V4.6C2 4.26863 2.26863 4 2.6 4H8.77805C8.92127 4 9.05977 4.05124 9.16852 4.14445L12.3315 6.85555C12.4402 6.94876 12.5787 7 12.722 7H21.4C21.7314 7 22 7.26863 22 7.6V11M2 11V19.4C2 19.7314 2.26863 20 2.6 20H21.4C21.7314 20 22 19.7314 22 19.4V11M2 11H22" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "config": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19.6224 10.3954L18.5247 7.7448L20 6L18 4L16.2647 5.48295L13.5578 4.36974L12.9353 2H10.981L10.3491 4.40113L7.70441 5.51596L6 4L4 6L5.45337 7.78885L4.3725 10.4463L2 11V13L4.40111 13.6555L5.51575 16.2997L4 18L6 20L7.79116 18.5403L10.397 19.6123L11 22H13L13.6045 19.6132L16.2551 18.5155C16.6969 18.8313 18 20 18 20L20 18L18.5159 16.2494L19.6139 13.598L21.9999 12.9772L22 11L19.6224 10.3954Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "moonfix": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="12" cy="12" r="10" stroke="{ACCENT}" stroke-width="1.5"/>
<path d="M7.63262 3.06689C8.98567 3.35733 9.99999 4.56025 9.99999 6.00007C9.99999 7.65693 8.65685 9.00007 6.99999 9.00007C5.4512 9.00007 4.17653 7.82641 4.01685 6.31997" stroke="{ACCENT}" stroke-width="1.5"/>
<path d="M22 13.0505C21.3647 12.4022 20.4793 12 19.5 12C17.567 12 16 13.567 16 15.5C16 17.2632 17.3039 18.7219 19 18.9646" stroke="{ACCENT}" stroke-width="1.5"/>
<path d="M14.5 8.51L14.51 8.49889" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M10 17C11.1046 17 12 16.1046 12 15C12 13.8954 11.1046 13 10 13C8.89543 13 8 13.8954 8 15C8 16.1046 8.89543 17 10 17Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "about": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 11.5V16.5" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 7.51L12.01 7.49889" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "instalar": f"""<svg width="100" height="100" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11 16L11 11L3 11" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 8H15V10" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M15 18L15 21" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 19V21" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 3V6" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 15H15L15 13" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 9V11" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 3.6V20.4C21 20.7314 20.7314 21 20.4 21H3.6C3.26863 21 3 20.7314 3 20.4V3.6C3 3.26863 3.26863 3 3.6 3H20.4C20.7314 3 21 3.26863 21 3.6Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "desinstalar": f"""<svg width="64" height="64" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M20 9L18.005 20.3463C17.8369 21.3026 17.0062 22 16.0353 22H7.96474C6.99379 22 6.1631 21.3026 5.99496 20.3463L4 9" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 6L15.375 6M3 6L8.625 6M8.625 6V4C8.625 2.89543 9.52043 2 10.625 2H13.375C14.4796 2 15.375 2.89543 15.375 4V6M8.625 6L15.375 6" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "download": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 3V15" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M7 10L12 15L17 10" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M4 17V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V17" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "refresh": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M21.8883 13.5C21.1645 18.3113 17.013 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C16.1006 2 19.6248 4.46819 21.1679 8" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M17 8H21.4C21.7314 8 22 7.73137 22 7.4V3" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "open_with": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8 21H20.4C20.7314 21 21 20.7314 21 20.4V3.6C21 3.26863 20.7314 3 20.4 3H3.6C3.26863 3 3 3.26863 3 3.6V16" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M3.5 20.5L12 12M12 12V16M12 12H8" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "pmcodeeditor": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3 21L12 21H21" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12.2218 5.82839L15.0503 2.99996L20 7.94971L17.1716 10.7781M12.2218 5.82839L6.61522 11.435C6.42769 11.6225 6.32233 11.8769 6.32233 12.1421L6.32233 16.6776L10.8579 16.6776C11.1231 16.6776 11.3774 16.5723 11.565 16.3847L17.1716 10.7781M12.2218 5.82839L17.1716 10.7781" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "folder": f"""<svg width="64" height="64" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2.6 4H8.77805C8.92127 4 9.05977 4.05124 9.16852 4.14445L12.3315 6.85555C12.4402 6.94876 12.5787 7 12.722 7H21.4C21.7314 7 22 7.26863 22 7.6V10.4C22 10.7314 21.7314 11 21.4 11H2.6C2.26863 11 2 10.7314 2 10.4V4.6C2 4.26863 2.26863 4 2.6 4Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M22 10L22 14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2 10V19.4C2 19.7314 2.26863 20 2.6 20H13" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19 21C20.1046 21 21 20.1046 21 19C21 17.8954 20.1046 17 19 17C18.6357 17 18.2942 17.0974 18 17.2676C17.4022 17.6134 17 18.2597 17 19C17 19.7403 17.4022 20.3866 18 20.7324C18.2942 20.9026 18.6357 21 19 21Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19 22C20.6569 22 22 20.6569 22 19C22 17.3431 20.6569 16 19 16C17.3431 16 16 17.3431 16 19C16 20.6569 17.3431 22 19 22Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="0.3 2"/>
</svg>""",
    "save": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6 20L18 20" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 4V16M12 16L15.5 12.5M12 16L8.5 12.5" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "language": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M13 2.04932C13 2.04932 16 5.99994 16 11.9999C16 17.9999 13 21.9506 13 21.9506" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 21.9506C11 21.9506 8 17.9999 8 11.9999C8 5.99994 11 2.04932 11 2.04932" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2.62964 15.5H21.3704" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2.62964 8.5H21.3704" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "restart": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6.67742 20.5673C2.53141 18.0212 0.758026 12.7584 2.71678 8.1439C4.87472 3.0601 10.7453 0.68822 15.8291 2.84617C20.9129 5.00412 23.2848 10.8747 21.1269 15.9585C20.2837 17.945 18.8736 19.5174 17.1651 20.5673" stroke="{ACCENT}"   stroke-linecap="round" stroke-linejoin="round"/>
<path d="M17 16V20.4C17 20.7314 17.2686 21 17.6 21H22" stroke="{ACCENT}"   stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 22.01L12.01 21.9989" stroke="{ACCENT}"   stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "dpi": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11 13.6V21H3.6C3.26863 21 3 20.7314 3 20.4V13H10.4C10.7314 13 11 13.2686 11 13.6Z" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 21H14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M3 13V10" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6 3H3.6C3.26863 3 3 3.26863 3 3.6V6" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M14 3H10" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 10V14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M18 3H20.4C20.7314 3 21 3.26863 21 3.6V6" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M18 21H20.4C20.7314 21 21 20.7314 21 20.4V18" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M11 10H14V13" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "palette": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M20.5096 9.54C20.4243 9.77932 20.2918 9.99909 20.12 10.1863C19.9483 10.3735 19.7407 10.5244 19.5096 10.63C18.2796 11.1806 17.2346 12.0745 16.5002 13.2045C15.7659 14.3345 15.3733 15.6524 15.3696 17C15.3711 17.4701 15.418 17.9389 15.5096 18.4C15.5707 18.6818 15.5747 18.973 15.5215 19.2564C15.4682 19.5397 15.3588 19.8096 15.1996 20.05C15.0649 20.2604 14.8877 20.4403 14.6793 20.5781C14.4709 20.7158 14.2359 20.8085 13.9896 20.85C13.4554 20.9504 12.9131 21.0006 12.3696 21C11.1638 21.0006 9.97011 20.7588 8.85952 20.2891C7.74893 19.8194 6.74405 19.1314 5.90455 18.2657C5.06506 17.4001 4.40807 16.3747 3.97261 15.2502C3.53714 14.1257 3.33208 12.9252 3.36959 11.72C3.4472 9.47279 4.3586 7.33495 5.92622 5.72296C7.49385 4.11097 9.60542 3.14028 11.8496 3H12.3596C14.0353 3.00042 15.6777 3.46869 17.1017 4.35207C18.5257 5.23544 19.6748 6.49885 20.4196 8C20.6488 8.47498 20.6812 9.02129 20.5096 9.52V9.54Z" stroke="{ACCENT}" stroke-width="1.5"/>
<path d="M8 16.01L8.01 15.9989" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6 12.01L6.01 11.9989" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M8 8.01L8.01 7.99889" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 6.01L12.01 5.99889" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M16 8.01L16.01 7.99889" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "display": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.2 14.2222V4C3.2 2.89543 4.09543 2 5.2 2H18.8C19.9046 2 20.8 2.89543 20.8 4V14.2222M3.2 14.2222H20.8M3.2 14.2222L1.71969 19.4556C1.35863 20.7321 2.31762 22 3.64418 22H20.3558C21.6824 22 22.6414 20.7321 22.2803 19.4556L20.8 14.2222" stroke="{ACCENT}" stroke-width="1.5"/>
<path d="M11 19L13 19" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "touch": f"""<svg width="64" height="64" stroke-width="1.5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M7 3.51555C8.4301 2.55827 10.1499 2 12 2C16.1031 2 19.5649 4.74572 20.6482 8.5" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M21 22V14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M3 22V11C3 9.94809 3.18046 8.93834 3.51212 8" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M18 22V11.3C18 7.82061 15.3137 5 12 5C8.68629 5 6 7.82061 6 11.3V14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M6 22V18" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M9 22V11.15C9 9.4103 10.3431 8 12 8C12.8653 8 13.645 8.38466 14.1926 9" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M15 22V14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 22V18.5" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M12 11V14" stroke="{ACCENT}" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "blur": f"""<svg width="64" height="64" viewBox="0 0 24 24" stroke-width="1.5" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11.7 1.1732C11.8856 1.06603 12.1144 1.06603 12.3 1.17321L21.2263 6.3268C21.4119 6.43397 21.5263 6.63205 21.5263 6.84641V17.1536C21.5263 17.3679 21.4119 17.566 21.2263 17.6732L12.3 22.8268C12.1144 22.934 11.8856 22.934 11.7 22.8268L2.77372 17.6732C2.58808 17.566 2.47372 17.3679 2.47372 17.1536V6.84641C2.47372 6.63205 2.58808 6.43397 2.77372 6.32679L11.7 1.1732Z" stroke="{ACCENT}"  stroke-linecap="round" stroke-linejoin="round"/>
<path d="M17 15L7 15L12 7L17 15Z" stroke="{ACCENT}"  stroke-linecap="round" stroke-linejoin="round"/>
<path d="M2.5 6.5L12 7" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M2.5 6.5L7 15" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M21.5 6.5L17 15" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M21.5 6.5L12 6.99995L12 1" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M21.5 17.5L17 15" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M2.5 17.5L7 15" stroke="{ACCENT}"  stroke-linejoin="round"/>
<path d="M7 15L12 23L17 15" stroke="{ACCENT}"  stroke-linejoin="round"/>
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
