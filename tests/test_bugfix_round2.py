# -*- coding: utf-8 -*-
"""Regresiones de la segunda ronda de bugs reportados.

Cubre con código real:

- resumen de errores largos por términos;
- realce del botón del diálogo que ya no se vuelve blanco;
- el fondo del splash se pinta con el acento;
- el texto gris pasa a negro en modo claro;
- el procedimiento real detrás del ``.iflapp`` se registra y se publica;
- no se acumulan filtros de efecto al maximizar (deriva a blanco);
- la pestaña "Crear" es opaca como el resto.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / name).read_text(encoding="utf-8")


class SummarizeMessageTests(unittest.TestCase):
    def test_short_message_is_returned_unchanged(self):
        from lib.report import summarize_message

        self.assertEqual(summarize_message("falló algo"), "falló algo")

    def test_long_traceback_keeps_error_lines(self):
        from lib.report import summarize_message

        noise = "\n".join(f"linea de ruido {i}" for i in range(200))
        message = f"{noise}\nTraceback (most recent call last):\nValueError: boom\n{noise}"
        summary = summarize_message(message)
        self.assertIn("ValueError: boom", summary)
        self.assertIn("Traceback", summary)
        self.assertLess(len(summary.splitlines()), 20)

    def test_long_message_without_terms_falls_back_to_edges(self):
        from lib.report import summarize_message

        message = "\n".join(f"paso {i}" for i in range(300))
        summary = summarize_message(message)
        self.assertIn("paso 0", summary)
        self.assertIn("paso 299", summary)
        self.assertIn("omitidas", summary)


class DialogHoverTests(unittest.TestCase):
    def test_default_button_hover_is_not_white(self):
        from PyQt6.QtWidgets import QApplication, QPushButton

        app = QApplication.instance() or QApplication([])
        from lib.alert_dialog import AlertDialog

        dialog = AlertDialog(None, "Titulo", "Mensaje", mode="info")
        dialog.show()
        app.processEvents()
        try:
            button = dialog.findChildren(QPushButton)[-1]
            qss = button.styleSheet()
            hover_block = qss.split(":hover")[1].split("}")[0]
            self.assertNotIn("255, 255, 255", hover_block)
            self.assertNotIn("white", hover_block.lower())
        finally:
            dialog.accept()

    def test_shift_color_lightens_and_darkens(self):
        from lib.alert_dialog import _shift_color

        self.assertEqual(_shift_color("#000000", 1.5), "#000000")
        self.assertEqual(_shift_color("#ffffff", 0.5), "#808080")
        self.assertEqual(_shift_color("#0078d4", 1.0), "#0078d4")


class SplashAccentTests(unittest.TestCase):
    def test_splash_uses_system_accent(self):
        text = source("packagemaker.py")
        splash = text.split("class IntegratedSplash")[1]
        self.assertIn("get_accent_color()", splash)
        self.assertNotIn("#1a1a1a", splash)


class LightModeTextTests(unittest.TestCase):
    def test_applyget_switches_text_to_black_in_light_theme(self):
        from lib.fluent_theme import applyget

        light = applyget("#0078d4", dark=False)
        self.assertIn("#000000", light)
        dark = applyget("#0078d4", dark=True)
        self.assertNotEqual(light, dark)

    def test_apply_theme_passes_dark_flag(self):
        text = source("packagemaker.py")
        self.assertIn("applyget(accent, dark)", text)


class CreateTabOpaqueTests(unittest.TestCase):
    def test_create_tab_is_not_translucent(self):
        text = source("packagemaker.py")
        create = text.split("def init_create_tab")[1].split("def init_build_tab")[0]
        self.assertIn("target.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)", create)
        self.assertNotIn(
            "target.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)", create
        )


class BuildArtifactCleanupTests(unittest.TestCase):
    def test_cleanup_removes_pyinstaller_and_nuitka_artifacts(self):
        import tempfile

        from lib.BuildThread import FlangCompiler

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            for name in ("dist", "build", "foundstore.build", "foundstore.onefile-build"):
                (project / name).mkdir()
            (project / "foundstore.spec").write_text("", encoding="utf-8")
            keep = project / "details.xml"
            keep.write_text("<app />", encoding="utf-8")

            compiler = FlangCompiler(project, Path(tmp) / "out")
            compiler._cleanup_build_artifacts()

            for name in ("dist", "build", "foundstore.build", "foundstore.onefile-build"):
                self.assertFalse((project / name).exists(), name)
            self.assertFalse((project / "foundstore.spec").exists())
            self.assertTrue(keep.exists())


class I18nCompletenessTests(unittest.TestCase):
    def _flatten(self, data, prefix=""):
        flat = {}
        for key, value in data.items():
            if key.startswith("_"):
                continue
            full = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._flatten(value, full))
            else:
                flat[full] = value
        return flat

    def test_every_tr_key_exists_in_the_spanish_catalog(self):
        import json
        import re

        catalog = self._flatten(json.loads((ROOT / "lang" / "es.json").read_text(encoding="utf-8")))
        used = set()
        for path in list(ROOT.glob("*.py")) + list(ROOT.glob("lib/*.py")):
            text = path.read_text(encoding="utf-8")
            used.update(re.findall(r'tr\(\s*"([^"]+)"', text))
        missing = sorted(key for key in used if key not in catalog)
        self.assertEqual(missing, [])

    def test_all_language_files_share_the_same_keys(self):
        import json

        base = set(self._flatten(json.loads((ROOT / "lang" / "es.json").read_text(encoding="utf-8"))))
        for path in sorted((ROOT / "lang").glob("*.json")):
            keys = set(self._flatten(json.loads(path.read_text(encoding="utf-8"))))
            self.assertFalse(base - keys, f"{path.name} carece de claves: {sorted(base - keys)}")


class BuildProcedureTests(unittest.TestCase):
    def test_flang_compiler_records_procedure(self):
        import tempfile

        from lib.BuildThread import FlangCompiler

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            compiler = FlangCompiler(project, Path(tmp) / "out")
            self.assertEqual(compiler.procedure, [])
            compiler._record_procedure("Paso de prueba")
            self.assertEqual(compiler.procedure, ["Paso de prueba"])

    def test_run_publishes_procedure_steps(self):
        text = source("lib/BuildThread.py")
        self.assertIn("Procedimiento detrás del .iflapp", text)
        self.assertIn("self._record_procedure(", text)


class WindowEffectsTests(unittest.TestCase):
    def test_reapplying_display_mode_releases_previous_effects(self):
        from PyQt6.QtWidgets import QApplication, QWidget

        app = QApplication.instance() or QApplication([])
        from lib.window_chrome import apply_display_mode

        window = QWidget()
        window.resize(400, 300)
        try:
            first = apply_display_mode(window, "GhostBlur (Cristal)")
            self.assertIs(window.window_effects, first)
            second = apply_display_mode(window, "GhostBlur (Cristal)")
            self.assertIsNot(first, second)
            self.assertIs(window.window_effects, second)
            # El efecto anterior queda desanclado de la ventana.
            self.assertIsNone(first.parent())
        finally:
            window.close()
            app.processEvents()


if __name__ == "__main__":
    unittest.main()
