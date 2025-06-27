import json
import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Utility class for loading uploaded analytics data"""

    def combine_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Load and concatenate uploaded files into a single DataFrame"""
        dataframes = []
        for path in file_paths:
            try:
                if path.endswith(".csv"):
                    df = pd.read_csv(path)
                elif path.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(path)
                elif path.endswith(".json"):
                    with open(path, "r") as f:
                        df = pd.DataFrame(json.load(f))
                else:
                    continue
                dataframes.append(df)
            except Exception as exc:
                logger.error(f"Failed to load {path}: {exc}")
        return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()


class StatsCalculator:
    """Generate analytics statistics from dataframes"""

    def basic_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"status": "error", "message": "Empty dataframe"}

        analytics = {
            "status": "success",
            "total_events": len(df),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "summary": {},
        }

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                analytics["summary"][col] = {
                    "type": "numeric",
                    "mean": float(df[col].mean()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "null_count": int(df[col].isnull().sum()),
                }
            else:
                counts = df[col].value_counts().head(10)
                analytics["summary"][col] = {
                    "type": "categorical",
                    "unique_values": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in counts.items()},
                    "null_count": int(df[col].isnull().sum()),
                }
        return analytics

    def sample_analytics(self) -> Dict[str, Any]:
        sample_df = pd.DataFrame(
            {
                "user_id": ["user_001", "user_002", "user_003"] * 100,
                "door_id": ["door_A", "door_B", "door_C"] * 100,
                "timestamp": pd.date_range("2024-01-01", periods=300, freq="1H"),
                "access_result": (["Granted"] * 250) + (["Denied"] * 50),
            }
        )
        return self.basic_analytics(sample_df)


class AnomalyDetector:
    """Basic anomaly detection utilities"""

    def detect_hourly_anomalies(self, df: pd.DataFrame, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        if "timestamp" not in df.columns:
            return []

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(subset=["timestamp"], inplace=True)
        if df.empty:
            return []

        counts = df.groupby(df["timestamp"].dt.floor("H")).size().reset_index(name="event_count")
        if len(counts) < 3:
            return []

        mean = counts["event_count"].mean()
        std = counts["event_count"].std()
        threshold = mean + threshold_multiplier * std
        anomalies = counts[counts["event_count"] > threshold]
        results = []
        for _, row in anomalies.iterrows():
            results.append(
                {
                    "time": row["timestamp"].isoformat(),
                    "event_count": int(row["event_count"]),
                    "severity": "high" if row["event_count"] > threshold * 1.5 else "medium",
                }
            )
        return results
