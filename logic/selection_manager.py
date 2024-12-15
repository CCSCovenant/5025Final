# logic/selection_manager.py

import numpy as np


class SelectionManager:
    def __init__(self):
        # 已经选中的笔画（Stroke）引用或ID
        self.selected_strokes = set()

        # 临时高亮的笔画（鼠标移动时更新）
        self.hovered_strokes = set()

    def clear_selection(self):
        for s in self.selected_strokes:
            s.is_selected = False
        self.selected_strokes.clear()

    def add_to_selection(self, strokes):
        """
        strokes: iterable of stroke引用或ID
        """
        for s in strokes:
            s.is_selected = True
            self.selected_strokes.add(s)

    def set_selection(self, strokes):
        """
        重置已选中的笔画
        """
        self.clear_selection()
        self.add_to_selection(strokes)

    def add_to_hovered(self,strokes):
        for s in strokes:
            s.is_hovered = True
            self.hovered_strokes.add(s)
    def set_hovered(self, strokes):
        self.clear_hovered()
        self.add_to_hovered(strokes)

    def clear_hovered(self):
        for s in self.hovered_strokes:
            s.is_hovered = False
        self.hovered_strokes.clear()

    # -------------------------------------------
    # 核心：判断哪些Stroke与“屏幕空间圆形”相交
    # -------------------------------------------
    def find_strokes_in_circle(self,
                               strokes_3d,
                               circle_center,
                               circle_radius):
        """
        给定所有笔画 strokes_3d, 以及一个在"屏幕空间"的圆：
          circle_center = (cx, cy) in screen coords
          circle_radius = float (in screen coords)
        返回与该圆相交的 strokes (的引用或对象)
        """
        # 这里要求 strokes_3d 已经变换到屏幕坐标
        # 一般在 canvas_widget 渲染/逻辑里做 "3D->2D投影" 后再传进来判断
        # 或者将 3D -> 2D 的逻辑写在这里也可以

        result = []
        cx, cy = circle_center
        r_sq = circle_radius ** 2

        for stroke in strokes_3d:
            points_2d = stroke.screen_coords  # 先假设我们给 stroke 扩展了一个属性 screen_coords
            # 检查 stroke 是否与圆相交：只要有一点落在圆内，就算相交
            # 或者更严格地检查线段与圆的最短距离
            for p in points_2d:
                dx = p[0] - cx
                dy = p[1] - cy
                dist_sq = dx * dx + dy * dy
                if dist_sq <= r_sq:
                    result.append(
                        stroke)
                    break  # 该stroke只要有一点命中就算命中
        return result
