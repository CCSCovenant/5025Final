#data/stroke_2d.py
class Stroke2D:
    def __init__(self, stroke_id, points_2d):
        """
        stroke_id : int 或 str，用于与3D笔画对应
        points_2d : list of (x, y)
        """
        self.stroke_id = stroke_id
        self.points_2d = points_2d  # 2D坐标列表

        # 如果想记录绘制时的相机信息，也可加在这里
        self.camera_rot = (0.0, 0.0)
        self.camera_dist = 3.0

        # 其他属性 (颜色、状态等)
        self.is_selected = False
        self.is_hovered = False
