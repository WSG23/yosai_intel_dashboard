# yosai_intel_dashboard/components/bottom_panel.py

from dash import html, dcc
from flask_babel import lazy_gettext as _l
from utils.lazystring_handler import sanitize_lazystring_recursive

layout = html.Div(
    [
        html.Div(
            [
                html.H4(_l("Incident Detection Breakdown")),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(_l(label), className="chip gold")
                                for label in [
                                    "Access Outcome",
                                    "Unusual Door",
                                    "Potential Tailgating",
                                    "Unusual Group",
                                ]
                            ],
                            className="chip-row",
                        ),
                        html.Div(
                            [
                                html.Div(_l(label), className="chip")
                                for label in [
                                    "Unusual Path",
                                    "Unusual Time",
                                    "Multiple Attempts",
                                    "Location Criticality",
                                ]
                            ],
                            className="chip-row",
                        ),
                        html.Div(
                            [
                                html.Div(_l(label), className="chip gold")
                                for label in [
                                    "Interaction Effects",
                                    "Token History",
                                    "Cross-Location",
                                    "Cross-Organization",
                                ]
                            ],
                            className="chip-row",
                        ),
                        html.Div(_l("Tech. Malfunction"), className="chip gray"),
                    ]
                ),
            ],
            className="bottom-column",
        ),
        html.Div(
            [
                html.H4(_l("Respond")),
                html.Div(_l("Action III"), className="respond-label"),
                html.Div(_l("Ticket I Action I"), className="ticket-box"),
                html.Button(_l("Mark As Completed"), className="complete-button"),
            ],
            className="bottom-column respond",
        ),
        html.Div(
            [
                html.H4(_l("Resolve")),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Checklist(
                                    [
                                        {"label": _l("Action I"), "value": "A1"},
                                        {"label": _l("Action II"), "value": "A2"},
                                        {"label": _l("Action III"), "value": "A3"},
                                        {"label": _l("Action IV"), "value": "A4"},
                                    ],
                                    id="action-checklist",
                                    className="action-checklist",
                                )
                            ]
                        ),
                        html.Button(
                            _l("Resolve As Harmful"), className="resolve-button"
                        ),
                        html.Button(
                            _l("Resolve As Malfunction"), className="resolve-button"
                        ),
                        html.Button(
                            _l("Resolve As Normal"), className="resolve-button"
                        ),
                        html.Button(_l("Dismiss"), className="resolve-button"),
                    ]
                ),
            ],
            className="bottom-column",
        ),
    ],
    className="bottom-panel",
)

# Sanitize to avoid LazyString serialization issues
layout = sanitize_lazystring_recursive(layout)
