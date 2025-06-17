# services/file_processor.py
import pandas as pd
import json
import os
import uuid
from typing import Dict, Any, Optional, Tuple, Sequence
import logging
from datetime import datetime

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
                'success': False,
                'error': f'File type not allowed. Allowed: {self.allowed_extensions}'
            }
        
        try:
            # Save file temporarily
            file_id = str(uuid.uuid4())
            file_path = os.path.join(self.upload_folder, f"{file_id}_{filename}")
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Parse based on file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'csv':
                df = self._parse_csv(file_path)
            elif file_ext == 'json':
                df = self._parse_json(file_path)
            elif file_ext in ['xlsx', 'xls']:
                df = self._parse_excel(file_path)
            else:
                return {'success': False, 'error': 'Unsupported file type'}
            
            # Validate and clean data
            validation_result = self._validate_data(df)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'suggestions': validation_result.get('suggestions', [])
                }
            
            # Clean up temporary file
            os.remove(file_path)
            
            return {
                'success': True,
                'data': df,
                'filename': filename,
                'rows': len(df),
                'columns': list(df.columns),
                'file_id': file_id,
                'processed_at': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}")
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    def _parse_csv(self, file_path: str) -> pd.DataFrame:
        """Parse CSV file with various delimiters"""
        
        # Try different delimiters
        delimiters = [',', ';', '\t', '|']

        # Read the header only once to determine date parsing
        header = pd.read_csv(file_path, nrows=0).columns
        parse_dates = ['timestamp'] if 'timestamp' in header else False

        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding='utf-8',
                    parse_dates=parse_dates
                )

                # Check if we got reasonable columns (more than 1 column)
                if len(df.columns) > 1:
                    return df

            except Exception:
                continue
        
        # Fallback to default comma delimiter
        return pd.read_csv(file_path, encoding='utf-8')
    
    def _parse_json(self, file_path: str) -> pd.DataFrame:
        """Parse JSON file"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'data' in data:
                return pd.DataFrame(data['data'])
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
            parse_dates=['timestamp'] if 'timestamp' in pd.read_excel(file_path, nrows=0).columns else False
        )
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data format for access control events"""
        
        if df.empty:
            return {'valid': False, 'error': 'File is empty'}
        
        # Required columns for access control data
        required_columns = ['person_id', 'door_id', 'access_result']
        missing_columns = []
        
        # Check for exact matches first
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        # If exact matches not found, try fuzzy matching
        if missing_columns:
            fuzzy_matches = self._fuzzy_match_columns(list(df.columns), required_columns)
            
            if fuzzy_matches:
                return {
                    'valid': False,
                    'error': f'Missing required columns: {missing_columns}',
                    'suggestions': fuzzy_matches
                }
        
        # Validate data types and content
        validation_errors = []
        
        # Check for timestamp column
        timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        if not timestamp_cols:
            validation_errors.append("No timestamp column found")
        
        # Check for reasonable data ranges
        if 'access_result' in df.columns:
            valid_results = ['granted', 'denied', 'timeout', 'error']
            invalid_results = df['access_result'].str.lower().unique()
            invalid_results = [r for r in invalid_results if r not in valid_results]
            
            if invalid_results:
                validation_errors.append(f"Invalid access results found: {invalid_results}")
        
        if validation_errors:
            return {
                'valid': False,
                'error': '; '.join(validation_errors)
            }
        
        return {'valid': True}
    
    def _fuzzy_match_columns(self, available_columns: Sequence[str], required_columns: Sequence[str]) -> Dict[str, str]:
        """Suggest column mappings based on fuzzy matching"""
        
        suggestions = {}
        
        # Simple fuzzy matching based on common patterns
        mapping_patterns = {
            'person_id': ['user', 'employee', 'badge', 'card', 'id'],
            'door_id': ['door', 'reader', 'device', 'access_point'],
            'access_result': ['result', 'status', 'outcome', 'decision'],
            'timestamp': ['time', 'date', 'when', 'occurred']
        }
        
        for required_col, patterns in mapping_patterns.items():
            for available_col in available_columns:
                for pattern in patterns:
                    if pattern in available_col.lower():
                        suggestions[required_col] = available_col
                        break
                if required_col in suggestions:
                    break
        
        return suggestions
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

# services/analytics_service.py
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import numpy as np

class AnalyticsService:
    """Service for analytics calculations"""
    
    def __init__(self, access_model, anomaly_model):
        self.access_model = access_model
        self.anomaly_model = anomaly_model
    
    def process_uploaded_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process uploaded data and generate analytics"""
        
        # Basic statistics
        total_events = len(df)
        date_range = {
            'start': df['timestamp'].min() if 'timestamp' in df.columns else None,
            'end': df['timestamp'].max() if 'timestamp' in df.columns else None
        }
        
        # Access patterns
        access_patterns = {}
        if 'access_result' in df.columns:
            access_patterns = df['access_result'].value_counts().to_dict()
        
        # Hourly patterns
        hourly_patterns = {}
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            hourly_patterns = df['hour'].value_counts().sort_index().to_dict()
        
        # Top users/doors
        top_users = {}
        top_doors = {}
        
        if 'person_id' in df.columns:
            top_users = df['person_id'].value_counts().head(10).to_dict()
        
        if 'door_id' in df.columns:
            top_doors = df['door_id'].value_counts().head(10).to_dict()
        
        return {
            'total_events': total_events,
            'date_range': date_range,
            'access_patterns': access_patterns,
            'hourly_patterns': hourly_patterns,
            'top_users': top_users,
            'top_doors': top_doors,
            'processed_at': datetime.now()
        }
