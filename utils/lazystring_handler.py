#!/usr/bin/env python3
"""
LazyString Safe Wrapper
Handles Flask-Babel LazyString objects in Dash callbacks
"""

import json
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def sanitize_lazystring_recursive(obj: Any) -> Any:
    """Recursively sanitize LazyString objects"""

    # Handle Flask-Babel LazyString objects directly
    try:
        from flask_babel import LazyString
        if isinstance(obj, LazyString):
            return str(obj)
    except ImportError:
        pass

    # Handle LazyString objects by class name (fallback detection)
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)

    # Handle Babel lazy objects with _func and _args
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        try:
            return str(obj)
        except Exception:
            return f"LazyString: {repr(obj)}"

    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return type(obj)(sanitize_lazystring_recursive(item) for item in obj)

    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: sanitize_lazystring_recursive(value) for key, value in obj.items()}

    # Handle Dash components with LazyString properties
    if hasattr(obj, 'children') and hasattr(obj, 'to_plotly_json'):
        try:
            # Try to serialize as-is first
            json.dumps(obj.to_plotly_json())
            return obj
        except (TypeError, ValueError):
            # Component has LazyString properties, sanitize them
            component_dict = obj.to_plotly_json()
            return sanitize_lazystring_recursive(component_dict)

    # Handle objects with LazyString attributes
    if hasattr(obj, '__dict__'):
        try:
            # Test if already serializable
            json.dumps(obj.__dict__, default=str)
            return obj
        except Exception:
            # Create safe representation
            safe_dict = {}
            for key, value in obj.__dict__.items():
                safe_dict[key] = sanitize_lazystring_recursive(value)
            return {
                'type': obj.__class__.__name__,
                'attributes': safe_dict
            }

    # For primitive types, return as-is
    return obj


def lazystring_safe_callback(func: Callable) -> Callable:
    """Decorator to make callbacks safe from LazyString serialization errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute original callback
            result = func(*args, **kwargs)
            
            # Sanitize LazyString objects in the result
            sanitized_result = sanitize_lazystring_recursive(result)
            
            # Test final serialization
            try:
                json.dumps(sanitized_result, default=str)
                return sanitized_result
            except:
                # Ultimate fallback
                return str(sanitized_result)
                
        except Exception as e:
            logger.error(f"LazyString callback {func.__name__} failed: {e}")
            
            # Return safe error component
            try:
                from dash import html
                return html.Div([
                    html.H4("⚠️ Translation Error", className="text-warning"),
                    html.P(f"Callback: {func.__name__}"),
                    html.P(f"LazyString serialization error"),
                ], className="alert alert-warning")
            except ImportError:
                return {"error": "LazyString serialization error", "callback": func.__name__}
    
    return wrapper


# Export for easy importing
__all__ = ['lazystring_safe_callback', 'sanitize_lazystring_recursive']
