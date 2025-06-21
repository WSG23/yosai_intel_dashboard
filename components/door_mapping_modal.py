"""
Door Mapping Modal Component for Device Attribute Assignment
Integrates with Yōsai Intel Dashboard modular architecture
"""
from dash import html, dcc, clientside_callback, Input, Output, State, callback_context
import dash
import dash_bootstrap_components as dbc
from typing import Any, List, Dict, Optional
import logging
import json

logger = logging.getLogger(__name__)

# Safe import handling
try:
    from dash import dcc
    DASH_AVAILABLE = True
except ImportError:
    logger.warning("Dash not available for door mapping modal")
    DASH_AVAILABLE = False


def create_door_mapping_modal() -> html.Div:
    """Create the door mapping modal component"""
    
    if not DASH_AVAILABLE:
        return html.Div("Door mapping modal not available")

    try:
        modal_content = html.Div([
            # Modal overlay
            html.Div([
                # Modal container
                html.Div([
                    # Modal header
                    html.Div([
                        html.Div([
                            html.H2("Device Attribute Assignment", 
                                   className="text-white text-xl font-semibold mb-1"),
                            html.P("Review and adjust values before final upload.", 
                                  className="text-gray-400 text-sm")
                        ], className="flex-1"),
                        html.Button([
                            html.I(className="fas fa-times")
                        ], 
                        id="door-mapping-modal-close-btn",
                        className="text-gray-400 hover:text-white text-xl bg-transparent border-0 p-0")
                    ], className="flex items-start justify-between mb-4"),

                    # Modal body - main content area
                    html.Div([
                        # Left panel - Summary info
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Strong("Upload Summary: ", className="text-gray-300"),
                                    html.Span(id="door-mapping-row-count", 
                                             children="0 rows detected",
                                             className="text-gray-200")
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Data Source: ", className="text-gray-300"),
                                    html.Span(id="door-mapping-data-source",
                                             children="Parsed from AI model v2.3",
                                             className="text-gray-200")
                                ], className="mb-2"),
                                html.Div([
                                    html.Strong("Profile: ", className="text-gray-300"),
                                    html.Span(id="door-mapping-client-profile",
                                             children="Auto-detected profile",
                                             className="text-gray-200")
                                ], className="mb-2"),
                                
                                # Action buttons
                                html.Div([
                                    dbc.Button("Save Manual Edits", 
                                             id="door-mapping-save-edits-btn",
                                             color="primary", 
                                             size="sm",
                                             className="me-2 mb-2"),
                                    dbc.Button("Reset to AI Values", 
                                             id="door-mapping-reset-btn",
                                             color="secondary", 
                                             size="sm",
                                             className="mb-2"),
                                    dbc.Button("Apply & Upload", 
                                             id="door-mapping-apply-btn",
                                             color="success", 
                                             size="sm",
                                             className="w-100")
                                ], className="mt-4")
                            ])
                        ], className="bg-gray-800 p-4 rounded-md w-1/4 text-sm"),

                        # Right panel - Device mapping table
                        html.Div([
                            html.Div([
                                # Table container with scroll
                                html.Div(id="door-mapping-table-container", 
                                        className="overflow-y-auto", 
                                        style={"height": "500px"})
                            ])
                        ], className="w-3/4 ml-4")

                    ], className="flex gap-4"),

                    # Hidden storage for manual edits tracking
                    dcc.Store(id="door-mapping-manual-edits-store", data={}),
                    dcc.Store(id="door-mapping-original-data-store", data={}),
                    dcc.Store(id="door-mapping-current-data-store", data={}),
                    dcc.Store(id="door-mapping-modal-data-trigger", data=None)

                ], className="bg-gray-900 rounded-xl shadow-xl p-6 flex flex-col",
                   style={"width": "90%", "maxWidth": "1200px"}),
            ], 
            className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden",
            id="door-mapping-modal-overlay",
            style={"zIndex": "9999"})
        ], id="door-mapping-modal-container")

        return modal_content

    except Exception as e:
        logger.error(f"Error creating door mapping modal: {e}")
        return html.Div(f"Door mapping modal error: {e}", className="text-danger")


def create_device_mapping_table(devices_data: List[Dict[str, Any]]) -> html.Div:
    """Create the device mapping table with toggles and sliders"""
    
    if not devices_data:
        return html.Div("No device data available", className="text-gray-400 text-center p-4")
    
    # Table header
    table_header = html.Thead([
        html.Tr([
            html.Th("Device", className="p-2 text-left text-gray-300"),
            html.Th("Entry", className="p-2 text-center text-gray-300"),
            html.Th("Exit", className="p-2 text-center text-gray-300"),
            html.Th("Elevator", className="p-2 text-center text-gray-300"),
            html.Th("Stairwell", className="p-2 text-center text-gray-300"),
            html.Th("Fire Escape", className="p-2 text-center text-gray-300"),
            html.Th("Other", className="p-2 text-center text-gray-300"),
            html.Th("Security Level", className="p-2 text-center text-gray-300"),
        ], className="sticky top-0 bg-gray-800")
    ], className="sticky top-0 bg-gray-800")
    
    # Table rows
    table_rows = []
    for i, device in enumerate(devices_data):
        device_id = device.get('door_id', f"device_{i}")
        confidence = device.get('confidence', 0)
        
        # Confidence badge
        confidence_badge = ""
        if confidence > 0:
            confidence_badge = html.Span(
                f"{confidence}% match",
                className="ml-2 text-xs bg-blue-600 text-white rounded-full px-2 py-0.5"
            )
        
        row = html.Tr([
            # Device name with confidence badge
            html.Td([
                html.Span(device.get('name', device_id)),
                confidence_badge
            ], className="p-2"),
            
            # Toggle switches for each attribute
            html.Td(create_toggle_switch(f"{device_id}-entry", device.get('entry', False)), 
                   className="p-2 text-center"),
            html.Td(create_toggle_switch(f"{device_id}-exit", device.get('exit', False)), 
                   className="p-2 text-center"),
            html.Td(create_toggle_switch(f"{device_id}-elevator", device.get('elevator', False)), 
                   className="p-2 text-center"),
            html.Td(create_toggle_switch(f"{device_id}-stairwell", device.get('stairwell', False)), 
                   className="p-2 text-center"),
            html.Td(create_toggle_switch(f"{device_id}-fire_escape", device.get('fire_escape', False)), 
                   className="p-2 text-center"),
            html.Td(create_toggle_switch(f"{device_id}-other", device.get('other', False)), 
                   className="p-2 text-center"),
            
            # Security level slider
            html.Td([
                dcc.Slider(
                    id=f"{device_id}-security-slider",
                    min=0,
                    max=100,
                    value=device.get('security_level', 50),
                    marks={0: {'label': 'Low', 'style': {'color': '#10B981'}},
                           100: {'label': 'High', 'style': {'color': '#EF4444'}}},
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="security-level-slider"
                )
            ], className="p-2", style={"width": "120px"})
            
        ], className="border-b border-gray-700 hover:bg-gray-800",
           id=f"device-row-{device_id}")
        
        table_rows.append(row)
    
    # Complete table
    table = html.Table([
        table_header,
        html.Tbody(table_rows)
    ], className="w-full text-left text-sm text-gray-300")
    
    return table


def create_toggle_switch(switch_id: str, checked: bool = False) -> dbc.Switch:
    """Create a custom toggle switch component"""
    return dbc.Switch(
        id=switch_id,
        value=checked,
        className="door-mapping-toggle-switch",
        style={"transform": "scale(0.8)"}
    )


def register_door_mapping_modal_callbacks(app):
    """Register callbacks for door mapping modal functionality"""
    
    if not DASH_AVAILABLE:
        return

    try:
        # Toggle modal visibility
        @app.callback(
            Output("door-mapping-modal-overlay", "className"),
            [
                Input("door-mapping-modal-trigger", "n_clicks"),
                Input("door-mapping-modal-close-btn", "n_clicks"),
                Input("door-mapping-modal-overlay", "n_clicks"),
            ],
            [State("door-mapping-modal-overlay", "className")],
            prevent_initial_call=True,
        )
        def toggle_door_mapping_modal(open_clicks, close_clicks, overlay_clicks, current_class):
            """Toggle the door mapping modal visibility"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            if triggered_id == "door-mapping-modal-trigger":
                # Open modal
                return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center"
            else:
                # Close modal
                return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

        # Update modal content when data is uploaded
        @app.callback(
            [
                Output("door-mapping-table-container", "children"),
                Output("door-mapping-row-count", "children"),
                Output("door-mapping-original-data-store", "data"),
                Output("door-mapping-current-data-store", "data")
            ],
            [Input("door-mapping-modal-data-trigger", "data")],
            prevent_initial_call=True
        )
        def update_door_mapping_content(modal_data):
            """Update modal content when new data is provided"""
            if not modal_data:
                raise dash.exceptions.PreventUpdate
            
            devices_data = modal_data.get('devices', [])
            row_count = len(devices_data)
            
            table = create_device_mapping_table(devices_data)
            row_count_text = f"{row_count} rows detected"
            
            return table, row_count_text, devices_data, devices_data

        # Track manual edits
        clientside_callback(
            """
            function(n_clicks, current_edits, original_data) {
                if (!n_clicks) {
                    return window.dash_clientside.no_update;
                }
                
                // Collect all current form values
                const manual_edits = {};
                const form_elements = document.querySelectorAll('[id*="-entry"], [id*="-exit"], [id*="-elevator"], [id*="-stairwell"], [id*="-fire_escape"], [id*="-other"], [id*="-security-slider"]');
                
                form_elements.forEach(element => {
                    const device_id = element.id.split('-')[0];
                    const attribute = element.id.split('-').slice(1).join('_');
                    
                    if (!manual_edits[device_id]) {
                        manual_edits[device_id] = {};
                    }
                    
                    if (element.type === 'range') {
                        manual_edits[device_id][attribute] = parseInt(element.value);
                    } else {
                        manual_edits[device_id][attribute] = element.checked;
                    }
                });
                
                // Store in localStorage for persistence
                localStorage.setItem('yosai_door_mapping_manual_edits', JSON.stringify(manual_edits));
                
                return manual_edits;
            }
            """,
            Output("door-mapping-manual-edits-store", "data"),
            [Input("door-mapping-save-edits-btn", "n_clicks")],
            [State("door-mapping-manual-edits-store", "data"),
             State("door-mapping-original-data-store", "data")],
            prevent_initial_call=True
        )

        # Reset to AI values
        @app.callback(
            Output("door-mapping-current-data-store", "data"),
            [Input("door-mapping-reset-btn", "n_clicks")],
            [State("door-mapping-original-data-store", "data")],
            prevent_initial_call=True,
            allow_duplicate=True
        )
        def reset_to_ai_values(n_clicks, original_data):
            """Reset all values to original AI-generated values"""
            if not n_clicks:
                raise dash.exceptions.PreventUpdate
            
            # Clear localStorage
            clientside_callback(
                """
                function() {
                    localStorage.removeItem('yosai_door_mapping_manual_edits');
                    return null;
                }
                """,
                Output("door-mapping-manual-edits-store", "data"),
                [Input("door-mapping-reset-btn", "n_clicks")],
                prevent_initial_call=True,
                allow_duplicate=True
            )
            
            return original_data

    except Exception as e:
        logger.error(f"Error registering door mapping modal callbacks: {e}")


# Export the layout function for consistency with other components
layout = create_door_mapping_modal
__all__ = ["create_door_mapping_modal", "register_door_mapping_modal_callbacks", "layout", "create_device_mapping_table"]
