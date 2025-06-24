"""Simplified application factory for the Yōsai Intel Dashboard."""

import logging
from typing import Dict, Any
from datetime import datetime

import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

from core.container import get_service
from core.exceptions import YosaiBaseException

logger = logging.getLogger(__name__)


class DashboardApp:
    """Main dashboard application."""

    def __init__(self) -> None:
        self.config = get_service("config")
        self.analytics_service = get_service("analytics_service")
        self.app = self._create_app()
        self._setup_callbacks()

    def _create_app(self) -> dash.Dash:
        app = dash.Dash(
            __name__,
            title="Yōsai Intel Dashboard",
            suppress_callback_exceptions=True,
            external_stylesheets=[
                "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
            ],
        )
        app.layout = self._create_layout()
        return app

    def _create_layout(self) -> html.Div:
        return html.Div(
            [
                html.Nav(
                    [
                        html.Div(
                            [
                                html.H1("🏯 Yōsai Intel Dashboard", className="navbar-brand mb-0"),
                                html.Div(
                                    [
                                        html.Button(
                                            "Refresh",
                                            id="refresh-btn",
                                            className="btn btn-outline-light btn-sm",
                                        ),
                                        html.Span(id="last-updated", className="text-light ms-3"),
                                    ],
                                    className="d-flex align-items-center",
                                ),
                            ],
                            className="container-fluid d-flex justify-content-between align-items-center",
                        )
                    ],
                    className="navbar navbar-dark bg-primary mb-4",
                ),
                html.Div(
                    [
                        html.Div(id="status-cards", className="row mb-4"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4("Hourly Activity Pattern"),
                                        dcc.Graph(id="hourly-chart"),
                                    ],
                                    className="col-md-6",
                                ),
                                html.Div(
                                    [
                                        html.H4("Location Analysis"),
                                        dcc.Graph(id="location-chart"),
                                    ],
                                    className="col-md-6",
                                ),
                            ],
                            className="row mb-4",
                        ),
                        html.Div(
                            [html.H4("Recent Activity"), html.Div(id="recent-events")],
                            className="row",
                        ),
                    ],
                    className="container",
                ),
                dcc.Interval(id="interval-component", interval=30 * 1000, n_intervals=0),
            ]
        )

    def _setup_callbacks(self) -> None:
        @self.app.callback(
            [
                Output("status-cards", "children"),
                Output("hourly-chart", "figure"),
                Output("location-chart", "figure"),
                Output("recent-events", "children"),
                Output("last-updated", "children"),
            ],
            [Input("interval-component", "n_intervals"), Input("refresh-btn", "n_clicks")],
        )
        def update_dashboard(n_intervals, refresh_clicks):
            try:
                data = self.analytics_service.get_dashboard_data()
                status_cards = self._create_status_cards(data["summary"])
                hourly_chart = self._create_hourly_chart(data["hourly_patterns"])
                location_chart = self._create_location_chart(data["location_stats"])
                recent_events = self._create_recent_events_table(data["summary"])
                last_updated = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
                return status_cards, hourly_chart, location_chart, recent_events, last_updated
            except Exception as e:  # pragma: no cover - runtime errors
                logger.error(f"Dashboard update failed: {e}")
                error = html.Div([html.Div("⚠️ Error loading dashboard data", className="alert alert-warning")])
                empty = go.Figure()
                return error, empty, empty, error, "Error occurred"

    def _create_status_cards(self, summary: Dict[str, Any]) -> html.Div:
        total_events = summary.get("total_events", 0)
        success_rate = summary.get("success_rate", 0)
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Total Events", className="card-title"),
                                html.H2(f"{total_events:,}", className="card-text text-primary"),
                            ],
                            className="card-body",
                        )
                    ],
                    className="card col-md-3",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Success Rate", className="card-title"),
                                html.H2(f"{success_rate}%", className="card-text text-success"),
                            ],
                            className="card-body",
                        )
                    ],
                    className="card col-md-3",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("System Status", className="card-title"),
                                html.H2("🟢 Online", className="card-text text-success"),
                            ],
                            className="card-body",
                        )
                    ],
                    className="card col-md-3",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Period", className="card-title"),
                                html.H2(f"{summary.get('period_days', 0)} days", className="card-text text-info"),
                            ],
                            className="card-body",
                        )
                    ],
                    className="card col-md-3",
                ),
            ],
            className="row",
        )

    def _create_hourly_chart(self, hourly_data: Dict[str, Any]) -> go.Figure:
        data = hourly_data.get("hourly_data", [])
        if not data:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        hours = [int(item["hour"]) for item in data]
        counts = [item["event_count"] for item in data]
        fig = px.bar(x=hours, y=counts, title="Events by Hour", labels={"x": "Hour", "y": "Event Count"})
        fig.update_layout(xaxis=dict(tickmode="linear", tick0=0, dtick=2), height=400)
        return fig

    def _create_location_chart(self, location_data: Dict[str, Any]) -> go.Figure:
        locations = location_data.get("locations", [])
        if not locations:
            fig = go.Figure()
            fig.add_annotation(text="No location data available", x=0.5, y=0.5, showarrow=False)
            return fig
        location_names = [loc["location"] for loc in locations]
        event_counts = [loc["total_events"] for loc in locations]
        fig = px.pie(values=event_counts, names=location_names, title="Events by Location")
        fig.update_layout(height=400)
        return fig

    def _create_recent_events_table(self, summary: Dict[str, Any]) -> html.Div:
        breakdown = summary.get("event_breakdown", [])
        if not breakdown:
            return html.Div("No recent events", className="text-muted")
        rows = []
        for event in breakdown[:10]:
            rows.append(
                html.Tr([
                    html.Td(event.get("event_type", "Unknown")),
                    html.Td(event.get("status", "Unknown")),
                    html.Td(f"{event.get('count', 0):,}"),
                ])
            )
        return html.Table(
            [
                html.Thead([html.Tr([html.Th("Event Type"), html.Th("Status"), html.Th("Count")])]),
                html.Tbody(rows),
            ],
            className="table table-striped",
        )

    def run(self) -> None:
        logger.info(
            "Starting Yōsai Intel Dashboard on %s:%s",
            self.config.host,
            self.config.port,
        )
        self.app.run_server(host=self.config.host, port=self.config.port, debug=self.config.debug)


def create_app() -> DashboardApp:
    """Application factory function."""
    try:
        return DashboardApp()
    except YosaiBaseException as e:  # pragma: no cover - rare errors
        logger.error(f"Application creation failed: {e.message}")
        raise
    except Exception as e:  # pragma: no cover - unexpected errors
        logger.error(f"Unexpected error during app creation: {e}")
        raise


def create_application() -> dash.Dash:
    """Compatibility wrapper returning Dash instance."""
    return create_app().app


def create_application_for_testing() -> dash.Dash:
    """Create application with extra test routes."""
    app_wrapper = create_app()
    server = app_wrapper.app.server

    @server.route("/api/ping")
    def ping():
        from flask import jsonify

        return jsonify(msg="pong")

    @server.route("/i18n/<lang>")
    def set_lang(lang: str):
        from flask import session, redirect, request

        session["lang"] = lang
        return redirect(request.referrer or "/")

    return app_wrapper.app


__all__ = ["create_app", "create_application", "create_application_for_testing", "DashboardApp"]
