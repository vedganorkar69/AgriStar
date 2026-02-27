import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_fetcher import get_weather_forecast
from utils.geo import DISTRICT_COORDS
from utils.explainer import explain_spoilage

# ─── Spoilage parameters per crop ─────────────────────────────────────────────
SPOILAGE_PARAMS = {
    "Tomato":    {"temp_sensitivity": 0.9, "humidity_sensitivity": 0.85, "shelf_days": 5},
    "Onion":     {"temp_sensitivity": 0.4, "humidity_sensitivity": 0.70, "shelf_days": 30},
    "Wheat":     {"temp_sensitivity": 0.2, "humidity_sensitivity": 0.55, "shelf_days": 180},
    "Potato":    {"temp_sensitivity": 0.5, "humidity_sensitivity": 0.60, "shelf_days": 60},
    "Rice":      {"temp_sensitivity": 0.3, "humidity_sensitivity": 0.60, "shelf_days": 150},
    "Soybean":   {"temp_sensitivity": 0.3, "humidity_sensitivity": 0.50, "shelf_days": 120},
    "Cotton":    {"temp_sensitivity": 0.2, "humidity_sensitivity": 0.40, "shelf_days": 180},
    "Sugarcane": {"temp_sensitivity": 0.7, "humidity_sensitivity": 0.65, "shelf_days": 2},
    "Maize":     {"temp_sensitivity": 0.4, "humidity_sensitivity": 0.55, "shelf_days": 90},
    "Grapes":    {"temp_sensitivity": 0.8, "humidity_sensitivity": 0.80, "shelf_days": 7},
}

# ─── Storage penalties ─────────────────────────────────────────────────────────
STORAGE_PENALTY = {
    "Open (Field)": 0.30,
    "Warehouse":    0.10,
    "Cold Storage": -0.10,
}

# ─── Preservation actions catalogue ───────────────────────────────────────────
ALL_ACTIONS = {
    "refrigerated_transport": {
        "action":        "Use refrigerated transport",
        "cost":          "₹200/qtl",
        "effectiveness": "High",
        "for_risk":      ["HIGH", "MEDIUM"],
    },
    "harvest_dawn": {
        "action":        "Harvest at dawn to reduce field heat",
        "cost":          "Free",
        "effectiveness": "Medium",
        "for_risk":      ["HIGH", "MEDIUM"],
    },
    "wax_coating": {
        "action":        "Apply food-grade wax coating",
        "cost":          "₹50/qtl",
        "effectiveness": "Medium",
        "for_risk":      ["HIGH", "MEDIUM"],
    },
    "cold_storage": {
        "action":        "Move to cold storage within 6 hours",
        "cost":          "₹80/qtl",
        "effectiveness": "High",
        "for_risk":      ["HIGH"],
    },
    "ventilated_bags": {
        "action":        "Use ventilated jute bags",
        "cost":          "₹10/qtl",
        "effectiveness": "Medium",
        "for_risk":      ["MEDIUM", "LOW"],
    },
    "dry_well": {
        "action":        "Store in dry, well-ventilated area",
        "cost":          "Free",
        "effectiveness": "High",
        "for_risk":      ["LOW"],
    },
    "sort_discard": {
        "action":        "Sort and discard visibly damaged produce",
        "cost":          "Free",
        "effectiveness": "Medium",
        "for_risk":      ["HIGH", "MEDIUM", "LOW"],
    },
}


def _risk_level(score: float) -> str:
    if score >= 0.65:
        return "HIGH"
    elif score >= 0.35:
        return "MEDIUM"
    return "LOW"


def _risk_color(level: str) -> str:
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[level]


def assess_spoilage(
    crop: str,
    district: str,
    quantity_qtl: float,
    storage_type: str,
    transit_hours: float,
) -> dict:
    """
    Assess post-harvest spoilage risk and recommend actions.
    """
    params = SPOILAGE_PARAMS.get(crop, {"temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "shelf_days": 30})
    lat, lon = DISTRICT_COORDS.get(district, (18.5204, 73.8567))

    weather = get_weather_forecast(lat, lon, days=3)

    # Use 3-day average forecast
    avg_humidity = float(np.mean(weather.get("relative_humidity_2m_max", [65, 65, 65])[:3]))
    avg_temp     = float(np.mean(weather.get("temperature_2m_max",       [30, 30, 30])[:3]))

    # Normalise inputs
    humidity_norm = np.clip((avg_humidity - 40) / 60, 0, 1)   # 40–100% range
    temp_norm     = np.clip((avg_temp      - 15) / 25, 0, 1)  # 15–40°C range
    transit_norm  = np.clip(transit_hours / 24, 0, 1)          # up to 24h

    # Spoilage risk score
    raw_score = (
        params["humidity_sensitivity"] * humidity_norm +
        params["temp_sensitivity"]     * temp_norm     * 0.5 +
        0.20                           * transit_norm
    )
    penalty  = STORAGE_PENALTY.get(storage_type, 0.10)
    score    = float(np.clip(raw_score + penalty, 0, 1))

    risk     = _risk_level(score)
    color    = _risk_color(risk)
    prob_pct = f"{int(score * 100)}%"

    # Filter and sort actions
    actions = [
        v for v in ALL_ACTIONS.values()
        if risk in v["for_risk"]
    ]
    effectiveness_order = {"High": 0, "Medium": 1, "Low": 2}
    actions = sorted(actions, key=lambda x: effectiveness_order.get(x["effectiveness"], 2))

    reason = explain_spoilage(risk, crop, avg_humidity, avg_temp, storage_type)

    return {
        "risk_level":          risk,
        "risk_color":          color,
        "spoilage_probability": prob_pct,
        "score":               round(score, 3),
        "actions":             actions[:4],
        "reason":              reason,
        "weather_summary": {
            "avg_humidity": round(avg_humidity, 1),
            "avg_temp":     round(avg_temp, 1),
        },
    }
