"""
Door Mapping Modal Component for Device Attribute Assignment
Integrates with Yōsai Intel Dashboard modular architecture
"""
from dash import html, dcc, Input, Output, State
from dash import callback_context
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
                        html.Button("×", 
                                   id="door-mapping-modal-close-btn",
                                   className="text-white hover:text-gray-300 text-2xl font-bold")
                    ], className="flex items-center justify-between p-6 border-b border-gray-700"),
                    
                    # Modal body
                    html.Div([
                        html.Div(id="door-mapping-table-container"),
                        html.Div(id="door-mapping-row-count", className="text-sm text-gray-400 mt-2")
                    ], className="p-6 max-h-96 overflow-y-auto"),
                    
                    # Modal footer
                    html.Div([
                        html.Button("Reset", 
                                   id="door-mapping-reset-btn",
                                   className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 mr-2"),
                        html.Button("Save Changes", 
                                   id="door-mapping-save-btn",
                                   className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700")
                    ], className="flex justify-end p-6 border-t border-gray-700")
                ], className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-screen overflow-hidden")
            ], className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden",
               id="door-mapping-modal-overlay"),
            
            # Data stores
            dcc.Store(id="door-mapping-modal-data-trigger"),
            dcc.Store(id="door-mapping-original-data-store"),
            dcc.Store(id="door-mapping-current-data-store"),
            dcc.Store(id="door-mapping-manual-edits-store", data={})
        ])
        
        return modal_content
        
    except Exception as e:
        logger.error(f"Error creating door mapping modal: {e}")
        return html.Div(f"Error creating door mapping modal: {str(e)}")


def create_device_mapping_table(devices_data: List[Dict]) -> html.Table:
    """Create the device mapping table"""
    if not devices_data:
        return html.Div("No devices data available", className="text-gray-400")
    
    # Table header
    table_header = html.Thead([
        html.Tr([
            html.Th("Device ID", className="p-3 text-left font-medium text-gray-300"),
            html.Th("Location", className="p-3 text-left font-medium text-gray-300"),
            html.Th("Critical", className="p-3 text-center font-medium text-gray-300"),
            html.Th("Security Level", className="p-3 text-center font-medium text-gray-300")
        ])
    ], className="bg-gray-700")
    
    # Table rows
    table_rows = []
    for i, device in enumerate(devices_data):
        device_id = device.get('device_id', f'device_{i}')
        location = device.get('location', 'Unknown')
        is_critical = device.get('critical', False)
        security_level = device.get('security_level', 50)
        
        row = html.Tr([
            html.Td(device_id, className="p-3 text-gray-300"),
            html.Td(location, className="p-3 text-gray-300"),
            html.Td([
                dbc.Switch(
                    id=f"critical-switch-{device_id}",
                    value=is_critical,
                    className="justify-center"
                )
            ], className="p-3 text-center"),
            html.Td([
                dcc.Slider(
                    id=f"security-slider-{device_id}",
                    min=0,
                    max=100,
                    step=10,
                    value=security_level,
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


class DoorMappingCallbackManager:
    """Callback manager for door mapping modal"""
    
    def __init__(self, callback_registry):
        self.registry = callback_registry
        
    def register_all(self):
        """Register all door mapping callbacks"""
        self._register_modal_visibility()
        self._register_data_updates()
        self._register_table_updates()
        self._register_clientside_callbacks()
        
    def _register_modal_visibility(self):
        """Register modal visibility callbacks"""
        @self.registry.register_callback(
            outputs=Output("door-mapping-modal-overlay", "className"),  # Single output
            inputs=[
                Input("door-mapping-modal-trigger", "n_clicks"),
                Input("door-mapping-modal-close-btn", "n_clicks"),
                Input("door-mapping-modal-overlay", "n_clicks")
            ],
            states=[State("door-mapping-modal-overlay", "className")],
            callback_id="door_mapping_modal_visibility"
        )
        def toggle_modal_visibility(open_clicks, close_clicks, overlay_clicks, current_class):
            """Toggle door mapping modal visibility"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            if triggered_id == "door-mapping-modal-trigger":
                return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center"
            else:
                return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"
    
    def _register_data_updates(self):
        """Register data update callbacks"""
        @self.registry.register_callback(
            outputs=Output("door-mapping-current-data-store", "data"),  # Single output
            inputs=[
                Input("door-mapping-modal-data-trigger", "data"),
                Input("door-mapping-reset-btn", "n_clicks")
            ],
            states=[State("door-mapping-original-data-store", "data")],
            callback_id="door_mapping_data_updates"
        )
        def handle_data_updates(modal_data, reset_clicks, original_data):
            """Handle current data store updates"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if triggered_id == "door-mapping-modal-data-trigger":
                if modal_data:
                    return modal_data.get('devices', [])
            elif triggered_id == "door-mapping-reset-btn":
                if reset_clicks and original_data:
                    return original_data

            raise dash.exceptions.PreventUpdate
    
    def _register_table_updates(self):
        """Register table update callbacks"""
        @self.registry.register_callback(
            outputs=[
                Output("door-mapping-table-container", "children"),
                Output("door-mapping-row-count", "children"),
                Output("door-mapping-original-data-store", "data")
            ],
            inputs=[Input("door-mapping-modal-data-trigger", "data")],
            callback_id="door_mapping_table_updates"
        )
        def update_table_content(modal_data):
            """Update table content when new data is provided"""
            if not modal_data:
                raise dash.exceptions.PreventUpdate

            devices_data = modal_data.get('devices', [])
            row_count = len(devices_data)

            table = create_device_mapping_table(devices_data)
            row_count_text = f"{row_count} rows detected"

            return table, row_count_text, devices_data
    
    def _register_clientside_callbacks(self):
        """Register clientside callbacks"""
        # Handle manual edits tracking
        self.registry.register_clientside_callback(
            """
            function(save_clicks, reset_clicks, current_edits, original_data) {
                const ctx = window.dash_clientside.callback_context;
                if (!ctx.triggered || ctx.triggered.length === 0) {
                    return window.dash_clientside.no_update;
                }

                const triggered_id = ctx.triggered[0].prop_id.split('.')[0];
                
                if (triggered_id === 'door-mapping-save-btn') {
                    // Handle save logic here
                    return current_edits || {};
                } else if (triggered_id === 'door-mapping-reset-btn') {
                    // Clear edits on reset
                    return {};
                }
                
                return window.dash_clientside.no_update;
            }
            """,
            outputs=[Output("door-mapping-manual-edits-store", "data")],
            inputs=[
                Input("door-mapping-save-btn", "n_clicks"),
                Input("door-mapping-reset-btn", "n_clicks")
            ],
            states=[
                State("door-mapping-manual-edits-store", "data"),
                State("door-mapping-original-data-store", "data")
            ],
            callback_id="door_mapping_manual_edits_tracking"
        )

