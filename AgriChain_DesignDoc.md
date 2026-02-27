# AgriChain — Technical Design Document

**Version:** 1.0  
**Stack:** Python · Streamlit · Pandas · Scikit-learn · Open-Meteo · Agmarknet  

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     STREAMLIT FRONTEND                   │
│   [Crop Input] [District Input] [Storage Type Input]     │
│   [Harvest Widget] [Mandi Ranker] [Spoilage Assessor]    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   AGRICHAIN BACKEND (Python)             │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Harvest    │  │    Mandi     │  │   Spoilage     │  │
│  │  Engine     │  │   Ranker     │  │   Assessor     │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│  ┌──────▼────────────────▼───────────────────▼────────┐  │
│  │              Data Layer                             │  │
│  │  WeatherAPI │ PriceCache │ SoilAPI │ SpoilageLUT   │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  Open-Meteo      Agmarknet      ISRIC Soil
  (Weather)       (Prices)       (Soil data)
```

---

## 2. Module Design

### 2.1 Harvest Engine

**Purpose:** Recommend optimal harvest window (7-day range)

**Algorithm:**
```
harvest_score(day) = 
    0.5 × price_seasonality_score(crop, day) +
    0.3 × weather_score(district, day) +
    0.2 × soil_readiness_score(crop, sowing_date, day)
```

**Inputs:**
- `crop_name: str`
- `district: str`
- `sowing_date: date`

**Output:**
```python
{
  "recommended_window": {"start": "2026-03-10", "end": "2026-03-15"},
  "expected_price_premium": "18%",
  "confidence": "High",
  "reasons": [
    "Mandi prices historically peak in this week for Tomato",
    "Weather forecast shows low humidity — ideal for harvest"
  ]
}
```

**Data flow:**
1. Fetch last 3 years Agmarknet prices for crop × district
2. Compute weekly average price index
3. Fetch 14-day weather forecast from Open-Meteo
4. Score each harvest day, return top window

---

### 2.2 Mandi Ranker

**Purpose:** Rank top 3 mandis by expected net profit

**Algorithm:**
```
mandi_score(m) = 
    avg_price(m, crop) - transport_cost(district, m)

transport_cost = distance_km × cost_per_km × quantity_qtl
```

**Inputs:**
- `crop_name: str`
- `quantity_quintals: float`
- `farmer_district: str`

**Output:**
```python
[
  {
    "mandi": "Pune APMC",
    "expected_price": 2450,
    "transport_cost": 180,
    "net_profit_per_qtl": 2270,
    "distance_km": 45,
    "reason": "Highest price this week, manageable distance"
  },
  ...
]
```

**Data flow:**
1. Load Agmarknet CSV filtered for crop
2. Compute 7-day rolling average price per mandi
3. Estimate transport cost using straight-line distance (haversine)
4. Rank by net profit, return top 3

---

### 2.3 Spoilage Assessor

**Purpose:** Assess post-harvest spoilage risk and recommend actions

**Spoilage Risk Model:**
```
risk_score = 
    humidity_weight × forecast_humidity +
    temp_weight × forecast_temp +
    transit_weight × transit_hours +
    storage_penalty[storage_type]
```

**Risk Thresholds:**
```python
LOW    = risk_score < 0.35
MEDIUM = 0.35 ≤ risk_score < 0.65
HIGH   = risk_score ≥ 0.65
```

**Spoilage Lookup Table (static):**
```python
SPOILAGE_PARAMS = {
    "tomato":   {"temp_sensitivity": 0.9, "humidity_sensitivity": 0.8, "shelf_days": 5},
    "onion":    {"temp_sensitivity": 0.4, "humidity_sensitivity": 0.7, "shelf_days": 30},
    "wheat":    {"temp_sensitivity": 0.2, "humidity_sensitivity": 0.6, "shelf_days": 180},
    "potato":   {"temp_sensitivity": 0.5, "humidity_sensitivity": 0.6, "shelf_days": 60},
    ...
}
```

**Output:**
```python
{
  "risk_level": "HIGH",
  "risk_color": "🔴",
  "spoilage_probability": "72%",
  "actions": [
    {"action": "Use refrigerated transport", "cost": "₹200/qtl", "effectiveness": "High"},
    {"action": "Harvest at dawn to reduce field heat", "cost": "Free", "effectiveness": "Medium"},
    {"action": "Apply wax coating", "cost": "₹50/qtl", "effectiveness": "Medium"}
  ],
  "reason": "3-day humidity forecast is 85%+ — very high spoilage risk for Tomato"
}
```

---

## 3. Data Layer

### 3.1 Weather (Open-Meteo)
```python
import requests

def get_weather_forecast(lat, lon, days=14):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "precipitation_sum", "relative_humidity_2m_max"],
        "forecast_days": days,
        "timezone": "Asia/Kolkata"
    }
    return requests.get(url, params=params).json()
```

### 3.2 Mandi Prices (Agmarknet CSV)
```python
import pandas as pd

def load_mandi_prices(crop: str, state: str = "Maharashtra"):
    df = pd.read_csv("data/agmarknet_prices.csv")
    df = df[df["Commodity"].str.lower() == crop.lower()]
    df = df[df["State"] == state]
    df["Date"] = pd.to_datetime(df["Arrival_Date"])
    return df.sort_values("Date")

def get_weekly_price_index(df):
    df["week"] = df["Date"].dt.isocalendar().week
    return df.groupby(["week"])["Modal_Price"].mean()
```

### 3.3 District Coordinates (Static Lookup)
```python
DISTRICT_COORDS = {
    "pune": (18.5204, 73.8567),
    "nashik": (19.9975, 73.7898),
    "nagpur": (21.1458, 79.0882),
    "solapur": (17.6868, 75.9064),
    # ... add more
}
```

---

## 4. Streamlit UI Structure

```
Ripple_Effect/                    # github.com/samyakg051-creator/Ripple_Effect
│
├── app.py
├── pages/
│   ├── 1_harvest.py        # Harvest Window page
│   ├── 2_mandi.py          # Mandi Ranker page
│   └── 3_spoilage.py       # Spoilage Assessor page
├── modules/
│   ├── harvest_engine.py
│   ├── mandi_ranker.py
│   ├── spoilage_assessor.py
│   └── data_fetcher.py
├── data/
│   └── agmarknet_prices.csv
├── utils/
│   ├── translator.py       # Hindi output
│   └── explainer.py        # Plain language reasons
└── requirements.txt
```

---

## 5. Explainability Layer

Every recommendation surfaces **exactly 2 reasons** in plain language:

```python
def explain_harvest(score_components: dict) -> list[str]:
    reasons = []
    if score_components["price_seasonality"] > 0.7:
        reasons.append(f"Mandi prices are historically 15–20% higher this week for {crop}")
    if score_components["weather"] > 0.6:
        reasons.append("Weather forecast looks dry — good conditions for harvest")
    if score_components["soil_readiness"] > 0.7:
        reasons.append(f"Crop is ready based on {days_since_sowing} days since sowing")
    return reasons[:2]
```

---

## 6. Hindi Output (Simple Translation Layer)

```python
TRANSLATIONS = {
    "Best harvest window": "सबसे अच्छा कटाई समय",
    "Expected price premium": "अनुमानित अतिरिक्त मूल्य",
    "High risk": "अधिक खतरा 🔴",
    "Low risk": "कम खतरा 🟢",
    "Recommended mandi": "सबसे अच्छी मंडी",
    "Transport cost": "परिवहन लागत",
}

def translate(text: str, lang: str = "hi") -> str:
    if lang == "hi":
        return TRANSLATIONS.get(text, text)
    return text
```

---

## 7. Tech Stack Summary

| Layer | Technology | Why |
|---|---|---|
| Frontend | Streamlit | Fast to build, mobile-friendly |
| Backend | Python 3.11 | Team familiarity, rich ML ecosystem |
| Data processing | Pandas, NumPy | CSV + time-series analysis |
| ML model | Scikit-learn (basic scoring) | No heavy training needed |
| Weather API | Open-Meteo | Free, no API key, reliable |
| Price data | Agmarknet CSV | Government data, downloadable |
| Distance calc | Haversine formula | No API key needed |
| Translation | Static dict (MVP) | Fast, no external dependency |
| Deployment | Streamlit Cloud | Free, instant deploy |

---

## 8. Environment Setup

**📦 Repository:** [https://github.com/samyakg051-creator/Ripple_Effect](https://github.com/samyakg051-creator/Ripple_Effect)

```bash
# Clone and setup
pip install -r requirements.txt

# requirements.txt
streamlit==1.32.0
pandas==2.2.0
numpy==1.26.0
requests==2.31.0
scikit-learn==1.4.0
plotly==5.18.0

# Run locally
streamlit run app.py

# Deploy — connect github.com/samyakg051-creator/Ripple_Effect on share.streamlit.io
```

---

## 9. Risk & Mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| Agmarknet API down | Medium | Pre-download CSV as fallback |
| Open-Meteo slow | Low | Cache last response for 1 hour |
| Wrong crop name input | High | Dropdown selector, not free text |
| Model inaccuracy | Medium | Show confidence score + caveat |
| Mobile layout broken | Medium | Test on 360px width early |
