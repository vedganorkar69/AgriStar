"""
Interactive Maharashtra district selector — Folium/Leaflet edition.

Features:
  • India map rendered per Indian government standard
    (PoK + Aksai Chin shown as part of India via datameet composite GeoJSON)
  • CartoDB Dark Matter tiles (Google Maps dark-mode aesthetic, no API key)
  • Maharashtra state highlighted in green
  • All 10 dataset districts shown as crop-emoji markers
  • Selected district zooms-in with a glowing ring + enlarged emoji
  • Click a marker popup → district selected via st_folium event data
  • Synced selectbox below for keyboard/accessibility

render_district_selector(page_key, lang_code, crop) → selected district name
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests as _requests

from utils.geo import DISTRICT_COORDS
from utils.shared_state import get_shared, set_shared, init_shared
from utils.geo_translate import translate_place

# ── Crop → emoji mapping ───────────────────────────────────────────────────────
CROP_EMOJIS = {
    "Tomato":       "🍅",
    "Onion":        "🧅",
    "Potato":       "🥔",
    "Wheat":        "🌾",
    "Rice":         "🌾",
    "Sugarcane":    "🎋",
    "Cotton":       "🌿",
    "Soybean":      "🫘",
    "Maize":        "🌽",
    "Jowar":        "🌾",
    "Bajra":        "🌾",
    "Turmeric":     "🫚",
    "Grapes":       "🍇",
    "Banana":       "🍌",
    "Mango":        "🥭",
    "Orange":       "🍊",
    "Pomegranate":  "🍎",
}
DEFAULT_EMOJI = "🌾"

# ── District names in Devanagari ──────────────────────────────────────────────
def _district_label(name: str, lang_code: str) -> str:
    """Return district name translated to Devanagari via Google Translate (cached)."""
    return translate_place(name, lang_code)


# ── India composite GeoJSON (Indian government perspective) ───────────────────
_INDIA_URLS = [
    # datameet composite: PoK + Aksai Chin shown as part of India
    "https://raw.githubusercontent.com/datameet/maps/master/Country/india-composite.geojson",
    # state-level fallback
    "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
]

@st.cache_data(ttl=86400, show_spinner=False)
def _fetch_india_geojson():
    """Fetch India states GeoJSON (Indian perspective). Returns dict or None."""
    for url in _INDIA_URLS:
        try:
            r = _requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
    return None


# ── Core map builder ─────────────────────────────────────────────────────────
def _build_map(selected_district: str, crop: str = "Wheat", lang_code: str = "en") -> folium.Map:
    districts = list(DISTRICT_COORDS.keys())
    emoji      = CROP_EMOJIS.get(crop, DEFAULT_EMOJI)

    # Zoom into selected district if one is chosen
    if selected_district and selected_district in DISTRICT_COORDS:
        sel_lat, sel_lon = DISTRICT_COORDS[selected_district]
        center, zoom = [sel_lat, sel_lon], 8
    else:
        center, zoom = [19.2, 76.5], 6   # Maharashtra overview

    # ── Base map: CartoDB Dark Matter (Google Maps dark-mode, free, no key) ──
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=None,
        prefer_canvas=True,
        control_scale=True,
    )

    folium.TileLayer(
        tiles=(
            "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        ),
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors '
             '&copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Dark (CartoDB)",
        subdomains="abcd",
        max_zoom=20,
        min_zoom=4,
    ).add_to(m)

    # ── India composite boundary (Indian gov standard: PoK + Aksai Chin) ─────
    india_geojson = _fetch_india_geojson()
    if india_geojson:
        def _style(feature):
            props = feature.get("properties", {})
            name  = (
                props.get("NAME_1") or props.get("ST_NM") or
                props.get("name")   or props.get("NAME")  or ""
            ).upper()
            is_mh = "MAHARASHTRA" in name
            return {
                "fillColor":   "#1a4d2e" if is_mh else "#0d1f12",
                "color":       "#52b788" if is_mh else "#2d4a35",
                "weight":      2.5       if is_mh else 0.8,
                "fillOpacity": 0.55      if is_mh else 0.25,
            }

        folium.GeoJson(
            india_geojson,
            name="India",
            style_function=_style,
            tooltip="India",
            highlight_function=lambda _: {"weight": 3, "color": "#52b788", "fillOpacity": 0.7},
        ).add_to(m)

    # ── District markers with crop emojis ────────────────────────────────────
    for district in districts:
        lat, lon   = DISTRICT_COORDS[district]
        is_selected = district == selected_district

        if is_selected:
            # Glowing ring
            folium.CircleMarker(
                location=[lat, lon],
                radius=28,
                color="#52b788",
                weight=2.5,
                fill=True,
                fill_color="#52b788",
                fill_opacity=0.12,
                popup=None,
            ).add_to(m)
            folium.CircleMarker(
                location=[lat, lon],
                radius=18,
                color="#52b788",
                weight=1.5,
                fill=True,
                fill_color="#52b788",
                fill_opacity=0.18,
                popup=None,
            ).add_to(m)

            # Large selected emoji marker — label in Devanagari if hi/mr
            display = _district_label(district, lang_code)
            icon_html = f"""
            <div style="text-align:center;">
              <div style="font-size:28px;text-shadow:0 0 12px rgba(82,183,136,0.9),0 2px 8px rgba(0,0,0,0.6);filter:drop-shadow(0 0 6px #52b788);animation:pulse 2s infinite;">{emoji}</div>
              <div style="font-size:11px;color:#52b788;font-weight:700;margin-top:2px;text-shadow:0 1px 4px #000;white-space:nowrap;">{display}</div>
            </div>
            <style>@keyframes pulse{{0%{{transform:scale(1);opacity:1;}}50%{{transform:scale(1.15);opacity:.85;}}100%{{transform:scale(1);opacity:1;}}}}</style>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f'<b style="color:#52b788;font-size:1rem;">📍 {display}</b>'
                    f'<br><span style="color:#7d8997;font-size:0.8rem;">Selected district</span>',
                    max_width=200,
                ),
                tooltip=folium.Tooltip(
                    f"✅ {display}",
                    style="background:#0a1e10;color:#52b788;border:1px solid #2d7a4f;border-radius:6px;padding:6px 10px;font-weight:700;",
                ),
                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(60, 50),
                    icon_anchor=(30, 25),
                ),
            ).add_to(m)

        else:
            # Unselected district marker — label in Devanagari if hi/mr
            display = _district_label(district, lang_code)
            icon_html = f"""
            <div style="text-align:center;">
              <div style="font-size:20px;opacity:0.82;text-shadow:0 2px 6px rgba(0,0,0,0.6);">{emoji}</div>
              <div style="font-size:10px;color:#c9d1d9;margin-top:1px;text-shadow:0 1px 4px #000;white-space:nowrap;opacity:0.9;">{display}</div>
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f'<b style="color:#7eb8f0;font-size:0.95rem;">{display}</b>'
                    f'<br><span style="color:#7d8997;font-size:0.78rem;">Click to select</span>',
                    max_width=200,
                ),
                tooltip=folium.Tooltip(
                    f"{emoji} {display}",
                    style="background:#0d1117;color:#c9d1d9;border:1px solid #253040;border-radius:6px;padding:5px 9px;font-size:0.82rem;",
                ),
                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(55, 42),
                    icon_anchor=(27, 21),
                ),
            ).add_to(m)

    # ── Map title box ─────────────────────────────────────────────────────────
    title_html = f"""
    <div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);
                background:rgba(13,17,23,0.88);backdrop-filter:blur(8px);
                border:1px solid #2d7a4f;border-radius:10px;
                padding:8px 20px;z-index:9999;
                font-family:Inter,sans-serif;font-size:0.82rem;
                color:#52b788;font-weight:700;letter-spacing:0.06em;
                box-shadow:0 4px 16px rgba(0,0,0,0.4);">
      🗺️ INDIA · MAHARASHTRA DISTRICT SELECTOR &nbsp;
      <span style="color:#7d8997;font-weight:400;">(PoK &amp; Aksai Chin — Integral part of India)</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    return m


# ── Public API ────────────────────────────────────────────────────────────────
def render_district_selector(page_key: str, lang_code: str = "en",
                              crop: str | None = None) -> str:
    """
    Renders the full interactive India/Maharashtra Leaflet map.
    Returns the selected district name.
    Syncs selection with shared_state so it persists across pages.
    """
    init_shared()

    districts = list(DISTRICT_COORDS.keys())
    state_key  = f"{page_key}_district"

    # Initialise from shared state (so page 1 defaults carry over)
    if state_key not in st.session_state:
        st.session_state[state_key] = get_shared("district")

    current = st.session_state[state_key]
    _crop   = crop or get_shared("crop") or "Wheat"

    # ── Map container styling ─────────────────────────────────────────────────
    st.markdown("""
    <style>
    iframe { border-radius: 14px !important; }
    .stIframe { border-radius: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Render Folium map ─────────────────────────────────────────────────────
    m      = _build_map(current, _crop, lang_code)
    result = st_folium(
        m,
        key=f"folium_{page_key}",
        height=400,
        use_container_width=True,
        returned_objects=["last_object_clicked_popup"],
        return_on_hover=False,
    )

    # ── Handle click ──────────────────────────────────────────────────────────
    if result and result.get("last_object_clicked_popup"):
        raw = result["last_object_clicked_popup"]
        # Extract plain district name from possible HTML
        import re
        text = re.sub(r"<[^>]+>", "", raw).strip()
        # Match against known districts
        matched = next((d for d in districts if d.lower() in text.lower()), None)
        if matched and matched != current:
            st.session_state[state_key] = matched
            set_shared("district", matched)
            st.rerun()

    # ── Sync selectbox ────────────────────────────────────────────────────────
    idx    = districts.index(st.session_state[state_key])
    chosen = st.selectbox(
        f"📍 District",
        districts,
        index=idx,
        key=f"sel_{page_key}",
        help="Click a district on the map above, or choose here",
    )
    if chosen != st.session_state[state_key]:
        st.session_state[state_key] = chosen
        set_shared("district", chosen)

    return st.session_state[state_key]
