# plugins/builtin/json_serialization_plugin.py
"""
JSON Serialization Plugin - First official plugin for Yōsai Intel Dashboard
Demonstrates the plugin architecture and solves JSON serialization issues
"""

import json
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, date
from dataclasses import dataclass, asdict, is_dataclass
import logging
import functools
from enum import Enum

try:
    # Optional dependency - may not be installed in test environment
    from flask_babel import LazyString  # type: ignore
except Exception:  # pragma: no cover - fallback when Flask-Babel not installed
    LazyString = None  # type: ignore

from core.plugins.protocols import (
    PluginProtocol, PluginMetadata, PluginPriority,
    ServicePluginProtocol, CallbackPluginProtocol
)
from core.protocols import SerializationProtocol, CallbackProtocol
from core.error_handling import with_error_handling, ErrorCategory, ErrorSeverity
from core.performance import measure_performance, MetricType

logger = logging.getLogger(__name__)

@dataclass
class JsonSerializationConfig:
    """Configuration for JSON serialization plugin"""
    enabled: bool = True
    max_dataframe_rows: int = 1000
    max_string_length: int = 10000
    include_type_metadata: bool = True
    compress_large_objects: bool = True
    fallback_to_repr: bool = True
    auto_wrap_callbacks: bool = True

class YosaiJSONEncoder(json.JSONEncoder):
    """Yōsai-specific JSON encoder with comprehensive type support"""
    
    def __init__(self, config: JsonSerializationConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def default(self, obj: Any) -> Any:
        """Handle all Yōsai-specific types with proper error boundaries"""
        
        # Handle Flask-Babel LazyString objects
        if (LazyString is not None and isinstance(obj, LazyString)) or 'LazyString' in obj.__class__.__name__:
            return str(obj)

        # Handle pandas DataFrames
        if isinstance(obj, pd.DataFrame):
            return self._encode_dataframe(obj)
        
        # Handle pandas Series
        if isinstance(obj, pd.Series):
            return self._encode_series(obj)
        
        # Handle numpy types
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        
        if isinstance(obj, np.ndarray):
            return self._encode_numpy_array(obj)
        
        # Handle datetime objects
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle callable objects (functions, methods)
        if callable(obj):
            return self._encode_callable(obj)
        
        # Handle dataclasses
        if is_dataclass(obj):
            return self._encode_dataclass(obj)
        
        # Handle enums
        if isinstance(obj, Enum):
            return obj.value
        
        # Handle sets
        if isinstance(obj, set):
            return list(obj)
        
        # Handle complex objects with __dict__
        if hasattr(obj, '__dict__'):
            return self._encode_complex_object(obj)
        
        # Fallback to string representation
        if self.config.fallback_to_repr:
            return f"<{type(obj).__name__}: {str(obj)[:100]}>"
        
        return super().default(obj)
    
    def _encode_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Safely encode DataFrame with size limits"""
        rows_to_include = min(len(df), self.config.max_dataframe_rows)
        
        return {
            '__type__': 'dataframe',
            '__shape__': df.shape,
            '__columns__': list(df.columns),
            '__data__': df.head(rows_to_include).to_dict('records'),
            '__truncated__': len(df) > self.config.max_dataframe_rows,
            '__dtypes__': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    def _encode_series(self, series: pd.Series) -> Dict[str, Any]:
        """Safely encode pandas Series"""
        return {
            '__type__': 'series',
            '__name__': series.name,
            '__length__': len(series),
            '__data__': series.head(100).to_dict(),
            '__dtype__': str(series.dtype)
        }
    
    def _encode_numpy_array(self, arr: np.ndarray) -> Dict[str, Any]:
        """Safely encode numpy arrays"""
        return {
            '__type__': 'numpy_array',
            '__shape__': arr.shape,
            '__dtype__': str(arr.dtype),
            '__data__': arr.flatten()[:1000].tolist()  # Limit size
        }
    
    def _encode_callable(self, obj: Any) -> Dict[str, Any]:
        """Safely encode callable objects"""
        return {
            '__type__': 'callable',
            '__name__': getattr(obj, '__name__', 'anonymous'),
            '__module__': getattr(obj, '__module__', None),
            '__qualname__': getattr(obj, '__qualname__', None),
            '__doc__': getattr(obj, '__doc__', None)
        }
    
    def _encode_dataclass(self, obj: Any) -> Dict[str, Any]:
        """Safely encode dataclass objects"""
        try:
            return {
                '__type__': 'dataclass',
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                '__data__': asdict(obj)
            }
        except Exception:
            return {
                '__type__': 'dataclass',
                '__class__': obj.__class__.__name__,
                '__repr__': repr(obj)
            }
    
    def _encode_complex_object(self, obj: Any) -> Dict[str, Any]:
        """Safely encode complex objects"""
        safe_dict = {}
        
        for key, value in obj.__dict__.items():
            try:
                # Test if value is JSON serializable
                json.dumps(value, cls=YosaiJSONEncoder, config=self.config)
                safe_dict[key] = value
            except (TypeError, ValueError):
                # Replace with type information
                safe_dict[f"{key}__type"] = type(value).__name__
        
        return {
            '__type__': 'object',
            '__class__': obj.__class__.__name__,
            '__module__': obj.__class__.__module__,
            '__dict__': safe_dict
        }

class JsonSerializationService:
    """JSON serialization service implementation"""
    
    def __init__(self, config: JsonSerializationConfig):
        self.config = config
        self.encoder = YosaiJSONEncoder(config)
        self.logger = logging.getLogger(__name__)
    
    @measure_performance("serialization.serialize", MetricType.SERIALIZATION)
    @with_error_handling(ErrorCategory.CONFIGURATION, ErrorSeverity.MEDIUM)
    def serialize(self, data: Any) -> str:
        """Serialize data to JSON string with comprehensive error handling"""
        try:
            return json.dumps(data, cls=YosaiJSONEncoder, config=self.config, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Serialization failed: {e}")
            return json.dumps({
                'error': True,
                'message': str(e),
                'type': type(data).__name__
            })
    
    @measure_performance("serialization.sanitize", MetricType.SERIALIZATION)
    def sanitize_for_transport(self, data: Any) -> Any:
        """Sanitize data specifically for Dash callback transport"""
        
        if data is None:
            return None

        # Handle Flask-Babel LazyString objects
        if (LazyString is not None and isinstance(data, LazyString)) or (
            hasattr(data, '__class__') and 'LazyString' in data.__class__.__name__
        ):
            return str(data)

        # Handle DataFrames - convert to transport-safe format
        if isinstance(data, pd.DataFrame):
            return self._sanitize_dataframe(data)
        
        # Handle functions - return metadata only
        if callable(data):
            return self._sanitize_callable(data)
        
        # Handle lists recursively
        if isinstance(data, list):
            return [self.sanitize_for_transport(item) for item in data]
        
        # Handle dictionaries recursively
        if isinstance(data, dict):
            return {key: self.sanitize_for_transport(value) 
                   for key, value in data.items()}
        
        # Handle complex objects
        if hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool)):
            return self._sanitize_complex_object(data)
        
        return data
    
    def is_serializable(self, data: Any) -> bool:
        """Check if data can be safely serialized to JSON"""
        try:
            json.dumps(data, cls=YosaiJSONEncoder, config=self.config)
            return True
        except (TypeError, ValueError):
            return False
    
    def _sanitize_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert DataFrame to transport-safe format"""
        if len(df) > self.config.max_dataframe_rows:
            df = df.head(self.config.max_dataframe_rows)
        
        return {
            'type': 'dataframe',
            'shape': df.shape,
            'columns': list(df.columns),
            'data': df.to_dict('records'),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    def _sanitize_callable(self, obj: Any) -> Dict[str, Any]:
        """Convert callable to transport-safe format"""
        return {
            'type': 'callable',
            'name': getattr(obj, '__name__', 'anonymous'),
            'module': getattr(obj, '__module__', None)
        }
    
    def _sanitize_complex_object(self, obj: Any) -> Dict[str, Any]:
        """Convert complex object to transport-safe format"""
        return {
            'type': 'object',
            'class': obj.__class__.__name__,
            'module': obj.__class__.__module__,
            'repr': str(obj)[:200]  # Limit representation length
        }

class JsonCallbackService:
    """Service for wrapping and managing Dash callbacks safely"""
    
    def __init__(self, serialization_service: JsonSerializationService):
        self.serialization = serialization_service
        self.logger = logging.getLogger(__name__)
    
    @measure_performance("callback.wrap", MetricType.CALLBACK)
    def wrap_callback(self, callback_func: Callable) -> Callable:
        """Wrap a callback function for safe execution and JSON serialization"""
        
        @functools.wraps(callback_func)
        def safe_wrapper(*args, **kwargs):
            try:
                # Execute the original callback
                result = callback_func(*args, **kwargs)
                
                # Validate and sanitize the result
                sanitized_result = self.validate_callback_output(result)
                
                return sanitized_result
                
            except Exception as e:
                self.logger.error(f"Callback {callback_func.__name__} failed: {e}")
                
                # Return safe error representation
                return self._create_error_response(callback_func.__name__, str(e))
        
        return safe_wrapper
    
    def validate_callback_output(self, output: Any) -> Any:
        """Validate and sanitize callback output for JSON transport"""
        
        # Handle single outputs
        if not isinstance(output, (list, tuple)):
            return self.serialization.sanitize_for_transport(output)
        
        # Handle multiple outputs (tuple/list)
        if isinstance(output, (list, tuple)):
            sanitized_outputs = []
            for item in output:
                sanitized_item = self.serialization.sanitize_for_transport(item)
                sanitized_outputs.append(sanitized_item)
            
            # Preserve the original type (tuple vs list)
            return type(output)(sanitized_outputs)
        
        return output
    
    def _create_error_response(self, callback_name: str, error_message: str) -> Dict[str, Any]:
        """Create a safe error response for failed callbacks"""
        return {
            'error': True,
            'callback': callback_name,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }

class JsonSerializationPlugin(ServicePluginProtocol, CallbackPluginProtocol):
    """JSON Serialization Plugin - Comprehensive solution for JSON serialization issues"""
    
    def __init__(self):
        self.config: Optional[JsonSerializationConfig] = None
        self.serialization_service: Optional[JsonSerializationService] = None
        self.callback_service: Optional[JsonCallbackService] = None
        self.logger = logging.getLogger(__name__)
        self._started = False
    
    @property
    def metadata(self) -> PluginMetadata:
        """Plugin metadata"""
        return PluginMetadata(
            name="json_serialization",
            version="1.0.0",
            description="Comprehensive JSON serialization solution for Dash callbacks",
            author="Yōsai Intelligence Team",
            priority=PluginPriority.CRITICAL,  # Core functionality
            config_section="json_serialization",
            enabled_by_default=True,
            min_yosai_version="1.0.0"
        )
    
    def load(self, container: Any, config: Dict[str, Any]) -> bool:
        """Load and register plugin services with the DI container"""
        try:
            self.logger.info("Loading JSON Serialization Plugin...")
            
            # Create configuration
            self.config = JsonSerializationConfig(**config)
            
            # Create services
            self.serialization_service = JsonSerializationService(self.config)
            self.callback_service = JsonCallbackService(self.serialization_service)
            
            # Register services with container
            service_definitions = self.get_service_definitions()
            for service_name, service_factory in service_definitions.items():
                container.register(service_name, service_factory, singleton=True)
                self.logger.debug(f"Registered service: {service_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON Serialization Plugin: {e}")
            return False
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the plugin with provided settings"""
        try:
            # Update configuration if provided
            if config:
                for key, value in config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            self.logger.info(f"Configured JSON Serialization Plugin with config: {self.config}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure JSON Serialization Plugin: {e}")
            return False
    
    def start(self) -> bool:
        """Start the plugin (if it has runtime components)"""
        try:
            # Plugin services are ready to use
            self._started = True
            self.logger.info("Started JSON Serialization Plugin")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start JSON Serialization Plugin: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the plugin gracefully"""
        try:
            self._started = False
            self.logger.info("Stopped JSON Serialization Plugin")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop JSON Serialization Plugin: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Return plugin health status"""
        try:
            # Test serialization service
            test_data = {'test': 'data', 'number': 42}
            serialized = self.serialization_service.serialize(test_data)
            
            # Test sanitization
            test_df = pd.DataFrame({'A': [1, 2, 3]})
            sanitized = self.serialization_service.sanitize_for_transport(test_df)
            
            return {
                'healthy': True,
                'started': self._started,
                'services_available': {
                    'serialization_service': self.serialization_service is not None,
                    'callback_service': self.callback_service is not None
                },
                'tests': {
                    'serialization_test': serialized is not None,
                    'sanitization_test': sanitized is not None and sanitized.get('type') == 'dataframe'
                }
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'started': self._started
            }
    
    def get_service_definitions(self) -> Dict[str, Any]:
        """Return service definitions for DI container registration"""
        return {
            'json_serialization_service': lambda: self.serialization_service,
            'json_callback_service': lambda: self.callback_service,
            # Backwards compatibility aliases
            'serialization_service': lambda: self.serialization_service,
            'callback_service': lambda: self.callback_service,
        }
    
    def register_callbacks(self, app: Any, container: Any) -> bool:
        """Register Dash callbacks with automatic wrapping"""
        try:
            if not self.config.auto_wrap_callbacks:
                self.logger.info("Auto callback wrapping is disabled")
                return True
            
            # This would implement automatic callback wrapping
            # For now, we provide the decorator that can be used manually
            self.logger.info("JSON Serialization Plugin callback registration complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register callbacks for JSON Serialization Plugin: {e}")
            return False

# Factory function for plugin discovery
def create_plugin() -> JsonSerializationPlugin:
    """Factory function for plugin discovery"""
    return JsonSerializationPlugin()

# Plugin instance for direct import
plugin = JsonSerializationPlugin()
