#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MoonFix Wizard - Asistente de reparación para proyectos PackageMaker
"""

import os
import time
import shutil
import zipfile
import tempfile
import json
import re
import urllib.request
import urllib.error
import subprocess
import sys

# PyQt6 imports
try:
    from PyQt6.QtWidgets import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QStackedWidget, QScrollArea, QGridLayout, QFileDialog,
        QRadioButton, QButtonGroup, QApplication
    )
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtCore import Qt, QThread, QTimer
    from PyQt6 import QtCore, QtWidgets, QtGui
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    class QDialog: pass
    class QWidget: pass
    class QThread: pass
    class QTimer:
        def __init__(self, *args, **kwargs): pass
        def start(self, *args): pass
        def stop(self): pass
        class timeout:
            @staticmethod
            def connect(func): pass

# XML handling
import xml.etree.ElementTree as ET

# Optional Windows registry
try:
    import winreg
except ImportError:
    winreg = None

# Leviathan UI imports
try:
    from leviathan_ui import WipeWindow
    from leviathan_ui.dialogs import LeviathanDialog
except (ImportError, SyntaxError):
    class WipeWindow: pass
    class LeviathanDialog: pass
from lib.uwp_animations import play_bounce_down_close

class FixedProxy:
    def __init__(self, v): self.v = v
    def text(self): return self.v
    def setText(self, t): self.v = t

class MoonFixWizard(QDialog):
    """Asistente de reparación estilo Setup que procesa múltiples proyectos en una sola ventana."""
    def __init__(self, parent, projects_with_issues):
        super().__init__(parent)
        self.projects = projects_with_issues
        self.current_project_index = 0
        self.results = {} # Store modified data per project index
        
        # Configuración de Ventana - REMOVED WindowStaysOnTopHint to avoid 'zombie' modal issues
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Responsive sizing: requested even more compact (-30px from 390 = 360)
        self.resize(720, 360)
        
        # Ensure it cleans up properly
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Initial position: centered horizontally, slightly higher vertically
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        start_x = (screen.width() - self.width()) // 2
        start_y = (screen.height() - self.height()) // 2 - 20
        self.move(max(0, start_x), max(0, start_y))
        
        # State for dragging
        self._dragging = False
        self._drag_pos = QtCore.QPoint()
        
        # Keyboard focus removal - more aggressive
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("""
            * { outline: none; }
            QWidget:focus { border: none; outline: none; }
            QPushButton:focus { outline: none; border: none; }
            QLineEdit:focus { border: 1px solid #1e88e5; background: rgba(0,0,0,0.2); }
            QPushButton#uwp_next {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid rgba(255,255,255,0.1);
                padding: 0 15px;
            }
            QPushButton#uwp_next:hover { background-color: #106ebe; }
            QPushButton#uwp_next:pressed { background-color: #005a9e; }
            QPushButton#uwp_next:disabled { background-color: #333; color: #777; }
        """)
        
        # Entrance state
        self.setWindowOpacity(0)
        
        # Animation references to prevent GC
        self._active_anims = []
        
        # Efecto de ventana Leviathan
        self.window_effects = WipeWindow.create().set_mode("ghostBlur").set_radius(20).apply(self)
        
        # Support for Asset Packs
        self.setAcceptDrops(True)
        self._temp_assets = {} # Store extracted paths temporarily

        self.init_ui()
        
    def showEvent(self, event):
        """Smooth entrance animation."""
        # Ensure it starts at 0 opacity and slightly offset before super() makes it visible
        self.setWindowOpacity(0)
        target_pos = self.pos()
        self.move(target_pos.x(), target_pos.y() + 40)
        
        super().showEvent(event)
        
        # Fade in + Slide Up
        self.anim_fade = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim_fade.setDuration(600)
        self.anim_fade.setStartValue(0)
        self.anim_fade.setEndValue(1)
        self.anim_fade.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        
        self.anim_pos = QtCore.QPropertyAnimation(self, b"pos")
        self.anim_pos.setDuration(600)
        self.anim_pos.setStartValue(self.pos())
        self.anim_pos.setEndValue(target_pos)
        self.anim_pos.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        
        # Store to prevent GC
        self._active_anims = [self.anim_fade, self.anim_pos]
        
        self.anim_fade.start()
        self.anim_pos.start()

    def closeEvent(self, event):
        if getattr(self, "_force_close", False):
            super().closeEvent(event)
            return
        event.ignore()
        play_bounce_down_close(self, on_finished=lambda: self._force_finish_close(), drop_px=72)

    def _force_finish_close(self):
        self._force_close = True
        super().close()
        
    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Barra de título personalizada
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(45)
        self.title_bar.setStyleSheet("background: transparent; border-bottom: 1px solid rgba(255,255,255,0.05);")
        t_layout = QHBoxLayout(self.title_bar)
        t_layout.setContentsMargins(20, 0, 10, 0)
        
        t_icon = QLabel("🌙")
        t_icon.setStyleSheet("font-size: 18px;")
        t_layout.addWidget(t_icon)
        
        self.t_title = QLabel("MoonFix Setup Wizard")
        self.t_title.setStyleSheet("color: white; font-weight: bold; font-family: 'Segoe UI'; font-size: 13px;")
        t_layout.addWidget(self.t_title)
        t_layout.addStretch()
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("QPushButton { background: transparent; color: #888; border-radius: 16px; font-size: 16px; } QPushButton:hover { background: #e81123; color: white; }")
        btn_close.clicked.connect(self.reject)
        t_layout.addWidget(btn_close)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Drag Logic for custom title bar
        def title_press(event):
            if event.button() == Qt.LeftButton:
                self._dragging = True
                self._drag_pos = event.globalPos() - self.pos()
                event.accept()

        def title_move(event):
            if self._dragging and event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self._drag_pos)
                event.accept()

        def title_release(event):
            self._dragging = False

        self.title_bar.mousePressEvent = title_press
        self.title_bar.mouseMoveEvent = title_move
        self.title_bar.mouseReleaseEvent = title_release

        # Stack de Páginas
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.stack)

        # 1. Página de Introducción
        self.page_intro = self.create_page_intro()
        self.stack.addWidget(self.page_intro)

        # 2. Páginas de Proyectos
        for i, proj in enumerate(self.projects):
            page = self.create_project_page(i, proj)
            self.stack.addWidget(page)

        # 3. Página Final
        self.page_done = self.create_page_done()
        self.stack.addWidget(self.page_done)

        # Barra de navegación inferior
        self.nav_bar = QWidget()
        self.nav_bar.setFixedHeight(48)
        self.nav_bar.setStyleSheet("background: rgba(0,0,0,0.2); border-top: 1px solid rgba(255,255,255,0.05);")
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(24, 0, 24, 0)
        
        self.lbl_step = QLabel(f"Página 1 de {len(self.projects) + 2}")
        self.lbl_step.setStyleSheet("background: transparent; color: #888; font-size: 11px; font-family: 'Segoe UI Variable Text';")
        nav_layout.addWidget(self.lbl_step)
        nav_layout.addStretch()
        
        self.btn_next = QPushButton("Empezar")
        self.btn_next.setObjectName("uwp_next")
        self.btn_next.setFixedSize(100, 32)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.clicked.connect(self.go_next)
        nav_layout.addWidget(self.btn_next)
        
        self.main_layout.addWidget(self.nav_bar)

    def create_page_intro(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(15)

        title = QLabel("Optimización de Proyectos")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white; font-family: 'Segoe UI Variable Display';")
        layout.addWidget(title)

        desc = QLabel(
            f"Se han detectado <b>{len(self.projects)}</b> proyectos que requieren atención inmediata.\n\n"
            "MoonFix corregirá automáticamente las claves inválidas y normalizará las versiones."
        )
        desc.setStyleSheet("color: #bbb; font-size: 14px; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        warning_box = QWidget()
        warning_box.setStyleSheet("background: transparent; border: 1px solid rgba(255, 152, 0, 0.2); border-radius: 8px;")
        w_layout = QHBoxLayout(warning_box)
        w_icon = QLabel("⚠️")
        w_text = QLabel("Asegúrate de tener conexión a internet si necesitas verificar perfiles de GitHub.")
        w_text.setStyleSheet("color: #ffb74d; font-size: 13px;")
        w_layout.addWidget(w_icon)
        w_layout.addWidget(w_text)
        layout.addWidget(warning_box)
        
        return page

    # --- DRAG & DROP FOR ASSET PACKS ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                f = url.toLocalFile().lower()
                if f.endswith(".ipm-assetpck") or f.endswith(".ipm-iconpck"):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".ipm-assetpck"):
                self.process_ipm_assetpck(path)
            elif path.lower().endswith(".ipm-iconpck"):
                self.process_ipm_iconpck(path)
        super().dropEvent(event)

    def process_ipm_iconpck(self, file_path):
        """Parser for *.ipm-iconpck (ZIP containing multiple .ico files)"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="ipm_icons_")
            with zipfile.ZipFile(file_path, 'r') as z:
                z.extractall(temp_dir)
                
            proj_idx = self.stack.currentIndex() - 1
            if proj_idx < 0: return

            applied = 0
            # Mapping: filename in zip -> ui field
            mapping = {
                "app-icon.ico": "extra_icon",
                "updater-icon.ico": "extra_icon_updater",
                "product_logo.png": "extra_icon" # Fallback
            }
            
            for zip_fn, ui_key in mapping.items():
                full_p = os.path.join(temp_dir, zip_fn)
                if os.path.exists(full_p):
                    target = self.results[proj_idx]["inputs"].get(ui_key)
                    if target:
                        target.setText(full_p)
                        applied += 1
            
            if applied > 0:
                self.statusBar().showMessage(f"Icon Pack aplicado: {applied} iconos vinculados.")
            else:
                self.statusBar().showMessage("Icon Pack cargado, pero no se encontraron nombres de archivos válidos.")
        except Exception as e:
            LeviathanDialog.launch(self, "Error de Icon Pack", str(e), mode="error")

    def process_ipm_assetpck(self, file_path):
        """Binary parser for *.ipm-assetpck (ZIP format with internal JSON)"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="ipm_assets_")
            with zipfile.ZipFile(file_path, 'r') as z:
                if 'metadata.json' not in z.namelist():
                    LeviathanDialog.launch(self, "Asset Pack", "El paquete no contiene metadata.json válida.", mode="error")
                    return
                
                z.extractall(temp_dir)
                meta_path = os.path.join(temp_dir, 'metadata.json')
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                # Mapping: json_key -> ui_field_suffix
                mapping = {
                    "splash": "extra_splash",
                    "storelogo": "extra_icon",
                    "setuplabel": "extra_splash_setup"
                }

                current_idx = self.stack.currentIndex()
                proj_idx = current_idx - 1 
                
                if proj_idx < 0 or proj_idx >= len(self.projects):
                    return

                applied_count = 0
                for json_key, ui_key in mapping.items():
                    filename = meta.get(json_key)
                    if filename:
                        src_img_p = os.path.join(temp_dir, filename)
                        if os.path.exists(src_img_p):
                            # Convert to standard PNG and Rename
                            ext_map = {"extra_splash": "splash.png", "extra_icon": "product_logo.png", "extra_splash_setup": "splash_Setup.png"}
                            dest_name = ext_map[ui_key]
                            dest_path = os.path.join(temp_dir, f"converted_{dest_name}")
                            
                            # Conversion Engine (Supports any format Qt supports)
                            pix = QPixmap(src_img_p)
                            if not pix.isNull():
                                pix.save(dest_path, "PNG")
                                
                                # Update UI field
                                target_edit = self.results[proj_idx]["inputs"].get(ui_key)
                                if target_edit:
                                    target_edit.setText(dest_path)
                                    applied_count += 1
                
                if applied_count > 0:
                    self.statusBar().showMessage(f"Asset Pack aplicado: {applied_count} imágenes convertidas y vinculadas.")
                else:
                    self.statusBar().showMessage("Asset Pack cargado, pero no hay campos faltantes compatibles.")
        except Exception as e:
            LeviathanDialog.launch(self, "Error de Pack", f"No se pudo parsear el Asset Pack: {str(e)}", mode="error")

    def create_project_page(self, index, proj_data):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)
        
        path = proj_data["path"]
        name = os.path.basename(path)
        
        # Header with Icon
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(60, 60)
        
        icon_path = os.path.join(path, "app", "app-icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.getcwd(), "app", "app-icon.ico")
            
        if os.path.exists(icon_path):
            icon_lbl.setPixmap(QPixmap(icon_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_lbl.setStyleSheet("background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-size: 24px;")
            icon_lbl.setText("")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_vbox = QVBoxLayout()
        t_name = QLabel(name)
        t_name.setStyleSheet("font-size: 24px; font-weight: 600; color: white; font-family: 'Segoe UI Variable Display';")
        t_path = QLabel(path)
        t_path.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.5); font-family: 'Segoe UI Variable Text';")
        t_path.setWordWrap(True)
        title_vbox.addWidget(t_name)
        title_vbox.addWidget(t_path)
        
        header.addWidget(icon_lbl)
        header.addSpacing(15)
        header.addLayout(title_vbox)
        header.addStretch()
        
        # Issues Summary Badge - UWP Card Style
        issues_box = QWidget()
        issues_box.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);")
        i_layout = QVBoxLayout(issues_box)
        i_layout.setContentsMargins(15, 10, 15, 10)
        i_layout.setSpacing(4)
        
        i_title = QLabel("INCONSISTENCIAS")
        i_title.setStyleSheet("color: #ff9800; font-size: 9px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Segoe UI Variable Text';")
        i_layout.addWidget(i_title)
        
        # Restore full issue list for "learning"
        for issue in proj_data["issues"]:
            desc = issue.get("desc", issue.get("type", "Error"))
            if issue["type"] == "missing_dir": desc = f"Falta directorio: {issue['path']}"
            elif issue["type"] == "missing_xml": desc = "Archivo details.xml ausente"
            elif issue["type"] == "missing_script": desc = "Script principal no encontrado"
            elif issue["type"] == "missing_icon": desc = "Icono de app (*.ico) faltante"
            elif issue["type"] == "missing_logo": desc = "Logotipo product_logo.png faltante"
            elif issue["type"] == "missing_icon_updater": desc = "Icono de updater (*.ico) faltante"
            elif issue["type"] == "dirty_version": desc = f"Versión '{issue.get('val','')}' no normalizada"
            elif issue["type"] == "missing_splash": desc = "Splash PNG faltante"
            elif issue["type"] == "missing_splash_setup": desc = "Banner de Setup faltante"
            
            i_lbl = QLabel(f"• {desc}")
            i_lbl.setStyleSheet("color: #bbb; font-size: 11px; font-family: 'Segoe UI Variable Text';")
            i_lbl.setWordWrap(True)
            i_layout.addWidget(i_lbl)
        
        header.addWidget(issues_box)
        
        layout.addLayout(header)
        layout.addSpacing(5)
        
        # Form Container
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        form_content = QWidget()
        form_layout = QGridLayout(form_content)
        form_layout.setColumnStretch(1, 1)
        form_layout.setContentsMargins(5, 5, 5, 5)
        form_layout.setVerticalSpacing(10)
        
        # XML Data Extraction
        xml_path = os.path.join(path, "details.xml")
        xml_data = {}
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                xml_data = {child.tag: child.text for child in root if child.text}
            except: pass

        self.results[index] = {"inputs": {}, "is_invalid": any(i["type"] == "invalid_package" for i in proj_data["issues"])}
        
        EDIT_QSS = """
            QLineEdit { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.4); border-radius: 4px; color: white; padding: 0 12px; font-family: 'Segoe UIVariable Text'; font-size: 13px; }
            QLineEdit:hover { background: rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.6); }
            QLineEdit:focus { border: 1px solid rgba(255,255,255,0.1); border-bottom: 2px solid #0078D4; background: rgba(0,0,0,0.3); }
        """
        
        RADIO_QSS = """
            QRadioButton { color: white; spacing: 8px; font-size: 11px; }
            QRadioButton::indicator { width: 14px; height: 14px; border-radius: 8px; border: 2px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.1); }
            QRadioButton::indicator:checked { background: #0078d4; border: 2px solid #0078d4; }
            QRadioButton::indicator:hover { border: 2px solid rgba(255,255,255,0.5); }
        """

        fields_def = [
            ("publisher", "Organización:"), ("app", "ID Interno (Slug):"), 
            ("name", "Nombre Público:"), ("version", "Versión:"), 
            ("author", "Autor (GitHub):"), ("platform", "Plataforma Base:")
        ]

        current_row = 0
        for key, label_text in fields_def:
            value = str(xml_data.get(key, "")).strip()
            is_generic = value.lower() in ["1.0", "myorg", "appid", "public name", "unknown", "none", ""]
            is_invalid_v = key == "version" and "-" in value 
            
            should_show = self.results[index]["is_invalid"] or is_generic or is_invalid_v
            
            if key == "platform":
                if should_show:
                    lbl = QLabel(label_text)
                    lbl.setStyleSheet("color: #aaa; font-weight: 500;")
                    form_layout.addWidget(lbl, current_row, 0)
                    
                    p_box = QHBoxLayout()
                    p_group = QButtonGroup(page)
                    rad_win = QRadioButton("Windows")
                    rad_lin = QRadioButton("Linux")
                    rad_multi = QRadioButton("Multi")
                    for r in [rad_win, rad_lin, rad_multi]:
                        r.setStyleSheet(RADIO_QSS)
                        p_group.addButton(r)
                        p_box.addWidget(r)
                    
                    if "win" in value.lower(): rad_win.setChecked(True)
                    elif "lin" in value.lower(): rad_lin.setChecked(True)
                    else: rad_multi.setChecked(True)
                    form_layout.addLayout(p_box, current_row, 1)
                    
                    class PlatformProxy:
                        def __init__(self, w, l, m): self.w, self.l, self.m = w, l, m
                        def text(self):
                            if self.w.isChecked(): return "Windows"
                            if self.l.isChecked(): return "Linux"
                            return "Multiplataforma"
                        def setText(self, t):
                            if "win" in t.lower(): self.w.setChecked(True)
                            elif "lin" in t.lower(): self.l.setChecked(True)
                            else: self.m.setChecked(True)
                    self.results[index]["inputs"][key] = PlatformProxy(rad_win, rad_lin, rad_multi)
                    current_row += 1
                else:
                    self.results[index]["inputs"][key] = FixedProxy(value)
                continue

            if should_show:
                lbl = QLabel(label_text)
                lbl.setStyleSheet("color: #aaa; font-weight: 500;")
                edit = QLineEdit(value)
                edit.setFixedHeight(30)
                edit.setStyleSheet(EDIT_QSS)
                if not value or is_generic:
                    edit.setPlaceholderText("Campo obligatorio...")
                    edit.setStyleSheet(edit.styleSheet() + "QLineEdit { border-left: 3px solid #f44336; }")
                
                form_layout.addWidget(lbl, current_row, 0)
                form_layout.addWidget(edit, current_row, 1)
                self.results[index]["inputs"][key] = edit
                
                if key == "version":
                    def on_v_change(txt, idx=index):
                        v_cl = self.clean_version_str(txt)
                        inputs = self.results[idx]["inputs"]
                        if "author" in inputs and not inputs["author"].text(): inputs["author"].setText("JesusQuijada34")
                        if "publisher" in inputs and not inputs["publisher"].text(): inputs["publisher"].setText("Influent")
                        if "app" in inputs and (not inputs["app"].text() or "appid" in inputs["app"].text().lower()):
                             inputs["app"].setText(f"app-v{v_cl.replace('.','')}")
                    edit.textChanged.connect(on_v_change)
                current_row += 1
            else:
                self.results[index]["inputs"][key] = FixedProxy(value)

        missing_icons = [i for i in proj_data["issues"] if "icon" in i["type"] or "logo" in i["type"]]
        missing_assets = [i for i in proj_data["issues"] if "splash" in i["type"]]
        
        if missing_icons or missing_assets:
            pack_box = QHBoxLayout()
            pack_box.setSpacing(10)
            btn_pack_css = (
                "QPushButton { background: #0078d4; color: white; border-radius: 4px;"
                " padding: 4px 10px; font-weight: 600; font-size: 11px; min-height: 28px; }"
                " QPushButton:hover { background: #106ebe; }"
            )
            
            if missing_icons:
                btn_i = QPushButton("Subir Icon Pack")
                btn_i.setStyleSheet(btn_pack_css)
                btn_i.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_i.clicked.connect(lambda: self.upload_icon_pack(index))
                pack_box.addWidget(btn_i)
            if missing_assets:
                btn_a = QPushButton("Subir Asset Pack")
                btn_a.setStyleSheet(btn_pack_css.replace("#0078d4", "#28a745"))
                btn_a.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_a.clicked.connect(lambda: self.upload_asset_pack(index))
                pack_box.addWidget(btn_a)
            pack_box.addStretch()
            form_layout.addLayout(pack_box, current_row, 1)
            current_row += 1

        # Hidden Proxies for assets (handled via Pack Uploads)
        for i in proj_data["issues"]:
            if i["type"] in ["missing_icon", "missing_icon_updater", "missing_logo", "missing_splash", "missing_splash_setup"]:
                key_map = {"missing_icon": "icon", "missing_icon_updater": "icon_updater", "missing_logo": "logo", "missing_splash": "splash", "missing_splash_setup": "splash_setup"}
                k = key_map[i["type"]]
                
                class HiddenProxy:
                    def __init__(self): self.val = ""
                    def text(self): return self.val
                    def setText(self, t): self.val = t
                
                # Only Create if it doesn't exist
                if f"extra_{k}" not in self.results[index]["inputs"]:
                    self.results[index]["inputs"][f"extra_{k}"] = HiddenProxy()

        scroll.setWidget(form_content)
        layout.addWidget(scroll)
        
        # GitHub Verification row
        gh_btn = QPushButton("Verificar GitHub")
        gh_btn.setFixedHeight(30)
        gh_btn.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 5px; font-size: 11px; }")
        gh_status = QLabel("Pendiente")
        gh_status.setStyleSheet("color: #777; font-size: 10px;")
        def verify_gh(idx=index, status_lbl=gh_status):
            user = self.results[idx]["inputs"]["author"].text().strip()
            ok, msg = verificar_github_username(user)
            status_lbl.setText("✅ OK" if ok else f"❌ {msg}")
            status_lbl.setStyleSheet(f"color: {'#4caf50' if ok else '#f44336'}; font-size: 10px;")
        gh_btn.clicked.connect(verify_gh)
        layout.addSpacing(5)
        gh_row = QHBoxLayout()
        gh_row.addWidget(gh_btn)
        gh_row.addWidget(gh_status)
        gh_row.addStretch()
        layout.addLayout(gh_row)
        
        return page

    def create_page_done(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("✨")
        icon.setStyleSheet("font-size: 60px;")
        layout.addWidget(icon)

        title = QLabel("Ecosistema Sanado")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(title)

        self.done_desc = QLabel("Se han procesado todos los proyectos exitosamente y sus configuraciones han sido normalizadas.")
        self.done_desc.setStyleSheet("color: #aaa; font-size: 15px;")
        self.done_desc.setWordWrap(True)
        self.done_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.done_desc)
        
        return page

    def clean_version_str(self, v):
        if not v: return "1.0.0"
        prohibited = ["danenone", "knosthalij", "keystone", "windows", "linux", "darwin", "macos", "win", "nix"]
        parts = re.split(r'([-_])', v)
        new_parts = []
        for p in parts:
            if p.lower() in prohibited:
                continue
            new_parts.append(p)
        res = "".join(new_parts)
        res = re.sub(r'[-_]{2,}', '-', res)
        res = res.strip('-_')
        return res if res else "1.0.0"

    def go_next(self):
        curr = self.stack.currentIndex()
        
        # Validation for project pages
        if 0 < curr < self.stack.count() - 1:
            idx = curr - 1
            # Check mandatory fields (Skip extra_ assets as they are hidden/optional-via-pack)
            inputs = self.results[idx]["inputs"]
            for k, edit in inputs.items():
                if k.startswith("extra_"): continue # Skip asset validation here
                if not edit.text().strip():
                    LeviathanDialog.launch(self, "Campo Requerido", f"El campo '{k}' es obligatorio para continuar.", mode="warning")
                    return
            
            # Apply fixes for this project
            self.apply_project_fixes(idx)

        if curr < self.stack.count() - 1:
            self.fade_to_page(curr + 1)
            self.update_nav()
        else:
            self.accept()

    def fade_to_page(self, index):
        """Transición suave con opacidad y desplazamiento lateral (W11 Inspired)."""
        old_widget = self.stack.currentWidget()
        new_widget = self.stack.widget(index)
        
        # Clean previous page anims
        for a in self._active_anims:
            if a.state() == QtCore.QAbstractAnimation.Running:
                a.stop()
        self._active_anims.clear()
        
        # Setup opacity effect for both to avoid flickering
        eff_new = QtWidgets.QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(eff_new)
        
        self.stack.setCurrentIndex(index)
        new_widget.show() # Ensure it's active
        new_widget.raise_()
        
        anim = QtCore.QPropertyAnimation(eff_new, b"opacity")
        anim.setDuration(450)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QtCore.QEasingCurve.Type.OutQuart)
        
        # Slide for the new page
        final_pos = QtCore.QPoint(0, 0)
        new_widget.move(20, 0) 
        anim_pos = QtCore.QPropertyAnimation(new_widget, b"pos")
        anim_pos.setDuration(450)
        anim_pos.setStartValue(new_widget.pos())
        anim_pos.setEndValue(final_pos)
        anim_pos.setEasingCurve(QtCore.QEasingCurve.Type.OutQuart)
        
        # Store references and start
        self._active_anims.extend([anim, anim_pos])
        anim.start()
        anim_pos.start()
        
        # Ensure all controls are repainted
        new_widget.update()
        QtWidgets.QApplication.processEvents()

    def update_nav(self):
        curr = self.stack.currentIndex()
        total = self.stack.count()
        self.lbl_step.setText(f"Página {curr + 1} de {total}")
        
        # Reset to UWP accent for all states, changing only text/icons
        if curr == 0:
            self.btn_next.setText("Empezar")
        elif curr == total - 1:
            self.btn_next.setText("Finalizar")
        else:
            self.btn_next.setText("Siguiente →")

    def apply_project_fixes(self, idx):
        proj = self.projects[idx]
        path = proj["path"]
        inputs = self.results[idx]["inputs"]

        publisher = inputs.get("publisher").text().strip() or "influent"
        app_id = inputs.get("app").text().strip() or os.path.basename(path)
        name_public = inputs.get("name").text().strip() or app_id.capitalize()
        version_raw = inputs.get("version").text().strip() or "1.0.0"
        author = inputs.get("author").text().strip() or "Unknown"
        platform_sel = inputs.get("platform").text().strip() or "Knosthalij"
        version_base = self.clean_version_str(version_raw)

        from pathlib import Path
        from lib.template_engine import normalize_platform, repair_project_from_templates

        repair_project_from_templates(
            Path(path),
            publisher,
            app_id.lower().replace(" ", "-"),
            name_public,
            author,
            normalize_platform(platform_sel),
            version_base=version_base,
            description="Proyecto reparado por MoonFix Suite",
        )

        # Asset Restoration
        # App Icon & Logo
        icon_src = inputs.get("extra_icon").text().strip() if inputs.get("extra_icon") else ""
        logo_src = inputs.get("extra_logo").text().strip() if inputs.get("extra_logo") else ""
        
        if icon_src and os.path.exists(icon_src):
            shutil.copy(icon_src, os.path.join(path, "app", "app-icon.ico"))
            # En Linux, también convertir a PNG
            if sys.platform.startswith("linux"):
                try:
                    from lib.linux_icon_handler import convert_ico_to_png
                    png_path = os.path.join(path, "app", "app-icon.png")
                    convert_ico_to_png(os.path.join(path, "app", "app-icon.ico"), png_path)
                except Exception:
                    pass
        
        if logo_src and os.path.exists(logo_src):
            shutil.copy(logo_src, os.path.join(path, "app", "product_logo.png"))
        elif icon_src and os.path.exists(icon_src):
            # Fallback if logo is missing but icon is provided (convert or just copy as placeholder)
            shutil.copy(icon_src, os.path.join(path, "app", "product_logo.png"))
        
        # Updater Icon
        upd_icon_src = inputs.get("extra_icon_updater").text().strip() if inputs.get("extra_icon_updater") else ""
        if upd_icon_src and os.path.exists(upd_icon_src):
            shutil.copy(upd_icon_src, os.path.join(path, "app", "updater-icon.ico"))
        
        splash_src = inputs.get("extra_splash").text().strip() if inputs.get("extra_splash") else ""
        if splash_src and os.path.exists(splash_src):
            shutil.copy(splash_src, os.path.join(path, "assets", "splash.png"))

        splash_setup_src = inputs.get("extra_splash_setup").text().strip() if inputs.get("extra_splash_setup") else ""
        if splash_setup_src and os.path.exists(splash_setup_src):
            shutil.copy(splash_setup_src, os.path.join(path, "assets", "splash_Setup.png"))

    def upload_icon_pack(self, index):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar Icon Pack", "", "Icon Pack (*.ipm-iconpck)")
        if f: self.process_ipm_iconpck(f)

    def upload_asset_pack(self, index):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar Asset Pack", "", "Asset Pack (*.ipm-assetpck)")
        if f: self.process_ipm_assetpck(f)

    def _uwp_close_then(self, callback):
        if getattr(self, "_closing", False):
            return
        self._closing = True

        def done():
            callback()
            self.deleteLater()

        play_bounce_down_close(self, on_finished=done, drop_px=72)

    def reject(self):
        self._uwp_close_then(super().reject)

    def accept(self):
        self._uwp_close_then(super().accept)


# Aliases to satisfy the user request for QSetup/QInstaller names
QSetup = MoonFixWizard
QInstaller = MoonFixWizard


def verificar_github_username(username):
    """Verifica si un username de GitHub existe. Si no hay internet, deja pasar el username."""
    if not username or not username.strip():
        return False, "El username no puede estar vacío"
    username = username.strip()
    url = f"https://api.github.com/users/{username}"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "Username válido"
            else:
                return False, f"Username no encontrado (código: {response.status})"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "El username no existe en GitHub"
        else:
            return False, f"Error al verificar: {e.code}"
    except urllib.error.URLError as e:
        # Si no hay internet, se permite el username
        return True, "Conexión a internet no disponible, se permite el username"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def detectar_modo_sistema():
    """Detecta el modo claro/oscuro del sistema operativo"""
    if sys.platform.startswith("win"):
        # Windows: leer del registro
        try:
            if winreg:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                try:
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    return value == 0  # 0 = oscuro, 1 = claro
                except FileNotFoundError:
                    # Si no existe la clave, asumir modo claro
                    return False
            else:
                # Fallback: usar la paleta de Qt
                app = QApplication.instance()
                if app:
                      palette = app.palette()
                      return palette.color(QtGui.QPalette.ColorRole.Window).lightness() < 128
                return False
        except Exception:
            # Fallback: usar la paleta de Qt
            app = QApplication.instance()
            if app:
                palette = app.palette()
                return palette.color(QtGui.QPalette.Window).lightness() < 128
            return False
    elif sys.platform.startswith("linux"):
        # Linux: intentar con gsettings (GNOME) o xfconf (XFCE)
        try:
            # Intentar gsettings primero (GNOME)
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                theme = result.stdout.strip().lower()
                return "dark" in theme
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        try:
            # Intentar xfconf (XFCE)
            result = subprocess.run(
                ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                theme = result.stdout.strip().lower()
                return "dark" in theme
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Fallback: leer archivo de configuración
        try:
            theme_file = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
            if os.path.exists(theme_file):
                with open(theme_file, 'r') as f:
                    content = f.read().lower()
                    return "dark" in content
        except Exception:
            pass
        
        # Último fallback: usar la paleta de Qt
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return palette.color(QtGui.QPalette.Window).lightness() < 128
        return False
    else:
        # Otros sistemas: usar la paleta de Qt
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return palette.color(QtGui.QPalette.Window).lightness() < 128
        return False

