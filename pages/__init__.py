#!/usr/bin/env python3
"""
Simplified Pages Package
"""
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

# Only import existing pages
_pages = {}

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

__all__ = ['get_page_layout']
