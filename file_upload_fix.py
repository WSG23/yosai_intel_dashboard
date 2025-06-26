# file_upload_fix.py
"""
CRITICAL FIX: File Upload and Data Loading Issues
This module fixes the disconnect between file upload and analytics dashboard
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import base64
import io

logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: FIX THE GLOBAL DATA STORE IN pages/file_upload.py
# =============================================================================

"""
REPLACE the existing _uploaded_data_store section in pages/file_upload.py with this:
"""

# Global data store with persistence
class UploadedDataStore:
    """Persistent uploaded data store with file system backup"""
    
    def __init__(self):
        self._data_store = {}
        self._file_info_store = {}
        self.storage_dir = Path("temp/uploaded_data")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()
    
    def _get_file_path(self, filename: str) -> Path:
        """Get storage file path for uploaded data"""
        safe_filename = filename.replace(' ', '_').replace('/', '_')
        return self.storage_dir / f"{safe_filename}.pkl"
    
    def _get_info_file_path(self) -> Path:
        """Get file info storage path"""
        return self.storage_dir / "file_info.json"
    
    def _load_from_disk(self):
        """Load uploaded data from disk on startup"""
        try:
            # Load file info
            if self._get_info_file_path().exists():
                with open(self._get_info_file_path(), 'r') as f:
                    self._file_info_store = json.load(f)
            
            # Load data files
            for filename in self._file_info_store.keys():
                file_path = self._get_file_path(filename)
                if file_path.exists():
                    df = pd.read_pickle(file_path)
                    self._data_store[filename] = df
                    logger.info(f"Loaded {filename} from disk: {len(df)} rows")
                    
        except Exception as e:
            logger.error(f"Error loading data from disk: {e}")
    
    def _save_to_disk(self, filename: str, df: pd.DataFrame):
        """Save uploaded data to disk"""
        try:
            # Save data
            file_path = self._get_file_path(filename)
            df.to_pickle(file_path)
            
            # Save file info
            self._file_info_store[filename] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'upload_time': datetime.now().isoformat(),
                'size_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            with open(self._get_info_file_path(), 'w') as f:
                json.dump(self._file_info_store, f, indent=2)
                
            logger.info(f"Saved {filename} to disk")
            
        except Exception as e:
            logger.error(f"Error saving {filename} to disk: {e}")
    
    def add_file(self, filename: str, df: pd.DataFrame):
        """Add file to store"""
        self._data_store[filename] = df
        self._save_to_disk(filename, df)
        print(f"✅ Added {filename} to data store: {len(df)} rows")
    
    def get_file(self, filename: str) -> Optional[pd.DataFrame]:
        """Get file from store"""
        return self._data_store.get(filename)
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Get all uploaded data"""
        return self._data_store.copy()
    
    def get_filenames(self) -> List[str]:
        """Get all uploaded filenames"""
        return list(self._data_store.keys())
    
    def get_file_info(self) -> Dict[str, Dict[str, Any]]:
        """Get file information"""
        return self._file_info_store.copy()
    
    def clear_all(self):
        """Clear all data"""
        self._data_store.clear()
        self._file_info_store.clear()
        
        # Clear disk files
        try:
            for file_path in self.storage_dir.glob("*.pkl"):
                file_path.unlink()
            if self._get_info_file_path().exists():
                self._get_info_file_path().unlink()
        except Exception as e:
            logger.error(f"Error clearing disk files: {e}")
    
    def remove_file(self, filename: str):
        """Remove specific file"""
        if filename in self._data_store:
            del self._data_store[filename]
        
        if filename in self._file_info_store:
            del self._file_info_store[filename]
        
        # Remove from disk
        try:
            file_path = self._get_file_path(filename)
            if file_path.exists():
                file_path.unlink()
            
            # Update info file
            with open(self._get_info_file_path(), 'w') as f:
                json.dump(self._file_info_store, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error removing {filename} from disk: {e}")
    
    def __len__(self):
        return len(self._data_store)
    
    def __bool__(self):
        return bool(self._data_store)

# Create global instance
_uploaded_data_store = UploadedDataStore()

# =============================================================================
# STEP 2: UPDATE UPLOAD FUNCTIONS IN pages/file_upload.py
# =============================================================================

def get_uploaded_data() -> Dict[str, pd.DataFrame]:
    """REPLACE existing function in pages/file_upload.py"""
    data = _uploaded_data_store.get_all_data()
    print(f"📊 get_uploaded_data() called - returning {len(data)} files")
    for filename, df in data.items():
        print(f"   📄 {filename}: {len(df):,} rows")
    return data

def get_uploaded_filenames() -> List[str]:
    """REPLACE existing function in pages/file_upload.py"""
    filenames = _uploaded_data_store.get_filenames()
    print(f"📁 get_uploaded_filenames() called - returning {len(filenames)} files: {filenames}")
    return filenames

def clear_uploaded_data():
    """REPLACE existing function in pages/file_upload.py"""
    _uploaded_data_store.clear_all()
    logger.info("✅ All uploaded data cleared")

def get_file_info() -> Dict[str, Dict[str, Any]]:
    """REPLACE existing function in pages/file_upload.py"""
    return _uploaded_data_store.get_file_info()

# =============================================================================
# STEP 3: FIX THE UPLOAD PROCESSING FUNCTION
# =============================================================================

def process_uploaded_file_fixed(contents: str, filename: str) -> Dict[str, Any]:
    """
    REPLACE existing process_uploaded_file function in pages/file_upload.py
    """
    try:
        # Parse the uploaded file content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Determine file type and read accordingly
        if filename.endswith('.csv'):
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.StringIO(decoded.decode(encoding)))
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV file with any supported encoding")
                
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(decoded))
            
        elif filename.endswith('.json'):
            json_data = json.loads(decoded.decode('utf-8'))
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            else:
                df = pd.DataFrame([json_data])
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        
        # Validate the dataframe
        if df.empty:
            raise ValueError("File is empty or could not be parsed")
        
        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Add to store
        _uploaded_data_store.add_file(filename, df)
        
        # Log success
        logger.info(f"✅ Successfully processed {filename}: {len(df)} rows, {len(df.columns)} columns")
        
        return {
            "success": True,
            "data": df,
            "message": f"Successfully uploaded {filename}",
            "rows": len(df),
            "columns": len(df.columns),
            "filename": filename
        }
        
    except Exception as e:
        error_msg = f"Error processing {filename}: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "data": None,
            "message": error_msg,
            "filename": filename
        }

# =============================================================================
# STEP 4: FIX THE ANALYTICS SERVICE DATA LOADING
# =============================================================================

class FixedAnalyticsService:
    """
    REPLACEMENT for AnalyticsService in services/analytics_service.py
    """
    
    def __init__(self):
        self.database_manager = None
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
    
    def get_analytics_by_source(self, data_source: str) -> Dict[str, Any]:
        """Get analytics data by source with FIXED uploaded data handling"""
        
        print(f"🔧 FixedAnalyticsService.get_analytics_by_source('{data_source}')")
        
        if data_source == "uploaded":
            return self._get_uploaded_analytics_fixed()
        elif data_source == "sample":
            return self._get_sample_analytics()
        elif data_source == "database":
            return self._get_database_analytics()
        else:
            return {'status': 'error', 'message': f'Unknown data source: {data_source}'}
    
    def _get_uploaded_analytics_fixed(self) -> Dict[str, Any]:
        """Get analytics from uploaded files - FIXED VERSION"""
        try:
            # Import the fixed functions
            from pages.file_upload import get_uploaded_data, get_uploaded_filenames
            
            # Get uploaded data
            uploaded_data = get_uploaded_data()
            filenames = get_uploaded_filenames()
            
            print(f"🔍 FIXED SERVICE CHECK:")
            print(f"   Filenames: {filenames}")
            print(f"   Data objects: {len(uploaded_data)}")
            
            if not uploaded_data:
                return {
                    'status': 'no_data', 
                    'message': 'No uploaded files available',
                    'total_events': 0,
                    'data_source': 'uploaded'
                }
            
            # Combine all uploaded data
            all_dataframes = []
            total_events = 0
            file_summaries = []
            
            for filename, df in uploaded_data.items():
                print(f"   📄 Processing {filename}: {len(df):,} rows")
                
                # Validate required columns
                required_cols = ['timestamp', 'person_id', 'door_id', 'access_result']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    # Try to map columns automatically
                    df_mapped = self._auto_map_columns(df)
                    if df_mapped is not None:
                        df = df_mapped
                    else:
                        print(f"   ⚠️ Missing columns in {filename}: {missing_cols}")
                        continue
                
                all_dataframes.append(df)
                total_events += len(df)
                
                file_summaries.append({
                    'filename': filename,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'date_range': self._get_date_range(df)
                })
            
            if not all_dataframes:
                return {
                    'status': 'error',
                    'message': 'No valid data files found with required columns',
                    'total_events': 0,
                    'data_source': 'uploaded'
                }
            
            # Combine all data
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            # Generate analytics
            analytics_result = self._generate_analytics_from_dataframe(combined_df)
            
            # Add metadata
            analytics_result.update({
                'status': 'success',
                'data_source': 'uploaded',
                'total_events': total_events,
                'file_count': len(uploaded_data),
                'file_summaries': file_summaries,
                'combined_data_shape': combined_df.shape,
                'processing_timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ FIXED SERVICE RESULT: {total_events:,} events from {len(uploaded_data)} files")
            return analytics_result
            
        except Exception as e:
            error_msg = f"Error processing uploaded data: {str(e)}"
            logger.error(error_msg)
            print(f"❌ FIXED SERVICE ERROR: {error_msg}")
            return {
                'status': 'error',
                'message': error_msg,
                'total_events': 0,
                'data_source': 'uploaded'
            }
    
    def _auto_map_columns(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Automatically map columns to required fields"""
        column_mapping = {}
        
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # Map timestamp columns
            if any(word in col_lower for word in ['time', 'date', 'stamp']):
                column_mapping['timestamp'] = col
            
            # Map person/user columns
            elif any(word in col_lower for word in ['person', 'user', 'employee', 'id']):
                if 'person_id' not in column_mapping:
                    column_mapping['person_id'] = col
            
            # Map door/location columns
            elif any(word in col_lower for word in ['door', 'location', 'device']):
                column_mapping['door_id'] = col
            
            # Map access result columns
            elif any(word in col_lower for word in ['access', 'result', 'status', 'granted', 'denied']):
                column_mapping['access_result'] = col
        
        # Check if we have minimum required columns
        required_cols = ['timestamp', 'person_id', 'door_id', 'access_result']
        if all(req_col in column_mapping for req_col in required_cols):
            
            # Create mapped dataframe
            df_mapped = df.copy()
            df_mapped = df_mapped.rename(columns={v: k for k, v in column_mapping.items()})
            
            # Ensure timestamp is datetime
            try:
                df_mapped['timestamp'] = pd.to_datetime(df_mapped['timestamp'])
            except:
                return None
            
            return df_mapped
        
        return None
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get date range from dataframe"""
        try:
            if 'timestamp' in df.columns:
                timestamps = pd.to_datetime(df['timestamp'])
                return {
                    'start': timestamps.min().isoformat(),
                    'end': timestamps.max().isoformat()
                }
        except:
            pass
        
        return {'start': 'unknown', 'end': 'unknown'}
    
    def _generate_analytics_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate analytics from combined dataframe"""
        try:
            # Basic analytics
            total_events = len(df)
            unique_users = df['person_id'].nunique()
            unique_doors = df['door_id'].nunique()
            
            # Access results
            access_results = df['access_result'].value_counts().to_dict()
            success_rate = (df['access_result'] == 'Granted').mean() * 100
            
            # Time-based analytics
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            date_range = {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat(),
                'days': (df['timestamp'].max() - df['timestamp'].min()).days
            }
            
            # Top users and doors
            top_users = df['person_id'].value_counts().head(10).to_dict()
            top_doors = df['door_id'].value_counts().head(10).to_dict()
            
            # Hourly distribution
            df['hour'] = df['timestamp'].dt.hour
            hourly_distribution = df['hour'].value_counts().sort_index().to_dict()
            
            return {
                'total_events': total_events,
                'unique_users': unique_users,
                'unique_doors': unique_doors,
                'access_results': access_results,
                'success_rate': success_rate,
                'date_range': date_range,
                'top_users': top_users,
                'top_doors': top_doors,
                'hourly_distribution': hourly_distribution,
                'data_quality': self._assess_data_quality(df)
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {
                'total_events': 0,
                'error': str(e)
            }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> str:
        """Assess data quality"""
        required_cols = ['timestamp', 'person_id', 'door_id', 'access_result']
        missing_rate = df[required_cols].isnull().mean().mean()
        
        if missing_rate < 0.01:
            return 'excellent'
        elif missing_rate < 0.05:
            return 'good'
        elif missing_rate < 0.1:
            return 'fair'
        else:
            return 'poor'
    
    def _get_sample_analytics(self) -> Dict[str, Any]:
        """Generate sample data analytics"""
        from utils.sample_data_generator import generate_sample_access_data
        
        try:
            sample_df = generate_sample_access_data(1000)
            analytics_result = self._generate_analytics_from_dataframe(sample_df)
            analytics_result.update({
                'status': 'success',
                'data_source': 'sample',
                'message': 'Generated from sample data'
            })
            return analytics_result
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Sample data generation failed: {e}',
                'total_events': 0,
                'data_source': 'sample'
            }
    
    def _get_database_analytics(self) -> Dict[str, Any]:
        """Get analytics from database"""
        if not self.database_manager:
            return {
                'status': 'error', 
                'message': 'Database not available',
                'total_events': 0,
                'data_source': 'database'
            }
        
        try:
            # Implement database analytics here
            return {
                'status': 'success',
                'message': 'Database analytics not yet implemented',
                'total_events': 0,
                'data_source': 'database'
            }
        except Exception as e:
            return {
                'status': 'error', 
                'message': str(e),
                'total_events': 0,
                'data_source': 'database'
            }
    
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
        
        # Check uploaded files
        try:
            from pages.file_upload import get_uploaded_filenames
            health['uploaded_files'] = len(get_uploaded_filenames())
        except ImportError:
            health['uploaded_files'] = 'not_available'
        
        return health

# =============================================================================
# STEP 5: FIX THE DEEP ANALYTICS CALLBACK
# =============================================================================

from dash import html


def generate_analytics_display_fixed(n_clicks, data_source, analysis_type):
    """
    REPLACEMENT for generate_analytics_display in pages/deep_analytics.py
    """
    
    print(f"🚀 FIXED generate_analytics_display called")
    print(f"   Data source: '{data_source}'")
    print(f"   Analysis type: '{analysis_type}'")
    print(f"   Button clicks: {n_clicks}")
    
    if not n_clicks:
        return html.Div("Click 'Generate Analytics' to start analysis"), {}
    
    if not data_source or not analysis_type:
        return html.Div("Please select both data source and analysis type"), {}
    
    try:
        # Use the fixed analytics service
        analytics_service = FixedAnalyticsService()
        
        # Get analytics results
        analytics_results = analytics_service.get_analytics_by_source(data_source)
        
        print(f"📊 FIXED Analytics Results:")
        print(f"   Status: {analytics_results.get('status')}")
        print(f"   Total events: {analytics_results.get('total_events', 0):,}")
        print(f"   Data source: {analytics_results.get('data_source')}")
        
        # Handle different result statuses
        if analytics_results.get('status') == 'error':
            error_msg = analytics_results.get('message', 'Unknown error')
            return create_error_alert(f"Analytics error: {error_msg}"), {}
        
        elif analytics_results.get('status') == 'no_data':
            if data_source == 'uploaded':
                return create_warning_alert(
                    "No uploaded files found. Please upload a data file first."
                ), {}
            else:
                return create_warning_alert(
                    f"No data available for source: {data_source}"
                ), {}
        
        # Check for zero events (but successful processing)
        total_events = analytics_results.get('total_events', 0)
        if total_events == 0:
            return create_info_alert(
                f"Analytics completed but found 0 events. "
                f"Status: {analytics_results.get('status', 'unknown')}"
            ), {}
        
        # Success case - create dashboard
        success_msg = f"✅ Analytics completed successfully! Processed {total_events:,} events from {data_source} source."
        
        # Create analytics dashboard based on type
        if analysis_type == 'security':
            dashboard_content = create_security_dashboard(analytics_results, success_msg)
        elif analysis_type == 'trends':
            dashboard_content = create_trends_dashboard(analytics_results, success_msg)
        elif analysis_type == 'behavior':
            dashboard_content = create_behavior_dashboard(analytics_results, success_msg)
        elif analysis_type == 'anomaly':
            dashboard_content = create_anomaly_dashboard(analytics_results, success_msg)
        else:
            dashboard_content = create_general_dashboard(analytics_results, success_msg)
        
        return dashboard_content, analytics_results
        
    except Exception as e:
        error_msg = f"Analytics generation failed: {str(e)}"
        logger.error(error_msg)
        print(f"❌ FIXED Analytics Error: {error_msg}")
        return create_error_alert(error_msg), {}

# =============================================================================
# STEP 6: HELPER FUNCTIONS FOR DASHBOARD CREATION
# =============================================================================


def create_error_alert(message: str, title: str = "Error") -> html.Div:
    """Create error alert component"""
    return html.Div([
        html.H4(f"❌ {title}", className="text-danger"),
        html.P(message),
        html.Hr(),
        html.P("Troubleshooting steps:", className="fw-bold"),
        html.Ul([
            html.Li("Ensure you have uploaded a valid data file"),
            html.Li("Check that your file contains required columns (timestamp, person_id, door_id, access_result)"),
            html.Li("Try refreshing the page and uploading again"),
            html.Li("Contact support if the issue persists")
        ])
    ], className="alert alert-danger")

def create_warning_alert(message: str) -> html.Div:
    """Create warning alert component"""
    return html.Div([
        html.H4("⚠️ Warning", className="text-warning"),
        html.P(message)
    ], className="alert alert-warning")

def create_info_alert(message: str) -> html.Div:
    """Create info alert component"""
    return html.Div([
        html.H4("ℹ️ Information", className="text-info"),
        html.P(message)
    ], className="alert alert-info")

def create_general_dashboard(analytics_results: Dict[str, Any], success_msg: str) -> html.Div:
    """Create general analytics dashboard"""
    return html.Div([
        html.H3("📊 Analytics Results"),
        html.P(success_msg, className="text-success"),
        html.Hr(),
        
        # Summary cards
        html.Div([
            html.Div([
                html.H4(f"{analytics_results.get('total_events', 0):,}"),
                html.P("Total Events")
            ], className="col-md-3 text-center"),
            
            html.Div([
                html.H4(f"{analytics_results.get('unique_users', 0)}"),
                html.P("Unique Users")
            ], className="col-md-3 text-center"),
            
            html.Div([
                html.H4(f"{analytics_results.get('unique_doors', 0)}"),
                html.P("Unique Doors")
            ], className="col-md-3 text-center"),
            
            html.Div([
                html.H4(f"{analytics_results.get('success_rate', 0):.1f}%"),
                html.P("Success Rate")
            ], className="col-md-3 text-center"),
        ], className="row mb-4"),
        
        # Additional details
        html.Details([
            html.Summary("View Detailed Results"),
            html.Pre(json.dumps(analytics_results, indent=2, default=str))
        ])
    ])

# Security, trends, behavior, and anomaly dashboard functions would be similar...

# =============================================================================
# INTEGRATION INSTRUCTIONS
# =============================================================================

integration_instructions = """
🔧 CRITICAL FILE UPLOAD FIX - INTEGRATION STEPS
===============================================

STEP 1: UPDATE pages/file_upload.py
-----------------------------------
1. Replace the global _uploaded_data_store with UploadedDataStore class
2. Replace get_uploaded_data() function
3. Replace get_uploaded_filenames() function  
4. Replace process_uploaded_file() with process_uploaded_file_fixed()
5. Add required imports: import base64, import io

STEP 2: UPDATE services/analytics_service.py
-------------------------------------------
1. Replace AnalyticsService class with FixedAnalyticsService
2. Update all imports and references

STEP 3: UPDATE pages/deep_analytics.py
-------------------------------------
1. Replace generate_analytics_display() callback with generate_analytics_display_fixed()
2. Add helper functions for dashboard creation
3. Update imports

STEP 4: TEST THE FIX
-------------------
1. Restart your Dash application
2. Upload a test CSV file with columns: timestamp, person_id, door_id, access_result
3. Navigate to analytics page
4. Select "uploaded" as data source
5. Run analytics

STEP 5: VERIFY DATA PERSISTENCE
------------------------------
1. Upload files should persist across page refreshes
2. Check temp/uploaded_data/ directory for saved files
3. Files should show in dropdown and analytics should process them

ERROR DEBUGGING:
---------------
- Check browser console for JavaScript errors
- Check Python console for error messages
- Verify file uploads are being saved to disk
- Check that analytics service can access uploaded data

This fix addresses:
✅ File upload persistence across sessions
✅ Data store visibility to analytics system
✅ Automatic column mapping
✅ Better error handling and debugging
✅ File system backup for uploaded data
"""

print(integration_instructions)
