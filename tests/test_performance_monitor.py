import importlib.util
from pathlib import Path
import pytest

# Skip tests if psutil dependency is missing
if importlib.util.find_spec("psutil") is None:
    pytest.skip("psutil not available", allow_module_level=True)

spec = importlib.util.spec_from_file_location(
    "core.performance",
    Path(__file__).resolve().parents[1] / "core" / "performance.py"
)
performance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(performance)
PerformanceMonitor = performance.PerformanceMonitor
get_performance_monitor = performance.get_performance_monitor


def test_get_performance_monitor_singleton():
    m1 = get_performance_monitor()
    m2 = get_performance_monitor()
    assert isinstance(m1, PerformanceMonitor)
    assert m1 is m2


def test_record_metric_via_singleton():
    monitor = get_performance_monitor()
    initial = len(monitor.metrics)
    monitor.record_metric("test.metric", 1.0)
    assert len(monitor.metrics) == initial + 1
