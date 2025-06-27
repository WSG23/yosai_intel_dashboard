"""Callbacks used by the deep analytics page."""

from __future__ import annotations

from dash import callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash import html

from .deep_analytics import (
    get_initial_message_safe,
    process_suggests_analysis_safe,
    process_quality_analysis_safe,
    analyze_data_with_service_safe,
    create_analysis_results_display_safe,
)


@callback(
    Output("analytics-display-area", "children"),
    [
        Input("security-btn", "n_clicks"),
        Input("trends-btn", "n_clicks"),
        Input("behavior-btn", "n_clicks"),
        Input("anomaly-btn", "n_clicks"),
        Input("suggests-btn", "n_clicks"),
        Input("quality-btn", "n_clicks"),
        Input("unique-patterns-btn", "n_clicks"),
    ],
    [State("analytics-data-source", "value")],
    prevent_initial_call=True,
)
def handle_analysis_buttons(security_n, trends_n, behavior_n, anomaly_n, suggests_n, quality_n, unique_n, data_source):
    """Handle analysis button clicks."""
    if not callback_context.triggered:
        return get_initial_message_safe()

    if not data_source or data_source == "none":
        return dbc.Alert("Please select a data source first", color="warning")

    button_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    analysis_map = {
        "security-btn": "security",
        "trends-btn": "trends",
        "behavior-btn": "behavior",
        "anomaly-btn": "anomaly",
        "suggests-btn": "suggests",
        "quality-btn": "quality",
        "unique-patterns-btn": "unique_patterns",
    }
    analysis_type = analysis_map.get(button_id)
    if not analysis_type:
        return dbc.Alert("Unknown analysis type", color="danger")

    if analysis_type == "suggests":
        results = process_suggests_analysis_safe(data_source)
    elif analysis_type == "quality":
        results = process_quality_analysis_safe(data_source)
    else:
        results = analyze_data_with_service_safe(data_source, analysis_type)

    if isinstance(results, dict) and "error" in results:
        return dbc.Alert(str(results["error"]), color="danger")

    return create_analysis_results_display_safe(results, analysis_type)

__all__ = ["handle_analysis_buttons"]
