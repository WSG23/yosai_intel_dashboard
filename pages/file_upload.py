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


@callback(
    [Output('column-mapping-modal', 'children'),
     Output('column-mapping-modal', 'style'),
     Output('upload-status', 'children')],
    Input('upload-data', 'contents'),
    [State('upload-data', 'filename'),
     State('user-session', 'data')],
    prevent_initial_call=True
)
def process_upload_with_existing_ai(contents, filename, user_session):
    """Use your existing AI plugin for file processing"""
    if not contents or not filename:
        return [], {'display': 'none'}, ""

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            headers = df.columns.tolist()

            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
                df.to_csv(tmp.name, index=False)
                temp_path = tmp.name

            try:
                from plugins.ai_classification.plugin import AIClassificationPlugin

                ai_plugin = AIClassificationPlugin()
                ai_plugin.start()

                user_id = user_session.get('user_id', 'default_client') if user_session else 'default_client'
                session_id = str(uuid.uuid4())

                processing_result = ai_plugin.process_csv_file(temp_path, session_id, user_id)

                if processing_result.get('success'):
                    mapping_result = ai_plugin.map_columns(headers, session_id)
                    floor_result = ai_plugin.estimate_floors(df.to_dict('records'), session_id)

                    modal_content = render_column_mapping_panel(
                        header_options=headers,
                        file_name=filename,
                        ai_suggestions=mapping_result.get('suggested_mapping', {}),
                        floor_estimate=floor_result,
                        user_id=user_id
                    )

                    status_content = html.Div([
                        html.Div("✅ File processed with AI analysis", className="alert alert-success"),
                        html.Div([
                            html.Ul([
                                html.Li(f"📊 {len(df)} rows, {len(headers)} columns processed"),
                                html.Li(f"🤖 AI mapped {len(mapping_result.get('suggested_mapping', {}))} columns"),
                                html.Li(f"🏢 {floor_result.get('total_floors', 'Unknown')} floors estimated"),
                            ])
                        ])
                    ])

                    return modal_content, {'display': 'block'}, status_content
                else:
                    modal_content = render_column_mapping_panel(
                        header_options=headers,
                        file_name=filename,
                        user_id=user_id
                    )

                    status_content = html.Div([
                        html.Div("⚠️ File processed (AI analysis unavailable)", className="alert alert-warning")
                    ])

                    return modal_content, {'display': 'block'}, status_content

            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            return [], {'display': 'none'}, html.Div([
                html.Div("❌ Please upload a CSV file", className="alert alert-danger")
            ])

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        try:
            if 'df' in locals():
                headers = df.columns.tolist()
                modal_content = render_column_mapping_panel(
                    header_options=headers,
                    file_name=filename
                )
                status_content = html.Div([
                    html.Div("⚠️ File processed with basic analysis", className="alert alert-warning"),
                    html.Small(f"AI analysis failed: {str(e)}")
                ])
                return modal_content, {'display': 'block'}, status_content
        except Exception:
            pass

        return [], {'display': 'none'}, html.Div([
            html.Div("❌ Error processing file", className="alert alert-danger"),
            html.Small(str(e))
        ])
