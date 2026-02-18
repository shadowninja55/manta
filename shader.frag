#version 460 core
out vec4 frag_color;
uniform float height;
uniform uint frame;
uniform float fov;
uniform vec3 pos;
uniform vec3 look;
in vec2 ndc;

struct Ray {
  vec3 o;
  vec3 d;
};

vec3 at(Ray r, float t) {
  return r.o + t * r.d;
}

struct Material {
  uint k;
  vec3 a;
  float f;
};

struct Sphere {
  vec3 c;
  float r;
  Material m;
};

struct Hit {
  float t;
  vec3 p;
  vec3 n;
  Material m;
};

const uint MATTE = 0;
const uint METAL = 1;
const Material NOTHING = Material(-1, vec3(-1), -1);

const float PI = 3.14159265359;
const float INF = 1.0 / 0.0;
const vec3 UP = vec3(0, 1, 0);
const Hit MISS = Hit(-1, vec3(0), vec3(0), NOTHING);
const uint MAX_DEPTH = 5;
const uint SAMPLES = 100;

Sphere scene[4] = Sphere[](
  // ground
  Sphere(
    vec3(0, -100.5, -1), 100, 
    Material(MATTE, vec3(0.8, 0.8, 0), -1)
  ),
  // center
  Sphere(
    vec3(0, 0, -1.2), 0.5,
    Material(MATTE, vec3(0.1, 0.2, 0.5), -1)
  ),
  // left
  Sphere(
    vec3(-1, 0, -1), 0.5,
    Material(METAL, vec3(0.8), 0.3)
  ),
  // u
  Sphere(
    vec3(1, 0, -1), 0.5,
    Material(METAL, vec3(0.8, 0.6, 0.2), 1.0)
  )
);

Hit hit_sphere(Sphere sphere, Ray r, float ta, float tb) {
  vec3 oc = sphere.c - r.o;
  float a = dot(r.d, r.d);
  float h = dot(r.d, oc);
  float c = dot(oc, oc) - sphere.r * sphere.r;
  float d = h * h - a * c;

  if (d < 0) return MISS;

  float rd = sqrt(d);
  float t = (h - rd) / a;
  if (t < ta || t > tb) {
    t = (h + rd) / a;
    if (t < ta || t > tb) return MISS;
  }

  vec3 p = at(r, t);
  return Hit(t, p, (p - sphere.c) / sphere.r, sphere.m);
}

uint hash(uint n) {
  n ^= n >> 16;
  n *= 0x7feb352d;
  n ^= n >> 15;
  n *= 0x846ca68b;
  n ^= n >> 16;
  return n;
}

float rand(inout uint seed) {
  seed = hash(seed);
  return float(seed) / 4294967296.0;
}

vec3 rand_unit(inout uint seed) {
  float u1 = rand(seed);
  float u2 = rand(seed);
  float z = 1 - 2 * u1;
  float r = sqrt(max(0, 1 - z * z));
  float phi = 2 * PI * u2;
  return vec3(r * cos(phi), r * sin(phi), z);
}

void main() {
  uint seed = uint(gl_FragCoord.x)
    + uint(gl_FragCoord.y) * 4096u 
    + frame * 1315423911u;

  // viewport and camera
  float px = 2 / height;
  float h = tan(radians(fov) / 2);
  vec3 u = normalize(cross(look, UP));
  vec3 v = cross(u, look);
  vec3 accrual = vec3(0);

  // sampling for antialiasing
  for (int s = 0; s < SAMPLES; s++) {
    vec3 color = vec3(1);
    vec2 offset = px * (vec2(rand(seed), rand(seed)) - 0.5);
    vec2 target = (ndc + offset) * h;
    vec3 dir = look + target.x * u + target.y * v;
    Ray ray = Ray(pos, dir);

    // limit ray depth
    for (int d = 0; d < MAX_DEPTH; d++) {
      // find nearest sphere intersection
      Hit nearest = Hit(INF, vec3(0), vec3(0), NOTHING);
      for (int i = 0; i < scene.length(); i++) {
        Hit hit = hit_sphere(scene[i], ray, 0.001, nearest.t);
        if (hit.t > 0) nearest = hit;
      }

      if (nearest.t < INF) {
        // object hit
        Material mat = nearest.m;
        vec3 bounce = mat.k == MATTE
          ? nearest.n + rand_unit(seed)
          : normalize(reflect(ray.d, nearest.n)) + mat.f * rand_unit(seed);
        ray = Ray(nearest.p, bounce);
        color *= mat.a;
      } else {
        // skybox
        float p = 0.5 * (ray.d.y / length(ray.d) + 1);
        color *= mix(vec3(1), vec3(0.5, 0.7, 1), p);
        accrual += color;
        break;
      }
    }

    // ray didn't finish within fixed depth, black
  }

  // gamma correction
  frag_color = vec4(sqrt(accrual / SAMPLES), 1);
}
