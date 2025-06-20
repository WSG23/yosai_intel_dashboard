from dash import html
import dash_bootstrap_components as dbc
from flask_babel import lazy_gettext as _l
from utils.lazystring_handler import sanitize_lazystring_recursive

# Example signal card
def signal_card(prefix, code, severity, location, description, timestamp):
    severity_class = f"signal-{severity.lower()}"
    return dbc.Card(
        [
            dbc.CardHeader(
                f"[{prefix}-{code}] - {severity}",
                className=f"signal-card-header {severity_class}",
            ),
            dbc.CardBody(
                [
                    html.P(f"Location: {location}"),
                    html.P(f"Description: {description}"),
                    html.P(f"Timestamp: {timestamp}"),
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
                f"{title} ({len(signals)})",
                className="signal-summary",
            ),
            html.Div(signals, className="signal-category-content"),
        ],
        id=category_id,
        className="signal-category",
    )

layout = html.Div(
    [
        html.H4(_l("Weak-Signal Live Feed"), className="panel-header"),
        category_block(
            _l("News Scraping"),
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
            _l("Cross-Location"),
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

# JSON SANITIZATION - Convert LazyString objects to regular strings  
layout = sanitize_lazystring_recursive(layout)
