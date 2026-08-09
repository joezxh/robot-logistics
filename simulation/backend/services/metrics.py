"""Lightweight, dependency-free Prometheus exposition formatter.

We do not pull in the `prometheus_client` library to keep the runtime
footprint small. Instead we maintain counters / gauges / histograms in
process memory and format them as text/plain on /metrics.
"""
from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Dict, List, Tuple

_lock = Lock()
_counters: Dict[str, float] = defaultdict(float)
_gauges: Dict[str, float] = defaultdict(float)
_histograms: Dict[str, List[float]] = defaultdict(list)


def inc(name: str, value: float = 1.0) -> None:
    with _lock:
        _counters[name] += value


def set_gauge(name: str, value: float) -> None:
    with _lock:
        _gauges[name] = value


def observe(name: str, value: float) -> None:
    with _lock:
        _histograms[name].append(value)
        # Bound memory: keep the most recent 1024 samples.
        if len(_histograms[name]) > 1024:
            _histograms[name] = _histograms[name][-1024:]


def render() -> str:
    lines: List[str] = []
    with _lock:
        for name, value in sorted(_counters.items()):
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        for name, value in sorted(_gauges.items()):
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        for name, samples in sorted(_histograms.items()):
            if not samples:
                continue
            sorted_samples = sorted(samples)
            count = len(sorted_samples)
            total = sum(sorted_samples)
            lines.append(f"# TYPE {name} summary")
            lines.append(f"{name}_count {count}")
            lines.append(f"{name}_sum {total:.4f}")
            for q in (0.5, 0.9, 0.99):
                idx = max(0, min(count - 1, int(q * (count - 1))))
                lines.append(f"{name}_{{{quantile_label(q)}}}={sorted_samples[idx]}")
    return "\n".join(lines) + "\n"


def quantile_label(q: float) -> str:
    return f"q{int(q * 100)}"


def snapshot() -> dict:
    """Return a JSON-serializable copy of all metrics (useful for /api/metrics)."""
    with _lock:
        return {
            "counters": dict(_counters),
            "gauges": dict(_gauges),
            "histograms": {name: list(samples[-32:]) for name, samples in _histograms.items()},
        }
