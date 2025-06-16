# models/__init__.py - Fixed imports to resolve Pylance errors
"""
Yōsai Intel Data Models Package - Type-safe and Modular
"""

# Import enums
from .enums import (
    AnomalyType,
    AccessResult, 
    BadgeStatus,
    SeverityLevel,
    TicketStatus,
    DoorType
)

# Import entities  
from .entities import (
    Person,
    Door, 
    Facility
)

# Import events
from .events import (
    AccessEvent,
    AnomalyDetection,
    IncidentTicket
)

# Import base models (fixed to use the new base.py structure)
from .base import (
    BaseModel,
    AccessEventModel,
    AnomalyDetectionModel,
    ModelFactory,
    MockDatabaseConnection
)

# Define what gets exported when someone does "from models import *"
__all__ = [
    # Enums
    'AnomalyType', 'AccessResult', 'BadgeStatus', 'SeverityLevel', 
    'TicketStatus', 'DoorType',
    
    # Entities
    'Person', 'Door', 'Facility',
    
    # Events
    'AccessEvent', 'AnomalyDetection', 'IncidentTicket',
    
    # Models (new structure)
    'BaseModel', 'AccessEventModel', 'AnomalyDetectionModel',
    
    # Factory and utilities
    'ModelFactory', 'MockDatabaseConnection'
]

# Package metadata
__version__ = "2.0.0"
__author__ = "Yōsai Intel Team"
__description__ = "Type-safe, modular data models for security intelligence"
