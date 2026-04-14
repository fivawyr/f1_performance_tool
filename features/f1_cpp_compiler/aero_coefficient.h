#pragma once 

typedef float f32;
typedef double f64;

// at this moment, we getting the data from NACA 2412 database (check out the reference made in the README)

struct AeroCoefficients {
    static constexpr f64 angle_alhpa[] = {
        -2.0, 0.0, 2.0, 4.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0
    }; 
    static constexpr f64 Cl[] = {
        0.0272, 0.2442, 0.4549, 0.7153, 0.9016, 1.0885, 1.2696, 1.4114, 1.5228, 1.5775, 1.5415 //stall @ 18.0
    }; 
    static constexpr f64 Cd[] = {
        0.00640, 0.005680 0.00581, 0.00711, 0.00945, 0.01270, 0.01591, 0.02015, 0.02622, 0.03935, 0.06805
    };
    static constexpr f32 AIR_DENSITY = 1.225; // always same, kg/m³
    static constexpr f32 WING_AERA = 0.5;
};

