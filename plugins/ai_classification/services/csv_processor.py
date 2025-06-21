"""Simplified CSV processor using polars"""

import logging
from typing import Dict, Any
from pathlib import Path
import polars as pl

from ..config import CSVProcessingConfig

logger = logging.getLogger(__name__)


class CSVProcessorService:
    def __init__(self, config: CSVProcessingConfig) -> None:
        self.config = config
        self.logger = logger

    def process_file(self, file_path: str, session_id: str, client_id: str) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(file_path)
            df = pl.read_csv(path)
            headers = list(df.columns)
            sample_data = df.head(self.config.sample_size).to_dicts()
            return {
                "success": True,
                "session_id": session_id,
                "file_info": {"name": path.name, "rows": len(df), "columns": len(headers)},
                "headers": headers,
                "sample_data": sample_data,
            }
        except Exception as exc:
            self.logger.error("CSV processing failed: %s", exc)
            return {"success": False, "error": str(exc)}
