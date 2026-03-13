from typing import List, Optional
from datetime import timedelta
from rich.console import Console

from core.models import LapData, ComparisonResult, SessionData

console = Console()


def compare_laps(lap1: LapData, lap2: LapData) -> Optional[ComparisonResult]:    

    if lap2.lap_time is None or lap1.lap_time is None:
        return None
    
    lap_time_delta = lap2.lap_time - lap1.lap_time

    sector_deltas = {}
    if lap2.sector1 is not None and lap1.sector1 is not None:
        sector_deltas[1] = lap2.sector1 - lap1.sector1

    if lap2.sector2 is not None and lap1.sector2 is not None:
        sector_deltas[2] = lap2.sector2 - lap1.sector2
    
    if lap2.sector3 is not None and lap1.sector3 is not None:         
        sector_deltas[3] = lap2.sector3 - lap1.sector3
    
    best_sector = 1
    max_delta = timedelta(0)

    for sec_nums, delta in sector_deltas.items():
        if delta > max_delta:
            max_delta = delta
            best_sector = sec_nums
    
    improvement_areas = []
    for sec_nums in [1, 2, 3]:
        if sec_nums in sector_deltas and sector_deltas[sec_nums] > timedelta(microseconds=25):
            improvement_areas.append(f"Sectors to improve: {sec_nums}: {sector_deltas[sec_nums]}") 

    if lap1.speed_st is not None and lap2.speed_st is not None:
        speed_diff = lap2.speed_st - lap1.speed_st
        if speed_diff < -5:  
            improvement_areas.append(f"Speed Trap: {speed_diff:.1f} km/h") 

    return ComparisonResult(
        driver1=lap1.driver,
        driver2=lap2.driver,
        lap_time_delta=lap_time_delta,
        sector_deltas=sector_deltas,
        best_sector=best_sector,
        improvement_areas=improvement_areas if improvement_areas else ["Comparable pace"]
    )


def find_best_lap_per_driver(session_data: SessionData) -> dict:
    
    best_laps = {}
    
    for driver in session_data.drivers:
        driver_laps = [lap for lap in session_data.laps if lap.driver == driver]
        valid_laps = [lap for lap in driver_laps if lap.lap_time is not None]
        
        if valid_laps:
            best_lap = min(valid_laps, key=lambda lap: lap.lap_time or timedelta.max)
            best_laps[driver] = best_lap

    return best_laps


def find_fastest_sector(session_data: SessionData, sector: int) -> dict:
    
    if sector not in [1, 2, 3]:
        console.print("[red]Invalid sector. Use 1, 2, or 3[/red]")
        return {}
    
    sector_times = {}
    
    sector_field = f"sector{sector}"
    
    for lap in session_data.laps:
        sector_time = getattr(lap, sector_field, None)
        
        if sector_time is not None:
            driver = lap.driver
            
            if driver not in sector_times:
                sector_times[driver] = sector_time
            elif sector_time < sector_times[driver]:
                sector_times[driver] = sector_time
    
    return sector_times

"""
This function was the first try/comparison of the tyre degradation. I wanted to prove, that there are too many
factors for making the parrel between tyre degradation and actually lap performance. The test results from 
test_analysis.py proves, that the tyre lifecycle doesn't just prove lap time. Thats why I wanted to implemented
the actual tyre degragation (in features/tyre_degradation)
"""
def analyze_tyre_degradation(driver: str, session_data: SessionData, compound: Optional[str] = None) -> dict:

    driver_laps = [lap for lap in session_data.laps if lap.driver == driver]
    
    if compound:
        driver_laps = [lap for lap in driver_laps if lap.tyre_compound == compound]
    
    valid_laps = [lap for lap in driver_laps if lap.lap_time is not None]
    
    valid_laps.sort(key=lambda lap: lap.lap_number)
    
    degradation = {
        int(lap.lap_number): lap.lap_time.total_seconds() 
        for lap in valid_laps
        if lap.lap_time is not None
    }
    
    return degradation
