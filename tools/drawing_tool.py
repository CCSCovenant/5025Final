# coding=utf-8
# tools/drawing_tool.py
from PyQt5.QtCore import Qt
import numpy as np
import uuid

from .base_tool import BaseTool
from data.stroke_2d import Stroke2D
from logic.stroke_2d_to_3d import convert_2d_stroke_to_3d

class DrawingTool(BaseTool):
    """
    Drawing tool with stroke preprocessing and feature toggles.
    在用户释放鼠标时，对当前笔划进行预处理（防抖、辅助线对齐）然后再进行2D->3D转换。
    """

    def __init__(self, stroke_manager_2d, stroke_manager_3d, stroke_preprocessor):
        super().__init__()
        self.stroke_manager_2d = stroke_manager_2d
        self.stroke_manager_3d = stroke_manager_3d
        self.stroke_preprocessor = stroke_preprocessor

        self.is_drawing = False
        self.current_points_2d = []
        self.temp_stroke_3d = None
        self.current_stroke_id = None
        self.temp_stroke_2d = None

    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.current_points_2d = [(event.x(), event.y())]
            self.current_stroke_id = str(uuid.uuid4())
            self.temp_stroke_2d = Stroke2D(
                stroke_id=self.current_stroke_id,
                points_2d=self.current_points_2d
            )
            # 记录当下的camera信息
            self.temp_stroke_2d.camera_rot = tuple(canvas_widget.camera_rot)
            self.temp_stroke_2d.camera_dist = canvas_widget.camera_distance

    def mouse_move(self, event, canvas_widget):
        if self.is_drawing:
            self.current_points_2d.append((event.x(), event.y()))
            self.temp_stroke_2d.points_2d = self.current_points_2d

            # 实时转换可省去预处理（实时显示原始轨迹），预处理只在最终确定时进行
            # 这里用原始点直接显示临时3D曲线(非必要)
            stroke_3d = convert_2d_stroke_to_3d(
                stroke_2d=self.temp_stroke_2d,
                canvas_width=canvas_widget.width(),
                canvas_height=canvas_widget.height(),
                projection_matrix=canvas_widget.renderer.projection_matrix,
                view_matrix=canvas_widget.renderer.view_matrix
            )
            if stroke_3d:
                stroke_3d.color = (1.0, 1.0, 1.0)
                self.temp_stroke_3d = stroke_3d
                canvas_widget.temp_stroke_3d = self.temp_stroke_3d
            canvas_widget.update()

    def mouse_release(self, event, canvas_widget):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            # 在最终提交前，对2D点列进行预处理
            processed_points = self.stroke_preprocessor.process(self.current_points_2d)
            self.temp_stroke_2d.points_2d = processed_points

            # 转换为3D笔画
            final_stroke_3d = convert_2d_stroke_to_3d(
                stroke_2d=self.temp_stroke_2d,
                canvas_width=canvas_widget.width(),
                canvas_height=canvas_widget.height(),
                projection_matrix=canvas_widget.renderer.projection_matrix,
                view_matrix=canvas_widget.renderer.view_matrix
            )
            if final_stroke_3d:
                final_stroke_3d.color = (1.0, 1.0, 1.0)
                self.stroke_manager_2d.add_stroke(self.temp_stroke_2d)
                self.stroke_manager_3d.add_stroke(final_stroke_3d)

            self.temp_stroke_3d = None
            self.temp_stroke_2d = None
            self.current_points_2d = []
            canvas_widget.temp_stroke_3d = None
            canvas_widget.update()


    def render_tool_icon(self, render, viewport_size):
        pass

