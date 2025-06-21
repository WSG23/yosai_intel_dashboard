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

try:
    from .settings_modal import create_settings_modal, register_settings_modal_callbacks
    SETTINGS_MODAL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Settings modal component not available: {e}")
    SETTINGS_MODAL_AVAILABLE = False

try:
    from .door_mapping_modal import create_door_mapping_modal, register_door_mapping_modal_callbacks
    DOOR_MAPPING_MODAL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Door mapping modal component not available: {e}")
    DOOR_MAPPING_MODAL_AVAILABLE = False

__all__ = ['NAVBAR_AVAILABLE', 'ANALYTICS_AVAILABLE', 'SETTINGS_MODAL_AVAILABLE', 'DOOR_MAPPING_MODAL_AVAILABLE']

if NAVBAR_AVAILABLE:
    __all__.append('create_navbar')
if ANALYTICS_AVAILABLE:
    __all__.append('analytics')
if SETTINGS_MODAL_AVAILABLE:
    __all__.extend(['create_settings_modal', 'register_settings_modal_callbacks'])

if DOOR_MAPPING_MODAL_AVAILABLE:
    __all__.extend(['create_door_mapping_modal', 'register_door_mapping_modal_callbacks'])


