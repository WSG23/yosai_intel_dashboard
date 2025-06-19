# core/protocols.py
"""
Protocol-oriented architecture inspired by Swift's approach
Defines clear contracts for all major system components
"""
from typing import Protocol, Dict, Any, Optional, List, Callable
from abc import abstractmethod
import pandas as pd
from datetime import datetime

class DatabaseProtocol(Protocol):
    """Protocol defining database operations contract"""
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame"""
        ...
    
    @abstractmethod
    def execute_command(self, command: str, params: Optional[tuple] = None) -> None:
        """Execute a command (INSERT, UPDATE, DELETE)"""
        ...
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify database connectivity"""
        ...

class AnalyticsServiceProtocol(Protocol):
    """Protocol for analytics service operations"""
    
    @abstractmethod
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get main dashboard summary statistics"""
        ...
    
    @abstractmethod
    def analyze_access_patterns(self, days: int) -> Dict[str, Any]:
        """Analyze access patterns over specified days"""
        ...
    
    @abstractmethod
    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in access data"""
        ...

class FileProcessorProtocol(Protocol):
    """Protocol for file processing operations"""
    
    @abstractmethod
    def validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file"""
        ...
    
    @abstractmethod
    def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded file and return structured data"""
        ...

class ConfigurationProtocol(Protocol):
    """Protocol for configuration management"""
    
    @abstractmethod
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        ...
    
    @abstractmethod
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        ...
    
    @abstractmethod
    def reload_configuration(self) -> None:
        """Reload configuration from source"""
        ...


class SerializationProtocol(Protocol):
    """Protocol for JSON serialization services"""

    @abstractmethod
    def serialize(self, data: Any) -> str:
        """Serialize data to a JSON string"""
        ...

    @abstractmethod
    def sanitize_for_transport(self, data: Any) -> Any:
        """Prepare data for network transport"""
        ...

    @abstractmethod
    def is_serializable(self, data: Any) -> bool:
        """Check if the given data can be serialized"""
        ...


class CallbackProtocol(Protocol):
    """Protocol for services that wrap and validate callbacks"""

    @abstractmethod
    def wrap_callback(self, callback_func: Callable) -> Callable:
        """Return a wrapped, safe callback function"""
        ...

    @abstractmethod
    def validate_callback_output(self, output: Any) -> Any:
        """Validate and sanitize callback output"""
        ...

# core/dependency_container.py
"""
Dependency injection container with protocol-based registration
"""
from typing import TypeVar, Type, Dict, Any, Callable
import logging

T = TypeVar('T')

class DependencyContainer:
    """
    Lightweight dependency injection container
    Inspired by Apple's approach to dependency management
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_singleton(self, protocol: Type[T], implementation: T, name: str = None) -> None:
        """Register a singleton service"""
        key = name or protocol.__name__
        self._singletons[key] = implementation
        self.logger.info(f"Registered singleton: {key}")
    
    def register_factory(self, protocol: Type[T], factory: Callable[[], T], name: str = None) -> None:
        """Register a factory for creating instances"""
        key = name or protocol.__name__
        self._factories[key] = factory
        self.logger.info(f"Registered factory: {key}")
    
    def get(self, protocol: Type[T], name: str = None) -> T:
        """Get service instance"""
        key = name or protocol.__name__
        
        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]
        
        # Check factories
        if key in self._factories:
            instance = self._factories[key]()
            return instance
        
        raise ValueError(f"Service not registered: {key}")
    
    def get_optional(self, protocol: Type[T], name: str = None) -> Optional[T]:
        """Get service instance or None if not registered"""
        try:
            return self.get(protocol, name)
        except ValueError:
            return None
    
    def verify_container(self) -> Dict[str, bool]:
        """Verify all registered services can be created"""
        results = {}
        
        for name in self._singletons:
            try:
                service = self._singletons[name]
                results[name] = service is not None
            except Exception as e:
                self.logger.error(f"Singleton verification failed for {name}: {e}")
                results[name] = False
        
        for name in self._factories:
            try:
                service = self._factories[name]()
                results[name] = service is not None
            except Exception as e:
                self.logger.error(f"Factory verification failed for {name}: {e}")
                results[name] = False
        
        return results

# Global container instance
container = DependencyContainer()

def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    return container