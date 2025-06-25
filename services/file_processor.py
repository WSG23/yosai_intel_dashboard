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
        """Enhanced validation with automatic column mapping"""

        if df.empty:
            return {'valid': False, 'error': 'File is empty'}

        required_columns = ['person_id', 'door_id', 'access_result', 'timestamp']

        exact_matches = [col for col in required_columns if col in df.columns]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if len(exact_matches) == len(required_columns):
            return self._validate_data_content(df)

        if missing_columns:
            fuzzy_matches = self._fuzzy_match_columns(list(df.columns), required_columns)

            print(f"\ud83d\udd27 Fuzzy matching found: {fuzzy_matches}")

            if len(fuzzy_matches) >= len(missing_columns):
                df_mapped = df.copy()
                df_mapped = df_mapped.rename(columns=fuzzy_matches)

                print(f"\u2705 Applied column mappings: {fuzzy_matches}")

                return self._validate_data_content(df_mapped)
            else:
                return {
                    'valid': False,
                    'error': f'Could not map required columns. Found: {fuzzy_matches}',
                    'suggestions': fuzzy_matches,
                    'available_columns': list(df.columns),
                    'required_columns': required_columns
                }

        return {'valid': True}

    def _validate_data_content(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the actual data content"""
        validation_errors = []

        if 'access_result' in df.columns:
            df['access_result'] = df['access_result'].astype(str).str.replace('Access ', '', regex=False)

            valid_results = ['granted', 'denied', 'timeout', 'error', 'failed']
            invalid_results = df['access_result'].str.lower().unique()
            invalid_results = [r for r in invalid_results if r not in valid_results]

            if invalid_results:
                print(f"\u26a0\ufe0f  Non-standard access results found: {invalid_results} (will be processed anyway)")

        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                validation_errors.append(f"Cannot parse timestamp column: {e}")

        if len(df) == 0:
            validation_errors.append("No data rows found")

        if validation_errors:
            return {
                'valid': False,
                'error': '; '.join(validation_errors)
            }

        return {'valid': True, 'data': df}
    
    def _fuzzy_match_columns(self, available_columns: Sequence[str], required_columns: Sequence[str]) -> Dict[str, str]:
        """Enhanced fuzzy matching based on your actual data"""

        suggestions = {}

        mapping_patterns = {
            'person_id': [
                'person id', 'userid', 'user id',
                'user', 'employee', 'badge', 'card', 'person', 'emp',
                'employee_id', 'badge_id', 'card_id'
            ],
            'door_id': [
                'device name', 'devicename', 'device_name',
                'door', 'reader', 'device', 'access_point', 'gate', 'entry',
                'door_name', 'reader_id', 'access_device'
            ],
            'access_result': [
                'access result', 'accessresult', 'access_result',
                'result', 'status', 'outcome', 'decision', 'success',
                'granted', 'denied', 'access_status'
            ],
            'timestamp': [
                'timestamp', 'time', 'datetime', 'date',
                'when', 'occurred', 'event_time', 'access_time',
                'date_time', 'event_date'
            ]
        }

        available_lower = {col.lower(): col for col in available_columns}

        for required_col, patterns in mapping_patterns.items():
            best_match = None

            for pattern in patterns:
                if pattern.lower() in available_lower:
                    best_match = available_lower[pattern.lower()]
                    break

            if not best_match:
                for pattern in patterns:
                    for available_col_lower, original_col in available_lower.items():
                        if pattern in available_col_lower or available_col_lower in pattern:
                            best_match = original_col
                            break
                    if best_match:
                        break
            if best_match:
                suggestions[required_col] = best_match

        return suggestions

    def apply_manual_mapping(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """Apply manual column mapping provided by user"""

        print(f"\ud83d\udd27 Applying manual mapping: {column_mapping}")

        missing_source_cols = [source for source in column_mapping.values() if source not in df.columns]
        if missing_source_cols:
            raise ValueError(f"Source columns not found: {missing_source_cols}")

        df_mapped = df.rename(columns={v: k for k, v in column_mapping.items()})

        return df_mapped

    def get_mapping_suggestions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get mapping suggestions for user interface"""

        required_columns = ['person_id', 'door_id', 'access_result', 'timestamp']
        fuzzy_matches = self._fuzzy_match_columns(list(df.columns), required_columns)

        return {
            'available_columns': list(df.columns),
            'required_columns': required_columns,
            'suggested_mappings': fuzzy_matches,
            'missing_mappings': [col for col in required_columns if col not in fuzzy_matches]
        }
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
