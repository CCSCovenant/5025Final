# tools/drawing_tool.py

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
import numpy as np

from .base_tool import BaseTool
from data.stroke_3d import Stroke3D
from logic.stroke_2d_to_3d import convert_2d_to_3d  # 或自己实现

class DrawingTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.is_drawing = False
        self.current_stroke_points = []
        self.temp_stroke_3d = None

    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.current_stroke_points = [(event.x(), event.y())]
            self.temp_stroke_3d = None

    def mouse_move(self, event, canvas_widget):
        if self.is_drawing:
            self.current_stroke_points.append((event.x(), event.y()))
            # 实时转换为3D笔画
            stroke_3d = convert_2d_to_3d(
                points_2d=self.current_stroke_points,
                canvas_width=canvas_widget.width(),
                canvas_height=canvas_widget.height(),
                projection_matrix=canvas_widget.renderer.projection_matrix,
                view_matrix=canvas_widget.renderer.view_matrix,
                model_matrix=np.eye(
                    4,
                    dtype=np.float32),

            )
            # 给临时笔画设置一个状态 or 颜色
            stroke_3d.status = 'normal'
            stroke_3d.color = (1.0, 1.0, 1.0)  # 白色
            self.temp_stroke_3d = stroke_3d
            canvas_widget.temp_stroke_3d = self.temp_stroke_3d
            canvas_widget.update()

    def mouse_release(self, event, canvas_widget):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            if self.temp_stroke_3d is not None:
                # 将最终笔画加入stroke_manager
                canvas_widget.stroke_manager.add_stroke(self.temp_stroke_3d)
                self.temp_stroke_3d = None
            self.current_stroke_points = []
            canvas_widget.temp_stroke_3d = None
            canvas_widget.update()
