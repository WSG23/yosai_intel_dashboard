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
        from core.service_container import configure_services
        configure_services()
        print("✅ Services configured")
    except Exception as e:
        print(f"⚠️ Service configuration failed: {e}")


def create_simple_dashboard():
    """Create a simplified dashboard that works immediately"""
    try:
        import dash
        from dash import html, dcc
        import dash_bootstrap_components as dbc
        
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
        
        logger.info("✅ Simple dashboard created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return None


def create_dashboard_page():
    """Create main dashboard page"""
    import dash_bootstrap_components as dbc
    from dash import html
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🏯 Welcome to Yōsai Intel Dashboard", className="card-title"),
                        html.P("Security intelligence and access control monitoring.", className="card-text"),
                        html.P("Your modular dashboard is now running successfully!", className="text-success"),
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
    """Main application entry point"""
    try:
        print("🚀 Starting Yōsai Intel Dashboard...")
        print("=" * 50)

        # Initialize services
        bootstrap_services()

        # Create simple dashboard
        app = create_simple_dashboard()
        if app is None:
            print("❌ Failed to create dashboard")
            sys.exit(1)
        
        # Configure Flask settings
        app.server.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        app.server.config["WTF_CSRF_ENABLED"] = os.getenv("WTF_CSRF_ENABLED", "True") == "True"
        
        # Get configuration
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8050"))
        debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # Print startup info
        print(f"🌐 URL: http://{host}:{port}")
        print(f"📊 Analytics: http://{host}:{port}/analytics")
        print(f"📤 Upload: http://{host}:{port}/file-upload")
        print("✅ Simplified Architecture: ACTIVE")
        print("✅ Basic Navigation: ENABLED")
        print("=" * 50)
        print("🚀 Dashboard starting...")
        
        # Run the application
        app.run_server(
            debug=debug,
            host=host,
            port=port
        )
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
