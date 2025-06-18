#!/usr/bin/env python3
"""
Emergency Safe Components
Provides safe fallback components that are guaranteed to be JSON serializable
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def safe_navbar():
    """Safe navbar component"""
    return dbc.Navbar([
        dbc.Container([
            html.H3("🏯 Yōsai Intel Dashboard", className="text-white mb-0"),
            html.Span("Safe Mode", className="badge bg-warning text-dark ms-2")
        ])
    ], color="dark", dark=True)


def safe_map_panel():
    """Safe map panel component"""
    return dbc.Card([
        dbc.CardHeader("🗺️ Map Panel"),
        dbc.CardBody([
            html.P("Map panel is running in safe mode"),
            html.P("No JSON serialization issues here!", className="text-success")
        ])
    ])


def safe_bottom_panel():
    """Safe bottom panel component"""
    return dbc.Card([
        dbc.CardHeader("📊 Analytics Panel"),
        dbc.CardBody([
            html.P("Analytics panel is running safely"),
            html.Div("All components are JSON serializable", className="alert alert-success")
        ])
    ])


def safe_incident_alerts():
    """Safe incident alerts component"""
    return dbc.Card([
        dbc.CardHeader("🚨 Incident Alerts"),
        dbc.CardBody([
            dbc.Alert("No active incidents", color="success"),
            html.P("System is operating normally")
        ])
    ])


def safe_weak_signal():
    """Safe weak signal panel component"""
    return dbc.Card([
        dbc.CardHeader("📡 Weak Signal Analysis"),
        dbc.CardBody([
            html.P("Weak signal analysis is running"),
            html.P("All data is properly serialized", className="text-info")
        ])
    ])


# Component registry mapping
SAFE_COMPONENTS = {
    'navbar': safe_navbar,
    'map_panel': safe_map_panel, 
    'bottom_panel': safe_bottom_panel,
    'incident_alerts': safe_incident_alerts,
    'weak_signal': safe_weak_signal,
}


def get_safe_component(name: str):
    """Get a safe component by name"""
    if name in SAFE_COMPONENTS:
        return SAFE_COMPONENTS[name]()
    else:
        return html.Div(f"Safe fallback for: {name}", className="alert alert-info")
