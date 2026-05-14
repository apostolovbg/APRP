"""APRP installation hook entrypoints."""

from __future__ import annotations


def before_install() -> None:
    """Prepare APRP for installation."""


def after_install() -> None:
    """Finalize APRP after installation."""


def before_tests() -> None:
    """Prepare APRP for the test lifecycle."""
