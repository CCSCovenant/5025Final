# logic/modifiers/smoothing_2d_modifier.py

from data.stroke_2d import Stroke2D
from .base_modifier import BaseModifier
from data.stroke_2d import Stroke2D
class Smoothing2DModifier(BaseModifier):
    """
    mod_id = "smooth_2d", enable_toggle_list = ["debounce"]
    当"debounce"开关开启时才执行。
    """
    def __init__(self):
        super().__init__(mod_id="smooth_2d",
                         enable_toggle_list=["debounce"])

    def apply_2d(self, stroke2d):
        points = stroke2d.points_2d
        if len(points) < 3:
            return stroke2d

        smoothed_pts = []
        for i in range(len(points)):
            if i==0 or i==len(points)-1:
                smoothed_pts.append(points[i])
            else:
                x_avg = (points[i-1][0] + points[i][0] + points[i+1][0]) / 3.0
                y_avg = (points[i-1][1] + points[i][1] + points[i+1][1]) / 3.0
                smoothed_pts.append((x_avg, y_avg))

        stroke2d.points_2d = smoothed_pts
        return stroke2d
