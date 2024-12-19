# coding=utf-8
# overlay/base_overlay_element.py
# Overlay元素基类

import OpenGL.GL as gl
import numpy as np


class BaseOverlayElement:
    """
    Base class for overlay elements.
    An overlay element:
      - has a position in screen space
      - can be hovered/selected
      - can be moved (if applicable)
      - can render itself on top of the canvas.

    Overlay元素基类，具有屏幕空间坐标、可被hover、可交互、可绘制在画布之上。
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_hovered = False
        self.is_selected = False

    def render(self, viewport_size):
        """
        Render the element onto the overlay.
        在overlay上渲染元素。

        :param viewport_size: (width, height)
        """
        pass

    def hit_test(self, mouse_x,
                 mouse_y):
        """
        Test if mouse position hits this element.
        测试鼠标点是否命中该元素。

        :param mouse_x: float
        :param mouse_y: float
        :return: bool - True if hit
        """
        return False

    def on_mouse_press(self, mouse_x,
                       mouse_y):
        pass

    def on_mouse_move(self, mouse_x,
                      mouse_y, dx, dy):
        pass

    def on_mouse_release(self, mouse_x,
                         mouse_y):
        pass
