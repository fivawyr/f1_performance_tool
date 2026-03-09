
# F1 Performance Engineering CLI

F1 Performance Analysis & Simulation Tool — Terminal-based interface for lap analysis, tire degradation modeling, and pace predictions.

## Project Goals

- **Data Analysis**: Analyze F1 (FastF1) 
- **Simulation & Prediction**: Predict lap times, tire degradation, and race pace
- **Terminal UI**: Interactive CLI for team selection, analysis features, and visualizations
- **C++ Integration**: Learning C++ through performance-critical calculations 
- **Multi-Series Support**: F1 + LMDH use cases

## 📋 Project Structure

```
bmw_f1_project/
├── main.py                              # CLI entry point
├── README.md                            # This file
├── pyproject.toml                       # uv project config
│
├── ui/                                  # Terminal UI components
│   ├── __init__.py
│   ├── ui_functions.py                  # Team banners, menus
│   └── menus.py                         # [TODO] Analysis feature menus
│
├── core/                                # [TODO] Core analysis logic
│   ├── __init__.py
│   ├── models.py                        # Data models (LapData, ComparisonResult)
│   ├── data_loader.py                   # FastF1 session loading
│   ├── analysis.py                      # Lap comparisons, telemetry analysis
│   └── simulation.py                    # ML models for predictions
│
├── features/                            # [TODO] Advanced features
│   ├── velocity_calculator.py           # Derivative calculation from position data
│   ├── tyre_degradation.py              # Tire degradation modeling
│   └── quali_race_converter.py          # Quali→Race pace conversion scoring
│
├── utils/                               # Utility functions
│   ├── check_fastf1.py                  # FastF1 data inspection
│   ├── data_utils.py                    # [TODO] Data normalization, filtering
│   └── constants.py                     # [TODO] Track layouts, LMDH data
│
├── cpp/                                 # [TODO] C++ integrations
│   ├── analysis/
│   │   └── velocity_calc.cpp            # Numeric differentiation, filtering
│   ├── CMakeLists.txt
│   └── ipc/
│       ├── data_in.json                 # Python → C++ input
│       └── data_out.json                # C++ → Python output
│
└── cache/                               # FastF1 cache directory
    └── [auto-generated season folders]
```

## 🚀 Setup & Workflow

### Installation
```bash
cd ~/bmw_f1_project
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # or ~/.bashrc / close terminal
```

### Project Setup
```bash
uv sync                 # Install dependencies
uv run main.py          # Run the application
```

### Running helper script
```bash
uv run utils/check_fastf1.py    # Inspect FastF1 data structure
```

---

##  Development Roadmap

### Phase 1: Foundation (This Week)
**Goal**: Build core data models and basic analysis functions

- [ ] Create `core/models.py` with dataclasses
  - `LapData` (driver, lap_time, sectors, telemetry)
  - `SessionData` (event, drivers, laps list)
  - `ComparisonResult` (delta times, insights)
- [ ] Create `core/data_loader.py` 
  - Load FastF1 sessions with caching
  - Extract lap data into models
- [ ] Create `core/analysis.py`
  - Compare two laps (time delta, sector breakdown)
  - Analyze throttle/brake profiles
- [ ] Extend `ui/menus.py`
  - Main menu after team selection
  - Analysis feature selection

### Phase 2: Analysis Features (Week 2)
**Goal**: Implement velocity calculations and tire degradation MVP

- [ ] Create `features/velocity_calculator.py` (Python version)
  - Numerische Differentiation: velocity = Δposition / Δtime
  - Smooth noisy position data (moving average)
  - Bonus: acceleration & jerk calculation
- [ ] Create `features/tyre_degradation.py` (MVP - Linear Regression)
  - Fit linear model: LapTime = a + b*LapNumber
  - Show degradation rate (ms/lap)
  - Predict tyre life
- [ ] Create `features/quali_race_converter.py` (Formula-based)
  - Implement empirical formula for fuel/tire impact
  - Confidence scoring based on data availability
- [ ] Create `utils/data_utils.py`
  - Fuel-corrected lap times
  - Temperature adjustment functions
  - Data filtering & normalization

### Phase 3: C++ Integration (Week 3)
**Goal**: Implement Velocity Calculator in C++ for performance

- [ ] Setup C++ project with CMakeLists.txt
- [ ] Implement `velocity_calc.cpp`
  - Read JSON input (position data from Python)
  - Apply Savitzky-Golay filter for noise reduction
  - Output velocity_trace.json
- [ ] Python wrapper to call C++ binary
- [ ] Benchmark: Compare Python vs C++ performance

### Phase 4: ML & Advanced Features (Week 4+)
**Goal**: Enhanced predictions with machine learning

- [ ] Historical data collection (50+ races)
- [ ] ML model for quali→race pace conversion
- [ ] Tire degradation advanced modeling (polynomial fit, temperature sensitivity)
- [ ] Driver consistency scoring

---

## 🔍 How to Proceed: Step-by-Step Guide

### Step 0: Inspect Current Data (Today)
```bash
uv run utils/check_fastf1.py
# This shows you:
# - Event info structure
# - Available drivers
# - Sample lap data
# - All column names in session.laps
```
**Why**: Understand what data FastF1 provides before building models.

---

### Step 1: Create Data Models (`core/models.py`)
**Time: ~2 hours**

Create dataclasses to represent your domain:

```python
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, List

@dataclass
class LapData:
    """Single lap telemetry & timing data"""
    driver: str
    lap_number: int
    lap_time: timedelta
    sector1: Optional[timedelta]
    sector2: Optional[timedelta]
    sector3: Optional[timedelta]
    speed_trap: Optional[float]      # km/h
    throttle_trace: List[float]      # 0-100%
    brake_trace: List[float]         # 0-100%
    speed_trace: List[float]         # km/h
    position_data: Optional[tuple]   # (x, y, z) coordinates
    fuel_load: Optional[float]       # kg
    tyre_age: int                    # laps on current tyre
    tyre_compound: str               # "SOFT", "MEDIUM", "HARD"
    is_personal_best: bool

@dataclass
class ComparisonResult:
    """Lap comparison output"""
    driver1: str
    driver2: str
    lap_time_delta: timedelta        # positive = driver1 slower
    sector_deltas: dict              # {1: timedelta, 2: ..., 3: ...}
    best_sector: int                 # which sector does driver1 lose most?
    improvement_areas: List[str]     # ["Sector 2", "Exit speed T3", ...]
```

**What to test:**
- Can you create a `LapData` object from FastF1 session data?
- Does it match the structure you need?

---

### Step 2: Create Data Loader (`core/data_loader.py`)
**Time: ~3 hours**

Bridge between FastF1 API and your models:

```python
import fastf1
from core.models import LapData, SessionData

def load_session(year: int, event: str, session_type: str) -> SessionData:
    """Load a FastF1 session and convert to LapData models"""
    session = fastf1.get_session(year, event, session_type)
    session.load()
    
    # Convert each row to LapData
    # Handle missing data gracefully
    # Return SessionData with list of LapData objects

def get_lap_data_from_row(lap_row) -> LapData:
    """Convert FastF1 lap row to LapData model"""
    # Extract telemetry (throttle, brake, speed traces)
    # Calculate sectors from lap timing data
    # Handle None values
```

**What to test:**
- Load a real session (e.g., 2024 Monaco Qualifying)
- Print first 3 laps to verify data integrity
- Check which fields are actually available in FastF1

---

### Step 3: Create Basic Analysis (`core/analysis.py`)
**Time: ~4 hours**

Implement comparison logic:

```python
def compare_laps(lap1: LapData, lap2: LapData) -> ComparisonResult:
    """Detailed lap comparison"""
    # Calculate time deltas
    # Sector-by-sector breakdown
    # Identify where main time loss comes from
    
def analyze_throttle_brake_profiles(lap1: LapData, lap2: LapData) -> dict:
    """Compare driver inputs"""
    # Compare throttle application points
    # Compare brake point & release
    # Return insights

def find_fastest_sector(session_laps: List[LapData]) -> dict:
    """Per-sector fastest splits"""
    # Group laps by sector
    # Find best sector1, sector2, sector3 across session
```

**What to test:**
- Load 2018 Monaco Qual + 2024 Monaco Qual
- Compare two drivers
- Verify sector delta calculations match FastF1 display

---

### Step 4: Extend UI with Analysis Menu (`ui/menus.py`)
**Time: ~2 hours**

```python
def analysis_menu(team_name: str):
    """Main analysis feature menu"""
    options = [
        "Compare Two Drivers",
        "Analyze Single Lap",
        "Tire Degradation Analysis",
        "Quali→Race Pace Conversion",
        "Exit"
    ]
    # Use simple_term_menu to let user choose
    # Call appropriate analysis function
    # Display results with Rich tables
```

**What to test:**
- Can you select a feature & get output?
- Does the menu flow feel natural?

---

### Step 5: Velocity Calculator - Python MVP (`features/velocity_calculator.py`)
**Time: ~2 hours**

```python
import numpy as np

def calculate_velocity(position_data: np.ndarray, time_data: np.ndarray) -> np.ndarray:
    """Numeric differentiation: v = dp/dt"""
    velocity = np.diff(position_data) / np.diff(time_data)
    return velocity

def smooth_trace(trace: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Moving average filter for noisy data"""
    return np.convolve(trace, np.ones(window_size)/window_size, mode='same')

def calculate_acceleration(velocity_trace: np.ndarray, time_data: np.ndarray) -> np.ndarray:
    """a = dv/dt"""
    return np.diff(velocity_trace) / np.diff(time_data)
```

**What to test:**
- Can you extract position data from a lap?
- Does the calculated velocity match FastF1's speed data?

---

### Step 6: Tire Degradation - MVP (`features/tyre_degradation.py`)
**Time: ~3 hours**

```python
from scipy import stats
import numpy as np

def analyze_tire_degradation(stint_lap_times: List[timedelta]) -> dict:
    """Linear regression on lap times over a stint"""
    times_ms = [lt.total_seconds() * 1000 for lt in stint_lap_times]
    lap_nums = np.arange(1, len(times_ms) + 1)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(lap_nums, times_ms)
    
    return {
        "degradation_rate_ms_per_lap": slope,
        "baseline_time_ms": intercept,
        "r_squared": r_value**2,
        "estimated_tyre_life_laps": estimate_tyre_life(slope),
        "confidence": "HIGH" if r_value**2 > 0.9 else "MEDIUM"
    }

def estimate_tyre_life(degradation_rate: float, max_acceptable_loss_ms: float = 2000) -> int:
    """How many more laps until tyre is too slow?"""
    return int(max_acceptable_loss_ms / abs(degradation_rate))
```

**What to test:**
- Load a race stint (e.g., Laps 1-25 of same driver on same tyre)
- Plot lap times vs lap number (visual check)
- Does degradation rate make sense?

---

### Step 7: Quali→Race Converter - MVP (`features/quali_race_converter.py`)
**Time: ~3 hours**

```python
def predict_race_pace(quali_best_lap: timedelta, fuel_load_kg: float, 
                      tyre_age: int = 0) -> dict:
    """Empirical prediction: Race pace from Quali data"""
    
    # Base prediction formula
    quali_ms = quali_best_lap.total_seconds() * 1000
    
    # Fuel penalty: ~0.4 ms per kg
    fuel_penalty_ms = (fuel_load_kg / 1000) * 0.4
    
    # Tire penalty: age + compound effect
    # Fresh soft tyre in quali vs used medium in race
    tire_penalty_ms = 0.8  # placeholder
    
    # Track evolution (track gets faster over race day)
    track_evolution_ms = -0.3  # negative = track gets faster
    
    predicted_race_pace = quali_ms + fuel_penalty_ms + tire_penalty_ms + track_evolution_ms
    
    return {
        "predicted_race_lap_ms": predicted_race_pace,
        "predicted_race_lap": timedelta(milliseconds=predicted_race_pace),
        "delta_vs_quali": predicted_race_pace - quali_ms,
        "confidence_percent": 65,  # Low confidence without ML data
        "factors": {
            "fuel_penalty": fuel_penalty_ms,
            "tire_penalty": tire_penalty_ms,
            "track_evolution": track_evolution_ms
        }
    }
```

**What to test:**
- Manual verification: does result seem realistic?
- Compare against historical data (e.g., 2024 Monaco Quali vs Race)

---

## 🛠️ Tools & Dependencies

**Already installed** (via `pyproject.toml`):
- `fastf1` — F1 telemetry data
- `pandas` — Data manipulation
- `numpy` — Numerical calculations
- `scipy` — Statistics & signal processing
- `rich` — Terminal UI
- `simple-term-menu` — Menu selection
- `scikit-learn` — ML models (for later phases)

**You will need for C++ phase:**
- `cmake` — Build C++ code
- `g++` or `clang++` — C++ compiler
- `nlohmann/json` — C++ JSON library

---

## 📝 Daily Checklist

**Week 1 Goals:**
- [ ] Day 1: Understand FastF1 structure (run `check_fastf1.py`)
- [ ] Day 2-3: Build `core/models.py` + `core/data_loader.py`
- [ ] Day 4: Build `core/analysis.py`
- [ ] Day 5: Extend UI menus
- [ ] Day 6-7: Start `core/simulation.py` or `features/velocity_calculator.py`

**Week 2 Goals:**
- [ ] Complete `features/velocity_calculator.py`
- [ ] Implement `features/tyre_degradation.py` (MVP with linear regression)
- [ ] Implement `features/quali_race_converter.py` (formula-based)
- [ ] Test all features with real F1 data

**Week 3+ Goals:**
- [ ] Setup C++ project, implement `velocity_calc.cpp`
- [ ] Collect historical data (50+ races)
- [ ] Build ML models for enhanced predictions

---

## 💡 Tips for Success

1. **Test Early & Often**: After each step, load real F1 data and verify results
2. **Use Rich for Visualization**: Tables, panels, and colors help spot patterns
3. **Document Data Flow**: Draw arrows between `data_loader.py` → `models.py` → `analysis.py`
4. **Incremental C++ Learning**: Start simple (read JSON, write JSON), then add math
5. **Keep LMDH in Mind**: Design functions to work with both F1 and LMDH data

---

## 📚 References

- FastF1 Docs: https://docs.fastf1.dev/
- F1 Physics/Telemetry: Research papers on tire models, fuel impact
- C++ IPC via JSON: Simple & language-agnostic approach