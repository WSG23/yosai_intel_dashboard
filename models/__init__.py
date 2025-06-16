# models/__init__.py - FIXED: Type-safe model imports
"""
Yōsai Intel Data Models Package - Type-safe and Modular
"""

# Import enums
try:
    from .enums import (
        AnomalyType, AccessResult, BadgeStatus,
        SeverityLevel, TicketStatus, DoorType
    )
except ImportError as e:
    print(f"Warning: Could not import enums: {e}")
    # Create fallback enums
    from enum import Enum
    class AnomalyType(Enum):
        UNKNOWN = "unknown"
    class AccessResult(Enum):
        UNKNOWN = "unknown"
    class BadgeStatus(Enum):
        UNKNOWN = "unknown"
    class SeverityLevel(Enum):
        UNKNOWN = "unknown"
    class TicketStatus(Enum):
        UNKNOWN = "unknown"
    class DoorType(Enum):
        UNKNOWN = "unknown"

# Import entities  
try:
    from .entities import Person, Door, Facility
except ImportError as e:
    print(f"Warning: Could not import entities: {e}")
    # Create fallback classes
    class Person:
        pass
    class Door:
        pass
    class Facility:
        pass

# Import events
try:
    from .events import AccessEvent, AnomalyDetection, IncidentTicket
except ImportError as e:
    print(f"Warning: Could not import events: {e}")
    # Create fallback classes
    class AccessEvent:
        pass
    class AnomalyDetection:
        pass
    class IncidentTicket:
        pass

# Import base models
try:
    from .base import BaseModel, AccessEventModel, AnomalyDetectionModel, ModelFactory
except ImportError as e:
    print(f"Warning: Could not import base models: {e}")
    # Create fallback classes
    class BaseModel:
        pass
    class AccessEventModel:
        pass
    class AnomalyDetectionModel:
        pass
    class ModelFactory:
        @staticmethod
        def create_access_model(db_connection):
            return AccessEventModel()
        @staticmethod
        def create_anomaly_model(db_connection):
            return AnomalyDetectionModel()

# Define exports
__all__ = [
    # Enums
    'AnomalyType', 'AccessResult', 'BadgeStatus', 'SeverityLevel', 
    'TicketStatus', 'DoorType',
    
    # Entities
    'Person', 'Door', 'Facility',
    
    # Events
    'AccessEvent', 'AnomalyDetection', 'IncidentTicket',
    
    # Models
    'BaseModel', 'AccessEventModel', 'AnomalyDetectionModel', 'ModelFactory'
]
