# F1 Performance Analysis Tool

**Terminal-based F1 performance engineering tool for lap analysis, tire degradation modeling, and data-driven insights. Built as a foundation for multi-series performance engineering (F1 + LMH).**

---

## What This Tool Does

- **Session Analysis**: Load F1 qualifying/race sessions via FastF1
- **Lap Comparison**: Compare two drivers lap-by-lap with sector deltas
- **Sector Analysis**: Find fastest drivers per sector, identify strengths/weaknesses  
- **Tire Degradation**: **Multi-model regression** (linear, quadratic, exponential) &rarr; replaced with Pacejka (since the results are not representing enough)
- **Interactive CLI**: Rich terminal UI with tables, dropdowns, formatted displays
- **JSON Export**: Prepare data for C++ Pacejka Magic Formula analysis (future)
- **Physics Model**: Aero Coefficients (future)
- **Actual laptime simulation**: (future)
- **Powertrain Model**: (future)

---

## Installation & Usage

### Setup (with `uv`)
```bash
# Clone and enter project
git clone <repo-url>
cd bmw_f1_project

# Install dependencies with uv (creates virtual env automatically)
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Run the application
```bash
# Start the CLI
uv run python main.py

# Run tests
uv run python test_analysis.py
uv run python test_tyre_degradation.py
```
---

## Tire Degradation Analysis

### Multi-Model Regression (pre Pacjeka)

The analyzer automatically fits **three regression models** and selects the best:

1. **Linear Model**: $T(n) = T_0 + r \cdot n$
2. **Quadratic Model**: $T(n) = a + b \cdot n + c \cdot n^2$
3. **Exponential Model**: $T(n) = T_0 + a(1 - e^{-\lambda n})$

Each model computes an R² goodness-of-fit score. The best model is selected automatically.
**What are those model?**: We use them as empirial fits, to lay the graph on the actual data &rarr; this is called **Regression Analysis** and the result of the **Goodness-of-Fit-Comparision** shows, that we need to use something more accurate (pacejka)

**Example Output:**
```
HAM SOFT Stint 1:
  Baseline: 71404 ms (1:11.404)
  Degradation: 0.0 ms/lap (Quadratic)
  R²: 0.195 (vs linear: 0.003, exponential: varies)
```
```
EMPIRISCHE MODELS:
┌──────────────────────────────────┐
│  Lap Time                        │
│        ╱╱                        │
│      ╱╱  ← Quadratic Fit         │
│    ╱╱                            │
│   • ← Actual data                │
│    •                             │
│      •                           │
│        •                         │
└──────────────────────────────────┘
          Lap Number

Problem: Curve looks good, but why is not enough?
        → Regression Analysis are just checks for data fitting, no physics!


PACEJKA-MODEL:
┌──────────────────────────────────┐
│  Lap Time                        │
│        ╱╱                        │
│      ╱╱  ← Physics-based Curve   │
│    ╱╱                            │
│   • ← Actual data                │
│    •                             │
│      •                           │
│        •                         │
└──────────────────────────────────┘
          Lap Number

Advantage: Incorporating real conditions (physical)
         "Tyre age → lose of grip → lose of lap time"
```

---
### Why Qualifying Data is Challenging

Analysis of 2024 Monaco Qualifying reveals why tire degradation is hard to model:

| Session Type | Issues | Best Model |
|---|---|---|
| **Qualifying** (2-7 laps/stint) | Setup changes, tire warm-up, traffic, one-lap strategy | **None (R² < 0.3)** |
| **Race** (20-50+ laps/stint) | Consistent pace, full tire temperature, fuel variation | **Polynomial/Exponential** |

### Key Findings
- **Low R² in Qualifying**: Most stints show R² < 0.2 because:
  - Tire temperature has not stabilized
  - Drivers optimize setup mid-stint
  - Limited data points (2-3 samples)
- **2-lap Stints are Degenerate**: With n=2, quadratic always fits with R²=1.0 (3 parameters, 2 datapoints)
- **Qualifying ≠ Race Pace**: Even best drivers show noise

### Interpretation Guide
- **R² > 0.7**: Strong model, meaningful degradation trend
- **R² 0.4-0.7**: Moderate noise, use with caution
- **R² < 0.4**: Poor model fit, don't trust predictions (typical for qualifying)
- **Stints < 3 laps**: Filtered out (degenerate/insufficient data)

### Real-World Testing Results

**2024 Monaco Qualifying Analysis**:
- Total stints analyzed: 46
- Meaningful fits (R² > 0.3): **1 out of 46** (2.2%)
- Best fit: Sergio Pérez SOFT Stint 3 (R² = 0.412)

**Conclusion**: Qualifying sessions are **unsuitable** for tire degradation modeling.
> for more information, checkout the ANALYSIS_NOTE.md

---

## Future Architecture: F1 + LMH

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

## 📖 References

- **FastF1 Docs**: https://fastf1.readthedocs.io/
- **Pacejka Magic Formula**: https://en.wikipedia.org/wiki/Hans_B._Pacejka#Magic_formula
- **F1 Technical**: https://www.motorsport.com/f1/
- **LMH Regulations**: https://www.fia.com/

---
