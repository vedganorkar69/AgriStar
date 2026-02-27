"""
Global AgriChain green theme.
Call inject_theme() at the top of every page (after set_page_config).
"""
import streamlit as st

# ── Core palette ──────────────────────────────────────────────────────────────
BG_BASE     = "#040d07"   # deepest black-green
BG_SURFACE  = "#081b0e"   # card / section background
BG_RAISED   = "#0d2818"   # hovered cards, elevated panels
BG_BORDER   = "#1a4a2a"   # subtle borders
BG_SIDEBAR  = "#030e06"   # sidebar background

GREEN_DIM   = "#1b5e35"   # muted green for inactive elements
GREEN_MID   = "#2d7a4f"   # mid green
GREEN_MAIN  = "#40916c"   # primary accent
GREEN_LIGHT = "#52b788"   # highlights, labels
GREEN_GLOW  = "#74c69d"   # hover / focused glow
GREEN_TEXT  = "#b7e4c7"   # readable green text
WHITE_85    = "#d8f3dc"   # near white on green
WHITE_60    = "#95d5b2"   # softer white

TEXT_PRIMARY = "#d8f3dc"
TEXT_MUTED   = "#74a88a"
TEXT_DIM     = "#3d7a52"

RED_SOFT     = "#c44a3a"
AMBER_SOFT   = "#b07b2a"
BLUE_SOFT    = "#2a7a8a"   # kept for contrast on charts only

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* ── Global background ── */
.stApp {{
  background: {BG_BASE} !important;
  background-image:
    radial-gradient(ellipse 80% 40% at 50% -10%, rgba(64,145,108,.18) 0%, transparent 70%),
    radial-gradient(ellipse 50% 30% at 90% 80%,  rgba(29,95,50,.12)  0%, transparent 60%);
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: {BG_SIDEBAR} !important;
  border-right: 1px solid {BG_BORDER} !important;
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 28px; }}
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {{ color: {TEXT_MUTED}; }}
section[data-testid="stSidebar"] a:hover {{ color: {GREEN_LIGHT} !important; }}

/* ── Metric cards ── */
[data-testid="metric-container"] {{
  background: {BG_SURFACE} !important;
  border: 1px solid {BG_BORDER} !important;
  border-radius: 14px !important;
  padding: 18px !important;
  transition: border-color .2s, box-shadow .2s;
}}
[data-testid="metric-container"]:hover {{
  border-color: {GREEN_MAIN} !important;
  box-shadow: 0 4px 20px rgba(64,145,108,.15) !important;
}}
[data-testid="metric-container"] label {{
  color: {TEXT_MUTED} !important;
  font-size: 0.82rem !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  color: {GREEN_LIGHT} !important;
  font-weight: 800 !important;
  font-size: 1.5rem !important;
}}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
  color: {GREEN_TEXT} !important;
}}

/* ── Buttons ── */
.stButton > button {{
  background: linear-gradient(135deg, {GREEN_MID}, {GREEN_MAIN}) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  letter-spacing: .03em !important;
  transition: filter .2s, transform .15s, box-shadow .2s !important;
  box-shadow: 0 2px 12px rgba(64,145,108,.25) !important;
}}
.stButton > button:hover {{
  filter: brightness(1.15) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(64,145,108,.4) !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, {GREEN_MAIN}, {GREEN_GLOW}) !important;
  box-shadow: 0 4px 18px rgba(82,183,136,.35) !important;
}}

/* ── Selectbox / input ── */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
  background: {BG_SURFACE} !important;
  border-color: {BG_BORDER} !important;
  color: {TEXT_PRIMARY} !important;
  border-radius: 10px !important;
}}
div[data-baseweb="select"]:focus-within > div,
div[data-baseweb="input"]:focus-within > div {{
  border-color: {GREEN_MAIN} !important;
  box-shadow: 0 0 0 2px rgba(64,145,108,.25) !important;
}}
div[data-baseweb="popover"] {{ background: {BG_RAISED} !important; border:1px solid {BG_BORDER} !important; }}
li[role="option"]:hover {{ background: {BG_BORDER} !important; color: {GREEN_LIGHT} !important; }}

/* ── Slider ── */
div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {{
  background: {GREEN_MAIN} !important;
  border-color: {GREEN_LIGHT} !important;
}}
div[data-testid="stSlider"] div[data-baseweb="slider"] [data-testid="stSliderThumbValue"] {{
  color: {GREEN_LIGHT} !important;
}}

/* ── Number input ── */
input[type="number"] {{
  background: {BG_SURFACE} !important;
  color: {TEXT_PRIMARY} !important;
  border-radius: 8px !important;
}}

/* ── Expander ── */
details[data-testid="stExpander"] {{
  background: {BG_SURFACE} !important;
  border: 1px solid {BG_BORDER} !important;
  border-radius: 12px !important;
}}
details[data-testid="stExpander"] summary {{
  color: {GREEN_LIGHT} !important;
  font-weight: 600 !important;
}}

/* ── Dataframe / table ── */
.stDataFrame, iframe {{ border-radius: 12px !important; }}
div[data-testid="stDataFrame"] table {{ background: {BG_SURFACE} !important; }}
div[data-testid="stDataFrame"] th {{ background: {BG_RAISED} !important; color:{GREEN_LIGHT} !important; }}
div[data-testid="stDataFrame"] td {{ color: {TEXT_PRIMARY} !important; }}

/* ── Chat ── */
div[data-testid="stChatMessage"] {{
  background: {BG_SURFACE} !important;
  border: 1px solid {BG_BORDER} !important;
  border-radius: 14px !important;
}}
div[data-testid="stChatInput"] > div {{
  background: {BG_SURFACE} !important;
  border-color: {BG_BORDER} !important;
  border-radius: 14px !important;
}}
div[data-testid="stChatInput"]:focus-within > div {{
  border-color: {GREEN_MAIN} !important;
  box-shadow: 0 0 0 2px rgba(64,145,108,.2) !important;
}}

/* ── Spinner / progress ── */
div[data-testid="stSpinner"] > div > div {{ border-top-color: {GREEN_MAIN} !important; }}
div[data-testid="stProgressBar"] > div {{ background: {BG_BORDER} !important; }}
div[data-testid="stProgressBar"] > div > div {{ background: {GREEN_MAIN} !important; }}

/* ── Typography ── */
h1, h2, h3, h4, h5 {{ color: {TEXT_PRIMARY} !important; }}
p, li {{ color: {TEXT_MUTED}; }}
hr {{ border-color: {BG_BORDER} !important; }}

/* ── Page link buttons ── */
a[data-testid="stPageLink"] button {{
  background: {BG_SURFACE} !important;
  border: 1px solid {BG_BORDER} !important;
  color: {GREEN_LIGHT} !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: all .2s !important;
}}
a[data-testid="stPageLink"] button:hover {{
  background: {BG_RAISED} !important;
  border-color: {GREEN_MAIN} !important;
  box-shadow: 0 4px 16px rgba(64,145,108,.2) !important;
  transform: translateY(-2px) !important;
}}

/* ── Caption / small text ── */
.stCaption, small {{ color: {TEXT_DIM} !important; }}

/* ── Section containers ── */
.input-section {{
  background: {BG_SURFACE} !important;
  border: 1px solid {BG_BORDER} !important;
  border-radius: 18px !important;
  padding: 28px 28px 20px !important;
  margin-bottom: 24px !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height:6px; }}
::-webkit-scrollbar-track {{ background: {BG_BASE}; }}
::-webkit-scrollbar-thumb {{ background: {GREEN_DIM}; border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {GREEN_MAIN}; }}
</style>
"""


def inject_theme():
    """Call once per page, immediately after set_page_config."""
    st.markdown(CSS, unsafe_allow_html=True)
