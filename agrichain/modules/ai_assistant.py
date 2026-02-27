"""
AI Assistant backend — wraps LangChain + Ollama.
Provides:
  - Ollama availability check and model listing
  - Farm context builder (runs all 3 engines to generate a rich prompt context)
  - build_chain(model_name) → LangChain chain
  - chat(chain, messages, context) → streamed or full response string
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import requests as _requests
from typing import Generator

# ─── Ollama connectivity helpers ───────────────────────────────────────────────
OLLAMA_BASE = "http://localhost:11434"

RECOMMENDED_MODELS = [
    ("llama3.2",     "3B params · fast · best for Q&A"),
    ("llama3.2:1b",  "1B params · very fast · basic answers"),
    ("mistral",      "7B params · great reasoning"),
    ("gemma2:2b",    "2B params · Google model · fast"),
    ("phi3",         "3.8B params · excellent instruction following"),
    ("qwen2.5:3b",   "3B params · multilingual support"),
]


def is_ollama_running() -> bool:
    try:
        r = _requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def list_available_models() -> list[str]:
    """Return list of model names currently pulled in Ollama."""
    try:
        r = _requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


# ─── LangChain chain builder ───────────────────────────────────────────────────
def build_chain(model_name: str):
    """Build a LangChain chain using the specified Ollama model."""
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOllama(
        model=model_name,
        base_url=OLLAMA_BASE,
        temperature=0.7,
        num_predict=512,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()
    return chain


# ─── Farm context builder ──────────────────────────────────────────────────────
def build_farm_context(
    crop: str,
    district: str,
    quantity_qtl: float,
    storage_type: str,
    transit_hours: float,
    sowing_date: datetime.date,
) -> str:
    """
    Runs all 3 AgriChain engines and builds a comprehensive context string
    to inject into the system prompt.
    """
    lines = [
        "=== FARMER PROFILE ===",
        f"Crop: {crop}",
        f"District: {district}, Maharashtra",
        f"Quantity: {quantity_qtl} quintals",
        f"Storage: {storage_type}",
        f"Transit Duration: {transit_hours} hours",
        f"Sowing Date: {sowing_date.strftime('%d %B %Y')}",
        "",
    ]

    # Harvest Engine
    try:
        from modules.harvest_engine import get_harvest_recommendation
        h = get_harvest_recommendation(crop, district, sowing_date)
        lines += [
            "=== HARVEST RECOMMENDATION ===",
            f"Best Window: {h['recommended_window']['start']} to {h['recommended_window']['end']}",
            f"Expected Price Premium: {h['expected_price_premium']}",
            f"Confidence: {h['confidence']}",
            f"Reason 1: {h['reasons'][0] if h['reasons'] else 'N/A'}",
            f"Reason 2: {h['reasons'][1] if len(h['reasons']) > 1 else 'N/A'}",
            f"Price Seasonality Score: {int(h['score_components']['price_seasonality']*100)}%",
            f"Weather Score: {int(h['score_components']['weather']*100)}%",
            f"Soil Readiness Score: {int(h['score_components']['soil_readiness']*100)}%",
            "",
        ]
    except Exception as e:
        lines += [f"=== HARVEST RECOMMENDATION ===", f"Error: {e}", ""]

    # Mandi Ranker
    try:
        from modules.mandi_ranker import rank_mandis
        mandis = rank_mandis(crop, quantity_qtl, district, top_n=3)
        lines += ["=== TOP MANDIS ==="]
        for i, m in enumerate(mandis, 1):
            lines.append(
                f"#{i} {m['mandi']}: Price ₹{m['expected_price']:,.0f}/qtl, "
                f"Transport ₹{m['transport_cost_qtl']:,.0f}/qtl, "
                f"Net Profit ₹{m['net_profit_per_qtl']:,.0f}/qtl, "
                f"Distance {m['distance_km']:.0f} km"
            )
        lines.append("")
    except Exception as e:
        lines += [f"=== TOP MANDIS ===", f"Error: {e}", ""]

    # Spoilage Assessor
    try:
        from modules.spoilage_assessor import assess_spoilage
        s = assess_spoilage(crop, district, quantity_qtl, storage_type, transit_hours)
        lines += [
            "=== SPOILAGE RISK ===",
            f"Risk Level: {s['risk_level']} ({s['spoilage_probability']} probability)",
            f"Reason: {s['reason']}",
            f"Top Action: {s['actions'][0]['action']} (Cost: {s['actions'][0]['cost']}, Effectiveness: {s['actions'][0]['effectiveness']})",
            "",
        ]
    except Exception as e:
        lines += [f"=== SPOILAGE RISK ===", f"Error: {e}", ""]

    return "\n".join(lines)


# ─── System prompt builder ─────────────────────────────────────────────────────
def build_system_prompt(farm_context: str, lang: str = "en") -> str:
    lang_instruction = {
        "hi": (
            "The user may write in Hindi (Devanagari), Hinglish (Roman-script Hindi), or mixed Hindi-English. "
            "Auto-detect the language the user is using and ALWAYS reply in the same language/script mix. "
            "If they write 'Mera fasal kab bechna chahiye?' reply naturally in Hinglish. "
            "If they write in Devanagari, reply in Devanagari. "
            "Keep language simple and conversational, like talking to a farmer friend."
        ),
        "mr": (
            "The user may write in Marathi (Devanagari), Minglish (Roman-script Marathi), or mixed Marathi-English. "
            "Auto-detect and ALWAYS reply in the same language/script. "
            "If they write in Devanagari Marathi, reply in Marathi. If Roman/mixed, reply similarly. "
            "Keep language simple and warm, like a helpful agricultural officer."
        ),
        "en": (
            "The user may write in English, Hinglish (Hindi-English mix like 'Mera crop kab sell karna chahiye?'), "
            "or simple Hindi transliterated in Roman script. "
            "Auto-detect the language mix and reply in the SAME style — if they write Hinglish, you reply Hinglish. "
            "Keep language simple, conversational, and friendly for a farmer."
        ),
    }.get(lang, "Respond in English. Also understand Hinglish/Minglish and reply in the same language the user uses.")

    return f"""You are AgriBot, a friendly and expert AI assistant for Indian farmers. You specialize in:
- Harvest timing and crop readiness
- Best markets (mandis) to sell produce
- Post-harvest storage and spoilage prevention
- Agricultural best practices for Indian conditions

LANGUAGE BEHAVIOUR:
{lang_instruction}

You understand and can converse in: English, Hindi (Devanagari), Marathi (Devanagari),
Hinglish (Roman-script Hindi-English mix), and Minglish (Roman-script Marathi-English mix).
ALWAYS reply in whatever language/script the user writes in — never force a single language.

FARMER DATA (use this to give specific, grounded answers):
{farm_context}

RESPONSE GUIDELINES:
- Always refer to the actual data above when answering questions about harvest, mandis, or spoilage
- Give specific, actionable advice based on the farmer's crop ({farm_context.split('Crop:')[1].split(chr(10))[0].strip() if 'Crop:' in farm_context else 'the crop'})
- Keep answers concise and practical — 3-5 sentences max unless details are needed
- If asked something outside agriculture, politely redirect: "Main sirf kheti ke baare mein help kar sakta hoon 🌾"
- Be warm, supportive, and respectful — use local terms like "bhai", "kisan bhai" when appropriate
"""


# ─── Streamed chat ─────────────────────────────────────────────────────────────
def stream_response(chain, system_prompt: str, history: list, user_input: str) -> Generator:
    """Stream tokens from the LangChain chain."""
    from langchain_core.messages import HumanMessage, AIMessage

    lc_history = []
    for msg in history[:-1]:   # exclude the latest user message
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    return chain.stream({
        "system_prompt": system_prompt,
        "history":       lc_history,
        "input":         user_input,
    })
