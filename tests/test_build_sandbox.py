"""Entorno de compilación aislado por proyecto (Q-019).

Se prueba con un ``runner`` falso: los comandos se inspeccionan sin crear
venvs reales ni descargar dependencias.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


from lib.blindcubeEngine import build_sandbox
from lib.blindcubeEngine.build_sandbox import (
    NETWORK_METERED,
    NETWORK_UNRESTRICTED,
    BuildSandbox,
    IsolatedBackend,
    isolation_enabled,
    plan_sandbox,
    project_requirements,
    resolve_network_mode,
    wrap_backend,
)


class FakeRunner:
    """Registra los comandos y simula la salida del compilador."""

    def __init__(self, *, fail_on: str = "", artifact: Path | None = None):
        self.calls = []
        self.fail_on = fail_on
        self.artifact = artifact

    def __call__(self, argv, **kwargs):
        self.calls.append(list(argv))
        joined = " ".join(str(item) for item in argv)
        if self.fail_on and self.fail_on in joined:
            return SimpleNamespace(returncode=1, stdout="", stderr=f"fallo simulado en {self.fail_on}")
        if self.artifact is not None and list(argv[1:3]) in (["-m", "nuitka"], ["-m", "PyInstaller"]):
            self.artifact.parent.mkdir(parents=True, exist_ok=True)
            self.artifact.write_bytes(b"binario")
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")


class StubBackend:
    name = "nuitka"
    display_name = "Nuitka (C/C++ nativo, embebido)"
    pip_packages = ("nuitka",)
    embedded = True

    def __init__(self):
        self.last_error = ""
        self.compiled = 0

    def is_available(self) -> bool:
        return True

    def version(self) -> str:
        return "4.4"

    def compile(self, **kwargs):
        self.compiled += 1
        return str(Path(kwargs["output_dir"]) / kwargs["output_name"])

    def cleanup(self) -> None:
        pass


def _project(tmp_path: Path, requirements: str | None = None) -> Path:
    project = tmp_path / "Influent.demo.v1.0-26.11-08.00-AlphaCube"
    project.mkdir(parents=True)
    if requirements is not None:
        (project / "requirements.txt").write_text(requirements, encoding="utf-8")
    (project / "app.py").write_text("print('hola')\n", encoding="utf-8")
    return project


def test_resolve_network_mode_accepts_spanish_and_unknown_values():
    assert resolve_network_mode("metered") == NETWORK_METERED
    assert resolve_network_mode("Uso medido") == NETWORK_METERED
    assert resolve_network_mode("unrestricted") == NETWORK_UNRESTRICTED
    assert resolve_network_mode(None) == NETWORK_UNRESTRICTED
    assert resolve_network_mode(42) == NETWORK_UNRESTRICTED


def test_isolation_enabled_respects_metered_mode_and_switch(monkeypatch):
    monkeypatch.delenv(build_sandbox.DISABLE_ENV, raising=False)
    assert isolation_enabled(NETWORK_UNRESTRICTED) is True
    assert isolation_enabled(NETWORK_METERED) is False
    assert isolation_enabled(NETWORK_UNRESTRICTED, env={build_sandbox.DISABLE_ENV: "0"}) is False
    assert isolation_enabled(NETWORK_UNRESTRICTED, env={build_sandbox.DISABLE_ENV: "1"}) is True


def test_plan_lives_under_build_so_it_never_enters_the_package(tmp_path):
    project = _project(tmp_path)
    plan = plan_sandbox(project, backend="nuitka")

    assert plan.root == project.resolve() / "build" / "pm-sandbox" / "nuitka"
    assert plan.venv_dir == plan.root / "venv"
    assert plan.interpreter.parent.name in {"bin", "Scripts"}
    assert plan.network_mode == NETWORK_UNRESTRICTED
    assert plan.as_dict()["backend"] == "nuitka"


def test_build_directory_is_excluded_from_the_package(tmp_path):
    from lib.blindcubeEngine.BuildThread import FlangCompiler

    compiler = FlangCompiler(_project(tmp_path), tmp_path / "out", log_callback=lambda _m: None)
    patterns = compiler._load_gitignore_patterns()

    assert compiler._should_exclude("build", patterns) is True


def test_project_requirements_ignores_comments_and_blank_lines(tmp_path):
    project = _project(tmp_path, "# dependencias\n\nrequests==2.32.3\n  PyQt6==6.7.0\n")
    assert project_requirements(project) == ("requests==2.32.3", "PyQt6==6.7.0")
    assert project_requirements(tmp_path / "vacio") == ()


def test_prepare_creates_venv_installs_and_checks_the_backend(tmp_path):
    project = _project(tmp_path, "requests==2.32.3\n")
    plan = plan_sandbox(project, backend="nuitka", base_python="/usr/bin/python3")
    runner = FakeRunner()
    sandbox = BuildSandbox(plan, runner=runner)

    assert sandbox.prepare() is True

    venv_call, pip_call, check_call = runner.calls
    assert venv_call == ["/usr/bin/python3", "-m", "venv", str(plan.venv_dir)]
    assert pip_call[:4] == [str(plan.interpreter), "-m", "pip", "install"]
    assert "requests==2.32.3" in pip_call
    assert {"nuitka", "ordered-set", "zstandard"} <= set(pip_call)
    assert check_call == [str(plan.interpreter), "-c", "import nuitka"]
    assert plan.root.joinpath("installed.json").is_file()


def test_prepare_skips_pip_when_the_marker_matches(tmp_path):
    project = _project(tmp_path, "requests==2.32.3\n")
    plan = plan_sandbox(project, backend="nuitka")
    plan.interpreter.parent.mkdir(parents=True, exist_ok=True)
    plan.interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
    plan.root.joinpath("installed.json").write_text(
        '{"packages": ["requests==2.32.3", "nuitka", "ordered-set", "zstandard"]}',
        encoding="utf-8",
    )
    runner = FakeRunner()

    assert BuildSandbox(plan, runner=runner).prepare() is True
    assert len(runner.calls) == 1  # sólo la comprobación de importación


def test_prepare_reports_pip_failures(tmp_path):
    project = _project(tmp_path, "dependencia-inexistente\n")
    plan = plan_sandbox(project, backend="nuitka")
    sandbox = BuildSandbox(plan, runner=FakeRunner(fail_on="pip install"))

    assert sandbox.prepare() is False
    assert "pip install falló" in sandbox.last_error


def test_compile_runs_the_backend_inside_the_venv(tmp_path):
    project = _project(tmp_path)
    plan = plan_sandbox(project, backend="nuitka")
    plan.interpreter.parent.mkdir(parents=True, exist_ok=True)
    plan.interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
    output_dir = tmp_path / "dist"
    artifact = output_dir / "demo"
    runner = FakeRunner(artifact=artifact)
    sandbox = BuildSandbox(plan, runner=runner)

    result = sandbox.compile(
        script_path=str(project / "app.py"),
        output_name="demo",
        output_dir=str(output_dir),
        windowed=True,
        onefile=True,
        build_dir=str(tmp_path / "work"),
    )

    assert result == str(artifact)
    compile_call = runner.calls[-1]
    assert compile_call[0] == str(plan.interpreter)
    assert compile_call[1:3] == ["-m", "nuitka"]
    assert any(arg.startswith("--output-dir=") for arg in compile_call)
    assert str(project / "app.py") in compile_call


def test_nuitka_arguments_drop_the_qt_plugin_when_the_venv_lacks_pyqt6(tmp_path):
    without_qt = BuildSandbox(plan_sandbox(_project(tmp_path / "a")))
    with_qt = BuildSandbox(
        plan_sandbox(_project(tmp_path / "b", "PyQt6==6.7.0\n"))
    )
    common = dict(
        script_path=str(tmp_path / "app.py"),
        output_name="demo",
        output_dir=str(tmp_path / "dist"),
    )

    assert not any(
        arg.startswith("--enable-plugin=pyqt6") for arg in without_qt._nuitka_arguments(**common)
    )
    assert any(arg.startswith("--enable-plugin=pyqt6") for arg in with_qt._nuitka_arguments(**common))


def test_compile_without_artifact_reports_the_missing_binary(tmp_path):
    project = _project(tmp_path)
    plan = plan_sandbox(project, backend="nuitka")
    plan.interpreter.parent.mkdir(parents=True, exist_ok=True)
    plan.interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
    sandbox = BuildSandbox(plan, runner=FakeRunner())

    assert sandbox.compile(
        script_path=str(project / "app.py"),
        output_name="demo",
        output_dir=str(tmp_path / "dist"),
    ) is None
    assert "no generó el binario esperado" in sandbox.last_error


def test_isolated_backend_falls_back_to_the_embedded_one(tmp_path):
    inner = StubBackend()
    backend = IsolatedBackend(
        inner,
        project_path=_project(tmp_path),
        sandbox_factory=lambda plan: BuildSandbox(plan, runner=FakeRunner(fail_on="venv")),
    )

    result = backend.compile(script_path="app.py", output_name="demo", output_dir=str(tmp_path))

    assert result == str(tmp_path / "demo")
    assert inner.compiled == 1
    assert backend.last_error == ""


def test_isolated_backend_reports_the_isolated_display_name(tmp_path):
    backend = IsolatedBackend(StubBackend(), project_path=_project(tmp_path))

    assert backend.name == "nuitka"
    assert "aislado" in backend.display_name
    assert backend.embedded is False
    assert backend.is_available() is True


def test_wrap_backend_only_isolates_compilers_with_network_access(tmp_path, monkeypatch):
    monkeypatch.delenv(build_sandbox.DISABLE_ENV, raising=False)
    project = _project(tmp_path)
    nuitka = StubBackend()
    zipapp = StubBackend()
    zipapp.name = "zipapp"

    isolated = wrap_backend(nuitka, project, network_mode=NETWORK_UNRESTRICTED, log_callback=lambda _m: None)
    metered = wrap_backend(nuitka, project, network_mode=NETWORK_METERED, log_callback=lambda _m: None)
    other = wrap_backend(zipapp, project, network_mode=NETWORK_UNRESTRICTED, log_callback=lambda _m: None)

    assert isinstance(isolated, IsolatedBackend)
    assert metered is nuitka
    assert other is zipapp


def test_metered_mode_explains_that_system_python_is_required(tmp_path, monkeypatch):
    monkeypatch.delenv(build_sandbox.DISABLE_ENV, raising=False)
    messages = []
    wrap_backend(
        StubBackend(),
        _project(tmp_path),
        network_mode=NETWORK_METERED,
        log_callback=messages.append,
    )

    assert "uso medido" in messages[0].lower()
    assert "Python del sistema" in messages[0]


def test_build_thread_wraps_the_backend_with_the_project_sandbox(tmp_path, monkeypatch):
    from lib.blindcubeEngine import BuildThread as module

    project = _project(tmp_path)
    compiler = module.FlangCompiler(project, tmp_path / "out", log_callback=lambda _m: None)
    monkeypatch.delenv(build_sandbox.DISABLE_ENV, raising=False)
    monkeypatch.setattr(
        module, "resolve_backend", lambda name, log_callback=None: StubBackend()
    )

    backend = compiler._ensure_compiler()

    assert isinstance(backend, IsolatedBackend)
    assert backend._project_path == project


def test_build_thread_keeps_the_embedded_backend_when_isolation_is_disabled(tmp_path, monkeypatch):
    from lib.blindcubeEngine import BuildThread as module

    project = _project(tmp_path)
    compiler = module.FlangCompiler(project, tmp_path / "out", log_callback=lambda _m: None)
    monkeypatch.setenv(build_sandbox.DISABLE_ENV, "0")
    stub = StubBackend()
    monkeypatch.setattr(module, "resolve_backend", lambda name, log_callback=None: stub)

    assert compiler._ensure_compiler() is stub


def test_isolated_backend_prepares_the_sandbox_only_once(tmp_path):
    project = _project(tmp_path)
    output_dir = tmp_path / "dist"
    artifact = output_dir / "demo"
    runner = FakeRunner(artifact=artifact)
    inner = StubBackend()
    backend = IsolatedBackend(
        inner,
        project_path=project,
        sandbox_factory=lambda plan: BuildSandbox(plan, runner=runner),
    )

    for _ in range(2):
        assert backend.compile(
            script_path=str(project / "app.py"),
            output_name="demo",
            output_dir=str(output_dir),
        ) == str(artifact)

    venv_calls = [call for call in runner.calls if call[1:3] == ["-m", "venv"]]
    assert len(venv_calls) == 1
    assert inner.compiled == 0
