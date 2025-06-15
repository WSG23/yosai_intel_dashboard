# app.py - Updated version
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input

# Import your existing components
from components import navbar, incident_alerts_panel, map_panel, bottom_panel, weak_signal_panel

# Initialize the Dash app with pages support
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    use_pages=True  # Enable multi-page support
)

server = app.server

# Main dashboard page layout (your existing dashboard)
def dashboard_layout():
    return html.Div([
        navbar.layout,
        html.Div([
            html.Div(incident_alerts_panel.layout, className='left-panel'),
            html.Div(map_panel.layout, className='map-panel'),
            html.Div(weak_signal_panel.layout, className='right-panel'),
        ], className='main-content'),
        html.Div(bottom_panel.layout, className='bottom-panel')
    ])

# Register the main dashboard as the index page
dash.register_page(
    "dashboard", 
    path="/", 
    title="Yōsai Intel Dashboard",
    layout=dashboard_layout
)

# App layout with page container
app.layout = html.Div([
    dcc.Location(id='url'),
    
    # Page content will be rendered here
    dash.page_container
])

# Optional: Add callback for any global app functionality
@app.callback(
    Output('url', 'pathname'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def update_page(pathname):
    """Handle page navigation if needed"""
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)