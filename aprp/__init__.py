"""APRP package root."""

from __future__ import annotations

from pathlib import Path

__all__ = ["__version__"]

_version_file = Path(__file__).resolve().parents[1] / "VERSION"
__version__ = _version_file.read_text(encoding="utf-8").strip()
