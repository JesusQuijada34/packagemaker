# -*- coding: utf-8 -*-
"""Pacing del splash y reporte de tirones del arranque (Q-027 / R-7b2c9e51)."""

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.startup_timing import (  # noqa: E402
    DEFAULT_MIN_SECONDS,
    LAG_THRESHOLD_SECONDS,
    QUANTUM_SECONDS,
    SplashWaiter,
    StartupTimeline,
    minimum_splash_seconds,
    performance_points,
    startup_lag_report,
)


class FakeClock:
    """Reloj manual para medir fases sin depender del tiempo real."""

    def __init__(self, start: float = 0.0):
        self.now = float(start)

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += float(seconds)


class TestPerformancePoints:
    def test_unknown_hardware_scores_zero(self):
        assert performance_points(ram_mb=0, cores=0) == 0

    def test_points_grow_with_ram_and_cores(self):
        small = performance_points(ram_mb=4 * 1024, cores=4)
        big = performance_points(ram_mb=32 * 1024, cores=16)
        assert small == 2
        assert big > small

    def test_points_are_capped(self):
        assert performance_points(ram_mb=1024 * 1024, cores=512) == 8

    def test_real_hardware_never_fails(self):
        assert performance_points() >= 0


class TestMinimumSplashSeconds:
    def test_base_is_five_seconds(self):
        assert minimum_splash_seconds(ram_mb=0, cores=0, environ={}) == DEFAULT_MIN_SECONDS

    def test_slower_hardware_waits_a_little_longer(self):
        fast = minimum_splash_seconds(ram_mb=4 * 1024, cores=2, environ={})
        slow = minimum_splash_seconds(ram_mb=32 * 1024, cores=16, environ={})
        assert slow > fast >= DEFAULT_MIN_SECONDS

    def test_value_is_rounded_and_bounded(self):
        for ram, cores in ((0, 0), (8 * 1024, 4), (64 * 1024, 32), (1024 * 1024, 512)):
            value = minimum_splash_seconds(ram_mb=ram, cores=cores, environ={})
            assert value % QUANTUM_SECONDS == pytest.approx(0.0)
            assert DEFAULT_MIN_SECONDS <= value <= DEFAULT_MIN_SECONDS + 1.0

    def test_environment_override_wins(self):
        assert minimum_splash_seconds(environ={"PM_SPLASH_MIN_SECONDS": "0"}) == 0.0
        assert minimum_splash_seconds(environ={"PM_SPLASH_MIN_SECONDS": "2.5"}) == 2.5

    def test_invalid_override_falls_back(self):
        value = minimum_splash_seconds(ram_mb=0, cores=0, environ={"PM_SPLASH_MIN_SECONDS": "pronto"})
        assert value == DEFAULT_MIN_SECONDS


class TestStartupTimeline:
    def _timeline(self):
        clock = FakeClock()
        return StartupTimeline.start(clock=clock), clock

    def test_phases_are_measured_in_order(self):
        timeline, clock = self._timeline()
        clock.advance(0.30)
        assert timeline.mark("estilos") == pytest.approx(0.30)
        clock.advance(0.70)
        assert timeline.mark("ventana") == pytest.approx(0.70)
        assert [phase.name for phase in timeline.phases] == ["estilos", "ventana"]
        assert timeline.total() == pytest.approx(1.0)

    def test_total_stops_at_the_last_mark(self):
        timeline, clock = self._timeline()
        clock.advance(0.4)
        timeline.mark("ventana")
        clock.advance(5.0)  # espera deliberada del splash
        assert timeline.total() == pytest.approx(0.4)

    def test_lags_only_reports_slow_phases(self):
        timeline, clock = self._timeline()
        clock.advance(0.1)
        timeline.mark("estilos")
        clock.advance(LAG_THRESHOLD_SECONDS + 0.4)
        timeline.mark("ventana")
        assert [phase.name for phase in timeline.lags()] == ["ventana"]

    def test_report_lines_are_sorted_and_limited(self):
        timeline, clock = self._timeline()
        for name, seconds in (("a", 0.1), ("b", 0.9), ("c", 0.4)):
            clock.advance(seconds)
            timeline.mark(name)
        lines = timeline.report_lines(limit=2)
        assert lines[0].startswith("b: 0.90")
        assert lines[1].startswith("c: 0.40")
        assert len(lines) == 2


class TestSplashWaiter:
    def _waiter(self, minimum, clock):
        scheduled = []
        waiter = SplashWaiter(
            minimum,
            clock=clock,
            schedule=lambda delay, callback: scheduled.append((delay, callback)),
        )
        waiter.arm()
        return waiter, scheduled

    def test_waits_until_the_minimum(self):
        clock = FakeClock()
        waiter, scheduled = self._waiter(5.0, clock)
        closed = []
        assert waiter.request(lambda: closed.append(True)) is False
        assert closed == []
        assert scheduled and scheduled[0][0] == pytest.approx(5.0)

        clock.advance(4.9)
        scheduled[0][1]()
        assert closed == []
        assert scheduled[-1][0] == pytest.approx(0.1)

        clock.advance(0.1)
        scheduled[-1][1]()
        assert closed == [True]

    def test_closes_immediately_without_a_scheduler(self):
        clock = FakeClock()
        waiter = SplashWaiter(5.0, clock=clock)
        waiter.arm()
        closed = []
        assert waiter.request(lambda: closed.append(True)) is True
        assert closed == [True]

    def test_zero_minimum_closes_at_once(self):
        clock = FakeClock()
        waiter, scheduled = self._waiter(0.0, clock)
        closed = []
        assert waiter.request(lambda: closed.append(True)) is True
        assert closed == [True]
        assert scheduled == []

    def test_ready_time_is_captured_before_the_wait(self):
        clock = FakeClock()
        waiter, scheduled = self._waiter(5.0, clock)
        timeline = StartupTimeline.start(clock=clock)
        clock.advance(0.8)
        timeline.mark("ventana")
        waiter.request(lambda: None, timeline=timeline)
        clock.advance(10.0)
        waiter.request(lambda: None, timeline=timeline)
        assert waiter.ready_seconds == pytest.approx(0.8)


class TestStartupLagReport:
    def _timeline(self, phases):
        clock = FakeClock()
        timeline = StartupTimeline.start(clock=clock)
        for name, seconds in phases:
            clock.advance(seconds)
            timeline.mark(name)
        return timeline

    def test_fast_startup_reports_nothing(self):
        timeline = self._timeline([("estilos", 0.05), ("ventana", 0.4)])
        assert startup_lag_report(timeline, minimum=5.0, ready=0.45) is None

    def test_slow_phase_is_reported(self):
        timeline = self._timeline([("ventana", 1.4)])
        entry = startup_lag_report(timeline, minimum=5.0, ready=1.4)
        assert entry is not None
        assert entry["kind"] == "StartupLag"
        assert entry["auto"] is True
        assert entry["title"].startswith("[auto] Arranque con tirones")
        assert "ventana" in entry["title"]
        assert "ventana: 1.40 s" in entry["description"]
        assert entry["fingerprint"]

    def test_interface_ready_after_the_minimum_is_a_lag(self):
        timeline = self._timeline([("ventana", 0.2)])
        entry = startup_lag_report(timeline, minimum=5.0, ready=7.25)
        assert entry is not None
        assert entry["title"] == "[auto] Arranque lento: interfaz lista en 7.2 s"
        assert "Interfaz lista en: 7.25 s" in entry["description"]
        assert "Espera mínima del splash: 5.00 s" in entry["description"]

    def test_remaining_errors_are_included(self):
        timeline = self._timeline([("ventana", 1.0)])
        entry = startup_lag_report(
            timeline, minimum=5.0, ready=1.0, errors=["details.xml roto", "  "]
        )
        assert "Errores restantes del arranque:" in entry["description"]
        assert "details.xml roto" in entry["description"]

    def test_fingerprint_depends_on_the_slow_phases_only(self):
        first = startup_lag_report(self._timeline([("ventana", 1.0)]), minimum=5.0, ready=1.0)
        second = startup_lag_report(self._timeline([("ventana", 3.0)]), minimum=5.0, ready=3.0)
        other = startup_lag_report(self._timeline([("estilos", 1.0)]), minimum=5.0, ready=1.0)
        assert first["fingerprint"] == second["fingerprint"]
        assert first["fingerprint"] != other["fingerprint"]

    def test_uses_the_timeline_total_without_a_ready_measure(self):
        timeline = self._timeline([("ventana", 0.2)])
        assert startup_lag_report(timeline, minimum=0.1) is not None


class TestStartupLagWiring:
    """El enganche real de ``main``: opt-in respetado y entrada encolada."""

    def _timeline(self, seconds):
        clock = FakeClock()
        timeline = StartupTimeline.start(clock=clock)
        clock.advance(seconds)
        timeline.mark("ventana")
        return timeline

    def test_opt_in_disabled_enqueues_nothing(self, monkeypatch):
        import packagemaker
        from lib import crash_capture, report_queue

        calls = []
        monkeypatch.setattr(crash_capture, "auto_report_enabled", lambda: False)
        monkeypatch.setattr(report_queue, "enqueue", lambda entry: calls.append(entry) or True)

        assert packagemaker.report_startup_lags(self._timeline(2.0), minimum=5.0) is False
        assert calls == []

    def test_lag_is_enqueued_when_opt_in_is_on(self, monkeypatch):
        import packagemaker
        from lib import crash_capture, report_queue

        calls = []
        monkeypatch.setattr(crash_capture, "auto_report_enabled", lambda: True)
        monkeypatch.setattr(report_queue, "enqueue", lambda entry: calls.append(entry) or True)

        assert packagemaker.report_startup_lags(self._timeline(2.0), minimum=5.0) is True
        assert len(calls) == 1
        assert calls[0]["kind"] == "StartupLag"

    def test_clean_startup_enqueues_nothing(self, monkeypatch):
        import packagemaker
        from lib import crash_capture, report_queue

        calls = []
        monkeypatch.setattr(crash_capture, "auto_report_enabled", lambda: True)
        monkeypatch.setattr(report_queue, "enqueue", lambda entry: calls.append(entry) or True)

        assert packagemaker.report_startup_lags(self._timeline(0.2), minimum=5.0) is False
        assert calls == []

    def test_already_queued_lag_is_not_duplicated(self, monkeypatch):
        import packagemaker
        from lib import crash_capture, report_queue

        calls = []
        monkeypatch.setattr(crash_capture, "auto_report_enabled", lambda: True)
        monkeypatch.setattr(report_queue, "already_sent", lambda fingerprint: False)
        monkeypatch.setattr(
            report_queue,
            "pending",
            lambda: [{"fingerprint": startup_lag_report(
                self._timeline(2.0), minimum=5.0
            )["fingerprint"]}],
        )
        monkeypatch.setattr(report_queue, "enqueue", lambda entry: calls.append(entry) or True)

        assert packagemaker.report_startup_lags(self._timeline(2.0), minimum=5.0) is False
        assert calls == []

    def test_lag_already_sent_is_not_repeated(self, monkeypatch):
        import packagemaker
        from lib import crash_capture, report_queue

        calls = []
        monkeypatch.setattr(crash_capture, "auto_report_enabled", lambda: True)
        monkeypatch.setattr(report_queue, "already_sent", lambda fingerprint: True)
        monkeypatch.setattr(report_queue, "pending", lambda: [])
        monkeypatch.setattr(report_queue, "enqueue", lambda entry: calls.append(entry) or True)

        assert packagemaker.report_startup_lags(self._timeline(2.0), minimum=5.0) is False
        assert calls == []

    def test_main_holds_the_splash_until_the_minimum(self):
        source = (ROOT / "packagemaker.py").read_text(encoding="utf-8")
        assert "splash_waiter.arm()" in source
        assert "splash_waiter.request(finish_splash" in source
        body = source[source.index("def finish_splash") :]
        assert body.index("splash.finish()") < body.index("report_startup_lags(")
        assert "minimum_splash_seconds()" in source


class TestSplashWindowPacing:
    def test_splash_is_not_closed_before_the_minimum(self, _qt_app):
        QtCore = pytest.importorskip("PyQt6.QtCore")
        from lib.splash_window import IntegratedSplash

        splash = IntegratedSplash(title="Package Maker")
        splash.show_splash()
        finished = []
        waiter = SplashWaiter(
            0.4,
            schedule=lambda delay, callback: QtCore.QTimer.singleShot(
                int(delay * 1000) + 1, callback
            ),
        )
        waiter.arm()
        start = time.perf_counter()

        def _close():
            finished.append(time.perf_counter() - start)
            splash.finish()

        waiter.request(_close)
        assert finished == []

        deadline = start + 3.0
        while not finished and time.perf_counter() < deadline:
            _qt_app.processEvents()
            time.sleep(0.01)

        assert finished, "el splash no llegó a cerrarse"
        assert finished[0] >= 0.35
