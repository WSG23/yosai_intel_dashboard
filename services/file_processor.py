# services/file_processor.py
import pandas as pd
import json
import os
import uuid
from typing import Dict, Any, Optional, Tuple, Sequence
import logging
from datetime import datetime

from utils import (
    fuzzy_match_columns,
    apply_manual_mapping as util_apply_manual_mapping,
    get_mapping_suggestions as util_get_mapping_suggestions,
)


class FileProcessor:
    """Service for processing uploaded files"""

    def __init__(self, upload_folder: str, allowed_extensions: set):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions

        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)

    def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process uploaded file and return parsed data"""

        if not self._is_allowed_file(filename):
            return {
                "success": False,
                "error": f"File type not allowed. Allowed: {self.allowed_extensions}",
            }

        try:
            # Save file temporarily
            file_id = str(uuid.uuid4())
            file_path = os.path.join(self.upload_folder, f"{file_id}_{filename}")

            with open(file_path, "wb") as f:
                f.write(file_content)

            # Parse based on file type
            file_ext = filename.rsplit(".", 1)[1].lower()

            if file_ext == "csv":
                df = self._parse_csv(file_path)
            elif file_ext == "json":
                df = self._parse_json(file_path)
            elif file_ext in ["xlsx", "xls"]:
                df = self._parse_excel(file_path)
            else:
                return {"success": False, "error": "Unsupported file type"}

            # Validate and clean data
            validation_result = self._validate_data(df)

            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "suggestions": validation_result.get("suggestions", []),
                }

            # Clean up temporary file
            os.remove(file_path)

            return {
                "success": True,
                "data": df,
                "filename": filename,
                "rows": len(df),
                "columns": list(df.columns),
                "file_id": file_id,
                "processed_at": datetime.now(),
            }

        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}")
            return {"success": False, "error": f"Error processing file: {str(e)}"}

    def _parse_csv(self, file_path: str) -> pd.DataFrame:
        """Parse CSV file with various delimiters"""

        # Try different delimiters
        delimiters = [",", ";", "\t", "|"]

        # Read the header only once to determine date parsing
        header = pd.read_csv(file_path, nrows=0).columns
        parse_dates = ["timestamp"] if "timestamp" in header else False

        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding="utf-8",
                    parse_dates=parse_dates,
                )

                # Check if we got reasonable columns (more than 1 column)
                if len(df.columns) > 1:
                    return df

            except Exception:
                continue

        # Fallback to default comma delimiter
        return pd.read_csv(file_path, encoding="utf-8")

    def _parse_json(self, file_path: str) -> pd.DataFrame:
        """Parse JSON file"""

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if "data" in data:
                return pd.DataFrame(data["data"])
            else:
                return pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")

    def _parse_excel(self, file_path: str) -> pd.DataFrame:
        """Parse Excel file"""

        # Try to read the first sheet
        excel_file = pd.ExcelFile(file_path)

        # Get the first sheet name
        sheet_name = excel_file.sheet_names[0]

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            parse_dates=(
                ["timestamp"]
                if "timestamp" in pd.read_excel(file_path, nrows=0).columns
                else False
            ),
        )

        return df

    def _validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced validation with automatic column mapping - NO EMOJIS"""

        if df.empty:
            return {"valid": False, "error": "File is empty"}

        # Required columns for access control data
        required_columns = ["person_id", "door_id", "access_result", "timestamp"]

        print(f"[INFO] Validating data: {len(df)} rows, columns: {list(df.columns)}")

        # Check for exact matches first
        exact_matches = [col for col in required_columns if col in df.columns]
        missing_columns = [col for col in required_columns if col not in df.columns]

        print(f"[INFO] Exact matches: {exact_matches}, Missing: {missing_columns}")

        # If we have all exact matches, proceed with validation
        if len(exact_matches) == len(required_columns):
            print("[SUCCESS] All columns found exactly, proceeding with validation")
            return self._validate_data_content(df)

        # Try fuzzy matching for missing columns
        if missing_columns:
            print("[INFO] Attempting fuzzy matching...")
            fuzzy_matches = self._fuzzy_match_columns(
                list(df.columns), required_columns
            )

            print(f"[INFO] Fuzzy matches found: {fuzzy_matches}")

            # Check if we found matches for all required columns
            if len(fuzzy_matches) >= len(missing_columns):
                # Apply column mappings
                print("[SUCCESS] Applying column mappings...")
                try:
                    df_mapped = df.copy()
                    # FIX: Invert the dictionary - fuzzy_matches is target->source, but rename needs source->target
                    rename_dict = {
                        source_col: target_col
                        for target_col, source_col in fuzzy_matches.items()
                    }
                    df_mapped = df_mapped.rename(columns=rename_dict)

                    print(f"[SUCCESS] Applied rename dict: {rename_dict}")
                    print(f"[INFO] New columns: {list(df_mapped.columns)}")

                    # Validate the mapped dataframe and ensure column names are preserved
                    validation_result = self._validate_data_content(df_mapped)

                    # Force the renamed dataframe to be returned
                    if validation_result["valid"]:
                        validation_result["data"] = (
                            df_mapped  # Ensure the renamed df is returned
                        )
                        print(
                            f"[DEBUG] Returning dataframe with columns: {list(df_mapped.columns)}"
                        )

                    return validation_result

                except Exception as e:
                    print(f"[ERROR] Error applying column mappings: {e}")
                    return {
                        "valid": False,
                        "error": f"Error applying column mappings: {str(e)}",
                        "suggestions": fuzzy_matches,
                    }
            else:
                missing_after_fuzzy = [
                    col for col in required_columns if col not in fuzzy_matches
                ]
                print(
                    f"[WARNING] Could not map all columns. Still missing: {missing_after_fuzzy}"
                )
                return {
                    "valid": False,
                    "error": f"Could not map required columns. Missing: {missing_after_fuzzy}",
                    "suggestions": fuzzy_matches,
                    "available_columns": list(df.columns),
                    "required_columns": required_columns,
                }

        # If we reach here, all exact matches were found
        validation_result = self._validate_data_content(df)
        return validation_result

    def _validate_data_content(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the actual data content after column mapping - NO EMOJIS"""

        print("[INFO] Validating data content...")
        validation_errors = []

        # Standardize access_result values if present
        if "access_result" in df.columns:
            print("[INFO] Standardizing access_result values...")
            original_values = df["access_result"].unique()
            print(f"[INFO] Original access results: {original_values}")

            # Handle your specific format: "Access Granted" -> "Granted"
            df["access_result"] = (
                df["access_result"].astype(str).str.replace("Access ", "", regex=False)
            )
            standardized_values = df["access_result"].unique()
            print(f"[INFO] Standardized access results: {standardized_values}")

            # Check for valid results (be more permissive)
            valid_results = ["granted", "denied", "timeout", "error", "failed"]
            invalid_results = [
                r
                for r in df["access_result"].str.lower().unique()
                if r not in valid_results and r != "nan"
            ]

            if invalid_results:
                print(
                    f"[WARNING] Non-standard access results found: {invalid_results} (will be processed anyway)"
                )

        # Validate timestamp if present
        if "timestamp" in df.columns:
            print("[INFO] Validating timestamp column...")
            try:
                # Try to convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

                # Check for invalid timestamps
                null_timestamps = df["timestamp"].isnull().sum()
                if null_timestamps > 0:
                    print(
                        f"[WARNING] Found {null_timestamps} invalid timestamps (will be processed anyway)"
                    )
            except Exception as e:
                print(
                    f"[WARNING] Timestamp validation error: {e} (will be processed anyway)"
                )

        # Return validation result with the processed DataFrame
        if validation_errors:
            return {
                "valid": False,
                "error": "; ".join(validation_errors),
                "data": df,  # Still return the DataFrame even if there are errors
            }
        else:
            return {
                "valid": True,
                "data": df,  # CRITICAL: Return the processed DataFrame
                "message": "Data validation successful",
            }

    def _fuzzy_match_columns(
        self,
        available_columns: Sequence[str],
        required_columns: Sequence[str],
    ) -> Dict[str, str]:
        """Delegate fuzzy matching to shared utility."""
        return fuzzy_match_columns(available_columns, required_columns)

    def apply_manual_mapping(
        self, df: pd.DataFrame, column_mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """Apply manual column mapping via shared utility."""
        return util_apply_manual_mapping(df, column_mapping)

    def get_mapping_suggestions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return mapping suggestions using shared utility."""
        return util_get_mapping_suggestions(df)

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )
