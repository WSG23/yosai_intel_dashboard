from dash import html
from flask_babel import lazy_gettext as _l
from utils.lazystring_handler import sanitize_lazystring_recursive

def get_layout():
    """Return the complete bottom panel layout with both sections"""

    layout = html.Div(
        [
            # Left Section: Incident Detection Breakdown
            html.Div(
                [
                    html.H4(_l("Incident Detection Breakdown")),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(_l("Access Outcome"), className="chip gold"),
                                    html.Div(_l("Unusual Door"), className="chip gold"),
                                    html.Div(_l("Potential Tailgating"), className="chip gold"),
                                    html.Div(_l("Unusual Group"), className="chip gold"),
                                ],
                                className="chip-grid",
                            ),
                            html.Div(
                                [
                                    html.Div(_l("Unusual Path"), className="chip"),
                                    html.Div(_l("Unusual Time"), className="chip"),
                                    html.Div(_l("Multiple Attempts"), className="chip"),
                                    html.Div(_l("Location Criticality"), className="chip"),
                                ],
                                className="chip-grid",
                            ),
                            html.Div(
                                [
                                    html.Div(_l("Interaction Effects"), className="chip gold"),
                                    html.Div(_l("Token History"), className="chip gold"),
                                    html.Div(_l("Cross-Location"), className="chip gold"),
                                    html.Div(_l("Cross-Organization"), className="chip gold"),
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
                    html.H4(_l("Respond")),
                    
                    # Active Ticket Section
                    html.Div(
                        [
                            html.Div(_l("Action III"), className="respond-label"),
                            html.Div(
                                _l("Ticket I Action I"),
                                className="ticket-box"
                            ),
                            html.Button(
                                _l("Mark As Completed"),
                                className="complete-button",
                                id="complete-ticket-btn"
                            ),
                        ]
                    ),
                    
                    # Action Checklist
                    html.Div(
                        [
                            html.Div(_l("Action I"), className="action-checklist"),
                            html.Div(_l("Action II"), className="action-checklist"),
                            html.Div(_l("Action IV"), className="action-checklist"),
                        ]
                    ),
                    
                    # Resolve Buttons
                    html.Div(
                        [
                            html.Button(_l("Resolve As Harmful"), className="resolve-button", id="resolve-harmful"),
                            html.Button(_l("Resolve As Malfunction"), className="resolve-button", id="resolve-malfunction"),
                            html.Button(_l("Resolve As Normal"), className="resolve-button", id="resolve-normal"),
                            html.Button(_l("Dismiss"), className="resolve-button", id="dismiss-ticket"),
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

# Create layout and ensure JSON serialization
layout = sanitize_lazystring_recursive(get_layout())
