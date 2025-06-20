"""
Navbar Plugin - Grid layout with icons and dynamic content
Implements PluginProtocol for the Yōsai Intel Dashboard
"""

import datetime
import logging
from typing import TYPE_CHECKING, Dict, Any
from dataclasses import dataclass

from flask_babel import lazy_gettext as _l
from core.plugins.protocols import PluginProtocol, CallbackPluginProtocol, PluginMetadata, PluginPriority
from core.plugins.decorators import safe_callback

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input

try:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input
    DASH_AVAILABLE = True
except ImportError:
    logger.warning("Dash components not available")
    DASH_AVAILABLE = False
    dbc = html = dcc = callback = Output = Input = None


@dataclass
class NavbarConfig:
    """Navbar plugin configuration"""
    location_name: str = "Tokyo HQ"
    zone_name: str = "East Wing"
    user_info: str = "HQ Tower – East Wing"
    logo_path: str = "/assets/yosai_logo_name_white.png"
    logo_height: str = "45px"
    enable_language_toggle: bool = True
    enable_live_time: bool = True
    icons_base_path: str = "/assets/navbar_icons"


class NavbarPlugin(CallbackPluginProtocol):
    """
    Navbar Plugin with responsive grid layout, icons, and dynamic content
    """
    
    def __init__(self):
        self.config = NavbarConfig()
        self._app = None
        self._container = None
        self._status = {"healthy": True, "errors": []}
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="navbar",
            version="2.0.0",
            description="Responsive navbar with grid layout and icon navigation",
            author="Yōsai Intel Team",
            priority=PluginPriority.CRITICAL,
            dependencies=[],
            config_section="navbar",
            enabled_by_default=True
        )
    
    def load(self, container: Any, config: Dict[str, Any]) -> bool:
        """Load navbar plugin with configuration"""
        try:
            self._container = container
            
            # Update config from provided settings
            navbar_config = config.get("navbar", {})
            if navbar_config:
                for key, value in navbar_config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Register navbar layout service
            container.register('navbar_layout', self.create_navbar_layout)
            container.register('navbar_plugin', self)
            
            logger.info("Navbar plugin loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load navbar plugin: {e}")
            self._status["errors"].append(str(e))
            return False
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure navbar plugin"""
        try:
            navbar_settings = config.get("navbar", {})
            for key, value in navbar_settings.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as e:
            logger.error(f"Failed to configure navbar plugin: {e}")
            return False
    
    def start(self) -> bool:
        """Start navbar plugin"""
        return True
    
    def stop(self) -> bool:
        """Stop navbar plugin"""
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return navbar plugin health status"""
        return {
            "healthy": self._status["healthy"] and DASH_AVAILABLE,
            "dash_available": DASH_AVAILABLE,
            "errors": self._status["errors"],
            "config": {
                "location": self.config.location_name,
                "zone": self.config.zone_name,
                "icons_enabled": True
            }
        }
    
    def create_navbar_layout(self):
        """Create responsive navbar layout with grid system"""
        if not DASH_AVAILABLE:
            return html.Div("Navbar unavailable - Dash components missing", 
                          className="navbar__fallback")
        
        try:
            return dbc.Navbar(
                [
                    dbc.Container(
                        [
                            dcc.Location(id="url-i18n"),
                            # Main grid container
                            html.Div(
                                [
                                    # Left Column: Logo Area
                                    html.Div(
                                        [
                                            html.A(
                                                html.Img(
                                                    src=self.config.logo_path,
                                                    height=self.config.logo_height,
                                                    className="navbar__logo",
                                                ),
                                                href="/",
                                                className="navbar__logo-link",
                                                style={"text-decoration": "none"}
                                            )
                                        ],
                                        className="navbar__left-column",
                                    ),
                                    
                                    # Center Column: Main Panel Label & Context
                                    html.Div(
                                        [
                                            html.Div(
                                                f"Main Panel: {self.config.location_name} – {self.config.zone_name}",
                                                className="navbar__main-label",
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        f"Logged in as: {self.config.user_info}",
                                                        className="navbar__user-info"
                                                    ),
                                                    html.Span(
                                                        [
                                                            html.Span("🟢", className="status-indicator"),
                                                            html.Span(
                                                                id="live-time",
                                                                children="Live: 2025-06-20 09:55:54",
                                                                className="navbar__live-time"
                                                            )
                                                        ],
                                                        className="ml-2"
                                                    ) if self.config.enable_live_time else None
                                                ],
                                                className="navbar__status-bar",
                                            )
                                        ],
                                        className="navbar__center-column",
                                    ),
                                    
                                    # Right Column: Navigation Icons + Language Toggle
                                    html.Div(
                                        [
                                            # Navigation Icons
                                            self._create_navigation_icons(),
                                            
                                            # Language Toggle
                                            self._create_language_toggle() if self.config.enable_language_toggle else None,
                                        ],
                                        className="navbar__right-column",
                                    ),
                                ],
                                className="navbar__grid-container",
                            ),
                        ],
                        fluid=True,
                        className="navbar__container"
                    )
                ],
                color="dark",
                dark=True,
                sticky="top",
                className="navbar__main"
            )
            
        except Exception as e:
            logger.error(f"Error creating navbar layout: {e}")
            self._status["errors"].append(str(e))
            return html.Div("Navbar error", className="navbar__fallback")
    
    def _create_navigation_icons(self):
        """Create navigation icons with hover effects"""
        nav_items = [
            {"icon": "dashboard.png", "href": "/", "title": "Dashboard", "alt": "Dashboard"},
            {"icon": "analytics.png", "href": "/analytics", "title": "Analytics", "alt": "Analytics"},
            {"icon": "upload.png", "href": "/file-upload", "title": "File Upload", "alt": "Upload"},
            {"icon": "print.png", "href": "/export", "title": "Export", "alt": "Export"},
            {"icon": "setting.png", "href": "/settings", "title": "Settings", "alt": "Settings"},
            {"icon": "logout.png", "href": "/logout", "title": "Logout", "alt": "Logout"},
        ]
        
        return html.Div(
            [
                html.A(
                    html.Img(
                        src=f"{self.config.icons_base_path}/{item['icon']}",
                        className="navbar__icon",
                        alt=item["alt"]
                    ),
                    href=item["href"],
                    className="navbar__nav-link",
                    title=item["title"]
                ) for item in nav_items
            ],
            className="navbar__icons-container",
        )
    
    def _create_language_toggle(self):
        """Create language toggle component"""
        return html.Div(
            [
                html.Span("EN", className="navbar__lang-option navbar__lang-active"),
                html.Span(" | ", className="navbar__lang-separator"),
                html.Span("JP", className="navbar__lang-option"),
            ],
            className="navbar__language-toggle ml-4",
            id="language-toggle"
        )
    
    def register_callbacks(self, app: Any, container: Any) -> bool:
        """Register navbar callbacks"""
        if not DASH_AVAILABLE:
            return False
            
        try:
            self._app = app
            
            # Live time update callback
            if self.config.enable_live_time:
                @app.callback(
                    Output("live-time", "children"),
                    Input("url-i18n", "pathname"),
                )
                @safe_callback
                def update_live_time(pathname):
                    """Update live time display"""
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return f"Live: {current_time}"
            
            # Language toggle callback (if enabled)
            if self.config.enable_language_toggle:
                @app.callback(
                    Output("language-toggle", "children"),
                    Input("language-toggle", "n_clicks"),
                    prevent_initial_call=True
                )
                @safe_callback
                def toggle_language(n_clicks):
                    """Toggle between EN and JP languages"""
                    if n_clicks and n_clicks % 2 == 1:
                        return [
                            html.Span("EN", className="navbar__lang-option"),
                            html.Span(" | ", className="navbar__lang-separator"),
                            html.Span("JP", className="navbar__lang-option navbar__lang-active"),
                        ]
                    else:
                        return [
                            html.Span("EN", className="navbar__lang-option navbar__lang-active"),
                            html.Span(" | ", className="navbar__lang-separator"),
                            html.Span("JP", className="navbar__lang-option"),
                        ]
            
            logger.info("Navbar callbacks registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register navbar callbacks: {e}")
            self._status["errors"].append(str(e))
            return False


# Plugin factory function
def create_plugin() -> NavbarPlugin:
    """Factory function to create navbar plugin instance"""
    return NavbarPlugin()


# Backward compatibility functions
def create_navbar_layout():
    """Backward compatibility function"""
    plugin = create_plugin()
    return plugin.create_navbar_layout()


def register_navbar_callbacks(app):
    """Backward compatibility function"""
    plugin = create_plugin()
    return plugin.register_callbacks(app, None)


# Export the plugin and compatibility functions
layout = create_navbar_layout
__all__ = ["NavbarPlugin", "create_plugin", "create_navbar_layout", "register_navbar_callbacks", "layout"]
