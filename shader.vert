#version 460 core
in vec3 pos;
uniform float aspect;
out vec2 ndc;

void main() {
  gl_Position = vec4(pos, 1.0);
  ndc = pos.xy * vec2(aspect, 1);
}
