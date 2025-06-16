# app.py - Complete app with updated navbar and new CSS system
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# Import updated navbar component
from components import navbar

# Initialize the Dash app with new CSS system
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "/assets/css/main.css"  # New modular CSS system
    ],
    suppress_callback_exceptions=True,
    # Add meta tags for better mobile experience
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "theme-color", "content": "#1B2A47"}
    ]
)

server = app.server

# Dashboard layout with updated navbar and new CSS classes
app.layout = html.Div([
    # Updated Navbar Component
    navbar.layout,
    
    # Main content grid with new CSS classes
    html.Div([
        # Left Panel - Incident Alerts
        html.Div([
            html.Div([
                html.H4("Incident Alerts", className="panel__title text-primary"),
            ], className="panel__header"),
            html.Div([
                # Sample ticket card with new CSS classes
                html.Div([
                    html.Div("Event ID: C333333", className="ticket-card__header text-secondary"),
                    html.Div([
                        # Threat indicator with new classes
                        html.Div([
                            html.Div("Threat Level:", className="threat-indicator__label text-tertiary"),
                            html.Div([
                                html.Div(
                                    className="threat-indicator__fill", 
                                    style={"width": "72%"}
                                )
                            ], className="threat-indicator__progress")
                        ], className="threat-indicator"),
                        
                        # Ticket details with new text classes
                        html.P("Location: Himeji Castle", className="text-primary"),
                        html.P("Timestamp: 25 June 2025", className="text-secondary"),
                        html.P("Area: Server Room Door", className="text-secondary"),
                        html.P("Device: Server Room II", className="text-secondary"),
                        html.P("Access Group: IT Services", className="text-secondary"),
                        html.P("Access Result: Access", className="text-success"),
                    ], className="ticket-card__body")
                ], className="ticket-card"),
                
                # Second ticket example
                html.Div([
                    html.Div("Event ID: D444444", className="ticket-card__header text-secondary"),
                    html.Div([
                        html.Div([
                            html.Div("Threat Level:", className="threat-indicator__label text-tertiary"),
                            html.Div([
                                html.Div(
                                    className="threat-indicator__fill", 
                                    style={"width": "35%"}
                                )
                            ], className="threat-indicator__progress")
                        ], className="threat-indicator"),
                        html.P("Location: Osaka HQ", className="text-primary"),
                        html.P("Timestamp: 25 June 2025", className="text-secondary"),
                        html.P("Area: Main Entrance", className="text-secondary"),
                        html.P("Access Result: Access Denied", className="text-critical"),
                    ], className="ticket-card__body")
                ], className="ticket-card"),
            ], className="panel__body")
        ], className="panel dashboard__left-panel"),
        
        # Map Panel (enhanced placeholder with new classes)
        html.Div([
            html.Div([
                html.H4("Facility Map", className="text-center text-primary"),
                html.Div([
                    html.Div("🗺️", style={"fontSize": "4rem", "marginBottom": "1rem"}),
                    html.P("Interactive Map Component", className="text-secondary"),
                    html.P("Tokyo HQ - Real-time Security Status", className="text-tertiary")
                ], className="text-center", style={"padding": "4rem"}),
                
                # Map controls with new classes
                html.Div([
                    html.Button("🌐", className="map-panel__control-button", title="Global View"),
                    html.Button("🏙️", className="map-panel__control-button", title="City View"),
                    html.Button("🏢", className="map-panel__control-button", title="Site View"),
                    html.Button("🧅", className="map-panel__control-button", title="Onion View"),
                ], className="map-panel__controls"),
                
                # Status badge with new classes
                html.Div([
                    html.Div(className="map-panel__status-indicator"),
                    "All systems operational"
                ], className="map-panel__status")
            ], className="map-panel__container")
        ], className="dashboard__map-panel"),
        
        # Right Panel - Weak Signal Feed
        html.Div([
            html.Div([
                html.H4("Weak-Signal Live Feed", className="panel__title text-primary"),
            ], className="panel__header"),
            html.Div([
                # News Scraping Signal
                html.Details([
                    html.Summary("News Scraping (1)", className="signal-summary text-secondary"),
                    html.Div([
                        html.Div([
                            html.Div("[N-0001] - High", className="signal-card-header signal-high"),
                            html.Div([
                                html.P("Location: Yokohama", className="text-secondary"),
                                html.P("Description: Foreign actor probing energy facilities", className="text-primary"),
                                html.P("Timestamp: 25 June 2025", className="text-tertiary")
                            ])
                        ], className="signal-card"),
                    ], className="signal-category-content")
                ], className="signal-category"),
                
                # Cross-Location Signals
                html.Details([
                    html.Summary("Cross-Location (1)", className="signal-summary text-secondary"),
                    html.Div([
                        html.Div([
                            html.Div("[CO-0001] - Medium", className="signal-card-header signal-medium"),
                            html.Div([
                                html.P("Location: Osaka HQ + Tokyo Base", className="text-secondary"),
                                html.P("Description: Simultaneous badge denial", className="text-primary"),
                                html.P("Timestamp: 25 June 2025", className="text-tertiary")
                            ])
                        ], className="signal-card"),
                    ], className="signal-category-content")
                ], className="signal-category"),
                
                # Cross-Organization Signals
                html.Details([
                    html.Summary("Cross-Organization (2)", className="signal-summary text-secondary"),
                    html.Div([
                        html.Div([
                            html.Div("[GS-0001] - Low", className="signal-card-header signal-low"),
                            html.Div([
                                html.P("Location: 3rd Party Vendor", className="text-secondary"),
                                html.P("Description: Matching token IDs detected in external firm", className="text-primary"),
                                html.P("Timestamp: 25 June 2025", className="text-tertiary")
                            ])
                        ], className="signal-card"),
                        html.Div([
                            html.Div("[GS-0002] - Medium", className="signal-card-header signal-medium"),
                            html.Div([
                                html.P("Location: Contractor Campus", className="text-secondary"),
                                html.P("Description: Repeated denied access at midnight", className="text-primary"),
                                html.P("Timestamp: 25 June 2025", className="text-tertiary")
                            ])
                        ], className="signal-card"),
                    ], className="signal-category-content")
                ], className="signal-category"),
            ], className="panel__body")
        ], className="panel dashboard__right-panel"),
    ], className="dashboard__content"),
    
    # Bottom Panel with new CSS classes
    html.Div([
        # Detection Breakdown Column
        html.Div([
            html.H4("Incident Detection Breakdown", className="bottom-panel__title"),
            html.Div([
                # Row 1 - Active chips
                html.Div([
                    html.Div("Access Outcome", className="detection-chip detection-chip--active"),
                    html.Div("Unusual Door", className="detection-chip detection-chip--active"),
                    html.Div("Potential Tailgating", className="detection-chip detection-chip--active"),
                    html.Div("Unusual Group", className="detection-chip detection-chip--active"),
                ], className="detection-row"),
                
                # Row 2 - Inactive chips
                html.Div([
                    html.Div("Unusual Path", className="detection-chip detection-chip--inactive"),
                    html.Div("Unusual Time", className="detection-chip detection-chip--inactive"),
                    html.Div("Multiple Attempts", className="detection-chip detection-chip--inactive"),
                    html.Div("Location Criticality", className="detection-chip detection-chip--inactive"),
                ], className="detection-row"),
                
                # Row 3 - Active chips
                html.Div([
                    html.Div("Interaction Effects", className="detection-chip detection-chip--active"),
                    html.Div("Token History", className="detection-chip detection-chip--active"),
                    html.Div("Cross-Location", className="detection-chip detection-chip--active"),
                    html.Div("Cross-Organization", className="detection-chip detection-chip--active"),
                ], className="detection-row"),
                
                # Row 4 - Malfunction
                html.Div([
                    html.Div("Tech. Malfunction", className="detection-chip detection-chip--malfunction"),
                ], className="detection-row justify-center"),
            ], className="detection-grid")
        ], className="bottom-panel__column"),
        
        # Response Column
        html.Div([
            html.H4("Respond", className="bottom-panel__title"),
            html.Div([
                html.Div("Action III", className="response-label"),
                html.Div("Ticket I Action I", className="ticket-display"),
                html.Button(
                    "Mark As Completed", 
                    className="btn btn--success btn--md",
                    style={"marginTop": "1rem"}
                )
            ], className="response-section")
        ], className="bottom-panel__column bottom-panel__column--center"),
        
        # Resolve Column  
        html.Div([
            html.H4("Resolve", className="bottom-panel__title"),
            html.Div([
                # Action checklist with new classes
                html.Div([
                    dcc.Checklist([
                        {"label": " Action I", "value": "A1"},
                        {"label": " Action II", "value": "A2"},
                        {"label": " Action III", "value": "A3"},
                        {"label": " Action IV", "value": "A4"},
                    ], 
                    className="action-checklist",
                    style={"marginBottom": "1rem"}
                    ),
                ]),
                
                # Action buttons with new classes
                html.Div([
                    html.Button("Resolve As Harmful", className="btn btn--critical btn--sm action-button"),
                    html.Button("Resolve As Malfunction", className="btn btn--warning btn--sm action-button"),
                    html.Button("Resolve As Normal", className="btn btn--success btn--sm action-button"),
                    html.Button("Dismiss", className="btn btn--secondary btn--sm action-button"),
                ], className="action-buttons")
            ], className="action-section")
        ], className="bottom-panel__column")
    ], className="bottom-panel")
], className="dashboard")

if __name__ == '__main__':
    app.run(debug=True)