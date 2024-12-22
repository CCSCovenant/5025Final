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
         - 获取 x,y,z 轴在当前相机下的无穷远消失点 (vanishing point)
         - 分别与笔画起点相连得到三条候选方向
         - 选与用户初始绘制方向最接近的一条, 将笔画投影到该直线上
         - 只保留两个端点, 并记录 'axis' 到 stroke2d.meta

      2) apply_2dto3d(stroke2d, canvas_widget):
         - 获取已有3D笔画, 投影到2D检查相交(若有多个,选stroke_id最小)
           得到 3D交点 anchor_3d
         - 如果找到 anchor_3d, 则对整条线(两个端点)执行“反投影+轴对齐”:
           线段在 3D 中只在某个坐标轴方向变化, 其余分量与 anchor_3d 相同
         - 若没找到交点, 则假设起点落在 y=0, 并沿指定轴方向计算另一个端点3D坐标
    """

    def __init__(self,
                 mod_id="axis_2d_to_3d",
                 enable_toggle_list=["always"]):
        super().__init__(mod_id,
                         enable_toggle_list)

    # -----------------------------
    # 1) apply_2d
    # -----------------------------
    def apply_2d(self, stroke2d,
                 canvas_widget):
        print("processing")
        pts = stroke2d.points_2d
        if len(pts) < 2:
            return stroke2d  # 无法构成线

        p0 = np.array(pts[0],
                      dtype=float)
        p1 = np.array(pts[1],
                      dtype=float)
        init_dir = p1 - p0
        if np.linalg.norm(
                init_dir) < 1e-9:
            return stroke2d

            # 我们在世界坐标中取 +X, -X, +Y, -Y, +Z, -Z 的"无穷远"点
        axis_candidates = ["x",
                           "x",
                           "y",
                           "y",
                           "z",
                           "z"]
        vanish_pts = {}
        for axis_name in axis_candidates:
            vanish_pts[
                axis_name] = self.get_vanishing_point_screen(
                axis_name,
                canvas_widget)

        # 计算与笔画起点相连的方向向量
        cand_dirs = {}
        for axis_name, vp_screen in vanish_pts.items():
            dir_vec = vp_screen - p0
            cand_dirs[
                axis_name] = dir_vec


        # 选出与 init_dir 夹角最小者
        best_axis = None
        best_cos = -1
        for aname, avec in cand_dirs.items():
            c = self.cosine_similarity(
                init_dir, avec)
            if c > best_cos:
                best_cos = c
                best_axis = aname

        stroke2d.meta[
            'axis'] = best_axis  # 记录所选轴

        chosen_dir = cand_dirs[best_axis]
        norm_dir = np.linalg.norm(
            chosen_dir)
        if norm_dir < 1e-9:
            return stroke2d

        dir_unit = chosen_dir / norm_dir

        # 把所有点投影到 p0 + t*dir_unit
        proj_pts = []
        for p in pts:
            v_p = p - p0
            t = np.dot(v_p, dir_unit)
            new_p = p0 + t * dir_unit
            proj_pts.append(
                (new_p[0], new_p[1]))

        # 最后只保留2个端点
        stroke2d.points_2d = [
            proj_pts[0], proj_pts[-1]]
        return stroke2d

    def get_vanishing_point_screen(self,
                                   axis_name,
                                   canvas_widget):
        """
        在世界坐标中取一个极远点, 正负方向:
         'x+' => (1e6, 0, 0)
         'x-' => (-1e6,0, 0)
         ...
        投影到屏幕 => vanish point
        """
        bigval = 1e6
        if axis_name == "x":
            world_pt = np.array(
                [bigval, 0.0, 0.0],
                dtype=float)
        elif axis_name == "y":
            world_pt = np.array(
                [0.0, bigval, 0.0],
                dtype=float)
        else:  # "z"
            world_pt = np.array(
                [0.0, 0.0, bigval],
                dtype=float)

        return self.project_point_3d_to_2d(
            world_pt, canvas_widget)

    # -----------------------------
    # 2) apply_2dto3d
    # -----------------------------
    def apply_2dto3d(self, stroke2d,
                     canvas_widget):
        """
        1) 在2D空间上和已有3D线投影相交, 找最小id
        2) 若有相交, 得到 anchor_3d
          - 对 stroke2d的2端点做 '反投影 + 轴对齐' => 生成 coords_3d
        3) 若没相交, 用 stroke2d的第一个端点抬到 y=0, 并轴对齐另一端
        4) 生成 Stroke3D
        """
        pts2d = stroke2d.points_2d
        if len(pts2d) < 2:
            return None

        # step0: 获取此线段是对齐到 x,y,z 中哪一条
        axis = stroke2d.meta.get('axis',
                                 'x')  # 默认x

        p0_2d = np.array(pts2d[0],
                         dtype=float)
        p1_2d = np.array(pts2d[1],
                         dtype=float)

        # step1: 查找相交
        existing_3d_strokes = canvas_widget.stroke_manager_3d.get_all_strokes()
        existing_3d_strokes = sorted(
            existing_3d_strokes,
            key=lambda s: s.stroke_id)

        chosen_anchor_3d = None
        chosen_intersect_2d = None
        for s3d in existing_3d_strokes:
            line2d = self.project_3d_line_to_2d(
                s3d, canvas_widget)
            if len(line2d) < 2:
                continue
            # 只示例: 取 line2d首尾
            L0_2d = np.array(line2d[0],
                             dtype=float)
            L1_2d = np.array(line2d[-1],
                             dtype=float)
            inter_pt = self.intersect_2d_lines(
                p0_2d, p1_2d, L0_2d,
                L1_2d)
            if inter_pt is not None:
                # 计算 3D交点: 这里演示 "只取离 inter_pt 更近的端点当作 anchor_3d"
                dist0 = np.linalg.norm(
                    inter_pt - L0_2d)
                dist1 = np.linalg.norm(
                    inter_pt - L1_2d)
                if dist0 < dist1:
                    anchor_3d = \
                    s3d.coords_3d[0]
                else:
                    anchor_3d = \
                    s3d.coords_3d[-1]

                chosen_anchor_3d = anchor_3d
                chosen_intersect_2d = inter_pt
                break

        # step2: 如果有 anchor_3d, 则对线段两端做 "反投影 + 轴对齐"
        if chosen_anchor_3d is not None:
            p0_3d = self.reproject_axis_line_2dpt_to_3d(
                p0_2d, axis,
                chosen_anchor_3d,
                canvas_widget)
            p1_3d = self.reproject_axis_line_2dpt_to_3d(
                p1_2d, axis,
                chosen_anchor_3d,
                canvas_widget)
        else:
            # step3: 无相交 -> 线段首点落地, 整条线对齐 axis
            p0_3d = self.lift_to_ground_plane(
                p0_2d, canvas_widget)
            # 由于是 axis 对齐, p0_3d就是 anchor, 再投 p1_2d
            p1_3d = self.reproject_axis_line_2dpt_to_3d(
                p1_2d, axis, p0_3d,
                canvas_widget)

        coords_3d = np.array(
            [p0_3d, p1_3d],
            dtype=np.float32)
        stroke3d = Stroke3D(coords_3d,
                            stroke2d.stroke_id)
        return stroke3d

    # =================================================================
    # 反投影: 将 2D 点 (u,v) 变为 3D 射线与 y=0 平面求交 (真正的射线-平面交点)
    # =================================================================
    def lift_to_ground_plane(self, pt2d,
                             canvas_widget):
        """
        通过完整的 'near/far clip -> inv(MVP)' 流程，将 (u,v) 反投影到 y=0 平面。
        """
        u, v = pt2d
        renderer = canvas_widget.renderer
        w, h = canvas_widget.width(), canvas_widget.height()

        # 1) 转换到 NDC
        x_ndc = (u / w) * 2.0 - 1.0
        y_ndc = 1.0 - (v / h) * 2.0

        # 构造 near/far clip
        near_clip = np.array(
            [x_ndc, y_ndc, -1.0, 1.0],
            dtype=np.float32)
        far_clip = np.array(
            [x_ndc, y_ndc, 1.0, 1.0],
            dtype=np.float32)

        # 2) 逆 MVP
        proj = renderer.projection_matrix  # 4x4
        view = renderer.view_matrix  # 4x4
        mvp = proj @ view  # model=I
        inv_mvp = np.linalg.inv(mvp)

        # 3) 反变换到世界坐标
        near_world = inv_mvp @ near_clip
        far_world = inv_mvp @ far_clip
        if abs(near_world[3]) > 1e-9:
            near_world /= near_world[3]
        if abs(far_world[3]) > 1e-9:
            far_world /= far_world[3]

        ray_origin = near_world[
                     :3]  # (x,y,z)
        ray_dir = far_world[
                  :3] - ray_origin

        # 4) 求与 y=0 平面交点
        if abs(ray_dir[1]) < 1e-9:
            # 平行或近似平行
            return (ray_origin[0], 0.0,
                    ray_origin[
                        2])  # 退化写法

        t = -ray_origin[1] / ray_dir[
            1]  # y=0 => ray_origin.y + t*ray_dir.y =0
        # 若 t<0 => 交点在相机后方, 这里示例也不再特殊处理
        xw = ray_origin[0] + t * \
             ray_dir[0]
        yw = 0.0
        zw = ray_origin[2] + t * \
             ray_dir[2]
        return (xw, yw, zw)

    # =================================================================
    # reproject_axis_line_2dpt_to_3d
    #  当已有 anchor_3d, 且线段只在 axis 方向上可变动, 反投影 2D 点
    # =================================================================
    def reproject_axis_line_2dpt_to_3d(
            self, pt2d, axis, anchor_3d,
            canvas_widget):
        """
        如果笔画对齐 'x' 轴 => 在世界中 (X, anchor_3d.y, anchor_3d.z).
        我们用完整的 2D->3D 反投影拿到 (X',Y',Z') 然后在 yz 上对齐 anchor_3d 的 yz, 仅 x 保持射线计算.

        若 axis='y' => fix x=anchor_3d.x, z=anchor_3d.z; 仅 y 变化.
        若 axis='z' => fix x=anchor_3d.x, y=anchor_3d.y; 仅 z 变化.

        这里使用 “射线-平面组” 做法:
         1) 先用 near/far clip + inv(MVP) 得到 3D 射线
         2) 要求 (X(t), Y(t), Z(t)) 在 axis 对齐下与 anchor_3d 其余坐标相同 => 解方程.

        示例: axis='x' => Y(t)=anchor_3d.y, Z(t)=anchor_3d.z => 两个方程 => 这个射线只要能同时满足 => 我们得到 t => X(t).
        """
        # 1) 先拿到 camera + MVP
        renderer = canvas_widget.renderer
        w, h = canvas_widget.width(), canvas_widget.height()

        # 2) 构造射线(与 lift_to_ground_plane 同)
        u, v = pt2d
        x_ndc = (u / w) * 2.0 - 1.0
        y_ndc = 1.0 - (v / h) * 2.0
        near_clip = np.array(
            [x_ndc, y_ndc, -1, 1],
            dtype=np.float32)
        far_clip = np.array(
            [x_ndc, y_ndc, 1, 1],
            dtype=np.float32)

        mvp = renderer.projection_matrix @ renderer.view_matrix
        inv_mvp = np.linalg.inv(mvp)

        near_world = inv_mvp @ near_clip
        far_world = inv_mvp @ far_clip
        if abs(near_world[3]) > 1e-9:
            near_world /= near_world[3]
        if abs(far_world[3]) > 1e-9:
            far_world /= far_world[3]

        ray_origin = near_world[:3]
        ray_dir = far_world[
                  :3] - ray_origin

        # 3) 求 axis 对齐下的交点.
        #    设 param = t,  world_pt(t) = ray_origin + t*ray_dir
        #    如果 axis='x', => world_pt(t).y = anchor_3d[1], world_pt(t).z = anchor_3d[2]
        #    => ray_origin[1] + t*ray_dir[1] = anchor_3d[1]
        #       ray_origin[2] + t*ray_dir[2] = anchor_3d[2]
        #    形成2个方程, 求 t

        ax3d = np.array(anchor_3d,
                        dtype=float)

        if axis == 'x':
            # y(t)=ax3d.y => t1; z(t)=ax3d.z => t2, 若一致 => x(t) 即
            tvals = []
            if abs(ray_dir[1]) > 1e-12:
                t1 = (ax3d[1] -
                      ray_origin[1]) / \
                     ray_dir[1]
                tvals.append(t1)
            else:
                # 平行 => 如果 ray_origin[1]不等 => 无解, 否则无限多
                if abs(ax3d[1] -
                       ray_origin[
                           1]) > 1e-9:
                    # 无解 => fallback
                    return tuple(
                        ray_origin)
                tvals.append(0.0)  # 随便

            if abs(ray_dir[2]) > 1e-12:
                t2 = (ax3d[2] -
                      ray_origin[2]) / \
                     ray_dir[2]
                tvals.append(t2)
            else:
                if abs(ax3d[2] -
                       ray_origin[
                           2]) > 1e-9:
                    return tuple(
                        ray_origin)
                tvals.append(0.0)

            # 若 t1和t2相差很大 => 无法同满足 => 这里可以选平均 or fallback
            if len(tvals) == 2 and abs(
                    tvals[0] - tvals[
                        1]) < 1e-3:
                t_ = 0.5 * (tvals[0] +
                            tvals[1])
            else:
                # 退化写法(取第一个)
                t_ = tvals[0]

            pt_world = ray_origin + t_ * ray_dir
            # 强制 y,z = anchor
            pt_world[1] = ax3d[1]
            pt_world[2] = ax3d[2]
            return tuple(pt_world)

        elif axis == 'y':
            # fix x=anchor_3d.x, z=anchor_3d.z => 两方程
            tvals = []
            if abs(ray_dir[0]) > 1e-12:
                t1 = (ax3d[0] -
                      ray_origin[0]) / \
                     ray_dir[0]
                tvals.append(t1)
            else:
                if abs(ax3d[0] -
                       ray_origin[
                           0]) > 1e-9:
                    return tuple(
                        ray_origin)
                tvals.append(0.0)

            if abs(ray_dir[2]) > 1e-12:
                t2 = (ax3d[2] -
                      ray_origin[2]) / \
                     ray_dir[2]
                tvals.append(t2)
            else:
                if abs(ax3d[2] -
                       ray_origin[
                           2]) > 1e-9:
                    return tuple(
                        ray_origin)
                tvals.append(0.0)

            if len(tvals) == 2 and abs(
                    tvals[0] - tvals[
                        1]) < 1e-3:
                t_ = 0.5 * (tvals[0] +
                            tvals[1])
            else:
                t_ = tvals[0]

            pt_world = ray_origin + t_ * ray_dir
            pt_world[0] = ax3d[
                0]  # fix x
            pt_world[2] = ax3d[
                2]  # fix z
            return tuple(pt_world)

        else:  # axis='z'
            # fix x=anchor_3d.x, y=anchor_3d.y
            tvals = []
            if abs(ray_dir[0]) > 1e-12:
                t1 = (ax3d[0] -
                      ray_origin[0]) / \
                     ray_dir[0]
                tvals.append(t1)
            else:
                if abs(ax3d[0] -
                       ray_origin[
                           0]) > 1e-9:
                    return tuple(
                        ray_origin)
                tvals.append(0.0)

            if abs(ray_dir[1]) > 1e-12:
                t2 = (ax3d[1] -
                      ray_origin[1]) / \
                     ray_dir[1]
                tvals.append(t2)
            else:
                if abs(ax3d[1] -
                       ray_origin[
                           1]) > 1e-9:
                    return tuple(
                        ray_origin)
                tvals.append(0.0)

            if len(tvals) == 2 and abs(
                    tvals[0] - tvals[
                        1]) < 1e-3:
                t_ = 0.5 * (tvals[0] +
                            tvals[1])
            else:
                t_ = tvals[0]

            pt_world = ray_origin + t_ * ray_dir
            pt_world[0] = ax3d[0]
            pt_world[1] = ax3d[1]
            return tuple(pt_world)

    # =================================================================
    # 投影相关:  project_point_3d_to_2d / project_3d_line_to_2d
    # =================================================================
    def project_point_3d_to_2d(self,
                               pt3d,
                               canvas_widget):
        """
        用 renderer.projection_matrix/view_matrix 做 MVP 投影，得到(u,v)屏幕坐标
        """
        renderer = canvas_widget.renderer
        proj = renderer.projection_matrix  # 4x4
        view = renderer.view_matrix  # 4x4
        w, h = canvas_widget.width(), canvas_widget.height()

        mvp = proj @ view
        p4 = np.array(
            [pt3d[0], pt3d[1], pt3d[2],
             1.0], dtype=np.float32)
        clip = mvp @ p4
        if abs(clip[3]) < 1e-9:
            return np.array(
                [9999.0, 9999.0],
                dtype=float)
        ndc = clip[:3] / clip[3]
        u_ = (ndc[0] * 0.5 + 0.5) * w
        v_ = (1.0 - (ndc[
                         1] * 0.5 + 0.5)) * h
        return np.array([u_, v_],
                        dtype=float)

    def project_3d_line_to_2d(self,
                              stroke3d,
                              canvas_widget):
        coords = stroke3d.coords_3d
        pts2d = []
        for c in coords:
            pts2d.append(
                self.project_point_3d_to_2d(
                    c, canvas_widget))
        return pts2d

    # =================================================================
    # 线段相交(2D)
    # =================================================================
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
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 < 1e-9 or n2 < 1e-9:
            return -1
        return np.dot(v1, v2) / (
                    n1 * n2)