# core/json_serialization_plugin.py - FIXED: Removed non-existent imports
"""
JSON Serialization Plugin - FIXED: Comprehensive LazyString handling
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
    from flask_babel import LazyString
    BABEL_AVAILABLE = True
except ImportError:
    LazyString = None
    BABEL_AVAILABLE = False

from core.plugins.protocols import (
    PluginProtocol, PluginMetadata, PluginPriority,
    ServicePluginProtocol, CallbackPluginProtocol
)

# Import error handling safely
try:
    from core.error_handling import (
        with_error_handling,
        ErrorCategory,
        ErrorSeverity,
    )
except ImportError:  # pragma: no cover - fallback for missing module
    from enum import Enum
    from typing import Any, Callable, TypeVar

    F = TypeVar("F", bound=Callable[..., Any])

    class ErrorCategory(str, Enum):
        DATABASE = "database"
        FILE_PROCESSING = "file_processing"
        AUTHENTICATION = "authentication"
        ANALYTICS = "analytics"
        CONFIGURATION = "configuration"
        EXTERNAL_API = "external_api"
        USER_INPUT = "user_input"

    class ErrorSeverity(str, Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    def with_error_handling(
        category: ErrorCategory = ErrorCategory.ANALYTICS,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        reraise: bool = False,
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            return func

        return decorator

# Import performance monitoring safely  
try:
    from core.performance import measure_performance, MetricType
except ImportError:  # pragma: no cover - fallback for missing module
    from typing import Callable, TypeVar

    F = TypeVar("F", bound=Callable[..., Any])

    def measure_performance(
        name: str | None = None,
        metric_type: "MetricType" = MetricType.EXECUTION_TIME,
        threshold: float | None = None,
        tags: dict[str, str] | None = None,
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            return func

        return decorator

    class MetricType(str, Enum):
        EXECUTION_TIME = "execution_time"
        SERIALIZATION = "serialization"
        CALLBACK = "callback"

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
    """Yōsai-specific JSON encoder with comprehensive LazyString support"""
    
    def __init__(self, config: JsonSerializationConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def default(self, o: Any) -> Any:
        """Handle all Yōsai-specific types with comprehensive error boundaries"""

        # COMPREHENSIVE LAZYSTRING HANDLING
        if self._is_lazystring(o):
            return self._handle_lazystring(o)

        # Handle pandas DataFrames
        if isinstance(o, pd.DataFrame):
            return self._encode_dataframe(o)

        # Handle pandas Series
        if isinstance(o, pd.Series):
            return self._encode_series(o)

        # Handle numpy types
        if hasattr(o, 'dtype') and hasattr(o, 'tolist'):
            try:
                return o.tolist()
            except Exception:
                return str(o)

        # Handle datetime objects
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        # Handle dataclasses
        if is_dataclass(o):
            return self._encode_dataclass(o)

        # Handle callable objects
        if callable(o):
            return self._encode_callable(o)

        # Handle complex objects
        if hasattr(o, '__dict__'):
            return self._encode_complex_object(o)

        # Handle numpy scalars
        if hasattr(o, 'item'):
            try:
                return o.item()
            except Exception:
                return str(o)

        # Fallback to string representation
        if self.config.fallback_to_repr:
            return str(o)

        # Let the parent handle it (may raise TypeError)
        return super().default(o)
    
    def _is_lazystring(self, obj: Any) -> bool:
        """Comprehensive LazyString detection"""
        # Direct instance check
        if BABEL_AVAILABLE and LazyString is not None and isinstance(obj, LazyString):
            return True
        
        # Class name check (works across Babel versions)
        class_name = str(obj.__class__)
        if 'LazyString' in class_name or 'lazy_string' in class_name.lower():
            return True
        
        # Duck typing check for lazy evaluation pattern
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            return True
        
        return False
    
    def _handle_lazystring(self, obj: Any) -> str:
        """Safely convert LazyString to regular string"""
        try:
            return str(obj)
        except Exception as e:
            logger.warning(f"LazyString conversion failed: {e}")
            return f"<LazyString conversion failed: {repr(obj)[:50]}>"
    
    def _encode_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Safely encode DataFrame with size limits"""
        try:
            rows_to_include = min(len(df), self.config.max_dataframe_rows)
            
            return {
                '__type__': 'dataframe',
                '__shape__': df.shape,
                '__columns__': list(df.columns),
                '__data__': df.head(rows_to_include).to_dict('records'),
                '__truncated__': len(df) > self.config.max_dataframe_rows,
                '__dtypes__': {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        except Exception as e:
            return {
                '__type__': 'dataframe',
                '__error__': f'DataFrame encoding failed: {str(e)}',
                '__shape__': getattr(df, 'shape', 'unknown')
            }
    
    def _encode_series(self, series: pd.Series) -> Dict[str, Any]:
        """Safely encode pandas Series"""
        try:
            return {
                '__type__': 'series',
                '__name__': series.name,
                '__length__': len(series),
                '__data__': series.head(100).to_dict(),
                '__dtype__': str(series.dtype)
            }
        except Exception as e:
            return {
                '__type__': 'series',
                '__error__': f'Series encoding failed: {str(e)}'
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
        
        try:
            for key, value in obj.__dict__.items():
                try:
                    # Test if value is JSON serializable
                    json.dumps(value, cls=YosaiJSONEncoder, config=self.config)
                    safe_dict[key] = value
                except (TypeError, ValueError):
                    # Replace with safe representation
                    if self._is_lazystring(value):
                        safe_dict[key] = self._handle_lazystring(value)
                    else:
                        safe_dict[f"{key}__type"] = type(value).__name__
            
            return {
                '__type__': 'object',
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                '__dict__': safe_dict
            }
        except Exception as e:
            return {
                '__type__': 'object',
                '__class__': obj.__class__.__name__,
                '__error__': f'Object encoding failed: {str(e)}'
            }

class JsonSerializationService:
    """JSON serialization service implementation with comprehensive LazyString support"""
    
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
            # Return safe fallback JSON
            return json.dumps({
                'error': True,
                'message': str(e),
                'type': type(data).__name__,
                'fallback_repr': str(data)[:200]
            })
    
    @measure_performance("serialization.sanitize", MetricType.SERIALIZATION)
    def sanitize_for_transport(self, data: Any) -> Any:
        """Sanitize data specifically for Dash callback transport"""

        if data is None:
            return None

        # Handle LazyString objects FIRST
        if self.encoder._is_lazystring(data):
            return self.encoder._handle_lazystring(data)

        # Handle DataFrames - convert to transport-safe format
        if isinstance(data, pd.DataFrame):
            return self._sanitize_dataframe(data)

        # Handle functions - return metadata only
        if callable(data):
            return self._sanitize_callable(data)

        # Handle lists recursively
        if isinstance(data, list):
            return [self.sanitize_for_transport(item) for item in data]

        # Handle tuples recursively
        if isinstance(data, tuple):
            return tuple(self.sanitize_for_transport(item) for item in data)

        # Handle dictionaries recursively
        if isinstance(data, dict):
            sanitized_dict = {}
            for key, value in data.items():
                # Ensure keys are strings
                safe_key = str(key) if not isinstance(key, str) else key
                sanitized_dict[safe_key] = self.sanitize_for_transport(value)
            return sanitized_dict

        # Handle objects with attributes
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
        try:
            rows_to_include = min(len(df), self.config.max_dataframe_rows)
            
            return {
                'type': 'dataframe',
                'shape': df.shape,
                'columns': list(df.columns),
                'data': df.head(rows_to_include).to_dict('records'),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'truncated': len(df) > self.config.max_dataframe_rows
            }
        except Exception as e:
            return {
                'type': 'dataframe',
                'error': f'DataFrame sanitization failed: {str(e)}'
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
    """JSON Serialization Plugin - FIXED: Comprehensive LazyString solution"""
    
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
            version="1.1.0",  # Updated version
            description="Comprehensive JSON serialization solution with LazyString support",
            author="Yōsai Intelligence Team",
            priority=PluginPriority.CRITICAL,
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
                try:
                    container.register(service_name, service_factory, singleton=True)
                    self.logger.debug(f"Registered service: {service_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to register service {service_name}: {e}")
            
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
        """Start the plugin and apply global JSON patches"""
        try:
            # Apply global JSON patch for comprehensive coverage
            self._apply_global_json_patch()
            
            self._started = True
            self.logger.info("Started JSON Serialization Plugin with global patches")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start JSON Serialization Plugin: {e}")
            return False
    
    def _apply_global_json_patch(self):
        """Apply global JSON patch for ultimate LazyString protection"""
        import json
        
        # Store original dumps
        if not hasattr(json, '_yosai_original_dumps'):
            setattr(json, '_yosai_original_dumps', json.dumps)
        
        # Create safe dumps function
        def safe_dumps(obj, **kwargs):
            # Use our plugin's encoder if available
            if self.serialization_service:
                try:
                    return self.serialization_service.serialize(obj)
                except Exception:
                    # Fallback to original with safe default
                    pass
            
            # Fallback: use safe default encoder
            def safe_default(o):
                if hasattr(o, '__class__') and 'LazyString' in str(o.__class__):
                    return str(o)
                if hasattr(o, '_func') and hasattr(o, '_args'):
                    return str(o)
                if callable(o):
                    return f"<function {getattr(o, '__name__', 'anonymous')}>"
                return str(o)
            
            if 'default' not in kwargs:
                kwargs['default'] = safe_default
            
            original = getattr(json, '_yosai_original_dumps')
            return original(obj, **kwargs)
        
        # Apply the patch
        json.dumps = safe_dumps
        self.logger.info("Applied global JSON.dumps patch")
    
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
            # Test basic serialization
            assert self.serialization_service is not None
            test_data = {'test': 'data', 'number': 42}
            serialized = self.serialization_service.serialize(test_data)
            
            # Test LazyString handling if available
            lazystring_test = True
            if BABEL_AVAILABLE:
                try:
                    from flask_babel import lazy_gettext as _l
                    lazy_test = _l("test")
                    sanitized = self.serialization_service.sanitize_for_transport(lazy_test)
                    assert isinstance(sanitized, str)
                except Exception:
                    lazystring_test = False
            
            return {
                'healthy': True,
                'started': self._started,
                'services_available': {
                    'serialization_service': self.serialization_service is not None,
                    'callback_service': self.callback_service is not None
                },
                'tests': {
                    'basic_serialization': serialized is not None,
                    'lazystring_handling': lazystring_test
                },
                'babel_available': BABEL_AVAILABLE
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
            assert self.config is not None
            if not self.config.auto_wrap_callbacks:
                self.logger.info("Auto callback wrapping is disabled")
                return True
            
            # Store plugin reference in app for decorators to use
            app._yosai_json_plugin = self
            
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
