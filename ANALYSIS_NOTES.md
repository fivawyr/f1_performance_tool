# F1 Tire Degradation Analysis - Technical Notes

## Current Status (March 2026)

### What We've Learned

**Testing**: 2024 Monaco Grand Prix Qualifying Session
- **Total stints analyzed**: 46 (across 20 drivers)
- **Average stint length**: 3-7 laps
- **Meaningful fits** (R² > 0.3): 1 out of 46 (2.2%)
- **Median R²**: 0.09 (linear regression)

**Conclusion**: Qualifying data is NOT suitable for tire degradation modeling.

---

## Why Linear Regression Failed

### Root Causes (Ranked by Impact)

1. **Insufficient Data Points** (Impact: Very High)
   - Qualifying stints: 2-7 laps
   - Tire degradation needs: 20+ data points for statistical significance
   - With n=3, any 3-parameter polynomial fits with R²=1.0 (degenerate)
   - **Fix**: Minimum 3 laps requirement implemented ✓

2. **Tire Temperature Ramp-Up** (Impact: High)
   - Laps 1-2: Tires cold, lap time artificially slow
   - Lap 3+: Optimal temperature zone
   - This creates a non-monotonic trend (fast improvement, then slow degradation)
   - **Fix needed**: Filter lap 1 per stint, use lap 2 as baseline

3. **Session Strategy Noise** (Impact: High)
   - Drivers push hard on one run, conservative on next
   - Engineers optimize setup between runs
   - Track/ambient temperature drifts during session
   - **Fix needed**: Classify runs by intent (qualifying vs. practicing)

4. **One-Lap Focus** (Impact: Medium)
   - Qualifying emphasizes single-lap optimization
   - No consistent pace like in races
   - Varying fuel load between runs
   - **Fix needed**: Filter outlier laps, smooth with moving average

5. **Traffic & Position Loss** (Impact: Medium)
   - Yellow flags force early returns
   - Backmarkers affect ideal line availability
   - Queue effects at chicanes
   - **Fix needed**: Detect car-following detection from telemetry

---

## Solution: Switch to Race Data

### Why Race Data Works Better

| Metric | Qualifying | Race |
|--------|------------|------|
| **Stint length** | 2-7 laps | 20-70 laps |
| **Tire warm-up** | Not complete | Fully warm after lap 3 |
| **Driver focus** | Qualifying (one lap) | Pace/strategy (consistent) |
| **Fuel load** | Varies (quali trim) | Predictable (fuel delta) |
| **Expected R²** | 0.05-0.4 | 0.6-0.95 |

### Cached Race Data Available

**2022 British Grand Prix - Race**:
- 71 laps total
- 20 drivers
- Multiple pit stops (3 stints each)
- Mix of tire compounds (Soft, Medium, Hard)
- **Estimated stints suitable for analysis**: ~60% of total

---

## Implementation Roadmap

### Phase 2: Race Data Validation (Week 1)

```python
# Load race data and run analysis
from core.data_loader import load_session
from features.tyre_degradation import analyze_all

session = load_session(2022, "British", "R")  # Load race
results = analyze_all(session)

# Expected: 30+ stints with R² > 0.6
high_quality_fits = {k: v for k, v in results.items() if v.r_squared > 0.6}
print(f"High-quality fits: {len(high_quality_fits)} out of {len(results)}")
```

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

## Technical Improvements Completed ✅

1. **Multi-model selection**: Linear, Quadratic, Exponential
   - Auto-selects best fit based on R²
   - Allows for non-linear degradation curves

2. **Minimum stint threshold**: 3 laps
   - Prevents degenerate fitting with 2 points
   - Allows polynomial models

3. **Enhanced output**: Model type and all three R² values
   - Allows comparison across model families
   - Highlights where quadratic fits better than linear

4. **Color-coded output**: R² > 0.7 (green), 0.4-0.7 (yellow), < 0.4 (red)
   - Quick visual identification of good fits

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

