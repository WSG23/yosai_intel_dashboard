# components/analytics/analytics_charts.py - Chart generation component
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Dict, Any, List, Optional, Tuple

def create_analytics_charts(analytics_data: Dict[str, Any]) -> html.Div:
    """Create analytics visualization charts"""
    
    if not analytics_data:
        return html.Div([
            dbc.Alert("No data available for visualization", color="info", className="text-center")
        ])
    
    charts = []
    
    # Access Patterns Chart
    if 'access_patterns' in analytics_data and analytics_data['access_patterns']:
        access_chart = _create_access_patterns_chart(analytics_data['access_patterns'])
        if access_chart:
            charts.append(access_chart)
    
    # Hourly Patterns Chart
    if 'hourly_patterns' in analytics_data and analytics_data['hourly_patterns']:
        hourly_chart = _create_hourly_patterns_chart(analytics_data['hourly_patterns'])
        if hourly_chart:
            charts.append(hourly_chart)
    
    # Top Users Chart
    if 'top_users' in analytics_data and analytics_data['top_users']:
        users_chart = _create_top_users_chart(analytics_data['top_users'])
        if users_chart:
            charts.append(users_chart)
    
    # Top Doors Chart
    if 'top_doors' in analytics_data and analytics_data['top_doors']:
        doors_chart = _create_top_doors_chart(analytics_data['top_doors'])
        if doors_chart:
            charts.append(doors_chart)
    
    if not charts:
        return html.Div([
            dbc.Alert("No charts available - insufficient data", color="warning", className="text-center")
        ])
    
    # Arrange charts in rows of 2
    rows = []
    for i in range(0, len(charts), 2):
        if i + 1 < len(charts):
            rows.append(dbc.Row([charts[i], charts[i + 1]], className="mb-4"))
        else:
            rows.append(dbc.Row([charts[i]], className="mb-4"))
    
    return html.Div(rows)

def create_summary_cards(analytics_data: Dict[str, Any]) -> html.Div:
    """Create summary statistic cards"""
    
    if not analytics_data:
        return html.Div()
    
    cards = []
    
    # Total Events Card
    if 'total_events' in analytics_data:
        cards.append(_create_metric_card(
            title="Total Events",
            value=f"{analytics_data['total_events']:,}",
            color="primary"
        ))
    
    # Date Range Card
    if 'date_range' in analytics_data and analytics_data['date_range'] and analytics_data['date_range'].get('start'):
        start_date = analytics_data['date_range']['start']
        end_date = analytics_data['date_range']['end']
        cards.append(_create_metric_card(
            title="Date Range",
            value=f"{start_date} to {end_date}",
            color="info",
            small_text=True
        ))
    
    # Active Users Count
    if 'top_users' in analytics_data:
        user_count = len(analytics_data['top_users'])
        cards.append(_create_metric_card(
            title="Active Users",
            value=str(user_count),
            color="success"
        ))
    
    # Active Doors Count
    if 'top_doors' in analytics_data:
        door_count = len(analytics_data['top_doors'])
        cards.append(_create_metric_card(
            title="Active Doors",
            value=str(door_count),
            color="warning"
        ))
    
    if cards:
        return html.Div([dbc.Row(cards, className="mb-4")])
    else:
        return html.Div()

def _create_access_patterns_chart(access_patterns: Dict[str, int]) -> Optional[dbc.Col]:
    """Create access patterns pie chart"""
    try:
        fig = px.pie(
            values=list(access_patterns.values()),
            names=list(access_patterns.keys()),
            title="Access Result Distribution"
        )
        fig.update_layout(height=400, showlegend=True)
        
        return dbc.Col([
            dbc.Card([
                dbc.CardHeader("Access Patterns"),
                dbc.CardBody([
                    dcc.Graph(figure=fig, id="access-patterns-chart")
                ])
            ])
        ], width=6)
    except Exception as e:
        print(f"Error creating access patterns chart: {e}")
        return None

def _create_hourly_patterns_chart(hourly_patterns: Dict[str, int]) -> Optional[dbc.Col]:
    """Create hourly patterns bar chart"""
    try:
        hours = list(hourly_patterns.keys())
        counts = list(hourly_patterns.values())
        
        fig = px.bar(
            x=hours,
            y=counts,
            title="Access Events by Hour of Day",
            labels={'x': 'Hour of Day', 'y': 'Number of Events'}
        )
        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Number of Events",
            height=400,
            xaxis=dict(tickmode='linear')
        )
        
        return dbc.Col([
            dbc.Card([
                dbc.CardHeader("Hourly Activity Patterns"),
                dbc.CardBody([
                    dcc.Graph(figure=fig, id="hourly-patterns-chart")
                ])
            ])
        ], width=6)
    except Exception as e:
        print(f"Error creating hourly patterns chart: {e}")
        return None

def _create_top_users_chart(top_users: Dict[str, int]) -> Optional[dbc.Col]:
    """Create top users horizontal bar chart"""
    try:
        users = list(top_users.keys())
        counts = list(top_users.values())
        
        fig = px.bar(
            x=counts,
            y=users,
            orientation='h',
            title="Top 10 Most Active Users",
            labels={'x': 'Number of Access Events', 'y': 'User ID'}
        )
        fig.update_layout(
            xaxis_title="Number of Access Events",
            yaxis_title="User ID",
            height=400
        )
        
        return dbc.Col([
            dbc.Card([
                dbc.CardHeader("Most Active Users"),
                dbc.CardBody([
                    dcc.Graph(figure=fig, id="top-users-chart")
                ])
            ])
        ], width=6)
    except Exception as e:
        print(f"Error creating top users chart: {e}")
        return None

def _create_top_doors_chart(top_doors: Dict[str, int]) -> Optional[dbc.Col]:
    """Create top doors horizontal bar chart"""
    try:
        doors = list(top_doors.keys())
        counts = list(top_doors.values())
        
        fig = px.bar(
            x=counts,
            y=doors,
            orientation='h',
            title="Top 10 Most Used Doors",
            labels={'x': 'Number of Access Events', 'y': 'Door ID'}
        )
        fig.update_layout(
            xaxis_title="Number of Access Events",
            yaxis_title="Door ID",
            height=400
        )
        
        return dbc.Col([
            dbc.Card([
                dbc.CardHeader("Most Active Doors"),
                dbc.CardBody([
                    dcc.Graph(figure=fig, id="top-doors-chart")
                ])
            ])
        ], width=6)
    except Exception as e:
        print(f"Error creating top doors chart: {e}")
        return None

def _create_metric_card(
    title: str, value: str, color: str, small_text: bool = False
) -> dbc.Col:
    """Create a metric display card"""
    value_class = "h6" if small_text else "h4"
    heading = html.H6 if small_text else html.H4

    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                heading(value, className=f"card-title text-{color} {value_class}"),
                html.P(title, className="card-text text-muted"),
            ])
        ], color=color, outline=True),
    ], width=3)

__all__ = [
    "create_analytics_charts",
    "create_summary_cards"
]
