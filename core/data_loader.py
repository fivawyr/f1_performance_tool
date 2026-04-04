import os
import fastf1
from core.models import LapData, SessionData
from features.tyre_temperature import estimate_tyre_temp
from rich.console import Console
import pandas as pd

console = Console()

def load_session(year: int, event: str, session_type: str) -> SessionData:

    os.makedirs("cache", exist_ok=True)
    fastf1.Cache.enable_cache("cache/")
    
    with console.status("[cyan]Loading session...", spinner="dots"):
        session = fastf1.get_session(year, event, session_type)
        session.load(weather=True)
    
    console.print(f"[green] Session loaded: {year} {event} {session_type}[/green]")

    valid_session_laps = session.laps[
        (session.laps['IsAccurate'] == True) & 
        (session.laps['LapTime'].notna())
    ]
    
    console.print(f"[dim] Found {len(valid_session_laps)} valid laps (out of {len(session.laps)} total)[/dim]")
    
    lap_data_list = []
    for _, lap_row in valid_session_laps.iterrows():
        lap_data = get_lap_data_from_row(lap_row)
        lap_data_list.append(lap_data)
    
    # Extract unique driver CODES from laps (not driver numbers)
    drivers = sorted(list(set([lap.driver for lap in lap_data_list])))
    
    return SessionData(
        year=year,
        event=event,
        session_type=session_type,
        laps=lap_data_list,
        drivers=drivers
    )


def get_lap_data_from_row(lap_row) -> LapData:

    # this isna statements reduces time for validate the data (delete Nat, NaN) -> for delta calc
    lap_time = lap_row['LapTime'] if not pd.isna(lap_row['LapTime']) else None
    sector1 = lap_row['Sector1Time'] if not pd.isna(lap_row['Sector1Time']) else None
    sector2 = lap_row['Sector2Time'] if not pd.isna(lap_row['Sector2Time']) else None
    sector3 = lap_row['Sector3Time'] if not pd.isna(lap_row['Sector3Time']) else None
    speed_i1 = lap_row['SpeedI1'] if not pd.isna(lap_row['SpeedI1']) else None
    speed_i2 = lap_row['SpeedI2'] if not pd.isna(lap_row['SpeedI2']) else None
    speed_fl = lap_row['SpeedFL'] if not pd.isna(lap_row['SpeedFL']) else None
    speed_st = lap_row['SpeedST'] if not pd.isna(lap_row['SpeedST']) else None 
    weather = lap_row.get_weather_data()
    track_temp = float(weather['TrackTemp'].mean()) if not weather.empty else 30.0
    air_temp = float(weather['AirTemp'].mean()) if not weather.empty else 20.0
    wind_speed = float(weather['WindSpeed'].mean()) if not weather.empty else 0.0
    rainfall = bool(weather['Rainfall'].any()) if not weather.empty else False

    avg_speed = float(speed_st) if speed_st is not None else 180.0

    tyre_age = int(lap_row['TyreLife'])
    compound = lap_row['Compound']

    tyre_temps = estimate_tyre_temp(
        track_temp=track_temp,
        air_temp=air_temp,
        speed=avg_speed,
        compound=compound,
        tyre_age=tyre_age,
        wind_speed=wind_speed,
        rainfall=rainfall,
        fresh_tyre=(tyre_age <= 1),
    )

    return LapData(
        driver=lap_row['Driver'],
        lap_number=int(lap_row['LapNumber']),
        lap_time=lap_time,
        sector1=sector1,
        sector2=sector2,
        sector3=sector3,
        speed_i1=speed_i1,
        speed_i2=speed_i2,
        speed_fl=speed_fl,
        speed_st=speed_st,
        tyre_age=int(lap_row['TyreLife']),
        tyre_compound=lap_row['Compound'],
        is_personal_best=lap_row['IsPersonalBest'],
        is_accurate=lap_row['IsAccurate'],
        stint=int(lap_row['Stint']),
        # Telemetry lazy-loaded: not loaded by default (None)
        throttle_trace=None,
        brake_trace=None,
        speed_trace=None,
        position_data=None,
        estimated_surface_temp=tyre_temps["surface_temp"],
        estimated_core_temp=tyre_temps["core_temp"],
        tyre_in_optimal_window=tyre_temps["in_optimal_window"],
    )


