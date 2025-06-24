#!/usr/bin/env python3
"""
Streamlined App Factory - Single responsibility for creating Dash applications
Replaces: core/app_factory.py, core/layout_manager.py, core/callback_manager.py
"""
import dash
import logging
from typing import Optional, Any
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

logger = logging.getLogger(__name__)


def create_app() -> dash.Dash:
    """Create Dash application with clean architecture"""
    try:
        # Create Dash app with external stylesheets
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
            assets_folder='assets'
        )
        
        app.title = "Yōsai Intel Dashboard"
        
        # Set main layout
        app.layout = _create_main_layout()
        
        # Register callbacks
        _register_callbacks(app)
        
        logger.info("✅ Dash application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def _create_main_layout() -> html.Div:
    """Create main application layout"""
    return html.Div([
        # URL routing component
        dcc.Location(id='url', refresh=False),
        
        # Navigation bar
        _create_navbar(),
        
        # Main content area (dynamically populated)
        html.Div(id='page-content', className="main-content p-4"),
        
        # Global data stores
        dcc.Store(id='global-store', data={}),
        dcc.Store(id='session-store', data={}),
    ])


def _create_navbar() -> dbc.Navbar:
    """Create navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            # Brand
            dbc.NavbarBrand([
                html.I(className="fas fa-shield-alt me-2"),
                "Yōsai Intel Dashboard"
            ], href="/", className="text-primary fw-bold"),
            
            # Navigation links
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                dbc.NavItem(dbc.NavLink("Analytics", href="/analytics", active="exact")),
                dbc.NavItem(dbc.NavLink("Upload", href="/upload", active="exact")),
            ], className="ms-auto", navbar=True),
            
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4"
    )


def _register_callbacks(app: dash.Dash) -> None:
    """Register all application callbacks"""
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
        prevent_initial_call=False
    )
    def display_page(pathname: Optional[str]) -> Any:
        """Route to appropriate page based on URL"""
        try:
            # Default to dashboard
            if pathname == "/" or pathname is None:
                return _create_dashboard_page()
            
            elif pathname == "/analytics":
                return _create_analytics_page()
            
            elif pathname == "/upload":
                return _create_upload_page()
            
            else:
                return _create_404_page(pathname)
                
        except Exception as e:
            logger.error(f"Error routing to {pathname}: {e}")
            return _create_error_page(f"Error loading page: {str(e)}")


def _create_dashboard_page() -> dbc.Container:
    """Create main dashboard page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🏯 Dashboard", className="text-primary mb-4"),
                dbc.Alert("✅ Dashboard loaded successfully!", color="success"),
                
                # Dashboard metrics
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("156", className="text-primary mb-0"),
                                html.P("Active Events", className="text-muted mb-0")
                            ])
                        ])
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("23", className="text-warning mb-0"),
                                html.P("Pending Alerts", className="text-muted mb-0")
                            ])
                        ])
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("8", className="text-danger mb-0"),
                                html.P("Critical Issues", className="text-muted mb-0")
                            ])
                        ])
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("99.7%", className="text-success mb-0"),
                                html.P("System Health", className="text-muted mb-0")
                            ])
                        ])
                    ], width=3),
                ], className="mb-4"),
                
                # Quick actions
                dbc.Card([
                    dbc.CardHeader("Quick Actions"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button("📊 View Analytics", href="/analytics", color="primary"),
                            dbc.Button("📁 Upload Data", href="/upload", color="secondary"),
                            dbc.Button("⚙️ Settings", color="outline-secondary"),
                        ])
                    ])
                ])
            ])
        ])
    ], fluid=True)


def _create_analytics_page() -> Any:
    """Create analytics page - imports from pages module"""
    try:
        from pages.deep_analytics import layout
        return layout()
    except ImportError:
        return _create_placeholder_page(
            "📊 Analytics", 
            "Analytics page is being loaded...",
            "The deep analytics module is not available."
        )


def _create_upload_page() -> dbc.Container:
    """Create file upload page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("📁 File Upload", className="text-primary mb-4"),
                
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Upload Data Files", className="mb-3"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                                html.H6("Drag and Drop or Click to Select Files"),
                                html.P("Supports CSV, Excel, JSON files", 
                                      className="text-muted")
                            ], className="text-center p-4"),
                            style={
                                'width': '100%',
                                'border': '2px dashed #ddd',
                                'borderRadius': '8px',
                                'textAlign': 'center',
                                'cursor': 'pointer'
                            },
                            multiple=True
                        ),
                        
                        html.Div(id='upload-output', className="mt-3")
                    ])
                ])
            ])
        ])
    ], fluid=True)


def _create_placeholder_page(title: str, subtitle: str, message: str) -> dbc.Container:
    """Create placeholder page for missing components"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(title, className="text-primary mb-2"),
                html.P(subtitle, className="text-muted mb-4"),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    message
                ], color="info"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        ])
    ], fluid=True)


def _create_404_page(pathname: str) -> dbc.Container:
    """Create 404 error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("404 - Page Not Found", className="text-danger mb-4"),
                html.P(f"The page '{pathname}' was not found.", className="mb-4"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        ])
    ], fluid=True)


def _create_error_page(error_message: str) -> dbc.Container:
    """Create error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("⚠️ Error", className="text-danger mb-4"),
                dbc.Alert([
                    html.P(error_message, className="mb-0")
                ], color="danger"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        ])
    ], fluid=True)


# Export main function
__all__ = ['create_app']
