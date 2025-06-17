# pyright: reportArgumentType=false

import dash
import dash_leaflet as dl
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    dl.Map(
        center=[35.6895, 139.6917],  # type: ignore
        zoom=15,
        children=[
            dl.TileLayer(),
            dl.Marker(position=[35.6895, 139.6917], children=[  # type: ignore
                dl.Tooltip("Tokyo HQ"),
                dl.Popup("Main Entrance - Last access: OK")
            ])
        ],
        style={'width': '100%', 'height': '100vh'},
        id="test-map"
    )
])

if __name__ == "__main__":
    app.run(debug=True)
