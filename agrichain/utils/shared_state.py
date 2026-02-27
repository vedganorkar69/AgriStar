"""
Shared parameter state across all AgriChain pages.

When the user sets crop/district/quantity/etc. on any page, those values
are persisted in st.session_state under "shared_*" keys and used as
defaults when any other page first loads.
"""
import datetime
import streamlit as st

# ── Defaults ──────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "crop":     "Tomato",
    "district": "Pune",
    "quantity": 50.0,
    "storage":  "Open (Field)",
    "transit":  6,
    "sowing":   datetime.date.today() - datetime.timedelta(days=85),
}

def init_shared():
    """Initialise all shared keys with defaults if not already set."""
    for k, v in _DEFAULTS.items():
        if f"shared_{k}" not in st.session_state:
            st.session_state[f"shared_{k}"] = v


def get_shared(key: str):
    """Return the current shared value for the given key."""
    init_shared()
    return st.session_state.get(f"shared_{key}", _DEFAULTS.get(key))


def set_shared(key: str, value):
    """Update a shared value (called by each page widget's on_change)."""
    st.session_state[f"shared_{key}"] = value


def sync_all(crop, district, quantity=None, storage=None, transit=None, sowing=None):
    """Convenience: update all provided shared keys at once."""
    set_shared("crop",     crop)
    set_shared("district", district)
    if quantity is not None: set_shared("quantity", quantity)
    if storage  is not None: set_shared("storage",  storage)
    if transit  is not None: set_shared("transit",  transit)
    if sowing   is not None: set_shared("sowing",   sowing)
