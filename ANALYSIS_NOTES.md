# F1 Tire Degradation Analysis - Technical Notes

## Current Status (roadmap for clarity since I work one 3 projects)

### Qualifying Data, Step One (validates & proofs, if the three models are enough)

**Testing**: 2024 Monaco Grand Prix Qualifying Session
- **Total stints analyzed**: 46 (across 20 drivers)
- **Average stint length**: 3-7 laps (one of our big issue with qualifying data)
- **Meaningful fits** (R² > 0.3): 1 out of 46 (2.2%)
- **Median R²**: 0.09 (linear regression) -> horrendously bad determination coefficient median! 

**Conclusion**: Qualifying data is NOT suitable for tire degradation modeling and the three models are not valid enough for real tyre degradation

---

### Phase 2: Race Data Analysis 

**Testing**: 2022 British Grand Prix - Race Session
- **Total stints analyzed**: 46 (across 17 drivers)
- **Total laps processed**: 674 valid laps (big improvement to qualifiyind rounds)
- **Average stint length**: 11.5 laps
- **Average R²**: 0.444 (vs 0.09 from qualifying) 
- **4.9x improvement!**
- **High-quality fits** (R² > 0.6): 13 out of 46 (28.3%)
- **Medium-quality fits** (0.3 ≤ R² ≤ 0.6): 19 out of 46 (41.3%)

**Model distribution**:
- Quadratic: 40 stints (87%)
- Linear: 4 stints (8.7%)
- Exponential: 2 stints (4.3%)

**Best fits**:
1. NOR HARD Stint 3: R² = 0.974 (4 laps, -215.50 ms/lap) 
2. HAM HARD Stint 3: R² = 0.969 (4 laps, -261.70 ms/lap)
3. VET MEDIUM Stint 3: R² = 0.906 (31 laps, minimal degradation)

---

## Why Race Data Works Better

| Metric | Qualifying | Race (2022 British) |
|--------|------------|-----|
| **Stint length** | 2-7 laps | 3-32 laps |
| **Average R²** | 0.09 | 0.444 |
| **High-quality stints** | 2.2% | 28.3% |
| **Tire warm-up** | Not complete | Fully warm after lap 3 |
| **Driver focus** | Qualifying (one lap) | Pace/strategy (consistent) |
| **Fuel load** | Varies (quali trim) | Predictable (fuel delta) |

**Key Insight**: Race data provides 4.9x better average fit than qualifying, but still needs preprocessing to reach target R² > 0.6 across majority of stints. We could get a determination coefficient by reducing factors like temp, competition or fuel. Instead of simplyfing our issue, we need to create a new modell (pacejka), to include physical effects. 

---

### Cached Race Data Available

**2022 British Grand Prix - Race**:
- 71 laps total, 674 valid laps processed
- 46 stints across 17 drivers
- Mix of tire compounds (Soft, Medium, Hard)
- **Actual stints suitable for analysis**: 46 out of 46 (100%)
- **High-quality stints**: 13 (28.3%)

---

## Implementation Roadmap

### Phase 2: Race Data Validation

**Script**: `analyze_race_data.py`
```bash
cd /Users/finn/dev/f1_performance_tool/f1_performance_tool
uv run python analyze_race_data.py
```

**Output files** (in `analysis_results/`):
- `race_analysis_2022_British_R_<timestamp>.json` - Full data
- `race_analysis_2022_British_R_<timestamp>.md` - Human-readable report

**Results Summary**:
```
Average R²:                    0.444 (vs 0.09 from qualifying)
High quality (R² > 0.6):      13 stints (28.3%)
Medium quality (0.3-0.6):     19 stints (41.3%)
Low quality (R² < 0.3):       14 stints (30.4%)

Best fit:                      NOR HARD Stint 3 (R² = 0.974)
Quadratic model dominance:     40/46 stints (87%)
```

**Conclusions**:
- Race data is significantly better than qualifying
- Quadratic model is best fit for most stints
- Still need preprocessing to improve remaining 72% of stints
- Target: Phase 3 should push >60% to R² > 0.6

---

### Phase 3: Data Preprocessing (Week 2-3)

#### 3.1 Lap Filtering
```python
def filter_stint(laps):
    """Remove out-lap and warm-up effects"""
    # Exclude lap 1 (out-lap, cold tires)
    # Exclude pit-lap (lap before stop)
    # Flag laps >2% slower (traffic/yellow flag)
    return laps[1:-1]  # Remove first and last
```

#### 3.2 Fuel Correction
```python
def correct_for_fuel(lap_times, fuel_loads):
    """Fuel adds ~0.5-0.6% lap time per 5kg"""
    fuel_delta = (fuel_loads - fuel_loads[0]) * 0.001  # per kg
    return lap_times - fuel_delta
```

#### 3.3 Temperature Correction
```python
def correct_for_temperature(lap_times, track_temps):
    """Temperature delta: ~0.05ms per 1°C"""
    temp_delta = (track_temps - track_temps[0]) * 0.05
    return lap_times - temp_delta
```

### Phase 4: Enhanced Models (Week 4+)

#### 4.1 Segmented Linear Regression
```
T(n) = {
    T0 (warm-up)        if n <= 3
    T_min + r*(n-3)     if 3 < n < end
    T_min + r_high      if n > degradation_threshold
}
```
Two-slope model captures warm-up and mid-life degradation separately.

#### 4.2 Logarithmic Model
```
T(n) = T_min + a*ln(n) + b
```
More realistic for tire physics (diminishing returns on degradation).

#### 4.3 Pacejka-Inspired Model
```
T(n) = T_min * (1 + B * arctan(C * (grip_loss(n) - D)))
```
Links lap time directly to grip coefficient loss.

---

## Key Metrics to Track

### Model Quality
- **R² value**: Goodness of fit
  - \> 0.7: Excellent
  - 0.5-0.7: Good
  - 0.3-0.5: Fair
  - < 0.3: Poor
  
- **RMSE**: Root Mean Square Error (in ms)
  - \< 50ms: Excellent
  - 50-200ms: Good
  - \> 500ms: Poor

- **Prediction error**: Max deviation from model
  - Should decrease as stint length increases

### Physical Validity
- Degradation rate should be positive (slower laps)
- Estimated tire life should be 30-70 laps for Soft compound
- Should vary by driver (aggressive = faster degradation)

---

## Next Steps

1. **Immediate**: Run test on 2022 British GP race data
   ```bash
   uv run -c "
   from core.data_loader import load_session
   from features.tyre_degradation import analyze_all
   from rich.console import Console
   
   console = Console()
   session = load_session(2022, 'British', 'R')
   results = analyze_all(session)
   good = {k:v for k,v in results.items() if v.r_squared > 0.6}
   console.print(f'High-quality: {len(good)}/{len(results)}')
   "
   ```

2. **Week 1**: Add lap filtering + fuel correction

3. **Week 2**: Implement temperature correction

4. **Week 3**: Validate against known tire degradation rates

5. **Week 4+**: Pacejka integration

---

## References

- Tire Physics: "Tire and Vehicle Dynamics" by Hans B. Pacejka
- F1 Fuel Impact: ~0.5-0.6 ms/kg across 50-lap stint
- Temperature Impact: ~0.05 ms/°C across range 20-80°C
- Qualifying vs Race: Tire life tests show 20-30% difference in degradation rates

