"""Analytics helpers for already uploaded data."""

import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .analytics_base import AnalyticsModule

logger = logging.getLogger(__name__)


class UploadedDataAnalytics(AnalyticsModule):
    """Process in-memory uploaded data frames."""

    def process_uploaded_data(self, uploaded_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        try:
            logger.info("Processing %d uploaded files", len(uploaded_data))
            all_dataframes: List[pd.DataFrame] = []
            for filename, df in uploaded_data.items():
                logger.debug("%s: %d rows", filename, len(df))
                df_processed = df.copy()
                if "Person ID" in df_processed.columns:
                    df_processed = df_processed.rename(
                        columns={
                            "Timestamp": "timestamp",
                            "Person ID": "person_id",
                            "Device name": "door_id",
                            "Access result": "access_result",
                        }
                    )
                    logger.debug("Columns mapped for %s", filename)
                all_dataframes.append(df_processed)

            combined_df = pd.concat(all_dataframes, ignore_index=True)
            total_events = len(combined_df)
            active_users = combined_df["person_id"].nunique() if "person_id" in combined_df.columns else 0
            active_doors = combined_df["door_id"].nunique() if "door_id" in combined_df.columns else 0

            date_range = {"start": "Unknown", "end": "Unknown"}
            if "timestamp" in combined_df.columns:
                combined_df["timestamp"] = pd.to_datetime(combined_df["timestamp"], errors="coerce")
                valid = combined_df["timestamp"].dropna()
                if not valid.empty:
                    date_range = {
                        "start": valid.min().strftime("%Y-%m-%d"),
                        "end": valid.max().strftime("%Y-%m-%d"),
                    }
            result = {
                "status": "success",
                "total_events": total_events,
                "active_users": active_users,
                "active_doors": active_doors,
                "unique_users": active_users,
                "unique_doors": active_doors,
                "data_source": "uploaded",
                "date_range": date_range,
                "top_users": (
                    [
                        {"user_id": u, "count": int(c)}
                        for u, c in combined_df["person_id"].value_counts().head(10).items()
                    ]
                    if "person_id" in combined_df.columns
                    else []
                ),
                "top_doors": (
                    [
                        {"door_id": d, "count": int(c)}
                        for d, c in combined_df["door_id"].value_counts().head(10).items()
                    ]
                    if "door_id" in combined_df.columns
                    else []
                ),
                "timestamp": datetime.now().isoformat(),
            }
            return result
        except Exception as exc:
            logger.error("Direct processing failed: %s", exc)
            return {"status": "error", "message": str(exc)}

    def get_analytics(self, uploaded_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        return self.process_uploaded_data(uploaded_data)
