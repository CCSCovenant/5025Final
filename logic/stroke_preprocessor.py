# coding=utf-8
# logic/stroke_preprocessor.py
# 在2D->3D转换前对2D笔画进行预处理的管线，例如防抖、对齐辅助线等。

import numpy as np


class StrokePreprocessor:
    """
    StrokePreprocessor applies various transformations on 2D stroke points
    before converting them into 3D.
    This includes:
      - Debounce (smooth the stroke points)
      - Assist lines alignment (snap stroke to vanishing points or guide lines)

    笔画预处理器：在2D笔画转换为3D之前，对点列执行一些可选预处理步骤。
    """

    def __init__(self,
                 feature_toggle_manager,
                 overlay_manager):
        """
        :param feature_toggle_manager: FeatureToggleManager instance
        :param overlay_manager: OverlayManager instance (for access to vanishing points, etc.)
        """
        self.feature_toggle_manager = feature_toggle_manager
        self.overlay_manager = overlay_manager

    def process(self, points_2d):
        """
        Process the given list of 2D points according to enabled features.
        根据开启的特性对2D点列进行处理。

        Input:
            points_2d: list of (x, y)
        Output:
            processed_points_2d: list of (x, y) after modifications
        """
        processed = points_2d

        # If debounce is enabled, apply a simple smoothing
        if self.feature_toggle_manager.is_enabled(
                "debounce"):
            processed = self._apply_debounce(
                processed)

        # If assist_lines is enabled, align strokes to vanishing directions
        if self.feature_toggle_manager.is_enabled(
                "assist_lines"):
            processed = self._apply_assist_lines(
                processed)

        return processed

    def _apply_debounce(self, points):
        """
        A simple debounce: smoothing the points by averaging neighbors.
        简单的防抖算法：对点进行平滑。例如对每个点与相邻点取平均，减少抖动。
        """
        if len(points) < 3:
            return points
        smoothed = []
        # Example: simple moving average with window=3
        for i in range(len(points)):
            if i == 0 or i == len(
                    points) - 1:
                smoothed.append(
                    points[i])
            else:
                x_avg = (points[i - 1][
                             0] +
                         points[i][0] +
                         points[i + 1][
                             0]) / 3.0
                y_avg = (points[i - 1][
                             1] +
                         points[i][1] +
                         points[i + 1][
                             1]) / 3.0
                smoothed.append(
                    (x_avg, y_avg))
        return smoothed

    def _apply_assist_lines(self,
                            points):
        """
        Align strokes according to vanishing points.
        根据VanishingPoint进行对齐。

        For demonstration, assume we have one vanishing point and we snap the stroke line
        to pass through it by linear regression or projection.

        实际实现可复杂：例如找到与消失点连线方向最接近的直线，将笔画点投影到该直线上。
        """
        # 假设OverlayManager有方法获取当前活跃的VanishingPoint位置（仅示意）
        vps = self.overlay_manager.get_vanishing_points()
        if not vps:
            return points

        # 简单示例：将所有点朝某个消失点方向对齐
        # （实际可更复杂的对齐策略，这里仅作演示）
        vp = vps[0].position  # 取第一个消失点
        # Compute direction from first point to vp, then project all points onto that line
        if len(points) < 2:
            return points

        base = np.array(points[0],
                        dtype=np.float32)
        vp_vec = np.array(vp,
                          dtype=np.float32)
        direction = vp_vec - base
        direction_norm = direction / (
                    np.linalg.norm(
                        direction) + 1e-6)

        aligned = []
        for p in points:
            p_vec = np.array(p,
                             dtype=np.float32)
            # projection of (p - base) onto direction
            proj_len = np.dot(
                (p_vec - base),
                direction_norm)
            p_aligned = base + proj_len * direction_norm
            aligned.append((float(
                p_aligned[0]), float(
                p_aligned[1])))

        return aligned
