# pages/login.py
"""Login page component"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Output, Input, State
from core.plugins.decorators import safe_callback


def layout():
    """Create login page layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Img(
                                src="/assets/yosai_logo_name_white.png",
                                height="60px",
                                className="mb-4"
                            ),
                            html.H3("Yōsai Intel Dashboard", className="text-center mb-4 text-primary"),
                            dbc.Form([
                                dbc.InputGroup([
                                    dbc.InputGroupText("👤"),
                                    dbc.Input(
                                        id="username-input",
                                        placeholder="Username",
                                        type="text",
                                        className="form-control"
                                    )
                                ], className="mb-3"),
                                dbc.InputGroup([
                                    dbc.InputGroupText("🔒"),
                                    dbc.Input(
                                        id="password-input",
                                        placeholder="Password",
                                        type="password",
                                        className="form-control"
                                    )
                                ], className="mb-3"),
                                dbc.Button(
                                    "Login",
                                    id="login-button",
                                    color="primary",
                                    className="w-100 mb-3"
                                ),
                                html.Div(id="login-status", className="text-center")
                            ])
                        ], className="text-center")
                    ])
                ], className="shadow")
            ], width=4)
        ], justify="center", className="min-vh-100 align-items-center")
    ], fluid=True, className="bg-dark")


@safe_callback
def register_login_callbacks(app):
    """Register login page callbacks"""
    @app.callback(
        Output("login-status", "children"),
        Input("login-button", "n_clicks"),
        State("username-input", "value"),
        State("password-input", "value"),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        if n_clicks and username and password:
            # Simple validation - replace with real authentication
            if username and password:
                return dcc.Location(pathname="/", id="redirect")
            else:
                return dbc.Alert("Invalid credentials", color="danger")
        return ""
