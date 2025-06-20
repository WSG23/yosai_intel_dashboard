"""Component registry with safe imports and fallbacks"""
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Manages component loading with fallbacks"""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._load_all_components()

    def _load_all_components(self) -> None:
        """Load all components with error handling"""
        logger.info("🔄 Loading all components...")
        
        # Load main components with full debug logging
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
        except Exception as e:
            logger.warning(f"Could not load analytics module: {e}")
            self._components["analytics_module"] = None

        # Debug: Log what was loaded
        self._log_component_status()

    def _safe_import_component(self, module_path: str, component_name: str) -> Any:
        """Safe component import with detailed logging"""
        try:
            logger.info(f"🔄 Attempting to import {component_name} from {module_path}")
            
            # Import the module
            module = __import__(module_path, fromlist=[component_name])
            logger.info(f"✅ Module {module_path} imported successfully")
            
            # Get the component attribute
            component = getattr(module, component_name, None)
            
            if component is not None:
                logger.info(f"✅ Component {component_name} loaded successfully from {module_path}")
                # Test if it's callable and works
                if callable(component):
                    try:
                        test_result = component()
                        logger.info(f"✅ Component {component_name} is callable and working")
                    except Exception as test_e:
                        logger.warning(f"⚠️ Component {component_name} callable but failed test: {test_e}")
                return component
            else:
                logger.error(f"❌ Component {component_name} not found in {module_path}")
                return None
                
        except ImportError as e:
            logger.error(f"❌ ImportError loading {component_name} from {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error loading {component_name}: {e}")
            return None

    def _safe_import_module(self, module_path: str) -> Any:
        """Safe module import"""
        try:
            logger.info(f"🔄 Importing module {module_path}")
            module = __import__(module_path, fromlist=[""])
            logger.info(f"✅ Module {module_path} imported successfully")
            return module
        except ImportError as e:
            logger.warning(f"❌ Could not import module {module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error importing module {module_path}: {e}")
            return None

    def get_component(self, name: str) -> Any:
        """Get a component safely"""
        component = self._components.get(name)
        if component is not None:
            logger.debug(f"✅ Retrieved component '{name}' successfully")
        else:
            logger.warning(f"❌ Component '{name}' not found in registry")
        return component

    def get_component_or_fallback(self, name: str, fallback_text: str) -> Any:
        """Get component or return proper fallback"""
        component = self.get_component(name)
        
        if component is not None:
            logger.debug(f"✅ Using real component for '{name}'")
            return component
        
        # Component failed to load, use fallback
        logger.warning(f"⚠️ Using fallback for '{name}': {fallback_text}")
        
        # Try to import html for a proper fallback
        try:
            from dash import html
            return html.Div([
                html.H4(f"Component Loading Error", className="text-warning"),
                html.P(fallback_text, className="text-muted"),
                html.Small(f"Component '{name}' failed to load", className="text-info")
            ], className="alert alert-warning text-center", style={"margin": "1rem", "padding": "1rem"})
        except ImportError:
            # Ultimate fallback - return simple text
            return f"FALLBACK: {fallback_text}"

    def _log_component_status(self) -> None:
        """Log the status of all loaded components"""
        logger.info("=== COMPONENT REGISTRY STATUS ===")
        for component_name, component in self._components.items():
            status = "✅ LOADED" if component is not None else "❌ FAILED"
            component_type = type(component).__name__ if component is not None else "None"
            logger.info(f"  {component_name}: {status} ({component_type})")
        logger.info("================================")

    def list_components(self) -> Dict[str, bool]:
        """Return a dictionary of component names and their load status"""
        return {name: comp is not None for name, comp in self._components.items()}

    def reload_component(self, name: str) -> bool:
        """Attempt to reload a specific component"""
        logger.info(f"🔄 Attempting to reload component '{name}'")
        
        # Component mapping for reload
        component_map = {
            "incident_alerts": ("components.incident_alerts_panel", "layout"),
            "map_panel": ("components.map_panel", "layout"),
            "bottom_panel": ("components.bottom_panel", "layout"),
            "weak_signal": ("components.weak_signal_panel", "layout"),
            "navbar": ("dashboard.layout.navbar", "create_navbar_layout"),
        }
        
        if name in component_map:
            module_path, component_name = component_map[name]
            self._components[name] = self._safe_import_component(module_path, component_name)
            return self._components[name] is not None
        else:
            logger.error(f"❌ Unknown component name for reload: {name}")
            return False
