# AgriChain — Tech Stack Reference

**For:** 24-Hour Hackathon MVP  
**Philosophy:** Minimal setup. Maximum output. Zero surprises.

---

## 🏗️ Full Stack at a Glance

```
┌──────────────────────────────────────────┐
│           FRONTEND + BACKEND             │
│              Streamlit                   │
│         (Python all the way)             │
└──────────────────┬───────────────────────┘
                   │
     ┌─────────────┼──────────────┐
     ▼             ▼              ▼
 Pandas +      Scikit-learn    Requests
 NumPy         (Scoring)       (APIs)
 (Data)
     │             │              │
     ▼             ▼              ▼
Agmarknet      Rule-based     Open-Meteo
  CSV          + ML scoring   (Weather)
```

---

## 🧰 Layer-by-Layer Stack

### 🖥️ Frontend
| Tool | Version | Purpose |
|---|---|---|
| **Streamlit** | 1.32+ | Entire UI — no HTML/CSS needed |
| **Plotly Express** | 5.18+ | Price trend charts |
| **st.columns / st.metric** | built-in | Mobile-friendly layout |

> **Why Streamlit?** Write Python → get a web app. No frontend dev needed. Deploys free on Streamlit Cloud in 2 minutes.

---

### ⚙️ Backend / Logic
| Tool | Version | Purpose |
|---|---|---|
| **Python** | 3.11 | Core language |
| **Pandas** | 2.2 | CSV loading, price aggregation |
| **NumPy** | 1.26 | Scoring calculations |
| **Scikit-learn** | 1.4 | MinMaxScaler for score normalization |
| **Requests** | 2.31 | API calls (weather, soil) |

---

### 🌐 External APIs
| API | Cost | Key Required | What We Use It For |
|---|---|---|---|
| **Open-Meteo** | Free | ❌ None | 14-day weather forecast (temp, humidity, rain) |
| **ISRIC SoilGrids** | Free | ❌ None | Soil properties by lat/lon |
| **Agmarknet** | Free | ❌ None | Historical mandi prices (CSV download) |
| **data.gov.in** | Free | ✅ Free signup | Backup price data |

> ⭐ **Open-Meteo is the MVP hero API** — no signup, returns JSON, handles Indian coordinates perfectly.

---

### 🗃️ Data Storage
| What | How |
|---|---|
| Mandi price history | Local CSV (`data/agmarknet_prices.csv`) |
| District coordinates | Python dict (hardcoded, ~50 districts) |
| Crop spoilage parameters | Python dict (lookup table) |
| Weather cache | `st.cache_data` with 1-hour TTL |
| User session state | `st.session_state` (in-memory) |

> **No database needed for MVP.** Everything fits in CSVs + Python dicts.

---

### 🚀 Deployment
| Option | Time to Deploy | Cost | Recommended |
|---|---|---|---|
| **Streamlit Cloud** | 2 minutes | Free | ✅ Yes |
| Railway.app | 5 minutes | Free tier | Backup |
| Localhost | 0 minutes | Free | For demo |

**Deploy to Streamlit Cloud:**
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to share.streamlit.io
# 3. Connect repo → Done ✅
```

---

## 📁 Project Structure

```
agrichain/
│
├── app.py                    # Main entry point
│
├── pages/
│   ├── 1_🌾_Harvest.py       # Harvest window page
│   ├── 2_🏪_Mandi.py         # Market ranker page
│   └── 3_⚠️_Spoilage.py      # Spoilage risk page
│
├── modules/
│   ├── harvest_engine.py     # Harvest scoring logic
│   ├── mandi_ranker.py       # Market ranking logic
│   ├── spoilage_assessor.py  # Spoilage risk logic
│   └── data_fetcher.py       # API calls + caching
│
├── data/
│   └── agmarknet_prices.csv  # Pre-downloaded price data
│
├── utils/
│   ├── translator.py         # Hindi/English toggle
│   ├── explainer.py          # Plain-language reasons
│   └── geo.py                # Haversine distance calc
│
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start (Copy-Paste Ready)

```bash
# 1. Setup
mkdir agrichain && cd agrichain
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install
pip install streamlit pandas numpy requests scikit-learn plotly

# 3. Run
streamlit run app.py
```

---

## 📦 requirements.txt

```
streamlit==1.32.0
pandas==2.2.0
numpy==1.26.0
requests==2.31.0
scikit-learn==1.4.0
plotly==5.18.0
```

---

## 🔌 Key API Calls (Ready to Use)

### Weather (Open-Meteo) — No API key needed
```python
import requests

def get_weather(lat: float, lon: float, days: int = 14) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min", 
            "precipitation_sum",
            "relative_humidity_2m_max"
        ],
        "forecast_days": days,
        "timezone": "Asia/Kolkata"
    }
    r = requests.get(url, params=params)
    return r.json()["daily"]
```

### Mandi Prices (Agmarknet CSV)
```python
import pandas as pd

def get_mandi_prices(crop: str, state: str = "Maharashtra") -> pd.DataFrame:
    df = pd.read_csv("data/agmarknet_prices.csv")
    mask = (
        (df["Commodity"].str.lower() == crop.lower()) & 
        (df["State"] == state)
    )
    df = df[mask].copy()
    df["Date"] = pd.to_datetime(df["Arrival_Date"], dayfirst=True)
    return df.sort_values("Date").tail(90)  # Last 90 days
```

### Distance (Haversine — No API key)
```python
import math

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

---

## 🎨 Streamlit UI Patterns

### Mobile-friendly metric cards
```python
col1, col2, col3 = st.columns(3)
col1.metric("Best Mandi", "Pune APMC", "₹2,450/qtl")
col2.metric("Transport Cost", "₹180", "-8%")
col3.metric("Net Profit", "₹2,270/qtl", "+12%")
```

### Color-coded risk badge
```python
risk = "HIGH"
color_map = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
st.markdown(f"## Spoilage Risk: {color_map[risk]} {risk}")
```

### Explainability box
```python
with st.expander("🤔 Why this recommendation?"):
    st.write("✅ Mandi prices are 18% higher this week historically")
    st.write("✅ Low humidity forecast — safe for transport")
```

### Language toggle
```python
lang = st.sidebar.radio("भाषा / Language", ["English", "हिंदी"])
```

---

## ⚠️ Things to Avoid (Saves You 4 Hours)

| Don't | Do Instead |
|---|---|
| Free-text crop input | Dropdown with 20 common crops |
| Real-time Agmarknet scraping | Pre-download CSV the night before |
| Google Maps API (needs billing) | Haversine formula |
| Complex ML model training | Weighted scoring (interpretable + fast) |
| Multiple pages from scratch | Streamlit multipage (`pages/` folder) |
| Custom CSS mobile layout | `st.columns()` — already responsive |
