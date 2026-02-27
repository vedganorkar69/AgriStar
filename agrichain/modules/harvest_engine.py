import sys
import os
import numpy as np
import pandas as pd
import datetime

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_fetcher import load_mandi_prices, get_weekly_price_index, get_weather_forecast
from utils.geo import DISTRICT_COORDS
from utils.explainer import explain_harvest

# ─── Crop maturity days from sowing ───────────────────────────────────────────
CROP_MATURITY_DAYS = {
    "Tomato":    90,
    "Onion":     120,
    "Wheat":     120,
    "Potato":    80,
    "Rice":      130,
    "Soybean":   100,
    "Cotton":    180,
    "Sugarcane": 365,
    "Maize":     90,
    "Grapes":    150,
}


def _price_seasonality_score(crop: str, target_week: int) -> float:
    """
    Returns a score 0–1 based on how good the target week is historically
    for the given crop.
    """
    df = load_mandi_prices(crop)
    if df.empty:
        return 0.5

    weekly_idx = get_weekly_price_index(df)
    if target_week not in weekly_idx.index:
        target_week = weekly_idx.index[0]

    week_price = weekly_idx.get(target_week, weekly_idx.mean())
    min_p, max_p = weekly_idx.min(), weekly_idx.max()
    if max_p == min_p:
        return 0.5
    return float(np.clip((week_price - min_p) / (max_p - min_p), 0, 1))


def _weather_score(weather: dict, start_day: int = 0, window: int = 7) -> float:
    """
    Score 0–1 based on weather over the harvest window.
    Lower humidity + less rain = better.
    """
    humidity = weather.get("relative_humidity_2m_max", [])
    rain     = weather.get("precipitation_sum", [])
    temp     = weather.get("temperature_2m_max", [])

    h_window = humidity[start_day: start_day + window]
    r_window = rain[start_day: start_day + window]
    t_window = temp[start_day: start_day + window]

    avg_h = np.mean(h_window) if h_window else 65
    avg_r = np.mean(r_window) if r_window else 2
    avg_t = np.mean(t_window) if t_window else 30

    # Ideal: humidity < 60, rain < 2mm, temp 20–35
    h_score = np.clip((90 - avg_h) / 60, 0, 1)
    r_score = np.clip((10 - avg_r) / 10, 0, 1)
    t_score = np.clip(1 - abs(avg_t - 27) / 20, 0, 1)

    return float(0.5 * h_score + 0.35 * r_score + 0.15 * t_score)


def _soil_readiness_score(crop: str, days_since_sowing: int) -> float:
    """
    Returns a score 0–1 based on how close to maturity the crop is.
    Peaks at 100% maturity, penalises early or very late harvests.
    """
    maturity = CROP_MATURITY_DAYS.get(crop, 100)
    ratio = days_since_sowing / maturity
    if ratio < 0.85:
        return float(ratio / 0.85 * 0.6)     # Not ready yet
    elif ratio <= 1.10:
        return float(1.0 - abs(ratio - 1.0) * 2)   # Optimal window
    else:
        return float(max(0, 1 - (ratio - 1.1) * 3))  # Overdue penalty


def get_harvest_recommendation(
    crop: str,
    district: str,
    sowing_date: datetime.date,
) -> dict:
    """
    Returns the recommended harvest window and supporting data.
    """
    today = datetime.date.today()
    days_since_sowing = (today - sowing_date).days

    # Fetch weather
    lat, lon = DISTRICT_COORDS.get(district, (18.5204, 73.8567))
    weather = get_weather_forecast(lat, lon, days=14)

    # Score each of the next 7 days as a potential start of harvest window
    scores = []
    for start in range(7):
        candidate_date = today + datetime.timedelta(days=start)
        target_week = int(candidate_date.strftime("%V"))

        ps = _price_seasonality_score(crop, target_week)
        ws = _weather_score(weather, start_day=start, window=7)
        sr = _soil_readiness_score(crop, days_since_sowing + start)

        total = 0.5 * ps + 0.3 * ws + 0.2 * sr
        scores.append({
            "start_offset": start,
            "date":         candidate_date,
            "price_seasonality": round(ps, 3),
            "weather":           round(ws, 3),
            "soil_readiness":    round(sr, 3),
            "total":             round(total, 3),
        })

    best = max(scores, key=lambda x: x["total"])
    best_start = best["date"]
    best_end   = best_start + datetime.timedelta(days=5)

    # Confidence
    score_val = best["total"]
    if score_val >= 0.65:
        confidence = "High"
        premium_pct = int(score_val * 28)
    elif score_val >= 0.45:
        confidence = "Medium"
        premium_pct = int(score_val * 18)
    else:
        confidence = "Low"
        premium_pct = int(score_val * 10)

    reasons = explain_harvest(
        {k: best[k] for k in ("price_seasonality", "weather", "soil_readiness")},
        crop,
        days_since_sowing,
    )

    # Build 14-day price forecast for chart
    df = load_mandi_prices(crop)
    weekly_idx = get_weekly_price_index(df)
    chart_data = []
    for i in range(14):
        d = today + datetime.timedelta(days=i)
        wk = int(d.strftime("%V"))
        p = weekly_idx.get(wk, weekly_idx.mean()) if not weekly_idx.empty else 1800
        chart_data.append({"Date": d.isoformat(), "Price (₹/qtl)": round(float(p))})

    return {
        "recommended_window": {
            "start": best_start.strftime("%B %d, %Y"),
            "end":   best_end.strftime("%B %d, %Y"),
        },
        "expected_price_premium": f"{premium_pct}%",
        "confidence": confidence,
        "score": score_val,
        "reasons": reasons,
        "weather": weather,
        "chart_data": chart_data,
        "score_components": {k: best[k] for k in ("price_seasonality", "weather", "soil_readiness")},
    }
