# yosai_intel_dashboard/components/map_panel.py

import dash_leaflet as dl  # type: ignore
import dash_leaflet.express as dlx  # type: ignore
from dash import html
import dash_bootstrap_components as dbc

# Example markers
example_markers = [
    dl.Marker(position=[35.6895, 139.6917], children=[  # type: ignore
        dl.Tooltip("Tokyo HQ"),
        dl.Popup("Main Entrance - Last access: OK")
    ]),
    dl.CircleMarker(center=[35.6895, 139.6920], radius=15, color="red", fillOpacity=0.7,  # type: ignore
                    children=[dl.Tooltip("Unauthorized Access")])
]

# Map view toggle icons — placeholders
view_toggle = html.Div([
    html.Div([
        html.Img(src="/assets/main_icon_globe.png", title="Global View", className="map-toggle-icon"),
        html.Img(src="/assets/main_icon_facilities..png", title="City View", className="map-toggle-icon"),
        html.Img(src="/assets/main_icon_site.png", title="Site View", className="map-toggle-icon"),
        html.Img(src="/assets/main_icon_onion.png", title="Onion View", className="map-toggle-icon")
    ], className="view-toggle-stack")
], className="view-toggle-container")

layout = html.Div([
    dl.Map(center=[35.6895, 139.6917], zoom=16, children=[  # type: ignore
        dl.TileLayer(),
        *example_markers
    ], style={'width': '100%', 'height': '50vh'}, id="facility-map"),

    view_toggle  # Floating button stack
], className="map-panel")
