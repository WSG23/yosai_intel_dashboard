"""File processing service implementation"""
import pandas as pd
import json
import os
import uuid
from typing import Dict, Any

from services.interfaces import FileProcessorProtocol


class FileProcessorService(FileProcessorProtocol):
    """Service for processing uploaded files"""

    def __init__(self, upload_folder: str = "uploads", allowed_extensions: set | None = None) -> None:
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions or {"csv", "json", "xlsx", "xls"}
        os.makedirs(upload_folder, exist_ok=True)

    def process_upload(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Process uploaded file and return parsed dataframe"""
        if not self._is_allowed_file(filename):
            raise ValueError(f"File type not allowed. Allowed: {self.allowed_extensions}")

        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_folder, f"{file_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)

        ext = filename.rsplit(".", 1)[1].lower()
        if ext == "csv":
            df = self._parse_csv(file_path)
        elif ext == "json":
            df = self._parse_json(file_path)
        elif ext in {"xlsx", "xls"}:
            df = self._parse_excel(file_path)
        else:
            raise ValueError("Unsupported file type")

        os.remove(file_path)
        return df

    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data integrity"""
        if data.empty:
            return {"valid": False, "error": "File is empty"}

        required_columns = {"person_id", "door_id", "access_result"}
        missing = [c for c in required_columns if c not in data.columns]
        if missing:
            return {"valid": False, "error": f"Missing required columns: {missing}"}

        return {"valid": True}

    def _parse_csv(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)

    def _parse_json(self, path: str) -> pd.DataFrame:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame([data])

    def _parse_excel(self, path: str) -> pd.DataFrame:
        return pd.read_excel(path)

    def _is_allowed_file(self, filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
