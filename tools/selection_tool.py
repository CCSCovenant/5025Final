# tools/selection_tool.py

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
import OpenGL.GL as gl
import numpy as np

from .base_tool import BaseTool

class SelectionTool(BaseTool):
    def __init__(self, selection_manager, radius=50):
        super().__init__()
        self.selection_manager = selection_manager
        self.radius = radius
        self.mouse_pos = None

    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            # 获取当前 hovered_strokes
            hovered = self.selection_manager.hovered_strokes
            if event.modifiers() & Qt.ShiftModifier:
                # 多选
                self.selection_manager.add_to_selection(hovered)
            else:
                # 覆盖式选择
                self.selection_manager.set_selection(hovered)
            canvas_widget.update()
        elif event.button() == Qt.RightButton:
            # 获取当前 hovered_strokes
            selected = self.selection_manager.selected_strokes

            for s in selected:
                canvas_widget.stroke_manager_3d.remove_stroke(s.stroke_id)
            canvas_widget.update()
        self.mouse_pos = (event.x(),event.y())

    def mouse_move(self, event, canvas_widget):
        # 实时更新 hovered_strokes
        self.mouse_pos = (event.x(), event.y())
        # 需要先做3D->2D投影, stroke.screen_coords 应该由 canvas_widget / renderer维护
        strokes_3d = canvas_widget.get_all_strokes_for_selection()
        hovered = self.selection_manager.find_strokes_in_circle(
            strokes_3d, self.mouse_pos, self.radius
        )
        self.selection_manager.set_hovered(hovered)
        canvas_widget.update()

    def mouse_release(self, event, canvas_widget):
        pass  # 点击时已经处理完选择逻辑

    def wheelEvent(self, event,canvas_widget):
        pass
    def render_tool_icon(self, renderer,
               viewport_size):
        """
        绘制悬浮时的图标。
        """
        if self.mouse_pos:
            cx, cy = self.mouse_pos
            radius = self.radius   # 图标半径
            w, h = viewport_size

            # 保存当前的 OpenGL 状态
            gl.glPushAttrib(
                gl.GL_ENABLE_BIT | gl.GL_CURRENT_BIT)
            gl.glDisable(
                gl.GL_DEPTH_TEST)  # 禁用深度测试，确保圆形显示在最前面

            # 设置2D正交投影
            gl.glMatrixMode(
                gl.GL_PROJECTION)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glOrtho(0, w, h, 0, -1,
                       1)  # 2D 正交投影

            gl.glMatrixMode(
                gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glLoadIdentity()

            # 绘制圆圈
            gl.glColor3f(1.0, 0.0,
                         0.0)  # 红色圆圈
            segments = 64
            gl.glBegin(gl.GL_LINE_LOOP)
            for i in range(segments):
                angle = 2 * np.pi * i / segments
                x = cx + radius * np.cos(
                    angle)
                y = cy + radius * np.sin(
                    angle)
                gl.glVertex2f(x, y)
            gl.glEnd()

            # 恢复矩阵
            gl.glPopMatrix()
            gl.glMatrixMode(
                gl.GL_PROJECTION)
            gl.glPopMatrix()

            # 恢复 OpenGL 状态
            gl.glPopAttrib()

            gl.glMatrixMode(
                gl.GL_MODELVIEW)
    def set_radius(self, r):
        self.radius = r
