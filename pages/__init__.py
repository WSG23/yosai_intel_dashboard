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


def get_page_layout(page_name: str) -> Optional[Callable]:
    """Get page layout function safely"""
    page_module = _pages.get(page_name)
    if page_module and hasattr(page_module, 'layout'):
        return page_module.layout
    return None


def register_page_callbacks(page_name: str, app: Any, container: Any = None) -> bool:
    """Register page callbacks safely"""
    page_module = _pages.get(page_name)
    if page_module and hasattr(page_module, 'register_analytics_callbacks'):
        try:
            page_module.register_analytics_callbacks(app, container)
            return True
        except Exception as e:
            logger.error(f"Failed to register callbacks for {page_name}: {e}")
    return False

__all__ = ['get_page_layout', 'register_page_callbacks']

