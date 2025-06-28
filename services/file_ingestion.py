"""Analytics from uploaded file ingestion."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .analytics_base import AnalyticsModule
from .analytics_computation import generate_basic_analytics

logger = logging.getLogger(__name__)


class FileIngestionAnalytics(AnalyticsModule):
    """Process raw uploaded files and generate analytics."""

    def get_analytics(self) -> Dict[str, Any]:
        """Load uploaded files via FileProcessor and compute analytics."""
        try:
            from pages.file_upload import get_uploaded_filenames
            from services.file_processor import FileProcessor
        except Exception:
            logger.warning("File upload utilities unavailable")
            return {"status": "no_data", "message": "No uploaded files available"}

        uploaded_files = get_uploaded_filenames()
        if not uploaded_files:
            return {"status": "no_data", "message": "No uploaded files available"}

        processor = FileProcessor(upload_folder="temp", allowed_extensions={"csv", "json", "xlsx"})
        all_data: List[pd.DataFrame] = []
        processing_info: List[str] = []
        total_records = 0

        for file_path in uploaded_files:
            try:
                logger.info("Processing uploaded file: %s", file_path)
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(".json"):
                    with open(file_path, "r") as f:
                        json_data = json.load(f)
                    df = pd.DataFrame(json_data)
                elif file_path.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(file_path)
                else:
                    continue

                result = processor._validate_data(df)
                if result["valid"]:
                    processed_df = result.get("data", df)
                    processed_df["source_file"] = file_path
                    all_data.append(processed_df)
                    total_records += len(processed_df)
                    processing_info.append(f"✅ {file_path}: {len(processed_df)} records")
                    logger.info("Processed %s records from %s", len(processed_df), file_path)
                else:
                    error_msg = result.get("error", "Unknown error")
                    processing_info.append(f"❌ {file_path}: {error_msg}")
                    logger.error("Failed to process %s: %s", file_path, error_msg)
            except Exception as exc:
                processing_info.append(f"❌ {file_path}: Exception - {exc}")
                logger.error("Exception processing %s: %s", file_path, exc)

        if not all_data:
            return {
                "status": "error",
                "message": "No files could be processed successfully",
                "processing_info": processing_info,
            }

        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info("Combined data: %s total records", len(combined_df))

        analytics = generate_basic_analytics(combined_df)
        analytics.update(
            {
                "data_source": "uploaded_files_fixed",
                "total_files_processed": len(all_data),
                "total_files_attempted": len(uploaded_files),
                "processing_info": processing_info,
                "total_events": total_records,
                "active_users": combined_df["person_id"].nunique() if "person_id" in combined_df.columns else 0,
                "active_doors": combined_df["door_id"].nunique() if "door_id" in combined_df.columns else 0,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return analytics
