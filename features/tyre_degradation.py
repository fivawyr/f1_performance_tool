import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import numpy as np
from scipy import stats


@dataclass
class vehicle_parameters:
    mass_kg: float = 768.0
    CL: float = 3.5
    CD: float = 0.9
    aero_area: float = 5.0
    rho_air: float = 1.225
    pacejka_B: float = 1.0
    pacejka_C: float = 1.3
    pacejka_D: float = 1.0
    pacejka_E: float = 0.97
    mu_x: float = 1.5
    mu_y: float = 1.5
    power_max_kw: float = 760.0
    brake_force_max: float = 34000.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "vehicle_parameters":
        return cls(**data)


@dataclass
class AnalysisKey:
    driver: str
    compound: str
    stint: int

    def __hash__(self):
        return hash((self.driver, self.compound, self.stint))


@dataclass
class TireDegradationResult:
    key: AnalysisKey
    num_laps: int
    baseline_time_ms: float
    degradation_rate_ms_per_lap: float
    r_squared: float
    estimated_tyre_life_laps: int

    def to_dict(self) -> dict:
        return {
            "driver": self.key.driver,
            "compound": self.key.compound,
            "stint": self.key.stint,
            "num_laps": self.num_laps,
            "baseline_time_ms": self.baseline_time_ms,
            "degradation_rate_ms_per_lap": self.degradation_rate_ms_per_lap,
            "r_squared": self.r_squared,
            "estimated_tyre_life_laps": self.estimated_tyre_life_laps,
        }


class TireDegradationAnalyzer:
    def __init__(self, vehicle_params: Optional[vehicle_parameters] = None):
        self.vehicle_params = vehicle_params or vehicle_parameters()
        self.results: List[TireDegradationResult] = []

    def analyze_stint(
        self,
        laps: List,
        driver: str,
        compound: str,
        stint: int,
    ) -> Optional[TireDegradationResult]:
        if not laps or len(laps) < 2:
            return None

        times_ms = np.array(
            [lap.lap_time.total_seconds() * 1000 for lap in laps]
        )
        lap_nums = np.arange(1, len(laps) + 1)

        result = stats.linregress(lap_nums, times_ms)
        slope = result.slope
        intercept = result.intercept
        r_value = result.rvalue

        baseline_time = intercept
        degradation_rate = slope
        r_squared = r_value**2

        laps_until_limit = 999
        if degradation_rate > 0:
            laps_until_limit = int(2000.0 / degradation_rate)

        key = AnalysisKey(driver, compound, stint)
        result = TireDegradationResult(
            key=key,
            num_laps=len(laps),
            baseline_time_ms=baseline_time,
            degradation_rate_ms_per_lap=degradation_rate,
            r_squared=r_squared,
            estimated_tyre_life_laps=laps_until_limit,
        )

        self.results.append(result)
        return result

    def export_json(
        self, session_data, output_file: str = "cpp/ipc/tire_data_in.json"
    ) -> None:
        laps_data = []
        for lap in session_data.laps:
            if lap.lap_time is None:
                continue

            laps_data.append({
                "driver": lap.driver,
                "lap_number": int(lap.lap_number),
                "lap_time_ms": lap.lap_time.total_seconds() * 1000,
                "sector1_ms": lap.sector1.total_seconds() * 1000
                if lap.sector1
                else None,
                "sector2_ms": lap.sector2.total_seconds() * 1000
                if lap.sector2
                else None,
                "sector3_ms": lap.sector3.total_seconds() * 1000
                if lap.sector3
                else None,
                "speed_i1": lap.speed_i1,
                "speed_i2": lap.speed_i2,
                "speed_fl": lap.speed_fl,
                "speed_st": lap.speed_st,
                "compound": lap.tyre_compound,
                "tyre_age": lap.tyre_age,
                "stint": lap.stint,
            })

        export_data = {
            "session": {
                "year": session_data.year,
                "event": session_data.event,
                "session_type": session_data.session_type,
            },
            "vehicle_params": self.vehicle_params.to_dict(),
            "laps": laps_data,
        }

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)

    def import_json(self, input_file: str = "cpp/ipc/tire_data_out.json") -> None:
        """Import C++ Pacejka results"""
        try:
            with open(input_file, "r") as f:
                data = json.load(f)

            for result_dict in data.get("results", []):
                key = AnalysisKey(
                    result_dict["driver"],
                    result_dict["compound"],
                    result_dict["stint"],
                )
                result = TireDegradationResult(
                    key=key,
                    num_laps=result_dict["num_laps"],
                    baseline_time_ms=result_dict["baseline_time_ms"],
                    degradation_rate_ms_per_lap=result_dict[
                        "degradation_rate_ms_per_lap"
                    ],
                    r_squared=result_dict["r_squared"],
                    estimated_tyre_life_laps=result_dict["estimated_tyre_life_laps"],
                )
                self.results.append(result)

        except FileNotFoundError:
            pass

    def save_results(self, output_file: str = "cpp/ipc/tire_results.json") -> None:
        """Save analysis results to JSON"""
        results_dict = {
            "model": "linear_regression",
            "vehicle_params": self.vehicle_params.to_dict(),
            "results": [r.to_dict() for r in self.results],
        }

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results_dict, f, indent=2)


def analyze_stint(
    session_data, driver: str, compound: str, stint: int
) -> Optional[TireDegradationResult]:
    """Analyze one stint"""
    filtered_laps = [
        lap
        for lap in session_data.laps
        if lap.driver == driver
        and lap.tyre_compound == compound
        and lap.stint == stint
        and lap.lap_time is not None
    ]

    if len(filtered_laps) < 2:
        return None

    analyzer = TireDegradationAnalyzer()
    return analyzer.analyze_stint(filtered_laps, driver, compound, stint)


def analyze_all(
    session_data,
) -> Dict[Tuple[str, str, int], TireDegradationResult]:
    results = {}
    analyzer = TireDegradationAnalyzer()

    combinations = set()
    for lap in session_data.laps:
        combinations.add((lap.driver, lap.tyre_compound, lap.stint))

    for driver, compound, stint in sorted(combinations):
        result = analyze_stint(session_data, driver, compound, stint)
        if result:
            results[(driver, compound, stint)] = result

    return results

