#!/usr/bin/env python3
"""
Column Header Verification Component
Allows manual verification of AI-suggested column mappings
Feeds back to AI training data
"""

import pandas as pd
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from typing import Dict, List, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Standard field options for dropdown
STANDARD_FIELD_OPTIONS = [
    {"label": "Person/User ID", "value": "person_id"},
    {"label": "Door/Location ID", "value": "door_id"},
    {"label": "Timestamp", "value": "timestamp"},
    {"label": "Access Result", "value": "access_result"},
    {"label": "Token/Badge ID", "value": "token_id"},
    {"label": "Badge Status", "value": "badge_status"},
    {"label": "Device Status", "value": "device_status"},
    {"label": "Event Type", "value": "event_type"},
    {"label": "Building/Floor", "value": "building_id"},
    {"label": "Entry/Exit Type", "value": "entry_type"},
    {"label": "Duration", "value": "duration"},
    {"label": "Ignore Column", "value": "ignore"},
    {"label": "Other/Custom", "value": "other"}
]

def create_column_verification_modal(file_info: Dict[str, Any]) -> dbc.Modal:
    """Create column verification modal for uploaded file"""
    filename = file_info.get('filename', 'Unknown File')
    columns = file_info.get('columns', [])
    sample_data = file_info.get('sample_data', {})
    ai_suggestions = file_info.get('ai_suggestions', {})

    return dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle(f"Verify Column Mappings - {filename}")
        ]),
        dbc.ModalBody([
            create_verification_interface(columns, sample_data, ai_suggestions)
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "Cancel",
                id="column-verify-cancel",
                color="secondary",
                className="me-2"
            ),
            dbc.Button(
                "Use AI Suggestions",
                id="column-verify-ai-auto",
                color="info",
                className="me-2"
            ),
            dbc.Button(
                "Confirm Mappings",
                id="column-verify-confirm",
                color="success"
            )
        ])
    ],
    id="column-verification-modal",
    size="xl",
    is_open=False,
    backdrop="static"
    )

def create_verification_interface(columns: List[str], sample_data: Dict, ai_suggestions: Dict) -> html.Div:
    """Create the main verification interface"""
    if not columns:
        return dbc.Alert("No columns found in uploaded file", color="warning")

    header_cards = []
    for i, column in enumerate(columns):
        ai_suggestion = ai_suggestions.get(column, {})
        suggested_field = ai_suggestion.get('field', '')
        confidence = ai_suggestion.get('confidence', 0.0)
        sample_values = list(sample_data.get(column, []))[:5]
        confidence_badge = create_confidence_badge(confidence)
        card = create_column_mapping_card(
            column_index=i,
            column_name=column,
            sample_values=sample_values,
            ai_suggestion=suggested_field,
            confidence_badge=confidence_badge
        )
        header_cards.append(card)

    return html.Div([
        dbc.Alert([
            html.H5("Column Mapping Verification", className="alert-heading mb-3"),
            html.P([
                "Please verify the AI-suggested column mappings below. Your feedback will help improve future suggestions. ",
                html.Strong("Green badges"), " indicate high AI confidence, ",
                html.Strong("yellow badges"), " indicate medium confidence, and ",
                html.Strong("red badges"), " indicate low confidence or no suggestion."
            ])
        ], color="info", className="mb-4"),
        html.Div(header_cards, className="column-mapping-cards"),
        dbc.Card([
            dbc.CardHeader([
                html.H6("AI Training Feedback", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Data Source Type:"),
                        dcc.Dropdown(
                            id="training-data-source-type",
                            options=[
                                {"label": "Corporate Access Control", "value": "corporate"},
                                {"label": "Educational Institution", "value": "education"},
                                {"label": "Healthcare Facility", "value": "healthcare"},
                                {"label": "Manufacturing/Industrial", "value": "manufacturing"},
                                {"label": "Retail/Commercial", "value": "retail"},
                                {"label": "Government/Public", "value": "government"},
                                {"label": "Residential", "value": "residential"},
                                {"label": "Other", "value": "other"}
                            ],
                            value="corporate",
                            className="mb-3"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Data Quality:"),
                        dcc.Dropdown(
                            id="training-data-quality",
                            options=[
                                {"label": "Excellent - Clean, consistent data", "value": "excellent"},
                                {"label": "Good - Minor inconsistencies", "value": "good"},
                                {"label": "Average - Some data issues", "value": "average"},
                                {"label": "Poor - Many inconsistencies", "value": "poor"},
                                {"label": "Very Poor - Major data quality issues", "value": "very_poor"}
                            ],
                            value="good",
                            className="mb-3"
                        )
                    ], width=6)
                ])
            ])
        ], className="mt-4")
    ])

def create_column_mapping_card(column_index: int, column_name: str, sample_values: List, ai_suggestion: str, confidence_badge: html.Span) -> dbc.Card:
    """Create individual column mapping card"""
    suggested_option = next((opt for opt in STANDARD_FIELD_OPTIONS if opt["value"] == ai_suggestion), None)
    default_value = ai_suggestion if suggested_option else "other"
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H6([
                        html.Code(column_name, className="bg-light px-2 py-1 rounded")
                    ], className="mb-0")
                ], width=8),
                dbc.Col([
                    confidence_badge
                ], width=4, className="text-end")
            ])
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Map to Standard Field:", className="fw-bold"),
                    dcc.Dropdown(
                        id={"type": "column-mapping", "index": column_index},
                        options=STANDARD_FIELD_OPTIONS,
                        value=default_value,
                        clearable=False,
                        className="mb-3"
                    ),
                    html.Div([
                        dbc.Label("Custom Field Name:"),
                        dbc.Input(
                            id={"type": "custom-field", "index": column_index},
                            placeholder="Enter custom field name...",
                            style={"display": "none"}
                        )
                    ], id={"type": "custom-field-container", "index": column_index})
                ], width=6),
                dbc.Col([
                    dbc.Label("Sample Values:", className="fw-bold"),
                    html.Div([
                        dbc.Badge(
                            str(value)[:50] + "..." if len(str(value)) > 50 else str(value),
                            color="light",
                            text_color="dark",
                            className="me-1 mb-1"
                        ) for value in sample_values[:5]
                    ] if sample_values else [
                        html.Small("No sample data available", className="text-muted")
                    ])
                ], width=6)
            ])
        ])
    ], className="mb-3")

def create_confidence_badge(confidence: float) -> html.Span:
    """Create confidence badge based on AI confidence score"""
    if confidence >= 0.8:
        return dbc.Badge(f"High {confidence:.0%}", color="success", className="confidence-badge")
    elif confidence >= 0.5:
        return dbc.Badge(f"Medium {confidence:.0%}", color="warning", className="confidence-badge")
    elif confidence > 0:
        return dbc.Badge(f"Low {confidence:.0%}", color="danger", className="confidence-badge")
    else:
        return dbc.Badge("No AI Suggestion", color="secondary", className="confidence-badge")

def get_ai_column_suggestions(df: pd.DataFrame, filename: str) -> Dict[str, Dict[str, Any]]:
    """Get AI suggestions for column mappings"""
    suggestions = {}
    try:
        from plugins.ai_classification.plugin import AIClassificationPlugin
        from plugins.ai_classification.config import get_ai_config
        ai_plugin = AIClassificationPlugin(get_ai_config())
        if ai_plugin.start():
            headers = df.columns.tolist()
            session_id = f"column_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ai_result = ai_plugin.map_columns(headers, session_id)
            if ai_result.get('success'):
                suggested_mapping = ai_result.get('suggested_mapping', {})
                confidence_scores = ai_result.get('confidence_scores', {})
                for header in headers:
                    if header in suggested_mapping:
                        suggestions[header] = {
                            'field': suggested_mapping[header],
                            'confidence': confidence_scores.get(header, 0.0)
                        }
                    else:
                        suggestions[header] = {'field': '', 'confidence': 0.0}
                logger.info(f"AI suggestions generated for {len(suggestions)} columns")
            else:
                logger.warning("AI mapping failed, using fallback suggestions")
                suggestions = _get_fallback_suggestions(df.columns.tolist())
        else:
            logger.warning("AI plugin failed to start, using fallback suggestions")
            suggestions = _get_fallback_suggestions(df.columns.tolist())
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        suggestions = _get_fallback_suggestions(df.columns.tolist())
    return suggestions

def _get_fallback_suggestions(columns: List[str]) -> Dict[str, Dict[str, Any]]:
    """Fallback column suggestions using simple heuristics"""
    suggestions = {}
    for column in columns:
        column_lower = column.lower()
        suggestion = {'field': '', 'confidence': 0.0}
        if any(keyword in column_lower for keyword in ['person', 'user', 'employee', 'name']):
            suggestion = {'field': 'person_id', 'confidence': 0.7}
        elif any(keyword in column_lower for keyword in ['door', 'location', 'device', 'room']):
            suggestion = {'field': 'door_id', 'confidence': 0.7}
        elif any(keyword in column_lower for keyword in ['time', 'date', 'stamp']):
            suggestion = {'field': 'timestamp', 'confidence': 0.8}
        elif any(keyword in column_lower for keyword in ['result', 'status', 'access']):
            suggestion = {'field': 'access_result', 'confidence': 0.7}
        elif any(keyword in column_lower for keyword in ['token', 'badge', 'card']):
            suggestion = {'field': 'token_id', 'confidence': 0.6}
        suggestions[column] = suggestion
    return suggestions

def save_verified_mappings(filename: str, column_mappings: Dict[str, str], metadata: Dict[str, Any]) -> bool:
    """Save verified column mappings for AI training"""
    try:
        training_data = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'mappings': column_mappings,
            'metadata': metadata,
            'verified_by_user': True
        }
        try:
            from plugins.ai_classification.plugin import AIClassificationPlugin
            from plugins.ai_classification.config import get_ai_config
            ai_plugin = AIClassificationPlugin(get_ai_config())
            if ai_plugin.start():
                session_id = f"verified_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                ai_plugin.confirm_column_mapping(column_mappings, session_id)
                if hasattr(ai_plugin, 'csv_repository'):
                    ai_plugin.csv_repository.store_column_mapping(session_id, training_data)
                logger.info(f"Verified mappings saved to AI system for {filename}")
        except Exception as ai_e:
            logger.warning(f"Failed to save to AI system: {ai_e}")
        try:
            import os
            os.makedirs('data/training', exist_ok=True)
            training_file = f"data/training/column_mappings_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(training_file, 'a') as f:
                f.write(json.dumps(training_data) + '\n')
            logger.info(f"Training data appended to {training_file}")
        except Exception as file_e:
            logger.warning(f"Failed to save training file: {file_e}")
        return True
    except Exception as e:
        logger.error(f"Error saving verified mappings: {e}")
        return False

@callback(
    Output({"type": "custom-field", "index": MATCH}, "style"),
    Input({"type": "column-mapping", "index": MATCH}, "value")
)
def toggle_custom_field(selected_value):
    """Show custom field input when 'other' is selected"""
    if selected_value == "other":
        return {"display": "block"}
    else:
        return {"display": "none"}

__all__ = [
    'create_column_verification_modal',
    'get_ai_column_suggestions',
    'save_verified_mappings'
]
