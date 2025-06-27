"""
File Processing Service for Yōsai Intel Dashboard
"""
import io
import logging
import re
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from .base import BaseService

logger = logging.getLogger(__name__)

class FileProcessorService(BaseService):
    """File processing service implementation"""
    
    ALLOWED_EXTENSIONS = {'.csv', '.json', '.xlsx', '.xls'}
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self):
        super().__init__("file_processor")
    
    def _do_initialize(self) -> None:
        """Initialize file processor"""
        pass  # No special initialization needed
    
    def validate_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate uploaded file"""
        issues = []
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            issues.append(f"File type {file_ext} not allowed. Allowed: {self.ALLOWED_EXTENSIONS}")
        
        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            issues.append(f"File too large: {size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB")
        
        # Check for empty file
        if len(content) == 0:
            issues.append("File is empty")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'size_mb': size_mb,
            'extension': file_ext
        }
    
    def process_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Process uploaded file and return DataFrame"""
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.csv':
                return self._process_csv(file_content)
            elif file_ext == '.json':
                return self._process_json(file_content)
            elif file_ext in ['.xlsx', '.xls']:
                return self._process_excel(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            raise
    
    def _sanitize_text(self, text: str) -> str:
        """Remove characters that could cause encoding issues."""
        return re.sub(r"[\ud800-\udfff]", "", text)

    def _decode_bytes(self, content: bytes) -> str:
        """Safely decode bytes using multiple fallbacks."""
        for encoding in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    def _process_csv(self, content: bytes) -> pd.DataFrame:
        """Process CSV file with safe decoding"""
        try:
            text = self._decode_bytes(content)
            text = self._sanitize_text(text)
            return pd.read_csv(io.StringIO(text))
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")
    
    def _process_json(self, content: bytes) -> pd.DataFrame:
        """Process JSON file"""
        try:
            text = self._decode_bytes(content)
            text = self._sanitize_text(text)
            return pd.read_json(io.StringIO(text))
        except Exception as e:
            raise ValueError(f"Error reading JSON: {e}")
    
    def _process_excel(self, content: bytes) -> pd.DataFrame:
        """Process Excel file"""
        try:
            return pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")
