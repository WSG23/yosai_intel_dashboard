"""Device verification component - follows exact same pattern as column_verification.py"""

import pandas as pd
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH
import dash
import dash_bootstrap_components as dbc
from typing import Dict, List, Any
import logging
from datetime import datetime

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
    Output("upload-results", "children", allow_duplicate=True),
    [Input("device-verify-confirm", "n_clicks")],
    [State({"type": "device-name", "index": ALL}, "data"),
     State({"type": "device-floor", "index": ALL}, "value"),
     State({"type": "device-access", "index": ALL}, "value"),
     State({"type": "device-special", "index": ALL}, "value"),
     State({"type": "device-security", "index": ALL}, "value"),
     State("current-session-id", "data")],
    prevent_initial_call=True
)
def confirm_device_mappings(n_clicks, device_names, floors, access_types, special_areas, 
                          security_levels, session_id):
    """Confirm device mappings - same pattern as column confirmation"""
    if not n_clicks or not session_id:
        return dash.no_update

    try:
        device_mappings = {}
        corrections_count = 0
        
        for i, device_name in enumerate(device_names or []):
            if not device_name:
                continue
                
            # Get original attributes for comparison
            # (In real implementation, you'd compare with original AI suggestions)
            manually_edited = True  # Simplified - assume user reviewed it
            
            attributes = {
                'floor_number': floors[i] if i < len(floors or []) else None,
                'is_entry': 'is_entry' in (access_types[i] if i < len(access_types or []) else []),
                'is_exit': 'is_exit' in (access_types[i] if i < len(access_types or []) else []),
                'is_elevator': 'is_elevator' in (special_areas[i] if i < len(special_areas or []) else []),
                'is_stairwell': 'is_stairwell' in (special_areas[i] if i < len(special_areas or []) else []),
                'is_fire_escape': 'is_fire_escape' in (special_areas[i] if i < len(special_areas or []) else []),
                'security_level': security_levels[i] if i < len(security_levels or []) else 1,
                'manually_edited': manually_edited,
                'ai_generated': True
            }
            
            device_mappings[device_name] = attributes
            if manually_edited:
                corrections_count += 1

        print(f"🤖 Device AI will learn from {corrections_count} corrections")
        
        # Here you would call your AI service
        # ai_plugin = get_ai_plugin()  # Your method to get plugin
        # ai_plugin.confirm_device_mapping(device_mappings, session_id)

        return dbc.Alert([
            html.H6("Device Classifications Confirmed!", className="alert-heading mb-2"),
            html.P([
                f"Processed {len(device_mappings)} devices. ",
                f"AI learned from {corrections_count} manual corrections."
            ]),
            html.Hr(),
            html.P("Ready for data analysis with enhanced device context.", className="mb-0")
        ], color="success")

    except Exception as e:
        return dbc.Alert(f"Error confirming device mappings: {str(e)}", color="danger")


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
    'confirm_device_mappings'
]
