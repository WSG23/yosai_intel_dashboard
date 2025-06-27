"""Reusable UI components for the deep analytics page."""

from __future__ import annotations

from typing import Dict, Any

import dash_bootstrap_components as dbc
from dash import html


def get_analysis_buttons_section() -> dbc.Col:
    """Return the analysis buttons layout used on the analytics page."""
    return dbc.Col(
        [
            html.Label("Analysis Type", className="fw-bold mb-3"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "🔒 Security Analysis",
                            id="security-btn",
                            color="danger",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "📈 Trends Analysis",
                            id="trends-btn",
                            color="info",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "👤 Behavior Analysis",
                            id="behavior-btn",
                            color="warning",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "🚨 Anomaly Detection",
                            id="anomaly-btn",
                            color="dark",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "🤖 AI Suggestions",
                            id="suggests-btn",
                            color="success",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "💰 Data Quality",
                            id="quality-btn",
                            color="secondary",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Unique Patterns",
                            id="unique-patterns-btn",
                            color="primary",
                            outline=True,
                            size="sm",
                            className="w-100 mb-2",
                        ),
                        width=6,
                    ),
                ]
            ),
        ],
        width=6,
    )


def create_analysis_results_display(results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Render analysis results in a card component."""
    total_events = results.get("total_events", 0)
    unique_users = results.get("unique_users", 0)
    unique_doors = results.get("unique_doors", 0)
    success_rate = results.get("success_rate", 0)
    analysis_focus = results.get("analysis_focus", "")

    if analysis_type == "security":
        specific_content = [
            html.P(f"Security Score: {results.get('security_score', 0):.1f}/100"),
            html.P(f"Failed Attempts: {results.get('failed_attempts', 0):,}"),
            html.P(f"Risk Level: {results.get('risk_level', 'Unknown')}")
        ]
        color = "danger" if results.get("risk_level") == "High" else "warning" if results.get("risk_level") == "Medium" else "success"
    elif analysis_type == "trends":
        specific_content = [
            html.P(f"Daily Average: {results.get('daily_average', 0):.0f} events"),
            html.P(f"Peak Usage: {results.get('peak_usage', 'Unknown')}") ,
            html.P(f"Trend: {results.get('trend_direction', 'Unknown')}")
        ]
        color = "info"
    elif analysis_type == "behavior":
        specific_content = [
            html.P(f"Avg Accesses/User: {results.get('avg_accesses_per_user', 0):.1f}"),
            html.P(f"Heavy Users: {results.get('heavy_users', 0)}"),
            html.P(f"Behavior Score: {results.get('behavior_score', 'Unknown')}")
        ]
        color = "success"
    elif analysis_type == "anomaly":
        specific_content = [
            html.P(f"Anomalies Detected: {results.get('anomalies_detected', 0):,}"),
            html.P(f"Threat Level: {results.get('threat_level', 'Unknown')}") ,
            html.P(f"Status: {results.get('suspicious_activities', 'Unknown')}")
        ]
        color = "danger" if results.get("threat_level") == "Critical" else "warning"
    else:
        specific_content = [html.P("Standard analysis completed")]
        color = "info"

    return dbc.Card(
        [
            dbc.CardHeader([html.H5(f"📊 {results.get('analysis_type', analysis_type)} Results")]),
            dbc.CardBody(
                [
                    dbc.Row([
                        dbc.Col([
                            html.H6("📈 Summary"),
                            html.P(f"Total Events: {total_events:,}"),
                            html.P(f"Unique Users: {unique_users:,}"),
                            html.P(f"Unique Doors: {unique_doors:,}"),
                            dbc.Progress(value=success_rate * 100,
                                         label=f"Success Rate: {success_rate:.1%}",
                                         color="success" if success_rate > 0.8 else "warning"),
                        ], width=6),
                        dbc.Col([
                            html.H6(f"🎯 {analysis_type.title()} Specific"),
                            html.Div(specific_content),
                        ], width=6),
                    ]),
                    html.Hr(),
                    dbc.Alert([html.H6("Analysis Focus"), html.P(analysis_focus)], color=color),
                ]
            ),
        ]
    )

__all__ = ["get_analysis_buttons_section", "create_analysis_results_display"]
