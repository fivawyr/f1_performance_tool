"""
Pacejka Magic Formula 5.2 Calculator (Python Implementation)
Designed to bridge Python data analysis with C++ optimized calculations

Reference: Pacejka, H.B. "Tire and Vehicle Dynamics" (2012), Appendix 3
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional, Dict
import math


@dataclass
class PacejkaCoefficients:
    # Literal (y) direction
    pCy1: float = 1.3
    pDy1: float = 1.0
    pDy2: float = -0.1
    pEy1: float = -1.0
    pEy2: float = -0.5
    pKy1: float = 10.0
    pKy2: float = 1.5
    pHy1: float = 0.003
    pHy2: float = 0.001
    pVy1: float = 0.04 
    pVy2: float = -0.04
    
    # Longitudinal (x) direction
    pCx1: float = 1.65
    pDx1: float = 1.1
    pDx2: float = -0.1
    pEx1: float = 0.3
    pEx2: float = 0.15
    pEx3: float = 0.0
    pKx1: float = 12.0
    pKx2: float = 10.0
    pHx1: float = 0.002
    pHx2: float = 0.0
    pVx1: float = 0.0
    pVx2: float = 0.0
    
    # Aligning moment (z) direction
    qBz1: float = 9.0
    qBz2: float = -1.5
    qCz1: float = 1.1
    qDz1: float = 0.1
    qDz2: float = -0.02
    qEz1: float = -1.0
    qHz1: float = 0.005
    
    # Reference normal load
    Fz0: float = 4000.0     # Nominal load [N]


@dataclass
class TyreForces:
    """Output: Tyre forces and moments"""
    Fy: float = 0.0         # Lateral force [N]
    Fx: float = 0.0         # Longitudinal force [N]
    Mz: float = 0.0         # Aligning moment [N⋅m]


class PacejkaCalculator:
    """Pacejka Magic Formula 5.2 Tyre Force Calculator"""
    
    EPS = 1e-9
    
    def __init__(self, coefficients: Optional[PacejkaCoefficients] = None):

        self.coeffs = coefficients or PacejkaCoefficients()
    
    def _normalized_load(self, Fz: float) -> float:
        return (Fz - self.coeffs.Fz0) / self.coeffs.Fz0
    
    @staticmethod
    def _magic_formula(B: float, C: float, E: float, x: float) -> float:
        Bx = B * x
        arctan_bx = math.atan(Bx)
        return math.sin(C * math.atan(Bx - E * (Bx - arctan_bx)))
    
    def calc_lateral_force(
        self, 
        alpha: float, 
        Fz: float, 
        gamma: float = 0.0
    ) -> float:

        dfz = self._normalized_load(Fz)
        
        Cy = self.coeffs.pCy1
        mu_y = self.coeffs.pDy1 + self.coeffs.pDy2 * dfz
        Dy = mu_y * Fz
        
        # Lateral stiffness
        Ky = (self.coeffs.pKy1 * self.coeffs.Fz0 * 
              math.atan(2.0 * math.atan(Fz / (self.coeffs.pKy2 * self.coeffs.Fz0))))
        
        By = Ky / (Cy * Dy + self.EPS)
        Ey = self.coeffs.pEy1 + self.coeffs.pEy2 * dfz
        
        # Horizontal shift (camber effect)
        Shy = self.coeffs.pHy1 + self.coeffs.pHy2 * dfz
        alpha_y = alpha + Shy
        
        # Vertical shift (load effect)
        Svy = (self.coeffs.pVy1 + self.coeffs.pVy2 * dfz) * Fz
        
        return Dy * self._magic_formula(By, Cy, Ey, alpha_y) + Svy
    
    def calc_longitudinal_force(
        self, 
        kappa: float, 
        Fz: float
    ) -> float:

        dfz = self._normalized_load(Fz)
        
        Cx = self.coeffs.pCx1
        mu_x = self.coeffs.pDx1 + self.coeffs.pDx2 * dfz
        Dx = mu_x * Fz
        
        # Longitudinal stiffness
        Kx = Fz * (self.coeffs.pKx1 + self.coeffs.pKx2 * dfz)
        Bx = Kx / (Cx * Dx + self.EPS)
        Ex = self.coeffs.pEx1 + self.coeffs.pEx2 * dfz
        
        # Horizontal shift (inflation pressure effect)
        Shx = self.coeffs.pHx1 + self.coeffs.pHx2 * dfz
        kappa_x = kappa + Shx
        
        # Vertical shift (load effect)
        Svx = (self.coeffs.pVx1 + self.coeffs.pVx2 * dfz) * Fz
        
        return Dx * self._magic_formula(Bx, Cx, Ex, kappa_x) + Svx
    
    def calc_aligning_moment(
        self, 
        alpha: float, 
        Fz: float, 
        Fy: float
    ) -> float:

        dfz = self._normalized_load(Fz)
        
        Bt = self.coeffs.qBz1 + self.coeffs.qBz2 * dfz
        Ct = self.coeffs.qCz1
        Dt = (self.coeffs.qDz1 + self.coeffs.qDz2 * dfz) * Fz
        Et = self.coeffs.qEz1
        Sht = self.coeffs.qHz1
        
        alpha_t = alpha + Sht
        t = Dt * self._magic_formula(Bt, Ct, Et, alpha_t)
        
        return -t * Fy
    
    def calc_combined_forces(
        self, 
        alpha: float, 
        kappa: float, 
        Fz: float, 
        gamma: float = 0.0
    ) -> TyreForces:

        # Isolated forces
        Fy0 = self.calc_lateral_force(alpha, Fz, gamma)
        Fx0 = self.calc_longitudinal_force(kappa, Fz)
        
        # Friction ellipse scaling (combined slip reduces available grip)
        mu_x = abs(Fx0) / (Fz + self.EPS)
        mu_y = abs(Fy0) / (Fz + self.EPS)
        denom = math.sqrt(mu_x**2 + mu_y**2) + self.EPS
        
        # Scale forces to stay within friction limit
        Fx = Fx0 * (mu_x / denom)
        Fy = Fy0 * (mu_y / denom)
        
        # Aligning moment from scaled lateral force
        Mz = self.calc_aligning_moment(alpha, Fz, Fy)
        
        return TyreForces(Fy=Fy, Fx=Fx, Mz=Mz)
    
    def calc_grip_level(
        self, 
        alpha: float, 
        kappa: float, 
        Fz: float
    ) -> float:

        forces = self.calc_combined_forces(alpha, kappa, Fz)
        total_force = math.sqrt(forces.Fx**2 + forces.Fy**2)
        max_force = Fz  # Simplified: mu_max ≈ 1.0
        return min(total_force / (max_force + self.EPS), 1.0)


class PacejkaTyreDegradation:

    def __init__(self, initial_coeffs: Optional[PacejkaCoefficients] = None):
        self.initial_coeffs = initial_coeffs or PacejkaCoefficients()
        self.calculator = PacejkaCalculator(self.initial_coeffs)
    
    def degrade_coefficients(
        self, 
        tyre_age_laps: int, 
        max_life_laps: int = 40
    ) -> PacejkaCoefficients:
        # D coefficient decreases with age (grip loss)
        # Quadratic degradation: D(n) = D0 * (1 - 0.4 * (n/N)^2)
        age_factor = tyre_age_laps / max_life_laps
        d_loss_factor = 1.0 - 0.4 * (age_factor ** 2)
        
        # B coefficient increases with age (less stiff)
        b_increase_factor = 1.0 + 0.15 * age_factor
        
        degraded = PacejkaCoefficients(
            # Scale D coefficients (peak force)
            pDy1=self.initial_coeffs.pDy1 * d_loss_factor,
            pDx1=self.initial_coeffs.pDx1 * d_loss_factor,
            qDz1=self.initial_coeffs.qDz1 * d_loss_factor,
            # Scale B coefficients (stiffness)
            pKy1=self.initial_coeffs.pKy1 / b_increase_factor,
            pKx1=self.initial_coeffs.pKx1 / b_increase_factor,
            # Copy all other coefficients
            pCy1=self.initial_coeffs.pCy1,
            pDy2=self.initial_coeffs.pDy2,
            pEy1=self.initial_coeffs.pEy1,
            pEy2=self.initial_coeffs.pEy2,
            pKy2=self.initial_coeffs.pKy2,
            pHy1=self.initial_coeffs.pHy1,
            pHy2=self.initial_coeffs.pHy2,
            pVy1=self.initial_coeffs.pVy1,
            pVy2=self.initial_coeffs.pVy2,
            pCx1=self.initial_coeffs.pCx1,
            pDx2=self.initial_coeffs.pDx2,
            pEx1=self.initial_coeffs.pEx1,
            pEx2=self.initial_coeffs.pEx2,
            pEx3=self.initial_coeffs.pEx3,
            pKx2=self.initial_coeffs.pKx2,
            pHx1=self.initial_coeffs.pHx1,
            pHx2=self.initial_coeffs.pHx2,
            pVx1=self.initial_coeffs.pVx1,
            pVx2=self.initial_coeffs.pVx2,
            qBz1=self.initial_coeffs.qBz1,
            qBz2=self.initial_coeffs.qBz2,
            qCz1=self.initial_coeffs.qCz1,
            qDz2=self.initial_coeffs.qDz2,
            qEz1=self.initial_coeffs.qEz1,
            qHz1=self.initial_coeffs.qHz1,
            Fz0=self.initial_coeffs.Fz0,
        )
        return degraded
    
    def estimate_laptime_penalty(
        self, 
        tyre_age_laps: int,
        max_life_laps: int = 40,
        reference_grip: float = 1.0
    ) -> float:

        # Simple linear grip loss model
        age_factor = tyre_age_laps / max_life_laps
        grip_loss = 0.4 * age_factor  # Up to 40% grip loss at end of life
        grip_ratio = 1.0 - grip_loss
        
        # Empirical correlation: 1% grip loss ≈ 0.02s lap time (circuit dependent)
        penalty = (1.0 - grip_ratio) * 0.02 * 60  # Convert to seconds
        return penalty


if __name__ == "__main__":
    calc = PacejkaCalculator()
    
    # Typical F1 corner: 1.5° slip angle, 4000N load
    alpha = math.radians(1.5)
    Fz = 4000.0
    kappa = 0.0
    
    forces = calc.calc_combined_forces(alpha, kappa, Fz)
    print(f"Lateral force (Fy): {forces.Fy:.1f} N")
    print(f"Longitudinal force (Fx): {forces.Fx:.1f} N")
    print(f"Aligning moment (Mz): {forces.Mz:.1f} N⋅m")
    
    # Degradation example
    deg = PacejkaTyreDegradation()
    for age in [0, 10, 20, 30, 40]:
        penalty = deg.estimate_laptime_penalty(age, max_life_laps=40)
        print(f"Age {age} laps: {penalty:.3f}s penalty")
