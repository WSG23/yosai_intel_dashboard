"""Utilities for ingesting uploaded data and applying mappings."""

from __future__ import annotations

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

import pandas as pd

from utils import apply_standard_mappings

logger = logging.getLogger(__name__)


class AnalyticsDataAccessor:
    """Load uploaded files and apply learned mappings."""

    def __init__(self, base_data_path: str = "data") -> None:
        self.base_path = Path(base_data_path)
        self.mappings_file = self.base_path / "learned_mappings.pkl"
        self.session_storage = self.base_path.parent / "session_storage"

    def get_processed_database(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Return combined dataframe and metadata using stored mappings."""
        mappings_data = self._load_consolidated_mappings()
        uploaded_data = self._get_uploaded_data()

        if not uploaded_data:
            return pd.DataFrame(), {}

        combined_df, metadata = self._apply_mappings_and_combine(uploaded_data, mappings_data)
        return combined_df, metadata

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_consolidated_mappings(self) -> Dict[str, Any]:
        """Load consolidated mappings from ``learned_mappings.pkl`` if present."""
        try:
            if self.mappings_file.exists():
                with open(self.mappings_file, "rb") as f:
                    return pickle.load(f)
            return {}
        except Exception as exc:  # pragma: no cover - log errors
            logger.error("Error loading mappings: %s", exc)
            return {}

    def _get_uploaded_data(self) -> Dict[str, pd.DataFrame]:
        """Retrieve uploaded data frames from ``pages.file_upload``."""
        try:
            from pages.file_upload import get_uploaded_data

            uploaded_data = get_uploaded_data()
            if uploaded_data:
                return uploaded_data
            return {}
        except Exception:  # pragma: no cover - import failure
            return {}

    def _apply_mappings_and_combine(
        self, uploaded_data: Dict[str, pd.DataFrame], mappings_data: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Apply column/device mappings to uploaded data and concatenate."""
        combined_dfs = []
        metadata = {
            "total_files": len(uploaded_data),
            "processed_files": 0,
            "total_records": 0,
            "unique_users": set(),
            "unique_devices": set(),
            "date_range": {"start": None, "end": None},
        }

        for filename, df in uploaded_data.items():
            try:
                mapped_df = self._apply_column_mappings(df, filename, mappings_data)
                enriched_df = self._apply_device_mappings(mapped_df, filename, mappings_data)

                enriched_df["source_file"] = filename
                enriched_df["processed_at"] = datetime.now()

                combined_dfs.append(enriched_df)
                metadata["processed_files"] += 1
                metadata["total_records"] += len(enriched_df)

                if "person_id" in enriched_df.columns:
                    metadata["unique_users"].update(enriched_df["person_id"].dropna().unique())
                if "door_id" in enriched_df.columns:
                    metadata["unique_devices"].update(enriched_df["door_id"].dropna().unique())

                if "timestamp" in enriched_df.columns:
                    dates = pd.to_datetime(enriched_df["timestamp"], errors="coerce").dropna()
                    if len(dates) > 0:
                        if metadata["date_range"]["start"] is None:
                            metadata["date_range"]["start"] = dates.min()
                            metadata["date_range"]["end"] = dates.max()
                        else:
                            metadata["date_range"]["start"] = min(metadata["date_range"]["start"], dates.min())
                            metadata["date_range"]["end"] = max(metadata["date_range"]["end"], dates.max())
            except Exception as exc:  # pragma: no cover - log and continue
                logger.error("Error processing %s: %s", filename, exc)
                continue

        if combined_dfs:
            final_df = pd.concat(combined_dfs, ignore_index=True)
            metadata["unique_users"] = len(metadata["unique_users"])
            metadata["unique_devices"] = len(metadata["unique_devices"])
            return final_df, metadata

        return pd.DataFrame(), metadata

    def _apply_column_mappings(
        self, df: pd.DataFrame, filename: str, mappings_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """Rename columns using learned mappings or fall back to defaults."""
        for fingerprint, mapping_info in mappings_data.items():
            if mapping_info.get("filename") == filename:
                column_mappings = mapping_info.get("column_mappings", {})
                if column_mappings:
                    return df.rename(columns=column_mappings)
        return apply_standard_mappings(df)

    def _apply_device_mappings(
        self, df: pd.DataFrame, filename: str, mappings_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """Attach learned device attributes to the dataframe."""
        if "door_id" not in df.columns:
            return df

        device_mappings = {}
        for fingerprint, mapping_info in mappings_data.items():
            if mapping_info.get("filename") == filename:
                device_mappings = mapping_info.get("device_mappings", {})
                break

        if not device_mappings:
            return df

        device_attrs_df = pd.DataFrame.from_dict(device_mappings, orient="index")
        device_attrs_df.index.name = "door_id"
        device_attrs_df.reset_index(inplace=True)

        return df.merge(device_attrs_df, on="door_id", how="left")

__all__ = ["AnalyticsDataAccessor"]
