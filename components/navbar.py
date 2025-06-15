# yosai_intel_dashboard/components/navbar.py

import dash_bootstrap_components as dbc
from dash import html, dcc

layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Img(src="/assets/yosai_logo_name_white.png", height="40px"), width="auto"),
                dbc.Col(html.Div([
                    html.Div("Main Panel", className="navbar-title"),
                    html.Div("Logged in as: Imperial Castles Security", className="navbar-subtitle"),
                    html.Div(id="topbar-live-time", className="navbar-subtitle")
                ]), width="auto")
            ], align="center", className="g-2"),

            dbc.Row([
                dbc.Col(dcc.Input(type="text", placeholder="Search...", className="form-control", id="topbar-search-box")),
                dbc.Col(html.Div("🛡️ Operator", className="user-role-badge")),
                dbc.Col(html.Div("🔔", id="notification-button")),
                dbc.Col(html.Div("🌙", id="theme-toggle-button")),
                dbc.Col(dbc.Button("Export Logs", color="primary", href="/export", className="mx-1")),
                dbc.Col(dbc.Button("Deep Analytics", color="primary", href="/analytics", className="mx-1")),
                dbc.Col(dbc.Button("Executive Report", color="primary", href="/report", className="mx-1")),
                dbc.Col(dbc.Button("Manage Locations", color="primary", href="/locations", className="mx-1")),
                dbc.Col(dbc.Button("Settings", color="secondary", href="/settings", className="mx-1")),
                dbc.Col(dbc.Button("Log Off", color="danger", href="/login", className="mx-1"))
            ], align="center", justify="end", className="g-1")
        ]),
        color="dark",
        dark=True,
        className="top-navigation-bar sticky-top"
    )
])
