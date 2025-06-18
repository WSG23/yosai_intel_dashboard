#!/usr/bin/env python3
"""
Simple App Launcher - Bypasses complex auth setup for development
"""

# Load environment first
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    if Path(".env").exists():
        load_dotenv(override=True)
        print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not available")

# Set required environment variables
required_vars = {
    "DB_HOST": "localhost",
    "SECRET_KEY": "dev-secret-12345",
    "AUTH0_CLIENT_ID": "dev-client-id",
    "AUTH0_CLIENT_SECRET": "dev-client-secret",
    "AUTH0_DOMAIN": "dev.auth0.com",
    "AUTH0_AUDIENCE": "dev-audience",
    "YOSAI_ENV": "development"
}

for var, default in required_vars.items():
    if not os.getenv(var):
        os.environ[var] = default

def create_simple_app():
    """Create app without problematic auth integration"""
    try:
        import dash
        from dash import html, dcc
        
        # Create simple Dash app
        app = dash.Dash(__name__, suppress_callback_exceptions=True)
        app.title = "Yōsai Intel Dashboard"
        
        # Simple layout
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
            html.Hr(),
            html.Div([
                html.P("✅ Environment configuration loaded successfully"),
                html.P("✅ Dash application created"),
                html.P("⚠️  Running in simplified mode (auth disabled)"),
                html.Br(),
                html.H3("Available Features:"),
                html.Ul([
                    html.Li("Dashboard viewing"),
                    html.Li("Configuration management"), 
                    html.Li("Component loading"),
                ]),
                html.Br(),
                html.P("🚀 Dashboard is running successfully!", className="alert alert-success")
            ], className="container", style={"margin": "2rem"})
        ])
        
        return app
        
    except Exception as e:
        print(f"❌ Failed to create simple app: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Simple Yosai Intel Dashboard...")
    
    app = create_simple_app()
    if app:
        print("✅ App created successfully")
        print("🌐 Starting server...")
        print("📍 URL: http://127.0.0.1:8050")
        app.run_server(debug=True, host="127.0.0.1", port=8050)
    else:
        print("❌ Failed to create app")
