from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, List

@dataclass # telemetry for one lap, important for tyre_degradation
class LapData:
    driver: str
    lap_number: int
    lap_time: Optional[timedelta]
    sector1: Optional[timedelta]
    sector2: Optional[timedelta]
    sector3: Optional[timedelta]
    speed_i1: Optional[float]            
    speed_i2: Optional[float]           
    speed_fl: Optional[float]           
    speed_st: Optional[float]           
    tyre_age: int
    tyre_compound: str                
    is_personal_best: bool
    is_accurate: bool                   
    stint: int                         
    throttle_trace: Optional[List[float]] = None
    brake_trace: Optional[List[float]] = None
    speed_trace: Optional[List[float]] = None
    position_data: Optional[tuple] = None  
    # we dont get fuel_loads from fastf1, so I need to calculate it on data_processing 
    estimated_surface_temp: Optional[float] = None
    estimated_core_temp: Optional[float] = None
    tyre_in_optimal_window: Optional[bool] = None
    
@dataclass
class SessionData:
    year: int
    event: str                         
    session_type: str                   
    laps: List[LapData]
    drivers: List[str]                 
    
@dataclass
class ComparisonResult: 
    driver1: str
    driver2: str
    lap_time_delta: timedelta           
    sector_deltas: dict                 
    best_sector: int                   
    improvement_areas: List[str]       