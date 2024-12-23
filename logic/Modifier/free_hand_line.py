import numpy as np
from .base_modifier import BaseModifier
from data.stroke_3d import Stroke3D
from logic.stroke_2d_to_3d import \
    convert_2d_stroke_to_3d


class FreeHandModifier(BaseModifier):
    """
    主要实现:
      1) apply_2d(stroke2d, canvas_widget):
         - 把用户输入转换成直线

      2) apply_2dto3d(stroke2d, canvas_widget):
         - 获取已有3D笔画, 投影到2D检查相交(若有多个,选stroke_id最小)
           得到 3D交点 anchor_3d
         - 如果找到 anchor_3d, 则对整条线(两个端点)执行“反投影+轴对齐”:
           线段在 3D 中只在某个坐标轴方向变化, 其余分量与 anchor_3d 相同
         - 若没找到交点, 则假设起点落在 y=0, 并沿指定轴方向计算另一个端点3D坐标
    """

    def __init__(self,
                 mod_id="free_hand_line",
                 enable_toggle_list=["free_hand_line"]):
        super().__init__(mod_id,
                         enable_toggle_list)

    # -----------------------------
    # 1) apply_2d
    # -----------------------------
    def apply_2d(self, stroke2d,
                 canvas_widget):
        pts = stroke2d.points_2d
        if len(pts) < 2:
            return stroke2d  # 无法构成线

        p0 = np.array(pts[0],
                      dtype=float)
        p1 = np.array(pts[-1],
                      dtype=float)

        # 最后只保留2个端点
        stroke2d.points_2d = [
            p0, p1]
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

        intersections = []  # 存储 (dist, inter_pt, stroke3d)

        for s3d in existing_3d_strokes:
            if len(s3d.coords_3d) < 2:
                continue

            e = 1e-2
            s3d_p0 = np.array(s3d.coords_3d[0],
                             dtype=float)
            s3d_p1= np.array(s3d.coords_3d[-1], dtype=float)

            direction = s3d_p1 - s3d_p0
            unit_direction = direction / np.linalg.norm(
                direction)

            # Extend the line
            new_p1 = s3d_p0 - e * unit_direction
            new_p2 = s3d_p1 + e * unit_direction


            extends3d = Stroke3D([new_p1,new_p2])
            line2d = self.project_3d_line_to_2d(
                extends3d, canvas_widget)
            if len(line2d) < 2:
                continue
            # 这里只取首尾
            L0_2d = np.array(line2d[0],
                             dtype=float)
            L1_2d = np.array(line2d[-1],
                             dtype=float)

            inter_pt = self.intersect_2d_lines(
                p0_2d, p1_2d, L0_2d,
                L1_2d)
            if inter_pt is not None:
                # 计算 inter_pt 到 p0_2d 的距离
                dist_to_p0 = np.linalg.norm(inter_pt - p0_2d)
                dist_to_p1 = np.linalg.norm(inter_pt - p1_2d)
                intersections.append((
                                     dist_to_p0,
                                     dist_to_p1,
                                     inter_pt,
                                     s3d))
        # step2: 如果有 anchor_3d, 则对线段两端做 "反投影 + 轴对齐"
        if len(intersections) > 1:
            # 选距离 p0_2d 最小的
            intersections.sort(
                key=lambda x: x[
                    0])  # dist ascending
            chosen_inter_pt_0 = \
            intersections[0][2]  # 2D相交点
            chosen_s3d_0 = \
            intersections[0][3]  # 对应线段

            # 将 chosen_inter_pt 反投影到 chosen_s3d
            anchor_3d1 = self.unproject_2d_point_onto_3d_line(
                chosen_inter_pt_0,
                chosen_s3d_0,
                canvas_widget)

            intersections.sort(
                key=lambda x: x[
                    1])  # dist ascending
            chosen_inter_pt_1 = \
                intersections[0][
                    2]  # 2D相交点
            chosen_s3d_1 = \
                intersections[0][
                    3]  # 对应线段

            # 将 chosen_inter_pt 反投影到 chosen_s3d
            anchor_3d2 = self.unproject_2d_point_onto_3d_line(
                chosen_inter_pt_1,
                chosen_s3d_1,
                canvas_widget)

            pred_coords_3d = np.array(
            [anchor_3d1, anchor_3d2],
            dtype=np.float32)
            pred3d = Stroke3D(pred_coords_3d)
            p0_3d = self.unproject_2d_point_onto_3d_line(
                p0_2d, pred3d,
                canvas_widget)
            p1_3d = self.unproject_2d_point_onto_3d_line(
                p1_2d, pred3d,
                canvas_widget)
        else:
            return None

        coords_3d = np.array(
            [p0_3d, p1_3d],
            dtype=np.float32)
        stroke3d = Stroke3D(coords_3d,
                            stroke_id=stroke2d.stroke_id)
        return stroke3d



    # =================================================================
    # reproject_axis_line_2dpt_to_3d
    #  当已有 anchor_3d, 且线段只在 axis 方向上可变动, 反投影 2D 点
    # =================================================================
    def unproject_2d_point_onto_3d_line(
            self, inter_pt, stroke3d,
            canvas_widget):
        """
        假设 stroke3d.coords_3d = [L0_3d, L1_3d] 表示一条 3D 线段。
        step:
          1) 将 inter_pt => 一条射线(r_o, r_d)
          2) 在 3D 中, 对 "线段 L(t)=L0 + t*(L1-L0)" 做射线-线段最近点 or param 解
          3) 返回该 3D 坐标(就是 2D交点在 3D上对应的真实点)

        示例: 仅展示"射线-线段"的最近点(最短距离)做近似.
              也可做线-线相交(若那条线在无限延长).
        """
        # 1) 先构造 2D->3D 射线
        r_o, r_d = self.build_ray_from_screen_pt(
            inter_pt, canvas_widget)

        # 2) 线段: P(t)= L0 + t*(L1-L0), t in [0,1]
        L0_3d = stroke3d.coords_3d[0]
        L1_3d = stroke3d.coords_3d[-1]
        v_line = L1_3d - L0_3d  # 3D向量

        # 3) 做 "射线-线段" 最近点(简化：线对线最近点)
        #    param ray: r(t)=r_o + t*r_d
        #    param line: L(u)=L0 + u*v_line
        #    见: "线-线最短距离" 常见公式
        #    这里只做示例, 并假定 r_d, v_line不平行
        #    (若平行需处理退化情况).
        A = np.dot(r_d, r_d)
        B = np.dot(r_d, v_line)
        C = np.dot(v_line, v_line)
        w0 = r_o - L0_3d
        D = np.dot(r_d, w0)
        E = np.dot(v_line, w0)

        denom = A * C - B * B
        if abs(denom) < 1e-9:
            # 退化, 平行或近似平行 => 取 L0_3d
            return L0_3d

        sc = (B * E - C * D) / denom
        tc = (A * E - B * D) / denom

        # sc => param for r,   tc => param for L

        # 4) 线段上的点: anchor_3d
        anchor_3d = L0_3d + tc * v_line
        return anchor_3d

    def build_ray_from_screen_pt(self,
                                 pt2d,
                                 canvas_widget):
        """
        构建 "从相机出发" 的3D射线: r_o, r_d
        """
        renderer = canvas_widget.renderer
        w, h = canvas_widget.width(), canvas_widget.height()
        x_ndc = (pt2d[
                     0] / w) * 2.0 - 1.0
        y_ndc = 1.0 - (
                    pt2d[1] / h) * 2.0
        near_clip = np.array(
            [x_ndc, y_ndc, -1, 1],
            dtype=np.float32)
        far_clip = np.array(
            [x_ndc, y_ndc, 1, 1],
            dtype=np.float32)

        mvp = renderer.projection_matrix @ renderer.view_matrix
        inv_mvp = np.linalg.inv(mvp)

        p_near = inv_mvp @ near_clip
        p_far = inv_mvp @ far_clip
        if abs(p_near[3]) > 1e-9:
            p_near /= p_near[3]
        if abs(p_far[3]) > 1e-9:
            p_far /= p_far[3]

        r_o = p_near[:3]  # origin
        r_d = p_far[
              :3] - r_o  # direction
        return r_o, r_d

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