"""Organized Fluent styles and animated controls shared by the desktop UI."""

import os
import sys

try:
    from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
    from PyQt6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QPainter, QPainterPath, QPen
    from PyQt6.QtWidgets import QCheckBox, QStyle, QStyleOptionButton
    from lib.qml_animations import animate_property
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


if PYQT6_AVAILABLE:
    class FluentCheckBox(QCheckBox):
        """WinUI 3 checkbox with a smooth, native Qt state transition."""

        def __init__(self, text="", parent=None):
            super().__init__(text, parent)
            self._check_progress = float(self.isChecked())
            self._fallback_animation = None
            # Qt 6 emits the semantic enum through checkStateChanged.  Keep the
            # visual progress synchronized with both user clicks and programmatic
            # setChecked()/setCheckState() calls.
            if hasattr(self, "checkStateChanged"):
                self.checkStateChanged.connect(self._animate_check_state)
            else:
                self.stateChanged.connect(self._animate_check_state)
            self._sync_check_state(self.checkState(), animate=False)

        @pyqtProperty(float)
        def checkProgress(self):
            return self._check_progress

        @checkProgress.setter
        def checkProgress(self, progress):
            self._check_progress = min(1.0, max(0.0, float(progress)))
            self.update()

        def _sync_check_state(self, state, animate=True):
            if isinstance(state, Qt.CheckState):
                state_value = state.value
            else:
                state_value = int(state)
            end = 0.5 if state_value == Qt.CheckState.PartiallyChecked.value else float(
                state_value == Qt.CheckState.Checked.value
            )
            if not animate:
                self._check_progress = end
                self.update()
                return
            if not self.isVisible():
                self.checkProgress = end
                return
            if self._fallback_animation is not None:
                self._fallback_animation.stop()
            self._fallback_animation = QPropertyAnimation(self, b"checkProgress", self)
            self._fallback_animation.setDuration(190)
            self._fallback_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._fallback_animation.setStartValue(self._check_progress)
            self._fallback_animation.setEndValue(end)
            self._fallback_animation.start()

        def _animate_check_state(self, state):
            self._sync_check_state(state, animate=True)

        def showEvent(self, event):
            # A checkbox can be initialized before it becomes visible; repaint
            # from the actual Qt state when it enters the scene.
            self._sync_check_state(self.checkState(), animate=False)
            super().showEvent(event)

        def enterEvent(self, event):
            self.update()
            super().enterEvent(event)

        def leaveEvent(self, event):
            self.update()
            super().leaveEvent(event)

        def paintEvent(self, event):
            option = QStyleOptionButton()
            self.initStyleOption(option)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.style().drawControl(
                QStyle.ControlElement.CE_CheckBoxLabel, option, painter, self
            )

            rect = self.style().subElementRect(
                QStyle.SubElement.SE_CheckBoxIndicator, option, self
            ).adjusted(1, 1, -1, -1)
            # Never infer the state from animation progress alone.  The Qt
            # checkState is authoritative, including partially checked boxes.
            actual_state = self.checkState()
            progress = self._check_progress
            if actual_state == Qt.CheckState.Checked and progress <= 0:
                progress = 1.0
            elif actual_state == Qt.CheckState.Unchecked and progress >= 1:
                progress = 0.0
            accent = QColor("#60CDFF")
            border = QColor("#b3b3b3")
            if not self.isEnabled():
                accent = QColor("#626262")
                border = QColor("#555555")
            elif self.underMouse():
                border = QColor("#60CDFF")
            if progress > 0:
                border = accent

            painter.setPen(QPen(border, 1.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, 3, 3)
            if progress > 0:
                fill = QColor(accent)
                fill.setAlphaF(progress)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(fill)
                painter.drawRoundedRect(rect, 3, 3)

                painter.setOpacity(progress)
                painter.setPen(QPen(QColor("#ffffff"), 1.8, Qt.PenStyle.SolidLine,
                                    Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                center_y = rect.center().y()
                if actual_state == Qt.CheckState.PartiallyChecked:
                    painter.drawLine(rect.left() + 4, center_y, rect.right() - 4, center_y)
                else:
                    mark = QPainterPath()
                    mark.moveTo(rect.left() + 4, center_y)
                    mark.lineTo(rect.left() + 7, center_y + 3)
                    mark.lineTo(rect.right() - 3, center_y - 4)
                    painter.drawPath(mark)
            painter.end()
else:
    class FluentCheckBox:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("FluentCheckBox requires PyQt6.")

# Extracted styles stay grouped by the interface area that owns them.
WINDOW_CHROME_STYLES = {
    'packagemaker_001': 'background:transparent;border:none;',
    'packagemaker_003': 'background:transparent;border-right:1px solid rgba(255,255,255,0.08);',
    'packagemaker_004': "color:#ffffff;font-size:24px;font-weight:700;font-family:'Segoe UI Variable Display';letter-spacing:0.3px;background:transparent;border:none;",
    'packagemaker_005': 'QWidget{background-color:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:10px;margin-top:10px;}',
    'packagemaker_006': 'border:none;background:transparent;color:#888;font-weight:bold;font-size:11px;text-transform:uppercase;',
    'packagemaker_007': 'background:transparent;color:#bbb;font-size:12px;line-height:1.2;border:none;',
    'packagemaker_008': 'background:#3a3f4b;border:none;',
    'packagemaker_010': 'QMainWindow{background:\x00QSS_SLOT_0\x00;}',
    'packagemaker_065': 'color:\x00QSS_SLOT_0\x00;font-weight:600;',
    'packagemaker_066': "QPushButton{background-color:transparent;color:#c7ced8;text-align:left;padding-left:17px;border:none;border-left:\x00QSS_SLOT_0\x00px solid transparent;border-radius:9px;font-family:'Segoe UI Variable Display','Segoe UI',sans-serif;font-size:15px;font-weight:500;}QPushButton:hover{background-color:rgba(255,255,255,0.06);color:#ffffff;}QPushButton:checked{background-color:rgba(255,255,255,0.08);color:#ffffff;border-left:\x00QSS_SLOT_1\x00px solid \x00QSS_SLOT_2\x00;}QPushButton:focus{outline:none;}",
    'packagemaker_067': 'QPushButton{background:rgba(255,255,255,0.04);color:#f3f5f8;border:1px solid rgba(255,255,255,0.08);border-radius:8px;font-weight:700;}QPushButton:hover{background:rgba(255,255,255,0.08);}',
    'packagemaker_068': 'QWidget{background-color:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:10px;margin-top:10px;}',
    'packagemaker_069': 'QPushButton{background-color:\x00QSS_SLOT_0\x00;color:white;font-weight:600;font-size:14px;border-radius:6px;border:none;}QPushButton:hover{background-color:\x00QSS_SLOT_1\x00;}QPushButton:pressed{background-color:\x00QSS_SLOT_2\x00;}QPushButton:disabled{background-color:#333;color:#666;}',
}

PROJECT_CREATION_STYLES = {
    'packagemaker_011': 'font-size:24px;font-weight:600;color:white;margin-bottom:10px;background:transparent;',
    'packagemaker_012': 'QGroupBox{border:none;margin-top:0px;background:transparent;}',
    'packagemaker_013': 'QPushButton{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:white;font-weight:bold;}QPushButton:hover{background-color:transparent;}QPushButton:pressed{background-color:transparent;border-color:rgba(255,255,255,0.05);}',
    'packagemaker_014': 'background-color:transparent;',
    'packagemaker_015': "font-family:'Segoe UI',sans-serif;font-size:10px;color:#ff9800;background-color:transparent;padding:3px 7px;border-radius:4px;margin-top:2px;border:none;",
    'packagemaker_016': 'margin-left:10px;',
    'packagemaker_017': 'font-size:32px;background-color:transparent;',
    'packagemaker_018': "font-family:'Segoe UI',sans-serif;font-size:16px;font-weight:600;color:#f44336;background-color:transparent;",
    'packagemaker_019': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#888888;background-color:transparent;",
    'packagemaker_020': 'background-color:transparent;',
    'packagemaker_021': 'background-color:transparent;',
    'packagemaker_022': 'background-color:transparent;',
    'packagemaker_023': "font-family:'Segoe UI',sans-serif;font-size:12px;color:#cccccc;background-color:transparent;",
    'packagemaker_024': "font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;color:#ff9800;background-color:transparent;",
    'packagemaker_025': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#bbbbbb;background-color:transparent;line-height:1.0;",
    'packagemaker_026': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#4CAF50;background-color:transparent;padding:1px;border-radius:6px;",
    'packagemaker_027': "QPushButton{background-color:#4CAF50;color:white;padding:0 16px;border-radius:6px;font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;}QPushButton:hover{background-color:#45a049;}",
    'packagemaker_028': "QPushButton{background-color:transparent;color:#f44336;padding:0 16px;border-radius:6px;border:1.5px solid #f44336;font-family:'Segoe UI',sans-serif;font-size:12px;font-weight:600;}QPushButton:hover{background-color:transparent;}",
    'packagemaker_071': "font-family:'Inter Regular';font-size:14px;color:#cccccc;font-weight:500;background:transparent;",
    'packagemaker_072': "QLineEdit{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-bottom:1px solid rgba(255,255,255,0.4);border-radius:4px;color:white;font-family:'Segoe UI',sans-serif;font-size:14px;selection-background-color:#ff5722;}QLineEdit:hover{background-color:transparent;border-bottom:1px solid rgba(255,255,255,0.6);}QLineEdit:focus{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-bottom:2px solid #ff5722;}",
    'packagemaker_073': "QCheckBox{color:#dddddd;font-family:'Segoe UI',sans-serif;font-size:12px;spacing:8px;background:transparent;border:none;}QCheckBox::indicator{width:18px;height:18px;border-radius:3px;border:1px solid #858585;background:transparent;}QCheckBox::indicator:hover{border-color:#60cdff;}QCheckBox::indicator:pressed{background:rgba(96,205,255,0.24);border-color:#60cdff;}QCheckBox::indicator:checked{background:#60cdff;border-color:#60cdff;image:url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAyIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);}QCheckBox::indicator:indeterminate{background:#60cdff;border-color:#60cdff;image:url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMiAxMiI+PHBhdGggZD0iTTIgNmg4IiBmaWxsPSJub25lIiBzdHJva2U9IiMxMTEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PC9zdmc+);}QCheckBox::indicator:disabled{background:#333;border-color:#555;}QCheckBox::indicator:checked:disabled{background:#555;border-color:#555;}QCheckBox:disabled{color:#777;}QCheckBox:focus{outline:none;}",
    'packagemaker_074': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#4CAF50;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
    'packagemaker_075': 'color:#c62828;',
    'packagemaker_076': 'color:#c62828;',
    'packagemaker_077': 'color:#388e3c;',
    'packagemaker_089': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_090': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_091': 'color:#aaa;font-size:13px;margin-bottom:20px;',
    'packagemaker_092': 'color:white;font-weight:600;',
    'packagemaker_093': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_094': 'color:white;font-weight:600;',
    'packagemaker_095': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_096': 'color:white;font-weight:600;',
    'packagemaker_097': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_098': 'color:white;font-weight:600;',
    'packagemaker_099': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_100': 'color:white;font-weight:600;',
    'packagemaker_101': 'QTextEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QTextEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_154': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#ff9800;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
    'packagemaker_155': 'color:#c62828;',
    'packagemaker_158': "font-family:'Segoe UI',sans-serif;font-size:11px;color:#2196F3;background-color:transparent;padding:5px 10px;border-radius:4px;margin-top:5px;",
}

BUILD_AND_INSTALL_STYLES = {
    'packagemaker_029': 'font-size:24px;font-weight:600;color:white;margin-bottom:10px;background:transparent;',
    'packagemaker_030': 'QGroupBox{border:none;margin-top:0px;background:transparent;}',
    'packagemaker_031': 'margin-top:8px;',
    'packagemaker_032': 'QPushButton{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-radius:4px;color:white;font-weight:bold;}QPushButton:hover{background-color:transparent;}QPushButton:pressed{background-color:transparent;border-color:rgba(255,255,255,0.05);}',
    'packagemaker_033': 'color:#aaa;margin-left:10px;background-color:transparent;',
    'packagemaker_034': "QPushButton{background-color:#ff5722;color:white;font-weight:600;font-size:14px;border-radius:3px;border:none;font-family:'Inter Regular';}QPushButton:hover{background-color:#ff7043;}QPushButton:pressed{background-color:#e64a19;}QPushButton:disabled{background-color:#333;color:#666;}",
    'packagemaker_078': "font-family:'Inter Regular';font-size:14px;color:#cccccc;font-weight:500;background:transparent;",
    'packagemaker_079': "QLineEdit{background-color:transparent;border:1px solid rgba(255,255,255,0.08);border-bottom:1px solid rgba(255,255,255,0.4);border-radius:4px;padding:0 10px;color:white;font-family:'Segoe UI',sans-serif;font-size:14px;selection-background-color:#ff5722;}QLineEdit:hover{background-color:transparent;border-bottom:1px solid rgba(255,255,255,0.6);}QLineEdit:focus{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-bottom:2px solid #ff5722;}",
    'packagemaker_080': "QRadioButton{color:#ddd;font-family:'Segoe UI',sans-serif;font-size:14px;spacing:8px;background-color:transparent;}QRadioButton::indicator{width:18px;height:18px;border-radius:10px;border:2px solid #999;background:transparent;}QRadioButton::indicator:hover{border-color:white;}QRadioButton::indicator:checked{border-color:#ff5722;background-color:#ff5722;}",
    'packagemaker_104': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_105': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_106': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_107': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_110': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_111': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_112': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_113': 'QGroupBox{color:white;font-weight:bold;border:2px solid rgba(255,255,255,0.2);border-radius:8px;margin-top:10px;padding-top:15px;}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px;}',
    'packagemaker_114': 'color:white;font-size:14px;',
    'packagemaker_115': 'color:white;font-size:14px;',
    'packagemaker_116': 'color:white;font-size:14px;',
    'packagemaker_117': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_156': 'QLineEdit{color:#888;font-style:italic;}',
}

PACKAGE_MANAGER_STYLES = {
    'packagemaker_035': 'font-size:24px;font-weight:600;color:white;margin-bottom:5px;background:transparent;',
    'packagemaker_036': 'QSplitter::handle{background-color:transparent;}',
    'packagemaker_037': 'color:#aaa;margin-top:5px;',
    'packagemaker_081': "font-family:'Segoe UI';font-size:16px;font-weight:600;color:#e0e0e0;background-color:transparent;",
    'packagemaker_082': "QListWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:5px;outline:none;}QListWidget::item{background-color:transparent;border-radius:6px;padding:8px;margin-bottom:2px;color:#ddd;font-family:'Segoe UI',sans-serif;font-size:14px;}QListWidget::item:hover{background-color:transparent;}QListWidget::item:selected{background-color:transparent;border-left:3px solid #ff5722;color:white;}",
    'packagemaker_083': "QPushButton{background-color:\x00QSS_SLOT_0\x00;color:\x00QSS_SLOT_1\x00;border:\x00QSS_SLOT_2\x00;border-radius:4px;font-weight:600;font-size:13px;font-family:'Segoe UI',sans-serif;padding:0 15px;}QPushButton:hover{background-color:\x00QSS_SLOT_3\x00;}QPushButton:pressed{background-color:\x00QSS_SLOT_4\x00;opacity:0.8;}",
}

CONFIGURATION_STYLES = {
    'packagemaker_038': 'color:#ff7043;font-size:13px;font-weight:700;margin-top:8px;background:transparent;',
    'packagemaker_039': 'color:#9aa4b2;font-size:12px;background:transparent;',
    'packagemaker_040': 'font-size:22px;font-weight:600;color:white;',
    'packagemaker_041': 'QFrame{background:rgba(255,152,0,0.12);border:1px solid rgba(255,152,0,0.35);border-radius:6px;}',
    'packagemaker_042': 'color:#ffcc80;font-size:12px;background:transparent;',
    'packagemaker_043': 'QScrollArea{background:transparent;border:none;}',
    'packagemaker_044': 'background:transparent;',
    'packagemaker_046': 'QPushButton{background:rgba(255,255,255,0.08);color:white;border-radius:4px;padding:0 12px;}QPushButton:hover{background:rgba(255,255,255,0.14);}',
    'packagemaker_049': 'color:#ddd;font-size:12px;background:transparent;',
    'packagemaker_050': 'color:#666;font-size:11px;',
    'packagemaker_051': 'QPushButton{background:#0078d4;color:white;border:none;border-radius:4px;font-weight:600;}QPushButton:hover{background:#106ebe;}',
    'packagemaker_052': 'QPushButton{background:rgba(244,67,54,0.2);color:#ff5722;border:1px solid rgba(244,67,54,0.4);border-radius:4px;font-weight:600;}QPushButton:hover{background:rgba(244,67,54,0.3);}',
    'packagemaker_084': 'color:#666;font-size:11px;',
    'packagemaker_085': 'color:#aaa;font-size:11px;',
}

MAINTENANCE_STYLES = {
    'packagemaker_053': 'font-size:22px;font-weight:600;color:white;background:transparent;',
    'packagemaker_054': 'color:#9aa4b2;font-size:12px;background:transparent;',
    'packagemaker_055': 'color:#ddd;font-size:12px;background:transparent;',
    'packagemaker_056': 'QLineEdit{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:4px;color:white;padding:0 8px;}',
    'packagemaker_057': 'QPushButton{background:rgba(255,255,255,0.08);color:white;border-radius:4px;}QPushButton:hover{background:rgba(255,255,255,0.14);}',
    'packagemaker_058': 'QPushButton{background:#a371f7;color:white;font-weight:600;font-size:12px;border:none;border-radius:4px;}QPushButton:hover{background:#b084f9;}',
    'packagemaker_120': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_121': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_122': 'color:#aaa;font-size:14px;margin-bottom:10px;',
    'packagemaker_123': 'color:#888;font-size:13px;margin-bottom:20px;',
    'packagemaker_124': 'QGroupBox{color:white;font-weight:bold;border:2px solid rgba(255,255,255,0.2);border-radius:8px;margin-top:10px;padding-top:15px;}QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px;}',
    'packagemaker_125': 'color:white;font-size:14px;',
    'packagemaker_126': 'color:white;font-size:14px;',
    'packagemaker_127': 'color:white;font-size:14px;',
    'packagemaker_128': 'color:white;font-size:14px;',
    'packagemaker_129': "QTextEdit{background-color:transparent;color:#0ff;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,255,0.3);border-radius:8px;padding:10px;font-size:13px;}",
}

ABOUT_STYLES = {
    'packagemaker_059': "font-size:28px;font-weight:bold;color:white;font-family:'Segoe UI Variable Display';",
    'packagemaker_060': 'font-size:16px;color:#aaa;',
    'packagemaker_061': 'color:#ddd;font-size:14px;line-height:1.5;',
    'packagemaker_062': 'background-color:#333;color:white;border:none;border-radius:4px;padding:8px 16px;',
    'packagemaker_063': 'background-color:#0088cc;color:white;border:none;border-radius:4px;padding:8px 16px;',
    'packagemaker_086': 'background-color:#ff5722;border-radius:32px;color:white;font-weight:bold;font-size:24px;',
    'packagemaker_087': 'color:#888;font-weight:bold;',
    'packagemaker_088': 'color:white;',
}

PACKAGE_INSTALL_STYLES = {
    'packagemaker_132': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_133': 'color:white;font-size:24px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_134': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_135': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
}

MEXF_STYLES = {
    'packagemaker_138': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_139': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_140': 'color:#aaa;font-size:14px;margin-bottom:20px;',
    'packagemaker_141': "QTextEdit{background-color:transparent;color:#0f0;font-family:'Consolas','Courier New',monospace;border:2px solid rgba(0,255,0,0.3);border-radius:8px;padding:10px;font-size:13px;}",
    'packagemaker_144': 'QWidget#CentralWidget{background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:16px;}',
    'packagemaker_145': 'color:white;font-size:22px;font-weight:bold;margin-bottom:10px;',
    'packagemaker_146': 'color:#aaa;font-size:13px;margin-bottom:20px;',
    'packagemaker_147': 'color:white;font-weight:600;',
    'packagemaker_148': 'QLineEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QLineEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_149': 'color:white;font-weight:600;',
    'packagemaker_150': 'QTextEdit{background-color:transparent;color:white;border:2px solid rgba(255,255,255,0.2);border-radius:8px;padding:12px;font-size:14px;}QTextEdit:focus{border:2px solid #2486ff;}',
    'packagemaker_151': 'color:#888;font-size:12px;margin-top:10px;',
    'packagemaker_157': 'color:white;background-color:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:15px;font-size:13px;',
}

SHARED_DIALOG_STYLES = {
    'packagemaker_002': 'background-color:transparent;border:none;border-radius:5px;',
    'packagemaker_064': 'QWidget#SplashContainer{background-color:#1a1a1a;border-radius:0px;}',
}

STYLE_GROUPS = (
    WINDOW_CHROME_STYLES,
    PROJECT_CREATION_STYLES,
    BUILD_AND_INSTALL_STYLES,
    PACKAGE_MANAGER_STYLES,
    CONFIGURATION_STYLES,
    MAINTENANCE_STYLES,
    ABOUT_STYLES,
    PACKAGE_INSTALL_STYLES,
    MEXF_STYLES,
    SHARED_DIALOG_STYLES,
)
INLINE_STYLES = {key: stylesheet for group in STYLE_GROUPS for key, stylesheet in group.items()}

WINUI3_CHECKBOX_QSS = INLINE_STYLES["packagemaker_073"]


def qss_value(value, conversion=None, format_spec=""):
    """Apply Python f-string conversion/formatting to a QSS placeholder."""
    if conversion == "r":
        value = repr(value)
    elif conversion == "a":
        value = ascii(value)
    elif conversion == "s":
        value = str(value)
    return format(value, format_spec)


def set_qss(widget, stylesheet, values=(), append=False):
    """Apply a centralized stylesheet or a named extracted QSS template."""
    if isinstance(stylesheet, str) and stylesheet in INLINE_STYLES:
        stylesheet = INLINE_STYLES[stylesheet]
        for index, value in enumerate(values):
            stylesheet = stylesheet.replace(f"\x00QSS_SLOT_{index}\x00", str(value))
    elif values:
        raise ValueError("QSS values were supplied for a non-template stylesheet.")

    if append:
        current = widget.styleSheet().rstrip()
        stylesheet = f"{current}\n{stylesheet}" if current else stylesheet
    widget.setStyleSheet(stylesheet)


def preferred_ui_font(size=11):
    """Return the first preferred UI font installed on the host.

    Roboto remains the project preference; Inter and SF Pro are useful native
    fallbacks on systems where Roboto is not installed.

    ``QFontDatabase.families()`` requires a live ``QGuiApplication``, so the
    query is skipped when no application exists yet and a default ``QFont`` is
    returned instead. Callers that need the preferred family must run after the
    application is constructed.

    Las fuentes descargadas por :mod:`lib.font_manager` tienen prioridad sobre
    las del sistema, de modo que la interfaz se ve igual en cualquier máquina.
    """
    if not PYQT6_AVAILABLE:
        return None
    if QGuiApplication.instance() is None:
        return QFont("sans-serif", int(size))

    family = _preferred_family()
    if family:
        return QFont(family, int(size))
    return QFont("sans-serif", int(size))


def _preferred_family():
    """Familia de UI preferida: caché del proyecto primero, luego el sistema."""
    try:
        from lib.font_manager import UI_PREFERENCE, resolve_family

        family = resolve_family(UI_PREFERENCE, kind="ui")
        if family:
            return family
    except Exception:
        pass

    installed = {family.casefold(): family for family in QFontDatabase.families()}
    for candidate in ("Roboto", "Inter Regular", "Inter", "SF Pro Display", "SF Pro", "Segoe UI Variable", "Segoe UI"):
        if candidate.casefold() in installed:
            return installed[candidate.casefold()]
    return None


def preferred_mono_font(size=10):
    """Fuente monoespaciada preferida (JetBrains Mono si está disponible)."""
    if not PYQT6_AVAILABLE:
        return None
    if QGuiApplication.instance() is None:
        return QFont("monospace", int(size))

    try:
        from lib.font_manager import MONO_PREFERENCE, resolve_family

        family = resolve_family(MONO_PREFERENCE, kind="mono")
        if family:
            return QFont(family, int(size))
    except Exception:
        pass

    installed = {family.casefold(): family for family in QFontDatabase.families()}
    for candidate in ("JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono"):
        if candidate.casefold() in installed:
            return QFont(installed[candidate.casefold()], int(size))
    return QFont("monospace", int(size))


def system_theme_mode():
    """Return ``dark`` or ``light`` using Qt's system color scheme first."""
    if not PYQT6_AVAILABLE:
        return "light"
    app = QGuiApplication.instance()
    if app is not None:
        try:
            hints = app.styleHints()
            if hasattr(hints, "colorScheme"):
                scheme = hints.colorScheme()
                if scheme == Qt.ColorScheme.Dark:
                    return "dark"
                if scheme == Qt.ColorScheme.Light:
                    return "light"
        except (AttributeError, RuntimeError):
            pass
        try:
            return "dark" if app.palette().color(app.palette().ColorRole.Window).lightness() < 128 else "light"
        except (AttributeError, RuntimeError):
            pass
    if sys.platform.startswith("win"):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if int(value) else "dark"
        except (ImportError, OSError, ValueError):
            pass
    return "dark" if "dark" in os.environ.get("GTK_THEME", "").casefold() else "light"


def sidebar_stylesheet(dark, accent="#0078d4"):
    """Theme-aware sidebar frame and navigation button styles."""
    if dark:
        sidebar_bg, border, text, hover, selected = "#2b303a", "rgba(255,255,255,.10)", "#d8dee9", "rgba(255,255,255,.07)", "rgba(255,255,255,.11)"
    else:
        sidebar_bg, border, text, hover, selected = "#eef2f7", "rgba(15,23,42,.12)", "#334155", "rgba(15,23,42,.07)", "rgba(0,120,212,.14)"
    return f"""
        QWidget#NavigationSidebar {{ background:{sidebar_bg}; border-right:1px solid {border}; }}
        QPushButton#SidebarCollapseButton {{ background:transparent; color:{text}; border:none; border-radius:7px; }}
        QPushButton#SidebarCollapseButton:hover {{ background:{hover}; }}
        QPushButton#SidebarCollapseButton:pressed {{ background:{selected}; }}
        QWidget#SidebarContextCard {{ background:{hover}; border:1px solid {border}; border-radius:10px; }}
        QWidget#NavigationSidebar QPushButton {{ color:{text}; font-family:'Roboto','Inter Regular','SF Pro Display','Segoe UI',sans-serif; }}
        QWidget#NavigationSidebar QPushButton:hover {{ background:{hover}; color:{text}; }}
        QWidget#NavigationSidebar QPushButton:checked {{ background:{selected}; color:{text}; border-left:3px solid {accent}; }}
    """


def sidebar_button_stylesheet(dark, accent="#0078d4", border_width=3):
    """Return an explicit stylesheet for one sidebar navigation button."""
    if dark:
        text, hover, selected = "#c7ced8", "rgba(255,255,255,.06)", "rgba(255,255,255,.08)"
    else:
        text, hover, selected = "#334155", "rgba(15,23,42,.07)", "rgba(0,120,212,.14)"
    return f"""
        QPushButton {{ background:transparent; color:{text}; text-align:left; padding-left:17px;
            border:none; border-left:{int(border_width)}px solid transparent; border-radius:9px;
            font-family:'Roboto','Inter Regular','SF Pro Display','Segoe UI',sans-serif;
            font-size:15px; font-weight:500; }}
        QPushButton:hover {{ background:{hover}; color:{text}; }}
        QPushButton:checked {{ background:{selected}; color:{text}; border-left:{int(border_width)}px solid {accent}; }}
        QPushButton:focus {{ outline:none; }}
    """


def checkbox_stylesheet(accent="#60cdff"):
    """Return the complete WinUI 3 checkbox states for native and custom controls."""
    return WINUI3_CHECKBOX_QSS.replace("#60cdff", str(accent))


def splash_titlebar_stylesheet():
    return """
        QWidget#SharedSplash QWidget#customTitleBar {
            background: rgba(25, 30, 39, 0.96);
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        QWidget#SharedSplash QLabel#titleLabel {
            color: #f3f5f8;
            background: transparent;
        }
    """


def conf_field_stylesheet(readonly=False):
    if readonly:
        return """
            QLineEdit, QComboBox {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 4px;
                color: #888;
                padding: 0 10px;
            }
        """
    return """
        QLineEdit, QComboBox {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.12);
            border-bottom: 2px solid #0078d4;
            border-radius: 4px;
            color: white;
            padding: 0 10px;
            min-height: 32px;
        }
    """


BTN_STYLES = {'default': 'background-color: transparent;color: rgba(32,33,36,0.96);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(209,215,224,0.65);',
 'success': 'background-color: transparent;color: rgba(5,98,55,0.99);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(199,232,206,0.60);',
 'danger': 'background-color: transparent;color: rgba(185,29,29,1.0);border-radius: 9px;padding: '
           '10px 20px;font-weight: 600;border: 1px solid rgba(255,180,180,0.68);',
 'warning': 'background-color: transparent;color: rgba(168,132,4,0.97);border-radius: 9px;padding: '
            '10px 20px;font-weight: 600;border: 1px solid rgba(255,224,149,0.66);',
 'info': 'background-color: transparent;color: rgba(9,82,165,1.0);border-radius: 9px;padding: 10px '
         '20px;font-weight: 600;border: 1px solid rgba(185,213,253,0.56);',
 'best': 'background-color: transparent;color: #0853c4;border-radius: 11px;padding: 12px '
         '22px;font-weight: 700;border: 2px solid #99d3f7;font-size: 15px;',
 'grayed-black': 'background-color: #292929;color: #b9b9b9;border-radius: 9px;padding: 10px '
                 '20px;font-weight: 600;border: 1px solid #444;background-image: none;'}

TITLE_BAR_STYLESHEET = """
    QWidget#SharedTitleBar {
        background-color: rgba(26, 30, 37, 0.96);
        border: none;
    }
    QLabel#SharedTitleLabel {
        color: #f3f5f8;
        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        font-size: 13px;
        font-weight: 500;
        background: transparent;
    }
    QLabel#SharedIconFallback {
        color: #ff7043;
        font-size: 20px;
        font-weight: 600;
        background: transparent;
    }
    QPushButton#TitleMinimizeButton, QPushButton#TitleMaximizeButton,
    QPushButton#TitleCloseButton {
        color: #f3f5f8;
        background: transparent;
        border: none;
        border-radius: 0;
        font-size: 13px;
        padding: 0;
    }
    QPushButton#TitleMinimizeButton:hover,
    QPushButton#TitleMaximizeButton:hover {
        background: rgba(255, 255, 255, 0.12);
    }
    QPushButton#TitleCloseButton:hover {
        background: #c42b1c;
    }
"""

SPLASH_STYLESHEET = """
    QWidget#SharedSplash {
        background-color: #202630;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
    }
    QLabel#SplashIconFallback {
        color: #ff7043;
        font-size: 72px;
        font-weight: 300;
        background: transparent;
    }
    QLabel#SplashTitle {
        color: #f3f5f8;
        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        font-size: 17px;
        font-weight: 600;
        background: transparent;
    }
""" + splash_titlebar_stylesheet()


def applyget(accent: str) -> str:
    return f"""
    * {{
        outline: none;
    }}
    QWidget:focus {{
        border: none;
        outline: none;
    }}
    QPushButton:focus {{
        outline: none;
        border: none;
    }}
    QLineEdit:focus {{
        border: 1px solid #1e88e5;
        background: rgba(0,0,0,0.2);
    }}
    QComboBox {{
        border:none;
    }}
    QWidget#ContentContainer {{
        background-color: #303641;
        border: none
    }}
    QWidget#NavigationSidebar {{
        background-color: #2b303a;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }}
    QWidget#DialogCentral {{
        background-color: transparent;
        border: none;
    }}
    QWidget#SidebarContextCard {{ background-color: rgba(255, 255, 255, 0.035); border: 1px solid rgba(255, 255, 255, 0.09); border-radius: 10px; }}
    QGroupBox {{ color: #f3f5f8; background-color: transparent; border: none; font-weight: 600; }}
    QHBoxLayout {{ color: #ffffff; font-size: 24px; font-weight: 700; font-family: 'Segoe UI Variable Display'; letter-spacing: 0.3px; background: transparent; border: none; }}
    QWidget {{ background-color: transparent ; border: none; border-radius: 5px; }}
    QLineEdit, QTextEdit, QPlainTextEdit {{ background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.08);  border-radius: 4px; color: white; font-family: 'Segoe UI', sans-serif; font-size: 14px; selection-background-color: {accent}; margin-left: 5px; margin-right: 5px;}}
    QLineEdit:hover {{ background-color: transparent;  }}
    QLineEdit:focus {{ background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.1); }}
    QScrollBar:vertical {{ width: 10px; margin: 2px; background: transparent; }}
    QScrollBar:horizontal {{ height: 10px; margin: 2px; background: transparent; }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ background: rgba(255, 255, 255, 0.24); border-radius: 4px; min-height: 24px; min-width: 24px; }}
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{ background: rgba(255, 255, 255, 0.38); }}
    QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; border: none; }}
    QWidget:focus, QPushButton:focus, QCheckBox:focus, QComboBox:focus, QListWidget:focus {{ outline: none; }}
    QLabel {{ font-family: 'Inter Regular'; font-size: 14px; color: #cccccc; font-weight: 500; background: transparent; border: none}}
    QStackedWidget {{ background: transparent; color: #bbb; font-size: 12px; line-height: 1.2; border:none; }}
    QPushButton {{ background-color: {accent}; color: white; font-weight: 600; font-size: 14px; border-radius: 3px; border: none; font-family: 'Inter Regular'; }}
    QPushButton:hover {{ background-color: #ff7043; }}
    QPushButton:pressed {{ background-color: #e64a19; border-color: rgba(255, 255, 255, 0.05); }}
    QPushButton:disabled {{ background-color: #333; color: #666; }}
    {checkbox_stylesheet(accent)}
    QProgressBar {{
        background: transparent;
        border: none;
        border-radius: 2px;
    }}
    QProgressBar::chunk {{
        background: #ff5722;
    }}
    """
