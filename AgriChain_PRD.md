# AgriChain — Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** February 2026  
**Team:** Hackathon MVP  
**Platform:** Streamlit Web App  

---

## 1. Problem Statement

India's farmers lose up to **40% of produce** not due to poor farming — but due to:
- Wrong harvest timing
- Selling in wrong market (mandi)
- Post-harvest spoilage from poor storage & transit decisions

Farmers lack access to data-driven, personalized, explainable recommendations in their language.

---

## 2. Goal

Build an AI-powered platform that tells a farmer:
1. **When** to harvest their crop
2. **Where** to sell it (best mandi)
3. **How** to store/transport it to minimize spoilage
4. **Why** — with plain-language explanations

---

## 3. Target User

| Attribute | Detail |
|---|---|
| Who | Small & marginal farmers (0–5 acres) |
| Device | Basic Android phone / shared kiosk |
| Language | Hindi, Marathi, English |
| Data literacy | Very low — no charts, no jargon |
| Connectivity | Intermittent 2G/3G |

---

## 4. Core Features

### 4.1 Harvest Window Recommender
- **Input:** Crop name, district, sowing date
- **Data used:** Weather forecast (Open-Meteo), historical price seasonality (Agmarknet)
- **Output:** "Best harvest window: March 10–15. Prices are typically 18% higher this week."
- **Explainability:** Show top 2 reasons for recommendation

### 4.2 Market (Mandi) Selector
- **Input:** Crop, quantity, farmer's village/district
- **Data used:** Live mandi prices, distance to mandi, historical price variance
- **Output:** Top 3 mandis ranked by expected profit after transport cost
- **Explainability:** Show price difference and distance trade-off

### 4.3 Spoilage Risk Assessor
- **Input:** Crop, quantity, storage type (open/cold/warehouse), transit duration
- **Data used:** Temperature + humidity forecast, crop spoilage curves
- **Output:** Risk level (Low/Medium/High) + ranked preservation actions with cost
- **Explainability:** "High humidity forecast for next 3 days — refrigerated transport recommended"

### 4.4 Plain Language Output
- All outputs rendered in simple sentences, not tables
- Language toggle: Hindi / English (MVP scope)
- Color-coded urgency: 🟢 Green / 🟡 Yellow / 🔴 Red

---

## 5. Out of Scope (for MVP)

- Loan or insurance integration
- Farmer login / profile persistence
- Live GPS tracking of transport

---

## 6. Success Metrics

| Metric | Target |
|---|---|
| Recommendation generated in | < 5 seconds |
| Explainability shown | Every recommendation |
| Mobile usability score | Usable on 360px screen |
| Languages supported | Hindi + English |
| Data freshness | Weather: real-time, Prices: daily |

---

## 7. User Flow

```
[Farmer opens app]
        ↓
[Selects crop + enters district]
        ↓
[App fetches weather + price data]
        ↓
[Shows Harvest Window Recommendation]
        ↓
[Shows Top 3 Mandis to sell]
        ↓
[Shows Spoilage Risk + Storage Tips]
        ↓
[All in plain Hindi/English with color codes]
```

---

## 8. Constraints

- Must work on mobile browser (Streamlit responsive)
- No login required for MVP
- All API calls must complete within 5s
- Fallback to cached data if APIs are down

---

## 9. Data Sources

| Data Type | Source | Access |
|---|---|---|
| Mandi prices | Agmarknet / data.gov.in | CSV download / API |
| Weather forecast | Open-Meteo | Free REST API |
| Soil health | ISRIC SoilGrids | Free REST API |
| Distance to mandi | Google Maps API | Free tier |
| Spoilage curves | FAO open datasets | Static lookup table |

---

## 10. Timeline (24-Hour Hackathon)

| Hour | Milestone |
|---|---|
| 0–2 | Setup repo, fetch & clean Agmarknet + Open-Meteo data |
| 2–5 | Build harvest window model (price seasonality + weather) |
| 5–8 | Build mandi ranker (price + distance scoring) |
| 8–11 | Build spoilage risk module |
| 11–16 | Build Streamlit UI — all 3 modules |
| 16–20 | Hindi language output + explainability layer |
| 20–23 | Testing, polish, demo prep |
| 23–24 | Buffer / bug fixes |
