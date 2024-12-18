# tools/drawing_tool.py

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
import numpy as np
import uuid

from .base_tool import BaseTool
from data.stroke_2d import Stroke2D
from logic.stroke_2d_to_3d import convert_2d_stroke_to_3d

class DrawingTool(BaseTool):
    def __init__(self, stroke_manager_2d, stroke_manager_3d):
        super().__init__()
        self.stroke_manager_2d = stroke_manager_2d
        self.stroke_manager_3d = stroke_manager_3d

        self.is_drawing = False
        self.current_points_2d = []
        self.temp_stroke_3d = None
        self.current_stroke_id = None  # 用于记录当前笔画的ID

    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.current_points_2d = [(event.x(), event.y())]

            # 生成笔画ID
            self.current_stroke_id = str(uuid.uuid4())
            # 先创建2D笔画对象（不一定要在按下鼠标就加到manager里，也可以等释放后一次性加）
            self.temp_stroke_2d = Stroke2D(
                stroke_id = self.current_stroke_id,
                points_2d = self.current_points_2d
            )
            # 如果想记录当下的camera信息到2D笔画，也可以：
            self.temp_stroke_2d.camera_rot = tuple(canvas_widget.camera_rot)
            self.temp_stroke_2d.camera_dist = canvas_widget.camera_distance

    def mouse_move(self, event, canvas_widget):
        if self.is_drawing:
            self.current_points_2d.append((event.x(), event.y()))
            self.temp_stroke_2d.points_2d = self.current_points_2d

            # 实时转换为3D笔画
            stroke_3d = convert_2d_stroke_to_3d(
                stroke_2d=self.temp_stroke_2d,
                canvas_width=canvas_widget.width(),
                canvas_height=canvas_widget.height(),
                projection_matrix=canvas_widget.renderer.projection_matrix,
                view_matrix=canvas_widget.renderer.view_matrix,
                model_matrix=np.eye(4,dtype=np.float32),
            )
            if stroke_3d:
                stroke_3d.color = (1.0, 1.0, 1.0)  # 临时颜色
                self.temp_stroke_3d = stroke_3d
                canvas_widget.temp_stroke_3d = self.temp_stroke_3d

            canvas_widget.update()

    def mouse_release(self, event, canvas_widget):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            if self.temp_stroke_3d is not None:
                # 最终将2D笔画加入 manager_2d
                self.stroke_manager_2d.add_stroke(self.temp_stroke_2d)

                # 将对应3D笔画加入 manager_3d
                self.stroke_manager_3d.add_stroke(self.temp_stroke_3d)

            self.temp_stroke_3d = None
            self.temp_stroke_2d = None
            self.current_points_2d = []
            canvas_widget.temp_stroke_3d = None
            canvas_widget.update()

    def render_tool_icon(self, render, viewport_size):
        pass

