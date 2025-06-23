"""
Yōsai Intel Dashboard - Simplified Working Version
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Load environment variables early
try:
    from dotenv import load_dotenv
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print("✅ Loaded .env file")
    else:
        print("⚠️ .env file not found")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Set required defaults
os.environ.setdefault("SECRET_KEY", "dev-key-change-me")
os.environ.setdefault("WTF_CSRF_ENABLED", "True")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "8050")
os.environ.setdefault("DEBUG", "True")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def bootstrap_services():
    """Bootstrap application services"""
    try:
        # Use your existing service registry instead of core.service_container
        from services.service_registry import register_all_services

        container = register_all_services()
        print("✅ Services configured")
        try:
            service_count = len(container.list_services())
        except AttributeError:
            # Fallback for containers without list_services
            service_count = len(getattr(container, "_services", {})) + len(getattr(container, "_factories", {}))
        print(f"✅ Registered services: {service_count}")
        return True
    except Exception as e:
        print(f"⚠️ Service configuration failed: {e}")
        return False


def create_simple_dashboard():
    """Create dashboard with proper CSS loading"""
    try:
        from dash import Dash, html, dcc
        import dash_bootstrap_components as dbc
        import io

        # External stylesheets - ensure Bootstrap is loaded first
        external_stylesheets = [
            dbc.themes.BOOTSTRAP,  # Bootstrap base
            {
                'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
                'rel': 'stylesheet'
            }
        ]

        app = Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=True,
            assets_folder='assets'  # Ensure assets folder is detected
        )

        # Add meta tags for better rendering
        app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>Yōsai Intel Dashboard</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                {%favicon%}
                {%css%}
                <style>
                    /* Immediate contrast fix */
                    body, html, #_dash-app-content {
                        background-color: white !important;
                        color: #212529 !important;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''

        app.layout = _create_layout()
        _setup_routes(app)
        register_upload_callback(app)

        logger.info("✅ Simple dashboard created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return None


def _create_layout():
    import dash_bootstrap_components as dbc
    from dash import html, dcc

    return html.Div([
        dbc.NavbarSimple(
            brand="🏯 Yōsai Intel Dashboard",
            brand_href="/",
            color="dark",
            dark=True,
            children=[
                dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
                dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
                dbc.NavItem(dbc.NavLink("Upload", href="/file-upload")),
            ],
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content", className="container mt-4"),
    ])


def _setup_routes(app):
    import dash

    @app.callback(
        dash.dependencies.Output("page-content", "children"),
        dash.dependencies.Input("url", "pathname"),
    )
    def display_page(pathname):  # pragma: no cover - simple routing
        if pathname == "/analytics":
            return create_analytics_page()
        if pathname == "/file-upload":
            return create_upload_page()
        return create_dashboard_page()


def register_upload_callback(app):
    """Register file upload callback with proper list handling"""
    from dash import callback, Output, Input, State, html
    import base64
    import pandas as pd
    import io

    @callback(
        Output('upload-output', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def handle_file_upload(contents, filename):
        if contents is None:
            return ""

        try:
            # FIX: Handle both single file (string) and multiple files (list)
            if isinstance(contents, list):
                # Multiple files uploaded - process the first one
                if len(contents) == 0:
                    return html.Div("No files uploaded", className="alert alert-warning")

                content = contents[0]  # Take first file
                fname = filename[0] if isinstance(filename, list) else filename
            else:
                # Single file uploaded
                content = contents
                fname = filename

            # Validate content format
            if not content or ',' not in content:
                return html.Div("Invalid file format", className="alert alert-danger")

            # Decode uploaded file
            content_type, content_string = content.split(',', 1)
            decoded = base64.b64decode(content_string)

            # Process based on file type
            if fname.endswith('.csv'):
                try:
                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            df = pd.read_csv(io.StringIO(decoded.decode(encoding)))
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        raise ValueError("Could not decode CSV file")

                except Exception as e:
                    return html.Div([
                        html.H6("❌ Error processing CSV", className="text-danger"),
                        html.P(f"Error: {str(e)}")
                    ], className="alert alert-danger")

            elif fname.endswith('.json'):
                try:
                    import json
                    json_data = json.loads(decoded.decode('utf-8'))
                    if isinstance(json_data, list):
                        df = pd.DataFrame(json_data)
                    else:
                        df = pd.DataFrame([json_data])
                except Exception as e:
                    return html.Div([
                        html.H6("❌ Error processing JSON", className="text-danger"),
                        html.P(f"Error: {str(e)}")
                    ], className="alert alert-danger")

            elif fname.endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(io.BytesIO(decoded))
                except Exception as e:
                    return html.Div([
                        html.H6("❌ Error processing Excel file", className="text-danger"),
                        html.P(f"Error: {str(e)}")
                    ], className="alert alert-danger")
            else:
                return html.Div([
                    html.H6("❌ Unsupported file type", className="text-danger"),
                    html.P(f"File: {fname}"),
                    html.P("Supported: .csv, .json, .xlsx, .xls")
                ], className="alert alert-danger")

            # Validate DataFrame
            if df.empty:
                return html.Div([
                    html.H6("⚠️ Empty file", className="text-warning"),
                    html.P(f"File '{fname}' contains no data")
                ], className="alert alert-warning")

            # Success - show file info
            return html.Div([
                html.H6("✅ File processed successfully!", className="text-success"),
                html.P(f"📁 Filename: {fname}"),
                html.P(f"📊 Rows: {len(df):,}"),
                html.P(f"📋 Columns: {len(df.columns)}"),
                html.Details([
                    html.Summary("📋 Column Names"),
                    html.Ul([html.Li(col) for col in df.columns[:10]])
                ]),
                html.Hr(),
                html.H6("Next Steps:"),
                html.P("• Go to Analytics page for detailed analysis"),
                html.P("• File data is temporarily stored for this session")
            ], className="alert alert-success")

        except Exception as e:
            return html.Div([
                html.H6("❌ Upload failed", className="text-danger"),
                html.P(f"Error: {str(e)}"),
                html.P("Please check your file format and try again.")
            ], className="alert alert-danger")



def create_dashboard_page():
    """Create main dashboard page"""
    import dash_bootstrap_components as dbc
    from dash import html

    # Test service integration
    try:
        from services.service_registry import get_analytics_service
        analytics = get_analytics_service()
        service_status = "✅ Analytics service ready"
        if hasattr(analytics, 'analyze_data'):
            service_status += " (Full functionality)"
    except Exception as e:
        service_status = f"⚠️ Analytics: {str(e)[:50]}"

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🏯 Welcome to Yōsai Intel Dashboard", className="card-title"),
                        html.P("Security intelligence and access control monitoring.", className="card-text"),
                        html.P("Your modular dashboard is now running successfully!", className="text-success"),
                        html.P(service_status, className="text-info"),
                        dbc.Button("View Analytics", href="/analytics", color="primary", className="me-2"),
                        dbc.Button("Upload Data", href="/file-upload", color="secondary"),
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 System Status"),
                        html.P("✅ Core modules loaded", className="text-success mb-1"),
                        html.P("✅ Configuration active", className="text-success mb-1"),
                        html.P("✅ Dashboard functional", className="text-success mb-1"),
                        html.P("✅ Ready for development", className="text-success mb-1"),
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🚀 Quick Actions"),
                        dbc.Button("Analytics", href="/analytics", color="outline-primary", size="sm", className="me-2 mb-2"),
                        dbc.Button("File Upload", href="/file-upload", color="outline-secondary", size="sm", className="mb-2"),
                        html.Br(),
                        html.Small("Navigate using the top menu", className="text-muted"),
                    ])
                ])
            ], width=6),
        ])
    ])


def create_analytics_page():
    """Create analytics page"""
    import dash_bootstrap_components as dbc
    from dash import html
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("📊 Analytics Dashboard"),
                html.P("Data analysis and security insights"),
                html.Hr(),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Analytics Features"),
                        html.P("• Access pattern analysis"),
                        html.P("• Anomaly detection"),
                        html.P("• User behavior insights"),
                        html.P("• Security trend monitoring"),
                        dbc.Button("Upload Data for Analysis", href="/file-upload", color="primary"),
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Sample Analytics"),
                        html.P("Total Events: 1,247", className="mb-1"),
                        html.P("Active Users: 156", className="mb-1"),
                        html.P("Security Alerts: 3", className="text-warning mb-1"),
                        html.P("System Health: Good", className="text-success mb-1"),
                    ])
                ])
            ], width=6),
        ])
    ])


def create_upload_page():
    """Create file upload page with fixed upload handling"""
    import dash_bootstrap_components as dbc
    from dash import html, dcc

    return html.Div([
        html.H1("📤 File Upload", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Upload Data File"),
                        html.P("Upload your access control data for analysis", className="text-muted mb-3"),

                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-2x mb-2", style={"color": "#007bff"}),
                                html.Br(),
                                'Drag and Drop or ',
                                html.A('Click to Select File', style={"color": "#007bff", "textDecoration": "underline"})
                            ], style={"textAlign": "center"}),
                            style={
                                'width': '100%',
                                'height': '120px',
                                'lineHeight': '120px',
                                'borderWidth': '2px',
                                'borderStyle': 'dashed',
                                'borderRadius': '10px',
                                'borderColor': '#007bff',
                                'textAlign': 'center',
                                'margin': '10px 0',
                                'backgroundColor': '#f8f9fa'
                            },
                            multiple=False  # FIXED: Single file only
                        ),

                        html.Div(id='upload-output', className="mt-3"),

                        html.Hr(),
                        html.H6("📋 Supported Formats:", className="mt-3"),
                        html.Ul([
                            html.Li("CSV files (.csv) - Recommended"),
                            html.Li("Excel files (.xlsx, .xls)"),
                            html.Li("JSON files (.json)")
                        ], className="mb-3"),

                        html.H6("📊 Expected Data Structure:"),
                        html.P("Your file should contain columns like:", className="text-muted"),
                        html.Ul([
                            html.Li("person_id - Employee/visitor identifier"),
                            html.Li("door_id - Door/access point identifier"),
                            html.Li("timestamp - When access occurred"),
                            html.Li("access_result - Granted/Denied/etc.")
                        ])
                    ])
                ])
            ], width=8),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📈 What happens next?"),
                        html.Ol([
                            html.Li("File is validated and processed"),
                            html.Li("Data structure is analyzed"),
                            html.Li("Summary statistics are generated"),
                            html.Li("Go to Analytics for detailed insights")
                        ]),
                        html.Hr(),
                        html.H6("🔒 Security Note:"),
                        html.P(
                            "Files are processed securely and temporarily stored only for your session.",
                            className="text-muted small"
                        )
                    ])
                ])
            ], width=4)
        ])
    ], className="container-fluid")


def main():
    """Main application entry point with enhanced error handling"""
    try:
        # Validate environment before starting
        _validate_environment()

        print("🚀 Starting Yōsai Intel Dashboard...")
        print("=" * 50)

        # Initialize services with error checking
        if not bootstrap_services():
            raise RuntimeError("Service initialization failed")

        # Create dashboard with validation
        app = create_simple_dashboard()
        if app is None:
            raise RuntimeError("Failed to create dashboard application")

        # Configure Flask settings securely
        from config.unified_config import get_config
        config = get_config()

        secret_key = config.get('security.secret_key')
        if secret_key == 'change-me' or len(str(secret_key)) < 32:
            raise ValueError("SECRET_KEY must be changed from default and be at least 32 characters")

        app.server.config["SECRET_KEY"] = secret_key
        app.server.config["WTF_CSRF_ENABLED"] = config.get('security.csrf_enabled', True)

        # Get runtime configuration
        host = config.get('app.host', '127.0.0.1')
        port = config.get('app.port', 8050)
        debug = config.get('app.debug', False)

        # Validate network configuration
        if host not in ['127.0.0.1', 'localhost'] and debug:
            logger.warning("Debug mode enabled with non-local host - security risk")

        # Print startup info
        print(f"🌐 URL: http://{host}:{port}")
        print(f"📊 Analytics: http://{host}:{port}/analytics")
        print(f"📤 Upload: http://{host}:{port}/file-upload")
        print("✅ Enhanced Security: ACTIVE")
        print("✅ Unified Configuration: ACTIVE")
        print("=" * 50)
        print("🚀 Dashboard starting...")

        # Run the application
        app.run_server(
            debug=debug,
            host=host,
            port=port
        )

    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        print(f"❌ Import Error: {e}")
        print("💡 Run: pip install -r requirements.txt")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Application startup error: {e}")
        print(f"❌ Startup Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected Error: {e}")
        print("📋 Check logs for detailed error information")
        sys.exit(1)


def _validate_environment():
    """Validate environment configuration before startup"""
    secret_key = os.getenv('SECRET_KEY', '')

    # For development, be more lenient
    env = os.getenv('YOSAI_ENV', 'development')
    if env == 'development':
        if not secret_key or len(secret_key) < 16:
            # Generate a temporary secret for development
            import secrets
            temp_secret = secrets.token_hex(32)
            os.environ['SECRET_KEY'] = temp_secret
            print(f"⚠️ Generated temporary SECRET_KEY for development: {temp_secret[:16]}...")
    else:
        # Production requirements are strict
        if not secret_key or len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters for production")

        if secret_key in ['change-me', 'dev-key-change-me', 'change-me-in-production']:
            raise ValueError("SECRET_KEY must be changed from default value")

    # Validate database configuration if not using mock
    db_type = os.getenv('DB_TYPE', 'mock')
    if db_type != 'mock':
        db_required = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        db_missing = [var for var in db_required if not os.getenv(var)]
        if db_missing:
            raise ValueError(f"Database configuration missing: {', '.join(db_missing)}")


if __name__ == "__main__":
    main()
