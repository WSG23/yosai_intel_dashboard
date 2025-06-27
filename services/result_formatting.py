"""Utilities to format analytics results for presentation."""

from __future__ import annotations

from typing import Dict, Any


def format_dashboard_summary(analytics: Dict[str, Any]) -> Dict[str, Any]:
    """Return dashboard summary structure.

    The default implementation simply echoes the analytics dictionary but
    exists as a dedicated hook for future formatting logic.
    """
    return analytics

__all__ = ["format_dashboard_summary"]
