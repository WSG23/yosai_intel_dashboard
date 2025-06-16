# pages/__init__.py - Safe page imports
"""
Dashboard pages package
"""

try:
    from . import deep_analytics
except ImportError as e:
    print(f"Warning: Could not import deep_analytics: {e}")
    deep_analytics = None

__all__ = ['deep_analytics']
