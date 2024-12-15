import numpy as np
from data.stroke_3d import Stroke3D


def convert_2d_to_3d(points_2d=None,
                     canvas_width=None,
                     canvas_height=None,
                     projection_matrix=None,      # 4x4 numpy array (float32)
                     view_matrix=None,            # 4x4 numpy array (float32)
                     model_matrix=None,           # 4x4 numpy array (float32)
                     z = 0
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

        # 计算 MVP 和它的逆矩阵
    mvp = projection_matrix @ view_matrix @ model_matrix
    inv_mvp = np.linalg.inv(mvp)

    # 用于存储最终的3D坐标
    coords_3d = []

    for pt in points_2d:
        # 处理QPoint和元组的兼容
        if hasattr(pt, 'x') and hasattr(
                pt, 'y'):
            x_screen, y_screen = pt.x(), pt.y()
        else:
            x_screen, y_screen = pt

        # 1) 将屏幕坐标转换到 NDC (clip) 空间
        x_ndc = (
                            x_screen / canvas_width) * 2.0 - 1.0
        y_ndc = 1.0 - (
                    y_screen / canvas_height) * 2.0

        # 构造 near/far 的 clip坐标 (z=-1 对应 near plane，z=1 对应 far plane；OpenGL约定)
        near_clip = np.array(
            [x_ndc, y_ndc, -1.0, 1.0],
            dtype=np.float32)
        far_clip = np.array(
            [x_ndc, y_ndc, 1.0, 1.0],
            dtype=np.float32)

        # 2) 反变换到世界坐标
        near_world = inv_mvp @ near_clip
        far_world = inv_mvp @ far_clip
        # 做透视除法
        near_world /= near_world[3]
        far_world /= far_world[3]

        ray_origin = near_world[:3]
        ray_dir = (far_world[
                   :3] - ray_origin)

        # 如果射线与 z=0 平面平行，则无法求交
        if abs(ray_dir[2]) < 1e-8:
            # 这里也可以直接把它丢弃 或者假设z_plane=0恰好是射线路径
            continue

        t = (z - ray_origin[2]) / \
            ray_dir[2]
        if t >= 0:  # 交点在相机前方
            intersection = ray_origin + t * ray_dir
            coords_3d.append(
                intersection)
        # else:
        #   可能 t<0，表示在摄像机后面，不处理

    if not coords_3d:
        return None

    coords_3d = np.array(coords_3d,
                         dtype=np.float32)
    return Stroke3D(coords_3d)
