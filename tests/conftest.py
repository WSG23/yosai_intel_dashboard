"""Test configuration and fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:  # Optional pandas dependency
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - handled via skip in fixtures
    pd = None

class Container:
    """Minimal DI container for tests."""

    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def register(self, name: str, service: object) -> None:
        self._services[name] = service

    def get(self, name: str) -> object | None:
        return self._services.get(name)

    def has(self, name: str) -> bool:
        return name in self._services
from dataclasses import dataclass
from enum import Enum


class AccessResult(Enum):
    GRANTED = "Granted"
    DENIED = "Denied"
    TIMEOUT = "Timeout"
    ERROR = "Error"


class DoorType(Enum):
    STANDARD = "standard"
    CRITICAL = "critical"
    RESTRICTED = "restricted"
    EMERGENCY = "emergency"
    VISITOR = "visitor"


@dataclass
class Person:
    person_id: str
    name: str = ""
    department: str = ""
    clearance_level: int = 1


@dataclass
class Door:
    door_id: str
    door_name: str
    facility_id: str
    area_id: str
    door_type: DoorType
    required_clearance: int | None = None


@dataclass
class AccessEvent:
    person_id: str
    door_id: str
    timestamp: str
    access_result: AccessResult


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests"""

    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def di_container() -> Container:
    """Create DI container for tests"""

    return Container()


@pytest.fixture
def sample_access_data() -> "pd.DataFrame":
    """Sample access data for testing"""

    if pd is None:
        pytest.skip("pandas is required for sample_access_data")

    return pd.DataFrame(
        [
            {
                "person_id": "EMP001",
                "door_id": "MAIN_ENTRANCE",
                "timestamp": "2024-01-15 09:00:00",
                "access_result": AccessResult.GRANTED.value,
            },
            {
                "person_id": "EMP002",
                "door_id": "SERVER_ROOM",
                "timestamp": "2024-01-15 23:00:00",
                "access_result": AccessResult.DENIED.value,
            },
        ]
    )


@pytest.fixture
def sample_persons() -> list[Person]:
    """Sample person entities for testing"""

    return [
        Person(
            person_id="EMP001",
            name="John Doe",
            department="IT",
            clearance_level=3,
        ),
        Person(
            person_id="EMP002",
            name="Jane Smith",
            department="Security",
            clearance_level=5,
        ),
    ]


@pytest.fixture
def sample_doors() -> list[Door]:
    """Sample door entities for testing"""

    return [
        Door(
            door_id="MAIN_ENTRANCE",
            door_name="Main Entrance",
            facility_id="HQ",
            area_id="LOBBY",
            door_type=DoorType.STANDARD,
        ),
        Door(
            door_id="SERVER_ROOM",
            door_name="Server Room",
            facility_id="HQ",
            area_id="IT_FLOOR",
            door_type=DoorType.CRITICAL,
            required_clearance=4,
        ),
    ]

