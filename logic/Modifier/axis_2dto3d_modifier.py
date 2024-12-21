# logic/modifiers/basic_2dto3d_modifier.py

import numpy as np
from .base_modifier import BaseModifier
from data.stroke_3d import Stroke3D
from logic.stroke_2d_to_3d import \
    convert_2d_stroke_to_3d


class Axis2Dto3DModifier(BaseModifier):
    """
    将2D笔画转换到3D的示例Modifier。
    使用最简单的透视投影逻辑, 也可改成调用 stroke_2d_to_3d 的某个函数。
    """
    def __init__(self):
        super().__init__(mod_id="axis_2d_to_3d", enable_toggle_list=["always"])

    def apply_2dto3d(self, stroke2d,
                     canvas_width, canvas_height,
                     projection_matrix, view_matrix, model_matrix):

        stroke_3d = convert_2d_stroke_to_3d(
            stroke_2d=stroke2d,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            projection_matrix=projection_matrix,
            view_matrix=view_matrix
        )

        return stroke_3d
