# components/navbar.py - Updated with new CSS classes
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input
import datetime

# Updated navbar with new CSS classes
layout = dbc.Navbar([
    dbc.Container([
        # Left side - Logo  
        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/yosai_logo_name_white.png", 
                    height="40px",
                    className="navbar__logo"  # ← NEW CSS CLASS
                )
            ], width="auto")
        ], align="center"),
        
        # Center - Current page info
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Main Panel", className="navbar__title text-primary"),  # ← NEW CLASSES
                    html.Small("Logged in as: HQ Tower - East Wing", className="navbar__subtitle text-secondary"),  # ← NEW CLASSES
                    html.Small(id="live-time", className="navbar__subtitle text-tertiary")  # ← NEW CLASSES
                ], className="text-center")
            ])
        ], align="center", className="flex-grow-1"),
        
        # Right side - Navigation links
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/", className="nav-link", active="exact")),  # ← NEW CLASS
                    dbc.NavItem(dbc.NavLink("Deep Analytics", href="/analytics", className="nav-link", active="exact")),  # ← NEW CLASS
                    dbc.NavItem(dbc.NavLink("Export Log", href="#", className="nav-link")),  # ← NEW CLASS
                    dbc.NavItem(dbc.NavLink("Executive Report", href="#", className="nav-link")),  # ← NEW CLASS
                    dbc.NavItem(dbc.NavLink("Settings", href="#", className="nav-link")),  # ← NEW CLASS
                    dbc.NavItem(dbc.NavLink("Logoff", href="#", className="nav-link"))  # ← NEW CLASS
                ], navbar=True, className="navbar__nav")  # ← NEW CLASS
            ])
        ], align="center")
    ], fluid=True, className="navbar__container")  # ← NEW CLASS
], color="dark", dark=True, className="navbar")  # ← UPDATED CLASS

# CALLBACK: Updated with error handling
@callback(
    Output("live-time", "children"),
    Input("live-time", "id"),
    prevent_initial_call=False  # ← IMPORTANT: Prevents callback errors
)
def update_time(_):
    """Update live time display"""
    try:
        return f"Live Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return "Time unavailable"

# CLASS MAPPING REFERENCE:
# OLD CLASS → NEW CLASS
# .navbar-brand → .navbar__logo
# .mb-0 text-white → .navbar__title text-primary  
# .text-light → .navbar__subtitle text-secondary
# .ms-auto → .navbar__nav
# Standard Bootstrap → .nav-link