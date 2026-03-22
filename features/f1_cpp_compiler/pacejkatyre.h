#pragma once 
#include "pacejkacoefficients.h" 
#include <cmath>
typedef double f64;

struct Tyreforces {
  f64 Fy = 0.0; // Lateral force
  f64 Fx  = 0.0; // Longitudinal force
  f64 Am = 0.0; // aligning moment 
};
/* Explaination of the pacejka calulation:#
 * We having our coefficients, which are variable, depending of our vehcicle. The absolut best case would to get the values by a formula student car 
 * and changing the values, that I got from the lecture. We passing D - max force, C - curve shape, B - stiffness, E - curvature factor (how sharp is the curve?),
 * Sh/Sv Horizontal shifts (how is the horizontal changes of the car - due to camber effects or tyre asymmetry -> Shy horizontal / svy vertical). 
 * Those coefficients are passed in the magic formula 
 */
class PacejkaCalculation {
  public:
    explicit PacejkaCalculation(const PacejkaCoefficients& coeffs) : c_(coeffs) {}
    
    f64 calcFy(f64 alpha, f64 Fz, f64 gamma = 0.0) const {
      const f64 dfz = normLoadData(Fz); 
      const f64 Cy = c_.pCy1;
      const f
    }
  private:
    PacejkaCoefficients c_;
    f64 normLoadData(f64 Fz) const {
      return (Fz - c_.Fz0) / c_.Fz0; 
    }
};
