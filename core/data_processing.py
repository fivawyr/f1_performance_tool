import numpy as np
from typing import List
from core.models import LapData
from features.tyre_temperature import estimate_tyre_temp

FUEL_START_KG = 110.0
FUEL_PER_LAP_KG = 1.8
FUEL_EFFECT_PER_KG = 0.03
TRAFFIC_THRESHOLD = 0.02

def add_tyre_temps(laps: List[LapData], weather_per_lap: List[dict]) -> List[LapData]:
    for lap, weather in zip(laps, weather_per_lap):
        avg_speed = np.mean(lap.speed_trace) if lap.speed_trace else 180.0
        result = estimate_tyre_temp(
            track_temp=float(weather.get("TrackTemp", 30)),
            air_temp=float(weather.get("AirTemp", 20)),
            speed_kmh=avg_speed,
            compound=lap.tyre_compound,
            tyre_age=lap.tyre_age,
            wind_speed=float(weather.get("WindSpeed", 0)),
            rainfall=bool(weather.get("Rainfall", False)),
            fresh_tyre=(lap.tyre_age <= 1),
        )
        lap.estimated_surface_temp = result["surface_temp"]
        lap.estimated_core_temp = result["core_temp"]
        lap.tyre_in_optimal_window = result["in_optimal_window"]
    return laps

def filter_stint(laps: List[LapData]) -> List[LapData]:
    return laps[1:-1]


def filter_high_traffic(laps: List[LapData]) -> List[LapData]:
    times = [lap.lap_time.total_seconds() for lap in laps]
    median = np.median(times)
    return [lap for lap in laps if lap.lap_time.total_seconds() <= median * (1 + TRAFFIC_THRESHOLD)]


def get_times_ms(laps: List[LapData]) -> np.ndarray:
    return np.array([lap.lap_time.total_seconds() * 1000 for lap in laps])


def estimate_fuel_loads(laps: List[LapData]) -> np.ndarray:
    return np.array([FUEL_START_KG - (lap.tyre_age * FUEL_PER_LAP_KG) for lap in laps])


def fuel_correction(times_ms: np.ndarray, fuel_loads: np.ndarray) -> np.ndarray:
    fuel_delta = (fuel_loads - fuel_loads.min()) * FUEL_EFFECT_PER_KG
    return times_ms - fuel_delta


def preprocess_stint(laps: List[LapData]) -> np.ndarray:
    laps = filter_stint(laps)
    laps = filter_high_traffic(laps)

    times_ms = get_times_ms(laps)
    fuel_loads = estimate_fuel_loads(laps)
    times_ms = fuel_correction(times_ms, fuel_loads)

    return times_ms