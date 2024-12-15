# ui/canvas_widget.py

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from logic.stroke_manager import StrokeManager
from rendering.renderer_3d import Renderer3D
from logic.selection_manager import SelectionManager
from data.stroke_3d import Stroke3D
from tools.selection_tool import \
    SelectionTool


class CanvasWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stroke_manager = StrokeManager()
        self.selection_manager = SelectionManager()
        self.renderer = Renderer3D()

        self.setMouseTracking(True)

        self.current_tool = None  # BaseTool的子类实例
        self.temp_stroke_3d = None  # 用于绘制中产生的临时笔画

        # 摄像机
        self.camera_rot = [0.0, 0.0]
        self.camera_distance = 3.0


    def set_tool(self, tool):
        """外部(如MainWindow)可调用此方法切换工具"""
        if isinstance(self.current_tool,
                      SelectionTool) and not isinstance(
                tool, SelectionTool):
            self.selection_circle = None
            self.selection_manager.clear_hovered()

        self.current_tool = tool
        self.update()

    def get_all_strokes_for_selection(self):
        """
        给SelectionTool用, 返回(所有Stroke + 临时笔画)便于在屏幕空间判定 hovered
        """
        strokes = self.stroke_manager.get_all_3d_strokes()
        if self.temp_stroke_3d:
            strokes = list(strokes) + [self.temp_stroke_3d]
        return strokes

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        strokes_3d = list(self.stroke_manager.get_all_3d_strokes())
        if self.temp_stroke_3d:
            strokes_3d.append(self.temp_stroke_3d)


        self.renderer.render(
            strokes_3d,
            camera_rot=self.camera_rot,
            camera_dist=self.camera_distance,
            viewport_size=(self.width(),
                           self.height()),
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
        self.stroke_manager.undo()
        self.update()

    def redo_stroke(self):
        self.stroke_manager.redo()
        self.update()

