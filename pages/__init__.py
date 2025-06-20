"""
Safe page imports with fallback handling
"""
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

# Safe page imports
_pages: dict[str, Optional[Any]] = {}

try:
    from . import deep_analytics
    _pages['deep_analytics'] = deep_analytics
except ImportError as e:
    logger.warning(f"Deep analytics page not available: {e}")
    _pages['deep_analytics'] = None

try:
    from . import file_upload
    _pages['file_upload'] = file_upload
except ImportError as e:
    logger.warning(f"File upload page not available: {e}")
    _pages['file_upload'] = None


def get_page_layout(page_name: str) -> Optional[Callable]:
    """Get page layout function safely"""
    page_module = _pages.get(page_name)
    if page_module and hasattr(page_module, 'layout'):
        return page_module.layout
    return None


def register_page_callbacks(page_name: str, app: Any, container: Any = None) -> bool:
    """Register page callbacks safely"""
    page_module = _pages.get(page_name)
    
    if page_name == 'deep_analytics' and page_module and hasattr(page_module, 'register_analytics_callbacks'):
        try:
            page_module.register_analytics_callbacks(app, container)
            return True
        except Exception as e:
            logger.error(f"Failed to register analytics callbacks: {e}")
    
    elif page_name == 'file_upload' and page_module and hasattr(page_module, 'register_file_upload_callbacks'):
        try:
            page_module.register_file_upload_callbacks(app, container)
            return True
        except Exception as e:
            logger.error(f"Failed to register file upload callbacks: {e}")
    
    return False


def get_available_pages():
    """Get list of available pages"""
    return [name for name, module in _pages.items() if module is not None]


__all__ = ['get_page_layout', 'register_page_callbacks', 'get_available_pages']
