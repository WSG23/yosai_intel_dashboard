"""Simple heuristic floor estimator"""

import logging
from typing import Dict, Any, List

from ..database.csv_storage import CSVStorageRepository
from ..config import FloorEstimationConfig

logger = logging.getLogger(__name__)


class FloorEstimationService:
    def __init__(self, repository: CSVStorageRepository, config: FloorEstimationConfig) -> None:
        self.repository = repository
        self.config = config
        self.logger = logger

    def estimate_floors(self, data: List[Dict], session_id: str) -> Dict[str, Any]:
        locations = [record.get("location", "") for record in data]
        floors = set()
        for loc in locations:
            for token in str(loc).split():
                if token.lower().endswith("f"):
                    try:
                        floors.add(int(token[:-1]))
                    except ValueError:
                        pass
        total_floors = max(floors) if floors else 1
        estimation = {"session_id": session_id, "total_floors": total_floors}
        self.repository.store_floor_estimation(session_id, estimation)
        return {"success": True, "total_floors": total_floors}

