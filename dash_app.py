from __future__ import annotations

import io
import base64
import os
from typing import Tuple, List, Dict, Any
import pandas as pd

from flask import Flask
import dash
from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from core.services.mapping import clean_dataframe
from core.services.interpretation import interpret_nd_nm
from utils.ast_detector import ASTDataDetector
from utils.glass_exporter import build_glass_export
from utils.whonet_exporter import build_whonet_wide
from utils.validator import DataValidator
from utils.glass_validator import validate_glass_df
from utils.schema_analyzer import SchemaAnalyzer
try:
    from Levenshtein import ratio as lev_ratio
    def _sim(a: str, b: str) -> float:
        return lev_ratio(a.lower(), b.lower())
except Exception:
    from difflib import SequenceMatcher
    def _sim(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def parse_contents(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if filename.lower().endswith('.csv'):
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), low_memory=False)
    else:
        df = pd.read_excel(io.BytesIO(decoded))
    df = clean_dataframe(df)
    return df


def build_filters(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    organisms = sorted([str(x) for x in df.get('Organism', pd.Series([], dtype=str)).dropna().unique().tolist() if str(x).strip()])
    specimen_types = sorted([str(x) for x in df.get('Specimen type', pd.Series([], dtype=str)).dropna().unique().tolist() if str(x).strip()])
    antimicrobials = []
    # detect antimicrobials from RSI columns
    rsi_cols = [c for c in df.columns if any(x in c.upper() for x in ['_R', '_S', '_I', 'RESISTANT', 'SUSCEPTIBLE', 'INTERMEDIATE'])]
    nd_cols = [c for c in df.columns if c.endswith('_ND')]
    nm_cols = [c for c in df.columns if c.endswith('_NM')]
    antimicrobials = sorted(set(
        [c.replace('_R','').replace('_S','').replace('_I','')
         .replace('_RESISTANT','').replace('_SUSCEPTIBLE','').replace('_INTERMEDIATE','') for c in rsi_cols] +
        [c.split('_ND')[0] for c in nd_cols] + [c.split('_NM')[0] for c in nm_cols]
    ))
    return organisms, specimen_types, antimicrobials


def compute_resistance_rates(df: pd.DataFrame) -> pd.DataFrame:
    # Works on interpreted RSI columns
    rsi_cols = [c for c in df.columns if any(x in c.upper() for x in ['_R', '_S', '_I', 'RESISTANT', 'SUSCEPTIBLE', 'INTERMEDIATE']) or c.upper().endswith('SIR')]
    if not rsi_cols or 'Organism' not in df.columns:
        return pd.DataFrame()
    results = []
    orgs = df['Organism'].dropna().unique().tolist()
    for org in orgs:
        sub = df[df['Organism'] == org]
        for col in rsi_cols:
            am = col.replace('_R','').replace('_S','').replace('_I','').replace('_RESISTANT','').replace('_SUSCEPTIBLE','').replace('_INTERMEDIATE','').replace('SIR','')
            vals = sub[col].astype(str).str.upper()
            tested = vals.isin(['R','S','I','RES','RESISTANT','SUSCEPTIBLE','SENSITIVE','INTERMEDIATE','INT'])
            if tested.sum() == 0:
                continue
            resistant = vals.isin(['R','RES','RESISTANT']).sum()
            susceptible = vals.isin(['S','SUSCEPTIBLE','SENSITIVE']).sum()
            total = tested.sum()
            res_rate = resistant / total * 100
            sus_rate = susceptible / total * 100
            results.append({
                'Organism': org,
                'Antimicrobial': am,
                'Total_Tested': total,
                'Resistance_Rate_%': round(res_rate, 2),
                'Susceptibility_Rate_%': round(sus_rate, 2)
            })
    return pd.DataFrame(results)


external_stylesheets = [dbc.themes.BOOTSTRAP]
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, title="GLASS Data Standardizer")

app.layout = dbc.Container(
    [
        dcc.Store(id="df-store"),
        dcc.Store(id="map-store"),
        dcc.Store(id="val-store"),
        dcc.Download(id="download-data"),
        dcc.Download(id="download-mapping"),
        dcc.Store(id="theme-store", data={"template":"plotly_white"}),
        dcc.Store(id="prefs-store", data={}, storage_type="local"),
        dcc.Loading(id="loading-overlay", type="default", children=html.Div(id="loading-output")),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H3("🏥 GLASS Data Standardizer", className="mb-0"),
                html.P("Advanced AMR Data Processing & Standardization", className="text-muted mb-0")
            ], width=5),
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("📥 GLASS CSV", id="btn-download-glass", color="primary", size="sm", className="me-1", n_clicks=0),
                    dbc.Button("📥 GLASS JSON", id="btn-download-glass-json", color="secondary", size="sm", n_clicks=0),
                ])
            ], width=4, className="text-end"),
            dbc.Col([
                dcc.Dropdown(id="theme-select", options=[{"label":"☀️ Light","value":"Light"},{"label":"🌙 Dark","value":"Dark"}], 
                           value="Light", clearable=False, style={"minWidth":"120px"})
            ], width=3, className="text-end"),
        ], align="center", className="mb-3"),
        # Workflow Progress Indicator
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Workflow Progress", className="mb-2"),
                        dbc.Progress(id="workflow-progress", value=0, className="mb-2", style={"height":"8px"}),
                        html.Small(id="workflow-status", children="Start by uploading your data", className="text-muted")
                    ])
                ], className="mb-3")
            ], width=12)
        ]),
        html.Hr(),
        dbc.Tabs([
            dbc.Tab(label="📁 Upload", tab_id="tab-upload", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📤 Upload Data File", className="mb-3"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.H2("📤", className="mb-2"),
                                html.P("Drag and Drop or Click to Select", className="mb-1"),
                                html.P("Supports: CSV, Excel (.xlsx, .xls)", className="text-muted small")
                            ], style={"padding":"20px"}),
                            style={
                                'width': '100%', 'minHeight': '150px',
                                'borderWidth': '2px', 'borderStyle': 'dashed',
                                'borderRadius': '8px', 'textAlign': 'center',
                                'borderColor': '#6c757d', 'backgroundColor': '#f8f9fa',
                                'cursor': 'pointer', 'transition': 'all 0.3s'
                            },
                            multiple=False
                        ),
                    ])
                ], className="mb-3"),
                html.Div(id='upload-feedback'),
                html.Div(id='data-preview')
            ]),
            dbc.Tab(label="🔀 Merge", tab_id="tab-merge", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Merge Multiple Files", className="mb-3"),
                        dcc.Upload(
                            id='upload-multi',
                            children=html.Div([
                                html.H2("📁", className="mb-2"),
                                html.P("Select Multiple Files to Merge", className="mb-1"),
                                html.P("All files will be intelligently merged", className="text-muted small")
                            ], style={"padding":"20px"}),
                            style={'width': '100%','minHeight': '150px','borderWidth': '2px','borderStyle': 'dashed',
                                   'borderRadius': '8px','textAlign': 'center','borderColor': '#17a2b8',
                                   'backgroundColor': '#f8f9fa','cursor': 'pointer'},
                            multiple=True
                        ),
                    ])
                ], className="mb-3"),
                dbc.Button("🔀 Merge Files", id="btn-merge", color="info", size="lg", className="mb-3", n_clicks=0),
                html.Div(id="merge-feedback")
            ]),
            dbc.Tab(label="🔗 Mapping", tab_id="tab-mapping", children=[
                html.Br(),
                dbc.Alert([
                    html.Strong("💡 Tip: "),
                    "Map your source columns to standard GLASS fields. You can save and reuse mappings for similar files."
                ], color="info", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("📥 Download Template", id="btn-download-mapping", color="secondary", size="sm", className="me-2"),
                        dbc.Button("📤 Load Template", id="btn-load-mapping", color="outline-secondary", size="sm")
                    ], width="auto"),
                    dbc.Col(dcc.Upload(
                        id="upload-mapping", 
                        children=html.Div(['📁 Upload mapping.json'], style={'padding':'8px'}),
                        style={'border':'2px dashed #6c757d','borderRadius':'4px','textAlign':'center','cursor':'pointer'}
                    ), width=3)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("📋 Target Fields"),
                            dbc.CardBody([
                                html.P("Select which standard fields you want to map:", className="small text-muted mb-2"),
                                dcc.Checklist(
                                    id="map-targets", 
                                    options=SchemaAnalyzer.STANDARD_FIELDS, 
                                    value=SchemaAnalyzer.STANDARD_FIELDS, 
                                    inputStyle={"margin-right":"8px", "margin-bottom":"4px"},
                                    labelStyle={"display":"block", "margin-bottom":"4px"}
                                ),
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("🔗 Column Mapping"),
                            dbc.CardBody([
                                html.Div(id="mapping-controls"),
                                html.Br(),
                                dbc.Button("✅ Apply Mapping", id="btn-apply-mapping", color="primary", size="lg", className="w-100")
                            ])
                        ])
                    ], width=8)
                ]),
                html.Br(),
                html.Div(id="mapping-feedback")
            ]),
            dbc.Tab(label="🔄 Transform", tab_id="tab-transform", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardHeader("🔤 Text Transformations"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select columns", className="fw-bold"),
                                dcc.Dropdown(id='tr-cols', options=[], multi=True, placeholder="Choose columns to transform")
                            ], width=6),
                            dbc.Col([
                                html.Label("Operation", className="fw-bold"),
                                dcc.Dropdown(
                                    id='tr-op', 
                                    options=[
                                        {'label': 'Strip whitespace', 'value': 'strip'},
                                        {'label': 'Uppercase', 'value': 'uppercase'},
                                        {'label': 'Lowercase', 'value': 'lowercase'},
                                        {'label': 'Title Case', 'value': 'titlecase'},
                                        {'label': 'Extract Numbers', 'value': 'extract_numbers'}
                                    ], 
                                    value='strip',
                                    placeholder="Select operation"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label(" ", className="fw-bold"),  # Spacer
                                html.Br(),
                                dbc.Button("▶️ Apply", id="btn-apply-transform", color="primary", className="w-100")
                            ], width=2),
                        ]),
                        html.Div(id="transform-feedback", className="mt-3")
                    ])
                ], className="mb-4"),
                dbc.Card([
                    dbc.CardHeader("👤 Age Standardization"),
                    dbc.CardBody([
                        dbc.Alert([
                            html.Strong("ℹ️ "),
                            "Automatically converts age values to years (e.g., '2 months' → 0.17, '5 years' → 5)"
                        ], color="info", className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Age column", className="fw-bold"),
                                dcc.Dropdown(id="age-col", options=[], placeholder="Select age column")
                            ], width=4),
                            dbc.Col([
                                html.Label(" ", className="fw-bold"),
                                html.Br(),
                                dbc.ButtonGroup([
                                    dbc.Button("👁️ Preview", id="btn-age-preview", color="info", outline=True),
                                    dbc.Button("✨ Convert", id="btn-age-apply", color="warning")
                                ])
                            ], width=8),
                        ]),
                        html.Div(id="age-preview", className="mt-3"),
                        html.Div(id="age-feedback", className="mt-2")
                    ])
                ])
            ]),
            dbc.Tab(label="✅ Validate", tab_id="tab-validate", children=[
                html.Br(),
                dbc.Alert([
                    html.Strong("🔍 Validation: "),
                    "Check your data quality and GLASS compliance before export"
                ], color="info", className="mb-3"),
                dbc.Button("▶️ Run Validation", id="btn-validate", color="primary", size="lg", className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("📊 General Data Validation"),
                            dbc.CardBody([
                                html.Div(id="val-general")
                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("🌍 WHO GLASS Validation"),
                            dbc.CardBody([
                                html.Div(id="val-glass")
                            ])
                        ])
                    ], width=6)
                ])
            ]),
            dbc.Tab(label="📥 Import (FHIR/HL7)", tab_id="tab-import", children=[
                html.Br(),
                dbc.Alert([
                    html.Strong("📥 Import Options: "),
                    "Import data from FHIR (JSON) or HL7 v2 (text) formats"
                ], color="info", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("🏥 FHIR Bundle (JSON)"),
                            dbc.CardBody([
                                dcc.Upload(
                                    id="upload-fhir", 
                                    children=html.Div([
                                        html.P("📁 Upload FHIR JSON Bundle", className="mb-0"),
                                        html.P("Drag and drop or click to select", className="small text-muted mb-0")
                                    ], style={'padding':'20px'}),
                                    style={'border':'2px dashed #6c757d','borderRadius':'4px','textAlign':'center','cursor':'pointer'}
                                )
                            ])
                        ])
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("📋 HL7 v2 Message (Text)"),
                            dbc.CardBody([
                                html.Label("Paste HL7 v2 message:", className="fw-bold mb-2"),
                                dcc.Textarea(id="hl7-text", placeholder="Paste HL7 v2 message here...", style={"width":"100%","height":"150px", "fontFamily":"monospace"}),
                                html.Br(),
                                dbc.Button("📥 Import HL7", id="btn-import-hl7", color="secondary", className="w-100")
                            ])
                        ])
                    ], width=6)
                ]),
                html.Br(),
                html.Div(id="import-feedback")
            ]),
            dbc.Tab(label="📊 Analysis", tab_id="tab-analysis", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardHeader("🔍 Filters & Controls"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("🦠 Organisms", className="fw-bold"),
                                dcc.Dropdown(id='f-orgs', options=[], multi=True, placeholder="All organisms"),
                            ], width=3),
                            dbc.Col([
                                html.Label("🧪 Specimen Types", className="fw-bold"),
                                dcc.Dropdown(id='f-spec', options=[], multi=True, placeholder="All types"),
                            ], width=3),
                            dbc.Col([
                                html.Label("💊 Antimicrobials", className="fw-bold"),
                                dcc.Dropdown(id='f-ams', options=[], multi=True, placeholder="All antimicrobials"),
                            ], width=3),
                            dbc.Col([
                                html.Label("⚙️ Interpretation", className="fw-bold"),
                                dbc.InputGroup([
                                    dbc.InputGroupText("Standard:"),
                                    dcc.Dropdown(id="bp-standard", options=[{"label":"CLSI","value":"CLSI"},{"label":"EUCAST","value":"EUCAST"}], 
                                               value="CLSI", clearable=False, style={"flex":1})
                                ], className="mb-2", size="sm"),
                                dbc.InputGroup([
                                    dbc.InputGroupText("Version:"),
                                    dbc.Input(id="bp-version", type="text", value="2024", placeholder="2024", size="sm")
                                ], className="mb-2"),
                                dbc.Button("🔄 Interpret ND/NM → S/I/R", id="btn-interpret", color="warning", size="sm", className="w-100", n_clicks=0),
                            ], width=3)
                        ]),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                html.Label("🎨 Color By", className="fw-bold"),
                                dcc.Dropdown(id='viz-color', options=[{"label":"None","value":"None"},{"label":"Antimicrobial","value":"Antimicrobial"}], 
                                           value="None", clearable=False),
                            ], width=3),
                            dbc.Col([
                                html.Label("📊 Bar Mode", className="fw-bold"),
                                dcc.Dropdown(id='viz-barmode', options=[{"label":"Grouped","value":"group"},{"label":"Stacked","value":"stack"}], 
                                           value="group", clearable=False),
                            ], width=3),
                        ]),
                    ])
                ], className="mb-3"),
                html.Br(),
                dbc.Card([
                    dbc.CardHeader("🔁 Episode-based Deduplication"),
                    dbc.CardBody([
                        dbc.Alert([
                            html.Strong("ℹ️ "),
                            "Remove duplicate isolates within a time window (default: 30 days) for the same patient and organism"
                        ], color="info", className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("👤 Patient ID", className="fw-bold"),
                                dcc.Dropdown(id="dedup-patient", options=[], placeholder="Select column")
                            ], width=3),
                            dbc.Col([
                                html.Label("🦠 Organism", className="fw-bold"),
                                dcc.Dropdown(id="dedup-organism", options=[], placeholder="Select column")
                            ], width=3),
                            dbc.Col([
                                html.Label("📅 Specimen Date", className="fw-bold"),
                                dcc.Dropdown(id="dedup-date", options=[], placeholder="Select column")
                            ], width=3),
                            dbc.Col([
                                html.Label("⏱️ Window (days)", className="fw-bold"),
                                dbc.Input(id="dedup-window", type="number", value=30, min=1, max=90, size="sm")
                            ], width=3),
                        ]),
                        html.Br(),
                        dbc.ButtonGroup([
                            dbc.Button("👁️ Preview", id="btn-dedup-preview", color="info", outline=True),
                            dbc.Button("✅ Apply", id="btn-dedup-apply", color="danger")
                        ]),
                        html.Br(), html.Br(),
                        html.Div(id="dedup-feedback"),
                        html.Div(id="dedup-preview")
                    ])
                ], className="mb-3"),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="overview-chart"),
                        html.Br(),
                        dbc.Button("Download Overview (PNG)", id="btn-dl-overview", color="secondary")
                    ], width=6),
                    dbc.Col([
                        dcc.Graph(id="antibiogram-heatmap"),
                        html.Br(),
                        dbc.Button("Download Antibiogram (PNG)", id="btn-dl-heatmap", color="secondary")
                    ], width=6),
                ]),
                html.Br(),
                html.Div(id='analysis-table')
            ]),
            dbc.Tab(label="📈 Pivot", tab_id="tab-pivot", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardHeader("⚙️ Pivot Table Configuration"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("📊 Index (Rows)", className="fw-bold"),
                                dcc.Dropdown(id='pv-idx', options=[], multi=True, placeholder="Select row dimensions"),
                            ], width=3),
                            dbc.Col([
                                html.Label("📋 Columns", className="fw-bold"),
                                dcc.Dropdown(id='pv-cols', options=[], multi=True, placeholder="Select column dimensions"),
                            ], width=3),
                            dbc.Col([
                                html.Label("🔢 Value", className="fw-bold"),
                                dcc.Dropdown(id='pv-val', options=[], multi=False, placeholder="Select value column"),
                            ], width=3),
                            dbc.Col([
                                html.Label("📈 Aggregation", className="fw-bold"),
                                dcc.Dropdown(id='pv-agg', options=[
                                    {'label': 'Mean', 'value': 'mean'},
                                    {'label': 'Sum', 'value': 'sum'},
                                    {'label': 'Median', 'value': 'median'},
                                    {'label': 'Min', 'value': 'min'},
                                    {'label': 'Max', 'value': 'max'}
                                ], value='mean'),
                            ], width=3),
                        ]),
                    ])
                ], className="mb-3"),
                dcc.Graph(id="pivot-heatmap"),
                html.Br(),
                html.Div(id='pivot-table')
            ]),
            dbc.Tab(label="📉 Trends", tab_id="tab-trends", children=[
                html.Br(),
                dbc.Card([
                    dbc.CardHeader("📈 Trend Analysis Configuration"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("🦠 Organism", className="fw-bold"),
                                dcc.Dropdown(id='tr-org', options=[], multi=False, placeholder="Select organism"),
                            ], width=6),
                            dbc.Col([
                                html.Label("💊 Antimicrobial", className="fw-bold"),
                                dcc.Dropdown(id='tr-am', options=[], multi=False, placeholder="Select antimicrobial"),
                            ], width=6),
                        ]),
                    ])
                ], className="mb-3"),
                dcc.Graph(id="trends-line")
            ]),
            dbc.Tab(label="🛡️ MDR", tab_id="tab-mdr", children=[
                html.Br(),
                dbc.Alert([
                    html.Strong("🛡️ MDR Analysis: "),
                    "Multi-Drug Resistant (MDR), Extensively Drug-Resistant (XDR), and Pandrug-Resistant (PDR) classification"
                ], color="info", className="mb-3"),
                dcc.Graph(id="mdr-bar"),
                html.Br(),
                html.Div(id="mdr-table")
            ]),
            dbc.Tab(label="📋 Audit", tab_id="tab-audit", children=[
                html.Br(),
                dbc.Button("🔄 Refresh Audit", id="btn-audit-refresh", color="secondary", className="me-2"),
                html.Br(), html.Br(),
                html.H5("Recent Audit Events"),
                html.Div(id="audit-events"),
                html.Hr(),
                html.H5("Artifacts"),
                html.Div(id="artifacts-list")
            ]),
            dbc.Tab(label="📊 Data Quality", tab_id="tab-quality", children=[
                html.Br(),
                dbc.Button("🔍 Analyze Data Quality", id="btn-quality", color="primary", size="lg", className="mb-3", n_clicks=0),
                html.Div(id="quality-results")
            ]),
        ], active_tab="tab-upload"),
    ], fluid=True
)


@app.callback(
    Output("df-store", "data"),
    Output("upload-feedback", "children"),
    Output("data-preview", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True
)
def handle_upload(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update
    try:
        df = parse_contents(contents, filename)
        
        # Create enhanced preview with statistics
        stats = [
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Rows", className="text-center mb-0"),
                        html.H4(f"{len(df):,}", className="text-center text-primary mb-0")
                    ])
                ]), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("📋 Columns", className="text-center mb-0"),
                        html.H4(f"{len(df.columns)}", className="text-center text-info mb-0")
                    ])
                ]), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("💾 Memory", className="text-center mb-0"),
                        html.H4(f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB", className="text-center text-success mb-0")
                    ])
                ]), width=3),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("❌ Missing", className="text-center mb-0"),
                        html.H4(f"{df.isna().sum().sum():,}", className="text-center text-warning mb-0")
                    ])
                ]), width=3),
            ], className="mb-3"),
            html.H5("📋 Data Preview (First 10 rows)"),
            dbc.Table.from_dataframe(df.head(10), striped=True, bordered=True, hover=True, responsive=True, className="table-sm")
        ]
        
        alert = dbc.Alert([
            html.Span("✅ ", className="me-2"),
            f"Successfully loaded {filename}: {len(df):,} rows × {len(df.columns)} columns"
        ], color="success", className="mb-3")
        
        return df.to_json(date_format='iso', orient='split'), alert, html.Div(stats)
    except Exception as ex:
        return None, dbc.Alert([
            html.Span("❌ ", className="me-2"),
            f"Error loading file: {str(ex)}"
        ], color="danger"), None


@app.callback(
    Output("f-orgs", "options"),
    Output("f-spec", "options"),
    Output("f-ams", "options"),
    Output("pv-idx", "options"),
    Output("pv-cols", "options"),
    Output("pv-val", "options"),
    Output("tr-org", "options"),
    Output("tr-am", "options"),
    Input("df-store", "data"),
    prevent_initial_call=True
)
def populate_filters(df_json):
    if not df_json:
        empty = []
        return empty, empty, empty, empty, empty, empty, empty, empty
    df = pd.read_json(df_json, orient='split')
    # Update transform column options as well
    orgs, specs, ams = build_filters(df)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    dims = df.columns.tolist()
    return orgs, specs, ams, dims, dims, numeric_cols, orgs, ams


@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Input("btn-interpret", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def interpret_btn(n_clicks, df_json):
    if not n_clicks or not df_json:
        return dash.no_update
    df = pd.read_json(df_json, orient='split')
    try:
        # Defaults; pull from context states if provided
        standard = ctx.states.get('bp-standard.value') if hasattr(ctx, 'states') else "CLSI"
        version = ctx.states.get('bp-version.value') if hasattr(ctx, 'states') else "2024"
        out = interpret_nd_nm(df, standard=standard or "CLSI", version=version or "2024")
        return out.to_json(date_format='iso', orient='split')
    except Exception:
        return dash.no_update


@app.callback(
    Output("overview-chart", "figure"),
    Output("antibiogram-heatmap", "figure"),
    Output("analysis-table", "children"),
    Input("df-store", "data"),
    State("f-orgs", "value"),
    State("f-spec", "value"),
    State("f-ams", "value"),
    prevent_initial_call=True
)
def analysis_overview(df_json, orgs, specs, ams):
    if not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if orgs:
        df = df[df['Organism'].isin(orgs)]
    if specs and 'Specimen type' in df.columns:
        df = df[df['Specimen type'].isin(specs)]
    if ams:
        # keep columns with selected antimicrobials (RSI or ND/NM)
        keep_cols = []
        for a in ams:
            keep_cols += [c for c in df.columns if a in c]
        df = df[[c for c in df.columns if c in keep_cols or c in ['Organism','Specimen type']]]
    rates = compute_resistance_rates(df)
    if rates.empty:
        return go.Figure(), go.Figure(), dbc.Alert("No interpreted RSI columns found. Try 'Interpret ND/NM → S/I/R'.", color="info")
    # Use color and barmode preferences if provided via states (fallback handled below)
    color_pref = ctx.states.get('viz-color.value') if hasattr(ctx, 'states') else "None"
    barmode = ctx.states.get('viz-barmode.value') if hasattr(ctx, 'states') else "group"
    if color_pref == "Antimicrobial":
        fig1 = px.bar(rates, x='Organism', y='Resistance_Rate_%', color='Antimicrobial', barmode=barmode, title="Resistance by Organism × Antimicrobial")
    else:
        fig1 = px.bar(rates.groupby('Organism')['Resistance_Rate_%'].mean().reset_index(), x='Organism', y='Resistance_Rate_%', title="Average Resistance Rate by Organism")
    pivot = rates.pivot_table(index='Organism', columns='Antimicrobial', values='Resistance_Rate_%', aggfunc='mean')
    fig2 = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns.astype(str), y=pivot.index.astype(str), colorscale='RdYlBu_r'))
    fig2.update_layout(title="Antibiogram (Resistance %)")
    table = dbc.Table.from_dataframe(rates.sort_values(['Organism','Antimicrobial']), striped=True, bordered=True, hover=True)
    return fig1, fig2, table

# ---------- Dedup ----------
@app.callback(
    Output("dedup-feedback", "children"),
    Output("dedup-preview", "children"),
    Input("btn-dedup-preview", "n_clicks"),
    State("df-store", "data"),
    State("dedup-patient", "value"),
    State("dedup-organism", "value"),
    State("dedup-date", "value"),
    State("dedup-window", "value"),
    prevent_initial_call=True
)
def dedup_preview(n_clicks, df_json, pid_col, org_col, date_col, window):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if not pid_col or not org_col or not date_col:
        return dbc.Alert("Select patient, organism, and date columns.", color="warning"), None
    try:
        from utils.deduplicator import deduplicate_by_episode
        marked = deduplicate_by_episode(df, patient_col=pid_col, organism_col=org_col, date_col=date_col, window_days=int(window or 30), mark_only=True)
        flagged = marked[marked.get("Deduplicated", False) == True]
        msg = dbc.Alert(f"Preview: would remove {len(flagged)} rows (window={window} days).", color="info")
        preview = dbc.Table.from_dataframe(flagged.head(10), striped=True, bordered=True, hover=True) if not flagged.empty else dbc.Alert("No duplicates found by rule.", color="success")
        return msg, preview
    except Exception as ex:
        return dbc.Alert(f"Dedup preview error: {str(ex)}", color="danger"), None


@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("dedup-feedback", "children", allow_duplicate=True),
    Input("btn-dedup-apply", "n_clicks"),
    State("df-store", "data"),
    State("dedup-patient", "value"),
    State("dedup-organism", "value"),
    State("dedup-date", "value"),
    State("dedup-window", "value"),
    prevent_initial_call=True
)
def dedup_apply(n_clicks, df_json, pid_col, org_col, date_col, window):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if not pid_col or not org_col or not date_col:
        raise dash.exceptions.PreventUpdate
    try:
        from utils.deduplicator import deduplicate_by_episode
        before = len(df)
        out = deduplicate_by_episode(df, patient_col=pid_col, organism_col=org_col, date_col=date_col, window_days=int(window or 30), mark_only=False)
        after = len(out)
        msg = dbc.Alert(f"Applied dedup: {before-after} rows removed. New size: {after}.", color="success")
        return out.to_json(date_format='iso', orient='split'), msg
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"Dedup apply error: {str(ex)}", color="danger")


# ---------- Merge ----------
@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("merge-feedback", "children"),
    Input("btn-merge", "n_clicks"),
    State("upload-multi", "contents"),
    State("upload-multi", "filename"),
    prevent_initial_call=True
)
def do_merge(n_clicks, contents_list, filenames):
    if not n_clicks or not contents_list:
        raise dash.exceptions.PreventUpdate
    dfs = []
    try:
        for contents, filename in zip(contents_list, filenames):
            dfs.append(parse_contents(contents, filename))
        merged = pd.concat(dfs, ignore_index=True)
        merged = clean_dataframe(merged)
        feedback = dbc.Alert(f"Merged {len(dfs)} files → {len(merged)} rows × {len(merged.columns)} columns", color="success")
        return merged.to_json(date_format='iso', orient='split'), feedback
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"Merge error: {str(ex)}", color="danger")


# ---------- Mapping ----------
def _suggest_mappings(source_cols: List[str], targets: List[str]) -> Dict[str,str]:
    suggestions: Dict[str, str] = {}
    used = set()
    for t in targets:
        best = None
        best_score = 0.0
        for s in source_cols:
            if s in used:
                continue
            sc = _sim(s, t)
            if sc > best_score:
                best_score, best = sc, s
        if best and best_score >= 0.6:
            suggestions[t] = best
            used.add(best)
    return suggestions


@app.callback(
    Output("mapping-controls", "children"),
    Input("df-store", "data"),
    Input("map-targets", "value"),
    prevent_initial_call=True
)
def render_mapping_controls(df_json, targets):
    if not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    src_cols = df.columns.tolist()
    sugg = _suggest_mappings(src_cols, targets)
    # Prefer existing map-store values if present
    current_map = dash.callback_context.states.get("map-store.data") if hasattr(dash, 'callback_context') else None
    rows = []
    for t in targets:
        rows.append(
            dbc.Row([
                dbc.Col(html.Div(t), width=4),
                dbc.Col(dcc.Dropdown(id={'type':'map-dd','field':t}, options=src_cols, value=(current_map.get(t) if isinstance(current_map, dict) else sugg.get(t)), placeholder="Select source column"), width=8)
            ], className="mb-2")
        )
    return rows


@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("map-store", "data"),
    Output("mapping-feedback", "children"),
    Input("btn-apply-mapping", "n_clicks"),
    State("df-store", "data"),
    State("map-targets", "value"),
    State({"type":"map-dd","field": dash.ALL}, "value"),
    State({"type":"map-dd","field": dash.ALL}, "id"),
    prevent_initial_call=True
)
def apply_mapping(n_clicks, df_json, targets, values, ids):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    mapping = {}
    for val, idobj in zip(values, ids):
        if val and idobj and isinstance(idobj, dict):
            mapping[idobj.get('field')] = val
    try:
        # Build renamed dataframe with mapped columns first (in target order)
        mapped = pd.DataFrame()
        for t in targets:
            src = mapping.get(t)
            if src in df.columns:
                mapped[t] = df[src]
        # Append remaining columns
        for c in df.columns:
            if c not in mapping.values():
                mapped[c] = df[c]
        feedback = dbc.Alert(f"Applied mapping for {len(mapping)} fields.", color="success")
        return mapped.to_json(date_format='iso', orient='split'), mapping, feedback
    except Exception as ex:
        return dash.no_update, dash.no_update, dbc.Alert(f"Mapping error: {str(ex)}", color="danger")


@app.callback(
    Output("download-mapping", "data"),
    Input("btn-download-mapping", "n_clicks"),
    State("map-store", "data"),
    prevent_initial_call=True
)
def download_mapping(n_clicks, mapping):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    mapping = mapping or {}
    import json
    content = json.dumps({"mappings": mapping}, indent=2)
    return dict(content=content, filename="mapping_template.json")


@app.callback(
    Output("map-store", "data", allow_duplicate=True),
    Input("upload-mapping", "contents"),
    State("upload-mapping", "filename"),
    prevent_initial_call=True
)
def upload_mapping(contents, filename):
    if not contents or not filename:
        raise dash.exceptions.PreventUpdate
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        import json
        data = json.loads(decoded)
        return data.get("mappings", {})
    except Exception:
        raise dash.exceptions.PreventUpdate


# ---------- Transform ----------
@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("transform-feedback", "children"),
    Input("btn-apply-transform", "n_clicks"),
    State("df-store", "data"),
    State("tr-cols", "value"),
    State("tr-op", "value"),
    prevent_initial_call=True
)
def apply_transform(n_clicks, df_json, cols, op):
    if not n_clicks or not df_json or not cols:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    try:
        if op == 'uppercase':
            for c in cols: df[c] = df[c].astype(str).str.upper()
        elif op == 'lowercase':
            for c in cols: df[c] = df[c].astype(str).str.lower()
        elif op == 'titlecase':
            for c in cols: df[c] = df[c].astype(str).str.title()
        elif op == 'strip':
            for c in cols: df[c] = df[c].astype(str).str.strip()
        elif op == 'extract_numbers':
            for c in cols: df[c] = pd.to_numeric(df[c].astype(str).str.extract(r'(\\d+)', expand=False), errors='coerce')
        fb = dbc.Alert(f"Applied '{op}' to {len(cols)} columns.", color="success")
        return df.to_json(date_format='iso', orient='split'), fb
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"Transform error: {str(ex)}", color="danger")


# ---------- Validate ----------
@app.callback(
    Output("val-general", "children"),
    Output("val-glass", "children"),
    Input("btn-validate", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def run_validation(n_clicks, df_json):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    try:
        # General validation
        v = DataValidator()
        gres = v.validate_data(df)
        gen_summary = dbc.Alert(f"Errors: {gres['summary']['total_errors']} | Warnings: {gres['summary']['total_warnings']}", color="info")
        # GLASS validation on exported rows
        glass_df = build_glass_export(df)
        gres2 = validate_glass_df(glass_df)
        # Detailed tables
        det_gen = [gen_summary]
        if gres['errors']:
            det_gen.append(html.H6("Errors"))
            det_gen.append(dbc.Table.from_dataframe(pd.DataFrame(gres['errors']), striped=True, bordered=True, hover=True))
        if gres['warnings']:
            det_gen.append(html.H6("Warnings"))
            det_gen.append(dbc.Table.from_dataframe(pd.DataFrame(gres['warnings']), striped=True, bordered=True, hover=True))
        glass_summary = dbc.Alert(f"GLASS - Errors: {len(gres2.get('errors', []))} | Warnings: {len(gres2.get('warnings', []))} | Passed: {gres2['summary'].get('passed', False)}", color=("success" if gres2['summary'].get('passed') else "warning"))
        det_glass = [glass_summary]
        if gres2.get('errors'):
            det_glass.append(html.H6("GLASS Errors"))
            det_glass.append(dbc.Table.from_dataframe(pd.DataFrame(gres2['errors']), striped=True, bordered=True, hover=True))
        if gres2.get('warnings'):
            det_glass.append(html.H6("GLASS Warnings"))
            det_glass.append(dbc.Table.from_dataframe(pd.DataFrame(gres2['warnings']), striped=True, bordered=True, hover=True))
        return det_gen, det_glass
    except Exception as ex:
        msg = dbc.Alert(f"Validation error: {str(ex)}", color="danger")
        return msg, dash.no_update


@app.callback(
    Output("pivot-heatmap", "figure"),
    Output("pivot-table", "children"),
    Input("df-store", "data"),
    State("pv-idx", "value"),
    State("pv-cols", "value"),
    State("pv-val", "value"),
    State("pv-agg", "value"),
    prevent_initial_call=True
)
def render_pivot(df_json, idx, cols, val, agg):
    if not df_json or not val:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    try:
        pivot = df.pivot_table(index=idx if idx else None, columns=cols if cols else None, values=val, aggfunc=agg)
        fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns.astype(str), y=pivot.index.astype(str), colorscale='Viridis'))
        fig.update_layout(title=f"Pivot heatmap: {val} ({agg})")
        table = dbc.Table.from_dataframe(pivot.reset_index(), striped=True, bordered=True, hover=True)
        return fig, table
    except Exception as ex:
        return go.Figure(), dbc.Alert(f"Pivot error: {str(ex)}", color="warning")

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("btn-dl-overview", "n_clicks"),
    State("df-store", "data"),
    State("f-orgs", "value"),
    State("f-spec", "value"),
    State("f-ams", "value"),
    State("viz-color", "value"),
    State("viz-barmode", "value"),
    prevent_initial_call=True
)
def download_overview_img(n_clicks, df_json, orgs, specs, ams, color_pref, barmode):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if orgs: df = df[df['Organism'].isin(orgs)]
    if specs and 'Specimen type' in df.columns: df = df[df['Specimen type'].isin(specs)]
    if ams:
        keep_cols = []
        for a in ams: keep_cols += [c for c in df.columns if a in c]
        df = df[[c for c in df.columns if c in keep_cols or c in ['Organism','Specimen type']]]
    rates = compute_resistance_rates(df)
    if rates.empty:
        raise dash.exceptions.PreventUpdate
    if color_pref == "Antimicrobial":
        fig = px.bar(rates, x='Organism', y='Resistance_Rate_%', color='Antimicrobial', barmode=barmode, title="Resistance by Organism × Antimicrobial")
    else:
        fig = px.bar(rates.groupby('Organism')['Resistance_Rate_%'].mean().reset_index(), x='Organism', y='Resistance_Rate_%', title="Average Resistance Rate by Organism")
    try:
        png = fig.to_image(format="png")
        return dict(content=png, filename="overview.png")
    except Exception:
        raise dash.exceptions.PreventUpdate

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("btn-dl-heatmap", "n_clicks"),
    State("df-store", "data"),
    State("f-orgs", "value"),
    State("f-spec", "value"),
    State("f-ams", "value"),
    prevent_initial_call=True
)
def download_heatmap_img(n_clicks, df_json, orgs, specs, ams):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if orgs: df = df[df['Organism'].isin(orgs)]
    if specs and 'Specimen type' in df.columns: df = df[df['Specimen type'].isin(specs)]
    if ams:
        keep_cols = []
        for a in ams: keep_cols += [c for c in df.columns if a in c]
        df = df[[c for c in df.columns if c in keep_cols or c in ['Organism','Specimen type']]]
    rates = compute_resistance_rates(df)
    if rates.empty:
        raise dash.exceptions.PreventUpdate
    pivot = rates.pivot_table(index='Organism', columns='Antimicrobial', values='Resistance_Rate_%', aggfunc='mean')
    fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns.astype(str), y=pivot.index.astype(str), colorscale='RdYlBu_r'))
    fig.update_layout(title="Antibiogram (Resistance %)")
    try:
        png = fig.to_image(format="png")
        return dict(content=png, filename="antibiogram.png")
    except Exception:
        raise dash.exceptions.PreventUpdate

# ---------- MDR ----------
@app.callback(
    Output("mdr-bar", "figure"),
    Output("mdr-table", "children"),
    Input("df-store", "data"),
    prevent_initial_call=True
)
def render_mdr(df_json):
    if not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    rsi_cols = [c for c in df.columns if any(x in c.upper() for x in ['_R','_S','_I','RESISTANT','SUSCEPTIBLE','INTERMEDIATE']) or c.upper().endswith('SIR')]
    if not rsi_cols or 'Organism' not in df.columns:
        return go.Figure(), dbc.Alert("No interpreted RSI columns found.", color="info")
    work = df.copy()
    mdr = []
    for _, row in work.iterrows():
        res_ams = set()
        for c in rsi_cols:
            v = str(row.get(c, "")).upper()
            if v in {"R","RES","RESISTANT"}:
                base = c.replace('_R','').replace('_S','').replace('_I','').replace('_RESISTANT','').replace('_SUSCEPTIBLE','').replace('_INTERMEDIATE','').replace('SIR','')
                res_ams.add(base)
        mdr.append(len(res_ams) >= 3)
    work['_is_mdr'] = mdr
    summary = work.groupby('Organism')['_is_mdr'].mean().mul(100).reset_index(name='MDR_Rate_%').sort_values('MDR_Rate_%', ascending=False)
    fig = px.bar(summary, x='MDR_Rate_%', y='Organism', orientation='h', title="MDR Rate by Organism")
    fig.update_xaxes(range=[0,100])
    table = dbc.Table.from_dataframe(summary, striped=True, bordered=True, hover=True)
    return fig, table


@app.callback(
    Output("trends-line", "figure"),
    Input("df-store", "data"),
    State("tr-org", "value"),
    State("tr-am", "value"),
    prevent_initial_call=True
)
def render_trends(df_json, org, am):
    if not df_json or not org or not am:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    if 'Specimen date' not in df.columns:
        return go.Figure()
    rsi_candidates = [c for c in df.columns if am in c and (c.upper().endswith('SIR') or any(x in c.upper() for x in ['_R','_S','_I','RESISTANT','SUSCEPTIBLE','INTERMEDIATE']))]
    if not rsi_candidates:
        return go.Figure()
    use_col = rsi_candidates[0]
    sub = df[df['Organism'] == org].copy()
    sub['_dt'] = pd.to_datetime(sub['Specimen date'], errors='coerce')
    sub = sub.dropna(subset=['_dt'])
    sub['_month'] = sub['_dt'].dt.to_period('M').dt.to_timestamp()
    sub['_is_R'] = sub[use_col].astype(str).str.upper().isin(['R','RES','RESISTANT']).astype(int)
    sub['_is_valid'] = sub[use_col].astype(str).str.upper().isin(['R','S','I','RES','RESISTANT','SUSCEPTIBLE','SENSITIVE','INTERMEDIATE','INT']).astype(int)
    grp = sub.groupby('_month').agg(resistant=('_is_R','sum'), tested=('_is_valid','sum')).reset_index()
    grp['Resistance_Rate_%'] = (grp['resistant'] / grp['tested']).replace([pd.NA, 0], 0) * 100
    fig = px.line(grp, x='_month', y='Resistance_Rate_%', markers=True, title=f"{org} – {am} monthly resistance")
    fig.update_yaxes(range=[0, 100])
    return fig

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("trends-line", "figure"),
    Input("mdr-bar", "figure"),
    prevent_initial_call=True
)
def enable_chart_downloads(trends_fig, mdr_fig):
    # This callback exists to ensure image export dependencies are ready; no-op
    raise dash.exceptions.PreventUpdate


@app.callback(
    Output("download-data", "data"),
    Input("btn-download-glass", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def download_glass(n_clicks, df_json):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    g = build_glass_export(df)
    return dcc.send_data_frame(g.to_csv, "glass_export.csv", index=False)

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("btn-download-glass-json", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def download_glass_json(n_clicks, df_json):
    # On second click with Shift (or as a second callback), provide JSON
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    g = build_glass_export(df)
    content = g.to_json(orient="records", indent=2)
    return dict(content=content, filename="glass_export.json")

# ---------- Age standardization ----------
@app.callback(
    Output("age-preview", "children"),
    Input("btn-age-preview", "n_clicks"),
    State("df-store", "data"),
    State("age-col", "value"),
    prevent_initial_call=True
)
def age_preview(n_clicks, df_json, age_col):
    if not n_clicks or not df_json or not age_col:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    try:
        from utils.helpers import preview_age_conversions
        prev = preview_age_conversions(df, age_col)
        if prev.empty:
            return dbc.Alert("No convertible age patterns found.", color="info")
        return dbc.Table.from_dataframe(prev.head(20), striped=True, bordered=True, hover=True)
    except Exception as ex:
        return dbc.Alert(f"Age preview error: {str(ex)}", color="danger")


@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("age-feedback", "children"),
    Input("btn-age-apply", "n_clicks"),
    State("df-store", "data"),
    State("age-col", "value"),
    prevent_initial_call=True
)
def age_apply(n_clicks, df_json, age_col):
    if not n_clicks or not df_json or not age_col:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    try:
        from utils.helpers import preview_age_conversions, convert_age_column
        prev = preview_age_conversions(df, age_col)
        if prev.empty:
            return dash.no_update, dbc.Alert("No age conversions applied.", color="info")
        approved = {str(r['Original']): float(r['Converted (Years)']) for _, r in prev.iterrows()}
        out = convert_age_column(df, age_col, approved)
        return out.to_json(date_format='iso', orient='split'), dbc.Alert(f"Converted age values in '{age_col}' to years.", color="success")
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"Age convert error: {str(ex)}", color="danger")

# ---------- Importers ----------
@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("import-feedback", "children", allow_duplicate=True),
    Input("upload-fhir", "contents"),
    State("upload-fhir", "filename"),
    prevent_initial_call=True
)
def import_fhir(contents, filename):
    if not contents:
        raise dash.exceptions.PreventUpdate
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')
        import json
        bundle = json.loads(decoded)
        from utils.importers.fhir_importer import import_fhir_bundle
        df = import_fhir_bundle(bundle)
        if df is None or df.empty:
            return dash.no_update, dbc.Alert("FHIR import produced no rows.", color="warning")
        df = clean_dataframe(df)
        return df.to_json(date_format='iso', orient='split'), dbc.Alert(f"Imported FHIR: {len(df)} rows", color="success")
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"FHIR import error: {str(ex)}", color="danger")


@app.callback(
    Output("df-store", "data", allow_duplicate=True),
    Output("import-feedback", "children", allow_duplicate=True),
    Input("btn-import-hl7", "n_clicks"),
    State("hl7-text", "value"),
    prevent_initial_call=True
)
def import_hl7(n_clicks, text):
    if not n_clicks or not text:
        raise dash.exceptions.PreventUpdate
    try:
        from utils.importers.hl7_importer import import_hl7_message
        df = import_hl7_message(text)
        if df is None or df.empty:
            return dash.no_update, dbc.Alert("HL7 import produced no rows.", color="warning")
        df = clean_dataframe(df)
        return df.to_json(date_format='iso', orient='split'), dbc.Alert(f"Imported HL7: {len(df)} rows", color="success")
    except Exception as ex:
        return dash.no_update, dbc.Alert(f"HL7 import error: {str(ex)}", color="danger")

# ---------- Audit ----------
@app.callback(
    Output("audit-events", "children"),
    Output("artifacts-list", "children"),
    Input("btn-audit-refresh", "n_clicks"),
    prevent_initial_call=True
)
def audit_refresh(n_clicks):
    try:
        events = []
        if os.path.exists("logs/audit.jsonl"):
            lines = []
            with open("logs/audit.jsonl", "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 200:  # limit
                        break
                    lines.append(line.strip())
            if lines:
                import json
                rows = [json.loads(x) for x in lines[::-1]]
                events = dbc.Table.from_dataframe(pd.DataFrame(rows), striped=True, bordered=True, hover=True)
        arts = []
        if os.path.isdir("artifacts"):
            files = os.listdir("artifacts")
            if files:
                arts = html.Ul([html.Li(x) for x in sorted(files, reverse=True)])
        return events or dbc.Alert("No recent audit entries.", color="info"), arts or dbc.Alert("No artifacts found.", color="info")
    except Exception as ex:
        return dbc.Alert(f"Audit read error: {str(ex)}", color="danger"), dbc.Alert("No artifacts found.", color="info")

# ---------- Data Quality Analysis ----------
@app.callback(
    Output("quality-results", "children"),
    Input("btn-quality", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def analyze_quality(n_clicks, df_json):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    try:
        df = pd.read_json(df_json, orient='split')
        
        # Calculate quality metrics
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isna().sum().sum()
        completeness = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0
        
        duplicate_rows = df.duplicated().sum()
        uniqueness = (1 - duplicate_rows / len(df)) * 100 if len(df) > 0 else 0
        
        # Column statistics
        col_stats = []
        for col in df.columns:
            null_pct = df[col].isna().sum() / len(df) * 100
            unique_vals = df[col].nunique()
            dtype = str(df[col].dtype)
            col_stats.append({
                'Column': col,
                'Type': dtype,
                'Missing %': f"{null_pct:.1f}%",
                'Unique Values': unique_vals,
                'Quality': 'Good' if null_pct < 10 else 'Warning' if null_pct < 30 else 'Poor'
            })
        
        col_df = pd.DataFrame(col_stats)
        
        # Create quality score
        quality_score = (completeness + uniqueness) / 2
        
        return [
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Overall Quality Score", className="text-center"),
                        html.H1(f"{quality_score:.1f}%", className="text-center", 
                               style={"color": "green" if quality_score >= 80 else "orange" if quality_score >= 60 else "red"}),
                        html.P("Based on completeness and uniqueness", className="text-center text-muted")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("✅ Completeness", className="mb-2"),
                        html.H4(f"{completeness:.1f}%", className="text-success"),
                        html.P(f"Missing: {missing_cells:,} cells", className="small text-muted mb-0")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("🔑 Uniqueness", className="mb-2"),
                        html.H4(f"{uniqueness:.1f}%", className="text-info"),
                        html.P(f"Duplicates: {duplicate_rows:,} rows", className="small text-muted mb-0")
                    ])
                ]), width=4),
            ], className="mb-4"),
            html.H5("📋 Column Quality Analysis"),
            dbc.Table.from_dataframe(col_df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")
        ]
    except Exception as ex:
        return dbc.Alert(f"Quality analysis error: {str(ex)}", color="danger")

# ---------- Theme ----------
@app.callback(
    Output("theme-store", "data"),
    Input("theme-select", "value"),
    prevent_initial_call=True
)
def set_theme(value):
    template = "plotly_dark" if value == "Dark" else "plotly_white"
    return {"template": template}

# ---------- Workflow Progress ----------
@app.callback(
    Output("workflow-progress", "value"),
    Output("workflow-status", "children"),
    Input("df-store", "data"),
    Input("map-store", "data"),
    Input("val-store", "data"),
    prevent_initial_call=False
)
def update_workflow_progress(df_data, map_data, val_data):
    steps_complete = 0
    status = "Start by uploading your data"
    
    if df_data:
        steps_complete += 25
        status = "✅ Data uploaded"
    if map_data:
        steps_complete += 25
        status = "✅ Mapping applied"
    if val_data:
        steps_complete += 25
        status = "✅ Validation complete"
    
    if steps_complete >= 75:
        status = "✅ Ready to export!"
        steps_complete = 100
    
    return steps_complete, status

# ---------- Preferences persist ----------
@app.callback(
    Output("prefs-store", "data", allow_duplicate=True),
    Input("theme-select", "value"),
    Input("f-orgs", "value"),
    Input("f-spec", "value"),
    Input("f-ams", "value"),
    prevent_initial_call=True
)
def save_prefs(theme, orgs, specs, ams):
    return {"theme": theme, "orgs": orgs or [], "specs": specs or [], "ams": ams or []}

@app.callback(
    Output("f-orgs", "value"),
    Output("f-spec", "value"),
    Output("f-ams", "value"),
    Output("theme-select", "value"),
    Input("prefs-store", "data"),
    State("f-orgs", "options"),
    State("f-spec", "options"),
    State("f-ams", "options"),
    prevent_initial_call=True
)
def load_prefs(prefs, org_options, spec_options, am_options):
    if not prefs:
        raise dash.exceptions.PreventUpdate
    orgs = [o for o in (prefs.get("orgs") or []) if o in (org_options or [])]
    specs = [o for o in (prefs.get("specs") or []) if o in (spec_options or [])]
    ams = [o for o in (prefs.get("ams") or []) if o in (am_options or [])]
    theme = prefs.get("theme") or "Light"
    return orgs or None, specs or None, ams or None, theme

@app.callback(
    Output("download-data", "data", allow_duplicate=True),
    Input("btn-download-whonet", "n_clicks"),
    State("df-store", "data"),
    prevent_initial_call=True
)
def download_whonet(n_clicks, df_json):
    if not n_clicks or not df_json:
        raise dash.exceptions.PreventUpdate
    df = pd.read_json(df_json, orient='split')
    g = build_glass_export(df)
    w = build_whonet_wide(g)
    return dcc.send_data_frame(w.to_csv, "whonet_export.csv", index=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8501"))
    app.run_server(host="0.0.0.0", port=port, debug=False)


