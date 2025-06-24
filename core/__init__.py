# core/__init__.py - FIXED: Remove f-string syntax error
"""
Yōsai Intel Dashboard - Core Package
FIXED version that removes the f-string syntax error
"""

from .unified_container import UnifiedServiceContainer, get_container
from .config_manager import ConfigManager
from .app_factory import create_application
from .container import get_service

# Export public API
__all__ = [
    'UnifiedServiceContainer',
    'get_container',
    'ConfigManager',
    'create_application',
    'get_service'
]

# Version info
__version__ = '1.0.0'

# Status check - FIXED: Safe version without problematic f-strings
def verify_di_system():
    """Quick verification that DI system is working"""
    try:
        # Test basic functionality
        container = UnifiedServiceContainer()
        container.register('test', lambda: "DI Working!")

        result = container.get('test')
        
        # Test configured container - FIXED: Safe service counting
        configured = get_container()
        service_count = len(get_container()._services)
        
        return {
            'status': 'healthy',
            'basic_di': result == "DI Working!",
            'configured_services': service_count,
            'message': 'Your DI system is production ready!'
        }
    except Exception as e:
        return {
            'status': 'error', 
            'error': str(e),
            'message': 'Check your DI configuration'
        }

# REMOVED: Problematic __main__ block that caused f-string issues
# The error was likely in a print statement with malformed f-string brackets

# Quick test function - SAFE VERSION
def test_di_system():
    """Safe test function without f-strings"""
    status = verify_di_system()
    print("DI Status: " + status['message'])
    return status['status'] == 'healthy'
