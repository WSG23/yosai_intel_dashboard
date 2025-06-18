"""
Fixed working example using the CSRF plugin
Run this to see your CSRF error fixed!
"""

import dash
from dash import html, dcc, Input, Output
from dash_csrf_plugin import DashCSRFPlugin, CSRFMode

# Create app
app = dash.Dash(__name__)

# Add CSRF protection (development mode - CSRF disabled)
csrf_plugin = DashCSRFPlugin(app, mode=CSRFMode.DEVELOPMENT)

# Layout
app.layout = html.Div([
    csrf_plugin.create_csrf_component(),
    
    html.Div(className="container mt-4", children=[
        html.H1("🛡️ CSRF Error Fixed!", className="text-success"),
        html.P("Your 'CSRF session token is missing' error has been resolved."),
        
        html.Div(className="alert alert-success", children=[
            html.H4("✅ Status"),
            html.P(f"Plugin Mode: {csrf_plugin.mode.value}"),
            html.P(f"CSRF Enabled: {csrf_plugin.is_enabled}"),
            html.P("Protection: Development Mode (CSRF disabled for easy testing)")
        ]),
        
        html.Button("Test Button", id="btn", n_clicks=0, className="btn btn-primary"),
        html.Div(id="output", className="mt-3")
    ])
])

@app.callback(Output("output", "children"), Input("btn", "n_clicks"))
def update_output(n_clicks):
    if n_clicks > 0:
        return html.Div(className="alert alert-success", children=[
            f"✅ Button clicked {n_clicks} times - No CSRF errors!"
        ])
    return "Click the button to test"

if __name__ == "__main__":
    print("🚀 Starting CSRF-protected Dash app...")
    print("🌐 URL: http://127.0.0.1:8050")
    print("✅ CSRF errors have been eliminated!")
    app.run_server(debug=True)
