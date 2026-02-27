import requests
import pandas as pd
import numpy as np
import os

# ─── Pre-packaged crop data used for CSV generation & scoring ─────────────────
CROPS = [
    "Tomato", "Onion", "Wheat", "Potato", "Rice",
    "Soybean", "Cotton", "Sugarcane", "Maize", "Grapes",
]

MANDIS = [
    "Pune APMC", "Nashik APMC", "Nagpur APMC", "Solapur APMC",
    "Kolhapur APMC", "Aurangabad APMC", "Mumbai APMC", "Sangli APMC",
]

# Base price ranges per crop (₹/quintal)
CROP_BASE_PRICES = {
    "Tomato":    (800,  2800),
    "Onion":     (600,  2200),
    "Wheat":     (1800, 2500),
    "Potato":    (700,  1800),
    "Rice":      (1600, 2800),
    "Soybean":   (3000, 4500),
    "Cotton":    (5000, 7500),
    "Sugarcane": (280,  380),
    "Maize":     (1200, 2000),
    "Grapes":    (4000, 9000),
}

# Mandi price multipliers (relative to base)
MANDI_MULTIPLIERS = {
    "Pune APMC":       1.10,
    "Nashik APMC":     1.08,
    "Nagpur APMC":     1.05,
    "Solapur APMC":    1.02,
    "Kolhapur APMC":   1.06,
    "Aurangabad APMC": 1.03,
    "Mumbai APMC":     1.15,
    "Sangli APMC":     1.04,
}


def generate_synthetic_csv(output_path: str = "data/agmarknet_prices.csv"):
    """Generate synthetic Agmarknet price CSV if not already present."""
    if os.path.exists(output_path):
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rng = np.random.default_rng(42)

    rows = []
    dates = pd.date_range("2025-09-01", periods=180, freq="D")

    for crop in CROPS:
        lo, hi = CROP_BASE_PRICES[crop]
        base_price = (lo + hi) / 2

        for mandi in MANDIS:
            mult = MANDI_MULTIPLIERS[mandi]
            for date in dates:
                # Add seasonality wave + noise
                day_of_year = date.day_of_year
                seasonal = 0.15 * np.sin(2 * np.pi * day_of_year / 365)
                noise = rng.normal(0, 0.05)
                price = base_price * mult * (1 + seasonal + noise)
                price = max(lo * 0.7, min(hi * 1.3, price))

                rows.append({
                    "State":        "Maharashtra",
                    "District":     mandi.replace(" APMC", ""),
                    "Market":       mandi,
                    "Commodity":    crop,
                    "Arrival_Date": date.strftime("%d/%m/%Y"),
                    "Min_Price":    round(price * 0.92),
                    "Max_Price":    round(price * 1.08),
                    "Modal_Price":  round(price),
                })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def load_mandi_prices(crop: str, state: str = "Maharashtra", csv_path: str = "data/agmarknet_prices.csv") -> pd.DataFrame:
    """Load and filter mandi price CSV for a given crop."""
    generate_synthetic_csv(csv_path)
    df = pd.read_csv(csv_path)
    df = df[(df["Commodity"].str.lower() == crop.lower()) & (df["State"] == state)].copy()
    df["Date"] = pd.to_datetime(df["Arrival_Date"], dayfirst=True)
    return df.sort_values("Date")


def get_weekly_price_index(df: pd.DataFrame) -> pd.Series:
    """Weekly average Modal_Price grouped by week-of-year."""
    df = df.copy()
    df["week"] = df["Date"].dt.isocalendar().week.astype(int)
    return df.groupby("week")["Modal_Price"].mean()


def get_weather_forecast(lat: float, lon: float, days: int = 14) -> dict:
    """
    Fetch weather forecast from Open-Meteo (no API key needed).
    Returns a dict with 'time', 'temperature_2m_max', 'precipitation_sum',
    'relative_humidity_2m_max' as lists.
    On error returns synthetic fallback data.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "relative_humidity_2m_max",
        ],
        "forecast_days": days,
        "timezone": "Asia/Kolkata",
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()["daily"]
    except Exception:
        # Fallback: synthetic data so app doesn't crash offline
        import datetime
        today = datetime.date.today()
        dates = [(today + datetime.timedelta(days=i)).isoformat() for i in range(days)]
        rng = np.random.default_rng(0)
        return {
            "time":                       dates,
            "temperature_2m_max":         [float(round(28 + rng.normal(0, 3), 1)) for _ in range(days)],
            "temperature_2m_min":         [float(round(18 + rng.normal(0, 2), 1)) for _ in range(days)],
            "precipitation_sum":          [float(round(max(0, rng.normal(1, 3)), 1)) for _ in range(days)],
            "relative_humidity_2m_max":   [float(round(min(100, max(30, 60 + rng.normal(0, 15))), 1)) for _ in range(days)],
        }
