#!/usr/bin/env python3
"""
Security Data Analysis Module
Modular, testable components for security pattern analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityLevel(Enum):
    """Data quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class AnalysisResults:
    """Container for analysis results"""
    total_events: int
    active_users: int
    active_doors: int
    data_quality: DataQualityLevel
    patterns: Dict[str, Any]
    recommendations: List[str]
    processing_time: float

class SecurityDataValidator:
    """Validates and diagnoses security data issues"""
    
    @staticmethod
    def diagnose_data_issues(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Diagnose why active users/doors might be 0
        
        Args:
            df: DataFrame with security events
            
        Returns:
            Dict with diagnostic information
        """
        diagnosis = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict(),
            'unique_values': {},
            'issues': []
        }
        
        # Check for key columns
        expected_columns = ['person_id', 'door_id', 'access_result', 'timestamp']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            diagnosis['issues'].append(f"Missing columns: {missing_columns}")
        
        # Analyze unique values in key columns
        for col in df.columns:
            if col in expected_columns:
                unique_vals = df[col].nunique()
                sample_vals = df[col].unique()[:5].tolist()
                diagnosis['unique_values'][col] = {
                    'count': unique_vals,
                    'samples': sample_vals
                }
                
                # Check for empty/null values
                null_pct = (df[col].isnull().sum() / len(df)) * 100
                if null_pct > 50:
                    diagnosis['issues'].append(f"{col} has {null_pct:.1f}% null values")
        
        return diagnosis

class SecurityPatternAnalyzer:
    """Analyzes security patterns and generates insights"""
    
    def __init__(self):
        self.validator = SecurityDataValidator()
    
    def analyze_patterns(self, df: pd.DataFrame) -> AnalysisResults:
        """
        Main analysis function - replacement for existing pattern analysis
        
        Args:
            df: DataFrame with security events
            
        Returns:
            AnalysisResults object with comprehensive analysis
        """
        start_time = datetime.now()
        
        # First, diagnose data issues
        diagnosis = self.validator.diagnose_data_issues(df)
        logger.info(f"Data diagnosis: {diagnosis}")
        
        # Clean and prepare data
        df_clean = self._clean_data(df)
        
        # Calculate metrics
        total_events = len(df_clean)
        active_users = self._calculate_active_users(df_clean)
        active_doors = self._calculate_active_doors(df_clean)
        
        # Analyze patterns
        patterns = self._extract_patterns(df_clean)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(df_clean, patterns)
        
        # Assess data quality
        data_quality = self._assess_data_quality(df_clean, diagnosis)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResults(
            total_events=total_events,
            active_users=active_users,
            active_doors=active_doors,
            data_quality=data_quality,
            patterns=patterns,
            recommendations=recommendations,
            processing_time=processing_time
        )
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize data - REPLACEMENT for existing cleaning
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Standardize column names (handle case variations)
        column_mapping = {
            'person_id': ['person_id', 'personid', 'user_id', 'userid', 'person', 'user'],
            'door_id': ['door_id', 'doorid', 'door', 'access_point', 'location'],
            'access_result': ['access_result', 'result', 'status', 'outcome'],
            'timestamp': ['timestamp', 'time', 'datetime', 'date_time']
        }
        
        for standard_name, variations in column_mapping.items():
            for col in df_clean.columns:
                if col.lower().strip() in [v.lower() for v in variations]:
                    df_clean = df_clean.rename(columns={col: standard_name})
                    break
        
        # Remove rows with critical null values
        critical_columns = ['person_id', 'door_id']
        for col in critical_columns:
            if col in df_clean.columns:
                df_clean = df_clean.dropna(subset=[col])
        
        # Clean string columns
        string_columns = ['person_id', 'door_id', 'access_result']
        for col in string_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                # Remove 'None', 'nan', empty strings
                df_clean = df_clean[~df_clean[col].isin(['None', 'nan', '', 'null'])]
        
        # Parse timestamps
        if 'timestamp' in df_clean.columns:
            df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], errors='coerce')
            df_clean = df_clean.dropna(subset=['timestamp'])
        
        logger.info(f"Data cleaned: {len(df)} -> {len(df_clean)} rows")
        return df_clean
    
    def _calculate_active_users(self, df: pd.DataFrame) -> int:
        """
        Calculate active users - REPLACEMENT for existing calculation
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Number of active users
        """
        if 'person_id' not in df.columns or df.empty:
            return 0
        
        # Define "active" as users with activity in last 24 hours
        if 'timestamp' in df.columns:
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_df = df[df['timestamp'] >= recent_cutoff]
            return recent_df['person_id'].nunique()
        else:
            # If no timestamp, count all unique users
            return df['person_id'].nunique()
    
    def _calculate_active_doors(self, df: pd.DataFrame) -> int:
        """
        Calculate active doors - REPLACEMENT for existing calculation
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Number of active doors
        """
        if 'door_id' not in df.columns or df.empty:
            return 0
        
        # Define "active" as doors with activity in last 24 hours
        if 'timestamp' in df.columns:
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_df = df[df['timestamp'] >= recent_cutoff]
            return recent_df['door_id'].nunique()
        else:
            # If no timestamp, count all unique doors
            return df['door_id'].nunique()
    
    def _extract_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract security patterns - REPLACEMENT for existing pattern extraction
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary of patterns
        """
        patterns = {
            'security_score': 100,
            'failed_attempts': 0,
            'suspicious_patterns': 0,
            'hourly_distribution': {},
            'daily_distribution': {},
            'access_results': {},
            'user_activity': {},
            'door_activity': {}
        }
        
        if df.empty:
            return patterns
        
        # Access result analysis
        if 'access_result' in df.columns:
            patterns['access_results'] = df['access_result'].value_counts().to_dict()
            
            # Count failed attempts
            failed_keywords = ['denied', 'failed', 'fail', 'reject', 'unauthorized']
            failed_count = 0
            for result in df['access_result'].values:
                if any(keyword in str(result).lower() for keyword in failed_keywords):
                    failed_count += 1
            patterns['failed_attempts'] = failed_count
            
            # Calculate security score
            if len(df) > 0:
                success_rate = ((len(df) - failed_count) / len(df)) * 100
                patterns['security_score'] = round(success_rate)
        
        # Temporal patterns
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
            
            patterns['hourly_distribution'] = df['hour'].value_counts().to_dict()
            patterns['daily_distribution'] = df['day_of_week'].value_counts().to_dict()
        
        # User activity patterns
        if 'person_id' in df.columns:
            user_counts = df['person_id'].value_counts()
            patterns['user_activity'] = {
                'most_active': user_counts.head(5).to_dict(),
                'total_unique': len(user_counts)
            }
        
        # Door activity patterns
        if 'door_id' in df.columns:
            door_counts = df['door_id'].value_counts()
            patterns['door_activity'] = {
                'most_used': door_counts.head(5).to_dict(),
                'total_unique': len(door_counts)
            }
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame, patterns: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations - REPLACEMENT for existing recommendations
        
        Args:
            df: Cleaned DataFrame
            patterns: Extracted patterns
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Data quality recommendations
        if df.empty:
            recommendations.append("⚠️ No valid data found - check data source and column mappings")
            return recommendations
        
        if patterns['failed_attempts'] > 0:
            recommendations.append(f"🔍 Investigate {patterns['failed_attempts']} failed access attempts")
        
        if patterns['security_score'] < 95:
            recommendations.append(f"🚨 Security score is {patterns['security_score']}% - review security protocols")
        
        # Activity-based recommendations
        if patterns['user_activity']['total_unique'] == 0:
            recommendations.append("👥 No user activity detected - verify person_id column format")
        
        if patterns['door_activity']['total_unique'] == 0:
            recommendations.append("🚪 No door activity detected - verify door_id column format")
        
        # Temporal recommendations
        if 'hourly_distribution' in patterns and patterns['hourly_distribution']:
            after_hours = sum(patterns['hourly_distribution'].get(hour, 0) for hour in range(22, 24) + list(range(0, 6)))
            if after_hours > 0:
                recommendations.append(f"🌙 {after_hours} after-hours access events detected - review for anomalies")
        
        if not recommendations:
            recommendations.append("✅ No critical security issues detected")
        
        return recommendations
    
    def _assess_data_quality(self, df: pd.DataFrame, diagnosis: Dict[str, Any]) -> DataQualityLevel:
        """
        Assess overall data quality
        
        Args:
            df: Cleaned DataFrame
            diagnosis: Diagnostic information
            
        Returns:
            DataQualityLevel enum
        """
        if df.empty:
            return DataQualityLevel.CRITICAL
        
        issues = len(diagnosis.get('issues', []))
        null_percentage = sum(df.isnull().sum()) / (len(df) * len(df.columns)) * 100
        
        if issues == 0 and null_percentage < 5:
            return DataQualityLevel.EXCELLENT
        elif issues <= 2 and null_percentage < 15:
            return DataQualityLevel.GOOD
        elif issues <= 5 and null_percentage < 30:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL

# TESTING FUNCTIONS
def test_analyzer_with_sample_data():
    """Test function to validate the analyzer"""
    # Create sample data
    sample_data = pd.DataFrame({
        'person_id': ['USER001', 'USER002', 'USER001', 'USER003'] * 75,  # 300 rows
        'door_id': ['DOOR_A', 'DOOR_B', 'DOOR_A', 'DOOR_C'] * 75,
        'access_result': ['Granted', 'Granted', 'Denied', 'Granted'] * 75,
        'timestamp': pd.date_range('2025-06-24', periods=300, freq='5min')
    })
    
    analyzer = SecurityPatternAnalyzer()
    results = analyzer.analyze_patterns(sample_data)
    
    print(f"✅ Test Results:")
    print(f"Total Events: {results.total_events}")
    print(f"Active Users: {results.active_users}")
    print(f"Active Doors: {results.active_doors}")
    print(f"Data Quality: {results.data_quality.value}")
    print(f"Security Score: {results.patterns['security_score']}")
    
    return results

if __name__ == "__main__":
    # Run test
    test_results = test_analyzer_with_sample_data()