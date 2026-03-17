def compute_risk_score(water_area_km2, ndci_mean, ndvi_mean, rainfall_mm):
    score = 0
    reasons = []

    if water_area_km2 is not None and water_area_km2 < 20000:
        score += 1
        reasons.append("Reduced water extent")

    if ndci_mean is not None and ndci_mean > 0.1:
        score += 1
        reasons.append("Elevated algae/chlorophyll proxy")

    if ndvi_mean is not None and ndvi_mean < 0.3:
        score += 1
        reasons.append("Low surrounding vegetation condition")

    if rainfall_mm is not None and rainfall_mm > 300:
        score += 1
        reasons.append("High rainfall and possible runoff pressure")

    if score <= 1:
        label = "Stable"
    elif score <= 3:
        label = "Watch"
    else:
        label = "High Concern"

    return score, label, reasons