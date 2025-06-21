"""Simple column mapping service"""

import logging
from typing import Dict, Any, List

from ..config import ColumnMappingConfig

logger = logging.getLogger(__name__)


class ColumnMappingService:
    STANDARD_FIELDS = {
        "timestamp": ["time", "date", "timestamp"],
        "user_id": ["user", "id", "card"],
        "location": ["location", "door", "room"],
        "access_type": ["access", "type", "action"],
    }

    def __init__(self, config: ColumnMappingConfig) -> None:
        self.config = config
        self.logger = logger

    def map_columns(self, headers: List[str], session_id: str) -> Dict[str, Any]:
        mapping: Dict[str, str] = {}
        for header in headers:
            h = header.lower()
            for field, keywords in self.STANDARD_FIELDS.items():
                if any(k in h for k in keywords):
                    mapping[header] = field
                    break
        return {"success": True, "suggested_mapping": mapping, "requires_confirmation": True}
