# models/__init__.py - Simplified re-exports for models package
"""Yōsai Intel Data Models Package"""

# Import enums
from .enums import (
    AnomalyType,
    AccessResult,
    BadgeStatus,
    SeverityLevel,
    TicketStatus,
    DoorType,
)

# Import entities
from .entities import Person, Door, Facility

# Import events
from .events import AccessEvent, AnomalyDetection, IncidentTicket

# Import base models
from .base import (
    BaseModel,
    AccessEventModel,
    AnomalyDetectionModel,
    ModelFactory,
)
from config.database_manager import MockDatabaseConnection

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
    'BaseModel',
    'AccessEventModel',
    'AnomalyDetectionModel',
    'ModelFactory',
    'MockDatabaseConnection'
]
