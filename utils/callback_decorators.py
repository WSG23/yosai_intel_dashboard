#!/usr/bin/env python3
"""
Decorators for Dash callbacks to handle JSON serialization
"""

import functools
import json
import logging
from typing import Callable, Any
import pandas as pd

# Safe import for Flask-Babel LazyString
try:
    from flask_babel import LazyString
    LAZYSTRING_AVAILABLE = True
except ImportError:
    LazyString = None
    LAZYSTRING_AVAILABLE = False

logger = logging.getLogger(__name__)


def sanitize_for_dash(data: Any) -> Any:
    """Sanitize data for Dash callback output - handles all JSON serialization issues"""

    if data is None:
        return None

    # Handle Flask-Babel LazyString objects (most common cause of the error)
    if LAZYSTRING_AVAILABLE and isinstance(data, LazyString):
        return str(data)

    # Handle any object that has LazyString in class name (fallback detection)
    if hasattr(data, '__class__') and 'LazyString' in str(data.__class__):
        return str(data)

    # Handle Babel lazy evaluation objects
    if hasattr(data, '_func') and hasattr(data, '_args'):
        try:
            return str(data)
        except Exception:
            return f"LazyString: {repr(data)}"

    # Handle functions - return safe representation
    if callable(data):
        try:
            from dash import html
            return html.Div(f"Function: {getattr(data, '__name__', 'anonymous')}")
        except ImportError:
            return {
                'type': 'function',
                'name': getattr(data, '__name__', 'anonymous'),
                'module': getattr(data, '__module__', None)
            }

    # Handle DataFrames
    if isinstance(data, pd.DataFrame):
        if len(data) > 100:  # Limit size
            data = data.head(100)
        return data.to_dict('records')

    # Handle lists and tuples recursively
    if isinstance(data, (list, tuple)):
        return type(data)(sanitize_for_dash(item) for item in data)

    # Handle dictionaries recursively
    if isinstance(data, dict):
        return {key: sanitize_for_dash(value) for key, value in data.items()}

    # Handle Dash components with potential LazyString properties
    if hasattr(data, 'to_plotly_json'):
        try:
            # Test if component is already serializable
            json.dumps(data.to_plotly_json())
            return data
        except (TypeError, ValueError):
            # Component has LazyString properties, sanitize them
            component_dict = data.to_plotly_json()
            return sanitize_for_dash(component_dict)

    # Handle complex objects
    if hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool)):
        try:
            # Test if object is already serializable
            json.dumps(data.__dict__)
            return data
        except (TypeError, ValueError):
            return {
                'type': 'object',
                'class': data.__class__.__name__,
                'repr': str(data)[:200]
            }

    # Test if primitive type is serializable
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
            try:
                from dash import html
                return html.Div([
                    html.H4("⚠️ Callback Error", className="text-warning"),
                    html.P(f"Function: {func.__name__}"),
                    html.P(f"Error: {str(e)[:100]}..."),
                ], className="alert alert-warning")
            except ImportError:
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
            try:
                from dash import html
                return html.Div([
                    html.H4("⚠️ Analytics Error", className="text-danger"),
                    html.P(f"Function: {func.__name__}"),
                    html.P(f"Analytics processing failed: {str(e)[:100]}..."),
                ], className="alert alert-danger")
            except ImportError:
                return {
                    'error': True,
                    'message': f"Analytics processing failed: {str(e)}",
                    'callback': func.__name__
                }

    return wrapper


# Export for easy importing
__all__ = ['safe_callback', 'analytics_callback', 'sanitize_for_dash']
