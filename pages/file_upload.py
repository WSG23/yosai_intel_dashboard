"""
Enhanced File Upload Page with AI Integration
Uses existing AI plugin for processing
"""

from dash import html, dcc, Input, Output, State, callback
import base64
import pandas as pd
import io
import tempfile
import os
import uuid
import logging

from components.analytics.file_uploader import render_column_mapping_panel

logger = logging.getLogger(__name__)


def layout():
    """File upload page layout with AI integration"""
    return html.Div([
        html.H1("File Upload", className="page-title"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='upload-status'),
        html.Div(id='column-mapping-modal', style={'display': 'none'}),
        html.Div(id='mapping-verified-status'),
        html.Div(id='door-mapping-modal', style={'display': 'none'}),
    ])


