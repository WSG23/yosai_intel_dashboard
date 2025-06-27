"""
Simple file validation utilities
"""

import pandas as pd
import io
import base64
from typing import Dict, Any, Optional, Tuple
from services.file_processor_service import FileProcessorService


def validate_upload_content(contents: str, filename: str) -> Dict[str, Any]:
    """Validate uploaded file content"""

    # Basic validation
    if not contents or not filename:
        return {"valid": False, "error": "Missing file content or filename"}

    # Check if contents is properly formatted
    if not contents.startswith("data:"):
        return {"valid": False, "error": "Invalid file format - not a data URL"}

    if "," not in contents:
        return {"valid": False, "error": "Invalid file format - missing data separator"}

    # Check file extension
    allowed_extensions = {".csv", ".json", ".xlsx", ".xls"}
    file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if file_ext not in allowed_extensions:
        return {
            "valid": False,
            "error": f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}",
        }

    return {"valid": True, "extension": file_ext}


def safe_decode_file(contents: str) -> Optional[bytes]:
    """Safely decode base64 file contents"""
    try:
        # Split the data URL
        if "," not in contents:
            return None

        content_type, content_string = contents.split(",", 1)

        # Decode base64
        decoded = base64.b64decode(content_string)
        return decoded

    except Exception:
        return None


def process_dataframe(
    decoded: bytes, filename: str
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Process decoded bytes into DataFrame using :class:`FileProcessorService`."""
    processor = FileProcessorService()
    try:
        file_validation = processor.validate_file(filename, decoded)
        if not file_validation.get("valid"):
            return None, "; ".join(file_validation.get("issues", []))

        df = processor.process_file(decoded, filename)
        return df, None
    except Exception as e:  # pragma: no cover - unexpected processing error
        return None, f"Error processing file: {str(e)}"
