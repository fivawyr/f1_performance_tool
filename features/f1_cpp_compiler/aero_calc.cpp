#include "aero_coefficient.h"
#include <cstdint>
#include <cmath> 

typedef int8_t i8; 
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;

typedef i8 b8;
typedef i32 b32;

typedef float f32;
typedef double f64;
using namespace std;
#define _F32_EPSILON 1.19e-07
#define _F64_EPSILON 2.22e-16

f64 calcLift(f64 alpha, f64 velocity) {
    constexpr i32 n = sizeof(AeroCoefficients::angle_alhpa) / sizeof(f64);
    f64 cl{0.0};
    for (i32 i{0}; i < n - 1; i++) {
        if (alpha >= AeroCoefficients::angle_alhpa[i] && alpha <= AeroCoefficients::angle_alhpa[i + 1]) {
            f64 cl_interpol = (alpha - AeroCoefficients::angle_alhpa[i]) / (AeroCoefficients::angle_alhpa[i + 1] - AeroCoefficients::angle_alhpa[i]);
            cl = AeroCoefficients::Cl[i] + cl_interpol * (AeroCoefficients::Cl[i + 1] - AeroCoefficients::Cl[i]);
            break; 
        }
    }
    return cl * 0.5 * AeroCoefficients::AIR_DENSITY * (velocity * velocity) * AeroCoefficients::WING_AERA;
}

f64 calcDownforce(f64 alpha, f64 velocity) {
    f64 downforce = calcLift((-alpha), velocity);
    return downforce; 
} 

f64 calcDrag(f64 alpha, f64 velocity) {
    constexpr i32 n = sizeof(AeroCoefficients::angle_alhpa) / sizeof(f64);
    f64 cd{0.0};
    for (i32 i{0}; i < n - 1; i++) {
        if (alpha >= AeroCoefficients::angle_alhpa[i] && alpha <= AeroCoefficients::angle_alhpa[i + 1]) {
            f64 cd_interpol = (alpha - AeroCoefficients::angle_alhpa[i]) / (AeroCoefficients::angle_alhpa[i + 1] - AeroCoefficients::angle_alhpa[i]);
            cd = AeroCoefficients::Cl[i] + cd_interpol * (AeroCoefficients::Cd[i + 1] - AeroCoefficients::Cl[i]);
            break; 
        }
    }
    return cd * 0.5 * AeroCoefficients::AIR_DENSITY * (velocity * velocity) * AeroCoefficients::WING_AERA;
}