"""Analytics computation helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

import pandas as pd


def generate_basic_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """Return simple summary statistics for ``df``."""
    analytics = {
        "status": "success",
        "total_events": len(df),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "summary": {},
        "timestamp": datetime.now().isoformat(),
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
            value_counts = df[col].value_counts().head(10)
            analytics["summary"][col] = {
                "type": "categorical",
                "unique_values": int(df[col].nunique()),
                "top_values": {str(k): int(v) for k, v in value_counts.items()},
                "null_count": int(df[col].isnull().sum()),
            }
    return analytics


def generate_sample_analytics() -> Dict[str, Any]:
    """Create a small sample dataset and analyse it."""
    sample_data = pd.DataFrame(
        {
            "user_id": ["user_001", "user_002", "user_003"] * 100,
            "door_id": ["door_A", "door_B", "door_C"] * 100,
            "timestamp": pd.date_range("2024-01-01", periods=300, freq="1H"),
            "access_result": (["Granted"] * 250) + (["Denied"] * 50),
        }
    )
    return generate_basic_analytics(sample_data)

__all__ = ["generate_basic_analytics", "generate_sample_analytics"]
