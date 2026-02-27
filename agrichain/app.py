import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules.data_fetcher import get_weather_forecast, generate_synthetic_csv
from utils.geo import DISTRICT_COORDS
from utils.translator import t, render_lang_sidebar
from utils.green_theme import inject_theme

st.set_page_config(
    page_title="AgriChain — Smart Farming Decisions",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

st.markdown("""
<style>
/* ── Home-page specific ── */
.hero {
    background: linear-gradient(135deg, #030e06 0%, #0a2e12 35%, #1b5e35 70%, #2d7a4f 100%);
    border-radius: 24px;
    padding: 56px 40px;
    text-align: center;
    margin-bottom: 36px;
    box-shadow: 0 12px 48px rgba(45,122,79,.35), 0 0 0 1px #1a4a2a;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(82,183,136,.06) 0%, transparent 60%);
    pointer-events: none;
}
.hero-icon { font-size: 5rem; margin-bottom: 8px; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4)); }
.hero h1 { font-size: 3.4rem; font-weight: 900; color: #d8f3dc; margin: 0; letter-spacing: -1.5px; }
.hero p  { font-size: 1.15rem; color: #95d5b2; margin: 14px auto 0; max-width: 560px; line-height: 1.6; }

.feat-card {
    background: linear-gradient(160deg, #061209 0%, #0d2818 100%);
    border: 1px solid #1a4a2a;
    border-radius: 20px;
    padding: 32px 24px;
    text-align: center;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.feat-card:hover { transform: translateY(-6px); border-color: #52b788; box-shadow: 0 12px 32px rgba(82,183,136,.2); }
.feat-icon { font-size: 2.8rem; margin-bottom: 14px; }
.feat-card h3 { font-size: 1.18rem; font-weight: 700; color: #d8f3dc; margin: 0 0 10px; }
.feat-card p  { font-size: 0.87rem; color: #74a88a; line-height: 1.55; margin: 0; }

.weather-section {
    background: linear-gradient(135deg, #061209, #0a1e10);
    border: 1px solid #1a4a2a;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 32px;
}
.weather-section h3 { color: #52b788; font-size: 1.1rem; font-weight: 700; margin: 0 0 20px; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0 0 16px;">
      <span style="font-size:2rem;">🌾</span>
      <div style="font-size:1.25rem; font-weight:800; color:#52b788; margin-top:4px;">AgriChain</div>
    </div>
    """, unsafe_allow_html=True)

    lang_code = render_lang_sidebar()

    st.markdown("---")
    st.markdown("<div style='color:#7d8997; font-size:0.78rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:8px;'>Navigation</div>", unsafe_allow_html=True)
    st.page_link("app.py",                       label="🏠  Home")
    st.page_link("pages/1_🌾_Harvest.py",        label="🌾  Harvest Window")
    st.page_link("pages/2_🏪_Mandi.py",          label="🏪  Mandi Ranker")
    st.page_link("pages/3_⚠️_Spoilage.py",       label="⚠️  Spoilage Assessor")
    st.markdown("---")
    st.caption("📡 Open-Meteo · Agmarknet")

# ─── Pre-generate CSV ──────────────────────────────────────────────────────────
generate_synthetic_csv("data/agmarknet_prices.csv")

# ─── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">🌾</div>
  <h1>AgriChain</h1>
  <p>AI-powered decisions for Indian farmers — Harvest smarter. Sell better. Waste less.</p>
</div>
""", unsafe_allow_html=True)

# ─── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="feat-card"><div class="feat-icon">🌤️</div>
    <h3>Harvest Window</h3>
    <p>Find the ideal 5-day harvest window using weather forecasts and historical price seasonality.</p>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/1_🌾_Harvest.py", label="→ Get Harvest Advice", use_container_width=True)

with c2:
    st.markdown("""<div class="feat-card"><div class="feat-icon">🏪</div>
    <h3>Mandi Ranker</h3>
    <p>Compare top 3 markets by net profit after transport costs — know exactly where to sell.</p>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/2_🏪_Mandi.py", label="→ Find Best Mandi", use_container_width=True)

with c3:
    st.markdown("""<div class="feat-card"><div class="feat-icon">🧊</div>
    <h3>Spoilage Assessor</h3>
    <p>Get a spoilage risk score and ranked preservation actions before your produce goes bad.</p>
    </div>""", unsafe_allow_html=True)
    st.page_link("pages/3_⚠️_Spoilage.py", label="→ Check Spoilage Risk", use_container_width=True)

# ─── Live weather widget ───────────────────────────────────────────────────────
st.markdown('<div class="weather-section"><h3>🌡️ Live Weather Snapshot</h3>', unsafe_allow_html=True)
district = st.selectbox("Select your district", list(DISTRICT_COORDS.keys()), index=0, key="home_district")
with st.spinner("Fetching weather..."):
    lat, lon = DISTRICT_COORDS[district]
    wx = get_weather_forecast(lat, lon, days=3)

if wx:
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("🌡️ Max Temp Today",   f"{wx['temperature_2m_max'][0]:.1f} °C")
    w2.metric("🌧️ Rainfall Today",   f"{wx['precipitation_sum'][0]:.1f} mm")
    w3.metric("💧 Max Humidity",     f"{wx['relative_humidity_2m_max'][0]:.0f}%")
    w4.metric("❄️ Min Temp Today",   f"{wx['temperature_2m_min'][0]:.1f} °C")
st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#4a5568;font-size:0.8rem;padding:20px 0 8px;">
  AgriChain · Hackathon MVP · Data: <a href="https://open-meteo.com" style="color:#52b788;">Open-Meteo</a> &amp; Agmarknet · Built with ❤️ for Indian farmers
</div>""", unsafe_allow_html=True)
