# coding=utf-8
# overlay/vanishing_point_element.py
# 消失点Overlay元素示例

import OpenGL.GL as gl
import numpy as np
from .base_overlay_element import \
    BaseOverlayElement


class VanishingPointElement(
    BaseOverlayElement):
    """
    A draggable vanishing point element.
    一个可拖拽的消失点元素。

    When hovered, changes color.
    When dragged, moves its position.
    """

    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 10

        self.dragging = False
        self.drag_offset = (0, 0)

    @property
    def position(self):
        return (self.x, self.y)

    def hit_test(self, mouse_x,
                 mouse_y):
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = np.sqrt(
            dx * dx + dy * dy)
        return dist <= self.radius

    def render(self, viewport_size):
        w, h = viewport_size
        # 设置2D绘制环境
        gl.glMatrixMode(
            gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, w, h, 0, -1, 1)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        # 根据状态选择颜色
        if self.is_hovered:
            gl.glColor3f(1.0, 0.5, 0.0)
        else:
            gl.glColor3f(1.0, 1.0, 0.0)

        # 绘制圆点
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glVertex2f(self.x, self.y)
        segments = 32
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            gl.glVertex2f(
                self.x + self.radius * np.cos(
                    angle),
                self.y + self.radius * np.sin(
                    angle))
        gl.glEnd()

        # 恢复矩阵
        gl.glPopMatrix()
        gl.glMatrixMode(
            gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def on_mouse_press(self, mouse_x,
                       mouse_y):
        # 开始拖拽
        self.dragging = True
        self.drag_offset = (
        self.x - mouse_x,
        self.y - mouse_y)

    def on_mouse_move(self, mouse_x,
                      mouse_y, dx, dy):
        if self.dragging:
            self.x = mouse_x + \
                     self.drag_offset[0]
            self.y = mouse_y + \
                     self.drag_offset[1]

    def on_mouse_release(self, mouse_x,
                         mouse_y):
        self.dragging = False
