# coding=utf-8
# ui/canvas_widget.py
from PyQt5.QtWidgets import \
    QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from data.stroke_manager_2d import \
    StrokeManager2D
from data.stroke_manager_3d import \
    StrokeManager3D
from rendering.renderer_3d import \
    Renderer3D
from logic.selection_manager import \
    SelectionManager

# 新增
from overlay.overlay_manager import \
    OverlayManager
from overlay.vanishing_point_element import \
    VanishingPointElement


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

        self.selection_manager = SelectionManager()
        self.renderer = Renderer3D()

        self.setMouseTracking(True)
        self.current_tool = None
        self.temp_stroke_3d = None

        # Camera params
        self.camera_rot = [0.0, 0.0]
        self.camera_distance = 3.0

        # Overlay Manager
        self.overlay_manager = OverlayManager()
        # 添加一个默认的消失点
        self.overlay_manager.add_element(
            VanishingPointElement(200,
                                  200))

        self.last_mouse_pos = QPoint()

    def set_tool(self, tool):
        self.current_tool = tool
        self.update()

    def get_all_strokes_for_selection(
            self):
        strokes = self.stroke_manager_3d.get_all_strokes()
        if self.temp_stroke_3d:
            strokes = list(strokes) + [
                self.temp_stroke_3d]
        return strokes

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        strokes_3d = list(
            self.stroke_manager_3d.get_all_strokes())
        if self.temp_stroke_3d:
            strokes_3d.append(
                self.temp_stroke_3d)

        self.renderer.render(
            strokes_3d,
            camera_rot=self.camera_rot,
            camera_dist=self.camera_distance,
            viewport_size=(self.width(),
                           self.height()),
            selection_manager=self.selection_manager,
            activated_tool=self.current_tool
        )

        # Render overlay elements on top
        self.overlay_manager.render((
                                    self.width(),
                                    self.height()))

    # Event handling
    def mousePressEvent(self, event):
        # First let overlay try to handle
        if self.overlay_manager.mouse_press_event(
                event):
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
            event, self.last_mouse_pos)
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
            event)
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

