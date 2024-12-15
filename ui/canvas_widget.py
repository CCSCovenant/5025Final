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

        # ---- 绘制相关 ----
        self.is_drawing = False
        self.current_stroke_points = []
        self.temp_stroke_3d = None

        # ---- 视图模式开关 ----
        self.view_mode = False

        # ---- 摄像机相关 ----
        self.last_mouse_pos = QPoint()
        self.camera_rot = [0.0,
                           0.0]  # 摄像机绕 X/Y 轴的旋转角度
        self.camera_distance = 2.0  # 摄像机和原点的距离(用于缩放)

    def set_view_mode(self,
                      enabled: bool):
        """
        当用户切换视图模式时调用该方法
        """
        self.view_mode = enabled
        if self.view_mode:
            self.is_drawing = False  # 如果切到视图模式，当前绘制立即结束
            self.current_stroke_points = []
            self.temp_stroke_3d = None
        self.update()

    def initializeGL(self):
        self.renderer.initialize()

    def resizeGL(self, w, h):
        self.renderer.resize(w, h)

    def paintGL(self):
        """
        绘制时：在普通（编辑）模式下，还要把正在绘制的笔画(temp_stroke_3d)也画上；
               在视图模式下，不存在正在绘制笔画。
        """
        final_strokes_3d = self.stroke_manager.get_all_3d_strokes()
        strokes_to_render = list(
            final_strokes_3d)
        if (not self.view_mode) and (
                self.temp_stroke_3d is not None):
            strokes_to_render.append(
                self.temp_stroke_3d)

        self.renderer.render(
            strokes_to_render,
            camera_rot=self.camera_rot,
            camera_dist=self.camera_distance)

    # =============== 鼠标事件处理 ===============
    def mousePressEvent(self,
                        event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if not self.view_mode:
                # 在非视图模式下才允许绘制
                self.is_drawing = True
                self.current_stroke_points = [
                    event.pos()]
                self.temp_stroke_3d = None
            # 如果是视图模式，则点击鼠标无绘制效果，只能做旋转/缩放
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self,
                       event: QMouseEvent):
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        if not self.view_mode:
            # === 编辑模式：绘制笔画 ===
            if self.is_drawing:
                self.current_stroke_points.append(
                    event.pos())
                # 实时更新 temp_stroke_3d
                self.temp_stroke_3d = convert_2d_to_3d(
                    self.current_stroke_points,
                    self.width(),
                    self.height()
                )
                self.update()
        else:
            # === 视图模式：旋转 or 缩放相机 ===
            # 鼠标左键拖动 -> 旋转摄像机
            buttons = event.buttons()
            if buttons & Qt.LeftButton:
                self.camera_rot[
                    0] += dx * 0.5
                self.camera_rot[
                    1] += dy * 0.5
                self.update()
            # 鼠标右键拖动 -> 缩放 (调节camera_distance)
            if buttons & Qt.RightButton:
                self.camera_distance -= dy * 0.01
                if self.camera_distance < 0.1:
                    self.camera_distance = 0.1
                self.update()

        self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self,
                          event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if not self.view_mode and self.is_drawing:
                self.is_drawing = False
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
