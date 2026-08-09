"""Tests for the Prometheus text exposition formatter."""
from __future__ import annotations

from backend.services import metrics as prom


def setup_function(_):
    prom._counters.clear()
    prom._gauges.clear()
    prom._histograms.clear()


def test_counter_accumulates() -> None:
    prom.inc("robot_logic_hits", 1.5)
    prom.inc("robot_logic_hits", 2.5)
    text = prom.render()
    assert "# TYPE robot_logic_hits counter" in text
    assert "robot_logic_hits 4.0" in text


def test_gauge_overwrites() -> None:
    prom.set_gauge("robot_logic_devices", 4)
    prom.set_gauge("robot_logic_devices", 6)
    text = prom.render()
    assert "# TYPE robot_logic_devices gauge" in text
    assert "robot_logic_devices 6" in text


def test_histogram_quantiles_rendered() -> None:
    for v in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        prom.observe("tick_latency_ms", float(v))
    text = prom.render()
    assert "tick_latency_ms_count 10" in text
    assert "tick_latency_ms_sum 550" in text
    assert "tick_latency_ms" in text


def test_histogram_bounded_by_max_samples() -> None:
    for v in range(2000):
        prom.observe("busy", float(v))
    snap = prom.snapshot()
    assert len(snap["histograms"]["busy"]) == 32
