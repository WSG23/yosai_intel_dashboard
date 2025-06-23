"""Service interfaces using Python 3.8+ Protocol for better type safety"""
from typing import Protocol, List, Dict, Any
import pandas as pd
from models.entities import Person, Door, AccessEvent

class AnalyticsServiceProtocol(Protocol):
    """Analytics service protocol for dependency injection"""

    def analyze_access_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        ...

    def detect_anomalies(self, events: List[AccessEvent]) -> List[Dict[str, Any]]:
        ...

    def generate_insights(self, timeframe: str) -> Dict[str, Any]:
        ...

class FileProcessorProtocol(Protocol):
    """File processing protocol"""

    def process_upload(self, file_content: bytes, filename: str) -> pd.DataFrame:
        ...

    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        ...
