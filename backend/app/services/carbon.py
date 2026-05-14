"""Carbon footprint calculation service.

Formula (MVP — simplified but grounded):
  co2_saved_kg = weight_kg * distance_km * (standard_factor - consolidated_factor)

Standard delivery: 0.0002 kg CO₂ per kg·km
Consolidated delivery: 0.00008 kg CO₂ per kg·km  (shared route, ~60% less)
"""

# kg CO₂ per kg-payload per km
STANDARD_EMISSION_FACTOR = 0.0002
CONSOLIDATED_EMISSION_FACTOR = 0.00008

# Rough km distances from major hubs to each region code
REGION_DISTANCE_KM: dict[str, float] = {
    "IST": 50.0,    # within Istanbul
    "ANK": 450.0,   # Istanbul → Ankara
    "IZM": 480.0,   # Istanbul → İzmir
    "BRS": 250.0,   # Istanbul → Bursa
    "ADN": 920.0,   # Istanbul → Adana
    "TRB": 1100.0,  # Istanbul → Trabzon
}
DEFAULT_DISTANCE_KM = 400.0

# Tree absorption: avg tree absorbs ~21 kg CO₂/year → ~0.058 kg/day
CO2_PER_TREE_PER_MONTH = 1.75  # kg


def get_distance(region_code: str) -> float:
    return REGION_DISTANCE_KM.get(region_code, DEFAULT_DISTANCE_KM)


def calculate_co2_saved(total_weight_kg: float, distance_km: float) -> float:
    standard = total_weight_kg * distance_km * STANDARD_EMISSION_FACTOR
    consolidated = total_weight_kg * distance_km * CONSOLIDATED_EMISSION_FACTOR
    return round(max(standard - consolidated, 0.0), 3)


def trees_equivalent(co2_kg: float) -> str:
    months = co2_kg / CO2_PER_TREE_PER_MONTH
    if months < 1:
        days = round(months * 30)
        return f"bir ağacın {days} günde temizlediği havaya eşdeğer"
    return f"bir ağacın {round(months, 1)} ayda temizlediği havaya eşdeğer"
