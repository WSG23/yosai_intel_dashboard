from abc import ABC, abstractmethod
from typing import Any, Dict


class AnalyticsModule(ABC):
    """Interface for analytics modules."""

    @abstractmethod
    def get_analytics(self, *args, **kwargs) -> Dict[str, Any]:
        """Return analytics results"""
        raise NotImplementedError
