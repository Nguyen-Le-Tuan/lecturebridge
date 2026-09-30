"""Real GPU tests always require an explicit command-line opt-in."""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-gpu",
        action="store_true",
        default=False,
        help="Explicitly allow tests that load real models on NVIDIA hardware",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-gpu"):
        return
    skip = pytest.mark.skip(
        reason="GPU tests are disabled; manual opt-in requires --run-gpu"
    )
    for item in items:
        if "gpu" in item.keywords:
            item.add_marker(skip)
