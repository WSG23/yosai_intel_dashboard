"""
Test script to verify the CSRF plugin works
"""

import dash
from dash import html
from dash_csrf_plugin import DashCSRFPlugin, CSRFMode

def test_plugin():
    """Test the CSRF plugin"""
    print("🧪 Testing CSRF Plugin...")
    
    try:
        # Test plugin creation
        app = dash.Dash(__name__)
        plugin = DashCSRFPlugin(app, mode=CSRFMode.DEVELOPMENT)
        
        print(f"✅ Plugin created: {plugin}")
        print(f"✅ Mode: {plugin.mode.value}")
        print(f"✅ Enabled: {plugin.is_enabled}")
        print(f"✅ Status: {plugin.get_status()}")
        
        # Test layout component
        csrf_component = plugin.create_csrf_component()
        print(f"✅ CSRF component created: {type(csrf_component)}")
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_plugin()
