"""Navbar component wrapper."""
from dashboard.layout.navbar import create_navbar_layout, layout, register_navbar_callbacks

# Expose simplified function name

def create_navbar():
    return create_navbar_layout()

__all__ = ["create_navbar", "layout", "register_navbar_callbacks"]

