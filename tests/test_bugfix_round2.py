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

    def test_all_pages_share_the_same_background(self):
        """Ninguna pestaña se estiliza por separado: todas heredan el fondo del stack."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QImage

        app = QApplication.instance() or QApplication([])
        import packagemaker

        window = packagemaker.PackageTodoGUI()
        window.resize(1024, 720)
        window.show()
        app.processEvents()
        try:
            pages = [
                window.page_create,
                window.page_build,
                window.page_config,
                window.page_moonfix,
                window.page_about,
            ]
            colours = set()
            for page in pages:
                window.stack.setCurrentWidget(page)
                app.processEvents()
                image = page.grab().toImage().convertToFormat(QImage.Format.Format_RGB32)
                colour = image.pixelColor(image.width() - 20, image.height() - 20)
                colours.add((colour.red(), colour.green(), colour.blue()))
            self.assertEqual(len(colours), 1, f"fondos dispares: {colours}")
        finally:
            window.close()
            app.processEvents()


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

    def test_no_hardcoded_spanish_widget_literals(self):
        """Los textos visibles pasan por ``tr()``; sin literales en español.

        Detecta constructores de widgets y setters de texto cuyo argumento es
        una cadena literal con palabras en español (con o sin acentos).
        """
        import re

        widgets = (
            r"QLabel|QCheckBox|QGroupBox|QPushButton|QRadioButton|QLineEdit|"
            r"setText|setWindowTitle|setPlaceholderText|setToolTip|"
            r"setLabelText|setInformativeText|addItem|setTitle"
        )
        spanish = (
            r"(?:Compilar|Cerrar|Proyecto|Crear|Versión|Archivo|Abrir|Guardar|"
            r"Cancelar|Ejecutar|Verificar|Configuración|Opciones|Descripción|"
            r"Ubicación|Reparación|Intérpretes|Página|Automática|Optimización|"
            r"Asegúrate|Excluir|Instalados|Descargar|Requerido|Paquete|"
            r"obligatorio|Nombre|Plataforma|Instalar|Desinstalar|Predeterminado)"
        )
        pattern = re.compile(
            rf'(?:{widgets})\s*\(\s*f?["\']([^"\']*)\b{spanish}\b',
        )
        offenders = []
        for path in list(ROOT.glob("*.py")) + list(ROOT.glob("lib/*.py")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "tr(" in line:
                    continue
                match = pattern.search(line)
                if match:
                    offenders.append(f"{path.name}:{lineno}: {line.strip()}")
        self.assertEqual(offenders, [], "literales sin tr():\n" + "\n".join(offenders))


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

    def test_orphan_filters_are_released(self):
        """Un filtro huérfano (sin referencia en ``window_effects``) también se retira.

        Reproduce el caso real: la ventana principal instalaba un WipeWindow en
        ``__init__`` y otro al reaplicar el modo; el segundo quedaba sin
        referencia y seguía pintando el tinte blanco, lavando la ventana.
        """
        from PyQt6.QtWidgets import QApplication, QWidget

        app = QApplication.instance() or QApplication([])
        from lib.window_chrome import apply_display_mode, _wipe_filters

        try:
            from leviathan_ui import WipeWindow
        except ImportError:
            self.skipTest("leviathan_ui no está instalado")

        window = QWidget()
        window.resize(400, 300)
        try:
            apply_display_mode(window, "GhostBlur (Cristal)")
            # Simula un filtro huérfano: se ancla a la ventana pero se pierde la
            # referencia en ``window_effects``.
            orphan = WipeWindow.create().set_mode("ghostBlur").apply(window)
            window.window_effects = None
            self.assertIn(orphan, _wipe_filters(window))

            apply_display_mode(window, "GhostBlur (Cristal)")
            self.assertNotIn(orphan, _wipe_filters(window))
            self.assertIsNone(orphan.parent())
        finally:
            window.close()
            app.processEvents()


if __name__ == "__main__":
    unittest.main()
