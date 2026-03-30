#include <iostream>
#include <cstdint>
#include <cmath>
#include <vector>
#include <GLFW/glfw3.h>

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

#define PI 3.14159265358979323846

GLFWwindow* StartGLFW();
f32 GravityPropertiesSpace(const string& planet);
f32 GravityPropertiesEarth(const string& EarthPosition);
void DrawCircle(f32 centerX, f32 centerY, f32 radius, i32 res);
void DistanceVectorR(f32& distanceSq, f32& distance, Body& a, Body& b); const f32 gravitationConstant = 6.6430e-11;
f32 gravitationEquator = 9.801f; 
f32 gravitationPole = 9.867f;
f32 screenHeight = 1000.0f;       
f32 screenWidth = 800.0f;

struct Body {
  f32 x, y;
  f32 vx, vy;
  f32 mass;
  f32 radius;
};

int main() {
  GLFWwindow* window = StartGLFW();
  if (!window) return -1;

  Body earthBall = { 250.0f, 50.0f, 0.0f, 0.0f, 10.0f, 25.0f };
  f32 gravityEarth = GravityPropertiesEarth("Equator");

  string choosenPlanet = "Mercury";
  Body planetBall = { 550.0f, 50.0f, 0.0f, 0.0f, 10.0f, 25.0f };
  f32 gravityPlanet = GravityPropertiesSpace(choosenPlanet);

  f32 floorY = 560.0f;            
  f32 bounceFactor = -0.7f;
  f32 scale = 20.0f;

  f64 lastTime = glfwGetTime();

  while (!glfwWindowShouldClose(window)) {
    f64 currentTime = glfwGetTime();
    f32 dt = static_cast<f32>(currentTime - lastTime);
    lastTime = currentTime;

    earthBall.vy += gravityEarth * scale * dt;
    earthBall.y += earthBall.vy * dt;  
    if (earthBall.y >= floorY) {       
      earthBall.y = floorY;
      earthBall.vy *= bounceFactor;
    }

    planetBall.vy += gravityPlanet * scale * dt;
    planetBall.y += planetBall.vy * dt;
    if (planetBall.y >= floorY) {     
      planetBall.y = floorY;          
      planetBall.vy *= bounceFactor;
    }

    glClear(GL_COLOR_BUFFER_BIT);
    DrawCircle(earthBall.x, earthBall.y, earthBall.radius, 50);
    DrawCircle(planetBall.x, planetBall.y, planetBall.radius, 50); 
    glfwSwapBuffers(window);
    glfwPollEvents();
  }

  glfwTerminate(); 
  return 0;
}

void DrawCircle(f32 centerX, f32 centerY, f32 radius, i32 res) {
  glBegin(GL_TRIANGLE_FAN);
  glVertex2f(centerX, centerY);  
  for (i32 i = 0; i <= res; i++) { 
    f32 angle = 2.0f * PI * (static_cast<f32>(i) / res);
    f32 x = centerX + cosf(angle) * radius;
    f32 y = centerY + sinf(angle) * radius;
    glVertex2f(x, y);            
  }
  glEnd();
}

f32 GravityPropertiesEarth(const string& EarthPosition) {
  if (EarthPosition == "NorthPole" || EarthPosition == "SouthPole") 
    return gravitationPole;
  return gravitationEquator;
}

f32 GravityPropertiesSpace(const string& planet) {
  if (planet == "Mercury") return 3.7f;
  if (planet == "Venus")   return 8.87f;
  if (planet == "Mars")    return 3.72f;
  if (planet == "Jupiter") return 24.79f;
  if (planet == "Saturn")  return 10.44f;
  if (planet == "Uranus")  return 8.69f;
  if (planet == "Neptune") return 11.15f;
  return 9.801f;
}

void DistanceVectorR(f32& distanceSq, f32& distance, Body& a, Body& b) { 
  f32 dx = b.x - a.x;
  f32 dy = b.y - a.y;
  distanceSq = (dx * dx) + (dy * dy);
  distance = sqrtf(distanceSq);  
}

GLFWwindow* StartGLFW() {
  if (!glfwInit()) {
    cerr << "Failed to initialize GLFW\n";
    return nullptr;
  }
  GLFWwindow* window = glfwCreateWindow(1000, 800, "Gravitation Simulation", NULL, NULL); 
  if (!window) {
    glfwTerminate();
    return nullptr;
  }
  glfwMakeContextCurrent(window);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glOrtho(0.0, 1000.0, 800.0, 0.0, -1.0, 1.0);
  return window;
}
