# -*- coding: utf-8 -*-
"""Panel de configuración en tarjetas (Fase 3.2 de ``bugs.txt``).

La raíz es una lista de tarjetas —icono a la izquierda, flecha a la derecha— y
cada una abre su detalle con un desplazamiento horizontal. El guardado es
automático: los detalles de selección múltiple confirman al retroceder y los de
selección única se aplican y vuelven solos.

El panel no guarda nada por su cuenta: expone ``widgets`` (los controles que el
resto de la ventana ya conocía por nombre) y avisa al anfitrión con
``settingsChanged`` para que persista y aplique los cambios.
"""

from __future__ import annotations

from typing import Dict, Optional

try:
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    def pyqtSignal(*args, **kwargs):  # type: ignore[no-redef]
        return None


from lib.design_tokens import TEXT, TEXT_DIM, uwp_button_qss
from lib.fluent_theme import conf_field_stylesheet
from lib.i18n import tr
from lib.pm_data import coerce_float, coerce_int
from lib.settings_cards import (
    ARROW_EXTERNAL,
    ARROW_FORWARD,
    SettingsCard,
    SettingsDetailPage,
    SettingsListPage,
    SettingsNavigator,
    SettingsOptionRow,
    card_icon,
    section_caption,
)

AUTOSAVE_DELAY_MS = 350


class SettingsPanel(QWidget):
    """Configuración completa: tarjetas raíz y detalles.

    La navegación se comunica al anfitrión con ``navigationChanged`` (título,
    profundidad y texto de confirmación) para que la página coloque la flecha
    de retroceso y el botón de confirmar en **su** barra de acciones: el panel
    no dibuja una segunda barra.
    """

    settingsChanged = pyqtSignal()
    resetRequested = pyqtSignal()
    fontsRequested = pyqtSignal()
    languageChanged = pyqtSignal(str)
    fontChosen = pyqtSignal(str)
    networkModeChanged = pyqtSignal(str)
    navigationChanged = pyqtSignal(str, int, str)

    def __init__(self, host, user: Dict[str, object], parent=None):
        super().__init__(parent)
        self.host = host
        self.widgets: Dict[str, object] = {}
        self._cards: Dict[str, SettingsCard] = {}
        self._pages: Dict[str, SettingsDetailPage] = {}
        self._language_rows: Dict[str, SettingsOptionRow] = {}
        self._font_rows: Dict[str, SettingsOptionRow] = {}
        self._network_rows: Dict[str, SettingsOptionRow] = {}
        self._network_mode = str(user.get("network_mode") or "unrestricted")
        self._titles: Dict[str, str] = {}
        self._title_keys: Dict[str, str] = {}
        self._subtitle_keys: Dict[str, str] = {}
        self._multi_details = set()
        self._current_key = None
        self._accent = TEXT
        self._loading = True

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.navigator = SettingsNavigator()
        self.navigator.depthChanged.connect(self._on_depth_changed)
        root.addWidget(self.navigator, 1)

        self.root_page = SettingsListPage()
        self._build_cards(user)
        self.navigator.set_root(self.root_page)

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(AUTOSAVE_DELAY_MS)
        self._autosave_timer.timeout.connect(self._emit_changed)

        self._connect_autosave()
        self._loading = False

    # --- Construcción ---------------------------------------------------
    def _build_cards(self, user: Dict[str, object]) -> None:
        store_base = user.get("base_dir")
        store_fluthin = user.get("fluthin_apps")

        # General: rutas y traducción automática (selección múltiple).
        general = SettingsDetailPage(tr("config.section_general"))
        general.add_widget(section_caption(tr("config.section_general")))

        self.widgets["conf_base_dir"] = self._path_row(
            general, tr("config.projects_path"), str(store_base or ""), self._browse_projects
        )
        self.widgets["conf_fluthin_dir"] = self._path_row(
            general, tr("config.fluthin_path"), str(store_fluthin or ""), self._browse_fluthin
        )
        auto_translate = QCheckBox(tr("config.auto_translate"))
        auto_translate.setChecked(bool(user.get("auto_translate", True)))
        self.widgets["conf_auto_translate"] = auto_translate
        general.add_widget(auto_translate)
        general.add_widget(self._hint(tr("config.auto_translate_hint")))
        general.add_stretch()
        self._register_card(
            "general", tr("config.section_general"), "config", general, multi=True,
            subtitle=tr("config.section_general_hint"),
            title_key="config.section_general",
            subtitle_key="config.section_general_hint",
        )

        # Idioma: selección única, se aplica y vuelve sola.
        language = SettingsDetailPage(tr("config.section_language"))
        language.add_widget(section_caption(tr("config.language")))
        try:
            from lib.i18n import get_available_languages

            languages = get_available_languages()
        except Exception:
            languages = [("es", "Español"), ("en", "English")]
        current_lang = str(user.get("language") or "es")
        for code, name in languages:
            row = SettingsOptionRow(name, code, checked=code == current_lang)
            row.chosen.connect(self._on_language_chosen)
            self._language_rows[code] = row
            language.add_widget(row)
        language.add_stretch()
        self._register_card(
            "language", tr("config.section_language"), "language", language,
            subtitle=tr("config.section_language_hint"),
            title_key="config.section_language",
            subtitle_key="config.section_language_hint",
        )

        # Apariencia: densidad + sliders (selección múltiple).
        appearance = SettingsDetailPage(tr("config.section_appearance"))
        appearance.add_widget(section_caption(tr("config.section_appearance")))
        density = QComboBox()
        density.addItem(tr("config.density_normal"), "normal")
        density.addItem(tr("config.density_compact"), "compact")
        idx = density.findData(str(user.get("ui_density") or "normal"))
        if idx >= 0:
            density.setCurrentIndex(idx)
        density.setStyleSheet(conf_field_stylesheet())
        self.widgets["conf_ui_density"] = density
        appearance.add_widget(self._labelled(tr("config.ui_density"), density))
        self.widgets["conf_sidebar_accent_slider"] = self._slider_row(
            appearance,
            tr("config.sidebar_accent"),
            0,
            8,
            coerce_int(user.get("sidebar_accent_width", 3), 3) or 0,
            " px",
        )
        self.widgets["conf_card_opacity_slider"] = self._slider_row(
            appearance,
            tr("config.card_opacity"),
            0,
            40,
            int(coerce_float(user.get("card_opacity", 0.08), 0.08) * 100),
            " %",
        )
        appearance.add_widget(self._hint(tr("config.personalization_hint")))
        appearance.add_stretch()
        self._register_card(
            "appearance", tr("config.section_appearance"), "palette", appearance, multi=True,
            subtitle=tr("config.section_appearance_hint"),
            title_key="config.section_appearance",
            subtitle_key="config.section_appearance_hint",
        )

        # Notificaciones y táctil (selección múltiple).
        notices = SettingsDetailPage(tr("config.section_notifications"))
        notices.add_widget(section_caption(tr("config.section_notifications")))
        notifications = QCheckBox(tr("config.notifications"))
        notifications.setChecked(bool(user.get("notifications_enabled", False)))
        self.widgets["conf_notifications"] = notifications
        notices.add_widget(notifications)
        touch = QCheckBox(tr("config.touch_mode"))
        touch.setChecked(bool(user.get("touch_mode", False)))
        self.widgets["conf_touch_mode"] = touch
        notices.add_widget(touch)
        notices.add_widget(self._hint(tr("config.touch_mode_hint")))
        notices.add_stretch()
        self._register_card(
            "notifications", tr("config.section_notifications"), "touch", notices, multi=True,
            subtitle=tr("config.section_notifications_hint"),
            title_key="config.section_notifications",
            subtitle_key="config.section_notifications_hint",
        )

        # Fuentes: estado en caché + descarga manual.
        fonts = SettingsDetailPage(tr("config.section_fonts"))
        fonts.add_widget(section_caption(tr("config.section_fonts")))
        self.conf_fonts_labels = {}
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)
        try:
            from lib.font_manager import available_fonts_report

            for row_index, (key, info) in enumerate(available_fonts_report().items()):
                name_lbl = QLabel(info["family"])
                name_lbl.setStyleSheet(
                    f"color:{TEXT};font-family:'Segoe UI';font-size:12px;background:transparent;"
                )
                state_lbl = QLabel(
                    tr("config.fonts_cached") if info["cached"] else tr("config.fonts_missing")
                )
                state_lbl.setStyleSheet(
                    f"color:{TEXT_DIM};font-size:11px;background:transparent;"
                )
                self.conf_fonts_labels[key] = state_lbl
                grid.addWidget(name_lbl, row_index, 0)
                grid.addWidget(state_lbl, row_index, 1)
        except Exception:
            pass
        fonts.add_widget(grid_host)

        # Selección manual de la fuente de interfaz entre las de la caché.
        fonts.add_widget(section_caption(tr("config.font_family")))
        current_family = str(user.get("ui_font_family") or "")
        auto_row = SettingsOptionRow(tr("config.font_auto"), "", checked=current_family == "")
        auto_row.chosen.connect(self._on_font_chosen)
        self._font_rows[""] = auto_row
        fonts.add_widget(auto_row)
        try:
            from lib.font_manager import available_fonts_report

            for key, info in available_fonts_report().items():
                family = str(info["family"])
                row = SettingsOptionRow(
                    family, family, checked=family == current_family
                )
                row.chosen.connect(self._on_font_chosen)
                self._font_rows[family] = row
                fonts.add_widget(row)
        except Exception:
            pass

        fonts_row = QHBoxLayout()
        self.widgets["conf_fonts_btn"] = QPushButton(tr("config.fonts_download"))
        fonts_btn = self.widgets["conf_fonts_btn"]
        fonts_btn.setFixedHeight(36)
        fonts_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fonts_btn.setStyleSheet(uwp_button_qss())
        fonts_btn.clicked.connect(self.fontsRequested.emit)
        fonts_row.addWidget(fonts_btn)
        fonts_row.addStretch()
        fonts.add_layout(fonts_row)
        self.widgets["conf_fonts_status"] = QLabel("")
        self.widgets["conf_fonts_status"].setStyleSheet(
            f"color:{TEXT_DIM};font-size:11px;background:transparent;"
        )
        self.widgets["conf_fonts_status"].setWordWrap(True)
        fonts.add_widget(self.widgets["conf_fonts_status"])
        fonts.add_stretch()
        self._register_card(
            "fonts", tr("config.section_fonts"), "download", fonts,
            subtitle=tr("config.section_fonts_hint"),
            title_key="config.section_fonts",
            subtitle_key="config.section_fonts_hint",
        )

        # Red: compilación aislada o uso medido (Q-019).
        network = SettingsDetailPage(tr("config.section_network"))
        network.add_widget(section_caption(tr("config.section_network")))
        for mode in ("unrestricted", "metered"):
            row = SettingsOptionRow(
                tr(f"config.network_{mode}"), mode, checked=mode == self._network_mode
            )
            row.chosen.connect(self._on_network_mode_chosen)
            self._network_rows[mode] = row
            network.add_widget(row)
        network.add_widget(self._hint(tr("config.network_hint")))
        network.add_stretch()
        self._register_card(
            "network", tr("config.section_network"), "download", network,
            subtitle=tr("config.section_network_hint"),
            title_key="config.section_network",
            subtitle_key="config.section_network_hint",
        )

        # Privacidad: control del túnel de reportes y del endpoint propio.
        privacy = SettingsDetailPage(tr("config.section_privacy"))
        privacy.add_widget(section_caption(tr("config.section_privacy")))

        telemetry = QCheckBox(tr("config.telemetry_enabled"))
        telemetry.setChecked(bool(user.get("auto_report_errors", True)))
        self.widgets["conf_telemetry"] = telemetry
        privacy.add_widget(telemetry)
        privacy.add_widget(self._hint(tr("config.telemetry_hint")))

        endpoint = QCheckBox(tr("config.telemetry_endpoint_enabled"))
        endpoint.setChecked(bool(user.get("telemetry_enabled", False)))
        self.widgets["conf_telemetry_endpoint"] = endpoint
        privacy.add_widget(endpoint)
        self._endpoint_field = QLineEdit(str(user.get("telemetry_endpoint", "") or ""))
        self._endpoint_field.setStyleSheet(conf_field_stylesheet())
        self._endpoint_field.setPlaceholderText("https://…")
        self.widgets["conf_telemetry_url"] = self._endpoint_field
        privacy.add_widget(
            self._labelled(tr("config.telemetry_endpoint_url"), self._endpoint_field)
        )
        privacy.add_widget(self._hint(tr("config.telemetry_endpoint_hint")))
        privacy.add_stretch()
        self._register_card(
            "privacy", tr("config.section_privacy"), "shield", privacy, multi=True,
            subtitle=tr("config.section_privacy_hint"),
            title_key="config.section_privacy",
            subtitle_key="config.section_privacy_hint",
        )

        self.root_page.add_stretch()
        self._add_reset_card()
        self.root_page.add_stretch()

    def _register_card(
        self, key, title, icon, page, multi=False, subtitle="",
        title_key="", subtitle_key="",
    ):
        card = SettingsCard(title, card_icon(icon), ARROW_FORWARD, subtitle)
        card.clicked.connect(lambda k=key: self._open(k))
        self._cards[key] = card
        self._titles[key] = title
        self._title_keys[key] = title_key
        self._subtitle_keys[key] = subtitle_key
        self._pages[key] = page
        if multi:
            self._multi_details.add(key)
        self.root_page.add_card(card)
        return card

    def _add_reset_card(self) -> None:
        card = SettingsCard(
            tr("config.reset"), card_icon("restart"), ARROW_EXTERNAL, tr("config.reset_hint")
        )
        card.clicked.connect(self.resetRequested.emit)
        self._cards["reset"] = card
        self._title_keys["reset"] = "config.reset"
        self._subtitle_keys["reset"] = "config.reset_hint"
        self.root_page.add_card(card)

    # --- Controles auxiliares -------------------------------------------
    def _labelled(self, text, widget):
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(10)
        label = QLabel(text)
        label.setMinimumWidth(180)
        label.setStyleSheet(f"color:{TEXT};font-size:12px;background:transparent;")
        box.addWidget(label)
        box.addWidget(widget, 1)
        return row

    def _path_row(self, page, label_text, value, browse_slot):
        field = QLineEdit(value)
        field.setStyleSheet(conf_field_stylesheet())
        button = QPushButton(tr("config.browse"))
        button.setFixedHeight(34)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(uwp_button_qss())
        button.clicked.connect(browse_slot)
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(8)
        box.addWidget(field, 1)
        box.addWidget(button)
        page.add_widget(self._labelled(label_text, row))
        return field

    def _slider_row(self, page, label_text, minimum, maximum, value, suffix=""):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setValue(int(value))
        slider.setFixedHeight(24)
        value_lbl = QLabel(f"{int(value)}{suffix}")
        value_lbl.setMinimumWidth(46)
        value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_lbl.setStyleSheet(f"color:{TEXT_DIM};font-size:11px;background:transparent;")
        slider.valueChanged.connect(
            lambda v, lbl=value_lbl, s=suffix: lbl.setText(f"{int(v)}{s}")
        )
        row = QWidget()
        box = QHBoxLayout(row)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(10)
        box.addWidget(slider, 1)
        box.addWidget(value_lbl)
        page.add_widget(self._labelled(label_text, row))
        return slider

    def _hint(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color:{TEXT_DIM};font-size:11px;background:transparent;")
        return label

    # --- Navegación -----------------------------------------------------
    def _open(self, key: str) -> None:
        page = self._pages.get(key)
        if page is None or self.navigator.busy() or key == self._current_key:
            return
        self._current_key = key
        self.navigator.push(page)

    def go_back(self) -> None:
        if self.navigator.busy() or self.navigator.depth() == 0:
            return
        key = self._current_key
        if key in self._multi_details:
            # Guardado validado al retroceder.
            self._emit_changed()
        self._current_key = None
        self.navigator.pop()

    def confirm_and_go_back(self) -> None:
        self._emit_changed()
        self.go_back()

    def _on_depth_changed(self, depth: int) -> None:
        if depth == 0:
            for card in self._cards.values():
                card.set_selected(False)
        self._emit_navigation(depth)

    def _emit_navigation(self, depth: Optional[int] = None) -> None:
        """Anuncia el estado de navegación para la barra de acciones de la página.

        ``depth`` llega desde la pila porque durante la animación de salida la
        página todavía no se ha retirado y ``depth()`` seguiría en el valor
        anterior.
        """
        if depth is None:
            depth = self.navigator.depth()
        title = tr("config.title")
        confirm = ""
        if depth > 0:
            title = self._titles.get(self._current_key, "") or title
            if self._current_key in self._multi_details:
                confirm = tr("config.confirm")
        self.navigationChanged.emit(title, depth, confirm)

    def _on_language_chosen(self, code: str) -> None:
        """Selección única: marca, aplica y vuelve sola."""
        for lang_code, row in self._language_rows.items():
            row.set_checked(lang_code == code)
        self.languageChanged.emit(code)
        self._emit_changed()
        QTimer.singleShot(120, self.go_back)

    def network_mode(self) -> str:
        """Modo de red elegido (``unrestricted`` o ``metered``)."""
        return self._network_mode

    def _on_network_mode_chosen(self, mode: str) -> None:
        """Selección única: marca, aplica y vuelve sola."""
        self._network_mode = str(mode)
        for key, row in self._network_rows.items():
            row.set_checked(key == self._network_mode)
        self.networkModeChanged.emit(self._network_mode)
        self._emit_changed()
        QTimer.singleShot(120, self.go_back)

    def _on_font_chosen(self, family: str) -> None:
        """Selección única: marca, aplica y vuelve sola."""
        for key, row in getattr(self, "_font_rows", {}).items():
            row.set_checked(key == family)
        self.fontChosen.emit(family)
        self._emit_changed()
        QTimer.singleShot(120, self.go_back)

    # --- Guardado -------------------------------------------------------
    def _connect_autosave(self) -> None:
        for key in ("conf_base_dir", "conf_fluthin_dir", "conf_telemetry_url"):
            widget = self.widgets.get(key)
            if widget is not None:
                widget.textChanged.connect(self._schedule_save)
        for key in (
            "conf_auto_translate",
            "conf_notifications",
            "conf_touch_mode",
            "conf_telemetry",
            "conf_telemetry_endpoint",
        ):
            widget = self.widgets.get(key)
            if widget is not None:
                widget.toggled.connect(self._schedule_save)
        for key in ("conf_ui_density",):
            widget = self.widgets.get(key)
            if widget is not None:
                widget.currentIndexChanged.connect(self._schedule_save)
        for key in ("conf_sidebar_accent_slider", "conf_card_opacity_slider"):
            widget = self.widgets.get(key)
            if widget is not None:
                widget.valueChanged.connect(self._schedule_save)

    def flush_autosave(self) -> None:
        """Cierra el guardado pendiente antes de cerrar la ventana.

        Sin esto el temporizador sobrevive al cierre y escribe ajustes de una
        ventana ya cerrada, pisando el almacén activo en ese momento.
        """
        if not self._autosave_timer.isActive():
            return
        self._autosave_timer.stop()
        self._emit_changed()

    def _schedule_save(self, *_args) -> None:
        if self._loading:
            return
        self._autosave_timer.start()

    def _emit_changed(self) -> None:
        if self._loading:
            return
        self.settingsChanged.emit()

    # --- Acciones delegadas al anfitrión --------------------------------
    def _browse_projects(self) -> None:
        host = self.host
        if hasattr(host, "_browse_config_dir"):
            host._browse_config_dir()

    def _browse_fluthin(self) -> None:
        host = self.host
        if hasattr(host, "_browse_fluthin_dir"):
            host._browse_fluthin_dir()

    # --- Tema / idioma --------------------------------------------------
    def set_accent(self, accent: str) -> None:
        self._accent = accent or TEXT
        self.root_page.set_accent(self._accent)
        for page in self._pages.values():
            for child in page.findChildren(SettingsOptionRow):
                child.set_accent(self._accent)

    def retranslate(self) -> None:
        """Reetiqueta tarjetas, títulos y opciones tras cambiar de idioma.

        Recorre todas las tarjetas registradas por su clave de traducción: una
        lista fija dejaba fuera las tarjetas nuevas (p. ej. Privacidad) y su
        flecha de retroceso aparecía sin nombre.
        """
        for key, title_key in self._title_keys.items():
            if not title_key:
                continue
            title = tr(title_key)
            self._titles[key] = title
            card = self._cards.get(key)
            if card is None:
                continue
            card.set_title(title)
            subtitle_key = self._subtitle_keys.get(key, "")
            if subtitle_key:
                card.set_subtitle(tr(subtitle_key))
        fonts_btn = self.widgets.get("conf_fonts_btn")
        if fonts_btn is not None:
            fonts_btn.setText(tr("config.fonts_download"))
        self._emit_navigation()
