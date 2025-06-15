# components/navbar.py - Updated version
import dash_bootstrap_components as dbc
from dash import html, dcc

# Your existing navbar with added analytics link
layout = dbc.Navbar([
    dbc.Container([
        # Left side - Logo
        dbc.Row([
            dbc.Col([
                html.Img(
                    src="/assets/yosai_logo_name_white.png", 
                    height="40px",
                    className="navbar-brand"
                )
            ], width="auto")
        ], align="center"),
        
        # Center - Current page info
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Main Panel", className="mb-0 text-white"),
                    html.Small("Logged in as: HQ Tower - East Wing", className="text-light"),
                    html.Small(id="live-time", className="text-light d-block")
                ], className="text-center")
            ])
        ], align="center", className="flex-grow-1"),
        
        # Right side - Navigation links
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Deep Analytics", href="/analytics", active="exact")),
                    dbc.NavItem(dbc.NavLink("Export Log", href="#", className="text-light")),
                    dbc.NavItem(dbc.NavLink("Executive Report", href="#", className="text-light")),
                    dbc.NavItem(dbc.NavLink("Settings", href="#", className="text-light")),
                    dbc.NavItem(dbc.NavLink("Logoff", href="#", className="text-light"))
                ], navbar=True, className="ms-auto")
            ])
        ], align="center")
    ], fluid=True)
], color="dark", dark=True, className="mb-4")

# Optional: Add callback for live time update
from dash import callback, Output, Input
import datetime

@callback(
    Output("live-time", "children"),
    Input("live-time", "id")  # Dummy input to trigger initial load
)
def update_time(_):
    return f"Live Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"