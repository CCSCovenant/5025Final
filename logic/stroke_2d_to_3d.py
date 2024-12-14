import numpy as np
from data.stroke_3d import Stroke3D


def convert_2d_to_3d(points_2d,
                     canvas_width,
                     canvas_height):
    """
    将一系列2D像素坐标 [QPoint(x, y), ...] 转换为3D坐标
    这里的规则可以非常灵活，比如：
    - z 固定为0 或者根据一些深度规则计算
    - x, y 归一化到[-1,1]区间
    """
    if not points_2d:
        return None

    coords_3d = []
    for pt in points_2d:
        # 简单做一下归一化，再映射到 [-1,1]
        nx = (
                         pt.x() / canvas_width) * 2.0 - 1.0
        ny = 1.0 - (
                    pt.y() / canvas_height) * 2.0  # y 轴方向反转
        nz = 0.0
        coords_3d.append([nx, ny, nz])

    coords_3d = np.array(coords_3d,
                         dtype=np.float32)
    stroke_3d = Stroke3D(coords_3d)
    return stroke_3d
