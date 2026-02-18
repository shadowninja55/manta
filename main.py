import moderngl as mgl
import glfw
import numpy as np

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

pos = np.array([-2, 2, 1])
target = np.array([0, 0, -1])
look = target - pos

program["fov"] = 30
program["pos"] = pos
program["look"] = look / np.linalg.norm(look)

# objects
vertices = np.array([
  [-1, -1, 0],
  [3, -1, 0],
  [-1, 3, 0],
], dtype=np.float32)
vbo = ctx.buffer(vertices)
vao = ctx.simple_vertex_array(program, vbo, "pos")

# callbacks
def on_resize(window, width, height):
  ctx.viewport = (0, 0, width, height)
  program["aspect"] = width / height
  program["height"] = height

def on_input(window):
  if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
    glfw.set_window_should_close(window, True)

def on_scroll(window, x, y):
  program["fov"] = np.clip(program["fov"].value - y, 10, 170)

glfw.set_framebuffer_size_callback(window, on_resize)
width, height = glfw.get_framebuffer_size(window)
on_resize(window, width, height)

glfw.set_scroll_callback(window, on_scroll)

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
