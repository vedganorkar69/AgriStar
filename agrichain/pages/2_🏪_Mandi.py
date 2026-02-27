import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import pandas as pd

from modules.mandi_ranker import rank_mandis
from modules.data_fetcher import CROPS
from utils.geo import DISTRICT_COORDS
from utils.translator import t, render_lang_sidebar
from utils.map_selector import render_district_selector
from utils.shared_state import init_shared, get_shared, sync_all
from utils.geo_translate import translate_place

st.set_page_config(page_title="Mandi Ranker — AgriChain", page_icon="🏪", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d1117; }

.page-header {
    background: linear-gradient(135deg, #0a1e3d 0%, #112044 60%, #1a3560 100%);
    border: 1px solid #1e3d6e;
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.page-header-icon { font-size: 3rem; flex-shrink: 0; }
.page-header h1   { font-size: 2.2rem; font-weight: 900; color: #e6edf3; margin: 0; line-height: 1.1; }
.page-header p    { font-size: 0.95rem; color: #7eb8f0; margin: 6px 0 0; }

.input-section {
    background: #131a22;
    border: 1px solid #253040;
    border-radius: 18px;
    padding: 28px 28px 20px;
    margin-bottom: 24px;
}

.mandi-card {
    border-radius: 18px;
    padding: 0;
    margin-bottom: 20px;
    border: 1px solid #253040;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.mandi-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }

.mandi-card-header {
    padding: 20px 24px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.rank-badge {
    width: 42px; height: 42px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 900; flex-shrink: 0;
}
.rank-1-badge { background: linear-gradient(135deg, #b8860b, #ffd700); color: #0d1117; }
.rank-2-badge { background: linear-gradient(135deg, #708090, #c0c0c0); color: #0d1117; }
.rank-3-badge { background: linear-gradient(135deg, #8b4513, #cd7f32); color: #fff; }

.mandi-name   { font-size: 1.15rem; font-weight: 800; color: #e6edf3; }
.mandi-reason { font-size: 0.83rem; color: #7d8997; font-style: italic; margin-top: 3px; }

.mandi-card-1 { background: linear-gradient(160deg, #0e1e10, #152318); border-color: #2d6a4f; }
.mandi-card-2 { background: linear-gradient(160deg, #0e1520, #141d2e); border-color: #2a4a7a; }
.mandi-card-3 { background: linear-gradient(160deg, #1a1208, #211810); border-color: #6b4520; }

.mandi-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    border-top: 1px solid #1e2833;
}
.mandi-metric-cell {
    padding: 14px 18px;
    border-right: 1px solid #1e2833;
    text-align: center;
}
.mandi-metric-cell:last-child { border-right: none; }
.mandi-metric-label { font-size: 0.72rem; color: #5a6676; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.mandi-metric-value { font-size: 1.1rem; font-weight: 800; color: #e6edf3; margin-top: 3px; }
.metric-green { color: #52b788 !important; }
.metric-red   { color: #f85149 !important; }

[data-testid="metric-container"] { background:#131a22 !important; border:1px solid #253040 !important; border-radius:14px !important; padding:18px !important; }
[data-testid="metric-container"] label { color:#7d8997 !important; font-size:0.82rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#e6edf3 !important; font-weight:800 !important; }
section[data-testid="stSidebar"] { background: #0a0f15 !important; border-right: 1px solid #1e2833; }
h1,h2,h3,h4 { color:#e6edf3; } p { color:#c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
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

# ─── Page header ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <div class="page-header-icon">🏪</div>
  <div>
    <h1>{t('Mandi Ranker', lang_code)}</h1>
    <p>Compare markets by <strong>net profit after transport costs</strong> — sell where it matters most.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Inputs ───────────────────────────────────────────────────────────────
init_shared()

# Crop first so emoji is ready for the map
inp_col, map_col = st.columns([1, 1.7])

with inp_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    _def_crop = get_shared("crop")
    crop      = st.selectbox(t("Select Crop", lang_code), CROPS,
                             index=CROPS.index(_def_crop) if _def_crop in CROPS else 0,
                             key="m_crop")
    quantity  = st.number_input(t("Quantity (Quintals)", lang_code),
                                min_value=1.0, max_value=5000.0,
                                value=float(get_shared("quantity") or 50.0), step=5.0)
    run = st.button(f"🔍 {t('Find Best Mandis', lang_code)}", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with map_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    district = render_district_selector("mandi", lang_code, crop=crop)
    st.markdown('</div>', unsafe_allow_html=True)

sync_all(crop=crop, district=district, quantity=quantity)

# ─── Results ──────────────────────────────────────────────────────────────────
if run:
    with st.spinner("Fetching prices and calculating net profits..."):
        mandis = rank_mandis(crop, quantity, district, top_n=3)

    st.markdown(f"### 🏆 Top 3 Mandis — **{quantity:.0f} Qtl** of **{crop}** from **{district}**")
    st.caption("Ranked by net profit per quintal after transport cost")

    card_classes  = ["mandi-card mandi-card-1", "mandi-card mandi-card-2", "mandi-card mandi-card-3"]
    badge_classes = ["rank-badge rank-1-badge", "rank-badge rank-2-badge", "rank-badge rank-3-badge"]
    rank_labels   = ["1", "2", "3"]
    rank_emojis   = ["🥇", "🥈", "🥉"]

    for i, m in enumerate(mandis):
        mandi_display = translate_place(m['mandi'], lang_code)
        st.markdown(f"""
        <div class="{card_classes[i]}">
          <div class="mandi-card-header">
            <div class="{badge_classes[i]}">{rank_labels[i]}</div>
            <div>
              <div class="mandi-name">{rank_emojis[i]} {mandi_display}</div>
              <div class="mandi-reason">💬 {m['reason']}</div>
            </div>
          </div>
          <div class="mandi-metrics">
            <div class="mandi-metric-cell">
              <div class="mandi-metric-label">{t('Expected Price', lang_code)}</div>
              <div class="mandi-metric-value metric-green">₹{m['expected_price']:,.0f}<span style="font-size:0.7rem;color:#5a6676;">/qtl</span></div>
            </div>
            <div class="mandi-metric-cell">
              <div class="mandi-metric-label">{t('Transport Cost', lang_code)}</div>
              <div class="mandi-metric-value metric-red">₹{m['transport_cost_qtl']:,.0f}<span style="font-size:0.7rem;color:#5a6676;">/qtl</span></div>
            </div>
            <div class="mandi-metric-cell">
              <div class="mandi-metric-label">{t('Net Profit per Qtl', lang_code)}</div>
              <div class="mandi-metric-value metric-green">₹{m['net_profit_per_qtl']:,.0f}</div>
            </div>
            <div class="mandi-metric-cell">
              <div class="mandi-metric-label">{t('Distance', lang_code)}</div>
              <div class="mandi-metric-value">{m['distance_km']:.0f} <span style="font-size:0.7rem;color:#5a6676;">km</span></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Chart ────────────────────────────────────────────────────────────────
    st.markdown(f"#### 📊 {t('Mandi Net Profit Comparison', lang_code)}")
    chart_df = pd.DataFrame([{
        "Mandi":                  translate_place(m["mandi"], lang_code),
        "Expected Price (₹/qtl)": m["expected_price"],
        "Transport Cost (₹/qtl)": m["transport_cost_qtl"],
        "Net Profit (₹/qtl)":     m["net_profit_per_qtl"],
    } for m in mandis])

    fig = px.bar(
        chart_df, x="Mandi",
        y=["Expected Price (₹/qtl)", "Transport Cost (₹/qtl)"],
        barmode="group",
        color_discrete_sequence=["#52b788", "#f85149"],
        template="plotly_dark",
    )
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font_color="#c9d1d9", height=320,
        legend=dict(bgcolor="#131a22", bordercolor="#253040", font=dict(size=12)),
        margin=dict(l=16, r=16, t=16, b=16),
        xaxis=dict(showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(gridcolor="#1c2530", tickfont=dict(size=11)),
        bargap=0.3, bargroupgap=0.08,
    )
    st.plotly_chart(fig, width="stretch")

    # ─── Total summary ────────────────────────────────────────────────────────
    st.markdown(f"#### 💰 {t('Total Earnings', lang_code)} — {quantity:.0f} Quintals")
    best  = mandis[0]
    worst = mandis[-1]
    gain  = max(0, (best["net_profit_per_qtl"] - worst["net_profit_per_qtl"]) * quantity)
    t1, t2, t3 = st.columns(3)
    t1.metric(f"🥇 Best Mandi — {best['mandi'].split()[0]}", f"₹{best['net_profit_per_qtl'] * quantity:,.0f}", border=True)
    t2.metric("🚛 Total Transport (Best)",                   f"₹{best['total_transport']:,.0f}", border=True)
    t3.metric("📈 Extra vs Worst Option",                    f"+₹{gain:,.0f}", border=True)
