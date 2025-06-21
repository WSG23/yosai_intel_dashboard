"""Service interfaces for dependency injection"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd

from models.entities import Person, Door, AccessEvent


class IAnalyticsService(ABC):
    """Analytics service interface"""

    @abstractmethod
    def analyze_access_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        pass

    @abstractmethod
    def detect_anomalies(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def generate_insights(self, timeframe: str) -> Dict[str, Any]:
        pass


class IFileProcessorService(ABC):
    """File processing service interface"""

    @abstractmethod
    def process_upload(self, file_content: str, filename: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        pass


class ISecurityService(ABC):
    """Security service interface"""

    @abstractmethod
    def assess_risk_score(self, person: Person) -> float:
        pass

    @abstractmethod
    def check_access_permission(self, person_id: str, door_id: str) -> bool:
        pass

