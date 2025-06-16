# core/component_registry.py
"""Component registry with safe imports - extracted from app.py"""
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class ComponentRegistry:
    """Manages component loading with fallbacks - replaces safe_import_* functions from app.py"""
    
    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._load_all_components()
    
    def _load_all_components(self) -> None:
        """Load all components with error handling"""
        # Extract all your current safe_import_* calls from app.py
        self._components['navbar'] = self._safe_import_component('components.navbar', 'layout')
        self._components['map_panel'] = self._safe_import_component('components.map_panel', 'layout')
        self._components['bottom_panel'] = self._safe_import_component('components.bottom_panel', 'layout')
        self._components['incident_alerts'] = self._safe_import_component('components.incident_alerts_panel', 'layout')
        self._components['weak_signal'] = self._safe_import_component('components.weak_signal_panel', 'layout')
        
        # Load callback registration functions
        self._components['map_panel_callbacks'] = self._safe_import_component('components.map_panel', 'register_callbacks')
        self._components['navbar_callbacks'] = self._safe_import_component('components.navbar', 'register_navbar_callbacks')
        
        # Load pages
        self._components['analytics_module'] = self._safe_import_module('pages.deep_analytics')
    
    def _safe_import_component(self, module_path: str, component_name: str) -> Any:
        """Safe component import - extracted from your safe_import_component()"""
        try:
            module = __import__(module_path, fromlist=[component_name])
            return getattr(module, component_name, None)
        except ImportError as e:
            logger.warning(f"Could not import {component_name} from {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error importing {component_name}: {e}")
            return None
    
    def _safe_import_module(self, module_path: str) -> Any:
        """Safe module import - extracted from your safe_import_module()"""
        try:
            return __import__(module_path, fromlist=[''])
        except ImportError as e:
            logger.warning(f"Could not import module {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error importing module {module_path}: {e}")
            return None
    
    def get_component(self, name: str) -> Any:
        """Get a component safely"""
        return self._components.get(name)
    
    def get_component_or_fallback(self, name: str, fallback_text: str) -> Any:
        """Get component or return fallback - replaces your safe_component() function"""
        component = self.get_component(name)
        if component is not None:
            return component
        
        # Import html for fallback
        try:
            from dash import html
            return html.Div(
                fallback_text,
                className="alert alert-warning text-center",
                style={"margin": "1rem", "padding": "1rem"}
            )
        except ImportError:
            # Ultimate fallback
            return None