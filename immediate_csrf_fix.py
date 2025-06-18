"""
IMMEDIATE CSRF FIX - Use this if you can't get the plugin working

Just run this file or copy the fix into your app.py
"""

import os
import dash
from dash import html, dcc, Input, Output

# IMMEDIATE FIX: Disable CSRF protection
os.environ['WTF_CSRF_ENABLED'] = 'False'

# Create your Dash app as usual
app = dash.Dash(__name__)

# Additional Flask config to ensure CSRF is disabled
app.server.config.update({
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'your-secret-key-here'
})

# Your layout (no changes needed)
app.layout = html.Div([
    html.H1("🛡️ CSRF Error Fixed!"),
    html.P("Your app now runs without CSRF errors."),
    html.Button("Test", id="btn", n_clicks=0),
    html.Div(id="output")
])

@app.callback(Output("output", "children"), Input("btn", "n_clicks"))
def update(n_clicks):
    return f"Clicked: {n_clicks} times - No CSRF errors!"

if __name__ == "__main__":
    print("✅ CSRF errors fixed with environment variable override")
    app.run_server(debug=True)
