"""Regresión: diálogo de alerta temático, botones verticales y efecto parcial.

Comprueba que:
- el fondo del diálogo es blanco o negro según el tema del sistema;
- los botones ocupan el ancho completo y se apilan en vertical con separadores;
- el efecto parcial (blur + atenuado) se instala al mostrar y se retira al
  cerrar, incluso cuando el cierre pasa por ``accept()``.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / name).read_text(encoding="utf-8")


class AlertDialogSourceTests(unittest.TestCase):
    def test_dialog_has_theme_palettes(self):
        text = source("lib/alert_dialog.py")
        self.assertIn("def _palette", text)
        self.assertIn('"bg": "#1c1c1e"', text)  # negro en tema oscuro
        self.assertIn('"bg": "#ffffff"', text)  # blanco en tema claro
        self.assertIn("system_theme_mode", text)

    def test_buttons_are_full_width_vertical_with_separators(self):
        text = source("lib/alert_dialog.py")
        self.assertIn("def _make_separator", text)
        self.assertIn("_default_index", text)
        # Los botones no llevan radio ni margen lateral: ancho completo.
        self.assertIn("border-radius: 0px", text)

    def test_all_button_states_are_styled(self):
        text = source("lib/alert_dialog.py")
        for state in (":hover", ":pressed", ":disabled"):
            self.assertIn(f"QPushButton{state}", text)


class PartialEffectSourceTests(unittest.TestCase):
    def test_overlay_blurs_and_dims(self):
        text = source("lib/dialog_effect.py")
        self.assertIn("ghostBlur", text)
        self.assertIn("QGraphicsBlurEffect", text)
        self.assertIn("OVERLAY_ALPHA", text)


try:
    from PyQt6.QtWidgets import QApplication, QPushButton, QWidget

    QT_AVAILABLE = True
except ImportError:  # pragma: no cover
    QT_AVAILABLE = False


@unittest.skipUnless(QT_AVAILABLE, "PyQt6 no disponible")
class AlertDialogQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _dialog(self, mode="question"):
        from lib.alert_dialog import AlertDialog

        dialog = AlertDialog(None, "Titulo", "Mensaje", mode=mode)
        dialog.show()
        self.app.processEvents()
        return dialog

    def test_buttons_stack_full_width(self):
        dialog = self._dialog()
        buttons = dialog.findChildren(QPushButton)
        self.assertEqual([b.text() for b in buttons], ["Cancelar", "Aceptar"])
        for button in buttons:
            self.assertEqual(button.width(), dialog.width())
        dialog.accept()

    def test_default_button_is_the_accepting_one(self):
        dialog = self._dialog()
        buttons = dialog.findChildren(QPushButton)
        self.assertTrue(buttons[-1].isDefault())
        dialog.accept()

    def test_accept_returns_one_and_reject_returns_zero(self):
        from lib.alert_dialog import _is_accept_text

        self.assertTrue(_is_accept_text("SI"))
        self.assertTrue(_is_accept_text("Aceptar"))
        self.assertFalse(_is_accept_text("NO"))
        self.assertFalse(_is_accept_text("Cancelar"))

    def test_overlay_is_removed_on_accept(self):
        from lib.dialog_effect import PartialEffectOverlay

        parent = QWidget()
        parent.resize(400, 300)
        from lib.alert_dialog import AlertDialog

        dialog = AlertDialog(parent, "Titulo", "Mensaje", "question")
        dialog.show()
        self.app.processEvents()
        self.assertIsNotNone(dialog._overlay)
        dialog.accept()
        self.app.processEvents()
        self.assertIsNone(dialog._overlay)
        self.assertEqual(dialog.findChildren(PartialEffectOverlay), [])

    def test_palette_differs_by_theme(self):
        from lib.alert_dialog import _palette

        self.assertNotEqual(_palette(True)["bg"], _palette(False)["bg"])


if __name__ == "__main__":
    unittest.main()
