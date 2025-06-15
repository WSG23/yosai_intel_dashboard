# pyright: reportArgumentType=false

# yosai_intel_dashboard/components/map_panel.py

import dash_leaflet as dl
from dash import html

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
    dl.Map(
        id="facility-map",
        center=[35.6895, 139.6917],  # type: ignore
        zoom=15,
        children=[
            dl.TileLayer(),
            dl.Marker(position=[35.6895, 139.6917], children=[
                dl.Tooltip("Tokyo HQ"),
                dl.Popup("Main Entrance - Last access: OK")
            ])
        ],
        style={'width': '100%', 'height': '100%'}
    ),
    view_toggle
], className="map-panel", style={'width': '100%', 'height': '100%', 'backgroundColor': '#121212'})

