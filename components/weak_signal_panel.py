# yosai_intel_dashboard/components/weak_signal_panel.py

from dash import html
import dash_bootstrap_components as dbc
from utils.lazystring_handler import sanitize_lazystring_recursive

# Safe text function that works with or without babel
def safe_text(text):
    """Return text safely, handling any babel objects"""
    return str(text)

# Example signal card
def signal_card(prefix, code, severity, location, description, timestamp):
    severity_class = f"signal-{severity.lower()}"
    return dbc.Card(
        [
            dbc.CardHeader(
                safe_text(f"[{prefix}-{code}] - {severity}"),
                className=f"signal-card-header {severity_class}",
            ),
            dbc.CardBody(
                [
                    html.P(safe_text(f"Location: {location}")),
                    html.P(safe_text(f"Description: {description}")),
                    html.P(safe_text(f"Timestamp: {timestamp}")),
                ]
            ),
        ],
        className="signal-card",
    )

# Expandable category block
def category_block(title, signals, category_id):
    return html.Details(
        [
            html.Summary(
                safe_text(f"{title} ({len(signals)})"),
                className="signal-summary",
            ),
            html.Div(signals, className="signal-category-content"),
        ],
        id=category_id,
        className="signal-category",
    )

layout = html.Div(
    [
        html.H4(safe_text("Weak-Signal Live Feed"), className="panel-header"),
        category_block(
            safe_text("News Scraping"),
            [
                signal_card(
                    "N",
                    "0001",
                    "High",
                    "Yokohama",
                    "Foreign actor probing energy facilities",
                    "25 June 2025",
                )
            ],
            "weak-signal-news",
        ),
        category_block(
            safe_text("Cross-Location"),
            [
                signal_card(
                    "CO",
                    "0001",
                    "Medium",
                    "Tokyo HQ",
                    "Unusual access pattern detected",
                    "25 June 2025",
                )
            ],
            "weak-signal-cross-location",
        ),
    ],
    className="weak-signal-panel",
)

# Convert any LazyString objects to regular strings for safe serialization  
layout = sanitize_lazystring_recursive(layout)
