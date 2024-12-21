# logic/modifiers/basic_2dto3d_modifier.py

import numpy as np
from .base_modifier import BaseModifier
from data.stroke_3d import Stroke3D
from logic.stroke_2d_to_3d import \
    convert_2d_stroke_to_3d


class Axis2Dto3DModifier(BaseModifier):
    """
    主要实现:
      1) apply_2d(stroke2d, canvas_widget):
         - 找到x,y,z轴在当前相机参数下的vanishing point(无穷远投影)
         - 以笔画起点为基准，各自构造候选方向
         - 选出与笔画初始方向最接近的一条，将所有点投影到该直线
         - 最终只保留两个端点
      2) apply_2dto3d(stroke2d, canvas_widget):
         - 在屏幕空间检查是否和已有3D线条的投影相交(若多个,取stroke_id最小)
         - 若有交点, 用对方线条的3D信息来确定交点的3D坐标
         - 若无, 假定起点落在y=0平面, 推算另一端点3D坐标
         - 返回一个Stroke3D
    """

    def __init__(self,
                 mod_id="Axis2Dto3D",
                 enable_toggle_list=["assist_lines"]):
        super().__init__(mod_id,
                         enable_toggle_list)

    # -----------------------------
    # 1) apply_2d
    # -----------------------------
    def apply_2d(self, stroke2d,
                 canvas_widget):
        """
        1) 找到 X/Y/Z 方向的vanishing point(无穷远处坐标),
           并将其投影到屏幕 => vanish_pt_x, vanish_pt_y, vanish_pt_z
        2) 分别和 stroke2d的起点相连，得到三条候选方向
        3) 与笔画初始方向对比, 选相近者
        4) 把所有点投影到那条直线上, 只留2端点
        """
        pts = stroke2d.points_2d
        if len(pts) < 2:
            return stroke2d

        # step1: 计算 x,y,z 三个轴的 vanishing point
        #        我们在世界系中取 (非常大, 0,0), (0,非常大,0), (0,0,非常大) 分别投影到屏幕
        #        当然, 你可也对负方向也做判断, 这里仅演示正轴
        start_pt = np.array(pts[0],
                            dtype=float)

        vx_screen = self.get_vanishing_point_screen(
            "x", canvas_widget)
        vy_screen = self.get_vanishing_point_screen(
            "y", canvas_widget)
        vz_screen = self.get_vanishing_point_screen(
            "z", canvas_widget)

        # 对应三条方向向量:
        dir_x = vx_screen - start_pt
        dir_y = vy_screen - start_pt
        dir_z = vz_screen - start_pt

        # step2: 笔画的初始方向
        second_pt = np.array(pts[1],
                             dtype=float)
        init_dir = second_pt - start_pt
        if np.linalg.norm(
                init_dir) < 1e-9:
            return stroke2d

        # step3: 选与 init_dir 夹角最小的一条
        cand_dirs = {
            'x': dir_x,
            'y': dir_y,
            'z': dir_z
        }
        best_axis = None
        best_cos = -1
        for aname, avec in cand_dirs.items():
            c = self.cosine_similarity(
                init_dir, avec)
            if c > best_cos:
                best_cos = c
                best_axis = aname

        if best_axis is None:
            return stroke2d

        chosen_dir = cand_dirs[
            best_axis]
        if np.linalg.norm(
                chosen_dir) < 1e-9:
            return stroke2d

        dir_unit = chosen_dir / np.linalg.norm(
            chosen_dir)

        # step4: 把所有点投影到 start_pt + t*dir_unit
        projected_pts = []
        for p in pts:
            v_p = p - start_pt
            t = np.dot(v_p, dir_unit)
            newp = start_pt + t * dir_unit
            projected_pts.append(
                (newp[0], newp[1]))

        # 只保留首尾
        stroke2d.points_2d = [
            projected_pts[0],
            projected_pts[-1]]
        return stroke2d

    def get_vanishing_point_screen(self,
                                   axis_name,
                                   canvas_widget):
        """
        在世界坐标中取一个“很远”的点, 例如(1e6,0,0), 然后用MVP投影到屏幕
        以模拟对 x轴 的无穷远投影(即vanishing point).

        axis_name: 'x','y','z'
        return: (u,v) in screen coords
        """
        big = 1e6
        if axis_name == 'x':
            world_pt = np.array(
                [big, 0.0, 0.0],
                dtype=float)
        elif axis_name == 'y':
            world_pt = np.array(
                [0.0, big, 0.0],
                dtype=float)
        else:  # 'z'
            world_pt = np.array(
                [0.0, 0.0, big],
                dtype=float)

        return self.project_point_3d_to_2d(
            world_pt, canvas_widget)

    # -----------------------------
    # 2) apply_2dto3d
    # -----------------------------
    def apply_2dto3d(self, stroke2d,
                     canvas_widget):
        """
        1) 获取已有的3D笔画, 投影到2D
        2) 若与本笔画线段相交(2D), 取 stroke_id最小的那条
        3) 用它的某种方式确定3D交点(此处演示: 只取端点)
        4) 若无相交, 假定起点落在y=0
        5) 返回Stroke3D
        """
        pts2d = stroke2d.points_2d
        if len(pts2d) < 2:
            return None

        # step1: 获取已有线条
        all_3d_strokes = canvas_widget.stroke_manager_3d.get_all_strokes()
        # 按 stroke_id 升序
        all_3d_strokes = sorted(
            all_3d_strokes,
            key=lambda s: s.stroke_id)

        p0 = np.array(pts2d[0],
                      dtype=float)
        p1 = np.array(pts2d[1],
                      dtype=float)

        chosen_intersect = None  # (stroke_id, 交点2D, 交点3D)
        for s3d in all_3d_strokes:
            # 投影到屏幕
            line2d = self.project_3d_line_to_2d(
                s3d, canvas_widget)
            if len(line2d) < 2:
                continue
            # 仅示例: 只拿第一个和最后一个 coords_3d 做成一条线
            l0 = np.array(line2d[0],
                          dtype=float)
            l1 = np.array(line2d[-1],
                          dtype=float)
            inter_pt = self.intersect_2d_lines(
                p0, p1, l0, l1)
            if inter_pt is not None:
                # 找到相交
                # 简化： 选哪端点? 假设离 inter_pt更近的一端
                dist_l0 = np.linalg.norm(
                    inter_pt - l0)
                dist_l1 = np.linalg.norm(
                    inter_pt - l1)
                if dist_l0 < dist_l1:
                    # 用 s3d.coords_3d[0]
                    inter_3d = \
                    s3d.coords_3d[0]
                else:
                    inter_3d = \
                    s3d.coords_3d[-1]

                chosen_intersect = (
                s3d.stroke_id, inter_pt,
                inter_3d)
                break

        if chosen_intersect is not None:
            # step2: 有相交 => 用它决定起点
            p0_3d = chosen_intersect[2]
            # p1_3d => 抬到地面(示例)
            p1_3d = self.lift_to_ground_plane(
                p1, canvas_widget)
        else:
            # step3: 无相交 => 全都落到地面 (示例)
            p0_3d = self.lift_to_ground_plane(
                p0, canvas_widget)
            p1_3d = self.lift_to_ground_plane(
                p1, canvas_widget)

        coords_3d = np.array(
            [p0_3d, p1_3d],
            dtype=np.float32)
        stroke3d = Stroke3D(coords_3d,
                            stroke2d.stroke_id)
        return stroke3d


    def project_point_3d_to_2d(self,
                               pt3d,
                               canvas_widget):
        """
        用 canvas_widget.renderer 的投影矩阵 (projection_matrix) 和视图矩阵 (view_matrix)
        做真正的 MVP 投影, 并转换到屏幕坐标(u,v).
        """
        x, y, z = pt3d
        # 1) 取 renderer
        renderer = canvas_widget.renderer
        projection_matrix = renderer.projection_matrix  # 4x4
        view_matrix = renderer.view_matrix  # 4x4
        w, h = canvas_widget.width(), canvas_widget.height()

        # 2) 构建 MVP = projection * view * model, 这里 model = I
        mvp = projection_matrix @ view_matrix

        # 3) 做齐次坐标
        p4 = np.array([x, y, z, 1.0],
                      dtype=np.float32)
        clip = mvp @ p4  # 形状(4,)

        # 4) 透视除法
        if abs(clip[3]) < 1e-9:
            # 避免除0
            return np.array(
                [99999.0, 99999.0],
                dtype=float)
        ndc = clip[:3] / clip[
            3]  # (X_ndc, Y_ndc, Z_ndc) in [-1,1]

        # 5) 转到屏幕坐标
        u = (ndc[0] * 0.5 + 0.5) * w
        v = (1.0 - (ndc[
                        1] * 0.5 + 0.5)) * h
        return np.array([u, v],
                        dtype=float)

    def project_3d_line_to_2d(self,
                              stroke3d,
                              canvas_widget):
        """
        将 stroke3d.coords_3d 的所有点投影到屏幕空间，返回[(u0,v0), (u1,v1), ...]
        """
        pts_2d = []
        for c in stroke3d.coords_3d:
            screen_pt = self.project_point_3d_to_2d(
                c, canvas_widget)
            pts_2d.append(screen_pt)
        return pts_2d


    def intersect_2d_lines(self, p1, p2,
                           p3, p4):
        d1 = p2 - p1
        d2 = p4 - p3
        cross = d1[0] * d2[1] - d1[1] * \
                d2[0]
        if abs(cross) < 1e-9:
            return None
        t = ((p3[0] - p1[0]) * d2[1] - (
                    p3[1] - p1[1]) * d2[
                 0]) / cross
        u = ((p3[0] - p1[0]) * d1[1] - (
                    p3[1] - p1[1]) * d1[
                 0]) / cross
        if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
            return p1 + t * d1
        return None

    # =================================================================
    # 余弦相似度
    # =================================================================
    def cosine_similarity(self, v1, v2):
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-9 or norm2 < 1e-9:
            return -1
        return np.dot(v1, v2) / (
                    norm1 * norm2)

    # =================================================================
    # 将2D点反投影到y=0平面 (简化示例)
    # =================================================================
    def lift_to_ground_plane(self, pt2d,
                             canvas_widget):
        """
        在真实工程中, 可基于相机外参(摄像机位置/旋转),
        对 (u,v) 做射线-平面(y=0)求交. 这里仅示范:
        """
        u, v = pt2d
        x = (u - 100) * 0.1
        z = (100 - v) * 0.1
        return (x, 0.0, z)
