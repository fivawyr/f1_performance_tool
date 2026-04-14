#pragma once 
#include "pacejkacoefficients.h" 
#include <cmath>
using namespace std;
typedef double f64;

struct Tyreforces {
  f64 Fy = 0.0; // Lateral force
  f64 Fx  = 0.0; // Longitudinal force
  f64 Am = 0.0; // aligning moment 
};
/* Explaination of the pacejka calulation:
 * We having our coefficients, which are variable, depending of our vehcicle. The absolut best case would to get the values by a formula student car 
 * and changing the values, that I got from the lecture. We passing D - max force, C - curve shape, B - stiffness, E - curvature factor (how sharp is the curve?),
 * Sh/Sv Horizontal shifts (how is the horizontal changes of the car - due to camber effects or tyre asymmetry -> Shy horizontal / svy vertical). 
 * Those coefficients are passed in the magic formula 
 * 
 * Source: Pacejka, "Tyre and Vehicle Dynamics", 3rd ed. (2012), Appendix 3
 */
class PacejkaCalculation {
  public:
    explicit PacejkaCalculation(const PacejkaCoefficients& coeffs) : c_(coeffs) {}
    
    f64 calcFy(f64 alpha, f64 Fz, f64 gamma = 0.0) const {
      const f64 dfz = normLoadData(Fz); 
      const f64 Cy = c_.pCy1;
      const f64 mu_y = (c_.pDy1 + c_.pDy2 * dfz);
      const f64 Dy = mu_y * Fz;
      const f64 Ky = c_.pKy1 * c_.Fz0 * atan(2.0 * atan(Fz / (c_.pKy2 * c_.Fz0)));
      const f64 By = Ky / (Cy * Dy + eps_); 
      const f64 Ey = c_.pEy1 + c_.pEy2 * dfz;
      const f64 Shy = c_.pHy1 + c_.pHy2 * dfz; 
      const f64 Svy = (c_.pVy1 + c_.pVy2 * dfz) * Fz;

      const f64 alpha_y = alpha + Shy;
      return Dy * magicFormula(By, Cy, Ey, alpha_y) + Svy;
    }

    f64 calcFx(f64 kappa, f64 Fz) const {
      const f64 dfz = normLoadData(Fz);
      const f64 Cx = c_.pCx1;
      const f64 mu_x = (c_.pDx1 + c_.pDx2 * dfz);
      const f64 Dx = mu_x * Fz;
      const f64 Kx = Fz * (c_.pKx1 + c_.pKx2 * dfz);
      const f64 Bx = Kx / (Cx * Dx + eps_);
      const f64 Ex = c_.pEx1 + c_.pEx2 * dfz;
      const f64 Shx = c_.pHx1 + c_.pHx2 * dfz; 
      const f64 Svx = (c_.pVx1 + c_.pVx2 * dfz) * Fz;
      const f64 kappa_x = kappa + Shx;
      return Dx * magicFormula(Bx, Cx, Ex, kappa_x) + Svx;
    }

    //TODO: calcCombined

    f64 calcAm(f64 alpha, f64 Fz, f64 Fy) const {
      const f64 dfz = normLoadData(Fz);
      const f64 Bt = c_.qBz1 + c_.qBz2 * dfz; 
      const f64 Ct = c_.qCz1;
      const f64 Dt = (c_.qDz1 + c_.qDz2 * dfz) * Fz;
      const f64 Et = c_.qEz1;
      const f64 Sht = c_.qHz1;

      const f64 alpha_t = alpha + Sht;
      const f64 t = Dt * magicFormula(Bt, Ct, Et, alpha_t);
      
      return -t * Fy;
    }

    Tyreforces calcCombined(f64 alpha, f64 kappa, f64 Fz, f64 gamma = 0.0) {
      const f64 Fx0 = calcFx(kappa, Fz);
      const f64 Fy0 = calcFy(alpha, Fz, gamma);

      const f64 mu_x = abs(Fx0) /  (Fz + eps_);
      const f64 mu_y = abs(Fy0) / (Fz + eps_); 
      const f64 denom = sqrt((mu_x * mu_x) + (mu_y * mu_y)) + eps_; 
      Tyreforces f; 
      f.Fx = Fx0 * (mu_x / denom);
      f.Fy = Fy0 * (mu_y / denom); 
      f.Am = calcAm(alpha, Fz, f.Fy);
      return f; 
    }

  private:
    PacejkaCoefficients c_;
    static constexpr f64 eps_ = 1e-9;

    f64 normLoadData(f64 Fz) const {
      return (Fz - c_.Fz0) / c_.Fz0; 
    }

    static f64 magicFormula(f64 B, f64 C, f64 E, f64 x) {
      const f64 Bx = B * x;
      return sin(C * atan(Bx - E * (Bx - atan(Bx))));
    }
};
