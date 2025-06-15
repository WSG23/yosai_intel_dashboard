# pyright: reportArgumentType=false

# yosai_intel_dashboard/components/map_panel.py

import dash_leaflet as dl
from dash_leaflet import Marker, TileLayer, Tooltip, Popup, ScaleControl, ZoomControl, Icon
from dash import html, dcc, Output, Input, callback_context

# Predefined map centers for each view
view_centers = {
    'global': [0, 0],
    'city': [35.68, 139.69],
    'site': [35.6895, 139.6917],
    'onion': [35.6897, 139.6919]
}

# Custom tile layer with light gray and low detail (CartoDB Positron)
tile_url = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
attribution = "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors &copy; <a href=\"https://carto.com/\">CARTO</a>"

# Map layout with enhancements
layout = html.Div([
    dcc.Store(id='map-center-store', data=view_centers['site']),
    dl.Map(
        id="facility-map",
        center=view_centers['site'],
        zoom=15,
        children=[
            TileLayer(url=tile_url, attribution=attribution),
            Marker(position=view_centers['site'], icon=Icon(iconUrl="/assets/main_icon_site.png", iconSize=[32, 32]), children=[
                Tooltip("Tokyo HQ"),
                Popup("Main Entrance - Last access: OK")
            ]),
            ScaleControl(position="bottomleft"),
            ZoomControl(position="topleft")
        ],
        style={
            'width': '100%',
            'height': '100%',
            'borderRadius': '12px',
            'boxShadow': '0 2px 12px rgba(0,0,0,0.3)',
            'overflow': 'hidden',
            'backgroundColor': '#121212'
        }
    ),
    html.Div("🟢 All systems operational", className="map-status-badge"),
    html.Div([
        html.Button("🌐", id="view-global", className="map-toggle-button"),
        html.Button("🏙️", id="view-city", className="map-toggle-button"),
        html.Button("🏢", id="view-site", className="map-toggle-button"),
        html.Button("🧅", id="view-onion", className="map-toggle-button")
    ], className="map-toggle-stack")
], className="map-panel", style={'width': '100%', 'height': '100%', 'backgroundColor': '#121212'})


# Register callbacks
def register_callbacks(app):
    @app.callback(
        Output("facility-map", "center"),
        [
            Input("view-global", "n_clicks"),
            Input("view-city", "n_clicks"),
            Input("view-site", "n_clicks"),
            Input("view-onion", "n_clicks")
        ]
    )
    def update_map_center(global_clicks, city_clicks, site_clicks, onion_clicks):
        ctx = callback_context
        if not ctx.triggered:
            return view_centers['site']
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return view_centers.get(button_id.split('-')[-1], view_centers['site'])
