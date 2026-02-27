import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from modules.spoilage_assessor import assess_spoilage, STORAGE_PENALTY
from modules.data_fetcher import CROPS
from utils.geo import DISTRICT_COORDS
from utils.translator import t, render_lang_sidebar
from utils.map_selector import render_district_selector
from utils.shared_state import init_shared, get_shared, sync_all
from utils.green_theme import inject_theme

st.set_page_config(page_title="Spoilage Assessor — AgriChain", page_icon="⚠️", layout="wide")
inject_theme()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d1117; }

.page-header {
    background: linear-gradient(135deg, #2a0a0a 0%, #3d1010 60%, #5c1a1a 100%);
    border: 1px solid #6b2020;
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    display: flex; align-items: center; gap: 20px;
}
.page-header-icon { font-size: 3rem; flex-shrink: 0; }
.page-header h1   { font-size: 2.2rem; font-weight: 900; color: #e6edf3; margin: 0; line-height: 1.1; }
.page-header p    { font-size: 0.95rem; color: #f09090; margin: 6px 0 0; }

.input-section {
    background: #131a22;
    border: 1px solid #253040;
    border-radius: 18px;
    padding: 28px 28px 20px;
    margin-bottom: 24px;
}

/* Risk banners */
.risk-banner {
    border-radius: 20px;
    padding: 30px 36px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
}
.risk-banner::after {
    position: absolute; right: 30px; top: 50%; transform: translateY(-50%);
    font-size: 7rem; opacity: 0.07; pointer-events: none;
}
.risk-high   { background: linear-gradient(135deg, #1c0505, #2d0a0a); border: 1.5px solid #f85149; }
.risk-high::after   { content: '🔴'; }
.risk-medium { background: linear-gradient(135deg, #1c1000, #2d1a00); border: 1.5px solid #e3a008; }
.risk-medium::after { content: '🟡'; }
.risk-low    { background: linear-gradient(135deg, #051c0d, #0a2d16); border: 1.5px solid #52b788; }
.risk-low::after    { content: '🟢'; }

.risk-label-high   { font-size: 2.6rem; font-weight: 900; color: #f85149; }
.risk-label-medium { font-size: 2.6rem; font-weight: 900; color: #e3a008; }
.risk-label-low    { font-size: 2.6rem; font-weight: 900; color: #52b788; }

.risk-prob  { font-size: 1.05rem; color: #c9d1d9; margin-top: 8px; }
.risk-why   { font-size: 0.9rem; color: #8899aa; margin-top: 10px; font-style: italic; line-height: 1.6; }

/* Action cards */
.action-card {
    border-radius: 14px;
    padding: 16px 20px;
    margin: 10px 0;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    border: 1px solid transparent;
}
.action-high   { background: #150505; border-color: #3c1010; }
.action-medium { background: #151005; border-color: #3c2c10; }
.action-low    { background: #051510; border-color: #103c20; }

.action-num  { font-size: 1.1rem; font-weight: 900; color: #5a6676; flex-shrink: 0; width: 24px; }
.action-text { font-size: 0.93rem; font-weight: 600; color: #e6edf3; line-height: 1.4; }
.action-meta { font-size: 0.82rem; color: #7d8997; margin-top: 4px; }
.eff-high    { color: #52b788 !important; font-weight: 700; }
.eff-medium  { color: #e3a008 !important; font-weight: 700; }

[data-testid="metric-container"] { background:#131a22 !important; border:1px solid #253040 !important; border-radius:14px !important; padding:18px !important; }
[data-testid="metric-container"] label { color:#7d8997 !important; font-size:0.82rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#e6edf3 !important; font-weight:800 !important; }
section[data-testid="stSidebar"] { background: #0a0f15 !important; border-right: 1px solid #1e2833; }
h1,h2,h3,h4 { color:#e6edf3; } p { color:#c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:0 0 16px;">
    <span style="font-size:2rem;">🌾</span>
    <div style="font-size:1.2rem;font-weight:800;color:#52b788;margin-top:4px;">AgriChain</div>
    </div>""", unsafe_allow_html=True)
    lang_code = render_lang_sidebar()
    st.markdown("---")
    st.page_link("app.py",                    label="🏠  Home")
    st.page_link("pages/1_🌾_Harvest.py",     label="🌾  Harvest Window")
    st.page_link("pages/2_🏪_Mandi.py",       label="🏪  Mandi Ranker")
    st.page_link("pages/3_⚠️_Spoilage.py",    label="⚠️  Spoilage Assessor")
    st.page_link("pages/4_🤖_AI_Assistant.py",label="🤖  AI Assistant")

# ─── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <div class="page-header-icon">⚠️</div>
  <div>
    <h1>{t('Spoilage Assessor', lang_code)}</h1>
    <p>Know your <strong>post-harvest spoilage risk</strong> and get ranked actions to preserve your produce.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Inputs ────────────────────────────────────────────────────────────────
init_shared()
storage_options = list(STORAGE_PENALTY.keys())

# Crop first so emoji is ready for the map
inp_col, map_col = st.columns([1, 1.7])

with inp_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    _def_crop = get_shared("crop")
    crop      = st.selectbox(t("Select Crop", lang_code), CROPS,
                             index=CROPS.index(_def_crop) if _def_crop in CROPS else 0,
                             key="sp_crop")
    quantity      = st.number_input(t("Quantity (Quintals)", lang_code),
                                    min_value=1.0, max_value=5000.0,
                                    value=float(get_shared("quantity") or 20.0), step=5.0)
    _def_stor     = get_shared("storage")
    storage_type  = st.selectbox(t("Storage Type", lang_code), storage_options,
                                 index=storage_options.index(_def_stor) if _def_stor in storage_options else 0)
    transit_hours = st.slider(t("Transit Duration (Hours)", lang_code),
                              min_value=1, max_value=48,
                              value=int(get_shared("transit") or 8), step=1)
    run = st.button(f"🔍 {t('Assess Spoilage Risk', lang_code)}", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with map_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    district = render_district_selector("spoilage", lang_code, crop=crop)
    st.markdown('</div>', unsafe_allow_html=True)

sync_all(crop=crop, district=district, quantity=quantity, storage=storage_type, transit=transit_hours)

# ─── Results ───────────────────────────────────────────────────────────────────
if run:
    with st.spinner("Calculating spoilage risk from weather + crop data..."):
        result = assess_spoilage(crop, district, quantity, storage_type, transit_hours)

    risk  = result["risk_level"]
    color = result["risk_color"]
    prob  = result["spoilage_probability"]
    wx    = result["weather_summary"]

    risk_class  = f"risk-{risk.lower()}"
    label_class = f"risk-label-{risk.lower()}"
    act_class   = f"action-{risk.lower()}"

    # ─── Risk Banner ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="risk-banner {risk_class}">
      <div style="color:#7d8997;font-size:0.78rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">
        {t('Spoilage Risk', lang_code)}
      </div>
      <div class="{label_class}">{color} {t(risk, lang_code)}</div>
      <div class="risk-prob">
        🎯 {t('Spoilage Probability', lang_code)}: <strong style="font-size:1.2rem;">{prob}</strong>
      </div>
      <div class="risk-why">📋 {result['reason']}</div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Metrics row ────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌡️ Risk Score",          f"{int(result['score']*100)}%",     border=True)
    m2.metric("💧 Avg Humidity",         f"{wx['avg_humidity']:.0f}%",       border=True)
    m3.metric("🌡️ Avg Temp (3-day)",    f"{wx['avg_temp']:.1f} °C",         border=True)
    m4.metric("🚛 Transit",             f"{transit_hours} hrs",               border=True)

    # ─── Gauge ────────────────────────────────────────────────────────────────
    col_gauge, col_actions = st.columns([1, 1.6])
    with col_gauge:
        gauge_color = {"HIGH": "#f85149", "MEDIUM": "#e3a008", "LOW": "#52b788"}[risk]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=int(result["score"] * 100),
            domain={"x": [0,1], "y": [0,1]},
            title={"text": "Risk Score", "font": {"color": "#8899aa", "size": 14}},
            number={"suffix": "%", "font": {"color": gauge_color, "size": 46}},
            gauge={
                "axis":       {"range": [0,100], "tickcolor": "#5a6676", "tickwidth": 1},
                "bar":        {"color": gauge_color, "thickness": 0.28},
                "bgcolor":    "#131a22",
                "bordercolor":"#253040",
                "borderwidth": 2,
                "steps": [
                    {"range": [0, 35],  "color": "#0a1e10"},
                    {"range": [35, 65], "color": "#1e1a05"},
                    {"range": [65, 100],"color": "#1e0505"},
                ],
                "threshold": {"line": {"color": gauge_color, "width": 3}, "thickness": 0.8, "value": int(result["score"]*100)},
            },
        ))
        fig.update_layout(
            paper_bgcolor="#0d1117", font_color="#c9d1d9",
            height=260, margin=dict(l=20, r=20, t=40, b=10),
        )
        st.plotly_chart(fig, width="stretch")

    # ─── Actions ──────────────────────────────────────────────────────────────
    with col_actions:
        st.markdown(f"### 🛡️ {t('Recommended Actions', lang_code)}")
        for i, action in enumerate(result["actions"]):
            eff_class = "eff-high" if action["effectiveness"] == "High" else "eff-medium"
            st.markdown(f"""
            <div class="action-card {act_class}">
              <div class="action-num">#{i+1}</div>
              <div>
                <div class="action-text">{action['action']}</div>
                <div class="action-meta">
                  💰 {t('Cost', lang_code)}: <strong>{action['cost']}</strong>
                  &nbsp;·&nbsp;
                  ⚡ {t('Effectiveness', lang_code)}: <span class="{eff_class}">{action['effectiveness']}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ─── Summary expander ─────────────────────────────────────────────────────
    with st.expander(f"📋 {t('Full Input Summary', lang_code)}", expanded=False):
        summary_df = pd.DataFrame([{
            "Crop": crop, "District": district, "Quantity": f"{quantity:.0f} qtl",
            "Storage Type": storage_type, "Transit": f"{transit_hours} hrs",
            "Risk Level": risk, "Probability": prob,
        }])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
