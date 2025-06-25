#!/usr/bin/env python3
"""
Data Diagnostics Module
Specialized functions to diagnose and fix data parsing issues
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class DataDiagnostics:
    """Diagnose and fix data parsing issues causing 0 active users/doors"""
    
    @staticmethod
    def diagnose_zero_actives(df: pd.DataFrame, debug: bool = True) -> Dict[str, Any]:
        """
        MAIN DIAGNOSTIC FUNCTION - Replace your current analysis call with this
        
        Args:
            df: Your DataFrame with 300 events
            debug: Print detailed diagnostic info
            
        Returns:
            Complete diagnostic report
        """
        report = {
            'raw_data_info': DataDiagnostics._analyze_raw_data(df),
            'column_issues': DataDiagnostics._identify_column_issues(df),
            'filtering_problems': DataDiagnostics._check_filtering_logic(df),
            'timestamp_issues': DataDiagnostics._diagnose_timestamp_problems(df),
            'suggested_fixes': [],
            'corrected_counts': {}
        }
        
        # Generate fixes based on issues found
        report['suggested_fixes'] = DataDiagnostics._generate_fixes(report)
        
        # Try to calculate corrected counts
        report['corrected_counts'] = DataDiagnostics._calculate_corrected_counts(df)
        
        if debug:
            DataDiagnostics._print_diagnostic_report(report)
        
        return report
    
    @staticmethod
    def _analyze_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the raw structure of your 300-event dataset"""
        info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'column_types': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'has_duplicates': df.duplicated().any(),
            'duplicate_count': df.duplicated().sum()
        }
        
        # Sample of actual data
        info['first_5_rows'] = df.head(5).to_dict('records') if not df.empty else []
        info['last_5_rows'] = df.tail(5).to_dict('records') if not df.empty else []
        
        return info
    
    @staticmethod
    def _identify_column_issues(df: pd.DataFrame) -> Dict[str, Any]:
        """Identify column-related issues causing 0 counts"""
        issues = {
            'missing_person_column': True,
            'missing_door_column': True,
            'person_column_candidates': [],
            'door_column_candidates': [],
            'null_percentages': {},
            'unique_value_counts': {},
            'string_cleaning_impact': {}  # FIXED: Initialize this key
        }
        
        # Check for person/user identification columns
        person_keywords = ['person', 'user', 'employee', 'badge', 'card', 'id']
        door_keywords = ['door', 'access', 'location', 'point', 'entry', 'exit']
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check for person-related columns
            if any(keyword in col_lower for keyword in person_keywords):
                issues['person_column_candidates'].append(col)
                if col_lower in ['person_id', 'user_id', 'person', 'user']:
                    issues['missing_person_column'] = False
            
            # Check for door-related columns
            if any(keyword in col_lower for keyword in door_keywords):
                issues['door_column_candidates'].append(col)
                if col_lower in ['door_id', 'door', 'access_point']:
                    issues['missing_door_column'] = False
            
            # Calculate null percentages
            null_pct = (df[col].isnull().sum() / len(df)) * 100
            issues['null_percentages'][col] = round(null_pct, 2)
            
            # Count unique values
            unique_count = df[col].nunique()
            issues['unique_value_counts'][col] = unique_count
            
            # Sample unique values
            if unique_count > 0 and unique_count <= 20:
                issues[f'{col}_sample_values'] = df[col].unique().tolist()
            
            # FIXED: Calculate string cleaning impact for object columns
            if df[col].dtype == 'object':
                original_unique = df[col].nunique()
                
                # Test cleaning impact
                try:
                    cleaned = df[col].astype(str).str.strip()
                    cleaned = cleaned[~cleaned.isin(['None', 'nan', '', 'null', 'NaN'])]
                    cleaned_unique = cleaned.nunique()
                    
                    issues['string_cleaning_impact'][col] = {
                        'original_unique': original_unique,
                        'after_cleaning': cleaned_unique,
                        'lost_values': original_unique - cleaned_unique
                    }
                except:
                    issues['string_cleaning_impact'][col] = {
                        'original_unique': original_unique,
                        'after_cleaning': original_unique,
                        'lost_values': 0
                    }
        
        return issues
    
    @staticmethod
    def _check_filtering_logic(df: pd.DataFrame) -> Dict[str, Any]:
        """Check if filtering logic is removing all active users/doors"""
        filtering = {
            'original_count': len(df),
            'after_dropna_count': len(df.dropna()),
            'string_cleaning_impact': {},
            'potential_active_users': 0,
            'potential_active_doors': 0
        }
        
        # Test different cleaning approaches
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                original_unique = df[col].nunique()
                
                # Test cleaning impact
                cleaned = df[col].astype(str).str.strip()
                cleaned = cleaned[~cleaned.isin(['None', 'nan', '', 'null', 'NaN'])]
                cleaned_unique = cleaned.nunique()
                
                filtering['string_cleaning_impact'][col] = {
                    'original_unique': original_unique,
                    'after_cleaning': cleaned_unique,
                    'lost_values': original_unique - cleaned_unique
                }
        
        # Try to find potential users/doors with looser criteria
        potential_person_cols = [col for col in df.columns 
                               if any(kw in col.lower() for kw in ['person', 'user', 'id', 'badge'])]
        
        potential_door_cols = [col for col in df.columns 
                             if any(kw in col.lower() for kw in ['door', 'location', 'access', 'point'])]
        
        if potential_person_cols:
            col = potential_person_cols[0]
            filtering['potential_active_users'] = df[col].nunique()
        
        if potential_door_cols:
            col = potential_door_cols[0]
            filtering['potential_active_doors'] = df[col].nunique()
        
        return filtering
    
    @staticmethod
    def _diagnose_timestamp_problems(df: pd.DataFrame) -> Dict[str, Any]:
        """Diagnose timestamp-related issues affecting "active" calculations"""
        timestamp_info = {
            'has_timestamp_column': False,
            'timestamp_column_candidates': [],
            'timestamp_range': None,
            'within_24h_count': 0,
            'future_dates': 0,
            'parsing_issues': []
        }
        
        # Find timestamp columns
        time_keywords = ['time', 'date', 'stamp', 'created', 'modified']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in time_keywords):
                timestamp_info['timestamp_column_candidates'].append(col)
                
                # Try to parse as datetime
                try:
                    parsed_times = pd.to_datetime(df[col], errors='coerce')
                    valid_times = parsed_times.dropna()
                    
                    if len(valid_times) > 0:
                        timestamp_info['has_timestamp_column'] = True
                        timestamp_info['timestamp_range'] = {
                            'min': str(valid_times.min()),
                            'max': str(valid_times.max()),
                            'valid_count': len(valid_times)
                        }
                        
                        # Check for recent activity (within 24 hours)
                        now = datetime.now()
                        recent_cutoff = now - timedelta(hours=24)
                        within_24h = valid_times[valid_times >= recent_cutoff]
                        timestamp_info['within_24h_count'] = len(within_24h)
                        
                        # Check for future dates
                        future_count = len(valid_times[valid_times > now])
                        timestamp_info['future_dates'] = future_count
                        
                        break
                
                except Exception as e:
                    timestamp_info['parsing_issues'].append(f"Column {col}: {str(e)}")
        
        return timestamp_info
    
    @staticmethod
    def _generate_fixes(report: Dict[str, Any]) -> List[str]:
        """Generate specific code fixes based on diagnostic results"""
        fixes = []
        
        column_issues = report.get('column_issues', {})
        filtering = report.get('filtering_problems', {})
        timestamp_issues = report.get('timestamp_issues', {})
        
        # Column mapping fixes
        if column_issues.get('missing_person_column') and column_issues.get('person_column_candidates'):
            candidates = column_issues['person_column_candidates']
            fixes.append(f"COLUMN FIX: Map '{candidates[0]}' to 'person_id'")
            fixes.append(f"CODE: df = df.rename(columns={{'{candidates[0]}': 'person_id'}})")
        
        if column_issues.get('missing_door_column') and column_issues.get('door_column_candidates'):
            candidates = column_issues['door_column_candidates']
            fixes.append(f"COLUMN FIX: Map '{candidates[0]}' to 'door_id'")
            fixes.append(f"CODE: df = df.rename(columns={{'{candidates[0]}': 'door_id'}})")
        
        # Filtering fixes - FIXED to handle missing key
        string_cleaning_impact = column_issues.get('string_cleaning_impact', {})
        for col, impact in string_cleaning_impact.items():
            if impact.get('lost_values', 0) > 0:
                fixes.append(f"FILTERING FIX: Column '{col}' losing {impact['lost_values']} unique values during cleaning")
                fixes.append(f"CODE: Check cleaning logic for '{col}' column")
        
        # Timestamp fixes
        if not timestamp_issues.get('has_timestamp_column', False):
            fixes.append("TIMESTAMP FIX: No valid timestamp column found")
            fixes.append("CODE: Add timestamp parsing or use all-time counts instead of 24h window")
        elif timestamp_issues.get('within_24h_count', 0) == 0:
            fixes.append("TIMESTAMP FIX: No events within last 24 hours")
            fixes.append("CODE: Use df['person_id'].nunique() instead of time-filtered count")
        
        if not fixes:
            fixes.append("✅ No critical issues detected - data structure looks good")
        
        return fixes
    
    @staticmethod
    def _calculate_corrected_counts(df: pd.DataFrame) -> Dict[str, int]:
        """Calculate what the counts SHOULD be with proper logic"""
        corrected = {
            'total_events': len(df),
            'active_users_all_time': 0,
            'active_doors_all_time': 0,
            'active_users_24h': 0,
            'active_doors_24h': 0
        }
        
        # Find best person column
        person_candidates = [col for col in df.columns 
                           if any(kw in col.lower() for kw in ['person', 'user', 'id', 'badge'])]
        
        # Find best door column  
        door_candidates = [col for col in df.columns 
                         if any(kw in col.lower() for kw in ['door', 'location', 'access', 'point'])]
        
        if person_candidates:
            person_col = person_candidates[0]
            # All-time count
            corrected['active_users_all_time'] = df[person_col].nunique()
            
            # 24h count (if timestamp available)
            timestamp_candidates = [col for col in df.columns 
                                  if any(kw in col.lower() for kw in ['time', 'date', 'stamp'])]
            
            if timestamp_candidates:
                try:
                    time_col = timestamp_candidates[0]
                    df_temp = df.copy()
                    df_temp['parsed_time'] = pd.to_datetime(df_temp[time_col], errors='coerce')
                    
                    recent_cutoff = datetime.now() - timedelta(hours=24)
                    recent_df = df_temp[df_temp['parsed_time'] >= recent_cutoff]
                    corrected['active_users_24h'] = recent_df[person_col].nunique()
                except:
                    corrected['active_users_24h'] = corrected['active_users_all_time']
        
        if door_candidates:
            door_col = door_candidates[0]
            corrected['active_doors_all_time'] = df[door_col].nunique()
            
            # Similar logic for doors...
            if timestamp_candidates:
                try:
                    time_col = timestamp_candidates[0]
                    df_temp = df.copy()
                    df_temp['parsed_time'] = pd.to_datetime(df_temp[time_col], errors='coerce')
                    
                    recent_cutoff = datetime.now() - timedelta(hours=24)
                    recent_df = df_temp[df_temp['parsed_time'] >= recent_cutoff]
                    corrected['active_doors_24h'] = recent_df[door_col].nunique()
                except:
                    corrected['active_doors_24h'] = corrected['active_doors_all_time']
        
        return corrected
    
    @staticmethod
    def _print_diagnostic_report(report: Dict[str, Any]) -> None:
        """Print formatted diagnostic report"""
        print("\n" + "="*60)
        print("🔍 DATA DIAGNOSTICS REPORT")
        print("="*60)
        
        print(f"\n📊 RAW DATA INFO:")
        raw = report['raw_data_info']
        print(f"   • Total Rows: {raw['total_rows']}")
        print(f"   • Columns: {raw['column_names']}")
        print(f"   • Duplicates: {raw['duplicate_count']}")
        
        print(f"\n🔧 COLUMN ISSUES:")
        col = report['column_issues']
        print(f"   • Missing person column: {col['missing_person_column']}")
        print(f"   • Person candidates: {col['person_column_candidates']}")
        print(f"   • Missing door column: {col['missing_door_column']}")
        print(f"   • Door candidates: {col['door_column_candidates']}")
        
        print(f"\n⏰ TIMESTAMP ISSUES:")
        time = report['timestamp_issues']
        print(f"   • Has timestamp: {time['has_timestamp_column']}")
        print(f"   • Events within 24h: {time['within_24h_count']}")
        print(f"   • Timestamp range: {time['timestamp_range']}")
        
        print(f"\n✅ CORRECTED COUNTS:")
        corrected = report['corrected_counts']
        for key, value in corrected.items():
            print(f"   • {key}: {value}")
        
        print(f"\n🛠️ SUGGESTED FIXES:")
        for fix in report['suggested_fixes']:
            print(f"   • {fix}")
        
        print("\n" + "="*60)

# REPLACEMENT FUNCTION FOR YOUR CURRENT ANALYSIS
def fix_zero_actives_issue(df: pd.DataFrame) -> Dict[str, Any]:
    """
    DIRECT REPLACEMENT for your current analysis function
    Call this instead of your existing pattern analysis
    
    Args:
        df: Your DataFrame with 300 events
        
    Returns:
        Fixed analysis results
    """
    # Run diagnostics
    diagnosis = DataDiagnostics.diagnose_zero_actives(df, debug=True)
    
    # Apply fixes automatically
    df_fixed = df.copy()
    
    # Auto-fix column names
    column_issues = diagnosis['column_issues']
    
    if column_issues['person_column_candidates'] and column_issues['missing_person_column']:
        best_person_col = column_issues['person_column_candidates'][0]
        df_fixed = df_fixed.rename(columns={best_person_col: 'person_id'})
        print(f"✅ Mapped '{best_person_col}' to 'person_id'")
    
    if column_issues['door_column_candidates'] and column_issues['missing_door_column']:
        best_door_col = column_issues['door_column_candidates'][0]
        df_fixed = df_fixed.rename(columns={best_door_col: 'door_id'})
        print(f"✅ Mapped '{best_door_col}' to 'door_id'")
    
    # Calculate fixed counts
    corrected_counts = diagnosis['corrected_counts']
    
    # Return results in your expected format
    return {
        'total_events': corrected_counts['total_events'],
        'active_users': corrected_counts['active_users_all_time'],
        'active_doors': corrected_counts['active_doors_all_time'],
        'diagnosis': diagnosis,
        'fixed_dataframe': df_fixed
    }

# TEST FUNCTION
def test_diagnostics():
    """Test the diagnostics with problematic sample data"""
    # Create data that would cause 0 active users/doors with bad logic
    problem_data = pd.DataFrame({
        'user_name': ['John Doe', 'Jane Smith', None, 'Bob Johnson'] * 75,  # 300 rows
        'access_location': ['Main Door', 'Side Door', 'Main Door', None] * 75,
        'result': ['Success', 'Success', 'Failed', 'Success'] * 75,
        'event_time': pd.date_range('2025-06-20', periods=300, freq='5min')  # Old dates
    })
    
    print("🧪 Testing with problematic data structure...")
    results = fix_zero_actives_issue(problem_data)
    
    print(f"\n✅ Fixed Results:")
    print(f"Total Events: {results['total_events']}")
    print(f"Active Users: {results['active_users']}")
    print(f"Active Doors: {results['active_doors']}")
    
    return results

if __name__ == "__main__":
    test_diagnostics()