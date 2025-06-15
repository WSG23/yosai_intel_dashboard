# models/entities.py
"""
Core entity models for the Yōsai Intel system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .enums import DoorType

@dataclass
class Person:
    """Person/User entity model"""
    person_id: str
    name: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    clearance_level: int = 1
    access_groups: List[str] = field(default_factory=list)
    is_visitor: bool = False
    host_person_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'person_id': self.person_id,
            'name': self.name,
            'employee_id': self.employee_id,
            'department': self.department,
            'clearance_level': self.clearance_level,
            'access_groups': self.access_groups,
            'is_visitor': self.is_visitor,
            'host_person_id': self.host_person_id,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'risk_score': self.risk_score
        }

@dataclass
class Door:
    """Door/Access Point entity model"""
    door_id: str
    door_name: str
    facility_id: str
    area_id: str
    floor: Optional[str] = None
    door_type: DoorType = DoorType.STANDARD
    required_clearance: int = 1
    is_critical: bool = False
    location_coordinates: Optional[Tuple[float, float]] = None
    device_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'door_id': self.door_id,
            'door_name': self.door_name,
            'facility_id': self.facility_id,
            'area_id': self.area_id,
            'floor': self.floor,
            'door_type': self.door_type.value,
            'required_clearance': self.required_clearance,
            'is_critical': self.is_critical,
            'location_coordinates': self.location_coordinates,
            'device_id': self.device_id,
            'is_active': self.is_active,
            'created_at': self.created_at
        }

@dataclass
class Facility:
    """Facility entity model"""
    facility_id: str
    facility_name: str
    campus_id: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "UTC"
    operating_hours: Dict[str, Any] = field(default_factory=dict)
    security_level: int = 1
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'facility_id': self.facility_id,
            'facility_name': self.facility_name,
            'campus_id': self.campus_id,
            'address': self.address,
            'timezone': self.timezone,
            'operating_hours': self.operating_hours,
            'security_level': self.security_level,
            'is_active': self.is_active,
            'created_at': self.created_at
        }