import pandas as pd
from typing import Sequence, Dict, Any, List

# Common column names for fallback mappings
STANDARD_COLUMN_MAPPINGS: Dict[str, str] = {
    "Timestamp": "timestamp",
    "Person ID": "person_id",
    "Token ID": "token_id",
    "Device name": "door_id",
    "Access result": "access_result",
}

# Patterns used for fuzzy column matching
MAPPING_PATTERNS: Dict[str, List[str]] = {
    "person_id": [
        "person id",
        "userid",
        "user id",
        "user",
        "employee",
        "badge",
        "card",
        "person",
        "emp",
        "employee_id",
        "badge_id",
        "card_id",
    ],
    "door_id": [
        "device name",
        "devicename",
        "device_name",
        "door",
        "reader",
        "device",
        "access_point",
        "gate",
        "entry",
        "door_name",
        "reader_id",
        "access_device",
    ],
    "access_result": [
        "access result",
        "accessresult",
        "access_result",
        "result",
        "status",
        "outcome",
        "decision",
        "success",
        "granted",
        "denied",
        "access_status",
    ],
    "timestamp": [
        "timestamp",
        "time",
        "datetime",
        "date",
        "when",
        "occurred",
        "event_time",
        "access_time",
        "date_time",
        "event_date",
    ],
}

REQUIRED_COLUMNS: List[str] = ["person_id", "door_id", "access_result", "timestamp"]

STANDARD_FIELD_OPTIONS = [
    {"label": "Person/User ID", "value": "person_id"},
    {"label": "Door/Location ID", "value": "door_id"},
    {"label": "Timestamp", "value": "timestamp"},
    {"label": "Access Result", "value": "access_result"},
    {"label": "Token/Badge ID", "value": "token_id"},
    {"label": "Badge Status", "value": "badge_status"},
    {"label": "Device Status", "value": "device_status"},
    {"label": "Event Type", "value": "event_type"},
    {"label": "Building/Floor", "value": "building_id"},
    {"label": "Entry/Exit Type", "value": "entry_type"},
    {"label": "Duration", "value": "duration"},
    {"label": "Ignore Column", "value": "ignore"},
    {"label": "Other/Custom", "value": "other"},
]


def fuzzy_match_columns(
    available_columns: Sequence[str],
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
    mapping_patterns: Dict[str, List[str]] = MAPPING_PATTERNS,
) -> Dict[str, str]:
    """Return best matches for required columns from available ones."""
    suggestions: Dict[str, str] = {}
    available_lower = {col.lower(): col for col in available_columns}

    for required_col in required_columns:
        patterns = mapping_patterns.get(required_col, [])
        best_match = None
        for pattern in patterns:
            if pattern.lower() in available_lower:
                best_match = available_lower[pattern.lower()]
                break
        if not best_match:
            for pattern in patterns:
                for col_lower, original in available_lower.items():
                    if pattern in col_lower or col_lower in pattern:
                        best_match = original
                        break
                if best_match:
                    break
        if best_match:
            suggestions[required_col] = best_match
    return suggestions


def apply_manual_mapping(
    df: pd.DataFrame, column_mapping: Dict[str, str]
) -> pd.DataFrame:
    """Rename columns using a user-provided mapping."""
    missing_cols = [src for src in column_mapping.values() if src not in df.columns]
    if missing_cols:
        raise ValueError(f"Source columns not found: {missing_cols}")
    return df.rename(columns={v: k for k, v in column_mapping.items()})


def get_mapping_suggestions(
    df: pd.DataFrame, required_columns: Sequence[str] = REQUIRED_COLUMNS
) -> Dict[str, Any]:
    """Generate mapping suggestions for UI consumption."""
    matches = fuzzy_match_columns(list(df.columns), required_columns)
    return {
        "available_columns": list(df.columns),
        "required_columns": list(required_columns),
        "suggested_mappings": matches,
        "missing_mappings": [col for col in required_columns if col not in matches],
    }


def apply_standard_mappings(
    df: pd.DataFrame, mappings: Dict[str, str] = STANDARD_COLUMN_MAPPINGS
) -> pd.DataFrame:
    """Apply standard column mappings to a DataFrame."""
    return df.rename(columns=mappings)


__all__ = [
    "fuzzy_match_columns",
    "apply_manual_mapping",
    "get_mapping_suggestions",
    "apply_standard_mappings",
    "STANDARD_COLUMN_MAPPINGS",
    "MAPPING_PATTERNS",
    "REQUIRED_COLUMNS",
    "STANDARD_FIELD_OPTIONS",
]
