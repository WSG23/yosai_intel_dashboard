"""Device verification component - follows exact same pattern as column_verification.py"""

import pandas as pd
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH
import dash
import dash_bootstrap_components as dbc
from typing import Dict, List, Any
import logging
from datetime import datetime
from components.simple_device_mapping import _device_ai_mappings

logger = logging.getLogger(__name__)


def create_device_verification_modal(device_mappings: Dict[str, Dict], session_id: str) -> dbc.Modal:
    """Create device verification modal - same pattern as column verification"""
    
    if not device_mappings:
        return html.Div()

    # Create table rows for each device
    table_rows = []
    for i, (device_name, attributes) in enumerate(device_mappings.items()):
        confidence = attributes.get('confidence', 0.0)
        
        table_rows.append(
            html.Tr([
                # Device name and confidence
                html.Td([
                    html.Strong(device_name),
                    html.Br(),
                    html.Small(
                        f"AI Confidence: {confidence:.0%}",
                        className="text-muted" if confidence < 0.5 else "text-success"
                    )
                ], style={"width": "25%"}),
                
                # Floor number
                html.Td([
                    dbc.Input(
                        id={"type": "device-floor", "index": i},
                        type="number",
                        min=0, max=50,
                        value=attributes.get('floor_number'),
                        placeholder="Floor #",
                        size="sm"
                    )
                ], style={"width": "10%"}),
                
                # Entry/Exit checkboxes
                html.Td([
                    dbc.Checklist(
                        id={"type": "device-access", "index": i},
                        options=[
                            {"label": "Entry", "value": "is_entry"},
                            {"label": "Exit", "value": "is_exit"},
                        ],
                        value=[k for k, v in attributes.items() if k in ["is_entry", "is_exit"] and v],
                        inline=True
                    )
                ], style={"width": "15%"}),
                
                # Special areas
                html.Td([
                    dbc.Checklist(
                        id={"type": "device-special", "index": i},
                        options=[
                            {"label": "Elevator", "value": "is_elevator"},
                            {"label": "Stairwell", "value": "is_stairwell"},
                            {"label": "Fire Escape", "value": "is_fire_escape"},
                        ],
                        value=[k for k, v in attributes.items() if k in ["is_elevator", "is_stairwell", "is_fire_escape"] and v],
                        inline=False
                    )
                ], style={"width": "20%"}),
                
                # Security level
                html.Td([
                    dbc.Input(
                        id={"type": "device-security", "index": i},
                        type="number",
                        min=0, max=10,
                        value=attributes.get('security_level', 1),
                        placeholder="0-10",
                        size="sm"
                    )
                ], style={"width": "10%"}),
                
                # Manually edited flag (hidden input)
                html.Td([
                    dcc.Store(
                        id={"type": "device-name", "index": i},
                        data=device_name
                    ),
                    dcc.Store(
                        id={"type": "device-edited", "index": i},
                        data=False
                    )
                ], style={"width": "0%", "display": "none"})
            ])
        )

    modal_body = html.Div([
        html.H5(f"Device Classification - {len(device_mappings)} devices found"),
        dbc.Alert([
            "AI has analyzed your devices and made suggestions. ",
            "Review and correct any mistakes to help the AI learn."
        ], color="info", className="mb-3"),
        
        dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Device Name", style={"width": "25%"}),
                    html.Th("Floor", style={"width": "10%"}),
                    html.Th("Access Type", style={"width": "15%"}),
                    html.Th("Special Areas", style={"width": "20%"}),
                    html.Th("Security (0-10)", style={"width": "10%"}),
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, hover=True, size="sm"),

        dbc.Card([
            dbc.CardHeader(html.H6("Security Level Guide", className="mb-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Badge("0-2", color="success"), " Public areas (lobby, restrooms)"
                    ], width=6),
                    dbc.Col([
                        dbc.Badge("3-5", color="warning"), " General office areas"
                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Badge("6-8", color="danger"), " Restricted areas (server rooms)"
                    ], width=6),
                    dbc.Col([
                        dbc.Badge("9-10", color="dark"), " High security (executive, finance)"
                    ], width=6),
                ], className="mt-2")
            ])
        ], className="mt-3")
    ])

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("AI Device Classification Verification")),
        dbc.ModalBody(modal_body, id="device-modal-body"),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="device-verify-cancel", color="secondary", className="me-2"),
            dbc.Button("Confirm & Train AI", id="device-verify-confirm", color="success"),
        ])
    ],
    id="device-verification-modal",
    size="xl",
    is_open=False,
    scrollable=True
    )


@callback(
    [
        Output("upload-results", "children", allow_duplicate=True),
        Output("device-verification-modal", "is_open", allow_duplicate=True),
    ],
    [Input("device-verify-confirm", "n_clicks")],
    [State({"type": "device-name", "index": ALL}, "data"),
     State({"type": "device-floor", "index": ALL}, "value"),
     State({"type": "device-access", "index": ALL}, "value"),
     State({"type": "device-special", "index": ALL}, "value"),
     State({"type": "device-security", "index": ALL}, "value")],
    prevent_initial_call=True
)
def confirm_device_mappings_with_success(n_clicks, device_names, floors, access_types, special_areas, security_levels):
    """Confirm device mappings with proper success message and keep buttons available"""
    if not n_clicks:
        return dash.no_update, dash.no_update

    try:
        print(f"🔄 Confirming device mappings...")

        # Safely handle inputs
        device_names = device_names or []
        floors = floors or []
        access_types = access_types or []
        special_areas = special_areas or []
        security_levels = security_levels or []

        device_mappings = {}
        corrections_count = 0

        for i, device_name in enumerate(device_names):
            if not device_name:
                continue

            # Safely get values
            floor_val = floors[i] if i < len(floors) else None
            access_val = access_types[i] if i < len(access_types) else []
            special_val = special_areas[i] if i < len(special_areas) else []
            security_val = security_levels[i] if i < len(security_levels) else 5

            access_val = access_val or []
            special_val = special_val or []

            attributes = {
                'floor_number': floor_val,
                'is_entry': 'is_entry' in access_val,
                'is_exit': 'is_exit' in access_val,
                'is_elevator': 'is_elevator' in special_val,
                'is_stairwell': 'is_stairwell' in special_val,
                'is_fire_escape': 'is_fire_escape' in special_val,
                'security_level': security_val,
                'manually_edited': True,
                'ai_generated': True
            }

            device_mappings[device_name] = attributes
            corrections_count += 1

        print(f"✅ Device mappings confirmed: {device_mappings}")

        # Store mappings globally for transfer to simple mapping
        global _device_ai_mappings
        _device_ai_mappings = device_mappings

        # Create success message with device mapping button still available
        success_message = html.Div([
            dbc.Alert([
                html.H6("🎉 Device Classifications Confirmed!", className="alert-heading mb-2"),
                html.P([
                    f"Successfully processed {len(device_mappings)} devices. ",
                    f"AI learned from {corrections_count} manual corrections."
                ]),
                html.Hr(),
                html.P("Device mappings saved and available for manual mapping!", className="mb-0")
            ], color="success", className="mb-3"),

            # Keep the device mapping button available
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "📍 Map Manual",
                        id="open-device-mapping",
                        color="outline-primary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "🤖 Classify Devices",
                        id="classify-devices-btn",
                        color="outline-info",
                        size="sm"
                    )
                ])
            ])
        ])

        return success_message, False  # Close modal but keep interface

    except Exception as e:
        print(f"❌ Error confirming device mappings: {e}")
        error_message = dbc.Alert([
            html.H6("Error Processing Device Mappings", className="alert-heading"),
            html.P(f"An error occurred: {str(e)}"),
        ], color="danger")
        return error_message, False


@callback(
    Output({"type": "device-edited", "index": MATCH}, "data"),
    [Input({"type": "device-floor", "index": MATCH}, "value"),
     Input({"type": "device-access", "index": MATCH}, "value"),
     Input({"type": "device-special", "index": MATCH}, "value"),
     Input({"type": "device-security", "index": MATCH}, "value")],
    prevent_initial_call=True
)
def mark_device_as_edited(floor, access, special, security):
    """Mark device as manually edited when user makes changes"""
    return True  # Simplified - any change marks as edited


__all__ = [
    'create_device_verification_modal',
    'confirm_device_mappings_with_success'
]
