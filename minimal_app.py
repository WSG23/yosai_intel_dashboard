# Create: minimal_app.py (for testing)
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# Minimal app to test CSS
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "/assets/css/main.css"
    ]
)

app.layout = html.Div([
    html.H1("CSS Test", className="text-primary"),
    html.Button("Test Button", className="btn btn--primary"),
    html.Div("Test Chip", className="chip chip--success")
])

if __name__ == '__main__':
    app.run(debug=True)
    