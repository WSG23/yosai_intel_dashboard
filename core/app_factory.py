# core/app_factory.py
"""App factory with Dependency Injection - replaces DashboardApp class from app.py"""
from typing import Any, Optional
import logging
from .config_manager import ConfigManager
from .component_registry import ComponentRegistry  
from .layout_manager import LayoutManager
from .callback_manager import CallbackManager
from .service_registry import get_configured_container
from .container import Container

logger = logging.getLogger(__name__)

class DashAppFactory:
    """Factory for creating Dash applications with Dependency Injection"""
    
    @staticmethod
    def create_app(container: Optional[Container] = None) -> Optional[Any]:
        """Create and configure Dash app with DI container"""
        
        # Use provided container or get configured one
        if container is None:
            container = get_configured_container()
        
        try:
            import dash
            
            # Get config from container
            config_manager = container.get('config')
            
            # Create Dash app with configuration
            app = dash.Dash(
                __name__,
                external_stylesheets=config_manager.get_stylesheets(),
                suppress_callback_exceptions=True,
                meta_tags=config_manager.get_meta_tags()
            )
            
            # Configure app
            app.title = config_manager.app_config.title
            
            # Store container in app for access in callbacks
            app._yosai_container = container
            
            # Initialize components with container
            component_registry = ComponentRegistry()
            layout_manager = LayoutManager(component_registry)
            callback_manager = CallbackManager(app, component_registry, layout_manager, container)
            
            # Set layout
            app.layout = layout_manager.create_main_layout()
            
            # Register callbacks
            callback_manager.register_all_callbacks()
            
            logger.info("Dashboard application created successfully with DI")
            return app
            
        except ImportError:
            logger.error("Cannot create app - Dash not available")
            return None
        except Exception as e:
            logger.error(f"Failed to create Dash application: {e}")
            return None

def create_application() -> Optional[Any]:
    """Create application with dependency injection"""
    try:
        # Check if Dash is available
        import dash
        
        # Create configured container
        container = get_configured_container()
        
        # Create app with container
        app = DashAppFactory.create_app(container)
        
        if app is None:
            logger.error("Failed to create Dash app instance")
            return None
        
        logger.info("Dashboard application created successfully with DI")
        return app
        
    except ImportError:
        logger.error("Cannot create application - Dash dependencies not available")
        print("❌ Error: Dash not installed. Run: pip install dash dash-bootstrap-components")
        return None
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        return None