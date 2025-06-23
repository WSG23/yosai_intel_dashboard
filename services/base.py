"""
Base service interfaces using protocols
"""
from typing import Protocol, List, Dict, Any, Optional
import pandas as pd
from dataclasses import dataclass


@dataclass
class ServiceResult:
    """Standard result type for service operations"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    warnings: List[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


class AnalyticsServiceProtocol(Protocol):
    """Analytics service protocol"""

    def analyze_data(self, data: pd.DataFrame) -> ServiceResult:
        """Analyze DataFrame and return insights"""
        ...

    def detect_anomalies(self, data: pd.DataFrame) -> ServiceResult:
        """Detect anomalies in access data"""
        ...


class FileServiceProtocol(Protocol):
    """File processing service protocol"""

    def process_file(self, content: bytes, filename: str) -> ServiceResult:
        """Process uploaded file content"""
        ...

    def validate_data(self, data: pd.DataFrame) -> ServiceResult:
        """Validate processed data"""
        ...
