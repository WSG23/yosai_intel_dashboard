"""Utilities for handling file uploads."""

import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

from utils.file_validator import (
    validate_upload_content,
    safe_decode_file,
)
from services.file_processor_service import FileProcessorService

logger = logging.getLogger(__name__)


def parse_uploaded_file(contents: str, filename: str) -> Dict[str, Any]:
    """Parse uploaded file contents into a DataFrame.

    Parameters
    ----------
    contents: str
        Base64 encoded file contents from ``dcc.Upload``.
    filename: str
        Name of the uploaded file.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing ``success`` flag, ``data`` DataFrame when
        successful and additional metadata or an ``error`` message when
        parsing fails.
    """
    validation = validate_upload_content(contents, filename)
    if not validation.get("valid"):
        return {
            "success": False,
            "error": validation.get("error", "Invalid file"),
        }

    decoded = safe_decode_file(contents)
    if decoded is None:
        return {"success": False, "error": "Could not decode file content"}

    processor = FileProcessorService()
    file_validation = processor.validate_file(filename, decoded)
    if not file_validation.get("valid"):
        return {
            "success": False,
            "error": "; ".join(file_validation.get("issues", [])),
        }

    try:
        df = processor.process_file(decoded, filename)
    except Exception as e:  # pragma: no cover - unexpected processing error
        logger.error(f"Error processing uploaded file {filename}: {e}")
        return {"success": False, "error": str(e)}

    if df is None or df.empty:
        return {"success": False, "error": "File contains no data"}

    return {
        "success": True,
        "data": df,
        "rows": len(df),
        "columns": list(df.columns),
        "upload_time": datetime.now(),
    }


def generate_preview(df: pd.DataFrame, filename: str) -> dbc.Card:
    """Create a short HTML preview for an uploaded file."""
    preview_df = df.head(5)
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H6(
                    f"\N{PAGE FACING UP} Data Preview: {filename}", className="mb-0"
                )
            ),
            dbc.CardBody(
                [
                    html.H6("First 5 rows:"),
                    dbc.Table.from_dataframe(
                        preview_df, striped=True, bordered=True, hover=True, size="sm"
                    ),
                    html.Hr(),
                    html.P(
                        [html.Strong("Columns: "), ", ".join(df.columns.tolist()[:10])]
                    ),
                ]
            ),
        ],
        className="mb-3",
    )


def update_upload_state(filename: str, df: pd.DataFrame, store) -> Dict[str, Any]:
    """Update the persistent upload store with a new file."""
    store.add_file(filename, df)
    return {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "upload_time": datetime.now().isoformat(),
    }
