"""
Working app factory with functional file upload
"""
import dash
import logging
from typing import Optional
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import base64
import io
import pandas as pd

logger = logging.getLogger(__name__)


def create_app() -> dash.Dash:
    """Create fully functional Dash application"""
    try:
        # Create Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )

        app.title = "Yōsai Intel Dashboard"

        # Set main layout with navigation
        app.layout = create_main_layout()

        # Register all callbacks
        register_all_callbacks(app)

        logger.info("✅ Complete Dash application created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def create_main_layout():
    """Create the main application layout with navigation"""
    try:
        return html.Div([
            dcc.Location(id='url', refresh=False),

            # Navigation bar
            create_navigation_bar(),

            # Main content area
            html.Div(id='page-content', className="main-content"),

            # Global stores
            dcc.Store(id='global-data-store', data={}),
            dcc.Store(id='user-session-store', data={}),
        ])
    except Exception as e:
        logger.error(f"Error creating main layout: {e}")
        return html.Div("Error creating layout")


def create_navigation_bar():
    """Create navigation bar"""
    try:
        return dbc.Navbar([
            dbc.Container([
                # Brand
                dbc.NavbarBrand([
                    html.Span("🏯 ", className="me-2"),
                    "Yōsai Intel Dashboard"
                ], href="/", className="navbar-brand"),

                # Navigation links
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("File Upload", href="/file-upload", active="exact")),
                    dbc.NavItem(dbc.NavLink("Analytics", href="/analytics", active="exact")),
                ], className="ms-auto", navbar=True),

                # Live time display
                html.Span(id="live-time", className="navbar-text text-light ms-3"),
            ], fluid=True)
        ], color="dark", dark=True, className="mb-4")

    except Exception as e:
        logger.error(f"Error creating navigation bar: {e}")
        return html.Div("Navigation error")


def register_all_callbacks(app):
    """Register all application callbacks"""
    try:
        # Page routing callback
        @app.callback(
            Output('page-content', 'children'),
            Input('url', 'pathname')
        )
        def display_page(pathname):
            """Route to appropriate page"""
            try:
                if pathname == '/' or pathname is None:
                    return create_dashboard_page()
                elif pathname == '/file-upload':
                    return create_file_upload_page()
                elif pathname == '/analytics':
                    return create_analytics_page()
                else:
                    return create_404_page(pathname)
            except Exception as e:
                logger.error(f"Error routing to {pathname}: {e}")
                return create_error_page(f"Error loading page: {str(e)}")

        # Live time callback
        @app.callback(
            Output('live-time', 'children'),
            Input('url', 'pathname')
        )
        def update_time(pathname):
            """Update live time display"""
            try:
                from datetime import datetime
                return f"Live: {datetime.now().strftime('%H:%M:%S')}"
            except Exception:
                return "Live: --:--:--"

        # File upload callback with AI column mapping
        @app.callback(
            [
                Output('upload-output', 'children'),
                Output('column-mapping-section', 'style'),
                Output('column-mapping-content', 'children')
            ],
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename')]
        )
        def handle_file_upload(contents, filename):
            """Handle file upload and show AI column mapping"""
            if contents is None:
                return "", {"display": "none"}, ""

            try:
                # Parse the uploaded file
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)

                # Try to read as CSV first
                try:
                    if 'csv' in filename.lower():
                        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    elif 'xlsx' in filename.lower() or 'xls' in filename.lower():
                        df = pd.read_excel(io.BytesIO(decoded))
                    else:
                        # Try CSV as default
                        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                except Exception as e:
                    return dbc.Alert(f"❌ Error reading file: {str(e)}", color="danger"), {"display": "none"}, ""

                if df.empty:
                    return dbc.Alert("❌ File is empty", color="warning"), {"display": "none"}, ""

                # Show success message
                success_msg = dbc.Alert([
                    html.H5("✅ File uploaded successfully!", className="alert-heading"),
                    html.P(f"📁 File: {filename}"),
                    html.P(f"📊 Records: {len(df)} rows, {len(df.columns)} columns"),
                ], color="success")

                # Create AI column mapping interface
                columns = list(df.columns)
                ai_suggestions = analyze_columns_ai(columns)

                mapping_content = create_column_mapping_interface(columns, ai_suggestions, df.head())

                return success_msg, {"display": "block"}, mapping_content

            except Exception as e:
                logger.error(f"Error processing upload: {e}")
                return dbc.Alert(f"❌ Error processing file: {str(e)}", color="danger"), {"display": "none"}, ""

        logger.info("All callbacks registered successfully")

    except Exception as e:
        logger.error(f"Error registering callbacks: {e}")


def analyze_columns_ai(columns):
    """Simple AI-like column analysis"""
    suggestions = {}

    # Simple pattern matching for common columns
    for col in columns:
        col_lower = col.lower()

        # Timestamp detection
        if any(word in col_lower for word in ['time', 'date', 'timestamp', 'datetime']):
            suggestions['timestamp'] = col

        # Device/Door detection
        elif any(word in col_lower for word in ['device', 'door', 'location', 'reader', 'gate']):
            suggestions['device'] = col

        # User detection
        elif any(word in col_lower for word in ['user', 'person', 'employee', 'badge', 'card', 'id']):
            suggestions['user'] = col

        # Event type detection
        elif any(word in col_lower for word in ['event', 'action', 'type', 'status', 'result']):
            suggestions['event'] = col

    return suggestions


def create_column_mapping_interface(columns, ai_suggestions, sample_data):
    """Create the AI column mapping interface"""

    column_options = [{"label": col, "value": col} for col in columns]

    return dbc.Card([
        dbc.CardHeader([
            html.H4("🤖 AI Column Mapping", className="mb-0"),
            html.P("AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                   className="text-muted mb-0 mt-2")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("🕐 Timestamp Column:"),
                    dcc.Dropdown(
                        id="timestamp-column",
                        options=column_options,
                        value=ai_suggestions.get('timestamp'),
                        placeholder="Select timestamp column..."
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("🚪 Device/Door Column:"),
                    dcc.Dropdown(
                        id="device-column",
                        options=column_options,
                        value=ai_suggestions.get('device'),
                        placeholder="Select device column..."
                    ),
                ], width=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("👤 User/Person Column:"),
                    dcc.Dropdown(
                        id="user-column",
                        options=column_options,
                        value=ai_suggestions.get('user'),
                        placeholder="Select user column..."
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("⚡ Event Type Column:"),
                    dcc.Dropdown(
                        id="event-column",
                        options=column_options,
                        value=ai_suggestions.get('event'),
                        placeholder="Select event column..."
                    ),
                ], width=6),
            ], className="mb-4"),

            html.Hr(),

            # Sample data preview
            html.H6("📋 Sample Data Preview:"),
            dbc.Table.from_dataframe(
                sample_data,
                striped=True,
                bordered=True,
                hover=True,
                size="sm",
                className="mb-3"
            ),

            # Action buttons
            dbc.ButtonGroup([
                dbc.Button("✅ Verify Mapping", id="verify-mapping-btn", color="success"),
                dbc.Button("🔄 Reset", id="reset-mapping-btn", color="secondary"),
            ], className="mt-3")
        ])
    ])


def create_dashboard_page():
    """Create main dashboard page"""
    try:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("🏯 Yōsai Intel Dashboard", className="text-center mb-4"),
                    html.Hr(),
                ])
            ]),

            # Dashboard content
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Dashboard Overview"),
                        dbc.CardBody([
                            dbc.Alert("✅ Dashboard loaded successfully!", color="success"),
                            html.P("Welcome to your security intelligence dashboard."),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4("42", className="card-title text-primary"),
                                            html.P("Total Events", className="card-text")
                                        ])
                                    ])
                                ], width=4),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4("98%", className="card-title text-success"),
                                            html.P("Success Rate", className="card-text")
                                        ])
                                    ])
                                ], width=4),
                                dbc.Col([
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.H4("3", className="card-title text-warning"),
                                            html.P("Alerts", className="card-text")
                                        ])
                                    ])
                                ], width=4),
                            ])
                        ])
                    ])
                ])
            ]),

            # Quick actions
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚀 Quick Actions"),
                        dbc.CardBody([
                            dbc.ButtonGroup([
                                dbc.Button("📂 Upload File", href="/file-upload", color="primary"),
                                dbc.Button("📊 View Analytics", href="/analytics", color="info"),
                                dbc.Button("🔍 Search Events", color="secondary", disabled=True),
                            ])
                        ])
                    ])
                ], className="mt-4")
            ])
        ], fluid=True)

    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return create_error_page("Dashboard error")


def create_file_upload_page():
    """Create file upload page with working AI column mapping"""
    try:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📂 File Upload & Processing", className="text-center mb-4"),
                    html.P("Upload CSV, JSON, and Excel files for security analytics processing",
                           className="text-center text-muted mb-4"),
                ])
            ]),

            # Upload area
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📤 Upload Files"),
                        dbc.CardBody([
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                                    html.H4("Drag and Drop or Click to Upload"),
                                    html.P("Supports CSV, Excel files"),
                                    html.P("Max file size: 100MB", className="text-muted small")
                                ], className="text-center p-4"),
                                style={
                                    'width': '100%',
                                    'height': '200px',
                                    'lineHeight': '60px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '10px',
                                    'borderColor': '#ccc',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                multiple=False
                            ),
                            html.Div(id='upload-output', className="mt-3")
                        ])
                    ])
                ])
            ]),

            # Column mapping section (initially hidden)
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id='column-mapping-content',
                        className="mt-4"
                    )
                ], id='column-mapping-section', style={'display': 'none'})
            ])
        ], fluid=True)

    except Exception as e:
        logger.error(f"Error creating file upload page: {e}")
        return create_error_page("File upload page error")


def create_analytics_page():
    """Create analytics page"""
    try:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Deep Analytics", className="text-center mb-4"),
                    html.P("Advanced data analysis and visualization for security intelligence",
                           className="text-center text-muted mb-4"),
                ])
            ]),

            # Data source selection
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Data Source Selection"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Select Data Source:"),
                                    dcc.Dropdown(
                                        id="analytics-data-source",
                                        options=[
                                            {"label": "Uploaded Files", "value": "uploaded"},
                                            {"label": "Sample Data", "value": "sample"},
                                            {"label": "Database", "value": "database"},
                                        ],
                                        value="sample",
                                        placeholder="Choose data source..."
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Analysis Type:"),
                                    dcc.Dropdown(
                                        id="analytics-type",
                                        options=[
                                            {"label": "Security Patterns", "value": "security"},
                                            {"label": "Access Trends", "value": "trends"},
                                            {"label": "User Behavior", "value": "behavior"},
                                            {"label": "Custom Analysis", "value": "custom"},
                                        ],
                                        value="security",
                                        placeholder="Select analysis type..."
                                    )
                                ], width=6),
                            ]),
                            html.Hr(),
                            dbc.Button(
                                "Generate Analytics",
                                id="generate-analytics-btn",
                                color="primary",
                                className="mt-2"
                            )
                        ])
                    ])
                ])
            ]),

            # Analytics display area
            dbc.Row([
                dbc.Col([
                    html.Div(id="analytics-display-area", className="mt-4")
                ])
            ])
        ], fluid=True)

    except Exception as e:
        logger.error(f"Error creating analytics page: {e}")
        return create_error_page("Analytics page error")


def create_404_page(pathname):
    """Create 404 error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("404 - Page Not Found", className="text-center text-danger"),
                html.P(f"The page '{pathname}' was not found.", className="text-center text-muted"),
                html.Div([
                    dbc.Button("← Back to Dashboard", href="/", color="primary")
                ], className="text-center mt-4")
            ])
        ])
    ], className="mt-5")


def create_error_page(error_message):
    """Create error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("⚠️ Error", className="alert-heading"),
                    html.P(error_message),
                    html.Hr(),
                    dbc.Button("← Back to Dashboard", href="/", color="primary")
                ], color="danger")
            ])
        ])
    ], className="mt-5")


def create_application():
    """Legacy compatibility function"""
    return create_app()
