"""AI powered column mapping service"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..database.csv_storage import CSVStorageRepository
from ..config import ColumnMappingConfig

logger = logging.getLogger(__name__)


class ColumnMappingService:
    """Suggest mappings from CSV headers to standard fields."""

    STANDARD_FIELDS = {
        "timestamp": ["time", "date", "datetime", "timestamp"],
        "user_id": ["user", "id", "card", "employee"],
        "location": ["location", "door", "room", "area"],
        "access_type": ["access", "type", "action", "entry", "exit"],
    }

    def __init__(self, repository: CSVStorageRepository, config: ColumnMappingConfig) -> None:
        self.repository = repository
        self.config = config
        self.logger = logger

    def map_columns(self, headers: List[str], session_id: str) -> Dict[str, Any]:
        mapping: Dict[str, str] = {}
        confidence: Dict[str, float] = {}

        for header in headers:
            field, score = self._predict_field_type(header)
            if field:
                mapping[header] = field
                confidence[header] = score

        mapping_data = {
            "session_id": session_id,
            "suggested_mapping": mapping,
            "confidence_scores": confidence,
            "status": "pending_confirmation",
            "created_at": datetime.now().isoformat(),
        }
        self.repository.store_column_mapping(session_id, mapping_data)

        return {
            "success": True,
            "suggested_mapping": mapping,
            "confidence_scores": confidence,
            "requires_confirmation": True,
        }

    def confirm_mapping(self, mapping: Dict[str, str], session_id: str) -> bool:
        try:
            confirmed = {
                "session_id": session_id,
                "confirmed_mapping": mapping,
                "status": "confirmed",
                "confirmed_at": datetime.now().isoformat(),
            }
            self.repository.update_column_mapping(session_id, confirmed)
            return True
        except Exception as exc:
            self.logger.error("mapping confirmation failed: %s", exc)
            return False

    def _predict_field_type(self, header: str) -> Tuple[Optional[str], float]:
        h = header.lower()
        best_field = None
        best_score = 0.0

        for field, keywords in self.STANDARD_FIELDS.items():
            for kw in keywords:
                if kw in h:
                    score = len(kw) / len(h)
                    if score > best_score:
                        best_score = score
                        best_field = field
        if best_score < self.config.min_confidence_threshold:
            return None, 0.0
        return best_field, best_score

