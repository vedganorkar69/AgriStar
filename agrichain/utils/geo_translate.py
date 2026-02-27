"""
Dynamic Devanagari translation for place names (districts, mandis, cities).

Uses the FREE Google Translate endpoint — no API key required.
Results are cached in Streamlit's cache for 24h to avoid repeated calls.

translate_place(name, lang) → Devanagari string (or original if lang == "en")

Supported lang codes: "hi" (Hindi), "mr" (Marathi), "en" (passthrough)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests as _requests
import streamlit as st

_BASE = "https://translate.googleapis.com/translate_a/t"

# ── Curated Devanagari overrides (more accurate than machine translation) ──────
# Machine translation of proper nouns is sometimes wrong; these take priority.
_OVERRIDES_HI = {
    # Districts
    "Pune":        "पुणे",
    "Nashik":      "नाशिक",
    "Aurangabad":  "औरंगाबाद",
    "Nagpur":      "नागपूर",
    "Solapur":     "सोलापूर",
    "Kolhapur":    "कोल्हापूर",
    "Satara":      "सातारा",
    "Jalgaon":     "जळगाव",
    "Ahmednagar":  "अहमदनगर",
    "Thane":       "ठाणे",
    # Common mandi suffixes
    "APMC":        "एपीएमसी",
    "Market":      "बाजार",
    "Maharashtra": "महाराष्ट्र",
    "India":       "भारत",
}
_OVERRIDES_MR = {
    # Districts (Marathi official names)
    "Pune":        "पुणे",
    "Nashik":      "नाशिक",
    "Aurangabad":  "छत्रपती संभाजीनगर",
    "Nagpur":      "नागपूर",
    "Solapur":     "सोलापूर",
    "Kolhapur":    "कोल्हापूर",
    "Satara":      "सातारा",
    "Jalgaon":     "जळगाव",
    "Ahmednagar":  "अहमदनगर",
    "Thane":       "ठाणे",
    # Common mandi suffixes
    "APMC":        "एपीएमसी",
    "Market":      "बाजार",
    "Maharashtra": "महाराष्ट्र",
    "India":       "भारत",
}


@st.cache_data(ttl=86400, show_spinner=False)
def translate_place(text: str, lang: str) -> str:
    """
    Translate a place name to Devanagari.

    Args:
        text: English place name (e.g. "Pune APMC", "Nashik")
        lang: "hi" for Hindi, "mr" for Marathi, "en" to passthrough

    Returns:
        Devanagari string, or original text if translation fails / lang is "en"
    """
    if lang == "en" or not text:
        return text

    overrides = _OVERRIDES_HI if lang == "hi" else _OVERRIDES_MR

    # Check exact match first
    if text in overrides:
        return overrides[text]

    # Word-by-word override substitution (handles "Pune APMC" etc.)
    words = text.split()
    all_known = all(w in overrides for w in words)
    if all_known:
        return " ".join(overrides[w] for w in words)

    # Fall back to Google Translate free endpoint
    try:
        tl = "hi" if lang == "hi" else "mr"
        r = _requests.get(
            _BASE,
            params={"client": "gtx", "sl": "en", "tl": tl, "q": text},
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            # Response is [[translated, original]] or just [translated]
            if isinstance(data, list):
                first = data[0]
                if isinstance(first, list):
                    return first[0]
                if isinstance(first, str):
                    return first
    except Exception:
        pass

    return text   # graceful fallback to original


def translate_places_batch(names: list[str], lang: str) -> dict[str, str]:
    """
    Translate a list of place names. Returns {english: devanagari} mapping.
    Calls translate_place for each (each is individually cached).
    """
    return {n: translate_place(n, lang) for n in names}
