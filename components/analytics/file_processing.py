# components/analytics/file_processing.py - File processing utilities
import pandas as pd
import json
import base64
import io
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime

class FileProcessor:
    """Handles file processing for analytics uploads"""
    
    @staticmethod
    def process_file_content(contents: str, filename: str) -> Optional[pd.DataFrame]:
        """Process file content based on file type"""
        
        try:
            # Decode the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            if filename.endswith('.csv'):
                return FileProcessor._process_csv(decoded)
            elif filename.endswith('.json'):
                return FileProcessor._process_json(decoded)
            elif filename.endswith(('.xlsx', '.xls')):
                return FileProcessor._process_excel(decoded)
            else:
                return None
                
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            return None
    
    @staticmethod
    def _process_csv(decoded: bytes) -> Optional[pd.DataFrame]:
        """Process CSV file with multiple encoding attempts"""
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(io.StringIO(decoded.decode(encoding)))
                # Clean column names
                df.columns = df.columns.astype(str).str.strip()
                return df
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        return None
    
    @staticmethod
    def _process_json(decoded: bytes) -> Optional[pd.DataFrame]:
        """Process JSON file"""
        try:
            json_data = json.loads(decoded.decode('utf-8'))
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if 'data' in json_data:
                    df = pd.DataFrame(json_data['data'])
                else:
                    df = pd.DataFrame([json_data])
            else:
                return None
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            return df
            
        except (json.JSONDecodeError, ValueError):
            return None
    
    @staticmethod
    def _process_excel(decoded: bytes) -> Optional[pd.DataFrame]:
        """Process Excel file"""
        try:
            df = pd.read_excel(io.BytesIO(decoded))
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            return df
        except Exception:
            return None
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str, List[str]]:
        """Validate DataFrame and return status, message, and suggestions"""
        
        if df.empty:
            return False, "File is empty", []
        
        # Basic validation
        if len(df.columns) < 2:
            return False, "File must have at least 2 columns", []
        
        # Check for reasonable data
        if len(df) < 1:
            return False, "File must have at least 1 row of data", []
        
        suggestions = []
        
        # Check for common access control columns
        expected_columns = ['person_id', 'user_id', 'employee_id', 'door_id', 'access_result', 'timestamp', 'datetime']
        found_columns = [col for col in expected_columns if col.lower() in [c.lower() for c in df.columns]]
        
        if not found_columns:
            # Suggest column mappings
            suggestions.extend(FileProcessor._suggest_column_mappings(df.columns))
        
        return True, f"Successfully loaded {len(df)} rows and {len(df.columns)} columns", suggestions
    
    @staticmethod
    def _suggest_column_mappings(columns: List[str]) -> List[str]:
        """Suggest column mappings for access control data"""
        suggestions = []
        column_lower = [col.lower() for col in columns]
        
        # Mapping patterns
        mappings = {
            'user/person identifier': ['user', 'person', 'employee', 'badge', 'card', 'id'],
            'door/location identifier': ['door', 'reader', 'device', 'location', 'access_point'],
            'access result': ['result', 'status', 'outcome', 'decision', 'access'],
            'timestamp': ['time', 'date', 'when', 'occurred', 'timestamp']
        }
        
        for purpose, patterns in mappings.items():
            matches = []
            for col in columns:
                if any(pattern in col.lower() for pattern in patterns):
                    matches.append(col)
            
            if matches:
                suggestions.append(f"Potential {purpose} columns: {', '.join(matches[:3])}")
        
        return suggestions

class AnalyticsGenerator:
    """Generates analytics from processed data"""
    
    @staticmethod
    def generate_analytics(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive analytics from DataFrame"""
        
        if df.empty:
            return {}
        
        analytics = {
            'total_events': len(df),
            'processed_at': datetime.now().isoformat()
        }
        
        # Date range analysis
        analytics.update(AnalyticsGenerator._analyze_dates(df))
        
        # Access patterns analysis
        analytics.update(AnalyticsGenerator._analyze_access_patterns(df))
        
        # User activity analysis
        analytics.update(AnalyticsGenerator._analyze_users(df))
        
        # Location/door analysis
        analytics.update(AnalyticsGenerator._analyze_locations(df))
        
        return analytics
    
    @staticmethod
    def _analyze_dates(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze date/time columns"""
        date_analysis = {}
        
        date_columns = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['date', 'time', 'timestamp'])]
        
        if date_columns:
            date_col = date_columns[0]
            try:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
                valid_dates = df_copy[date_col].dropna()
                
                if not valid_dates.empty:
                    date_analysis['date_range'] = {
                        'start': valid_dates.min().strftime('%Y-%m-%d'),
                        'end': valid_dates.max().strftime('%Y-%m-%d')
                    }
                    
                    # Hourly patterns
                    df_copy['hour'] = valid_dates.dt.hour
                    hourly_counts = df_copy['hour'].value_counts().sort_index()
                    date_analysis['hourly_patterns'] = {
                        str(k): int(v) for k, v in hourly_counts.items()
                    }
            except Exception as e:
                print(f"Error processing date column {date_col}: {e}")
        
        return date_analysis
    
    @staticmethod
    def _analyze_access_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze access result patterns"""
        access_analysis = {}
        
        access_columns = [col for col in df.columns 
                         if any(keyword in str(col).lower() 
                               for keyword in ['access', 'result', 'status', 'outcome'])]
        
        if access_columns:
            access_col = access_columns[0]
            try:
                access_counts = df[access_col].value_counts()
                access_analysis['access_patterns'] = {
                    str(k): int(v) for k, v in access_counts.items()
                }
            except Exception as e:
                print(f"Error processing access column {access_col}: {e}")
        
        return access_analysis
    
    @staticmethod
    def _analyze_users(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        user_analysis = {}
        
        user_columns = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                             for keyword in ['user', 'person', 'employee', 'id'])]
        
        if user_columns:
            user_col = user_columns[0]
            try:
                user_counts = df[user_col].value_counts().head(10)
                user_analysis['top_users'] = {
                    str(k): int(v) for k, v in user_counts.items()
                }
            except Exception as e:
                print(f"Error processing user column {user_col}: {e}")
        
        return user_analysis
    
    @staticmethod
    def _analyze_locations(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze location/door activity patterns"""
        location_analysis = {}
        
        location_columns = [col for col in df.columns 
                           if any(keyword in str(col).lower() 
                                 for keyword in ['door', 'location', 'device', 'reader', 'point'])]
        
        if location_columns:
            location_col = location_columns[0]
            try:
                location_counts = df[location_col].value_counts().head(10)
                location_analysis['top_doors'] = {
                    str(k): int(v) for k, v in location_counts.items()
                }
            except Exception as e:
                print(f"Error processing location column {location_col}: {e}")
        
        return location_analysis