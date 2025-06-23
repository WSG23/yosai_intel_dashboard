"""Service protocols and result types"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any, Dict, List, Optional

import pandas as pd


@dataclass
class ServiceResult:
    """Standard result from service operations."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


class DatabaseProtocol(Protocol):
    """Database service protocol."""

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute database query and return DataFrame."""
        ...

    def close(self) -> None:
        """Close database connection."""
        ...


class AnalyticsProtocol(Protocol):
    """Analytics service protocol."""

    def analyze_access_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze access patterns in DataFrame."""
        ...

    def detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in access events."""
        ...


class FileProcessorProtocol(Protocol):
    """File processor service protocol."""

    def process_upload(self, content: bytes, filename: str) -> pd.DataFrame:
        """Process uploaded file content."""
        ...

    def validate_data(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate processed data structure."""
        ...
