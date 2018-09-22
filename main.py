import sys
import logging.config
import ctypes

import pyglet
from pyglet import gl
from pyglet.window import key

import shaders
from gltools.glprogram import GlProgram

import terrain

class Application:
    def __init__(self, window):
        self.window = window
        self.initialize_gl()
        self.terrain = terrain.Terrain(5,5)

    def update(self, dt):
        pass

    def initialize_gl(self):
        self.program = GlProgram(shaders.vertex_scene, shaders.fragment_scene)

        self.buffer = gl.GLuint(0)
        gl.glGenBuffers(1, ctypes.pointer(self.buffer))

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)

    def on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        STRIDE = 8

        self.program.use()
        self.program.vertex_attrib_pointer(self.buffer, b"position", 4, stride=STRIDE * ctypes.sizeof(gl.GLfloat))
        self.program.vertex_attrib_pointer(self.buffer, b"color", 4, stride=STRIDE * ctypes.sizeof(gl.GLfloat), offset=4 * ctypes.sizeof(gl.GLfloat))

        data = ( float(d)
            for (x,y,z) in self.terrain.vertex_data()
            for d in (x,y,z,1, 0,0.5,0,1.0)
        )

        data = (gl.GLfloat * (STRIDE * self.terrain.nb_vertices()))(*data)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data), data, gl.GL_DYNAMIC_DRAW)
        gl.glDrawArrays(gl.GL_QUADS, 0, self.terrain.nb_vertices())

    def on_key_press(self, symbol, modifiers):
        logging.debug('Key Press {} {}'.format(symbol, modifiers))
        if symbol == key.I:
            logging.info('FPS: {}'.format(pyglet.clock.get_fps()))

def initialize_gl(context):
    logging.info('OpenGL Version {}'.format(context.get_info().get_version()))
    gl.glClearColor(0.5, 0.5, 0.35, 1)

def main():
    logging.config.fileConfig('logging.conf')
    try:
        window = pyglet.window.Window(resizable=True)
        initialize_gl(window.context)

        app = Application(window)
        window.push_handlers(app)

        pyglet.clock.schedule_interval(app.update, 0.01)
        pyglet.app.run()

    except:
        logging.exception('Uncaught Exception')
        sys.exit(1)

if __name__ == '__main__':
    main()
