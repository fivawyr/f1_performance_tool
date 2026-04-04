#pragma once 

typedef double f64;
//all values for the coefficients are based on the literature: "Tire and Vehicle Dynamics". 
//in reality, you would get the values by 1. the tyre manufactor or self tested. 

struct PacejkaCoefficients {
    
    f64 pCy1 = 1.3;  // Lateral shape
    f64 pDy1 = 1.0;  // Lateral peak coefficient base
    f64 pDy2 = -0.1; // Lateral peak coefficient load dependency
    f64 pEy1 = -1.0; // Lateral curvature base
    f64 pEy2 = -0.5; // Lateral curvature load dependency
    f64 pKy1 = 10.0; 
    f64 pKy2 = 1.5;
    f64 pHy1 = 0.003; 
    f64 pHy2 = 0.001;
    f64 pVy1 = 0.04; 
    f64 pVy2 = -0.04;

    f64 pCx1 = 1.65;  // Longitudinal
    f64 pDx1 = 1.1;
    f64 pDx2 = -0.1;
    f64 pEx1 = 0.3;
    f64 pEx2 = 0.15;
    f64 pEx3 = 0.0;
    f64 pKx1 = 12.0;
    f64 pKx2 = 10.0;
    f64 pHx1 = 0.002;
    f64 pHx2 = 0.0;
    f64 pVx1 = 0.0;
    f64 pVx2 = 0.0;

    f64 qBz1 = 9.0;
    f64 qBz2 = -1.5;
    f64 qCz1 = 1.1;
    f64 qDz1 = 0.1;
    f64 qDz2 = -0.02;
    f64 qEz1 = -1.0;
    f64 qHz1 = 0.005;

    f64 Fz0 = 4000.0; // Nominal load [N]
}; 
