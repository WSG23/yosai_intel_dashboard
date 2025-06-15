# pyright: reportArgumentType=false

# yosai_intel_dashboard/components/map_panel.py

import dash_leaflet as dl
from dash import html, dcc, Output, Input, callback_context

# Predefined map centers for each view
view_centers = {
    'global': [0, 0],
    'city': [35.68, 139.69],
    'site': [35.6895, 139.6917],
    'onion': [35.6897, 139.6919]
}

# Map layout with forced height for visibility
layout = html.Div([
    dcc.Store(id='map-center-store', data=view_centers['site']),
    dl.Map(
        id="facility-map",
        center=view_centers['site'],
        zoom=15,
        children=[
            dl.TileLayer(),
            dl.Marker(position=view_centers['site'], children=[
                dl.Tooltip("Tokyo HQ"),
                dl.Popup("Main Entrance - Last access: OK")
            ])
        ],
        style={'width': '100%', 'height': '100%'}  # <-- Force fixed height for visibility
    ),
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
