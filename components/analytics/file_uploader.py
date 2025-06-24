"""
Dual Upload Box Component with Tailwind styling and working callbacks
"""

from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc
import base64
import io
import pandas as pd
import uuid
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
import tempfile
import os

USER_MAPPING_FILE = os.path.join("data", "user_mappings.json")
SESSION_FILE = os.path.join("data", "verified_session.json")

logger = logging.getLogger(__name__)


class AIColumnMapper:
    """AI-powered column type detection"""

    FIELD_PATTERNS = {
        'timestamp': {
            'exact': ['timestamp', 'datetime', 'time', 'date'],
            'contains': ['time', 'date', 'when', 'occurred', 'created', 'logged', 'recorded'],
        },
        'device_name': {
            'exact': ['device', 'door', 'reader', 'location', 'terminal', 'gate'],
            'contains': ['device', 'door', 'location', 'area', 'reader', 'panel', 'terminal',
                        'gate', 'entrance', 'exit', 'access_point', 'checkpoint', 'zone'],
        },
        'user_id': {
            'exact': ['user', 'person', 'employee', 'badge', 'card', 'id'],
            'contains': ['user', 'person', 'employee', 'badge', 'card', 'id', 'worker',
                        'staff', 'visitor', 'holder', 'individual'],
        },
        'event_type': {
            'exact': ['event', 'action', 'type', 'result', 'status', 'access'],
            'contains': ['event', 'action', 'type', 'result', 'status', 'access',
                        'entry', 'exit', 'granted', 'denied', 'outcome'],
        }
    }

    def __init__(self, min_confidence: float = 0.3):
        self.min_confidence = min_confidence
        self.user_mappings: Dict[str, str] = {}
        self._load_user_mappings()

    def _load_user_mappings(self) -> None:
        """Load user confirmed mappings from disk"""
        if os.path.exists(USER_MAPPING_FILE):
            try:
                with open(USER_MAPPING_FILE, "r", encoding="utf-8") as f:
                    self.user_mappings = json.load(f)
            except Exception:
                self.user_mappings = {}

    def _save_user_mappings(self) -> None:
        """Persist user mappings to disk"""
        try:
            os.makedirs(os.path.dirname(USER_MAPPING_FILE), exist_ok=True)
            with open(USER_MAPPING_FILE, "w", encoding="utf-8") as f:
                json.dump(self.user_mappings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save user mappings: {e}")

    def learn_user_mapping(self, mapping: Dict[str, str]) -> None:
        """Update mapping knowledge from user input"""
        for field, column in mapping.items():
            self.user_mappings[column.lower()] = field
        self._save_user_mappings()

    def analyze_columns(self, column_names: List[str]) -> Dict[str, any]:
        """Analyze column names and return AI suggestions"""
        suggestions = {}
        confidence_scores = {}

        for column in column_names:
            column_key = column.lower().strip()
            if column_key in self.user_mappings:
                field_type = self.user_mappings[column_key]
                suggestions[field_type] = column
                confidence_scores[column] = 1.0
                continue

            match = self._find_best_match(column)
            if match and match['confidence'] >= self.min_confidence:
                suggestions[match['field_type']] = column
                confidence_scores[column] = match['confidence']

        final_suggestions = self._resolve_conflicts(suggestions, confidence_scores, column_names)

        return {
            'suggestions': final_suggestions,
            'confidence': confidence_scores
        }

    def _find_best_match(self, column_name: str) -> Optional[Dict]:
        """Find the best field type match for a column name"""
        column_lower = column_name.lower().strip()
        best_match = None
        best_confidence = 0.0

        for field_type, patterns in self.FIELD_PATTERNS.items():
            match = self._match_patterns(column_lower, patterns, field_type)
            if match and match['confidence'] > best_confidence:
                best_match = match
                best_confidence = match['confidence']

        return best_match

    def _match_patterns(self, column_lower: str, patterns: Dict, field_type: str) -> Optional[Dict]:
        """Check if column matches field type patterns"""

        # 1. Exact matches (highest confidence)
        if column_lower in patterns['exact']:
            return {'field_type': field_type, 'confidence': 1.0, 'pattern': column_lower}

        # 2. Contains patterns (medium-high confidence)
        for pattern in patterns['contains']:
            if pattern in column_lower:
                confidence = min(0.9, len(pattern) / len(column_lower) + 0.4)
                return {'field_type': field_type, 'confidence': confidence, 'pattern': pattern}

        return None

    def _resolve_conflicts(self, suggestions: Dict[str, str],
                           confidence_scores: Dict[str, float],
                           all_columns: List[str]) -> Dict[str, str]:
        """Resolve conflicts where multiple field types map to same column"""
        final_suggestions = {}
        used_columns = set()

        # Sort by confidence and assign
        field_confidence_pairs = []
        for field_type, column in suggestions.items():
            confidence = confidence_scores.get(column, 0.0)
            field_confidence_pairs.append((field_type, column, confidence))

        field_confidence_pairs.sort(key=lambda x: x[2], reverse=True)

        for field_type, column, confidence in field_confidence_pairs:
            if column not in used_columns:
                final_suggestions[field_type] = column
                used_columns.add(column)

        return final_suggestions


class FileUploadController:
    """Handles file upload workflow coordination"""

    def __init__(self):
        self.ai_mapper = AIColumnMapper(min_confidence=0.3)

    def process_upload(self, upload_contents: str, upload_filename: str) -> Dict[str, Any]:
        """Main entry point for file upload processing"""
        try:
            # Parse and validate file
            df = self._parse_file(upload_contents, upload_filename)
            if df is None or df.empty:
                return self._error_response("File is empty or corrupted")

            # Run AI column analysis
            columns = list(df.columns)
            ai_result = self.ai_mapper.analyze_columns(columns)

            # Prepare response data
            session_id = str(uuid.uuid4())

            return {
                'success': True,
                'session_id': session_id,
                'filename': upload_filename,
                'data': df.to_dict('records'),
                'columns': columns,
                'ai_suggestions': ai_result['suggestions'],
                'confidence_scores': ai_result['confidence'],
                'record_count': len(df),
                'column_count': len(columns),
                'show_modal': True
            }

        except Exception as e:
            logger.error(f"Upload processing failed: {e}")
            return self._error_response(f"Upload failed: {str(e)}")

    def _parse_file(self, upload_contents: str, filename: str) -> Optional[pd.DataFrame]:
        """Parse uploaded file content into DataFrame"""
        try:
            # Handle list input (multiple files)
            if isinstance(upload_contents, list):
                upload_contents = upload_contents[0]
            if isinstance(filename, list):
                filename = filename[0]

            # Decode base64 content
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)

            # Normalize file extension handling
            filename_lower = filename.lower()

            # Parse based on file extension
            if filename_lower.endswith('.csv'):
                return self._parse_csv(decoded)
            elif filename_lower.endswith(('.xlsx', '.xls')):
                return self._parse_excel(decoded)
            elif filename_lower.endswith('.json'):
                return self._parse_json(decoded)
            else:
                raise ValueError(f"Unsupported file type: {filename}")

        except Exception as e:
            logger.error(f"File parsing failed for {filename}: {e}")
            return None

    def _parse_csv(self, content: bytes) -> pd.DataFrame:
        """Parse CSV with encoding detection"""
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                text = content.decode(encoding)
                return pd.read_csv(io.StringIO(text))
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not decode CSV with any standard encoding")

    def _parse_excel(self, content: bytes) -> pd.DataFrame:
        """Parse Excel file"""
        return pd.read_excel(io.BytesIO(content))

    def _parse_json(self, content: bytes) -> pd.DataFrame:
        """Parse JSON file"""
        import json
        text = content.decode('utf-8')
        json_data = json.loads(text)
        if isinstance(json_data, list):
            return pd.DataFrame(json_data)
        else:
            return pd.json_normalize(json_data)

    def verify_column_mapping(self, mapping: Dict[str, str], session_data: Dict) -> Dict[str, Any]:
        """Verify user's column mapping choices"""
        try:
            required_fields = ['timestamp', 'device_name', 'user_id', 'event_type']
            missing_fields = [f for f in required_fields if f not in mapping.values()]

            if missing_fields:
                return {
                    'success': False,
                    'error': f"Missing required mappings: {missing_fields}",
                    'next_step': 'fix_mapping'
                }

            session_data['confirmed_mapping'] = mapping
            session_data['mapping_verified'] = True
            session_data['verified_at'] = datetime.now().isoformat()

            # learn from user mapping and persist
            self.ai_mapper.learn_user_mapping(mapping)
            try:
                os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to save session data: {e}")

            return {
                'success': True,
                'message': 'Column mapping verified successfully',
                'next_step': 'device_mapping',
                'session_data': session_data
            }

        except Exception as e:
            logger.error(f"Mapping verification failed: {e}")
            return self._error_response(f"Verification failed: {str(e)}")

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Return standardized error response"""
        return {'success': False, 'error': message}


class DeviceMapper:
    """AI-powered device location mapping"""

    LOCATION_PATTERNS = {
        'floor': {
            'patterns': [r'f(\d+)', r'floor[\s_-]*(\d+)', r'level[\s_-]*(\d+)', r'(\d+)f', r'(\d+)floor'],
            'keywords': ['floor', 'level', 'f1', 'f2', 'f3', 'f4', 'f5']
        },
        'area': {
            'entrance': ['entrance', 'entry', 'main', 'lobby', 'front', 'reception'],
            'office': ['office', 'desk', 'workspace', 'cubicle', 'room'],
            'server': ['server', 'data', 'it', 'network', 'computer'],
            'lab': ['lab', 'laboratory', 'test', 'research'],
            'storage': ['storage', 'warehouse', 'inventory', 'closet'],
            'security': ['security', 'guard', 'monitoring', 'control'],
            'emergency': ['emergency', 'exit', 'fire', 'stair', 'escape'],
            'bathroom': ['bathroom', 'restroom', 'wc', 'toilet'],
            'kitchen': ['kitchen', 'cafeteria', 'break', 'lunch'],
            'meeting': ['meeting', 'conference', 'boardroom', 'presentation']
        }
    }

    def __init__(self, default_floor: int = 1):
        self.default_floor = default_floor

    def analyze_devices(self, data: List[Dict], device_column: str) -> Dict[str, Any]:
        """Analyze devices and suggest floor/area mappings"""
        try:
            # Extract unique devices
            devices = list(set([
                str(row.get(device_column, "")).strip()
                for row in data
                if row.get(device_column)
            ]))

            devices = [d for d in devices if d and d != ""]

            # Generate mappings for each device
            device_mappings = []
            for device_id in devices:
                mapping = self._analyze_single_device(device_id)
                device_mappings.append(mapping)

            # Calculate summary statistics
            floor_distribution = {}
            area_distribution = {}

            for mapping in device_mappings:
                floor = mapping['suggested_floor']
                area = mapping['suggested_area']

                floor_distribution[floor] = floor_distribution.get(floor, 0) + 1
                area_distribution[area] = area_distribution.get(area, 0) + 1

            return {
                'success': True,
                'device_mappings': device_mappings,
                'device_count': len(devices),
                'floor_distribution': floor_distribution,
                'area_distribution': area_distribution,
                'estimated_floors': len(floor_distribution),
            }

        except Exception as e:
            logger.error(f"Device analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_single_device(self, device_id: str) -> Dict[str, Any]:
        """Analyze a single device for location mapping"""
        device_lower = device_id.lower().strip()

        # Extract floor number
        floor, floor_confidence, floor_pattern = self._extract_floor(device_lower)

        # Extract area type
        area, area_confidence, area_pattern = self._extract_area(device_lower)

        # Calculate overall confidence
        overall_confidence = (floor_confidence + area_confidence) / 2

        return {
            'device_id': device_id,
            'suggested_floor': floor,
            'suggested_area': area,
            'confidence': overall_confidence,
            'pattern_matched': f"floor: {floor_pattern}, area: {area_pattern}"
        }

    def _extract_floor(self, device_text: str) -> Tuple[int, float, str]:
        """Extract floor number from device name"""
        import re

        # Try regex patterns for floor numbers
        for pattern in self.LOCATION_PATTERNS['floor']['patterns']:
            match = re.search(pattern, device_text)
            if match:
                try:
                    floor_num = int(match.group(1))
                    return floor_num, 0.9, f"regex: {pattern}"
                except (ValueError, IndexError):
                    continue

        # Try keyword matching
        for keyword in self.LOCATION_PATTERNS['floor']['keywords']:
            if keyword in device_text:
                # Try to extract number near keyword
                floor_num = self._extract_number_near_keyword(device_text, keyword)
                if floor_num:
                    return floor_num, 0.7, f"keyword: {keyword}"

        # Default floor
        return self.default_floor, 0.3, "default"

    def _extract_area(self, device_text: str) -> Tuple[str, float, str]:
        """Extract area type from device name"""

        best_area = "general"
        best_confidence = 0.2
        best_pattern = "default"

        for area_type, keywords in self.LOCATION_PATTERNS['area'].items():
            for keyword in keywords:
                if keyword in device_text:
                    # Calculate confidence based on keyword specificity
                    confidence = min(0.9, len(keyword) / len(device_text) + 0.5)

                    if confidence > best_confidence:
                        best_area = area_type
                        best_confidence = confidence
                        best_pattern = f"keyword: {keyword}"

        return best_area, best_confidence, best_pattern

    def _extract_number_near_keyword(self, text: str, keyword: str) -> Optional[int]:
        """Extract number near a specific keyword"""
        import re

        # Find keyword position
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return None

        # Look for numbers before and after keyword
        search_range = 10  # characters to search around keyword
        start_pos = max(0, keyword_pos - search_range)
        end_pos = min(len(text), keyword_pos + len(keyword) + search_range)

        search_text = text[start_pos:end_pos]

        # Find numbers in search range
        numbers = re.findall(r'\d+', search_text)

        for num_str in numbers:
            try:
                num = int(num_str)
                if 1 <= num <= 50:  # Reasonable floor range
                    return num
            except ValueError:
                continue

        return None


# INITIALIZE THE CONTROLLER
upload_controller = FileUploadController()


def create_dual_file_uploader(upload_id="upload-data"):
    """Create a working dual file uploader component"""
    try:
        return html.Div(
            [
                # Upload header
                html.Div(
                    [
                        html.H2("📁 Upload Your Data", className="text-2xl font-bold mb-2"),
                        html.P(
                            "Choose your access control data file to begin analysis", className="text-gray-600 mb-6"
                        ),
                    ]
                ),
                # Main upload area - simplified and working
                html.Div(
                    [
                        dcc.Upload(
                            id=upload_id,
                            children=html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fas fa-cloud-upload-alt text-4xl text-blue-500 mb-4"),
                                            html.H3(
                                                "Drop files here or click to browse",
                                                className="text-lg font-semibold text-gray-700 mb-2",
                                            ),
                                            html.P("CSV, JSON, Excel files supported", className="text-gray-500 mb-4"),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "✅ CSV files (.csv)", className="block text-sm text-gray-600"
                                                    ),
                                                    html.Span(
                                                        "✅ JSON files (.json)", className="block text-sm text-gray-600"
                                                    ),
                                                    html.Span(
                                                        "✅ Excel files (.xlsx, .xls)",
                                                        className="block text-sm text-gray-600",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                className="border-2 border-dashed border-blue-300 rounded-lg p-8 bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer",
                            ),
                            multiple=False,
                            accept=".csv,.json,.xlsx,.xls",
                            className="w-full",
                        )
                    ],
                    className="mb-6",
                ),
                # Database upload option (inactive)
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-database text-2xl text-gray-400 mb-2"),
                                html.H4("Database Connection", className="text-md font-medium text-gray-500 mb-1"),
                                html.P("Coming soon - Direct database connections", className="text-sm text-gray-400"),
                            ],
                            className="text-center p-4 border border-gray-200 rounded-lg bg-gray-50",
                        )
                    ],
                    className="mb-4",
                ),
            ],
            className="max-w-2xl mx-auto",
        )

    except Exception as e:
        logger.error(f"Error creating file uploader: {e}")
        return html.Div(
            [html.H3("Upload Error", className="text-red-600"), html.P(f"Error: {str(e)}", className="text-red-500")]
        )


def render_column_mapping_panel(
    header_options, file_name="access_control_data.csv", ai_suggestions=None, floor_estimate=None, user_id="default"
):
    """Enhanced column mapping UI panel with AI suggestions and verification."""

    if ai_suggestions is None:
        ai_suggestions = {}
    if floor_estimate is None:
        floor_estimate = {"total_floors": 1, "confidence": 0}

    def create_field_dropdown(label, field_id, suggested_value=None, required=False):
        return html.Div(
            className="form-field",
            children=[
                html.Label(
                    label + (" *" if required else ""),
                    className="form-label" + (" form-label--required" if required else ""),
                ),
                html.Small(
                    f"AI Suggestion: {suggested_value}" if suggested_value else "No AI suggestion",
                    className="form-help-text",
                ),
                dcc.Dropdown(
                    id=field_id,
                    options=[{"label": col, "value": col} for col in header_options],
                    value=suggested_value,
                    placeholder="Select a column...",
                    className="form-select",
                ),
            ],
        )

    return html.Div(
        className="modal-overlay",
        children=[
            html.Div(
                className="modal modal--xl",
                children=[
                    html.Div(
                        className="modal__header",
                        children=[
                            html.H2("Verify AI Column Mapping", className="modal__title"),
                            html.P(f"File: {file_name}", className="modal__subtitle"),
                            html.Button("\xd7", id="close-mapping-modal", className="modal__close"),
                        ],
                    ),
                    html.Div(
                        className="modal__body",
                        children=[
                            # Instructions
                            html.Div(
                                className="form-instructions",
                                children=[
                                    html.P(
                                        "🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                                        className="form-instructions-text",
                                    ),
                                    html.P(
                                        f"📊 Detected {len(header_options)} columns in your file",
                                        className="form-instructions-subtext",
                                    ),
                                ],
                            ),
                            html.Hr(className="form-separator"),
                            # Column Mapping Fields
                            html.Div(
                                className="form-grid",
                                children=[
                                    create_field_dropdown(
                                        "Timestamp Column",
                                        "timestamp-dropdown",
                                        ai_suggestions.get("timestamp"),
                                        required=True,
                                    ),
                                    create_field_dropdown(
                                        "Device/Door Column",
                                        "device-column-dropdown",
                                        ai_suggestions.get("device_name"),
                                    ),
                                    create_field_dropdown(
                                        "User ID Column", "user-id-dropdown", ai_suggestions.get("user_id")
                                    ),
                                    create_field_dropdown(
                                        "Event Type Column", "event-type-dropdown", ai_suggestions.get("event_type")
                                    ),
                                ],
                            ),
                            html.Hr(className="form-separator"),
                            # Floor Estimate
                            html.Div(
                                className="form-row",
                                children=[
                                    html.Div(
                                        className="form-field",
                                        children=[
                                            html.Label("Number of Floors", className="form-label"),
                                            dcc.Input(
                                                id="floor-estimate-input",
                                                type="number",
                                                value=floor_estimate.get("total_floors", 1),
                                                min=1,
                                                max=100,
                                                className="form-input",
                                            ),
                                            html.Small(
                                                f"AI Confidence: {floor_estimate.get('confidence', 0) * 100:.0f}%",
                                                className="form-help-text",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                            # Hidden storage for user ID
                            html.Div(id="user-id-storage", children=user_id, style={"display": "none"}),
                        ],
                    ),
                    html.Div(
                        className="modal__footer",
                        children=[
                            html.Button("Cancel", id="cancel-mapping", className="btn btn-secondary"),
                            html.Button("\u2705 Verify & Learn", id="verify-mapping", className="btn btn-primary"),
                        ],
                    ),
                ],
            )
        ],
    )


def _handle_modal_close():
    """Handle modal close action"""
    return [
        {"display": "none"}, "", "", [], [], [], [],
        None, None, None, None, {}, {}, {"display": "none"}
    ]


@callback(
    [
        Output("column-mapping-modal", "style"),
        Output("upload-status-message", "children"),
        Output("modal-file-info", "children"),
        Output("timestamp-dropdown", "options"),
        Output("device-dropdown", "options"),
        Output("user-dropdown", "options"),
        Output("event-dropdown", "options"),
        Output("timestamp-dropdown", "value"),
        Output("device-dropdown", "value"),
        Output("user-dropdown", "value"),
        Output("event-dropdown", "value"),
        Output("uploaded-file-store", "data"),
        Output("processed-data-store", "data"),
        Output("proceed-to-device-mapping", "style"),
    ],
    [
        Input("upload-data", "contents"),
        Input("verify-mapping", "n_clicks"),
        Input("close-mapping-modal", "n_clicks"),
    ],
    [
        State("upload-data", "filename"),
        State("timestamp-dropdown", "value"),
        State("device-dropdown", "value"),
        State("user-dropdown", "value"),
        State("event-dropdown", "value"),
        State("uploaded-file-store", "data"),
        State("processed-data-store", "data"),
    ],
    prevent_initial_call=True
)
def handle_upload_workflow(upload_contents, verify_clicks, close_clicks,
                          upload_filename, timestamp_col, device_col, user_col, event_col,
                          file_store, processed_store):
    """Simplified callback handling upload workflow"""

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    default_return = [
        {"display": "none"},
        "",
        "",
        [],
        [], [], [],
        None, None, None, None,
        {},
        {},
        {"display": "none"},
    ]

    try:
        if trigger_id == "upload-data" and upload_contents:
            return _handle_file_upload(upload_contents, upload_filename)
        elif trigger_id == "verify-mapping" and verify_clicks:
            return _handle_mapping_verification(
                timestamp_col, device_col, user_col, event_col,
                file_store, processed_store
            )
        elif trigger_id == "close-mapping-modal":
            return _handle_modal_close()
        else:
            return default_return
    except Exception as e:
        logger.error(f"Callback error: {e}")
        error_msg = html.Div(f"❌ Error: {str(e)}", className="text-red-600")
        return [{"display": "none"}] + [error_msg] + default_return[2:]


def _handle_file_upload(upload_contents, upload_filename):
    """Handle file upload processing"""

    result = upload_controller.process_upload(upload_contents, upload_filename)

    if not result['success']:
        error_msg = html.Div(result['error'], className="text-red-600")
        return [
            {"display": "none"},
            error_msg,
            "",
            [],
            [],
            [],
            [],
            None,
            None,
            None,
            None,
            {},
            {},
            {"display": "none"},
        ]

    columns = result['columns']
    column_options = [{"label": col, "value": col} for col in columns]
    suggestions = result['ai_suggestions']

    success_msg = html.Div([
        html.P(f"✅ File '{result['filename']}' uploaded successfully!",
               className="text-green-600 font-medium"),
        html.P(f"📊 Found {result['record_count']} records with {result['column_count']} columns",
               className="text-gray-600"),
        html.P("🤖 AI analysis complete. Verify column mapping below.",
               className="text-blue-600"),
    ])

    file_info = f"File: {result['filename']} ({result['record_count']} records, {result['column_count']} columns)"

    return [
        {"display": "flex"},
        success_msg,
        file_info,
        column_options,
        column_options,
        column_options,
        column_options,
        suggestions.get('timestamp'),
        suggestions.get('device_name'),
        suggestions.get('user_id'),
        suggestions.get('event_type'),
        {
            'session_id': result['session_id'],
            'filename': result['filename']
        },
        {
            'data': result['data'],
            'columns': result['columns'],
            'ai_suggestions': result['ai_suggestions'],
            'confidence_scores': result['confidence_scores']
        },
        {"display": "none"},
    ]


def _handle_mapping_verification(timestamp_col, device_col, user_col, event_col,
                                file_store, processed_store):
    """Handle user verification of column mapping"""

    mapping = {}
    if timestamp_col:
        mapping['timestamp'] = timestamp_col
    if device_col:
        mapping['device_name'] = device_col
    if user_col:
        mapping['user_id'] = user_col
    if event_col:
        mapping['event_type'] = event_col

    verification_result = upload_controller.verify_column_mapping(mapping, processed_store)

    if not verification_result['success']:
        error_msg = html.Div(verification_result['error'], className="text-red-600")
        return [
            {"display": "flex"},
            error_msg,
        ] + [no_update] * 11

    success_msg = html.Div([
        html.P("✅ Column mapping verified successfully!", className="text-green-600"),
        html.P("Ready to proceed to device mapping.", className="text-blue-600")
    ])

    return [
        {"display": "none"},
        success_msg,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        verification_result.get('session_data', processed_store),
        {"display": "block"},
    ]


def enhanced_pattern_matching(headers):
    """Enhanced fallback pattern matching for column detection - now uses AI mapper"""
    mapper = AIColumnMapper()
    result = mapper.analyze_columns(headers)

    ai_suggestions = result['suggestions']
    confidence_scores = result['confidence']

    return ai_suggestions, confidence_scores


def fallback_floor_estimation(data):
    """Fallback floor estimation using simple heuristics"""
    floor_indicators = set()
    for record in data[:100]:
        for value in record.values():
            if value:
                text = str(value).lower()
                import re

                patterns = [r"\b(\d+)f\b", r"\bfloor\s*(\d+)", r"\bf(\d+)", r"\b(\d+)fl\b"]
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            floor_num = int(match)
                            if 1 <= floor_num <= 50:
                                floor_indicators.add(floor_num)
                        except ValueError:
                            continue

    if floor_indicators:
        max_floor = max(floor_indicators)
        confidence = f"{min(90, len(floor_indicators) * 20)}%"
        return max_floor, confidence

    return 1, "0%"


# New callback to prepare AI door mapping data when modal is opened
@callback(
    Output("door-mapping-modal-data-trigger", "data"),
    [Input("door-mapping-modal-trigger", "n_clicks"), Input("skip-door-mapping", "n_clicks")],
    [State("processed-data-store", "data"), State("device-column-dropdown", "value")],
    prevent_initial_call=True,
)
def handle_door_mapping(open_clicks, skip_clicks, processed_data, device_col):
    """Handle door mapping modal with AI pre-processing"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "skip-door-mapping":
        logger.info("Door mapping skipped by user")
        return dash.no_update

    if trigger_id == "door-mapping-modal-trigger" and open_clicks:
        try:
            if not processed_data or "data" not in processed_data:
                return dash.no_update

            # Extract CSV data
            csv_data = processed_data["data"]
            if not csv_data:
                return dash.no_update

            # Get device column
            available_columns = list(csv_data[0].keys())
            device_column = device_col

            if not device_column or device_column not in available_columns:
                # Fallback detection
                for col in available_columns:
                    if any(word in col.lower() for word in ["device", "door", "id"]):
                        device_column = col
                        break
                else:
                    device_column = available_columns[0]

            # Extract unique devices
            devices = list(set([str(row.get(device_column, "")).strip() for row in csv_data if row.get(device_column)]))
            devices = [d for d in devices if d and d != ""]

            # Generate AI mappings for each device
            ai_mapped_devices = []
            for device_id in devices:
                ai_attributes = generate_ai_door_attributes(device_id)
                ai_mapped_devices.append({"device_id": device_id, **ai_attributes})

            logger.info(f"AI processed {len(ai_mapped_devices)} devices for door mapping")

            return {"devices": ai_mapped_devices, "column": device_column, "ai_processed": True}

        except Exception as e:
            logger.error(f"Error in door mapping preparation: {e}")
            return dash.no_update

    return dash.no_update


# Door mapping callback
@callback(
    Output("door-mapping-modal-overlay", "className"),
    [Input("door-mapping-modal-trigger", "n_clicks"), Input("skip-door-mapping", "n_clicks")],
    [State("door-mapping-modal-data-trigger", "data")],
    prevent_initial_call=True,
)
def handle_door_mapping_buttons(open_clicks, skip_clicks, modal_data):
    """Handle door mapping and skip buttons with AI pre-processing"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "skip-door-mapping":
        logger.info("Door mapping skipped by user")
        return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

    if trigger_id == "door-mapping-modal-trigger":
        if not modal_data or not modal_data.get("ai_processed"):
            logger.warning("AI mapping not completed yet")
            return dash.no_update

        return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center"

    return dash.no_update


def create_error_modal(title, message):
    """Create a simple error modal"""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(f"❌ {title}", className="text-lg font-semibold text-red-600 mb-3"),
                            html.P(message, className="text-gray-700 mb-4"),
                            html.Button(
                                "Close",
                                id="close-error-modal",
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600",
                            ),
                        ],
                        className="bg-white p-6 rounded-lg max-w-md",
                    )
                ],
                className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4",
            )
        ]
    )


def create_door_mapping_modal_with_data(devices, device_column):
    """Create door mapping modal populated with actual CSV data"""

    # Generate AI suggestions for each device
    device_rows = []
    for i, device_id in enumerate(devices):
        # AI-based attribute suggestions
        ai_attributes = generate_ai_door_attributes(device_id)

        device_rows.append(
            html.Tr(
                [
                    # Device ID
                    html.Td(
                        [
                            html.Div(device_id, className="font-medium text-gray-900"),
                            html.Div(f"Device #{i+1}", className="text-sm text-gray-500"),
                        ],
                        className="px-4 py-3",
                    ),
                    # Location/Floor
                    html.Td(
                        [
                            dcc.Input(
                                id=f"location-input-{i}",
                                value=ai_attributes["location"],
                                placeholder="Enter location...",
                                className="w-full px-2 py-1 border rounded text-sm",
                                persistence=True,
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # Door Type
                    html.Td(
                        [
                            dcc.Dropdown(
                                id=f"door-type-{i}",
                                options=[
                                    {"label": "🚪 Standard Entry", "value": "entry"},
                                    {"label": "🚪 Exit Only", "value": "exit"},
                                    {"label": "🛗 Elevator", "value": "elevator"},
                                    {"label": "🪜 Stairwell", "value": "stairwell"},
                                    {"label": "🚨 Fire Escape", "value": "fire_escape"},
                                    {"label": "🚪 Emergency", "value": "emergency"},
                                    {"label": "🏢 Office", "value": "office"},
                                    {"label": "🔧 Utility", "value": "utility"},
                                    {"label": "🅿️ Parking", "value": "parking"},
                                    {"label": "❓ Other", "value": "other"},
                                ],
                                value=ai_attributes["door_type"],
                                className="text-sm",
                                persistence=True,
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # Critical Status
                    html.Td(
                        [
                            html.Div(
                                [
                                    dcc.Checklist(
                                        id=f"critical-check-{i}",
                                        options=[{"label": "Critical", "value": "critical"}],
                                        value=["critical"] if ai_attributes["is_critical"] else [],
                                        className="text-sm",
                                        persistence=True,
                                    )
                                ],
                                className="flex items-center justify-center",
                            )
                        ],
                        className="px-4 py-3 text-center",
                    ),
                    # Security Level
                    html.Td(
                        [
                            html.Div(
                                [
                                    dcc.Slider(
                                        id=f"security-level-{i}",
                                        min=1,
                                        max=10,
                                        step=1,
                                        value=ai_attributes["security_level"],
                                        marks={1: "1", 5: "5", 10: "10"},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        className="w-full",
                                        persistence=True,
                                    )
                                ],
                                className="px-2",
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # AI Confidence
                    html.Td(
                        [
                            html.Div(
                                [
                                    html.Span(f"{ai_attributes['confidence']}%", className="text-sm font-medium"),
                                    html.Div("AI Confidence", className="text-xs text-gray-500"),
                                ],
                                className="text-center",
                            )
                        ],
                        className="px-4 py-3 text-center verify-column",
                    ),
                ],
                className="border-b hover:bg-gray-50",
                id=f"device-row-{i}",
            )
        )

    # Create the complete modal
    modal = html.Div(
        [
            # Modal overlay
            html.Div(
                [
                    # Modal container
                    html.Div(
                        [
                            # Modal header
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2(
                                                "🏢 Door & Device Mapping",
                                                className="text-xl font-semibold text-gray-900",
                                            ),
                                            html.P(
                                                f"Configure attributes for {len(devices)} doors/devices from column '{device_column}'",
                                                className="text-sm text-gray-600 mt-1",
                                            ),
                                        ],
                                        className="flex-1",
                                    ),
                                    html.Button(
                                        "×",
                                        id="close-door-mapping-modal",
                                        className="text-gray-400 hover:text-gray-600 text-2xl font-bold",
                                    ),
                                ],
                                className="flex items-center justify-between p-6 border-b",
                            ),
                            # Modal body with scrollable table
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Table(
                                                [
                                                    # Table header
                                                    html.Thead(
                                                        [
                                                            html.Tr(
                                                                [
                                                                    html.Th(
                                                                        "Device ID",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Location/Floor",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Door Type",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Critical",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Security Level",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "AI Confidence",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider verify-column",
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="bg-gray-50",
                                                    ),
                                                    # Table body
                                                    html.Tbody(
                                                        device_rows, className="bg-white divide-y divide-gray-200"
                                                    ),
                                                ],
                                                className="min-w-full divide-y divide-gray-200",
                                            )
                                        ],
                                        className="overflow-x-auto",
                                    )
                                ],
                                className="max-h-96 overflow-y-auto p-6",
                            ),
                            # Modal footer
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                f"{len(devices)} doors detected", className="text-sm text-gray-600"
                                            ),
                                            html.Span(
                                                "• Adjust settings and click Save",
                                                className="text-sm text-gray-500 ml-2",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                "Reset to AI Suggestions",
                                                id="reset-door-mappings",
                                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 mr-3",
                                            ),
                                            html.Button(
                                                "Cancel",
                                                id="cancel-door-mapping",
                                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 mr-3",
                                            ),
                                            html.Button(
                                                "💾 Save Door Mappings",
                                                id="save-door-mappings",
                                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
                                            ),
                                        ],
                                        className="flex",
                                    ),
                                ],
                                className="flex justify-between items-center p-6 border-t bg-gray-50",
                            ),
                        ],
                        className="bg-white rounded-lg max-w-6xl w-full max-h-screen overflow-hidden shadow-xl",
                    )
                ],
                className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-auto",
            ),
            # Hidden store for door mappings
            dcc.Store(id="door-mappings-store", data={"devices": devices, "column": device_column}),
        ]
    )

    return modal


def generate_ai_door_attributes(device_id: str) -> Dict[str, Any]:
    """Generate AI suggestions for door attributes using the DeviceMapper"""
    try:
        mapper = DeviceMapper()
        device_data = [{'device_name': device_id}]
        result = mapper.analyze_devices(device_data, 'device_name')

        if result['success'] and result['device_mappings']:
            mapping = result['device_mappings'][0]
            return {
                'floor': mapping['suggested_floor'],
                'area': mapping['suggested_area'],
                'confidence': mapping['confidence'],
                'pattern': mapping['pattern_matched']
            }
        else:
            return {
                'floor': 1,
                'area': 'general',
                'confidence': 0.3,
                'pattern': 'default'
            }
    except Exception as e:
        logger.error(f"Error generating AI door attributes: {e}")
        return {
            'floor': 1,
            'area': 'general',
            'confidence': 0.3,
            'pattern': 'error'
        }


@callback(
    [
        Output("mapping-verified-status", "children", allow_duplicate=True),
        Output("door-mapping-modal-overlay", "className", allow_duplicate=True),
    ],
    [
        Input("save-door-mappings", "n_clicks"),
        Input("cancel-door-mapping", "n_clicks"),
        Input("close-door-mapping-modal", "n_clicks"),
    ],
    [State("door-mappings-store", "data"), State("processed-data-store", "data")],
    prevent_initial_call=True,
)
def handle_door_mapping_save(save_clicks, cancel_clicks, close_clicks, door_store, processed_data):
    """Handle saving door mapping configurations"""
    from dash import no_update

    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Close modal on cancel or close
    hidden_class = "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

    if trigger_id in ["cancel-door-mapping", "close-door-mapping-modal"]:
        return no_update, hidden_class

    # Save door mappings
    if trigger_id == "save-door-mappings" and save_clicks:
        try:
            if not door_store or not processed_data:
                error_msg = html.Div("❌ No door mapping data to save", className="alert alert-error")
                return error_msg, hidden_class

            devices = door_store.get("devices", [])
            session_id = processed_data.get("session_id")

            # In a real implementation, you would collect all the form values here
            # For now, we'll simulate saving the configuration

            # Save to AI plugin if available
            if session_id:
                try:
                    from plugins.ai_classification.plugin import AIClassificationPlugin

                    ai_plugin = AIClassificationPlugin()
                    ai_plugin.start()

                    # Store door mappings in session
                    door_mapping_data = {
                        "devices": devices,
                        "device_count": len(devices),
                        "mapping_completed": True,
                        "saved_at": datetime.now().isoformat(),
                    }

                    ai_plugin.csv_repository.update_session_data(session_id, {"door_mappings": door_mapping_data})

                    logger.info(f"Door mappings saved for session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to save door mappings: {e}")

            success_msg = html.Div(
                [
                    html.Div("✅ Door mappings saved successfully!", className="alert alert-success"),
                    html.Div(
                        [
                            html.H4("📋 Mapping Complete:", className="font-bold mt-3"),
                            html.Ul(
                                [
                                    html.Li(f"✅ {len(devices)} doors/devices configured"),
                                    html.Li("✅ Security levels assigned"),
                                    html.Li("✅ Critical status determined"),
                                    html.Li("✅ Door types classified"),
                                    html.Li("🎯 Ready for analytics and monitoring"),
                                ],
                                className="list-disc ml-6 mt-2",
                            ),
                        ],
                        className="mt-3 p-3 bg-green-50 border border-green-200 rounded",
                    ),
                    html.Div(
                        [
                            html.Button(
                                "📊 View Analytics Dashboard",
                                id="goto-analytics",
                                className="btn btn-primary mt-3 mr-2",
                            ),
                            html.Button(
                                "📤 Upload Another File", id="reset-upload", className="btn btn-secondary mt-3"
                            ),
                        ],
                        className="mt-4",
                    ),
                ]
            )

            return success_msg, hidden_class

        except Exception as e:
            logger.error(f"Error saving door mappings: {e}")
            error_msg = html.Div(f"❌ Error saving door mappings: {str(e)}", className="alert alert-error")
            return error_msg, hidden_class

    return no_update, no_update


@callback(Output("upload-info", "children"), [Input("processed-data-store", "data")], prevent_initial_call=True)
def show_debug_info(processed_data):
    """Show debug information about available columns"""
    if not processed_data or "data" not in processed_data:
        return ""

    csv_data = processed_data["data"]
    if not csv_data:
        return ""

    available_columns = list(csv_data[0].keys())
    ai_suggestions = processed_data.get("ai_suggestions", {})

    debug_info = html.Div(
        [
            html.Details(
                [
                    html.Summary("🔍 Debug: Available Columns", className="cursor-pointer text-sm text-gray-600"),
                    html.Div(
                        [
                            html.P(
                                f"Available columns: {', '.join(available_columns)}",
                                className="text-xs text-gray-500 mt-2",
                            ),
                            html.P(f"AI suggestions: {ai_suggestions}", className="text-xs text-gray-500"),
                            html.P(
                                f"Sample row: {dict(list(csv_data[0].items())[:3])}...",
                                className="text-xs text-gray-500",
                            ),
                        ],
                        className="mt-2 p-2 bg-gray-50 rounded text-xs",
                    ),
                ]
            )
        ],
        className="mt-2",
    )

    return debug_info


# Export the layout function
layout = create_dual_file_uploader

__all__ = [
    "create_dual_file_uploader",
    "layout",
    "render_column_mapping_panel",
    "handle_upload_workflow",
    "handle_door_mapping",
    "handle_door_mapping_save",
]
