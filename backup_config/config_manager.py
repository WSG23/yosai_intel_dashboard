# core/config_manager.py
"""Centralized configuration management extracted from app.py"""
import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    title: str = "Yōsai Intel Dashboard"
    secret_key: str = "dev-key-change-in-production"

class ConfigManager:
    """Configuration manager extracted from app.py"""
    
    def __init__(self):
        self.app_config = self._create_app_config()
    
    @classmethod
    def from_environment(cls) -> 'ConfigManager':
        """Create config from environment - replaces get_app_config() from app.py"""
        return cls()
    
    def _create_app_config(self) -> AppConfig:
        """Extract from your current get_app_config() function"""
        return AppConfig(
            debug=os.getenv('DEBUG', 'True').lower() == 'true',
            host=os.getenv('HOST', '127.0.0.1'),
            port=int(os.getenv('PORT', '8050')),
            secret_key=os.getenv('SECRET_KEY', 'dev-key-change-in-production')
        )
    
    def get_stylesheets(self) -> List[str]:
        """Get CSS stylesheets"""
        stylesheets = ["/assets/css/main.css"]
        
        # Add Bootstrap if available (from your current app.py logic)
        try:
            import dash_bootstrap_components as dbc
            if hasattr(dbc, 'themes') and hasattr(dbc.themes, 'BOOTSTRAP'):
                stylesheets.insert(0, dbc.themes.BOOTSTRAP)
        except ImportError:
            pass
        
        return stylesheets
    
    def get_meta_tags(self) -> List[Dict[str, str]]:
        """Get HTML meta tags - from your current app.py"""
        return [
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "theme-color", "content": "#1B2A47"}
        ]
    
    def print_startup_info(self) -> None:
        """Print startup info - extracted from your print_startup_info()"""
        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD")
        print("=" * 60)
        print(f"🌐 URL: http://{self.app_config.host}:{self.app_config.port}")
        print(f"🔧 Debug Mode: {self.app_config.debug}")
        print(f"📊 Analytics: http://{self.app_config.host}:{self.app_config.port}/analytics")
        print("=" * 60)
        
        if self.app_config.debug:
            print("⚠️  Running in DEBUG mode - do not use in production!")
        
        print("\n🚀 Dashboard starting...")