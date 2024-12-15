# tools/view_tool.py

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from .base_tool import BaseTool

class ViewTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.last_mouse_pos = None

    def mouse_press(self, event, canvas_widget):
        self.last_mouse_pos = event.pos()

    def mouse_move(self, event, canvas_widget):
        if event.buttons() & Qt.LeftButton:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # 简单的摄像机旋转操作
            if event.buttons() & Qt.LeftButton:
                canvas_widget.camera_rot[0] += dx * 0.5
                canvas_widget.camera_rot[1] += dy * 0.5
                canvas_widget.update()

            # 右键缩放
            if event.buttons() & Qt.RightButton:
                canvas_widget.camera_distance -= dy * 0.01
                if canvas_widget.camera_distance < 0.1:
                    canvas_widget.camera_distance = 0.1
                canvas_widget.update()

            self.last_mouse_pos = event.pos()

    def render_tool_icon(self,render,viewport_size):
        pass

    def mouse_release(self, event, canvas_widget):
        pass
