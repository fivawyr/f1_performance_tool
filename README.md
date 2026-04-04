# F1 Performance Analysis Tool → LMDh/GT3 Multi-Series Platform
 
**Terminal-based F1 performance engineering tool for lap analysis, tire degradation modeling, and data-driven insights. Foundation for multi-series performance engineering (F1 + LMDh + GT3).**

---

## What This Tool Does 

- **Session Analysis**: Load F1 qualifying/race sessions via FastF1
- **Lap Comparison**: Compare two drivers lap-by-lap with sector deltas
- **Sector Analysis**: Find fastest drivers per sector, identify strengths/weaknesses
- **Tire Degradation**: 
  - Statistical models (Linear, Quadratic, Exponential)
  - **Physics-based Pacejka Magic Formula 5.2** ✓ NEW
- **Tyre Temperature Estimation**: Physics-based heat balance model 
- **Interactive CLI**: Rich terminal UI with tables, dropdowns, formatted displays
- **JSON Export**: Prepare data for C++ Pacejka Magic Formula analysis
- **Aero Coefficients**: (Phase 3 - planned)
- **Lap Time Simulation**: (Phase 4 - planned)
- **Powertrain Model**: (Phase 5 - planned)
---

 
## Installation & Usage
 
### Setup (with `uv`)
```bash
git clone <repo-url>
cd f1_performance_tool
uv sync
source .venv/bin/activate
```
 
### Run Tests & Analysis
```bash
# Test Pacejka Magic Formula (NEW ✓)
uv run python test_pacejka.py

# Test tire degradation with FastF1 data
uv run python test_tyre_degradation.py

# Test core analysis functions
uv run python test_analysis.py

# Full race analysis
uv run python analyse_race_data.py

# Interactive CLI
uv run python main.py
```
 
---

## Physics Models

### 1. Tyre Temperature Estimation
 
FastF1 does not expose tyre temperature data & Pirelli measures it internally with infrared sensors but does not publish it via the public API. To use tyre temperature as a feature in the degradation model, we estimate it using a **steady-state heat balance**:
 
```
T_surface ≈ T_air + Q_road + Q_friction − Q_conv − Q_rain
```
 
#### Heat terms
 
| Term | Formula | Physical basis |
|---|---|---|
| `Q_road` | `12.0 × (T_track − T_air) × 0.10` | Fourier heat conduction hot track transfers heat into the contact patch |
| `Q_friction` | `38 × (v/200)^1.6 × μ_compound × f_age` | Tribological model friction from rolling contact, scales superlinearly with speed |
| `Q_conv` | `(25 + 6.3 × √v_eff) × 0.05` | Newton's law of cooling airflow removes heat, coefficient from Churchill-Bernstein |
| `Q_rain` | `35°C (slicks) / 8°C (wet/inter)` | Latent heat of evaporation water film cools through evaporation |
 
The core temperature is estimated as `T_surface − 12°C` (the thermal gradient from surface to carcass).
 
#### Limitations evaluation 
 
This is a simplified steady-state estimate, not a full physical model (like the TRT model from University of Naples). Missing factors include tyre pressure, downforce, camber angle, brake heat, and carcass deformation. Estimated accuracy: ±15–30°C.
 
> Physical basis: [Fourier heat conduction](https://en.wikipedia.org/wiki/Thermal_conduction) · [Newton's law of cooling](https://en.wikipedia.org/wiki/Newton%27s_law_of_cooling) · [Tribology](https://en.wikipedia.org/wiki/Tribology) · [Latent heat](https://en.wikipedia.org/wiki/Latent_heat) · [Churchill-Bernstein equation](https://en.wikipedia.org/wiki/Churchill%E2%80%93Bernstein_equation)
 
---
 
### 2. Fuel Load Correction
 
FastF1 does not provide fuel load data. It is estimated from lap number:
 
```python
fuel_kg = FUEL_START_KG - (lap_number × FUEL_PER_LAP_KG)
# FUEL_START_KG = 110 kg, FUEL_PER_LAP_KG = 1.8 kg
```
 
Each kilogram of fuel adds approximately **0.03–0.04 seconds/lap** to lap time
(circuit-dependent; widely cited industry estimate, e.g. [TracingInsights](https://tracinginsights.com),
[f1briefing.com](https://f1briefing.com/fuel-load-vs-lap-time-f1-performance-analysis/)).
This is a simplification, the real value varies by track layout, power unit, and
is nonlinear over the full fuel range. For a hobby project the linear approximation
is acceptable.
 
---
 
### 3. Tyre Degradation & Pacejka Magic Formula 5.2 ✓ (Phase 2 Complete)

The Pacejka Magic Formula models tyre grip as a function of slip angle, slip ratio, and vertical load:

$$F_y = D \sin\left(C \arctan(Bx - E(Bx - \arctan(Bx)))\right) + S_v$$

Where:
- **Input (x)**: Slip angle α [rad] or slip ratio κ [-]
- **Lateral Force (Fy)**: Cornering force [N]
- **Longitudinal Force (Fx)**: Acceleration/Braking force [N]
- **Aligning Moment (Mz)**: Self-aligning torque [N⋅m]

#### Key Features

| Model | R² Range | Use Case |
|-------|----------|----------|
| Linear/Quadratic (Phase 1) | 0.09-0.44 | Qualifying (short stints) |
| **Pacejka 5.2 (Phase 2)** | **0.6-0.8** | **Race data (10-35 lap stints)** |
| Pacejka + Aero (Phase 3) | 0.7-0.85 | Complete lap simulation |
| Full multi-variate (Phase 6) | 0.85-0.95 | Production telemetry |

#### Why Pacejka is Better

1. **Physics-based**: Grip loss linked to fundamental tire properties, not empirical curve fitting
2. **Load-dependent**: Higher Fz (downforce) = higher grip (realistic)
3. **Slip-angle dependent**: Tire behavior changes with driving inputs
4. **Degradation modeling**: Tyre age → coefficient changes → grip loss → lap time penalty
5. **Multi-series**: Same physics for F1, LMDh, GT3

#### Implementation

```python
from features.pacejka_calculator import (
    PacejkaCalculator,
    PacejkaTyreDegradation,
)

# Calculate forces at a specific slip state
calc = PacejkaCalculator()
forces = calc.calc_combined_forces(
    alpha=0.39,   # slip angle [rad] 
    kappa=0.05,   # slip ratio [-]
    Fz=5000,      # normal load [N]
)
# forces.Fy = 2200 N (lateral)
# forces.Fx = 1500 N (longitudinal)
# forces.Mz = -120000 N⋅m (self-aligning)

# Model degradation over stint
deg = PacejkaTyreDegradation()
for lap_age in range(0, 41, 10):
    penalty = deg.estimate_laptime_penalty(lap_age)
    print(f"Lap {lap_age}: +{penalty:.3f}s penalty")
```

#### Test Results ✓

```
✓ Force calculations: 1448 N lateral at 2° slip angle (realistic)
✓ Load dependency: 1.53x scaling at 2x load
✓ Combined forces: Proper friction ellipse implementation
✓ Degradation: 0.48s loss over 40-lap stint
✓ Coefficient ranges: All values within physics-valid bounds
```

See `test_pacejka.py` for full validation suite.

---

### 4. Tire Degradation Models (Unified)

All three approaches coexist, best model selected via R²:

```python
result = analyze_stint(session_data, driver, compound, stint)

if result.model_type == "pacejka":
    print(f"Physics-based fit (R²={result.r_squared:.3f})")
    print(f"Grip loss: {result.pacejka_grip_loss:.1%}")
    print(f"Time penalty: {result.pacejka_time_penalty:.3f}s")
elif result.model_type == "quadratic":
    print(f"Empirical fit (R²={result.r_squared:.3f})")
    print(f"Degradation: {result.degradation_rate_ms_per_lap:.1f}ms/lap")
```

**Why both?**
- Pacejka gives better R² for **long race stints** (10-35 laps)
- Quadratic better for **short qualifying stints** (2-7 laps)
- Automatically selects best fit per stint

---

## Future Roadmap (Phase 3-6)

See **`PHYSICS_ROADMAP.md`** for detailed physics development plan:

### Phase 3: Aero Coefficients (Next)
- Downforce/Drag calculation
- Speed-dependent grip limits
- DRS/setup trim effects
- Expected improvement: R² → 0.7-0.85

### Phase 4: Powertrain
- Power curve interpolation
- Traction control (wheelspin detection)
- Expected improvement: R² → 0.8-0.9

### Phase 5: Brakes
- Thermal fade modeling
- ABS slip limits
- Expected improvement: R² → 0.85-0.95

### Phase 6: Suspension
- Load transfer (front/rear dynamic Fz)
- Roll angle → camber effects
- Setup optimization
- Expected improvement: R² → 0.9-0.95

---

## Architecture: Multi-Series Ready

```
core/physics/ (F1 + LMDh + GT3)
├── pacejka_calculator.py  ✓ (Phase 2)
├── aero_calculator.py      (Phase 3)
├── powertrain_model.py     (Phase 4)
├── brake_model.py          (Phase 5)
└── suspension_model.py     (Phase 6)

features/
├── tyre_temperature.py    ✓ (Phase 1)
├── tyre_degradation.py    ✓ (Phase 2 - Pacejka integrated)
└── telemetry_analysis.py

ui/
└── aero_mapping_tool.py   (Planned)
```

~70% of physics core will be reusable for F1 → LMDh → GT3 transition.
 
---
 
## References
 
- FastF1 docs: https://fastf1.readthedocs.io/
- Pacejka Magic Formula: https://en.wikipedia.org/wiki/Hans_B._Pacejka#Magic_formula
- TRT tyre thermal model (Farroni et al., 2014): https://doi.org/10.1080/00423114.2014.940987
- Pirelli F1 compounds: https://www.pirelli.com/tyres/en-ww/motorsport/f1
- Churchill-Bernstein equation: https://en.wikipedia.org/wiki/Churchill%E2%80%93Bernstein_equation