"""Root conftest — shared fixtures and CLI flags."""
from __future__ import annotations


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden snapshot files instead of comparing",
    )
