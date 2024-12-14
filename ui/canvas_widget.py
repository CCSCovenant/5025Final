import numpy as np
from PyQt5.QtWidgets import \
    QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

from logic.stroke_2d_to_3d import \
    convert_2d_to_3d
from logic.stroke_manager import \
    StrokeManager
from rendering.renderer_3d import \
    Renderer3D
from data.stroke_3d import Stroke3D


class CanvasWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stroke_manager = StrokeManager()
        self.renderer = Renderer3D()

        # ---- 笔画相关 ----
        self.is_drawing = False
        self.current_stroke_points = []  # 当前进行中笔画的2D点列表
        self.temp_stroke_3d = None  # 当前进行中笔画对应的 3D 笔画

        # ---- 摄像机相关 ----
        self.last_mouse_pos = QPoint()
        self.camera_rot = [0.0,
                           0.0]  # 记录摄像机的旋转角度(简化为两个轴)

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        """
        每次刷新时，都需要：
          1. 绘制 stroke_manager 里所有已经完成的3D笔画
          2. 如果有正在绘制的笔画(temp_stroke_3d)，也要一起绘制
        """
        # 已完成笔画
        final_strokes_3d = self.stroke_manager.get_all_3d_strokes()

        # 如果有正在绘制的笔画，也加进去一起绘制
        strokes_to_render = list(
            final_strokes_3d)
        if self.temp_stroke_3d is not None:
            strokes_to_render.append(
                self.temp_stroke_3d)

        self.renderer.render(
            strokes_to_render,
            camera_rot=self.camera_rot)

    # =============== 鼠标事件处理 ===============
    def mousePressEvent(self,
                        event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 开始绘制新的2D笔画
            self.is_drawing = True
            self.current_stroke_points = [
                event.pos()]
            self.temp_stroke_3d = None  # 重置临时笔画

        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self,
                       event: QMouseEvent):
        if self.is_drawing:
            # 实时记录鼠标移动经过的点
            self.current_stroke_points.append(
                event.pos())
            # 实时转换为3D笔画
            self.temp_stroke_3d = convert_2d_to_3d(
                self.current_stroke_points,
                self.width(),
                self.height()
            )
            self.update()  # 触发paintGL()，实现实时显示
        else:
            # 如果不是在绘制笔画，就可能是旋转摄像机
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.camera_rot[
                0] += dx * 0.5
            self.camera_rot[
                1] += dy * 0.5

            self.last_mouse_pos = event.pos()
            self.update()  # 摄像机变换后也要重绘

    def mouseReleaseEvent(self,
                          event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
            # 当鼠标释放后，将临时笔画存入stroke_manager
            if self.temp_stroke_3d is not None:
                self.stroke_manager.add_stroke(
                    self.temp_stroke_3d)
                self.temp_stroke_3d = None

            self.current_stroke_points = []
            self.update()

    # =============== 撤销、重做 ===============
    def undo_stroke(self):
        self.stroke_manager.undo()
        self.update()

    def redo_stroke(self):
        self.stroke_manager.redo()
        self.update()
