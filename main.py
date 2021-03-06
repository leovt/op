import sys
import logging.config
import ctypes
import pickle

import pyglet
from pyglet import gl
from pyglet.window import key

import shaders
from gltools.glprogram import GlProgram
from gltools import gltexture

import terrain

class Application:
    def __init__(self, window):
        self.window = window
        self.initialize_gl()
        try:
            with open('terrain.pickle', 'rb') as f:
                self.terrain = pickle.load(f)
        except Exception:
            logging.exception('Could not load terrain - Starting with default terrain.')
            self.terrain = terrain.Terrain(20,20)
        self.pointed = (-1, -1, -1)
        self.profile = True
        self._cached_terrain_data = None

    def update(self, dt):
        pass

    def initialize_gl(self):
        self.program = GlProgram(shaders.vertex_scene, shaders.fragment_scene)
        self.program.uniform2f(b'scroll_offset', 0, 0)
        self.sprite_program = GlProgram(shaders.vertex_scene, shaders.fragment_sprite)
        self.sprite_texture = gltexture.make_texture('sprites.png')
        self.buffer = gl.GLuint(0)
        gl.glGenBuffers(1, ctypes.pointer(self.buffer))

        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def on_resize(self, width, height):
        gl.glViewport(0, 0, width, height)
        self.program.uniform2f(b'screen_size', width, height)
        self.vp_width = width
        self.vp_height = height

    def on_draw(self):
        if self.profile:
            self.profile = False
            import cProfile
            cProfile.runctx('self.on_draw()', globals(), locals())
        else:
            self._on_draw()

    def _on_draw(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        STRIDE = 8

        self.program.use()
        self.program.vertex_attrib_pointer(self.buffer, b"position", 4, stride=STRIDE * ctypes.sizeof(gl.GLfloat))
        self.program.vertex_attrib_pointer(self.buffer, b"color", 4, stride=STRIDE * ctypes.sizeof(gl.GLfloat), offset=4 * ctypes.sizeof(gl.GLfloat))

        if self.terrain.dirty or not self._cached_terrain_data:
            data = ( float(d)
                for (x,y,z,c,u,v,(r,g,b,a),lum) in self.terrain.vertex_data()
                for d in (x+u,y+v,z,1, r*lum,g*lum,b*lum,a)
            )
            data = (gl.GLfloat * (STRIDE * self.terrain.nb_vertices()))(*data)
            self._cached_terrain_data = data
        else:
            data = self._cached_terrain_data
        gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data), data, gl.GL_DYNAMIC_DRAW)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.terrain.nb_vertices())

        self.sprite_program.use()
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.sprite_texture)
        self.sprite_program.uniform1i(b'tex', 0)
        x,y,cp = self.pointed

        utex = [0.0, 1.0/16, 1.0/16, 0.0]
        vtex = [0.0, 0.0, 1.0/16, 1.0/16]

        data = ( float(d)
            for (x,y,z,c,u,v,(r,g,b,a),lum) in self.terrain.vertex_data_tile(x,y)
            for d in (x+u, y+v, z+1.0/256, 1, utex[(c-cp)%4], vtex[(c-cp)%4], 0.0, 0.0)
        )
        data = (gl.GLfloat * (STRIDE * 6))(*data)

        gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data), data, gl.GL_DYNAMIC_DRAW)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)


    def on_key_press(self, symbol, modifiers):
        logging.debug('Key Press {} {}'.format(symbol, modifiers))
        if symbol == key.I:
            logging.info('FPS: {}'.format(pyglet.clock.get_fps()))
        if symbol == key.P:
            self.profile = True

    def on_mouse_motion(self, x, y, dx, dy):
        depth = gl.GLfloat(0.0)
        gl.glReadPixels(x, y, 1, 1, gl.GL_DEPTH_COMPONENT, gl.GL_FLOAT, ctypes.pointer(depth))
        xn = 2.0 * x / self.vp_width - 1.0
        yn = 2.0 * y / self.vp_height - 1.0
        zn = 2.0 * depth.value - 1.0

        xs = 2.5*xn + 5.0*zn
        ys = -2.5*xn + 5.0*zn

        u = xs-int(xs)
        v = ys-int(ys)

        if u<0.5 and v<0.5:
            c = 2
        elif u<0.5:
            c = 1
        elif v<0.5:
            c = 3
        else:
            c = 0
        self.pointed = (int(xs), int(ys), c)
        #logging.debug('(%d, %d) -> (%0.2f,  %0.2f, %0.2f) -> (%0.2f, %0.2f) -> %s' % (x,y,xn,yn,zn,xs,ys,self.pointed))

    def on_mouse_press(self, x, y, button, modifiers):
        self.drag_start = (x,y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if y-self.drag_start[1] < -20:
            self.terrain.move_corner(self.pointed[0], self.pointed[1], self.pointed[2], -1)
            self.drag_start = (self.drag_start[0], self.drag_start[1] - 20)
        elif y-self.drag_start[1] > 20:
            self.terrain.move_corner(self.pointed[0], self.pointed[1], self.pointed[2], 1)
            self.drag_start = (self.drag_start[0], self.drag_start[1] + 20)

    def on_exit(self):
        with open('terrain.pickle', 'wb') as f:
            pickle.dump(self.terrain, f)

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
        app.on_exit()

    except:
        logging.exception('Uncaught Exception')
        sys.exit(1)

if __name__ == '__main__':
    main()
