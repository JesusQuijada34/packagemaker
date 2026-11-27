# -*- coding: utf-8 -*-
"""Página de ayuda global de la aplicación (Q-021, issue #11).

Una sola página con los temas de todas las áreas —crear, compilar, blindar y
reportar— y un buscador que filtra por título y cuerpo. Los textos viven en
``lang/*.json`` bajo ``help.*`` para que se traduzcan como el resto de la
interfaz; aquí sólo se decide qué temas hay y cómo se pintan.

Todo el color sale de ``lib/design_tokens``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QFrame,
        QLabel,
        QLineEdit,
        QScrollArea,
        QVBoxLayout,
        QWidget,
    )

    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin Qt (CLI headless)
    PYQT6_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass


from lib.design_tokens import (
    CONTENT_PADDING,
    TEXT,
    TEXT_DIM,
    TEXT_SOFT,
    card_qss,
    input_qss,
    scrollbar_qss,
)
from lib.i18n import tr
from lib.page_action_bar import install_page_action_bar

#: Temas de la ayuda, en el orden en que aparecen.
TOPIC_IDS: Tuple[str, ...] = ("start", "build", "harden", "report")


class HelpPage(QWidget):
    """Ayuda de toda la aplicación con buscador por tema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HelpPage")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING, CONTENT_PADDING
        )
        outer.setSpacing(10)

        self.action_bar, self.bar_title = install_page_action_bar(
            outer, tr("sidebar.help")
        )

        self.search_input = QLineEdit()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText(tr("help.search_placeholder"))
        self.search_input.setStyleSheet(input_qss())
        self.search_input.textChanged.connect(self._apply_filter)
        outer.addWidget(self.search_input)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}" + scrollbar_qss()
        )
        # Sin esto el viewport pinta el color base de la paleta y deja una
        # banda distinta del resto de la página (mismo defecto que issue #10).
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.viewport().setStyleSheet("background:transparent;")
        outer.addWidget(self.scroll, 1)

        body = QWidget()
        body.setObjectName("HelpBody")
        body.setStyleSheet("background:transparent;")
        self.scroll.setWidget(body)

        self._body_layout = QVBoxLayout(body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(16)

        self.intro_label = QLabel(tr("help.intro"))
        self.intro_label.setWordWrap(True)
        self.intro_label.setStyleSheet(f"color:{TEXT_DIM};font-size:12px;")
        self._body_layout.addWidget(self.intro_label)

        self._cards: Dict[str, Tuple[QFrame, QLabel, QLabel]] = {}
        for topic_id in TOPIC_IDS:
            self._cards[topic_id] = self._build_card(topic_id)

        self.empty_label = QLabel(tr("help.empty"))
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(f"color:{TEXT_DIM};font-size:13px;")
        self.empty_label.setVisible(False)
        self._body_layout.addWidget(self.empty_label)
        self._body_layout.addStretch(1)

    # ── construcción ────────────────────────────────────────────────────────

    def _build_card(self, topic_id: str) -> Tuple[QFrame, QLabel, QLabel]:
        card = QFrame()
        card.setObjectName(f"HelpCard_{topic_id}")
        card.setStyleSheet(card_qss())

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        title = QLabel(tr(f"help.topics.{topic_id}.title"))
        title.setWordWrap(True)
        title.setStyleSheet(f"color:{TEXT};font-size:15px;font-weight:600;")
        layout.addWidget(title)

        body = QLabel(tr(f"help.topics.{topic_id}.body"))
        body.setWordWrap(True)
        body.setStyleSheet(f"color:{TEXT_SOFT};font-size:13px;")
        layout.addWidget(body)

        self._body_layout.addWidget(card)
        return card, title, body

    # ── buscador ────────────────────────────────────────────────────────────

    def _apply_filter(self, text: str = "") -> None:
        needle = (text or "").strip().casefold()
        visible = 0
        for card, title, body in self._cards.values():
            matches = not needle or needle in (
                f"{title.text()}\n{body.text()}".casefold()
            )
            card.setVisible(matches)
            visible += int(matches)
        self.empty_label.setVisible(visible == 0)

    # ── idioma ──────────────────────────────────────────────────────────────

    def retranslate(self) -> None:
        """Reaplica los textos al idioma activo."""
        self.bar_title.setText(tr("sidebar.help"))
        self.search_input.setPlaceholderText(tr("help.search_placeholder"))
        self.intro_label.setText(tr("help.intro"))
        self.empty_label.setText(tr("help.empty"))
        for topic_id, (_card, title, body) in self._cards.items():
            title.setText(tr(f"help.topics.{topic_id}.title"))
            body.setText(tr(f"help.topics.{topic_id}.body"))
        self._apply_filter(self.search_input.text())

    # ── inspección (pruebas y accesibilidad) ────────────────────────────────

    def topic_ids(self) -> List[str]:
        return list(self._cards)

    def visible_topic_ids(self) -> List[str]:
        # ``isVisible`` es falso mientras la ventana no se muestra; ``isHidden``
        # refleja sólo el estado propio del widget.
        return [tid for tid, (card, _t, _b) in self._cards.items() if not card.isHidden()]
