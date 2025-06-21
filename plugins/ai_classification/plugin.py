"""AI Classification Plugin (simplified)"""

import logging
from typing import Optional, Dict, Any, List

from .config import AIClassificationConfig, get_ai_config

from .services.csv_processor import CSVProcessorService
from .services.column_mapper import ColumnMappingService
from .services.floor_estimator import FloorEstimationService

logger = logging.getLogger(__name__)


class AIClassificationPlugin:
    """Simplified plugin implementing CSV related services"""

    def __init__(self, config: Optional[AIClassificationConfig] = None) -> None:
        self.config = config or get_ai_config()
        self.is_started = False
        self.csv_processor: Optional[CSVProcessorService] = None
        self.column_mapper: Optional[ColumnMappingService] = None
        self.floor_estimator: Optional[FloorEstimationService] = None
        self.services: Dict[str, Any] = {}

    def start(self) -> bool:
        if self.is_started:
            logger.warning("plugin already started")
            return True
        try:
            self.csv_processor = CSVProcessorService(self.config.csv_processing)
            self.column_mapper = ColumnMappingService(self.config.column_mapping)
            self.floor_estimator = FloorEstimationService(self.config.floor_estimation)
            self._register_services()
            self.is_started = True
            logger.info("AIClassification plugin started")
            return True
        except Exception as exc:
            logger.error("failed to start plugin: %s", exc)
            return False

    def _register_services(self) -> None:
        self.services = {
            "process_csv": self.process_csv_file,
            "map_columns": self.map_columns,
            "estimate_floors": self.estimate_floors,
        }

    # Service wrappers
    def process_csv_file(self, file_path: str, session_id: str, client_id: str = "default") -> Dict[str, Any]:
        if not self.csv_processor:
            raise RuntimeError("service not started")
        return self.csv_processor.process_file(file_path, session_id, client_id)

    def map_columns(self, headers: List[str], session_id: str) -> Dict[str, Any]:
        if not self.column_mapper:
            raise RuntimeError("service not started")
        return self.column_mapper.map_columns(headers, session_id)

    def estimate_floors(self, data: List[Dict], session_id: str) -> Dict[str, Any]:
        if not self.floor_estimator:
            raise RuntimeError("service not started")
        return self.floor_estimator.estimate_floors(data, session_id)
