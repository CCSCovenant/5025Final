from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint

from data.stroke_manager_2d import StrokeManager2D
from data.stroke_manager_3d import StrokeManager3D
from rendering.renderer_3d import Renderer3D
from logic.selection_manager import SelectionManager
# 无需再用老的 stroke_manager.py

class CanvasWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 新的2D/3D管理器
        self.stroke_manager_2d = StrokeManager2D()
        self.stroke_manager_3d = StrokeManager3D()

        self.selection_manager = SelectionManager()
        self.renderer = Renderer3D()

        self.setMouseTracking(True)
        self.current_tool = None
        self.temp_stroke_3d = None

        # 摄像机
        self.camera_rot = [0.0, 0.0]
        self.camera_distance = 3.0

    def set_tool(self, tool):
        self.current_tool = tool
        self.update()

    def get_all_strokes_for_selection(self):
        """
        SelectionTool要用到。返回所有3D笔画 + (临时笔画).
        """
        strokes = self.stroke_manager_3d.get_all_strokes()
        if self.temp_stroke_3d:
            strokes = list(strokes) + [self.temp_stroke_3d]
        return strokes

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        strokes_3d = list(self.stroke_manager_3d.get_all_strokes())
        if self.temp_stroke_3d:
            strokes_3d.append(self.temp_stroke_3d)

        self.renderer.render(
            strokes_3d,
            camera_rot=self.camera_rot,
            camera_dist=self.camera_distance,
            viewport_size=(self.width(), self.height()),
            selection_manager=self.selection_manager,
            activated_tool=self.current_tool
        )

    # ============== 统一的鼠标事件分发 =================
    def mousePressEvent(self, event):
        if self.current_tool:
            self.current_tool.mouse_press(event, self)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_tool:
            self.current_tool.mouse_move(event, self)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.current_tool:
            self.current_tool.mouse_release(event, self)
        else:
            super().mouseReleaseEvent(event)

    # ============= 撤销、重做 =============
    def undo_stroke(self):
        # 分别undo 3D和2D
        self.stroke_manager_3d.undo()
        self.stroke_manager_2d.undo()
        self.update()

    def redo_stroke(self):
        # 分别redo 3D和2D
        self.stroke_manager_3d.redo()
        self.stroke_manager_2d.redo()
        self.update()

