import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import datetime

from modules.ai_assistant import (
    is_ollama_running, list_available_models,
    build_chain, build_farm_context, build_system_prompt,
    stream_response, RECOMMENDED_MODELS,
)
from modules.harvest_engine import CROP_MATURITY_DAYS
from modules.spoilage_assessor import STORAGE_PENALTY
from modules.data_fetcher import CROPS
from utils.geo import DISTRICT_COORDS
from utils.translator import t, render_lang_sidebar
from utils.green_theme import inject_theme

st.set_page_config(page_title="AI Assistant — AgriChain", page_icon="🤖", layout="wide")
inject_theme()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d1117; }

.page-header {
    background: linear-gradient(135deg, #0d1a2e 0%, #112240 55%, #1a3560 100%);
    border: 1px solid #1e3d6e;
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex; align-items: center; gap: 20px;
}
.page-header-icon { font-size: 3rem; }
.page-header h1   { font-size: 2rem; font-weight: 900; color: #e6edf3; margin: 0; }
.page-header p    { font-size: 0.92rem; color: #7eb8f0; margin: 5px 0 0; }

/* Ollama status banner */
.status-ok  { background:#0a1e10; border:1px solid #2d6a4f; border-radius:12px; padding:12px 18px; color:#52b788; font-weight:600; }
.status-err { background:#1e0a0a; border:1px solid #6b2020; border-radius:12px; padding:12px 18px; color:#f85149; font-weight:600; }

/* FAQ buttons */
.faq-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 20px; }

/* Context card */
.context-card {
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 14px;
    padding: 16px 18px;
    font-size: 0.82rem;
    color: #8899aa;
    line-height: 1.7;
    font-family: monospace;
    max-height: 220px;
    overflow-y: auto;
    margin-top: 12px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #131a22 !important;
    border: 1px solid #1e2833 !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    padding: 12px 18px !important;
}

/* Model select */
.model-card {
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    font-size: 0.83rem;
    color: #7eb8f0;
}

section[data-testid="stSidebar"] { background: #0a0f15 !important; border-right: 1px solid #1e2833; }
[data-testid="metric-container"] { background:#131a22 !important; border:1px solid #253040 !important; border-radius:12px !important; padding:14px !important; }
[data-testid="metric-container"] label { color:#7d8997 !important; font-size:0.8rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#e6edf3 !important; font-weight:800 !important; }
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
    st.markdown("---")

    # ── Farm parameters panel ─────────────────────────────────────────────────
    st.markdown("### 🌾 Farm Parameters")
    st.caption("Set your details — the AI uses these for recommendations")

    p_crop     = st.selectbox("Crop",     CROPS, index=0, key="ai_crop")
    p_district = st.selectbox("District", list(DISTRICT_COORDS.keys()), index=0, key="ai_district")
    p_qty      = st.number_input("Quantity (Qtl)", 1.0, 5000.0, 50.0, 5.0, key="ai_qty")
    p_storage  = st.selectbox("Storage Type", list(STORAGE_PENALTY.keys()), index=0, key="ai_storage")
    p_transit  = st.slider("Transit (Hours)", 1, 48, 6, key="ai_transit")
    maturity    = CROP_MATURITY_DAYS.get(p_crop, 100)
    default_sow = datetime.date.today() - datetime.timedelta(days=int(maturity * 0.85))
    p_sowing   = st.date_input("Sowing Date", value=default_sow,
                                max_value=datetime.date.today(), format="DD/MM/YYYY", key="ai_sowing")

    generate_btn = st.button("⚡ Generate Farm Context", type="primary", use_container_width=True)

    st.markdown("---")

    # ── Model selector ────────────────────────────────────────────────────────
    st.markdown("### 🧠 Ollama Model")
    ollama_ok = is_ollama_running()

    if ollama_ok:
        st.markdown('<div class="status-ok">✅ Ollama is running</div>', unsafe_allow_html=True)
        available = list_available_models()
        if available:
            selected_model = st.selectbox("Select Model", available, index=0, key="ai_model")
        else:
            st.markdown('<div class="status-err">⚠️ No models pulled yet</div>', unsafe_allow_html=True)
            selected_model = None
            st.markdown("**Pull a model first:**")
            st.code("ollama pull llama3.2", language="bash")
    else:
        st.markdown('<div class="status-err">❌ Ollama not running</div>', unsafe_allow_html=True)
        selected_model = None
        st.markdown("**Start Ollama:**")
        st.code("ollama serve", language="bash")
        st.markdown("**Then pull a model:**")
        st.code("ollama pull llama3.2", language="bash")

    # ── Recommended models info ────────────────────────────────────────────────
    with st.expander("💡 Recommended Models"):
        for model_id, desc in RECOMMENDED_MODELS:
            st.markdown(f"""
            <div class="model-card">
              <strong style="color:#e6edf3;">{model_id}</strong><br>
              <span style="color:#5a6676;">{desc}</span><br>
              <code style="color:#52b788;font-size:0.78rem;">ollama pull {model_id}</code>
            </div>""", unsafe_allow_html=True)

# ─── Page Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">🤖</div>
  <div>
    <h1>AgriBot — AI Assistant</h1>
    <p>Ask anything about your harvest, markets, or spoilage — powered by local AI via Ollama.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Session state init ───────────────────────────────────────────────────────
if "ai_messages"      not in st.session_state:
    st.session_state.ai_messages      = []
if "farm_context"     not in st.session_state:
    st.session_state.farm_context     = ""
if "system_prompt"    not in st.session_state:
    st.session_state.system_prompt    = ""
if "chain"            not in st.session_state:
    st.session_state.chain            = None
if "context_ready"    not in st.session_state:
    st.session_state.context_ready    = False
if "ai_pending"       not in st.session_state:
    st.session_state.ai_pending       = False

# ─── Generate context ─────────────────────────────────────────────────────────
if generate_btn:
    with st.spinner("Running harvest, mandi, and spoilage engines..."):
        ctx = build_farm_context(p_crop, p_district, p_qty, p_storage, p_transit, p_sowing)
        sys_prompt = build_system_prompt(ctx, lang_code)
        st.session_state.farm_context  = ctx
        st.session_state.system_prompt = sys_prompt
        st.session_state.context_ready = True
        st.session_state.ai_messages   = []   # reset chat on new context

        if selected_model and ollama_ok:
            st.session_state.chain = build_chain(selected_model)
        else:
            st.session_state.chain = None

    st.success(f"✅ Farm context generated for **{p_crop}** in **{p_district}**! Start chatting below.")

# ─── Show context summary ─────────────────────────────────────────────────────
if st.session_state.context_ready:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        c1, c2, c3 = st.columns(3)
        lines = st.session_state.farm_context.split("\n")

        harvest_premium = next((l.split(": ")[1] for l in lines if "Expected Price Premium" in l), "—")
        top_mandi       = next((l.split(" ", 1)[1].split(":")[0] for l in lines if l.startswith("#1 ")), "—")
        risk_level      = next((l.split(": ")[1].split(" ")[0] for l in lines if l.startswith("Risk Level")), "—")

        c1.metric("💰 Price Premium",    harvest_premium, border=True)
        c2.metric("🏪 Best Mandi",       top_mandi,       border=True)
        c3.metric("⚠️ Spoilage Risk",    risk_level,      border=True)
    with col_r:
        with st.expander("📋 View Raw Farm Context", expanded=False):
            st.markdown(f'<div class="context-card">{st.session_state.farm_context}</div>',
                        unsafe_allow_html=True)

    st.markdown("---")

# ─── Ollama not ready warning ─────────────────────────────────────────────────
if not ollama_ok or not selected_model:
    st.markdown("""
    <div style="background:#1a1000;border:1px solid #5c3e00;border-radius:14px;padding:20px 24px;margin:16px 0;">
      <div style="font-size:1.1rem;font-weight:700;color:#e3a008;margin-bottom:10px;">⚙️ Setup Required</div>
      <p style="color:#c9a040;margin:0 0 12px;">To use the AI chatbot, you need Ollama running locally with at least one model pulled.</p>
      <ol style="color:#a08020;font-size:0.9rem;line-height:2;">
        <li>Download Ollama from <strong>ollama.com</strong></li>
        <li>Run: <code style="background:#2a1e00;padding:2px 8px;border-radius:4px;">ollama serve</code></li>
        <li>Pull a model: <code style="background:#2a1e00;padding:2px 8px;border-radius:4px;">ollama pull llama3.2</code></li>
        <li>Refresh this page</li>
      </ol>
      <div style="color:#7d6020;font-size:0.85rem;margin-top:8px;">💡 Recommended: <strong>llama3.2</strong> (2GB, fast) or <strong>mistral</strong> (4GB, detailed)</div>
    </div>
    """, unsafe_allow_html=True)

# ─── FAQ Quick Buttons ────────────────────────────────────────────────────────
if st.session_state.context_ready:
    st.markdown("#### 💬 Quick Questions")
    faqs = [
        "🌾 When should I harvest?",
        "🏪 Which mandi gives the best profit?",
        "⚠️ What is my spoilage risk?",
        "🚛 How can I reduce transport costs?",
        "🌡️ How does the weather affect my crop?",
        "💰 How much will I earn from this harvest?",
        "🧊 What storage should I use?",
        "📈 Are prices good right now?",
    ]

    cols = st.columns(4)
    for i, faq in enumerate(faqs):
        if cols[i % 4].button(faq, key=f"faq_{i}", use_container_width=True):
            st.session_state.ai_messages.append({"role": "user", "content": faq})
            st.session_state.ai_pending = True   # signal: generate a reply on next run
            st.rerun()

    st.markdown("---")

# ─── Chat interface ───────────────────────────────────────────────────────────
st.markdown("#### 🗨️ Chat with AgriBot")

# Render history
if not st.session_state.ai_messages:
    if st.session_state.context_ready:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#5a6676;">
          <div style="font-size:3rem;margin-bottom:12px;">🤖</div>
          <div style="font-size:1rem;font-weight:600;color:#7d8997;">AgriBot is ready!</div>
          <div style="font-size:0.85rem;margin-top:6px;">Ask a quick question above or type your own below.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#5a6676;">
          <div style="font-size:3rem;margin-bottom:12px;">⚡</div>
          <div style="font-size:1rem;font-weight:600;color:#7d8997;">Set your farm parameters in the sidebar</div>
          <div style="font-size:0.85rem;margin-top:6px;">Then click <strong>Generate Farm Context</strong> to start chatting.</div>
        </div>""", unsafe_allow_html=True)

for msg in st.session_state.ai_messages:
    with st.chat_message(msg["role"], avatar="🧑‍🌾" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# ─── Chat input & response ────────────────────────────────────────────────────
user_input = st.chat_input(
    "Ask in English, Hinglish, हिंदी, मराठी, or Minglish (e.g. Mera fasal kab bechna chahiye?) 🌾",
    disabled=not (st.session_state.context_ready and ollama_ok and selected_model)
)

# Determine the question to answer:
#  - either from the chat box (user_input)
#  - or from a FAQ button click (ai_pending flag set before rerun)
pending_q = None
if user_input:
    st.session_state.ai_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🌾"):
        st.markdown(user_input)
    pending_q = user_input
elif st.session_state.ai_pending and st.session_state.ai_messages and st.session_state.ai_messages[-1]["role"] == "user":
    pending_q = st.session_state.ai_messages[-1]["content"]
    st.session_state.ai_pending = False   # consume the flag

if pending_q:
    # Rebuild chain if it was lost (e.g. after a rerun before generate was clicked)
    if not st.session_state.chain and ollama_ok and selected_model:
        st.session_state.chain = build_chain(selected_model)

    with st.chat_message("assistant", avatar="🤖"):
        if not (ollama_ok and selected_model and st.session_state.chain):
            st.error("⚙️ Please click **Generate Farm Context** first, and make sure Ollama is running.")
        elif not st.session_state.context_ready:
            st.error("⚙️ Please click **Generate Farm Context** in the sidebar first.")
        else:
            placeholder = st.empty()
            full_response = ""
            try:
                for chunk in stream_response(
                    st.session_state.chain,
                    st.session_state.system_prompt,
                    st.session_state.ai_messages,
                    pending_q,
                ):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state.ai_messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                err = str(e)
                if "connection refused" in err.lower() or "connect" in err.lower():
                    st.error("❌ Cannot connect to Ollama. Make sure `ollama serve` is running.")
                else:
                    st.error(f"❌ Error: {err}")

# ─── Clear chat ───────────────────────────────────────────────────────────────
if st.session_state.ai_messages:
    if st.button("🗑️ Clear Chat History", use_container_width=False):
        st.session_state.ai_messages = []
        st.session_state.ai_pending = False
        st.rerun()
