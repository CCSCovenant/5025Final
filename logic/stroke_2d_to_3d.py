import numpy as np
from data.stroke_3d import Stroke3D


def convert_2d_to_3d(points_2d=None,
                     canvas_width=None,
                     canvas_height=None,
                     projection_matrix=None,      # 4x4 numpy array (float32)
                     view_matrix=None,            # 4x4 numpy array (float32)
                     model_matrix=None,           # 4x4 numpy array (float32)
                     ):
    """
     将屏幕空间中的一组2D点 screen_points 转换为3D世界坐标 (z=z_plane)上的笔画.
     返回 Stroke3D 对象 (里面存储3D坐标).

     参数说明:
       - points_2d      : [(x1, y1), (x2, y2), ...] 或者 [QPoint, QPoint, ...]
       - canvas_width     : 视口宽度 (widget.width())
       - canvas_height    : 视口高度 (widget.height())
       - projection_matrix  : 渲染时使用的投影矩阵 (4x4)
       - view_matrix        : 渲染时使用的视图矩阵 (4x4)
       - model_matrix       : 物体(或世界)的模型变换矩阵 (4x4)，若无特殊变换可传 np.eye(4)
     """

    if not points_2d:
        return None

    print(1)
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
