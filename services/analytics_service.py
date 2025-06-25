#!/usr/bin/env python3
"""
Complete Analytics Service Integration - FIXED VERSION
"""
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Complete analytics service that integrates all data sources"""

    def __init__(self):
        self.database_manager: Optional[Any] = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection"""
        try:
            from config.database_manager import DatabaseManager
            from config.config import get_database_config
            db_config = get_database_config()
            self.database_manager = DatabaseManager(db_config)
            logger.info("Database manager initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            self.database_manager = None

    def get_analytics_from_uploaded_data(self) -> Dict[str, Any]:
        """Get analytics from uploaded files using the FIXED file processor"""
        try:
            # Get uploaded file paths (not pre-processed data)
            from pages.file_upload import get_uploaded_filenames
            uploaded_files = get_uploaded_filenames()

            if not uploaded_files:
                return {'status': 'no_data', 'message': 'No uploaded files available'}

            # Use the FIXED FileProcessor to process files
            from services.file_processor import FileProcessor
            processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})

            all_data: List[pd.DataFrame] = []
            processing_info: List[str] = []
            total_records = 0

            # Process each uploaded file with the FIXED processor
            for file_path in uploaded_files:
                try:
                    print(f"[INFO] Processing uploaded file: {file_path}")

                    # Read the file
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith('.json'):
                        import json
                        with open(file_path, 'r') as f:
                            json_data = json.load(f)
                        df = pd.DataFrame(json_data)
                    elif file_path.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file_path)
                    else:
                        continue

                    # Use the FIXED validation (which includes column mapping)
                    validation_result = processor._validate_data(df)

                    if validation_result['valid']:
                        processed_df = validation_result.get('data', df)
                        processed_df['source_file'] = file_path
                        all_data.append(processed_df)
                        total_records += len(processed_df)
                        processing_info.append(f"✅ {file_path}: {len(processed_df)} records")
                        print(f"[SUCCESS] Processed {len(processed_df)} records from {file_path}")
                    else:
                        error_msg = validation_result.get('error', 'Unknown error')
                        processing_info.append(f"❌ {file_path}: {error_msg}")
                        print(f"[ERROR] Failed to process {file_path}: {error_msg}")

                except Exception as e:
                    processing_info.append(f"❌ {file_path}: Exception - {str(e)}")
                    print(f"[ERROR] Exception processing {file_path}: {e}")

            if not all_data:
                return {
                    'status': 'error',
                    'message': 'No files could be processed successfully',
                    'processing_info': processing_info
                }

            # Combine all successfully processed data
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"[SUCCESS] Combined data: {len(combined_df)} total records")

            # Generate analytics from the properly processed data
            analytics = self._generate_basic_analytics(combined_df)

            # Add processing information
            analytics.update({
                'data_source': 'uploaded_files_fixed',
                'total_files_processed': len(all_data),
                'total_files_attempted': len(uploaded_files),
                'processing_info': processing_info,
                'total_events': total_records,
                'active_users': combined_df['person_id'].nunique() if 'person_id' in combined_df.columns else 0,
                'active_doors': combined_df['door_id'].nunique() if 'door_id' in combined_df.columns else 0,
                'timestamp': datetime.now().isoformat()
            })

            return analytics

        except Exception as e:
            logger.error(f"Error getting analytics from uploaded data: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_analytics_by_source(self, source: str) -> Dict[str, Any]:
        """Get analytics from specified source - FIXED for uploaded data"""
        if source == "sample":
            return self._generate_sample_analytics()
        elif source == "uploaded":
            return self._get_real_uploaded_data()  # FIXED METHOD
        elif source == "database":
            return self._get_database_analytics()
        else:
            return {'status': 'error', 'message': f'Unknown source: {source}'}

    def _get_real_uploaded_data(self) -> Dict[str, Any]:
        """FIXED: Actually access your uploaded 395K records"""
        try:
            from pages.file_upload import get_uploaded_data

            uploaded_data = get_uploaded_data()
            if not uploaded_data:
                return {'status': 'no_data', 'message': 'No uploaded files available'}

            print(f"🔍 Processing {len(uploaded_data)} uploaded files...")

            all_dfs = []
            total_original_rows = 0

            for filename, df in uploaded_data.items():
                print(f"📄 Processing {filename}: {len(df):,} rows")

                # Map YOUR specific column names (Demo3_data.csv format)
                column_mapping = {
                    'Timestamp': 'timestamp',
                    'Person ID': 'person_id',
                    'Token ID': 'token_id',
                    'Device name': 'door_id',
                    'Access result': 'access_result'
                }

                # Apply column mapping
                df_mapped = df.rename(columns=column_mapping)

                # Clean timestamp
                if 'timestamp' in df_mapped.columns:
                    df_mapped['timestamp'] = pd.to_datetime(df_mapped['timestamp'], errors='coerce')

                # Clean string columns
                for col in ['person_id', 'door_id', 'access_result']:
                    if col in df_mapped.columns:
                        df_mapped[col] = df_mapped[col].astype(str).str.strip()

                all_dfs.append(df_mapped)
                total_original_rows += len(df)
                print(f"✅ Mapped columns: {list(df_mapped.columns)}")

            # Combine all data
            combined_df = pd.concat(all_dfs, ignore_index=True)

            print(f"🎉 COMBINED: {len(combined_df):,} total rows")

            # Generate analytics from YOUR actual data
            total_events = len(combined_df)
            active_users = combined_df['person_id'].nunique() if 'person_id' in combined_df.columns else 0
            active_doors = combined_df['door_id'].nunique() if 'door_id' in combined_df.columns else 0

            # Date range
            date_range = {'start': 'Unknown', 'end': 'Unknown'}
            if 'timestamp' in combined_df.columns:
                valid_timestamps = combined_df['timestamp'].dropna()
                if not valid_timestamps.empty:
                    date_range = {
                        'start': str(valid_timestamps.min().date()),
                        'end': str(valid_timestamps.max().date())
                    }

            # Access patterns
            access_patterns = {}
            if 'access_result' in combined_df.columns:
                access_patterns = combined_df['access_result'].value_counts().to_dict()

            # Top users for display
            top_users = []
            if 'person_id' in combined_df.columns:
                user_counts = combined_df['person_id'].value_counts().head(10)
                top_users = [
                    {'user_id': user_id, 'count': int(count)}
                    for user_id, count in user_counts.items()
                ]

            # Top doors for display
            top_doors = []
            if 'door_id' in combined_df.columns:
                door_counts = combined_df['door_id'].value_counts().head(10)
                top_doors = [
                    {'door_id': door_id, 'count': int(count)}
                    for door_id, count in door_counts.items()
                ]

            analytics_result = {
                'total_events': total_events,
                'active_users': active_users,
                'active_doors': active_doors,
                'unique_users': active_users,  # Fallback
                'unique_doors': active_doors,  # Fallback
                'data_source': 'uploaded',  # CRITICAL: Mark as uploaded
                'date_range': date_range,
                'access_patterns': access_patterns,
                'top_users': top_users,
                'top_doors': top_doors,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'files_processed': len(uploaded_data),
                'original_total_rows': total_original_rows
            }

            print(f"📊 ANALYTICS RESULT:")
            print(f"   Total Events: {total_events:,}")
            print(f"   Active Users: {active_users:,}")
            print(f"   Active Doors: {active_doors:,}")

            return analytics_result

        except Exception as e:
            logger.error(f"Error processing uploaded data: {e}")
            return {
                'status': 'error',
                'message': f'Error processing uploaded data: {str(e)}',
                'total_events': 0
            }

    def _generate_sample_analytics(self) -> Dict[str, Any]:
        """Generate sample analytics data"""
        # Create sample DataFrame
        sample_data = pd.DataFrame({
            'user_id': ['user_001', 'user_002', 'user_003'] * 100,
            'door_id': ['door_A', 'door_B', 'door_C'] * 100,
            'timestamp': pd.date_range('2024-01-01', periods=300, freq='1H'),
            'access_result': (['Granted'] * 250) + (['Denied'] * 50)
        })

        return self._generate_basic_analytics(sample_data)

    def _generate_basic_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate basic analytics from DataFrame - JSON safe version"""
        try:
            analytics = {
                'status': 'success',
                'total_events': len(df),  # Changed from 'total_rows' to 'total_events'
                'total_rows': len(df),    # Keep both for compatibility
                'total_columns': len(df.columns),
                'summary': {},
                'timestamp': datetime.now().isoformat(),
            }

            # Basic statistics for each column
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    analytics['summary'][col] = {
                        'type': 'numeric',
                        'mean': float(df[col].mean()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'null_count': int(df[col].isnull().sum()),
                    }
                else:
                    value_counts = df[col].value_counts().head(10)
                    analytics['summary'][col] = {
                        'type': 'categorical',
                        'unique_values': int(df[col].nunique()),
                        # Ensure keys/values are JSON serialisable
                        'top_values': {str(k): int(v) for k, v in value_counts.items()},
                        'null_count': int(df[col].isnull().sum()),
                    }

            return analytics

        except Exception as e:
            logger.error(f"Error generating basic analytics: {e}")
            return {'status': 'error', 'message': str(e)}

    def _get_analytics_with_fixed_processor(self) -> Dict[str, Any]:
        """Get analytics using the FIXED file processor"""

        csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"
        json_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/key_fob_access_log_sample.json"

        try:
            from services.file_processor import FileProcessor
            import pandas as pd
            import json

            processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})
            all_data = []

            # Process CSV with FIXED processor
            if os.path.exists(csv_file):
                df_csv = pd.read_csv(csv_file)
                result = processor._validate_data(df_csv)
                if result['valid']:
                    processed_df = result['data']
                    processed_df['source_file'] = 'csv'
                    all_data.append(processed_df)

            # Process JSON with FIXED processor
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                df_json = pd.DataFrame(json_data)
                result = processor._validate_data(df_json)
                if result['valid']:
                    processed_df = result['data']
                    processed_df['source_file'] = 'json'
                    all_data.append(processed_df)

            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)

                return {
                    'status': 'success',
                    'total_events': len(combined_df),
                    'active_users': combined_df['person_id'].nunique(),
                    'active_doors': combined_df['door_id'].nunique(),
                    'data_source': 'fixed_processor',
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error in fixed processor analytics: {e}")
            return {'status': 'error', 'message': str(e)}

        return {'status': 'no_data', 'message': 'Files not available'}

    def _get_database_analytics(self) -> Dict[str, Any]:
        """Get analytics from database"""
        if not self.database_manager:
            return {'status': 'error', 'message': 'Database not available'}

        try:
            # Implement database analytics here
            return {
                'status': 'success',
                'message': 'Database analytics not yet implemented',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        health = {
            'service': 'healthy',
            'timestamp': datetime.now().isoformat()
        }

        # Check database
        if self.database_manager:
            try:
                health['database'] = 'healthy' if self.database_manager.health_check() else 'unhealthy'
            except:
                health['database'] = 'unhealthy'
        else:
            health['database'] = 'not_configured'

        # Check file upload
        try:
            from pages.file_upload import get_uploaded_filenames
            health['uploaded_files'] = len(get_uploaded_filenames())
        except ImportError:
            health['uploaded_files'] = 'not_available'

        return health

    def get_data_source_options(self) -> List[Dict[str, str]]:
        """Get available data source options"""
        options = [
            {"label": "Sample Data", "value": "sample"}
        ]

        # Check for uploaded data
        try:
            from pages.file_upload import get_uploaded_filenames
            uploaded_files = get_uploaded_filenames()
            if uploaded_files:
                options.append({"label": f"Uploaded Files ({len(uploaded_files)})", "value": "uploaded"})
        except ImportError:
            pass

        # Check for database
        if self.database_manager and self.database_manager.health_check():
            options.append({"label": "Database", "value": "database"})

        return options

    def get_date_range_options(self) -> Dict[str, str]:
        """Get default date range options"""
        from datetime import datetime, timedelta
        return {
            'start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end': datetime.now().strftime('%Y-%m-%d')
        }

    def get_analytics_status(self) -> Dict[str, Any]:
        """Get current analytics status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'data_sources_available': len(self.get_data_source_options()),
            'service_health': self.health_check()
        }

        try:
            from pages.file_upload import get_uploaded_filenames
            status['uploaded_files'] = len(get_uploaded_filenames())
        except ImportError:
            status['uploaded_files'] = 0

        return status

# Global service instance
_analytics_service: Optional[AnalyticsService] = None

def get_analytics_service() -> AnalyticsService:
    """Get global analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

def create_analytics_service() -> AnalyticsService:
    """Create new analytics service instance"""
    return AnalyticsService()

__all__ = ['AnalyticsService', 'get_analytics_service', 'create_analytics_service']
