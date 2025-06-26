"""Simple manual device mapping component"""

from dash import html, dcc, callback, Input, Output, State, ALL
import dash
import dash_bootstrap_components as dbc
from typing import List


def create_simple_device_modal(devices: List[str]) -> dbc.Modal:
    """Create simple device mapping modal"""

    if not devices:
        devices = [
            "lobby_door",
            "office_201",
            "server_room",
            "elevator_1",
        ]  # Sample devices

    # Create rows for each device
    device_rows = []
    for i, device in enumerate(devices):
        device_rows.append(
            dbc.Row(
                [
                    dbc.Col([html.Strong(device)], width=4),
                    dbc.Col(
                        [
                            dbc.Input(
                                id={"type": "device-floor", "index": i},
                                type="number",
                                placeholder="Floor #",
                                min=0,
                                max=50,
                                size="sm",
                            )
                        ],
                        width=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Checklist(
                                id={"type": "device-access", "index": i},
                                options=[
                                    {"label": "Entry", "value": "entry"},
                                    {"label": "Exit", "value": "exit"},
                                ],
                                inline=True,
                            )
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            dbc.Input(
                                id={"type": "device-security", "index": i},
                                type="number",
                                placeholder="0-10",
                                min=0,
                                max=10,
                                value=1,
                                size="sm",
                            )
                        ],
                        width=2,
                    ),
                    dcc.Store(
                        id={"type": "device-name", "index": i}, data=device
                    ),
                ],
                className="mb-2",
            )
        )

    modal_body = html.Div(
        [
            dbc.Alert(
                "Manually assign floor numbers and security levels to devices",
                color="info",
            ),
            dbc.Row(
                [
                    dbc.Col(html.Strong("Device Name"), width=4),
                    dbc.Col(html.Strong("Floor"), width=2),
                    dbc.Col(html.Strong("Access"), width=3),
                    dbc.Col(html.Strong("Security (0-10)"), width=2),
                ],
                className="mb-2",
            ),
            html.Hr(),
            html.Div(device_rows),
            html.Hr(),
            dbc.Alert(
                [
                    html.Strong("Security Levels: "),
                    "0-2: Public areas, 3-5: Office areas, 6-8: Restricted, 9-10: High security",
                ],
                color="light",
                className="small",
            ),
        ]
    )

    return dbc.Modal(
        [
            dbc.ModalHeader("Device Mapping"),
            dbc.ModalBody(modal_body),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id="device-modal-cancel", color="secondary"
                    ),
                    dbc.Button(
                        "Save", id="device-modal-save", color="primary"
                    ),
                ]
            ),
        ],
        id="simple-device-modal",
        size="lg",
        is_open=False,
    )


@callback(
    Output("simple-device-modal", "is_open"),
    [
        Input("open-device-mapping", "n_clicks"),
        Input("device-modal-cancel", "n_clicks"),
        Input("device-modal-save", "n_clicks"),
    ],
    [State("simple-device-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_simple_device_modal(open_clicks, cancel_clicks, save_clicks, is_open):
    """Control the simple device modal open/close state"""
    ctx = dash.callback_context

    if not ctx.triggered:
        return is_open

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"🎯 Modal button triggered: {button_id}")

    if button_id == "open-device-mapping" and open_clicks:
        print("📂 Opening device mapping modal")
        return True
    elif button_id in ["device-modal-cancel", "device-modal-save"]:
        print("🚪 Closing device mapping modal")
        return False

    return is_open


@callback(
    Output("upload-results", "children", allow_duplicate=True),
    Input("device-modal-save", "n_clicks"),
    [
        State({"type": "device-name", "index": ALL}, "data"),
        State({"type": "device-floor", "index": ALL}, "value"),
        State({"type": "device-access", "index": ALL}, "value"),
        State({"type": "device-security", "index": ALL}, "value"),
    ],
    prevent_initial_call=True,
)
def save_device_mappings(n_clicks, device_names, floors, access_lists, security_levels):
    """Save device mappings when Save button is clicked"""
    if not n_clicks:
        return dash.no_update

    device_mappings = {}
    for i, device in enumerate(device_names or []):
        if device:
            device_mappings[device] = {
                "floor": floors[i] if i < len(floors or []) else None,
                "access": access_lists[i] if i < len(access_lists or []) else [],
                "security_level": security_levels[i] if i < len(security_levels or []) else 1,
            }

    print(f"✅ Device mappings saved: {device_mappings}")

    success_message = dbc.Alert(
        [
            html.H6("Device Mapping Complete!", className="alert-heading"),
            html.P(f"Successfully mapped {len(device_mappings)} devices with floor and security information."),
            html.Hr(),
            html.P("Ready to proceed with analytics!", className="mb-0"),
        ],
        color="success",
    )

    return success_message


@callback(
    Output("upload-results", "children", allow_duplicate=True),
    Input("device-modal-cancel", "n_clicks"),
    prevent_initial_call=True,
)
def cancel_device_mappings(n_clicks):
    """Handle cancel button"""
    if n_clicks:
        print("❌ Device mapping cancelled")
        return dbc.Alert(
            "Device mapping cancelled.",
            color="warning",
            dismissable=True
        )
    return dash.no_update
