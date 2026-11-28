# -*- coding: utf-8 -*-
"""Pacing del splash y diagnóstico de tirones del arranque (Q-027).

El splash no se retira hasta que han pasado ``minimum_splash_seconds()``. El
mínimo parte de 5 s y crece con los puntos de rendimiento del equipo (RAM y
núcleos), de modo que una máquina lenta tenga tiempo de dibujar la interfaz
antes de que la cortina se abra. Si el arranque sufre tirones, el módulo arma la
entrada de reporte con qué se ejecutó, cuánto tardó y los errores que quedaron.

Sin Qt: toda la decisión se puede probar sin interfaz.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

DEFAULT_MIN_SECONDS = 5.0
# Grano del redondeo: el mínimo siempre es múltiplo de 0,25 s.
QUANTUM_SECONDS = 0.25
# Puntos de rendimiento: uno por cada 4 GB de RAM y uno por cada 4 núcleos.
_MAX_POINTS = 8
_POINTS_STEP_SECONDS = 0.125
# Por encima de esto una fase del arranque se considera un tirón perceptible.
LAG_THRESHOLD_SECONDS = 0.5

#: Variable de entorno para acortar (o anular) la espera en desarrollo y CI.
ENV_OVERRIDE = "PM_SPLASH_MIN_SECONDS"


def available_ram_mb() -> Optional[int]:
    """RAM física en MB, o ``None`` si el sistema no la expone."""
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        if pages > 0 and page_size > 0:
            return int(pages * page_size // (1024 * 1024))
    except (AttributeError, OSError, ValueError):
        pass
    if os.name == "nt":  # pragma: no cover - sólo Windows
        try:
            import ctypes

            class _MemoryStatus(ctypes.Structure):
                _fields_ = [
                    ("length", ctypes.c_ulong),
                    ("memory_load", ctypes.c_ulong),
                    ("total_physical", ctypes.c_ulonglong),
                    ("available_physical", ctypes.c_ulonglong),
                    ("total_page_file", ctypes.c_ulonglong),
                    ("available_page_file", ctypes.c_ulonglong),
                    ("total_virtual", ctypes.c_ulonglong),
                    ("available_virtual", ctypes.c_ulonglong),
                    ("available_extended_virtual", ctypes.c_ulonglong),
                ]

            status = _MemoryStatus()
            status.length = ctypes.sizeof(_MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.total_physical // (1024 * 1024))
        except Exception:
            return None
    return None


def cpu_cores() -> int:
    return int(os.cpu_count() or 0)


def performance_points(ram_mb: Optional[int] = None, cores: Optional[int] = None) -> int:
    """Puntos de rendimiento del equipo; más puntos, más espera de splash."""
    ram = available_ram_mb() if ram_mb is None else ram_mb
    count = cpu_cores() if cores is None else cores
    points = 0
    if ram:
        points += int(max(0, int(ram)) // (4 * 1024))
    if count:
        points += int(max(0, int(count)) // 4)
    return max(0, min(points, _MAX_POINTS))


def minimum_splash_seconds(
    ram_mb: Optional[int] = None,
    cores: Optional[int] = None,
    environ: Optional[Dict[str, str]] = None,
) -> float:
    """Segundos mínimos que el splash permanece visible.

    Parte de 5 s y suma hasta 1 s según los puntos de rendimiento, redondeado a
    múltiplos de 0,25 s. ``PM_SPLASH_MIN_SECONDS`` la sobrescribe (tests y
    desarrollo).
    """
    raw = (environ if environ is not None else os.environ).get(ENV_OVERRIDE)
    if raw not in (None, ""):
        try:
            return max(0.0, float(raw))
        except (TypeError, ValueError):
            pass
    extra = performance_points(ram_mb, cores) * _POINTS_STEP_SECONDS
    value = DEFAULT_MIN_SECONDS + extra
    return round(value / QUANTUM_SECONDS) * QUANTUM_SECONDS


@dataclass(frozen=True)
class Phase:
    """Un tramo del arranque ya medido."""

    name: str
    seconds: float

    def describe(self) -> str:
        return f"{self.name}: {self.seconds:.2f} s"


class StartupTimeline:
    """Cronómetro por fases del arranque.

    ``mark(name)`` cierra el tramo abierto con ese nombre y devuelve su
    duración.
    """

    def __init__(self, clock=time.perf_counter):
        self._clock = clock
        self._origin = clock()
        self._last = self._origin
        self._phases: List[Phase] = []

    @classmethod
    def start(cls, clock=time.perf_counter) -> "StartupTimeline":
        return cls(clock=clock)

    def mark(self, name: str) -> float:
        """Cierra la fase abierta, la registra con ``name`` y devuelve su duración."""
        now = self._clock()
        phase = Phase(str(name), max(0.0, now - self._last))
        self._phases.append(phase)
        self._last = now
        return phase.seconds

    def add(self, name: str, seconds: float) -> Phase:
        """Registra una fase medida fuera del cronómetro.

        La ventana principal mide sus tramos internos con su propio reloj; así
        el total de «ventana» no se parte y el reporte gana el desglose.
        """
        phase = Phase(str(name), max(0.0, float(seconds)))
        self._phases.append(phase)
        return phase

    @property
    def phases(self) -> Sequence[Phase]:
        return tuple(self._phases)

    def total(self) -> float:
        return max(0.0, self._last - self._origin)

    def lags(self, threshold: float = LAG_THRESHOLD_SECONDS) -> List[Phase]:
        return [phase for phase in self._phases if phase.seconds >= threshold]

    def report_lines(self, limit: int = 8) -> List[str]:
        """Las fases más lentas primero, para el cuerpo del reporte."""
        ordered = sorted(self._phases, key=lambda phase: phase.seconds, reverse=True)
        return [phase.describe() for phase in ordered[:limit]]


class SplashWaiter:
    """Retrasa el cierre del splash hasta cumplir la espera mínima.

    ``schedule(delay, callback)`` agenda la comprobación siguiente (en Qt,
    ``QTimer.singleShot``). Sin ``schedule`` el cierre es inmediato: la espera
    es cosmética y nunca debe bloquear el arranque. ``ready_seconds`` guarda el
    tiempo real de arranque en el primer aviso, antes de la espera añadida.
    """

    def __init__(self, minimum: float, *, clock=time.perf_counter, schedule=None):
        self.minimum = max(0.0, float(minimum))
        self._clock = clock
        self._schedule = schedule
        self._deadline: Optional[float] = None
        self.ready_seconds: Optional[float] = None

    def arm(self) -> None:
        """Fija el instante a partir del cual ya se puede cerrar."""
        self._deadline = self._clock() + self.minimum

    def remaining(self) -> float:
        if self._deadline is None:
            return 0.0
        return max(0.0, self._deadline - self._clock())

    def request(self, close, *, timeline: Optional[StartupTimeline] = None) -> bool:
        """Cierra si ya toca; si no, agenda otro aviso. ``True`` si cerró."""
        if self.ready_seconds is None and timeline is not None:
            self.ready_seconds = timeline.total()
        remaining = self.remaining()
        if remaining > 0 and self._schedule is not None:
            self._schedule(remaining, lambda: self.request(close, timeline=timeline))
            return False
        close()
        return True


def _signature(lags: Iterable[Phase], overdue: bool) -> str:
    """Huella estable: qué fases se pasaron de tiempo, no cuánto exactamente."""
    names = ",".join(sorted(phase.name for phase in lags))
    return f"{names}|overdue={int(overdue)}"


def startup_lag_report(
    timeline: StartupTimeline,
    *,
    errors: Sequence[str] = (),
    minimum: Optional[float] = None,
    ready: Optional[float] = None,
    threshold: float = LAG_THRESHOLD_SECONDS,
) -> Optional[dict]:
    """Entrada de reporte si el arranque sufrió tirones; ``None`` si fue fino.

    Un tirón es una fase que supera ``threshold`` o una interfaz que no estuvo
    lista dentro de la espera mínima del splash. ``ready`` es el tiempo real de
    arranque medido cuando la compuerta decidió: sin él se usa el total del
    cronómetro, que incluiría la espera deliberada del splash.
    """
    from lib import report_telemetry

    expected = minimum_splash_seconds() if minimum is None else float(minimum)
    measured = timeline.total() if ready is None else max(0.0, float(ready))
    lags = timeline.lags(threshold)
    overdue = measured > expected
    if not lags and not overdue:
        return None

    lines = ["El arranque de Package Maker sufrió tirones.", ""]
    lines.append(f"Espera mínima del splash: {expected:.2f} s")
    lines.append(f"Interfaz lista en: {measured:.2f} s")
    lines.append("")
    lines.append("Fases más lentas:")
    lines.extend(f"- {line}" for line in timeline.report_lines())
    pending = [str(error) for error in errors if str(error).strip()]
    if pending:
        lines.extend(["", "Errores restantes del arranque:"])
        lines.extend(f"- {error}" for error in pending)

    slowest = max((phase.seconds for phase in lags), default=0.0)
    if lags:
        title = f"[auto] Arranque con tirones ({slowest:.1f} s en {lags[0].name})"
    else:
        title = f"[auto] Arranque lento: interfaz lista en {measured:.1f} s"
    return {
        "title": title[:240],
        "description": report_telemetry.sanitize("\n".join(lines)),
        "kind": "StartupLag",
        "fingerprint": report_telemetry.fingerprint(
            "StartupLag", _signature(lags, overdue)
        ),
        "environment": report_telemetry.collect_environment(),
        "auto": True,
    }
