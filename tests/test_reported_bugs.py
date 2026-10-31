# -*- coding: utf-8 -*-
"""Regresiones de los cinco fallos reportados sobre la interfaz y la compilación.

Cubre, con código real (sin dobles salvo donde se indica):

- localización del proyecto por metadatos en vez de reconstruir el nombre;
- reporte en la barra de estado con diálogo OK para errores y advertencias;
- gating de plataforma (AlphaCube usa el SO anfitrión);
- estilo unificado de checkbox y texto a la derecha del control.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


DETAILS_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<app>
  <publisher>{publisher}</publisher>
  <app>{app}</app>
  <name>{name}</name>
  <version>{version}</version>
  <platform>{platform}</platform>
  <author>Autor</author>
</app>
"""


def _write_project(base: Path, folder: str, *, publisher, app, version, platform):
    project = base / folder
    project.mkdir(parents=True, exist_ok=True)
    (project / "details.xml").write_text(
        DETAILS_TEMPLATE.format(
            publisher=publisher, app=app, name=app, version=version, platform=platform
        ),
        encoding="utf-8",
    )
    return project


class ProjectLocatorTests(unittest.TestCase):
    """Bug 1: el proyecto se encuentra leyendo metadatos, no adivinando el nombre."""

    def test_locate_by_metadata_with_timestamped_folder(self):
        from lib.project_locator import locate_project

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            # Nombre de carpeta con marca temporal completa, imposible de
            # reconstruir a mano a partir de la versión corta "1.0".
            real = _write_project(
                base,
                "Influent.demo.v1.0.0-26.05-20.13-AlphaCube",
                publisher="Influent",
                app="demo",
                version="1.0.0",
                platform="AlphaCube",
            )
            found = locate_project(base, publisher="Influent", app_id="demo")
            self.assertEqual(found, real)

    def test_locate_ignores_other_projects(self):
        from lib.project_locator import locate_project

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_project(
                base, "Otro.otraapp.v2.0-25.01-10.00-Danenone",
                publisher="Otro", app="otraapp", version="2.0", platform="Danenone",
            )
            wanted = _write_project(
                base, "Influent.demo.v1.0-26.05-20.13-AlphaCube",
                publisher="Influent", app="demo", version="1.0", platform="AlphaCube",
            )
            found = locate_project(base, publisher="Influent", app_id="demo")
            self.assertEqual(found, wanted)

    def test_locate_returns_none_when_absent(self):
        from lib.project_locator import locate_project

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_project(
                base, "Influent.demo.v1.0-26.05-20.13-AlphaCube",
                publisher="Influent", app="demo", version="1.0", platform="AlphaCube",
            )
            self.assertIsNone(locate_project(base, publisher="Influent", app_id="otro"))

    def test_describe_available_lists_projects(self):
        from lib.project_locator import describe_available

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_project(
                base, "Influent.demo.v1.0-26.05-20.13-AlphaCube",
                publisher="Influent", app="demo", version="1.0", platform="AlphaCube",
            )
            summary = describe_available(base)
            self.assertIn("Influent.demo", summary)

    def test_build_thread_run_uses_locator(self):
        """``run`` debe localizar por metadatos y no emitir 'No se encontró la carpeta'."""
        from lib.BuildThread import BuildThread

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write_project(
                base, "Influent.demo.v1.0.0-26.05-20.13-AlphaCube",
                publisher="Influent", app="demo", version="1.0.0", platform="AlphaCube",
            )
            thread = BuildThread(
                empresa="Influent",
                nombre="demo",
                version="1.0",
                plataforma="AlphaCube",
                base_dir=base,
            )
            errors = []
            thread.error.connect(errors.append)
            # Se detiene tras localizar (no hay scripts): importa que el error
            # no sea el de carpeta no encontrada.
            thread.run()
            for message in errors:
                self.assertNotIn("No se encontró la carpeta", message)


class PlatformGatingTests(unittest.TestCase):
    """Bug 5: AlphaCube compila para el SO anfitrión; el resto queda acotado."""

    def _compiler(self, platform_type, current):
        from lib.BuildThread import FlangCompiler

        compiler = FlangCompiler.__new__(FlangCompiler)
        compiler.platform_type = platform_type
        compiler.current_platform = current
        return compiler

    def test_alphacube_builds_for_host(self):
        for host in ("Windows", "Linux"):
            compiler = self._compiler("AlphaCube", host)
            self.assertTrue(compiler.should_compile_for_platform(host))

    def test_knosthalij_only_windows(self):
        compiler = self._compiler("Knosthalij", "Windows")
        self.assertTrue(compiler.should_compile_for_platform("Windows"))
        self.assertFalse(compiler.should_compile_for_platform("Linux"))

    def test_danenone_only_linux(self):
        compiler = self._compiler("Danenone", "Linux")
        self.assertTrue(compiler.should_compile_for_platform("Linux"))
        self.assertFalse(compiler.should_compile_for_platform("Windows"))


class ReporterTests(unittest.TestCase):
    """Bug 2 y 3: barra de estado + diálogo con botón OK."""

    def test_notify_only_writes_status_bar(self):
        from lib.report import Reporter

        shown = []
        dialogs = []

        class Bar:
            def showMessage(self, text):
                shown.append(text)

        reporter = Reporter(
            status_bar=Bar(),
            dialog_launcher=lambda *a, **k: dialogs.append((a, k)),
        )
        reporter.progress("Compilando...")
        self.assertEqual(shown, ["Compilando..."])
        self.assertEqual(dialogs, [])

    def test_error_shows_status_and_dialog(self):
        from lib.report import Reporter

        shown = []
        dialogs = []

        class Bar:
            def showMessage(self, text):
                shown.append(text)

        reporter = Reporter(
            status_bar=Bar(),
            dialog_launcher=lambda parent, title, message, mode="info": dialogs.append(
                (title, message, mode)
            ),
        )
        reporter.error("Error de compilación", "falló algo")
        self.assertIn("falló algo", shown[-1])
        self.assertEqual(dialogs, [("Error de compilación", "falló algo", "error")])

    def test_classify_build_message(self):
        from lib.report import classify_build_message

        self.assertEqual(classify_build_message("[ERROR] boom"), "error")
        self.assertEqual(classify_build_message("[WARN] ojo"), "warning")
        self.assertEqual(classify_build_message("[SUCCESS] ok"), "success")
        self.assertEqual(classify_build_message("compilando paso 2"), "info")

    def test_alert_dialog_has_ok_button(self):
        from PyQt6.QtWidgets import QApplication, QPushButton

        app = QApplication.instance() or QApplication([])
        from lib.alert_dialog import AlertDialog

        dialog = AlertDialog(None, "Titulo", "Mensaje", mode="info")
        dialog.show()
        app.processEvents()
        labels = [b.text() for b in dialog.findChildren(QPushButton)]
        self.assertEqual(labels, ["OK"])
        dialog.accept()


class CheckboxStyleTests(unittest.TestCase):
    """Bug 4: un único estilo de checkbox y texto siempre a la derecha."""

    def test_all_checkbox_style_keys_share_indicator(self):
        from lib import fluent_theme

        for key in (
            "packagemaker_049",
            "packagemaker_055",
            "packagemaker_073",
            "packagemaker_114",
            "packagemaker_115",
            "packagemaker_116",
            "packagemaker_125",
            "packagemaker_126",
            "packagemaker_127",
            "packagemaker_128",
        ):
            self.assertIn(key, fluent_theme.INLINE_STYLES)
            qss = fluent_theme.INLINE_STYLES[key]
            self.assertIn("QCheckBox::indicator", qss, f"{key} sin regla de indicador")
            self.assertIn("spacing:", qss, f"{key} sin separación entre control y texto")

    def test_indicator_does_not_overlap_label(self):
        from PyQt6.QtWidgets import (
            QApplication,
            QStyle,
            QStyleOptionButton,
        )

        app = QApplication.instance() or QApplication([])
        from lib.fluent_theme import FluentCheckBox, set_qss

        for key in ("packagemaker_049", "packagemaker_073", "packagemaker_114"):
            cb = FluentCheckBox("Windows (Knosthalij)")
            set_qss(cb, key, append=False)
            cb.resize(300, 20)
            cb.show()
            app.processEvents()

            option = QStyleOptionButton()
            cb.initStyleOption(option)
            indicator = cb.style().subElementRect(
                QStyle.SubElement.SE_CheckBoxIndicator, option, cb
            )
            contents = cb.style().subElementRect(
                QStyle.SubElement.SE_CheckBoxContents, option, cb
            )
            self.assertGreaterEqual(
                contents.x(),
                indicator.x() + indicator.width(),
                f"{key}: el texto no queda a la derecha del indicador",
            )
            cb.close()


if __name__ == "__main__":
    unittest.main()
