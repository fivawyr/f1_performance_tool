# Tyre temperature estimation model for tyre degradation

## Background

FastF1 does not provide tyre temperatures. Formula 1 measures tyre temperatures internally using infrared sensors and thermocouples, but does not publish this data via the public live timing API. This model is a **simplified steady-state estimation model**, not a full physical model. Full models such as the **TRT (Thermo Racing Tyre)** from the University of Naples or the **Kelly-Sharp model** simulate tyre temperatures in three dimensions using systems of differential equations and take into account all of the following factors: tyre pressure, camber angle, downforce, braking heat, C1-C5 compound details. To further improve this model, the physics add-ons (braking G-force, aero) are used.

## Physical principles: Thermal Balance

The model is based on a simplified steady-state heat balance of the tyre:

```
T_surface ≈ T_air + Q_road + Q_friction − Q_conv − Q_rain
```

A tyre absorbs heat (from the road surface and through friction) and releases it (through air convection and, where applicable, rain). When these processes are in balance, the result is the surface temperature.

### Term 1: Q_road: Thermal Balance from the streets to the tyres

```
Q_road = α_road × (T_track − T_air)
α_road ≈ 12 W/m²K
```

The hot track transfers heat to the tyre tread. This is modelled as a simple Fourier’s law of heat conduction between two surfaces at different temperatures. According to Pirelli, track temperature is the single most significant factor affecting tyre temperature.

- Source: [Thermal Balance (Wikipedia)](https://en.wikipedia.org/wiki/Thermal_conduction)
### Term 2: Q_friction: Friction Heat

```
Q_friction = 38 × (v / 200)^1.6 × μ_compound × f_age
```

Rolling friction and shear forces within the contact patch generate heat. The term scales disproportionately with speed (exponent 1.6), as more energy is dissipated at higher speeds. The compound factor reflects the fact that softer compounds generate more friction and therefore more heat.
`The different μ-factors are: SOFT; 1.25 , MEDIUM; 1.00, HARD; 0.85, INTERMEDIATE; 0.70, WET; 0.55`

The ageing factor `f_age` models the fact that a tyre generates slightly more heat during the first ~20 laps due to increasing deformation, and then generates less heat as grip decreases:
```python
f_age = 1.0 + 0.008 × min(tyre_life, 20) − 0.003 × max(0, tyre_life − 20)
```

- Source: [Tribologie (Wikipedia)](https://en.wikipedia.org/wiki/Tribology)

### Term 3: Q_conv: Cooling by the air

```
h_conv = 25 + 6.3 × √v_eff
Q_conv = h_conv × 0.05
v_eff = v_fahrzeug / 3.6 + v_wind [m/s]
```

The air cools the tyre surface in accordance with Newton’s law of cooling. The convection coefficient `h_conv` increases with the square root of the effective air velocity — a simplified approach based on the **Churchill-Bernstein model** for cylindrical bodies in cross-flow.


- Source: [Newton's Law of Cooling (Wikipedia)](https://en.wikipedia.org/wiki/Newton%27s_law_of_cooling)
- Source: [Churchill-Bernstein-Equation (Wikipedia)](https://en.wikipedia.org/wiki/Churchill%E2%80%93Bernstein_equation)

### Term 4: Q_rain: Evaporative cooling in the rain

```
Q_rain = 35 °C   (Slicks when rainfall=True)
Q_rain =  8 °C   (WET / INTERMEDIATE when rainfall=True)
Q_rain =  0 °C   (no rain)
```

A film of water on the tyre surface cools the tyre through evaporative enthalpy (latent heat). Slick tyres lose a significant amount of heat as a result and fall outside their optimal operating range. WET and INTERMEDIATE tyres are designed for wet conditions and are less affected.

- Source: [Latent Heat (Wikipedia)](https://en.wikipedia.org/wiki/Latent_heat)
---

## All sources

- Fourier's law: [Fourier's law of thermal conduction](https://en.wikipedia.org/wiki/Thermal_conduction) ( is the basis for Q_road — heat conduction between two surfaces. Q = λ × A × ΔT / d)
- Newton's law of cooling: [Newtons law of cooling](https://en.wikipedia.org/wiki/Newton%27s_law_of_cooling)
  (is the direct basis for the convection term, Q = h × A × ΔT)
>  Note: For h_conv = 25 + 6.3 × √v_eff, I am using Churchill’s highly simplified approximation formula. The constants 25 and 6.3 are empirically calibrated, not derived from the Churchill–Bernstein formula. For this reason, I would like to explicitly refer you to the further reading provided here! 
- Churchill–Bernstein equation: [Churchill-Bernstein](https://en.wikipedia.org/wiki/Churchill%E2%80%93Bernstein_equation)
- Tribology / Frictional heat (Chapter: Physics): [Tribology Link](https://en.wikipedia.org/wiki/Tribology)
- Latent heat (evaporation): [Laten Heat Link](https://en.wikipedia.org/wiki/Latent_heat)
- Thermal conductance and resistance: [Therminal C & R Link](https://en.wikipedia.org/wiki/Thermal_resistance)
- Pirelli F1 compound information: [Pirellis Website](https://www.pirelli.com/tires/en-us/motorsport/f1/tires)
- TRT model (scientific reference): Farroni et al., 'An International Journal of Theoretical and Applied Mechanics' (Springer, Volume 48, 2014)  [Free PDF Download](https://www.researchgate.net/profile/Flavio-Farroni/publication/258226051_TRT_Thermo_racing_tyre_a_physical_model_to_predict_the_tyre_temperature_distribution/links/5adf0842aca272fdaf891721/TRT-Thermo-racing-tyre-a-physical-model-to-predict-the-tyre-temperature-distribution.pdf)

