"""
Runtime theming utilities for Streamlit.
Provides robust light/dark themes using CSS variables and configures Plotly defaults.
Avoids brittle selectors by scoping to .stApp and common form controls.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
from plotly import io as pio


LIGHT_CSS = """
<style>
:root {
  --gds-bg: #FFFFFF;
  --gds-fg: #1F2D3D;
  --gds-muted: #5A6B7B;
  --gds-primary: #005EB8;
  --gds-secondary-bg: #F6F8FA;
  --gds-border: #E5E7EB;
  --gds-card: #FFFFFF;
}
.stApp {
  background-color: var(--gds-bg);
  color: var(--gds-fg);
}
section[data-testid="stSidebar"] {
  background-color: var(--gds-secondary-bg);
}
.stApp a { color: var(--gds-primary) !important; }
.stApp .stMarkdown, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
  color: var(--gds-fg);
}
/* Inputs */
.stApp input, .stApp select, .stApp textarea, .stApp [data-baseweb="input"] input, .stApp [data-baseweb="textarea"] textarea {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border-color: var(--gds-border) !important;
}
/* Select/dropdown (BaseWeb) */
.stApp [data-baseweb="select"] > div {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border-color: var(--gds-border) !important;
}
.stApp div[role="listbox"] {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border: 1px solid var(--gds-border) !important;
}
/* Buttons */
.stApp button {
  background-color: var(--gds-secondary-bg) !important;
  color: var(--gds-fg) !important;
  border: 1px solid var(--gds-border) !important;
}
.stApp button:hover {
  background-color: var(--gds-card) !important;
}
/* DataFrame/table */
.stApp [data-testid="stDataFrame"] { background-color: var(--gds-card) !important; }
.stApp [data-testid="stDataFrame"] table { background-color: var(--gds-card) !important; color: var(--gds-fg) !important; }
.stApp [data-testid="stDataFrame"] th, .stApp [data-testid="stDataFrame"] td { background-color: var(--gds-card) !important; color: var(--gds-fg) !important; border-color: var(--gds-border) !important; }
/* Expander */
.stApp [data-testid="stExpander"] { background-color: var(--gds-secondary-bg) !important; border: 1px solid var(--gds-border) !important; }
/* Tabs */
.stApp [data-baseweb="tab-list"] { background-color: var(--gds-secondary-bg) !important; }
.stApp [data-baseweb="tab"] { color: var(--gds-fg) !important; }
.stApp [data-baseweb="tab"][aria-selected="true"] { border-bottom: 2px solid var(--gds-primary) !important; }
/* Alerts and code blocks */
.stApp .stAlert { background-color: var(--gds-secondary-bg) !important; color: var(--gds-fg) !important; }
.stApp pre, .stApp code { background-color: var(--gds-secondary-bg) !important; color: var(--gds-fg) !important; }
</style>
"""

DARK_CSS = """
<style>
:root {
  --gds-bg: #0E1117;
  --gds-fg: #E6E6E6;
  --gds-muted: #A0AEC0;
  --gds-primary: #4EA1F3;
  --gds-secondary-bg: #161A23;
  --gds-border: #2A2F3A;
  --gds-card: #161A23;
}
.stApp {
  background-color: var(--gds-bg);
  color: var(--gds-fg);
}
section[data-testid="stSidebar"] {
  background-color: var(--gds-secondary-bg);
}
.stApp a { color: var(--gds-primary) !important; }
.stApp .stMarkdown, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
  color: var(--gds-fg);
}
/* Inputs */
.stApp input, .stApp select, .stApp textarea {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border-color: var(--gds-border) !important;
}
/* Inputs (BaseWeb) */
.stApp [data-baseweb="input"] input, .stApp [data-baseweb="textarea"] textarea {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border-color: var(--gds-border) !important;
}
/* Select/dropdown (BaseWeb) */
.stApp [data-baseweb="select"] > div {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border-color: var(--gds-border) !important;
}
.stApp div[role="listbox"] {
  background-color: var(--gds-card) !important;
  color: var(--gds-fg) !important;
  border: 1px solid var(--gds-border) !important;
}
/* Buttons */
.stApp button {
  background-color: var(--gds-secondary-bg) !important;
  color: var(--gds-fg) !important;
  border: 1px solid var(--gds-border) !important;
}
.stApp button:hover {
  background-color: var(--gds-card) !important;
}
/* DataFrame/table */
.stApp [data-testid="stDataFrame"] { background-color: var(--gds-card) !important; }
.stApp [data-testid="stDataFrame"] table { background-color: var(--gds-card) !important; color: var(--gds-fg) !important; }
.stApp [data-testid="stDataFrame"] th, .stApp [data-testid="stDataFrame"] td { background-color: var(--gds-card) !important; color: var(--gds-fg) !important; border-color: var(--gds-border) !important; }
/* Expander */
.stApp [data-testid="stExpander"] { background-color: var(--gds-secondary-bg) !important; border: 1px solid var(--gds-border) !important; }
/* Tabs */
.stApp [data-baseweb="tab-list"] { background-color: var(--gds-secondary-bg) !important; }
.stApp [data-baseweb="tab"] { color: var(--gds-fg) !important; }
.stApp [data-baseweb="tab"][aria-selected="true"] { border-bottom: 2px solid var(--gds-primary) !important; }
/* Alerts and code blocks */
.stApp .stAlert { background-color: var(--gds-secondary-bg) !important; color: var(--gds-fg) !important; }
.stApp pre, .stApp code { background-color: var(--gds-secondary-bg) !important; color: var(--gds-fg) !important; }
</style>
"""


def apply_theme(theme: str) -> None:
    """
    Apply runtime theme and configure Plotly defaults.
    Args:
        theme: 'light' or 'dark'
    """
    if theme.lower() == "dark":
        st.markdown(DARK_CSS, unsafe_allow_html=True)
        try:
            px.defaults.template = "plotly_dark"
            pio.templates.default = "plotly_dark"
        except Exception:
            pass
    else:
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)
        try:
            px.defaults.template = "plotly_white"
            pio.templates.default = "plotly_white"
        except Exception:
            pass


