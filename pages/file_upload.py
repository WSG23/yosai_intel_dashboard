#!/usr/bin/env python3
"""
Complete File Upload Page - FIXED with direct app registration
"""
import logging
from datetime import datetime
from pathlib import Path
import json

import pandas as pd
from typing import Optional, Dict, Any, List
from dash import html, dcc, no_update, ctx
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc

from services.device_learning_service import DeviceLearningService
from services.upload_utils import (
    parse_uploaded_file,
    generate_preview,
    update_upload_state,
)
from components.column_verification import save_verified_mappings

logger = logging.getLogger(__name__)

# Initialize device learning service
learning_service = DeviceLearningService()


# -----------------------------------------------------------------------------
# Persistent Uploaded Data Store
# -----------------------------------------------------------------------------
class UploadedDataStore:
    """Persistent uploaded data store with file system backup"""

    def __init__(self) -> None:
        self._data_store: Dict[str, pd.DataFrame] = {}
        self._file_info_store: Dict[str, Dict[str, Any]] = {}
        self.storage_dir = Path("temp/uploaded_data")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()

    def _get_file_path(self, filename: str) -> Path:
        safe_name = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe_name}.pkl"

    def _info_path(self) -> Path:
        return self.storage_dir / "file_info.json"

    def _load_from_disk(self) -> None:
        """Load existing data from disk with proper error handling"""
        try:
            info_path = self._info_path()
            if info_path.exists() and info_path.stat().st_size > 0:
                try:
                    with open(info_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            self._file_info_store = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Corrupted file info, starting fresh")
                    self._file_info_store = {}

            # Load DataFrame files
            for info_filename, info in self._file_info_store.items():
                pkl_path = self._get_file_path(info_filename)
                if pkl_path.exists():
                    try:
                        df = pd.read_pickle(pkl_path)
                        self._data_store[info_filename] = df
                        logger.info(f"Restored {info_filename} from disk")
                    except Exception as e:
                        logger.warning(f"Could not load {info_filename}: {e}")

        except Exception as e:
            logger.warning(f"Error loading from disk: {e}")
            self._file_info_store = {}

    def add_file(self, filename: str, df: pd.DataFrame) -> None:
        """Add file to store and persist to disk"""
        self._data_store[filename] = df
        self._file_info_store[filename] = {
            "rows": len(df),
            "columns": len(df.columns),
            "upload_time": datetime.now().isoformat(),
        }
        self._persist_to_disk(filename, df)

    def _persist_to_disk(self, filename: str, df: pd.DataFrame) -> None:
        """Persist DataFrame and info to disk"""
        try:
            # Save DataFrame
            pkl_path = self._get_file_path(filename)
            df.to_pickle(pkl_path)

            # Save file info
            with open(self._info_path(), "w", encoding="utf-8") as f:
                json.dump(self._file_info_store, f, indent=2)

        except Exception as e:
            logger.error(f"Error persisting to disk: {e}")

    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Get all stored DataFrames"""
        return self._data_store.copy()

    def get_filenames(self) -> List[str]:
        """Get list of stored filenames"""
        return list(self._data_store.keys())

    def clear_all(self) -> None:
        """Clear all stored data"""
        self._data_store.clear()
        self._file_info_store.clear()
        try:
            for pkl_file in self.storage_dir.glob("*.pkl"):
                pkl_file.unlink()
            info_path = self._info_path()
            if info_path.exists():
                info_path.unlink()
        except Exception as e:
            logger.error(f"Error clearing disk storage: {e}")


# Initialize global store
_uploaded_data_store = UploadedDataStore()

# Load existing file info
try:
    existing_files = _uploaded_data_store.get_filenames()
    if existing_files:
        logger.info(f"Restored {len(existing_files)} files from previous session")
    else:
        logger.info("No existing file info found, starting fresh")
except Exception as e:
    logger.warning(f"Error loading existing files: {e}")


def get_ai_column_suggestions(column_names: List[str]) -> Dict[str, str]:
    """Get AI suggestions for column mappings"""
    suggestions = {}
    for col in column_names:
        col_lower = col.lower()
        if 'device' in col_lower or 'reader' in col_lower:
            suggestions[col] = 'device_name'
        elif 'user' in col_lower or 'name' in col_lower:
            suggestions[col] = 'user_name'
        elif 'time' in col_lower or 'date' in col_lower:
            suggestions[col] = 'timestamp'
        elif 'access' in col_lower or 'entry' in col_lower:
            suggestions[col] = 'access_type'
        elif 'floor' in col_lower or 'level' in col_lower:
            suggestions[col] = 'floor_number'
        else:
            suggestions[col] = 'custom'
    return suggestions


def layout():
    """Main file upload page layout"""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("File Upload"),
                            html.P("Upload CSV, Excel, or JSON files for analysis"),
                            html.Hr(),
                        ]
                    )
                ]
            ),
            # File upload card
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            dcc.Upload(
                                                id="upload-data",
                                                children=html.Div(
                                                    [
                                                        html.H5(
                                                            "Upload Files",
                                                            className="text-primary mb-3",
                                                        ),
                                                        html.H5(
                                                            "Drag and Drop or Click to Upload",
                                                            className="text-primary",
                                                        ),
                                                        html.P(
                                                            "Supports CSV, Excel (.xlsx, .xls), and JSON files",
                                                            className="text-muted mb-0",
                                                        ),
                                                    ]
                                                ),
                                                style={
                                                    "width": "100%",
                                                    "border": "2px dashed #007bff",
                                                    "borderRadius": "8px",
                                                    "textAlign": "center",
                                                    "padding": "50px",
                                                    "cursor": "pointer",
                                                    "backgroundColor": "#f8f9fa",
                                                },
                                                multiple=True,
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            ),
            # Upload results area
            dbc.Row([dbc.Col([html.Div(id="upload-results")])], className="mb-4"),
            # Data preview area
            dbc.Row([dbc.Col([html.Div(id="file-preview")])]),
            # Navigation to analytics
            dbc.Row([dbc.Col([html.Div(id="upload-nav")])]),
            # Container for toast notifications
            html.Div(id="toast-container"),
            # Hidden buttons to prevent callback errors
            html.Div(
                [
                    dbc.Button(
                        "", id="verify-columns-btn-simple", style={"display": "none"}
                    ),
                    dbc.Button(
                        "", id="classify-devices-btn", style={"display": "none"}
                    ),
                ],
                style={"display": "none"},
            ),
            # Store for uploaded data info
            dcc.Store(id="file-info-store", data={}),
            dcc.Store(id="current-file-info-store"),
            dcc.Store(id="current-session-id", data="session_123"),
        ],
        fluid=True,
    )


# -----------------------------------------------------------------------------
# Callback Functions (to be registered by app)
# -----------------------------------------------------------------------------
def consolidated_upload_callback(
    contents_list,
    verify_clicks,
    classify_clicks,
    confirm_clicks,
    cancel_col_clicks,
    cancel_dev_clicks,
    confirm_dev_clicks,
    pathname,
    filenames_list,
    dropdown_values,
    dropdown_ids,
    file_info,
    col_modal_open,
    dev_modal_open,
):
    """FIXED: Complete consolidated callback - handles file upload properly with correct imports"""
    
    # Use ctx instead of callback_context for newer Dash versions
    triggered_prop = ctx.triggered_prop_ids if hasattr(ctx, 'triggered_prop_ids') else ctx.triggered
    
    # Default returns - all 7 outputs
    default_returns = (no_update, no_update, no_update, no_update, no_update, no_update, no_update)
    
    # Debug logging
    logger.info(f"Upload callback triggered: {triggered_prop}")
    logger.info(f"Contents received: {contents_list is not None}")
    logger.info(f"Filenames received: {filenames_list is not None}")
    
    # Handle file upload FIRST and IMMEDIATELY
    if triggered_prop and any("upload-data.contents" in str(trigger) for trigger in triggered_prop):
        logger.info("Processing file upload...")
        
        # Validate inputs
        if not contents_list or not filenames_list:
            logger.warning("No files provided to upload")
            error_alert = dbc.Alert("No files selected", color="warning")
            return (error_alert, no_update, no_update, no_update, no_update, no_update, no_update)
            
        # Clear previous data
        _uploaded_data_store.clear_all()
        
        # Ensure lists
        if not isinstance(contents_list, list):
            contents_list = [contents_list]
        if not isinstance(filenames_list, list):
            filenames_list = [filenames_list]
        
        upload_results = []
        file_preview_components = []
        current_file_info = {}
        
        # Process each uploaded file
        for content, filename in zip(contents_list, filenames_list):
            try:
                logger.info(f"Processing file: {filename}")
                
                # Parse the file
                result = parse_uploaded_file(content, filename)
                
                if result["success"]:
                    df = result["data"]
                    
                    # Update store
                    info = update_upload_state(filename, df, _uploaded_data_store)
                    info["ai_suggestions"] = get_ai_column_suggestions(info["column_names"])
                    current_file_info = info
                    
                    # Create success message
                    upload_results.append(
                        dbc.Alert(
                            f"Successfully uploaded {filename} ({len(df)} rows, {len(df.columns)} columns)",
                            color="success",
                            className="mb-2"
                        )
                    )
                    
                    # Create preview
                    file_preview_components.append(generate_preview(df, filename))
                    
                    logger.info(f"Successfully processed {filename}")
                    
                else:
                    # Handle error
                    upload_results.append(
                        dbc.Alert(
                            f"Error uploading {filename}: {result['error']}",
                            color="danger",
                            className="mb-2"
                        )
                    )
                    logger.error(f"Error processing {filename}: {result['error']}")
                    
            except Exception as e:
                upload_results.append(
                    dbc.Alert(
                        f"Exception processing {filename}: {str(e)}",
                        color="danger",
                        className="mb-2"
                    )
                )
                logger.error(f"Exception processing {filename}: {e}")
        
        # Create navigation to analytics if successful uploads
        upload_nav = []
        if any("Successfully uploaded" in str(result) for result in upload_results):
            upload_nav.append(
                dbc.Alert(
                    [
                        html.P("File(s) uploaded successfully!", className="mb-2"),
                        dbc.Button(
                            "Go to Analytics",
                            href="/analytics",
                            color="primary",
                            className="me-2"
                        ),
                    ],
                    color="info"
                )
            )
        
        logger.info(f"Upload processing complete. Results: {len(upload_results)}")
        
        return (
            html.Div(upload_results),
            html.Div(file_preview_components),
            {"uploaded_files": _uploaded_data_store.get_filenames()},
            html.Div(upload_nav),
            current_file_info,
            no_update,
            no_update
        )
    
    # Handle other button clicks
    if triggered_prop:
        trigger_str = str(triggered_prop)
        
        if "verify-columns-btn-simple" in trigger_str and verify_clicks:
            return (no_update, no_update, no_update, no_update, no_update, True, False)
            
        elif "column-verify-confirm" in trigger_str and confirm_clicks:
            return (no_update, no_update, no_update, no_update, no_update, False, True)
            
        elif "classify-devices-btn" in trigger_str and classify_clicks:
            return (no_update, no_update, no_update, no_update, no_update, False, True)
            
        elif any(x in trigger_str for x in ["cancel", "confirm"]):
            return (no_update, no_update, no_update, no_update, no_update, False, False)
    
    # Default return
    return default_returns


def save_confirmed_device_mappings_callback(
    confirm_clicks, floors, security, access, special, file_info
):
    """Save confirmed device mappings to database"""
    if not confirm_clicks or not file_info:
        return no_update, no_update, no_update

    try:
        devices = file_info.get("devices", [])
        filename = file_info.get("filename", "")

        # Create user mappings from inputs
        user_mappings = {}
        for i, device in enumerate(devices):
            user_mappings[device] = {
                "floor_number": floors[i] if i < len(floors) else 1,
                "security_level": security[i] if i < len(security) else 5,
                "is_entry": "entry" in (access[i] if i < len(access) else []),
                "is_exit": "exit" in (access[i] if i < len(access) else []),
                "is_restricted": "is_restricted" in (special[i] if i < len(special) else []),
                "confidence": 1.0,
                "device_name": device,
                "source": "user_confirmed",
                "saved_at": datetime.now().isoformat(),
            }

        # Save to learning service database
        learning_service.save_user_device_mappings(filename, user_mappings)

        logger.info(f"Saved {len(user_mappings)} confirmed device mappings to database")

        success_alert = dbc.Toast(
            "Device mappings saved to database!",
            header="Confirmed & Saved",
            is_open=True,
            dismissable=True,
            duration=3000,
        )

        return success_alert, False, False

    except Exception as e:
        logger.error(f"Error saving device mappings: {e}")
        error_alert = dbc.Toast(
            f"Error saving mappings: {e}",
            header="Error",
            is_open=True,
            dismissable=True,
            duration=5000,
        )
        return error_alert, no_update, no_update


# -----------------------------------------------------------------------------
# FIXED: Register callbacks with app (called from app_factory)
# -----------------------------------------------------------------------------
def register_upload_callbacks(app):
    """Register upload callbacks with the app directly"""
    
    logger.info("Registering upload callbacks directly...")
    
    # Main upload callback
    app.callback(
        [
            Output("upload-results", "children"),
            Output("file-preview", "children"), 
            Output("file-info-store", "data"),
            Output("upload-nav", "children"),
            Output("current-file-info-store", "data"),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        [
            Input("upload-data", "contents"),
            Input("verify-columns-btn-simple", "n_clicks"),
            Input("classify-devices-btn", "n_clicks"),
            Input("column-verify-confirm", "n_clicks"),
            Input("column-verify-cancel", "n_clicks"),
            Input("device-verify-cancel", "n_clicks"),
            Input("device-verify-confirm", "n_clicks"),
            Input("url", "pathname"),
        ],
        [
            State("upload-data", "filename"),
            State({"type": "field-mapping", "column": ALL}, "value"),
            State({"type": "field-mapping", "column": ALL}, "id"),
            State("current-file-info-store", "data"),
            State("column-verification-modal", "is_open"),
            State("device-verification-modal", "is_open"),
        ],
        prevent_initial_call=False,
    )(consolidated_upload_callback)
    
    # Device mappings callback
    app.callback(
        [
            Output("toast-container", "children", allow_duplicate=True),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        [Input("device-verify-confirm", "n_clicks")],
        [
            State({"type": "device-floor", "index": ALL}, "value"),
            State({"type": "device-security", "index": ALL}, "value"),
            State({"type": "device-access", "index": ALL}, "value"),
            State({"type": "device-special", "index": ALL}, "value"),
            State("current-file-info-store", "data"),
        ],
        prevent_initial_call=True,
    )(save_confirmed_device_mappings_callback)
    
    logger.info("✅ Upload callbacks registered successfully")


# -----------------------------------------------------------------------------
# Public API Functions
# -----------------------------------------------------------------------------
def get_uploaded_data() -> Dict[str, pd.DataFrame]:
    """Get all uploaded data (for use by analytics)"""
    return _uploaded_data_store.get_all_data()


def get_uploaded_filenames() -> List[str]:
    """Get list of uploaded filenames"""
    return _uploaded_data_store.get_filenames()


def clear_uploaded_data():
    """Clear all uploaded data"""
    _uploaded_data_store.clear_all()


def get_file_info():
    """Get file information store"""
    return _uploaded_data_store._file_info_store


def process_uploaded_file(contents, filename):
    """Wrapper for parse_uploaded_file for backward compatibility"""
    return parse_uploaded_file(contents, filename)


def create_file_preview(df: pd.DataFrame, filename: str) -> dbc.Card:
    """Wrapper around generate_preview for backward compatibility"""
    return generate_preview(df, filename)


def save_ai_training_data(mappings: Dict[str, Any], filename: str) -> bool:
    """Save AI training data"""
    try:
        learning_service.save_user_device_mappings(filename, mappings)
        return True
    except Exception as e:
        logger.error(f"Error saving AI training data: {e}")
        return False


# Export functions for integration
__all__ = [
    "layout",
    "register_upload_callbacks",
    "get_uploaded_data",
    "get_uploaded_filenames", 
    "clear_uploaded_data",
    "get_file_info",
    "process_uploaded_file",
    "parse_uploaded_file",
    "save_ai_training_data",
]

logger.info("FILE_UPLOAD.PY LOADED - Ready for callback registration")
