#!/usr/bin/env python3
"""
Fixed File Processor Service - Handles Unicode encoding issues properly
"""
import io
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)


class FileProcessorService:
    """Fixed service for processing uploaded files with proper Unicode handling"""

    ALLOWED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}
    MAX_FILE_SIZE_MB = 100

    def __init__(self):
        """Initialize the file processor service"""
        pass

    def validate_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate uploaded file"""
        issues = []

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            issues.append(
                f"File extension {file_ext} not allowed. "
                f"Allowed: {self.ALLOWED_EXTENSIONS}"
            )

        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            issues.append(
                f"File too large: {size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB"
            )

        # Check for empty file
        if len(content) == 0:
            issues.append("File is empty")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "size_mb": size_mb,
            "extension": file_ext,
        }

    def process_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Process uploaded file and return DataFrame with proper Unicode handling"""
        try:
            file_ext = Path(filename).suffix.lower()

            if file_ext == ".csv":
                return self._process_csv(file_content)
            elif file_ext == ".json":
                return self._process_json(file_content)
            elif file_ext in [".xlsx", ".xls"]:
                return self._process_excel(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise

    def _sanitize_text(self, text: str) -> str:
        """Remove or replace problematic Unicode characters including surrogates"""
        try:
            # Remove surrogate characters that can cause encoding issues
            # Surrogates are in the range U+D800 to U+DFFF
            sanitized = ""
            for char in text:
                code_point = ord(char)
                if 0xD800 <= code_point <= 0xDFFF:
                    # Replace surrogate characters with a safe replacement
                    sanitized += "?"
                else:
                    sanitized += char

            # Ensure the text can be safely encoded as UTF-8
            sanitized.encode("utf-8")
            return sanitized

        except UnicodeEncodeError:
            # If we still have encoding issues, use a more aggressive approach
            return text.encode("utf-8", errors="replace").decode("utf-8")

    def _process_csv(self, content: bytes) -> pd.DataFrame:
        """Process CSV file with proper Unicode handling"""
        logger.info("Processing CSV file...")

        # List of encodings to try in order
        encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                logger.debug(f"Trying encoding: {encoding}")

                # Decode with current encoding
                if encoding == "utf-8":
                    # For UTF-8, use strict error handling first
                    text = content.decode(encoding, errors="strict")
                else:
                    # For other encodings, use replace to handle issues
                    text = content.decode(encoding, errors="replace")

                # Sanitize the text to remove problematic characters
                text = self._sanitize_text(text)

                # Try to parse with pandas
                df = pd.read_csv(io.StringIO(text))

                # Validate that we got reasonable data
                if len(df.columns) > 0 and len(df) > 0:
                    logger.info(f"Successfully parsed CSV with {encoding} encoding")
                    return df

            except UnicodeDecodeError as e:
                logger.debug(f"Encoding {encoding} failed: {e}")
                continue
            except Exception as e:
                logger.debug(f"Parsing with {encoding} failed: {e}")
                continue

        # If all encodings fail, try with error handling
        try:
            logger.warning(
                "All standard encodings failed, using UTF-8 with error replacement"
            )
            text = content.decode("utf-8", errors="replace")
            text = self._sanitize_text(text)
            return pd.read_csv(io.StringIO(text))
        except Exception as e:
            raise ValueError(f"Could not parse CSV file with any encoding method: {e}")

    def _process_json(self, content: bytes) -> pd.DataFrame:
        """Process JSON file with proper Unicode handling"""
        logger.info("Processing JSON file...")

        try:
            # Try UTF-8 first
            text = content.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            # Fallback with error replacement
            text = content.decode("utf-8", errors="replace")
            logger.warning("JSON file had encoding issues, used replacement characters")

        # Sanitize text
        text = self._sanitize_text(text)

        try:
            return pd.read_json(io.StringIO(text))
        except Exception as e:
            raise ValueError(f"Error reading JSON: {e}")

    def _process_excel(self, content: bytes) -> pd.DataFrame:
        """Process Excel file"""
        logger.info("Processing Excel file...")

        try:
            # Excel files are binary, so no encoding issues
            return pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")

    def get_file_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get information about the processed DataFrame"""
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": df.memory_usage(deep=True).sum(),
        }
