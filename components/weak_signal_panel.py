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
def signal_category_block(title, signals, category_id):
    """Return an accordion item block for a signal category"""
    return dbc.AccordionItem(
        html.Div(signals, className="signal-list"),
        title=f"{title} ({len(signals)})",
        item_id=category_id,
    )


def layout():
    layout_div = html.Div(
        [
            html.H4(_l("Weak-Signal Live Feed"), className="incident-panel-header"),
            dbc.Accordion(
                children=[
                    signal_category_block(
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
                    signal_category_block(
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
                start_collapsed=True,
                always_open=False,
                id="weak-signal-accordion",
            ),
        ],
        className="incident-alert-panel",
    )

    # JSON SANITIZATION - Convert LazyString objects to regular strings
    return sanitize_lazystring_recursive(layout_div)
