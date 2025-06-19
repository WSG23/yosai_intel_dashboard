"""
Modular components package with safe imports
"""
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

# Safe component imports
try:
    from .navbar import create_navbar
    NAVBAR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Navbar component not available: {e}")
    NAVBAR_AVAILABLE = False

try:
    from . import analytics
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analytics components not available: {e}")
    ANALYTICS_AVAILABLE = False

__all__ = ['NAVBAR_AVAILABLE', 'ANALYTICS_AVAILABLE']

if NAVBAR_AVAILABLE:
    __all__.append('create_navbar')
if ANALYTICS_AVAILABLE:
    __all__.append('analytics')

