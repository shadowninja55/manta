import moderngl as mgl
import glfw
import numpy as np
import math

# glfw
assert glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

assert (window := glfw.create_window(800, 800, "manta", None, None))
glfw.make_context_current(window)
ctx = mgl.create_context()

# shaders
with open("shader.vert") as f:
  vertex_shader = f.read()
with open("shader.frag") as f:
  fragment_shader = f.read()
program = ctx.program(vertex_shader, fragment_shader)

# objects
vertices = np.array([
  [-1, -1, 0],
  [3, -1, 0],
  [-1, 3, 0],
], dtype=np.float32)
vbo = ctx.buffer(vertices)
vao = ctx.simple_vertex_array(program, vbo, "pos")

# state
ZOOM_SPEED = 0.002
MOVE_SPEED = 0.2
yaw = pitch = 0

program["fov"] = 30
program["pos"] = np.array([-2, 2, 1])

# helpers
def axis(window, a, b):
  return (glfw.get_key(window, a) == glfw.PRESS) - (glfw.get_key(window, b) == glfw.PRESS)

# callbacks
def on_resize(window, width, height):
  ctx.viewport = (0, 0, width, height)
  program["aspect"] = width / height
  program["height"] = height

def on_input(window):
  # quit
  if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
    glfw.set_window_should_close(window, True)

  # cursor
  if glfw.get_key(window, glfw.KEY_EQUAL) == glfw.PRESS:
    mode = glfw.get_input_mode(window, glfw.CURSOR)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL if mode == glfw.CURSOR_DISABLED else glfw.CURSOR_DISABLED)

  # camera movement
  ws = axis(window, glfw.KEY_W, glfw.KEY_S)
  longitudinal = ws * np.array([math.cos(yaw), 0, math.sin(yaw)])

  ad = axis(window, glfw.KEY_A, glfw.KEY_D)
  lateral = ad * np.array([math.cos(yaw + math.pi / 2), 0, math.sin(yaw + math.pi / 2)])

  vertical = np.array([0, axis(window, glfw.KEY_SPACE, glfw.KEY_LEFT_SHIFT), 0])
  
  move = longitudinal - lateral + vertical
  if (mag := np.linalg.norm(move)):
    program["pos"].value += move / mag * MOVE_SPEED

def on_scroll(window, x, y):
  program["fov"] = np.clip(program["fov"].value - y, 10, 170)

def on_cursor_pos(window, x, y):
  global yaw, pitch
  yaw = ZOOM_SPEED * x % math.tau
  pitch = np.clip(ZOOM_SPEED * -y, -math.pi / 2, math.pi / 2)
  program["look"] = (
    math.cos(yaw) * math.cos(pitch),
    math.sin(pitch),
    math.sin(yaw) * math.cos(pitch),
  )

glfw.set_framebuffer_size_callback(window, on_resize)
width, height = glfw.get_framebuffer_size(window)
on_resize(window, width, height)

glfw.set_scroll_callback(window, on_scroll)
glfw.set_cursor_pos_callback(window, on_cursor_pos)

glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# loop
frame = 0
while not glfw.window_should_close(window):
  # input
  on_input(window)

  # update
  program["frame"] = frame
  # frame += 1

  # render
  vao.render(mgl.TRIANGLES)
  glfw.swap_buffers(window)
  glfw.poll_events()
