# core/callback_manager.py
"""Callback management extracted from DashboardApp.register_all_callbacks()"""
from typing import Any, Optional
import logging
from .component_registry import ComponentRegistry
from .layout_manager import LayoutManager

logger = logging.getLogger(__name__)

class CallbackManager:
    """Manages callback registration with Dependency Injection"""
    
    def __init__(self, app: Any, component_registry: ComponentRegistry, layout_manager: LayoutManager, container: Any):
        self.app = app
        self.registry = component_registry
        self.layout_manager = layout_manager
        self.container = container  # NEW: DI container
    
    def register_all_callbacks(self) -> None:
        """Register all callbacks - extracted from your register_all_callbacks()"""
        try:
            # Register page routing callback
            self._register_page_routing_callback()
            
            # Register component callbacks safely
            self._register_component_callbacks()
            
            # Register analytics callbacks
            self._register_analytics_callbacks()
            
            # Register navbar callback
            self._register_navbar_callback()
            
            logger.info("All callbacks registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering callbacks: {e}")
    
    def _register_page_routing_callback(self) -> None:
        """Page routing - extracted from your register_page_routing_callback()"""
        try:
            from dash import Output, Input
            
            @self.app.callback(
                Output('page-content', 'children'),
                Input('url', 'pathname'),
                prevent_initial_call=False
            )
            def display_page(pathname: Optional[str]) -> Any:
                """Route to appropriate page content"""
                try:
                    if pathname == '/analytics':
                        return self._handle_analytics_page()
                    else:
                        # Default to dashboard
                        return self.layout_manager.create_dashboard_content()
                        
                except Exception as e:
                    logger.error(f"Error in page routing: {e}")
                    return self._create_error_page(f"Page routing error: {str(e)}")
        
        except ImportError:
            logger.error("Cannot register page routing - Dash not available")
    
    def _handle_analytics_page(self) -> Any:
        """Handle analytics page - extracted from your display_page logic"""
        analytics_module = self.registry.get_component('analytics_module')
        
        if analytics_module is not None:
            layout_func = getattr(analytics_module, 'layout', None)
            if layout_func is not None and callable(layout_func):
                try:
                    return layout_func()
                except Exception as e:
                    logger.error(f"Error creating analytics layout: {e}")
                    return self._create_error_page(f"Error loading analytics page: {str(e)}")
        
        return self._create_error_page("Analytics page not available")
    
    def _create_error_page(self, message: str) -> Any:
        """Create error page"""
        try:
            from dash import html
            import dash_bootstrap_components as dbc
            
            return html.Div([
                dbc.Alert(message, color="warning", className="m-3")
            ])
        except ImportError:
            return None
    
    def _register_component_callbacks(self) -> None:
        """Register component callbacks - extracted from your logic"""
        # Map panel callbacks
        map_panel_register = self.registry.get_component('map_panel_callbacks')
        if map_panel_register is not None:
            try:
                map_panel_register(self.app)
                logger.info("Map panel callbacks registered")
            except Exception as e:
                logger.error(f"Error registering map panel callbacks: {e}")
    
    def _register_analytics_callbacks(self) -> None:
        """Register analytics callbacks with DI container"""
        analytics_module = self.registry.get_component('analytics_module')
        if analytics_module is not None:
            register_func = getattr(analytics_module, 'register_analytics_callbacks', None)
            if register_func is not None:
                try:
                    # Pass container to analytics callbacks for DI
                    register_func(self.app, self.container)
                    logger.info("Analytics callbacks registered with DI")
                except Exception as e:
                    logger.error(f"Error registering analytics callbacks: {e}")
                    # Fallback: try without container for backward compatibility
                    try:
                        register_func(self.app)
                        logger.info("Analytics callbacks registered (fallback)")
                    except Exception as e2:
                        logger.error(f"Fallback registration also failed: {e2}")
    
    def _register_navbar_callback(self) -> None:
        """Register navbar callback - extracted from your register_navbar_callback()"""
        try:
            from dash import Output, Input
            from datetime import datetime
            
            @self.app.callback(
                Output("live-time", "children"),
                Input("live-time", "id"),
                prevent_initial_call=False
            )
            def update_time(_: Any) -> str:
                """Update live time display"""
                try:
                    return f"Live Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                except Exception as e:
                    logger.error(f"Error updating time: {e}")
                    return "Time unavailable"
        
        except Exception as e:
            logger.error(f"Error registering navbar callback: {e}")