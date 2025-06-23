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
    """Create a simplified dashboard that works immediately"""
    try:
        import dash
        from dash import html, dcc
        import dash_bootstrap_components as dbc
        import io
        
        # Create basic Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
            meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ]
        )
        
        # Simple layout
        app.layout = html.Div([
            dbc.NavbarSimple(
                brand="🏯 Yōsai Intel Dashboard",
                brand_href="/",
                color="dark",
                dark=True,
                children=[
                    dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
                    dbc.NavItem(dbc.NavLink("Analytics", href="/analytics")),
                    dbc.NavItem(dbc.NavLink("Upload", href="/file-upload")),
                ]
            ),
            
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content", className="container mt-4")
        ])
        
        # Simple page routing callback
        @app.callback(
            dash.dependencies.Output("page-content", "children"),
            dash.dependencies.Input("url", "pathname")
        )
        def display_page(pathname):
            if pathname == "/analytics":
                return create_analytics_page()
            elif pathname == "/file-upload":
                return create_upload_page()
            else:
                return create_dashboard_page()

        # Register callback for file uploads
        register_upload_callback(app)

        logger.info("✅ Simple dashboard created successfully")

        return app

    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return None


def register_upload_callback(app):
    """Register file upload callback"""
    from dash import callback, Output, Input, State, html
    import base64
    import pandas as pd

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
            # Decode uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Get analytics service
            from services.service_registry import get_analytics_service
            analytics = get_analytics_service()

            # Simple file processing
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            else:
                return html.Div([
                    html.H6("File uploaded!", className="text-success"),
                    html.P(f"Filename: {filename}"),
                    html.P("Note: Only CSV processing implemented for demo")
                ], className="alert alert-info")

            # Analyze with your existing service
            result = analytics.analyze_data(df)

            if result.success:
                return html.Div([
                    html.H6("✅ File processed successfully!", className="text-success"),
                    html.P(f"Filename: {filename}"),
                    html.P(f"Rows processed: {result.data.get('total_events', 0)}"),
                    html.P(f"Columns found: {len(result.data.get('columns_found', []))}"),
                ], className="alert alert-success")
            else:
                return html.Div([
                    html.H6("⚠️ Processing error", className="text-warning"),
                    html.P(f"Error: {result.error}")
                ], className="alert alert-warning")

        except Exception as e:
            return html.Div([
                html.H6("❌ Upload failed", className="text-danger"),
                html.P(f"Error: {str(e)}")
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
    """Create file upload page"""
    import dash_bootstrap_components as dbc
    from dash import html, dcc
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H2("📤 File Upload"),
                html.P("Upload access control data for analysis"),
                html.Hr(),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Upload Data File"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=True
                        ),
                        html.Div(id='upload-output'),
                        html.Hr(),
                        html.H6("Supported Formats:"),
                        html.P("• CSV files (.csv)", className="mb-1"),
                        html.P("• Excel files (.xlsx, .xls)", className="mb-1"),
                        html.P("• JSON files (.json)", className="mb-1"),
                    ])
                ])
            ], width=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Expected Columns:"),
                        html.P("• person_id", className="mb-1"),
                        html.P("• door_id", className="mb-1"),
                        html.P("• timestamp", className="mb-1"),
                        html.P("• access_result", className="mb-1"),
                    ])
                ])
            ], width=4),
        ])
    ])


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
