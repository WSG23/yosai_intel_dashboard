#!/usr/bin/env python3
"""
Flask JSON Provider that handles LazyString objects
This fixes the core Dash JSON serialization issue
"""

import json
import logging
from typing import Any
from flask.json.provider import DefaultJSONProvider

# Safe import for Flask-Babel LazyString
try:
    from flask_babel import LazyString
    BABEL_AVAILABLE = True
except ImportError:
    LazyString = None  # type: ignore
    BABEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class LazyStringSafeJSONEncoder(json.JSONEncoder):
    """JSON encoder that specifically handles LazyString objects"""

    def default(self, obj: Any) -> Any:
        # Handle Flask-Babel LazyString objects - CRITICAL FIX
        if BABEL_AVAILABLE and isinstance(obj, LazyString):
            return str(obj)

        # Handle any object with LazyString in class name (fallback)
        if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
            return str(obj)

        # Handle Babel lazy evaluation objects
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            try:
                return str(obj)
            except Exception:
                return f"LazyString: {repr(obj)}"

        # Handle callables
        if callable(obj):
            return {
                'type': 'function',
                'name': getattr(obj, '__name__', 'anonymous')
            }

        # Let the parent encoder handle it
        return super().default(obj)


class YosaiJSONProvider(DefaultJSONProvider):
    """Custom JSON provider that handles LazyString and other Yōsai types"""

    def dumps(self, obj: Any, **kwargs) -> str:
        """Dump object to JSON string using LazyString-safe encoder"""
        kwargs.setdefault("cls", LazyStringSafeJSONEncoder)
        kwargs.setdefault("ensure_ascii", False)
        try:
            return json.dumps(obj, **kwargs)
        except Exception as e:
            logger.error(f"JSON serialization failed: {e}")
            # Return safe error representation
            return json.dumps({
                'error': 'JSON serialization failed',
                'message': str(e),
                'type': type(obj).__name__ if hasattr(obj, '__class__') else 'unknown'
            })

    def loads(self, s: str, **kwargs) -> Any:
        """Load JSON string to object"""
        return json.loads(s, **kwargs)
