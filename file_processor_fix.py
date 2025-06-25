#!/usr/bin/env python3
"""
File Processor Replacement Module
REPLACE your current file processing logic with these functions
"""

import pandas as pd
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class FixedFileProcessor:
    """
    REPLACEMENT for your current file processor
    Use this instead of your existing file processing logic
    """
    
    def __init__(self):
        self.required_columns = ['person_id', 'door_id', 'access_result', 'timestamp']
        self.valid_extensions = ['.csv', '.xlsx', '.xls', '.json']
        
    def process_file_with_validation(self, file_path: str) -> Dict[str, Any]:
        """
        REPLACE your main file processing function with this
        
        Args:
            file_path: Path to uploaded file
            
        Returns:
            Dict with processed data and validation results
        """
        result = {
            'success': False,
            'data': pd.DataFrame(),
            'total_records': 0,
            'validation_errors': [],
            'column_mappings_used': {},
            'processing_steps': []
        }
        
        try:
            # Step 1: Load file with proper error handling
            df, load_error = self._load_file_safely(file_path)
            if load_error:
                result['validation_errors'].append(f"File load error: {load_error}")
                return result
                
            result['processing_steps'].append(f"Loaded file: {len(df)} rows")
            
            # Step 2: Clean and prepare data
            df = self._clean_dataframe(df)
            result['processing_steps'].append(f"After cleaning: {len(df)} rows")
            
            # Step 3: Map columns (critical fix)
            df, mappings = self._map_columns_intelligently(df)
            result['column_mappings_used'] = mappings
            result['processing_steps'].append(f"Column mappings: {mappings}")
            
            # Step 4: Validate required columns exist
            missing_cols = self._check_required_columns(df)
            if missing_cols:
                result['validation_errors'].append(f"Missing required columns: {missing_cols}")
                return result
                
            # Step 5: Validate and standardize data
            df, validation_errors = self._validate_and_standardize_data(df)
            result['validation_errors'].extend(validation_errors)
            
            if validation_errors:
                logger.warning(f"Validation warnings: {validation_errors}")
                # Continue processing despite warnings
                
            # Step 6: Final validation
            if len(df) == 0:
                result['validation_errors'].append("No valid data rows after processing")
                return result
                
            result['success'] = True
            result['data'] = df
            result['total_records'] = len(df)
            result['processing_steps'].append(f"Final valid records: {len(df)}")
            
        except Exception as e:
            result['validation_errors'].append(f"Processing error: {str(e)}")
            logger.error(f"File processing failed: {e}")
            
        return result
    
    def _load_file_safely(self, file_path: str) -> Tuple[pd.DataFrame, Optional[str]]:
        """Load file with comprehensive error handling"""
        try:
            if file_path.endswith('.csv'):
                # Try different encodings and separators
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        if len(df.columns) > 1:  # Successfully parsed multiple columns
                            return df, None
                    except:
                        continue
                        
                # If all encodings fail, try with different separators
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(file_path, separator=sep, encoding='utf-8')
                        if len(df.columns) > 1:
                            return df, None
                    except:
                        continue
                        
                return pd.DataFrame(), "Could not parse CSV with any encoding/separator"
                
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
                return df, None
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    df = pd.DataFrame([json_data])
                else:
                    return pd.DataFrame(), "JSON must be an array of objects or a single object"
                return df, None
            else:
                return pd.DataFrame(), f"Unsupported file type: {file_path}"
                
        except Exception as e:
            return pd.DataFrame(), str(e)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the dataframe of common issues"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Remove any unnamed columns that are completely empty
        unnamed_cols = [col for col in df.columns if 'unnamed' in str(col).lower()]
        for col in unnamed_cols:
            if df[col].isna().all():
                df = df.drop(columns=[col])
                
        return df
    
    def _map_columns_intelligently(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        CRITICAL FIX: Intelligent column mapping
        This is likely where your 0 records issue originates
        """
        mappings = {}
        df_mapped = df.copy()
        
        # Enhanced mapping patterns
        mapping_patterns = {
            'person_id': [
                'person_id', 'personid', 'user_id', 'userid', 'employee_id', 
                'employeeid', 'badge_id', 'badgeid', 'card_id', 'cardid',
                'user', 'employee', 'person', 'id', 'emp_id', 'empid'
            ],
            'door_id': [
                'door_id', 'doorid', 'door', 'reader_id', 'readerid', 
                'device_id', 'deviceid', 'access_point', 'accesspoint',
                'gate_id', 'gateid', 'entry_id', 'entryid', 'reader', 'device'
            ],
            'access_result': [
                'access_result', 'accessresult', 'result', 'status', 
                'outcome', 'decision', 'success', 'granted', 'access_status',
                'accessstatus', 'auth_result', 'authresult'
            ],
            'timestamp': [
                'timestamp', 'time', 'datetime', 'date', 'event_time',
                'eventtime', 'access_time', 'accesstime', 'when',
                'occurred', 'date_time', 'ts'
            ]
        }
        
        # Find matches for each required column
        for required_col, patterns in mapping_patterns.items():
            found_match = False
            
            for pattern in patterns:
                for actual_col in df.columns:
                    if pattern == actual_col.lower() or pattern in actual_col.lower():
                        if required_col not in mappings:  # Avoid duplicate mappings
                            mappings[required_col] = actual_col
                            found_match = True
                            break
                if found_match:
                    break
        
        # Apply mappings by renaming columns
        if mappings:
            rename_dict = {v: k for k, v in mappings.items()}
            df_mapped = df_mapped.rename(columns=rename_dict)
            
        return df_mapped, mappings
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check which required columns are missing"""
        return [col for col in self.required_columns if col not in df.columns]
    
    def _validate_and_standardize_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Validate and standardize the data content"""
        validation_errors = []
        df_clean = df.copy()
        
        # Validate timestamp column
        if 'timestamp' in df_clean.columns:
            try:
                df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
            except Exception as e:
                validation_errors.append(f"Timestamp parsing error: {str(e)}")
                # Try to keep rows where timestamp is parseable
                df_clean = df_clean[pd.to_datetime(df_clean['timestamp'], errors='coerce').notna()]
        
        # Standardize access_result values
        if 'access_result' in df_clean.columns:
            df_clean['access_result'] = df_clean['access_result'].astype(str).str.strip().str.title()
            
            # Map common variations to standard values
            result_mappings = {
                'Success': 'Granted', 'Allow': 'Granted', 'Yes': 'Granted', 
                'True': 'Granted', '1': 'Granted', 'Pass': 'Granted',
                'Fail': 'Denied', 'False': 'Denied', 'No': 'Denied', 
                '0': 'Denied', 'Block': 'Denied', 'Reject': 'Denied'
            }
            
            df_clean['access_result'] = df_clean['access_result'].replace(result_mappings)
            
            # Check for invalid results
            valid_results = ['Granted', 'Denied', 'Failed', 'Error']
            invalid_results = set(df_clean['access_result'].unique()) - set(valid_results)
            if invalid_results:
                validation_errors.append(f"Unknown access results found: {invalid_results}")
        
        # Remove rows with critical missing data
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=['person_id', 'door_id'])
        final_count = len(df_clean)
        
        if initial_count != final_count:
            validation_errors.append(f"Removed {initial_count - final_count} rows with missing person_id or door_id")
        
        return df_clean, validation_errors


# REPLACEMENT FUNCTIONS - Use these in your main code

def process_uploaded_file_fixed(file_path: str) -> Dict[str, Any]:
    """
    REPLACE your current process_uploaded_file function with this
    
    Returns standardized result format for your analytics
    """
    processor = FixedFileProcessor()
    result = processor.process_file_with_validation(file_path)
    
    if result['success']:
        # Convert to your expected format
        analytics_result = {
            'total_events': result['total_records'],
            'unique_users': result['data']['person_id'].nunique() if 'person_id' in result['data'].columns else 0,
            'unique_doors': result['data']['door_id'].nunique() if 'door_id' in result['data'].columns else 0,
            'data': result['data'],
            'processing_info': {
                'column_mappings': result['column_mappings_used'],
                'processing_steps': result['processing_steps'],
                'validation_warnings': result['validation_errors']
            }
        }
        
        logger.info(f"Successfully processed file: {result['total_records']} records")
        return analytics_result
    else:
        logger.error(f"File processing failed: {result['validation_errors']}")
        return {
            'total_events': 0,
            'unique_users': 0, 
            'unique_doors': 0,
            'data': pd.DataFrame(),
            'error': result['validation_errors']
        }


def test_file_processing(file_path: str) -> None:
    """
    TESTING FUNCTION - Use this to test your files individually
    """
    print(f"\n=== TESTING FILE PROCESSING: {file_path} ===")
    
    result = process_uploaded_file_fixed(file_path)
    
    print(f"Total Events: {result['total_events']}")
    print(f"Unique Users: {result['unique_users']}")
    print(f"Unique Doors: {result['unique_doors']}")
    
    if 'processing_info' in result:
        print(f"Column Mappings: {result['processing_info']['column_mappings']}")
        print(f"Processing Steps: {result['processing_info']['processing_steps']}")
        
        if result['processing_info']['validation_warnings']:
            print(f"Warnings: {result['processing_info']['validation_warnings']}")
    
    if 'error' in result:
        print(f"ERRORS: {result['error']}")
        
    # Show sample data if available
    if not result['data'].empty:
        print("\nSample data:")
        print(result['data'].head(2).to_string())
    
    return result