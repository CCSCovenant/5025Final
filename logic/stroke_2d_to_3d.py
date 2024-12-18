#logic/stroke_2d_to_3d.py

import numpy as np
from data.stroke_3d import Stroke3D

def convert_2d_stroke_to_3d(
    stroke_2d,
    canvas_width,
    canvas_height,
    projection_matrix,
    view_matrix,
    model_matrix=None,
    z=0.0
):
    """
    给定 Stroke2D, 转换为 Stroke3D。
    """
    if model_matrix is None:
        model_matrix = np.eye(4, dtype=np.float32)

    points_2d = stroke_2d.points_2d
    if not points_2d:
        return None

    # 与之前逻辑相同
    mvp = projection_matrix @ view_matrix @ model_matrix
    inv_mvp = np.linalg.inv(mvp)

    coords_3d = []
    for (x_screen, y_screen) in points_2d:
        x_ndc = (x_screen / canvas_width) * 2.0 - 1.0
        y_ndc = 1.0 - (y_screen / canvas_height) * 2.0

        near_clip = np.array([x_ndc, y_ndc, -1.0, 1.0], dtype=np.float32)
        far_clip  = np.array([x_ndc, y_ndc,  1.0, 1.0], dtype=np.float32)

        near_world = inv_mvp @ near_clip
        far_world  = inv_mvp @ far_clip
        near_world /= near_world[3]
        far_world  /= far_world[3]

        ray_origin = near_world[:3]
        ray_dir    = (far_world[:3] - ray_origin)

        if abs(ray_dir[2]) < 1e-8:
            continue

        t = (z - ray_origin[2]) / ray_dir[2]
        if t >= 0:
            intersection = ray_origin + t * ray_dir
            coords_3d.append(intersection)

    if not coords_3d:
        return None

    coords_3d = np.array(coords_3d, dtype=np.float32)
    stroke_3d = Stroke3D(coords_3d, stroke_id=stroke_2d.stroke_id)
    return stroke_3d
