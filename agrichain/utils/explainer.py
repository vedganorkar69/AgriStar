def explain_harvest(score_components: dict, crop: str, days_since_sowing: int) -> list:
    """Return up to 2 plain-language reasons for the harvest recommendation."""
    reasons = []

    price = score_components.get("price_seasonality", 0)
    weather = score_components.get("weather", 0)
    soil = score_components.get("soil_readiness", 0)

    if price >= 0.6:
        pct = int(price * 25)
        reasons.append(f"Mandi prices are historically {pct}–{pct+5}% higher this week for {crop}")
    elif price >= 0.4:
        reasons.append(f"Mandi prices are moderately good this week for {crop}")
    else:
        reasons.append(f"Prices are currently below average — consider waiting a few days")

    if weather >= 0.6:
        reasons.append("Weather forecast shows dry conditions — ideal for harvest & transport")
    elif weather >= 0.4:
        reasons.append("Weather is acceptable; moderate humidity expected over the next week")
    else:
        reasons.append("High humidity or rainfall forecast — risk of field spoilage if delayed")

    if len(reasons) < 2 and soil >= 0.7:
        reasons.append(f"Crop is fully mature at {days_since_sowing} days since sowing — optimal readiness")

    return reasons[:2]


def explain_mandi(mandi_name: str, avg_price: float, transport: float, net: float, distance_km: float) -> str:
    """Return a plain-language reason for recommending a mandi."""
    if net > 2200:
        return f"Top choice — highest net return at ₹{net:,.0f}/qtl despite ₹{transport:,.0f} transport"
    elif distance_km < 60:
        return f"Nearby market ({distance_km:.0f} km away) with competitive price of ₹{avg_price:,.0f}/qtl"
    else:
        return f"Good price ₹{avg_price:,.0f}/qtl; transport cost of ₹{transport:,.0f} is manageable"


def explain_spoilage(risk_level: str, crop: str, humidity: float, temp: float, storage_type: str) -> str:
    """Return a plain-language reason for the spoilage risk level."""
    if risk_level == "HIGH":
        if humidity > 75:
            return f"3-day humidity forecast is {humidity:.0f}%+ — very high spoilage risk for {crop}"
        elif temp > 32:
            return f"Temperature forecast exceeds {temp:.0f}°C — rapid spoilage expected for {crop}"
        else:
            return f"Open storage + high transit time creates high spoilage risk for {crop}"
    elif risk_level == "MEDIUM":
        return f"Moderate humidity ({humidity:.0f}%) and {storage_type.lower()} storage pose manageable risk for {crop}"
    else:
        return f"Low humidity ({humidity:.0f}%) and controlled storage keep spoilage risk low for {crop}"
