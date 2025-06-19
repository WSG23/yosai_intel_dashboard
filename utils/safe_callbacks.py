#!/usr/bin/env python3
"""
Safe Callback Wrapper - Fixes JSON serialization issues
"""

import json
import functools
import logging
from typing import Any, Callable
import pandas as pd
from dash import html

logger = logging.getLogger(__name__)


def sanitize_dash_output(data: Any) -> Any:
    """Sanitize data for Dash callback output"""

    if data is None:
        return None

    # Handle LazyString objects FIRST
    try:
        from flask_babel import LazyString
        if isinstance(data, LazyString):
            return str(data)
    except ImportError:
        pass

    # Handle any object with LazyString in class name
    if hasattr(data, '__class__') and 'LazyString' in str(data.__class__):
        return str(data)

    # Handle Babel lazy objects
    if hasattr(data, '_func') and hasattr(data, '_args'):
        try:
            return str(data)
        except Exception:
            return f"LazyString: {repr(data)}"

    # Handle functions - return safe representation
    if callable(data):
        return html.Div(f"Function: {getattr(data, '__name__', 'anonymous')}")
    
    # Handle DataFrames
    if isinstance(data, pd.DataFrame):
        if len(data) > 100:  # Limit size
            data = data.head(100)
        return data.to_dict('records')
    
    # Handle lists
    if isinstance(data, (list, tuple)):
        return [sanitize_dash_output(item) for item in data]
    
    # Handle dictionaries  
    if isinstance(data, dict):
        return {key: sanitize_dash_output(value) for key, value in data.items()}
    
    # Handle complex objects
    if hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool)):
        return {
            'type': 'object',
            'class': data.__class__.__name__,
            'repr': str(data)[:200]
        }
    
    # Test if serializable
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError):
        # Return safe representation
        return {
            'type': type(data).__name__,
            'repr': str(data)[:200],
            'serializable': False
        }


def safe_callback(func: Callable) -> Callable:
    """Decorator to make callbacks safe from JSON serialization errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute original callback
            result = func(*args, **kwargs)
            
            # Sanitize the result
            if isinstance(result, (list, tuple)):
                # Multiple outputs
                sanitized = [sanitize_dash_output(item) for item in result]
                return type(result)(sanitized)
            else:
                # Single output
                return sanitize_dash_output(result)
                
        except Exception as e:
            logger.error(f"Callback {func.__name__} failed: {e}")
            
            # Return safe error component
            return html.Div([
                html.H4("⚠️ Callback Error", className="text-warning"),
                html.P(f"Function: {func.__name__}"),
                html.P(f"Error: {str(e)[:100]}..."),
            ], className="alert alert-warning")
    
    return wrapper


# Export for easy importing
__all__ = ['safe_callback', 'sanitize_dash_output']
