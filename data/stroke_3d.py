# data/stroke_3d.py
import numpy as np

class Stroke3D:
    def __init__(self, coords_3d, color=(1,1,1)):
        """
        coords_3d: shape=(N,3)
        color: (r,g,b)
        status: 'normal', 'hovered', 'selected' 等
        """
        self.coords_3d = coords_3d
        self.color = color
        self.is_hovered = False
        self.is_selected = False
        self.screen_coords = []  # 新增: 存储屏幕坐标 (N,2)

    def get_points(self):
        return self.coords_3d

    def set_status(self, new_status):
        self.status = new_status

    def set_color(self, new_color):
        self.color = new_color

    def set_screen_coordinate(self,new_coordinate):
        self.screen_coordinate = new_coordinate
