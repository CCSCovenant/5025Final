# coding=utf-8
# overlay/vanishing_point_element.py

from .base_overlay_element import BaseOverlayElement
import OpenGL.GL as gl
import numpy as np

class VanishingPointElement(BaseOverlayElement):
    def __init__(self, x, y, index,update_callback=None):
        """
        :param index: int 指定该消失点的索引(0,1,2)
        :param update_callback: callable，当位置更新时调用 update_callback(index, x, y)
        """
        super().__init__(x,y)
        self.radius = 10
        self.dragging = False
        self.drag_offset = (0,0)
        self.index = index
        self.update_callback = update_callback
        self.active = False

    def set_active(self, state):
        self.active = state
    @property
    def position(self):
        return (self.x, self.y)

    def hit_test(self, mouse_x, mouse_y):
        if not self.active:
            return False
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = np.sqrt(dx*dx + dy*dy)
        return dist <= self.radius

    def render(self, viewport_size):
        if not self.active:
            return
        w, h = viewport_size
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, w, h, 0, -1, 1)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        if self.is_hovered:
            gl.glColor3f(1.0, 0.5, 0.0)
        else:
            gl.glColor3f(1.0, 1.0, 0.0)

        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glVertex2f(self.x, self.y)
        segments = 32
        for i in range(segments+1):
            angle = 2*np.pi*i/segments
            gl.glVertex2f(self.x+self.radius*np.cos(angle), self.y+self.radius*np.sin(angle))
        gl.glEnd()

        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def on_mouse_press(self, mouse_x, mouse_y):
        if not self.active:
            return
        self.dragging = True
        self.drag_offset = (self.x - mouse_x, self.y - mouse_y)

    def on_mouse_move(self, mouse_x, mouse_y, dx, dy):
        if self.dragging and self.active:
            self.x = mouse_x + self.drag_offset[0]
            self.y = mouse_y + self.drag_offset[1]
            if self.update_callback:
                self.update_callback(
                    self.index,
                    self.x,
                    self.y)


    def on_mouse_release(self, mouse_x, mouse_y):
        if not self.active:
            return
        self.dragging = False

