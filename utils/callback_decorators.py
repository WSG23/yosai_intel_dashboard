# utils/callback_decorators.py
"""
Decorators for Dash callbacks to handle JSON serialization
"""

import functools
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def safe_callback(func: Callable) -> Callable:
    """Decorator to make Dash callbacks safe from JSON serialization errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute the original callback
            result = func(*args, **kwargs)
            
            # Sanitize the result for Dash
            sanitized_result = sanitize_for_dash(result)
            
            return sanitized_result
            
        except Exception as e:
            logger.error(f"Error in callback {func.__name__}: {e}")
            
            # Return safe error representation
            return {
                'error': True,
                'message': str(e),
                'callback': func.__name__
            }
    
    return wrapper


def analytics_callback(func: Callable) -> Callable:
    """Specialized decorator for analytics callbacks"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Special handling for analytics data
            if isinstance(result, dict) and 'analytics' in result:
                # Ensure analytics data is JSON serializable
                result['analytics'] = sanitize_for_dash(result['analytics'])
            
            return sanitize_for_dash(result)
            
        except Exception as e:
            logger.error(f"Error in analytics callback {func.__name__}: {e}")
            return {
                'error': True,
                'message': f"Analytics processing failed: {str(e)}",
                'callback': func.__name__
            }
    
    return wrapper

