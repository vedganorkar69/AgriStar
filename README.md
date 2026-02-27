# 🌾 AgriStar — AgriChain Smart Farming Platform

An AI-powered decision support system for Indian farmers built with Streamlit.

## 🚀 Features

| Page | What it does |
|---|---|
| 🌾 Harvest Window | Optimal 5-day harvest timing via weather + price seasonality |
| 🏪 Mandi Ranker | Top 3 markets ranked by net profit after transport cost |
| ⚠️ Spoilage Assessor | Post-harvest spoilage risk + ranked preservation actions |
| 🤖 AI Assistant | AgriBot — Hinglish/Marathi/English chatbot powered by Ollama |

## 🗺️ Map Features
- Interactive India map (Indian government standard — PoK & Aksai Chin shown as integral part)
- Maharashtra highlighted with district-level clickable markers
- Crop emoji markers (🍅🧅🥔🌽…) switch to Devanagari when Hindi/Marathi is selected
- Dynamic Google Translate–based Devanagari conversion (no API key needed)

## 🌐 Language Support
- English · हिंदी · मराठी
- AI chatbot understands **Hinglish / Minglish** and auto-mirrors the user's language

## 🛠️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/vedganorkar69/AgriStar.git
cd AgriStar/agrichain

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Install Ollama for AI Assistant
# https://ollama.com → then: ollama pull gemma2:2b

# 5. Run the app
python -m streamlit run app.py
```

## 📦 Tech Stack
- **Frontend**: Streamlit 1.54
- **Maps**: Folium + streamlit-folium (Leaflet.js, CartoDB Dark Matter tiles)
- **AI**: LangChain + Ollama (local LLMs — gemma2, llama3.2, mistral…)
- **Charts**: Plotly
- **Data**: Open-Meteo weather API, Agmarknet synthetic price data
- **Translation**: Free Google Translate endpoint (place names → Devanagari)

## 📁 Project Structure
```
agrichain/
├── app.py                  # Home page
├── pages/
│   ├── 1_🌾_Harvest.py
│   ├── 2_🏪_Mandi.py
│   ├── 3_⚠️_Spoilage.py
│   └── 4_🤖_AI_Assistant.py
├── modules/                # Core engines
│   ├── harvest_engine.py
│   ├── mandi_ranker.py
│   ├── spoilage_assessor.py
│   ├── data_fetcher.py
│   └── ai_assistant.py
├── utils/
│   ├── geo.py              # District coordinates
│   ├── geo_translate.py    # Google Translate Devanagari conversion
│   ├── map_selector.py     # Interactive Folium map
│   ├── shared_state.py     # Cross-page parameter sync
│   ├── green_theme.py      # Global CSS green theme
│   └── translator.py       # UI i18n (EN/HI/MR)
└── data/                   # Generated CSV (auto-created on startup)
```

## 📸 Screenshots
> Run the app and navigate to each page to see the interactive maps and AI chat.

---
Built with ❤️ for Indian farmers · Hackathon MVP
