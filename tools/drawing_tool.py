# coding=utf-8
# tools/drawing_tool.py
from PyQt5.QtCore import Qt
import numpy as np
import uuid

from logic.stroke_processor import \
    StrokeProcessor
from .base_tool import BaseTool
from data.stroke_2d import Stroke2D
from logic.stroke_2d_to_3d import convert_2d_stroke_to_3d

class DrawingTool(BaseTool):
    """
    Drawing tool with stroke preprocessing and feature toggles.
    在用户释放鼠标时，对当前笔划进行预处理（防抖、辅助线对齐）然后再进行2D->3D转换。
    """

    def __init__(self, stroke_manager_2d, stroke_manager_3d, stroke_processor,feature_toggle_manager):
        super().__init__()
        self.stroke_manager_2d = stroke_manager_2d
        self.stroke_manager_3d = stroke_manager_3d
        self.stroke_processor = stroke_processor
        self.feature_toggle_manager = feature_toggle_manager

        self.global_stroke_id = 0

        self.is_drawing = False
        self.is_viewing = False
        self.current_points_2d = []
        self.current_stroke_id = None
        self.temp_stroke_2d = None

        self.last_mouse_pos = None


    def new_stroke_id(self):
        self.global_stroke_id = self.global_stroke_id + 1
        return self.global_stroke_id
    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.current_points_2d = [(event.x(), event.y())]
            self.current_stroke_id = self.new_stroke_id()
            self.temp_stroke_2d = Stroke2D(
                stroke_id=self.current_stroke_id,
                points_2d=self.current_points_2d
            )
            # 记录当下的camera信息
            self.temp_stroke_2d.camera_rot = tuple(canvas_widget.camera_rot)
            self.temp_stroke_2d.camera_dist = canvas_widget.camera_distance
        elif event.button() == Qt.RightButton or event.button() == Qt.MidButton:
            self.is_viewing = True
            self.last_mouse_pos = event.pos()

    def mouse_move(self, event, canvas_widget):
        if self.is_drawing:
            self.current_points_2d.append((event.x(), event.y()))
            self.temp_stroke_2d.points_2d = self.current_points_2d

            processed_temp_stroke_2d = self.stroke_processor.process_2d_stroke(self.temp_stroke_2d,canvas_widget)
            # 实时转换可省去预处理（实时显示原始轨迹），预处理只在最终确定时进行
            # 这里用原始点直接显示临时3D曲线(非必要)

            if processed_temp_stroke_2d:
                canvas_widget.temp_stroke_2d = processed_temp_stroke_2d
            canvas_widget.update()
        elif self.is_viewing:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # 简单的摄像机旋转操作
            if event.buttons() & Qt.RightButton:
                canvas_widget.camera_rot[
                    0] += dx * 0.5
                canvas_widget.camera_rot[
                    1] += dy * 0.5
                canvas_widget.update()


            if event.buttons() & Qt.MidButton:
                self.pan_camera(canvas_widget,dx,dy)
                canvas_widget.update()

            self.last_mouse_pos = event.pos()

    def mouse_release(self, event, canvas_widget):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            # 在最终提交前，对2D点列进行预处理
            processed_temp_stroke_2d = self.stroke_processor.process_2d_stroke(self.temp_stroke_2d,canvas_widget)
            processed_final_stroke_3d = self.stroke_processor.process_2dto3d_stroke(processed_temp_stroke_2d,canvas_widget)
            # 转换为3D笔画
            self.stroke_manager_2d.add_stroke(self.temp_stroke_2d)
            if self.feature_toggle_manager.is_enabled("adv_sbm"):
                canvas_widget.viewable2d_stroke.append(processed_temp_stroke_2d)
            else:
                if processed_final_stroke_3d:
                    processed_final_stroke_3d.color = (
                    1.0, 1.0, 1.0)
                    self.stroke_manager_3d.add_stroke(
                        processed_final_stroke_3d)
                canvas_widget.viewable2d_stroke = []

            self.temp_stroke_2d = None
            self.current_points_2d = []
            canvas_widget.temp_stroke_2d = None
            canvas_widget.update()
        elif (event.button() == Qt.RightButton or event.button() == Qt.MidButton) and self.is_viewing:
          self.is_viewing = False

    def wheelEvent(self, event,
                         canvas_widget):
        delta = event.angleDelta().y()

        # 定义缩放速度（可根据需要调整）
        zoom_speed = 0.1

        # 根据滚动方向调整摄像机距离
        if delta > 0:
            # 向前滚动，缩小距离（放大视图）
            canvas_widget.camera_distance -= zoom_speed
        else:
            # 向后滚动，增大距离（缩小视图）
            canvas_widget.camera_distance += zoom_speed
        canvas_widget.camera_distance = max(10.0, min(canvas_widget.camera_distance, 40.0))
        canvas_widget.update()

    def render_tool_icon(self, render, viewport_size):
        pass


    def pan_camera(self,canvas_widget,dx, dy):
        """
        根据鼠标移动增量 dx, dy 平移摄像机的 look_at 位置。
        """
        # 将摄像机旋转角度从度转换为弧度
        camera_rot = canvas_widget.camera_rot
        yaw_rad = np.radians(
            camera_rot[0])
        pitch_rad = np.radians(
            camera_rot[1])

        # 计算前向向量（Forward Vector）
        forward = np.array([
            np.cos(pitch_rad) * np.sin(
                yaw_rad),
            np.sin(pitch_rad),
            np.cos(pitch_rad) * np.cos(
                yaw_rad)
        ])
        forward /= np.linalg.norm(
            forward)

        # 定义世界上向量（通常为 y 轴）
        world_up = np.array(
            [0.0, 1.0, 0.0])

        # 计算右向量（Right Vector）
        right = np.cross(forward,
                         world_up)
        right /= np.linalg.norm(right)

        # 计算真实的上向量（Up Vector）
        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        # 计算摄像机与 look_at 的距离，用于缩放平移速度
        camera_distance = canvas_widget.camera_distance

        # 定义平移速度（根据距离和鼠标移动增量）
        pan_speed = 0.002 * camera_distance  # 可根据需要调整

        # 计算平移向量
        pan_right = right * dx * pan_speed
        pan_up = up * dy * pan_speed

        # 更新 look_at 位置
        canvas_widget.look_at += pan_right + pan_up
