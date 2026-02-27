# AgriChain 🌾

**AI-powered farming decisions for Indian farmers**

AgriChain helps small & marginal farmers make smarter decisions about:
- **When** to harvest (Harvest Window Recommender)
- **Where** to sell (Mandi Ranker)
- **How** to preserve produce (Spoilage Assessor)

---

## Quick Start

```bash
cd agrichain
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Stack
- **Frontend:** Streamlit + Plotly
- **Backend:** Python · Pandas · NumPy · Scikit-learn
- **APIs:** Open-Meteo (weather, free, no key)
- **Price Data:** Synthetic Agmarknet CSV (auto-generated)

## Pages
| Page | Description |
|---|---|
| 🏠 Home | Weather snapshot + feature overview |
| 🌾 Harvest Window | Best harvest date using price + weather scoring |
| 🏪 Mandi Ranker | Top 3 markets by net profit after transport |
| ⚠️ Spoilage Assessor | Risk score + ranked preservation actions |
