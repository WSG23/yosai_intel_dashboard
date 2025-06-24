"""
Core package initialization
"""
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the main app factory function
from .app_factory import create_app, create_application

__all__ = ['create_app', 'create_application']
