"""Exercise only pure watchdog rules: no nvidia-smi, CUDA, or model execution."""

import runpy
from pathlib import Path


def test_watchdog_limits():
    rules = runpy.run_path(str(Path(__file__).parents[1] / "scripts/gpu-smoke.py"))
    stop = rules["stop_reason"]
    assert stop(60, 2048, 1) is None
    assert "temperature" in stop(75, 2048, 1)
    assert "VRAM" in stop(60, 512, 1)
    assert "time limit" in stop(60, 2048, 60)
