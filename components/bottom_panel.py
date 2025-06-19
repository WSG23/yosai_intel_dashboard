# yosai_intel_dashboard/components/bottom_panel.py

from dash import html, dcc

# Safe text function that works with or without babel
def safe_text(text):
    """Return text safely, handling any babel objects"""
    return str(text)


def get_layout():
    """Return the bottom panel layout without babel dependencies"""

    layout = html.Div(
        [
            html.Div(
                [
                    html.H4(safe_text("Incident Detection Breakdown")),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(safe_text(label), className="chip gold")
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
                                    html.Div(safe_text(label), className="chip")
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
                                    html.Div(safe_text(label), className="chip gold")
                                    for label in [
                                        "Interaction Effects",
                                        "Token History",
                                        "Cross-Location",
                                        "Cross-Organization",
                                    ]
                                ],
                                className="chip-row",
                            ),
                            html.Div(safe_text("Technology Core Engine Analysis"), className="tech-note"),
                        ],
                        className="chips-container",
                    ),
                ],
                className="incident-breakdown",
            ),
        ],
        className="bottom-panel",
    )
    
    return layout

# For backwards compatibility, expose the layout directly
layout = get_layout()
