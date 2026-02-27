import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_fetcher import load_mandi_prices
from utils.geo import MANDI_COORDS, DISTRICT_COORDS, haversine_km, TRANSPORT_COST_PER_KM_PER_QTL
from utils.explainer import explain_mandi

MANDIS = list(MANDI_COORDS.keys())


def _avg_mandi_price(df, mandi_name: str, days: int = 7) -> float:
    """Compute the rolling average Modal_Price for a mandi over the last N days."""
    mandi_df = df[df["Market"] == mandi_name].copy()
    if mandi_df.empty:
        return 0.0
    mandi_df = mandi_df.sort_values("Date")
    last = mandi_df.tail(days)
    return float(last["Modal_Price"].mean())


def rank_mandis(
    crop: str,
    quantity_qtl: float,
    farmer_district: str,
    top_n: int = 3,
) -> list:
    """
    Rank mandis by net profit per quintal.
    Returns a list of dicts, sorted by net_profit_per_qtl descending.
    """
    df = load_mandi_prices(crop)

    if farmer_district not in DISTRICT_COORDS:
        farmer_district = "Pune"

    f_lat, f_lon = DISTRICT_COORDS[farmer_district]

    results = []
    for mandi in MANDIS:
        avg_price = _avg_mandi_price(df, mandi, days=7)
        if avg_price == 0:
            # Use base estimate from price table if CSV has no data
            avg_price = 1800

        m_lat, m_lon = MANDI_COORDS[mandi]
        dist = haversine_km(f_lat, f_lon, m_lat, m_lon)

        # Transport cost per quintal
        cost_per_qtl = round(dist * TRANSPORT_COST_PER_KM_PER_QTL, 2)
        net_profit   = round(avg_price - cost_per_qtl, 2)

        reason = explain_mandi(mandi, avg_price, cost_per_qtl, net_profit, dist)

        results.append({
            "mandi":              mandi,
            "expected_price":     round(avg_price, 0),
            "transport_cost_qtl": round(cost_per_qtl, 0),
            "net_profit_per_qtl": round(net_profit, 0),
            "total_transport":    round(cost_per_qtl * quantity_qtl, 0),
            "distance_km":        round(dist, 1),
            "reason":             reason,
        })

    results.sort(key=lambda x: x["net_profit_per_qtl"], reverse=True)
    return results[:top_n]
