import math

# ─── District coordinates (Maharashtra) ────────────────────────────────────────
DISTRICT_COORDS = {
    "Pune":         (18.5204, 73.8567),
    "Nashik":       (19.9975, 73.7898),
    "Nagpur":       (21.1458, 79.0882),
    "Solapur":      (17.6868, 75.9064),
    "Aurangabad":   (19.8762, 75.3433),
    "Kolhapur":     (16.7050, 74.2433),
    "Amravati":     (20.9320, 77.7769),
    "Sangli":       (16.8524, 74.5815),
    "Satara":       (17.6805, 74.0183),
    "Latur":        (18.4088, 76.5604),
    "Osmanabad":    (18.1860, 76.0419),
    "Nanded":       (19.1383, 77.3210),
    "Jalgaon":      (21.0077, 75.5626),
    "Dhule":        (20.9042, 74.7749),
    "Raigad":       (18.5158, 73.1812),
    "Ratnagiri":    (16.9902, 73.3120),
    "Sindhudurg":   (16.3491, 73.8552),
    "Palghar":      (19.6967, 72.7697),
    "Thane":        (19.2183, 72.9781),
    "Mumbai":       (19.0760, 72.8777),
    "Ahmednagar":   (19.0952, 74.7496),
    "Beed":         (18.9891, 75.7601),
    "Hingoli":      (19.7173, 77.1490),
    "Jalna":        (19.8347, 75.8816),
    "Parbhani":     (19.2704, 76.7766),
    "Akola":        (20.7002, 77.0082),
    "Buldhana":     (20.5292, 76.1842),
    "Washim":       (20.1119, 77.1431),
    "Yavatmal":     (20.3888, 78.1204),
    "Gondiya":      (21.4605, 80.1952),
}

# ─── Mandi (APMC market) coordinates ──────────────────────────────────────────
MANDI_COORDS = {
    "Pune APMC":       (18.5196, 73.8553),
    "Nashik APMC":     (19.9750, 73.7578),
    "Nagpur APMC":     (21.1220, 79.0748),
    "Solapur APMC":    (17.6930, 75.9012),
    "Kolhapur APMC":   (16.7009, 74.2433),
    "Aurangabad APMC": (19.8680, 75.3320),
    "Mumbai APMC":     (19.0596, 72.8295),
    "Sangli APMC":     (16.8561, 74.5610),
}

# ─── Transport cost per km per quintal (₹) ────────────────────────────────────
TRANSPORT_COST_PER_KM_PER_QTL = 4.0   # ₹4/km/quintal

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance between two lat/lon points in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def transport_cost(farmer_district: str, mandi_name: str, quantity_qtl: float) -> float:
    """Estimated transport cost in ₹ for a given quantity."""
    if farmer_district not in DISTRICT_COORDS or mandi_name not in MANDI_COORDS:
        return 0.0
    lat1, lon1 = DISTRICT_COORDS[farmer_district]
    lat2, lon2 = MANDI_COORDS[mandi_name]
    dist = haversine_km(lat1, lon1, lat2, lon2)
    return round(dist * TRANSPORT_COST_PER_KM_PER_QTL * quantity_qtl, 2)


def distance_to_mandi(farmer_district: str, mandi_name: str) -> float:
    """Distance in km from district to mandi."""
    if farmer_district not in DISTRICT_COORDS or mandi_name not in MANDI_COORDS:
        return 0.0
    lat1, lon1 = DISTRICT_COORDS[farmer_district]
    lat2, lon2 = MANDI_COORDS[mandi_name]
    return round(haversine_km(lat1, lon1, lat2, lon2), 1)
