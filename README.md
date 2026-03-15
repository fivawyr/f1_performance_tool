# F1 Performance Analysis Tool
 
**Terminal-based F1 performance engineering tool for lap analysis, tire degradation modeling, and data-driven insights. Built as a foundation for multi-series performance engineering (F1 + LMH).**
 
---
 
## What This Tool Does
 
- Session Analysis: Load F1 qualifying/race sessions via FastF1
- Lap Comparison: Compare two drivers lap-by-lap with sector deltas
- Sector Analysis: Find fastest drivers per sector, identify strengths/weaknesses
- Tire Degradation: Multi-model regression → replaced with Pacejka Magic Formula
- Tyre Temperature Estimation: Physics-based heat balance model 
- Interactive CLI: Rich terminal UI with tables, dropdowns, formatted displays
- JSON Export: Prepare data for C++ Pacejka Magic Formula analysis (future)
- Aero Coefficients: (future)
- Lap Time Simulation: (future)
- Powertrain Model: (future)
 
---

 
## Installation & Usage
 
### Setup (with `uv`)
```bash
git clone <repo-url>
cd bmw_f1_project
uv sync
source .venv/bin/activate
```
 
### Run
```bash
uv run python main.py
uv run python test_analysis.py
uv run python test_tyre_degradation.py
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
 
### 3. Tyre Degradation & Regression Models (pre-Pacejka)
 
Three regression models are fitted per stint, best R² wins:
 
1. **Linear**: $T(n) = T_0 + r \cdot n$
2. **Quadratic**: $T(n) = a + b \cdot n + c \cdot n^2$
3. **Exponential**: $T(n) = T_0 + a(1 - e^{-\lambda n})$
 
**Why these are not enough**: regression models are empirical curve fits, they describe the data but have no physical meaning. R² < 0.3 in almost all qualifying stints (2024 Monaco: 1 out of 46 stints with R² > 0.3). This is expected because qualifying stints are too short and noisy for degradation modeling. Race sessions are required.
 
---
 
### 4. Tyre Degradation & Pacejka Magic Formula (in progress)
 
The Pacejka Magic Formula models tyre grip as a function of tyre age and temperature, this is physics, not curve fitting. The formula relates slip angle and vertical load to lateral/longitudinal force, from which grip loss over a stint can be derived.
 
This is the reason tyre temperature estimation matters: Pacejka needs temperature as an input. Without a temperature model, Pacejka cannot be applied to FastF1 data.
 
> Reference: [Pacejka Magic Formula](https://en.wikipedia.org/wiki/Hans_B._Pacejka#Magic_formula)
 
---
 
## Why Qualifying Data is Hard
 
**2024 Monaco Qualifying results**: 46 stints analyzed, 1 meaningful fit (R² > 0.3). Conclusion: qualifying is unsuitable for degradation modeling. Race sessions are the target.
 
See `ANALYSIS_NOTE.md` for full breakdown.
 
---
 
## Future Architecture: F1 + LMH
 
```
core/physics/
├── vehicle.py            # VehicleSpec (mass, power, aero)
├── tire_model.py         # Pacejka + tyre temperature model
├── aero_model.py         # Downforce, drag calculations
└── powertrain.py         # Engine, brake force curves
 
features/
├── laptime_simulator.py  # Universal lap time prediction
├── tyre_temperature # since we separate f1 and calc logic, we can use it for any race series
└── telemetry_analysis.py # Cross-series comparisons
```
 
~70% of core logic will be reusable for the LMH Aero Mapping Tool.
 
---
 
## References
 
- FastF1 docs: https://fastf1.readthedocs.io/
- Pacejka Magic Formula: https://en.wikipedia.org/wiki/Hans_B._Pacejka#Magic_formula
- TRT tyre thermal model (Farroni et al., 2014): https://doi.org/10.1080/00423114.2014.940987
- Pirelli F1 compounds: https://www.pirelli.com/tyres/en-ww/motorsport/f1
- Churchill-Bernstein equation: https://en.wikipedia.org/wiki/Churchill%E2%80%93Bernstein_equation