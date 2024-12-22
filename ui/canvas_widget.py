# coding=utf-8
# ui/canvas_widget.py
from PyQt5.QtWidgets import \
    QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from data.stroke_manager_2d import \
    StrokeManager2D
from data.stroke_manager_3d import \
    StrokeManager3D
from logic.vanishing_point_manager import \
    VanishingPointManager

from rendering.ground_plane_3d import \
    GroundPlane3D
from rendering.renderer_3d import \
    Renderer3D
from logic.selection_manager import \
    SelectionManager

# 新增
from overlay.overlay_manager import \
    OverlayManager
from overlay.vanishing_point_element import \
    VanishingPointElement

import OpenGL.GL as gl

class CanvasWidget(QOpenGLWidget):
    """
    The main canvas widget for rendering and interaction.
    Now includes overlay manager for interactive overlays.

    主画布部件，现在包含overlay层进行叠加元素的交互和显示。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.stroke_manager_2d = StrokeManager2D()
        self.stroke_manager_3d = StrokeManager3D()

        self.viewable2d_stroke = []

        self.selection_manager = SelectionManager()
        self.renderer = Renderer3D()

        self.setMouseTracking(True)
        self.current_tool = None
        self.temp_stroke_2d = None


        # Camera params
        self.camera_rot = [0.0, 0.0]
        self.camera_distance = 3.0

        # 创建VanishingPointManager
        self.overlay_manager = OverlayManager()

        self.groundPlane = GroundPlane3D()

        self.vanishing_point_manager = VanishingPointManager()
        self.vanishing_point_manager.set_overlay_manager(
            self.overlay_manager)

        self.last_mouse_pos = QPoint()

    def set_tool(self, tool):
        self.current_tool = tool
        self.update()

    def get_all_strokes_for_selection(
            self):
        strokes = self.stroke_manager_3d.get_all_strokes()

        return strokes

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        self.render3d_strokes()
        self.render2d_strokes()

        # Render overlay elements on top
        self.overlay_manager.render((
                                    self.width(),
                                    self.height()))

    def render2d_strokes(self):
        # 这里可以用一个 2D Renderer, 或者简单地在正交投影下画 line strips:
        strokes_2d = self.viewable2d_stroke.copy()
        if self.temp_stroke_2d:
            strokes_2d.append(self.temp_stroke_2d)
        w, h = self.width(), self.height()
        gl.glMatrixMode(
            gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, w, h, 0, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        for s2d in strokes_2d:
            pts = s2d.points_2d
            if len(pts) < 2:
                continue
            gl.glColor3f(1.0, 1.0, 1.0)
            gl.glBegin(gl.GL_LINE_STRIP)
            for (x, y) in pts:
                gl.glVertex2f(x, y)
            gl.glEnd()

        gl.glPopMatrix()
        gl.glMatrixMode(
            gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def render3d_strokes(self):
        strokes_3d = list(
            self.stroke_manager_3d.get_all_strokes())
        self.renderer.render(
            strokes_3d,
            camera_rot=self.camera_rot,
            camera_dist=self.camera_distance,
            viewport_size=(self.width(),
                           self.height()),
            ground_plane=self.groundPlane,
            activated_tool=self.current_tool
        )
    # Event handling
    def mousePressEvent(self, event):
        # First let overlay try to handle
        if self.overlay_manager.mouse_press_event(
                event,self):
            return
        # If not handled by overlay, pass to tool
        if self.current_tool:
            self.current_tool.mouse_press(
                event, self)
        else:
            super().mousePressEvent(
                event)

    def mouseMoveEvent(self, event):
        consumed = self.overlay_manager.mouse_move_event(
            event, self.last_mouse_pos,self)
        if not consumed:
            if self.current_tool:
                self.current_tool.mouse_move(
                    event, self)
            else:
                super().mouseMoveEvent(
                    event)
        self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.overlay_manager.mouse_release_event(
            event,self)
        if self.current_tool:
            self.current_tool.mouse_release(
                event, self)
        else:
            super().mouseReleaseEvent(
                event)

    def undo_stroke(self):
        self.stroke_manager_3d.undo()
        self.stroke_manager_2d.undo()
        self.update()

    def redo_stroke(self):
        self.stroke_manager_3d.redo()
        self.stroke_manager_2d.redo()
        self.update()

