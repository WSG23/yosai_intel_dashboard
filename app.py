# yosai_intel_dashboard/app.py

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
from components import map_panel

from components import navbar, incident_alerts_panel, map_panel, bottom_panel, weak_signal_panel

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Register component-specific callbacks
map_panel.register_callbacks(app)

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(navbar.layout, className='top-panel'),
    html.Div([
        html.Div(incident_alerts_panel.layout, className='left-panel'),
        html.Div(map_panel.layout, className='map-panel'),
        html.Div(weak_signal_panel.layout, className='right-panel')
    ], className='main-content'),
    html.Div(bottom_panel.layout, className='bottom-panel')
])
print(map_panel.layout)

if __name__ == '__main__':
    app.run(debug=True)
