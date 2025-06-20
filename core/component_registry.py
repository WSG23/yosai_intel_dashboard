"""Component registry with safe imports and fallbacks"""
from typing import Any, Optional, Dict
import logging
from utils.safe_components import get_safe_component

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Manages component loading with fallbacks"""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._load_all_components()

    def _load_all_components(self) -> None:
        """Load all components with error handling"""
        # Load your actual components with fallbacks
        self._components["navbar"] = self._safe_import_component(
            "dashboard.layout.navbar", "create_navbar_layout"
        )
        self._components["incident_alerts"] = self._safe_import_component(
            "components.incident_alerts_panel", "layout"
        )
        self._components["map_panel"] = self._safe_import_component(
            "components.map_panel", "layout"
        )
        self._components["bottom_panel"] = self._safe_import_component(
            "components.bottom_panel", "layout"
        )
        self._components["weak_signal"] = self._safe_import_component(
            "components.weak_signal_panel", "layout"
        )

        # Load callback registration functions
        self._components["map_panel_callbacks"] = self._safe_import_component(
            "components.map_panel", "register_callbacks"
        )
        self._components["navbar_callbacks"] = self._safe_import_component(
            "dashboard.layout.navbar", "register_navbar_callbacks"
        )

        # Load pages with safe handling
        try:
            self._components["analytics_module"] = self._safe_import_module(
                "pages.deep_analytics"
            )
            if self._components["analytics_module"]:
                logger.info("✅ Analytics module loaded successfully")
            else:
                logger.warning("⚠️ Analytics module not available")
        except Exception as e:
            logger.error(f"Error loading analytics module: {e}")
            self._components["analytics_module"] = None

    def _safe_import_component(self, module_path: str, component_name: str) -> Any:
        """Safe component import with fallback"""
        try:
            module = __import__(module_path, fromlist=[component_name])
            component = getattr(module, component_name, None)
            if callable(component):
                return component
            else:
                logger.warning(f"Component {component_name} is not callable")
                return None
        except ImportError as e:
            logger.warning(f"Could not import {component_name} from {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error importing {component_name}: {e}")
            return None

    def _safe_import_module(self, module_path: str) -> Any:
        """Safe module import"""
        try:
            return __import__(module_path, fromlist=[""])
        except ImportError as e:
            logger.warning(f"Could not import module {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error importing module {module_path}: {e}")
            return None

    def get_component(self, name: str) -> Optional[Any]:
        """Get component by name"""
        return self._components.get(name)

    def get_component_or_fallback(self, name: str, fallback_text: str = None) -> Any:
        """Get component or return safe fallback"""
        component = self.get_component(name)

        if component and callable(component):
            try:
                result = component()
                # Ensure result is JSON-safe
                if hasattr(result, '__dict__'):
                    # Component returned an object, convert to safe representation
                    return self._make_component_safe(result)
                return result
            except Exception as e:
                logger.error(f"Error calling component {name}: {e}")

        # Use safe component fallback from existing safe_components.py
        from utils.safe_components import get_safe_component
        safe_component = get_safe_component(name)
        if safe_component:
            return safe_component

        # Ultimate fallback
        from dash import html
        return html.Div(
            fallback_text or f"Component '{name}' not available",
            className="alert alert-warning"
        )

    def _make_component_safe(self, component):
        """Make any component JSON-safe"""
        try:
            # Test if component is already safe
            import json
            json.dumps(str(component))
            return component
        except Exception:
            # Convert to safe string representation
            return str(component)

    def has_component(self, name: str) -> bool:
        """Check if component exists"""
        return name in self._components and self._components[name] is not None
