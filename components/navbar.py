# components/navbar.py - FIXED: Type-safe navbar
"""
Navigation bar component with complete type safety
"""

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input

try:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input
    DASH_AVAILABLE = True
except ImportError:
    print("Warning: Dash components not available")
    DASH_AVAILABLE = False
    # Create fallbacks
    dbc = None
    html = None
    dcc = None
    callback = None
    Output = None
    Input = None

def create_navbar_layout():
    """Create navbar layout with fallback"""
    if not DASH_AVAILABLE:
        return None
    
    try:
        return dbc.Navbar([
            dbc.Container([
                # Logo
                dbc.Row([
                    dbc.Col([
                        html.Img(
                            src="/assets/yosai_logo_name_white.png", 
                            height="40px",
                            className="navbar__logo"
                        )
                    ], width="auto")
                ], align="center"),
                
                # Center content
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Main Panel", className="navbar__title text-primary"),
                            html.Small("Logged in as: HQ Tower - East Wing", className="navbar__subtitle text-secondary"),
                            html.Small(id="live-time", className="navbar__subtitle text-tertiary")
                        ], className="text-center")
                    ])
                ], align="center", className="flex-grow-1"),
                
                # Navigation links
                dbc.Row([
                    dbc.Col([
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Dashboard", href="/", className="nav-link", active="exact")),
                            dbc.NavItem(dbc.NavLink("Deep Analytics", href="/analytics", className="nav-link", active="exact")),
                            dbc.NavItem(dbc.NavLink("Export Log", href="#", className="nav-link")),
                            dbc.NavItem(dbc.NavLink("Settings", href="#", className="nav-link")),
                        ], navbar=True, className="navbar__nav")
                    ])
                ], align="center")
            ], fluid=True, className="navbar__container")
        ], color="dark", dark=True, className="navbar")
    except Exception as e:
        print(f"Error creating navbar: {e}")
        return html.Div("Navigation not available")

# Create the layout
layout = create_navbar_layout()

# Safe callback registration
def register_navbar_callbacks(app):
    """Register navbar callbacks safely"""
    if not DASH_AVAILABLE:
        return
    
    try:
        @app.callback(
            Output("live-time", "children"),
            Input("live-time", "id"),
            prevent_initial_call=False
        )
        def update_time(_):
            try:
                return f"Live Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            except Exception:
                return "Time unavailable"
    except Exception as e:
        print(f"Error registering navbar callbacks: {e}")
