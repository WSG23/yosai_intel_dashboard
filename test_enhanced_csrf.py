# test_enhanced_csrf.py
"""Test script for enhanced CSRF features"""

import dash
from dash import html, dcc
from dash_csrf_plugin import DashCSRFPlugin, CSRFConfig, CSRFMode

def test_enhanced_features():
    """Test the enhanced CSRF features"""
    
    app = dash.Dash(__name__)
    
    # Test enhanced config with wildcard routes
    config = CSRFConfig.for_development(
        exempt_routes=['/test/*', '/api/webhook'],
        exempt_views=['special_view']
    )
    
    plugin = DashCSRFPlugin(app, config=config, mode=CSRFMode.DEVELOPMENT)
    
    # Test wildcard route exemption
    plugin.add_exempt_route('/custom/*')
    plugin.add_exempt_view('my_view_function')
    
    status = plugin.get_status()
    
    print("🧪 Enhanced CSRF Test Results:")
    print(f"✅ Enhanced exemptions: {status.get('enhanced_exemptions', False)}")
    print(f"✅ Wildcard support: {status.get('wildcard_routes_supported', False)}")
    print(f"✅ Exempt routes: {len(status.get('exempt_routes', []))}")
    print(f"✅ Exempt views: {len(status.get('exempt_views', []))}")
    
    return plugin

if __name__ == "__main__":
    test_enhanced_features()
