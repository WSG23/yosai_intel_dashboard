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

__all__ = ['NAVBAR_AVAILABLE', 'ANALYTICS_AVAILABLE', 'SETTINGS_MODAL_AVAILABLE']

if NAVBAR_AVAILABLE:
    __all__.append('create_navbar')
if ANALYTICS_AVAILABLE:
    __all__.append('analytics')
if SETTINGS_MODAL_AVAILABLE:
    __all__.extend(['create_settings_modal', 'register_settings_modal_callbacks'])

# Dual upload component is now provided via plugin
try:
    from plugins.file_upload_plugin import (
        create_dual_file_uploader,
        register_dual_upload_callbacks,
    )
    DUAL_UPLOAD_AVAILABLE = True
except Exception as e:
    logger.warning(f"Dual upload component not available: {e}")
    DUAL_UPLOAD_AVAILABLE = False

__all__.append('DUAL_UPLOAD_AVAILABLE')

if DUAL_UPLOAD_AVAILABLE:
    __all__.extend(['create_dual_file_uploader', 'register_dual_upload_callbacks'])

