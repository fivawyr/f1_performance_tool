# BMW F1 Performance Analysis Tool

**Terminal-based F1 performance engineering tool for lap analysis, tire degradation modeling, and data-driven insights. Built as a foundation for multi-series performance engineering (F1 + LMH).**

---

## 📊 What This Tool Does

- **Live Session Analysis**: Load F1 qualifying/race sessions via FastF1
- **Lap Comparison**: Compare two drivers lap-by-lap with sector deltas
- **Sector Analysis**: Find fastest drivers per sector, identify strengths/weaknesses  
- **Tire Degradation**: Linear regression on lap times to predict tyre life
- **Interactive CLI**: Rich terminal UI with tables, dropdowns, formatted displays
- **JSON Export**: Prepare data for C++ Pacejka Magic Formula analysis (future)

---

## ✅ Current Features (Phase 1 - Complete)

### Core Infrastructure
- ✅ **Data Models** (`core/models.py`)
  - `LapData`: Full lap telemetry (time, sectors, speeds, tire info)
  - `SessionData`: Session wrapper with driver list
  - `ComparisonResult`: Structured comparison results
  
- ✅ **Data Loader** (`core/data_loader.py`)
  - Load FastF1 sessions with automatic caching
  - Filter valid laps (IsAccurate=True, LapTime exists)
  - Extract driver codes from lap data
  
- ✅ **Analysis Functions** (`core/analysis.py`)
  - `compare_laps()`: Side-by-side lap comparison with sector breakdown
  - `find_best_lap_per_driver()`: Best lap identification
  - `find_fastest_sector()`: Sector leader board
  - `analyze_tyre_degradation()`: Raw lap time trend analysis

- ✅ **Interactive CLI** (`ui/menus.py`)
  - Driver selection dropdowns
  - Rich formatted output (tables, split-screen panels)
  - Lap comparison display with delta highlighting
  - Sector analysis top-10 rankings
  - Tire degradation visualizations

### Advanced Features
- ✅ **Tire Degradation MVP** (`features/tyre_degradation.py`)
  - Linear regression: `LapTime = baseline + degradation_rate × lap_number`
  - F1 2026 vehicle parameters (768 kg, 760 kW, 34 kN brakes)
  - Pacejka Magic Formula placeholders (ready for C++ integration)
  - JSON export for C++ analysis pipeline
  - `AnalysisKey` dataclass for clean result identification

---

## 📋 Project Structure

```
bmw_f1_project/
├── main.py                    # CLI entry point
├── pyproject.toml            # Python dependencies (uv)
├── README.md                 # This file
│
├── core/
│   ├── models.py            # ✅ LapData, SessionData, ComparisonResult
│   ├── data_loader.py       # ✅ FastF1 session loading + filtering
│   └── analysis.py          # ✅ Comparison, sector, degradation analysis
│
├── features/
│   └── tyre_degradation.py  # ✅ Linear regression + JSON I/O
│
├── ui/
│   └── menus.py             # ✅ Interactive CLI with Rich formatting
│
├── utils/
│   └── check_fastf1.py      # Data inspection utility
│
├── tests/
│   ├── test_loader.py       # ✅ Data loading validation
│   ├── test_analysis.py     # ✅ Analysis function tests
│   └── test_tyre_degradation.py # ✅ Regression tests
│
└── cache/                   # FastF1 cache (auto-generated)
```

---

## 🚀 Installation & Usage

### Setup
```bash
# Clone and enter project
git clone <repo-url>
cd bmw_f1_project

# Create Python 3.12+ environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Run Application
```bash
python main.py
```

### Run Tests
```bash
python test_tyre_degradation.py      # Test tire analysis
python test_analysis.py              # Test core functions
python test_loader.py                # Test data loading
```

---

## 🔄 Tire Degradation Analysis

The MVP uses **linear regression** to model tire performance:

```
LapTime(n) = Baseline + DegradationRate × n
```

**Example Output:**
```
HAM SOFT Stint 1:
  Baseline: 86360 ms (1:26.360)
  Degradation: 487 ms/lap
  R²: 0.003 (poor fit - typical for qualifying)
```

### ⚠️ Current Limitations
- Linear regression works **best with race data** (50+ consecutive laps)
- Qualifying data shows high noise (R² near 0) due to:
  - Tire temperature ramp-up
  - Setup changes between runs
  - Traffic effects
  - Session strategy (push vs. conservative)

**Next Steps**: 
- Test with full-race data for validation
- Implement polynomial regression
- Add temperature/fuel correction factors

---

## 🌍 Future Architecture: F1 + LMH

This tool is being designed as a **reusable framework** for multiple motorsport series:

### Planned Abstraction Layer
```
core/physics/              (Generic models for any series)
├── vehicle.py           # VehicleSpec (mass, power, aero)
├── tire_model.py        # Pacejka + custom tire models
├── aero_model.py        # Downforce, drag calculations
└── powertrain.py        # Engine, brake force curves

features/
├── laptime_simulator.py  # Universal lap time prediction
└── telemetry_analysis.py # Cross-series comparisons
```

### Use Case: LMH Aero Mapping Tool
When building the companion **LMH Aero Mapping Tool**:
1. **CFD Results** → SessionData (generic)
2. **Reuse Physics Models** (Pacejka, aero coefficients)
3. **Reuse Analysis Functions** (degradation trends, optimization)
4. **Same UI Framework** (Rich dashboards)

**Code Share**: ~70% of core logic will be reusable.

---

## 🛠️ Development Roadmap

### Phase 1: Foundation ✅ COMPLETE
- ✅ Core data models
- ✅ FastF1 integration
- ✅ Basic analysis functions
- ✅ Interactive CLI
- ✅ Tire degradation MVP

### Phase 2: Integration & Testing (Next)
- [ ] Integrate tire degradation into main menu
- [ ] Test with race data (2022 British GP, etc.)
- [ ] Validate degradation trends
- [ ] Documentation & case studies

### Phase 3: Advanced Features
- [ ] **Velocity Calculator** (position data → speed/acceleration)
- [ ] **Qualifying to Race Converter** (empirical pace prediction)
- [ ] **Fuel/Temperature Corrections** (more realistic analysis)
- [ ] **ML-based Pace Modeling** (historical data trends)

### Phase 4: C++ Integration (Optional)
- [ ] Pacejka Magic Formula in C++
- [ ] JSON-based Python ↔ C++ IPC
- [ ] Performance benchmarking
- [ ] Production-grade simulation

---

## 📚 Data Flow

```
FastF1 API
    ↓
load_session()
    ↓
SessionData (generic, typed)
    ↓
┌─────────────────────────────────┐
│ Analysis Functions              │
├─────────────────────────────────┤
│ - compare_laps()                │
│ - find_best_lap_per_driver()    │
│ - find_fastest_sector()         │
│ - analyze_tyre_degradation()    │
└─────────────────────────────────┘
    ↓
Results (tables, JSON, insights)
    ↓
[Optional] JSON → C++ (Pacejka)
```

---

## 💡 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Dataclasses for models** | Type-safe, cleaner than dicts |
| **SessionData abstraction** | Generic enough for F1 + LMH |
| **JSON export for C++** | Language-agnostic data format |
| **Linear regression MVP** | Fast, simple, good starting point |
| **Rich CLI over web** | Lightweight, developer-friendly |
| **Modular architecture** | Easy to add features/series |

---

## 🤝 Contributing / Extending

### Add a New Analysis Function
```python
# In core/analysis.py
def analyze_fuel_efficiency(session_data: SessionData) -> dict:
    """Fuel consumption per lap"""
    results = {}
    for driver in session_data.drivers:
        # Your logic
        results[driver] = efficiency
    return results
```

### Add a New Feature
```python
# In features/my_feature.py
def calculate_something(session_data: SessionData) -> Result:
    # Implement
    return Result(...)

# In ui/menus.py - add to analysis menu
"My Feature": lambda: display_my_results(...)
```

---

## 📖 References

- **FastF1 Docs**: https://fastf1.readthedocs.io/
- **Pacejka Magic Formula**: https://en.wikipedia.org/wiki/Hans_B._Pacejka#Magic_formula
- **F1 Technical**: https://www.motorsport.com/f1/
- **LMH Regulations**: https://www.fia.com/

---

## ⚡ Performance Notes

- **Data Loading**: ~5 sec per session (FastF1 caching)
- **Regression Analysis**: <1 ms per stint (NumPy)
- **CLI Rendering**: <100 ms (Rich)
- **Memory**: ~50 MB for full qualifying session (241 laps)

---

Last Updated: March 2026  
Status: Phase 1 Complete, Phase 2 Ready

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