# yosai_intel_dashboard/components/bottom_panel.py

from dash import html
from flask_babel import lazy_gettext as _l


def safe_text(text):
    """Return text safely, handling any babel objects"""
    try:
        return str(text)
    except Exception:
        return text


def get_layout():
    """Return the complete bottom panel layout with Incident Detection + Respond sections"""

    layout = html.Div(
        [
            # Left Section: Incident Detection Breakdown
            html.Div(
                [
                    html.H4(safe_text(_l("Incident Detection Breakdown"))),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(safe_text(_l("Access Outcome")), className="chip gold"),
                                    html.Div(safe_text(_l("Unusual Door")), className="chip gold"),
                                    html.Div(safe_text(_l("Potential Tailgating")), className="chip gold"),
                                    html.Div(safe_text(_l("Unusual Group")), className="chip gold"),
                                ],
                                className="chip-grid",
                            ),
                            html.Div(
                                [
                                    html.Div(safe_text(_l("Unusual Path")), className="chip"),
                                    html.Div(safe_text(_l("Unusual Time")), className="chip"),
                                    html.Div(safe_text(_l("Multiple Attempts")), className="chip"),
                                    html.Div(safe_text(_l("Location Criticality")), className="chip"),
                                ],
                                className="chip-grid",
                            ),
                            html.Div(
                                [
                                    html.Div(safe_text(_l("Interaction Effects")), className="chip gold"),
                                    html.Div(safe_text(_l("Token History")), className="chip gold"),
                                    html.Div(safe_text(_l("Cross-Location")), className="chip gold"),
                                    html.Div(safe_text(_l("Cross-Organization")), className="chip gold"),
                                ],
                                className="chip-grid",
                            ),
                        ],
                        className="chips-container",
                    ),
                ],
                className="bottom-column",
            ),

            # Right Section: Respond Panel
            html.Div(
                [
                    html.H4(safe_text(_l("Respond"))),

                    # Active Ticket
                    html.Div(
                        [
                            html.Div(safe_text(_l("Action III")), className="respond-label"),
                            html.Div(
                                safe_text(_l("Ticket I Action I")),
                                className="ticket-box"
                            ),
                            html.Button(
                                safe_text(_l("Mark As Completed")),
                                className="complete-button"
                            ),
                        ]
                    ),

                    # Action Checklist
                    html.Div(
                        [
                            html.Div(safe_text(_l("Action I")), className="action-checklist"),
                            html.Div(safe_text(_l("Action II")), className="action-checklist"),
                            html.Div(safe_text(_l("Action IV")), className="action-checklist"),
                        ]
                    ),

                    # Resolve Buttons
                    html.Div(
                        [
                            html.Button(safe_text(_l("Resolve As Harmful")), className="resolve-button"),
                            html.Button(safe_text(_l("Resolve As Malfunction")), className="resolve-button"),
                            html.Button(safe_text(_l("Resolve As Normal")), className="resolve-button"),
                            html.Button(safe_text(_l("Dismiss")), className="resolve-button"),
                        ],
                        className="resolve-buttons"
                    ),
                ],
                className="bottom-column respond",
            ),
        ],
        className="bottom-panel",
    )

    return layout


# For backwards compatibility, expose the layout directly
layout = get_layout()

