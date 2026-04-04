# for detailed explaination, checkout the Markdown (cf. features/tyre_temperature_modell.md)

import math

# min and max temp for optimal tyre grip (cf. pirellis website, linked at the markdown)
COMPOUND_TEMP_LIST = {
    "SOFT": {"friction": 1.25, "min_temp": 85, "max_temp": 105},
    "MEDIUM": {"friction": 1.00, "min_temp": 90, "max_temp": 115},
    "HARD": {"friction": 0.85, "min_temp": 100, "max_temp": 125},
    "INTERMEDIATE": {"friction": 0.70, "min_temp": 50, "max_temp": 90},
    "WET": {"friction": 0.55, "min_temp": 30, "max_temp": 70},
}

# we separate calc logic from f1 logic. I do this, because I want to use those modells not 
# only for calculate f1 tyres, but also with other series in a future project (LMP!)
def estimate_tyre_temp(track_temp, air_temp, speed, compound = "MEDIUM" ,tyre_age=10,
                        fresh_tyre=False, wind_speed=0.0, rainfall=False):
    
    compound = compound.upper()
    if compound not in COMPOUND_TEMP_LIST:
        compound = "MEDIUM"
    cfg = COMPOUND_TEMP_LIST[compound]

    q_road = 12.0 * (track_temp - air_temp) * 0.10
    v = max(speed, 0.0) / 200.0

    q_friction = 38 * (v ** 1.6) * cfg["friction"]
    f_age = 1.0 + 0.008 * min(tyre_age, 20) - 0.003 * max(0, tyre_age - 20)
    
    if fresh_tyre and tyre_age <= 2:
        f_age *= 0.80
    q_friction = 38 * (v ** 1.6) * cfg["friction"] * f_age # just the calc for the Q_friction  

    v_air = speed / 3.6 + max(wind_speed, 0.0)
    # At 50 m/s, the air does not cool twice as effectively as at 25 m/s, but only about 1.4 times as effectively 
    # (`sqrt(2) ≈ 1.41`), hence the square root of (v_air)
    h_conv = 25 + 6.3 * math.sqrt(v_air)
    # 0.05 is the estimated tyre surface area (based on research). However, it is certainly a factor in the calculation that is open to criticism
    q_conv = h_conv * 0.05

    if rainfall:  
        q_rain = 8.0 if compound in ("WET", "INTERMEDIATE") else 35.0
    else:
        q_rain = 0.0

    calc_all_terms_together = q_road + q_friction - q_conv - q_rain
    surface_temp = air_temp + 8.0 + calc_all_terms_together

    surface_temp = max(air_temp + 5.0, min(125.0, surface_temp))
    core_temp = surface_temp - 12.0 - (5.0 if rainfall else 0.0)
    core_temp = max(air_temp + 2.0, min(110.0, core_temp))

    in_window = cfg["min_temp"] <= surface_temp <= cfg["max_temp"]

    return {
        "surface_temp": round(surface_temp, 1),
        "core_temp": round(core_temp, 1),
        "in_optimal_window": in_window,
        "optimal_window": (cfg["min_temp"], cfg["max_temp"]),
    }


def get_tyre_temps_for_lap(lap, weather):
    return estimate_tyre_temp(
        track_temp=float(weather.get("TrackTemp", 30)),
        air_temp=float(weather.get("AirTemp", 20)),
        speed_kmh=float(weather.get("avg_speed_kmh", 180)),
        compound=lap.tyre_compound,
        tyre_age=lap.tyre_age,
        wind_speed=float(weather.get("WindSpeed", 0)),
        rainfall=bool(weather.get("Rainfall", False)),
        fresh_tyre=(lap.tyre_age <= 1),
    )

if __name__ == "__main__":
    tests = [
        ("hot SOFT",      dict(track_temp=45, air_temp=30, speed_kmh=220, compound="SOFT",   tyre_age=5,  wind_speed=2, rainfall=False)),
        ("normal MEDIUM",   dict(track_temp=35, air_temp=22, speed_kmh=190, compound="MEDIUM", tyre_age=25, wind_speed=4, rainfall=False)),
        ("rain WET",       dict(track_temp=20, air_temp=15, speed_kmh=160, compound="WET",    tyre_age=3,  wind_speed=6, rainfall=True)),
        ("extrem HARD alt", dict(track_temp=55, air_temp=38, speed_kmh=240, compound="HARD",   tyre_age=40, wind_speed=1, rainfall=False)),
    ]
    for label, params in tests:
        r = estimate_tyre_temp(**params)
        w = f"{r['optimal_window'][0]} - {r['optimal_window'][1]}°C"
        is_r_in_optmal_window = "Yes its in the optimal window" if r["in_optimal_window"] else "it's not in the optimal window" 
        print(f"{label}: {r['surface_temp']}°C ({w}) - {is_r_in_optmal_window}")
