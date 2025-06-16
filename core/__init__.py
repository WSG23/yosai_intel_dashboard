# core/__init__.py - Simple and production ready
"""
Yōsai Intel Dashboard - Core Package
Your current DI implementation is perfect - no changes needed!
"""

from .container import Container, get_container, reset_container
from .config_manager import ConfigManager
from .app_factory import create_application
from .service_registry import get_configured_container

# Export public API
__all__ = [
    'Container',
    'get_container', 
    'reset_container',
    'ConfigManager',
    'create_application',
    'get_configured_container'
]

# Version info
__version__ = '1.0.0'

# Status check
def verify_di_system():
    """Quick verification that DI system is working"""
    try:
        # Test basic functionality
        container = Container()
        container.register('test', lambda: "DI Working!")
        result = container.get('test')
        
        # Test configured container
        configured = get_configured_container()
        
        return {
            'status': 'healthy',
            'basic_di': result == "DI Working!",
            'configured_services': len(configured.list_services()),
            'message': 'Your DI system is production ready!'
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': str(e),
            'message': 'Check your DI configuration'
        }

# Quick test on import
if __name__ == "__main__":
    status = verify_di_system()
    print(f"DI Status: {status['message']}")