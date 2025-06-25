#!/usr/bin/env python3
"""
File Analysis Diagnosis Module
Modular code to identify and isolate file parsing issues
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileAnalyzer:
    """Modular file analyzer to diagnose upload issues"""

    def __init__(self):
        self.required_columns = ['person_id', 'door_id', 'access_result', 'timestamp']
        self.optional_columns = ['event_id', 'badge_status', 'device_status']
        self.valid_access_results = ['granted', 'denied', 'failed', 'error']

    def diagnose_files(self, file_path: str) -> Dict[str, Any]:
        """Main diagnosis function - replace in your main analysis"""
        diagnosis = {
            'file_info': {},
            'column_analysis': {},
            'data_validation': {},
            'recommendations': [],
            'status': 'unknown'
        }

        try:
            diagnosis['file_info'] = self._analyze_file_basic(file_path)
            diagnosis['column_analysis'] = self._analyze_columns(file_path)
            diagnosis['data_validation'] = self._validate_data_content(file_path)
            diagnosis['recommendations'] = self._generate_recommendations(diagnosis)
            diagnosis['status'] = self._determine_status(diagnosis)
        except Exception as e:
            diagnosis['error'] = str(e)
            diagnosis['status'] = 'error'
            logger.error(f"Diagnosis failed: {e}")

        return diagnosis

    def _analyze_file_basic(self, file_path: str) -> Dict[str, Any]:
        """Step 1: Basic file information analysis"""
        info = {}

        if not os.path.exists(file_path):
            info['exists'] = False
            info['error'] = f"File not found: {file_path}"
            return info

        info['exists'] = True
        info['size_bytes'] = os.path.getsize(file_path)
        info['size_mb'] = round(info['size_bytes'] / (1024*1024), 2)
        info['extension'] = Path(file_path).suffix.lower()

        try:
            if info['extension'] == '.csv':
                df = pd.read_csv(file_path, nrows=1)
            elif info['extension'] in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=1)
            else:
                info['readable'] = False
                info['error'] = f"Unsupported format: {info['extension']}"
                return info

            info['readable'] = True
            info['detected_columns'] = list(df.columns)
        except Exception as e:
            info['readable'] = False
            info['error'] = f"Cannot read file: {str(e)}"

        return info

    def _analyze_columns(self, file_path: str) -> Dict[str, Any]:
        """Step 2: Column structure analysis"""
        analysis = {}

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=5)
            else:
                df = pd.read_excel(file_path, nrows=5)

            analysis['total_columns'] = len(df.columns)
            analysis['column_names'] = list(df.columns)

            analysis['required_found'] = {}
            for req_col in self.required_columns:
                analysis['required_found'][req_col] = req_col in df.columns

            analysis['column_mapping_suggestions'] = self._suggest_column_mappings(df.columns)
            analysis['column_types'] = df.dtypes.to_dict()
            analysis['missing_required'] = [col for col in self.required_columns if not analysis['required_found'][col]]
        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _validate_data_content(self, file_path: str) -> Dict[str, Any]:
        """Step 3: Data content validation"""
        validation = {}

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            validation['total_rows'] = len(df)
            validation['empty_rows'] = df.isnull().all(axis=1).sum()
            validation['actual_data_rows'] = validation['total_rows'] - validation['empty_rows']

            validation['column_issues'] = {}
            for col in self.required_columns:
                if col in df.columns:
                    col_validation = self._validate_column(df[col], col)
                    validation['column_issues'][col] = col_validation

            validation['sample_data'] = df.head(3).to_dict('records')
        except Exception as e:
            validation['error'] = str(e)

        return validation

    def _validate_column(self, column: pd.Series, col_name: str) -> Dict[str, Any]:
        validation = {
            'null_count': column.isnull().sum(),
            'unique_values': column.nunique(),
            'sample_values': column.dropna().head(5).tolist()
        }

        if col_name == 'access_result':
            unique_results = column.dropna().str.lower().unique()
            validation['invalid_results'] = [r for r in unique_results if r not in self.valid_access_results]
        elif col_name == 'timestamp':
            try:
                pd.to_datetime(column.dropna().head(10))
                validation['timestamp_parseable'] = True
            except Exception:
                validation['timestamp_parseable'] = False

        return validation

    def _suggest_column_mappings(self, available_columns: List[str]) -> Dict[str, str]:
        suggestions = {}
        mapping_patterns = {
            'person_id': ['user', 'employee', 'badge', 'card', 'id', 'userid', 'emp'],
            'door_id': ['door', 'reader', 'device', 'access_point', 'gate', 'entry'],
            'access_result': ['result', 'status', 'outcome', 'decision', 'success'],
            'timestamp': ['time', 'date', 'when', 'occurred', 'datetime', 'ts']
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

    def _generate_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        recommendations = []

        if not diagnosis['file_info'].get('readable', False):
            recommendations.append("FIX: File cannot be read - check file format and corruption")

        missing_cols = diagnosis['column_analysis'].get('missing_required', [])
        if missing_cols:
            suggestions = diagnosis['column_analysis'].get('column_mapping_suggestions', {})
            if suggestions:
                recommendations.append(f"REPLACE: Map columns - {suggestions}")
            else:
                recommendations.append(f"ADD: Missing required columns: {missing_cols}")

        data_rows = diagnosis['data_validation'].get('actual_data_rows', 0)
        if data_rows == 0:
            recommendations.append("FIX: No actual data rows found - check for empty file or header-only file")

        return recommendations

    def _determine_status(self, diagnosis: Dict[str, Any]) -> str:
        if diagnosis.get('error'):
            return 'error'
        elif not diagnosis['file_info'].get('readable', False):
            return 'unreadable'
        elif diagnosis['column_analysis'].get('missing_required'):
            return 'column_mismatch'
        elif diagnosis['data_validation'].get('actual_data_rows', 0) == 0:
            return 'no_data'
        else:
            return 'valid'


def quick_diagnosis(file_path: str) -> Dict[str, Any]:
    """Quick diagnosis function - USE THIS for immediate testing"""
    analyzer = FileAnalyzer()
    result = analyzer.diagnose_files(file_path)

    print(f"\n=== FILE DIAGNOSIS: {file_path} ===")
    print(f"Status: {result['status']}")
    print(f"Readable: {result['file_info'].get('readable', False)}")
    print(f"Data rows: {result['data_validation'].get('actual_data_rows', 0)}")

    if result['recommendations']:
        print("\nRECOMMENDATIONS:")
        for rec in result['recommendations']:
            print(f"  • {rec}")

    return result


def test_individual_file(file_path: str) -> bool:
    """Isolate test for single file"""
    try:
        result = quick_diagnosis(file_path)
        return result['status'] == 'valid'
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def test_column_mapping(file_path: str) -> Dict[str, str]:
    """Test and return column mapping suggestions"""
    analyzer = FileAnalyzer()
    result = analyzer.diagnose_files(file_path)
    return result['column_analysis'].get('column_mapping_suggestions', {})

__all__ = ['FileAnalyzer', 'quick_diagnosis', 'test_individual_file', 'test_column_mapping']
