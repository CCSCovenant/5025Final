# tools/selection_tool.py

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

from .base_tool import BaseTool

class SelectionTool(BaseTool):
    def __init__(self, selection_manager, radius=50):
        super().__init__()
        self.selection_manager = selection_manager
        self.radius = radius
        self.mouse_pos = None

    def mouse_press(self, event, canvas_widget):
        if event.button() == Qt.LeftButton:
            # 获取当前 hovered_strokes
            hovered = self.selection_manager.hovered_strokes
            if event.modifiers() & Qt.ShiftModifier:
                # 多选
                self.selection_manager.add_to_selection(hovered)
            else:
                # 覆盖式选择
                self.selection_manager.set_selection(hovered)
            canvas_widget.update()
        self.mouse_pos = event.pos()

    def mouse_move(self, event, canvas_widget):
        self.mouse_pos = event.pos()
        # 实时更新 hovered_strokes
        circle_center = (event.x(), event.y())
        # 需要先做3D->2D投影, stroke.screen_coords 应该由 canvas_widget / renderer维护
        strokes_3d = canvas_widget.get_all_strokes_for_selection()
        hovered = self.selection_manager.find_strokes_in_circle(
            strokes_3d, circle_center, self.radius
        )
        self.selection_manager.set_hovered(hovered)
        canvas_widget.update()

    def mouse_release(self, event, canvas_widget):
        pass  # 点击时已经处理完选择逻辑

    def set_radius(self, r):
        self.radius = r
