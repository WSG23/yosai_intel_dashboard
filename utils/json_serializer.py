# utils/json_serializer.py
"""
JSON Serialization utilities for Yōsai Intel Dashboard
Fixes the "TypeError: Type is not JSON serializable: function" error
"""

import json
import pandas as pd
import numpy as np
from typing import Any, Dict, Callable, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, is_dataclass
import logging

logger = logging.getLogger(__name__)


class YosaiJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles all Yōsai-specific types"""

    def default(self, obj: Any) -> Any:
        # Handle Flask-Babel LazyString objects FIRST
        try:
            from flask_babel import LazyString
            if isinstance(obj, LazyString):
                return str(obj)
        except ImportError:
            pass

        # Handle any object with LazyString in class name (fallback)
        if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
            return str(obj)

        # Handle Babel lazy evaluation objects
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            try:
                return str(obj)
            except Exception:
                return f"LazyString: {repr(obj)}"

        # Handle functions
        if callable(obj):
            return {
                '__type__': 'function',
                '__name__': getattr(obj, '__name__', 'anonymous'),
                '__module__': getattr(obj, '__module__', None),
                '__repr__': repr(obj)
            }
        
        # Handle pandas DataFrames
        if isinstance(obj, pd.DataFrame):
            return {
                '__type__': 'dataframe',
                '__shape__': obj.shape,
                '__columns__': list(obj.columns),
                '__data__': obj.to_dict('records')[:100],  # Limit to first 100 rows
                '__truncated__': len(obj) > 100
            }
        
        # Handle pandas Series
        if isinstance(obj, pd.Series):
            return {
                '__type__': 'series',
                '__name__': obj.name,
                '__data__': obj.to_dict()
            }
        
        # Handle numpy arrays
        if isinstance(obj, np.ndarray):
            return {
                '__type__': 'numpy_array',
                '__shape__': obj.shape,
                '__data__': obj.tolist()
            }
        
        # Handle numpy types
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        
        # Handle datetime objects
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                '__value__': obj.isoformat()
            }
        
        # Handle dataclasses
        if is_dataclass(obj):
            return {
                '__type__': 'dataclass',
                '__class__': obj.__class__.__name__,
                '__data__': asdict(obj)
            }
        
        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            return {
                '__type__': 'object',
                '__class__': obj.__class__.__name__,
                '__dict__': self._safe_dict(obj.__dict__)
            }
        
        # Handle sets
        if isinstance(obj, set):
            return {
                '__type__': 'set',
                '__data__': list(obj)
            }
        
        return super().default(obj)
    
    def _safe_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Safely convert dict, filtering out non-serializable items"""
        safe = {}
        for key, value in d.items():
            try:
                json.dumps(value, cls=YosaiJSONEncoder)
                safe[key] = value
            except TypeError:
                safe[f"{key}_type"] = type(value).__name__
        return safe


def safe_json_serialize(data: Any, pretty: bool = False) -> str:
    """Safely serialize data to JSON string"""
    try:
        indent = 2 if pretty else None
        return json.dumps(data, cls=YosaiJSONEncoder, indent=indent, ensure_ascii=False)
    except Exception as e:
        logger.error(f"JSON serialization failed: {e}")
        return json.dumps({"error": str(e), "type": type(data).__name__})


def sanitize_for_dash(data: Any) -> Any:
    """Sanitize data specifically for Dash callback outputs"""
    if data is None:
        return None
    
    # Handle DataFrames - convert to dict for Dash
    if isinstance(data, pd.DataFrame):
        if len(data) > 1000:  # Limit size for performance
            data = data.head(1000)
        return {
            'type': 'dataframe',
            'data': data.to_dict('records'),
            'columns': list(data.columns),
            'shape': data.shape
        }
    
    # Handle functions - return metadata only
    if callable(data):
        return {
            'type': 'function',
            'name': getattr(data, '__name__', 'anonymous'),
            'module': getattr(data, '__module__', None)
        }
    
    # Handle complex objects - return safe representation
    if hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool, list, dict)):
        return {
            'type': 'object',
            'class': data.__class__.__name__,
            'repr': str(data)
        }
    
    # Handle lists and dicts recursively
    if isinstance(data, list):
        return [sanitize_for_dash(item) for item in data]
    
    if isinstance(data, dict):
        return {key: sanitize_for_dash(value) for key, value in data.items()}
    
    return data
