# rendering/renderer_3d.py

import OpenGL.GL as gl
import numpy as np
import matplotlib.pyplot as plt

class Renderer3D:
    def __init__(self):
        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.view_matrix = np.eye(4, dtype=np.float32)
        self.use_depth_color = True

    def initialize(self):
        gl.glClearColor(0.1,0.1,0.1,1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resize(self, w, h):
        gl.glViewport(0,0,w,h)
        aspect = w/h if h!=0 else 1.0
        # 构建透视投影
        self.projection_matrix = perspective(45.0, aspect, 0.1, 100.0)

    def render(self,
                              strokes_3d,
                              camera_rot,
                              camera_dist,
                              viewport_size,
                              lookat,
                              activated_tool=None):
        """
        渲染所有笔画，并根据选择状态设置颜色。同时批量维护每个笔画的屏幕坐标。
        """
        w, h = viewport_size
        gl.glViewport(0, 0, w, h)
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 计算 View 矩阵
        eye = polar_to_cartesian(
            camera_dist, camera_rot[0],
            camera_rot[1])
        eye = eye + lookat
        center = np.array(
            lookat,
            dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0],
                      dtype=np.float32)
        self.view_matrix = look_at(
            eye, center, up)

        # 计算 MVP 矩阵
        mvp = self.projection_matrix @ self.view_matrix  # (4,4)
        '''
        if ground_plane is not None:
            model_mat = np.eye(4,
                               dtype=np.float32)  # ground plane model transform
            ground_plane.render(
                model_mat,
                self.view_matrix,
                self.projection_matrix)
        '''
        # 批量投影所有笔画的 3D 坐标到 2D 屏幕坐标
        # 首先收集所有坐标
        if len(strokes_3d) > 0:
            # 批量投影所有笔画的 3D 坐标到 2D 屏幕坐标
            all_coords_3d = np.vstack(
                [stroke.coords_3d for
                 stroke in
                 strokes_3d])  # (Total_N, 3)
            stroke_lengths = [
                len(stroke.coords_3d)
                for stroke in
                strokes_3d]

            # 添加第四维齐次坐标
            all_coords_homog = np.hstack(
                (all_coords_3d, np.ones(
                    (
                    all_coords_3d.shape[
                        0], 1),
                    dtype=np.float32)))  # (Total_N, 4)

            # 计算 Clip 坐标
            clip_coords = (
                        mvp @ all_coords_homog.T).T  # (Total_N, 4)

            # 透视除法，忽略 w=0 的情况
            with np.errstate(
                    divide='ignore',
                    invalid='ignore'):
                ndc = np.where(
                    clip_coords[:,
                    3:4] != 0,
                    clip_coords[:,
                    :3] / clip_coords[:,
                          3:4],
                    0)  # (Total_N, 3)

            # 转换为屏幕坐标
            x_screen = (ndc[:,
                        0] * 0.5 + 0.5) * w
            y_screen = (1.0 - (ndc[:,
                               1] * 0.5 + 0.5)) * h  # Y轴翻转
            screen_coords = np.stack(
                (x_screen, y_screen),
                axis=-1)  # (Total_N, 2)

            # 将屏幕坐标分配回各个笔画
            start = 0
            for stroke, length in zip(
                    strokes_3d,
                    stroke_lengths):
                if length > 0:
                    stroke.screen_coords = screen_coords[
                                           start:start + length]
                else:
                    stroke.screen_coords = np.empty(
                        (0, 2),
                        dtype=np.float32)
                start += length

            # 遍历所有笔画，设置颜色并绘制
            for stroke in strokes_3d:
                # 如果未启用深度映射，就用 stroke 原有的选中/悬停/默认颜色
                if not self.use_depth_color:
                    if stroke.is_selected:
                        r, g, b = (
                        1.0, 1.0,
                        0.0)  # 选中：黄色
                    elif stroke.is_hovered:
                        r, g, b = (
                        0.0, 1.0,
                        0.0)  # 悬停：绿色
                    else:
                        r, g, b = stroke.color  # 普通：自定义

                    gl.glColor3f(r, g,
                                 b)
                    gl.glLoadMatrixf(
                        mvp.T)

                    if len(stroke.coords_3d) > 0:
                        gl.glBegin(
                            gl.GL_LINE_STRIP)
                        for p in stroke.coords_3d:
                            gl.glVertex3f(
                                p[0],
                                p[1],
                                p[2])
                        gl.glEnd()

                else:
                    # 如果开启深度映射，每个顶点根据与 eye 的距离计算颜色 (R,0,B)


                    gl.glLoadMatrixf(
                        mvp.T)
                    if len(stroke.coords_3d) > 0:
                        gl.glBegin(
                            gl.GL_LINE_STRIP)
                        for p in stroke.coords_3d:
                            dist = np.linalg.norm(
                                p - eye)
                            # 使用一个简易函数：蓝色分量在近处~1，随 dist 增加衰减
                            # (可调节 0.2, 0.3 等让近处变化更明显)
                            rgb = self.distance_to_rgb(dist)

                            if stroke.is_selected:
                                r, g, b = (
                                    1.0,
                                    1.0,
                                    0.0)  # 选中：黄色
                            elif stroke.is_hovered:
                                r, g, b = (
                                    0.0,
                                    1.0,
                                    0.0)  # 悬停：绿色
                            else:
                                r, g, b = (
                                    rgb[0],rgb[1],rgb[2]
                                )
                            gl.glColor3f(
                                r,
                                g,
                                b)
                            gl.glVertex3f(
                                p[0],
                                p[1],
                                p[2])
                        gl.glEnd()

            # 绘制选择圆（如果有）
        if activated_tool is not None:
            activated_tool.render_tool_icon(self,viewport_size)


    def render_tools_hover_icon(self,tool):
        pass
    def render_selection_circle(self, cx, cy, radius, viewport_size):
            """
            在屏幕空间直接画一个2D圆环，用于指示选择工具的位置
            这儿可用正交投影或直接 glOrtho.
            """
            w, h = viewport_size
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glOrtho(0, w, h, 0, -1, 1)  # 2D正交投影

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            gl.glLoadIdentity()

            # 画圆圈 (2D)
            gl.glColor3f(1.0, 0.0, 0.0)
            segments = 64
            gl.glBegin(gl.GL_LINE_LOOP)
            for i in range(segments):
                angle = 2*np.pi*i/segments
                x = cx + radius*np.cos(angle)
                y = cy + radius*np.sin(angle)
                gl.glVertex2f(x, y)
            gl.glEnd()

            gl.glPopMatrix()
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glPopMatrix()

            gl.glMatrixMode(gl.GL_MODELVIEW)

    def distance_to_rgb(self,distance,
                        min_distance=0.0,
                        max_distance=25.0,
                        colormap='viridis'):
        """
        Convert a distance value to an RGB color based on a colormap.

        Parameters:
            distance (float): The input distance value.
            min_distance (float): The minimum distance value, mapped to the start of the colormap.
            max_distance (float): The maximum distance value, mapped to the end of the colormap.
            colormap (str): The name of the Matplotlib colormap to use.

        Returns:
            tuple: A tuple of (R, G, B) values, each in the range [0, 1].
        """
        # Normalize the distance value to [0, 1]
        norm_distance = (
                                    distance - min_distance) / (
                                    max_distance - min_distance)
        norm_distance = np.clip(
            norm_distance, 0.0,
            1.0)  # Ensure within [0, 1]

        # Get the colormap
        cmap = plt.get_cmap(colormap)

        # Convert normalized distance to an RGB color
        rgba = cmap(norm_distance)
        return rgba[
               :3]  # Exclude the alpha channel

    def project_to_screen_batch(self,
                                strokes_3d,
                                mvp_matrix,
                                viewport_size):
        """
        批量计算所有笔画的屏幕坐标，并更新 Stroke3D 对象。
        """
        w, h = viewport_size
        # 收集所有坐标
        all_coords_3d = np.vstack(
            [stroke.coords_3d for stroke in
             strokes_3d])  # (Total_N, 3)
        num_strokes = len(strokes_3d)
        stroke_lengths = [
            len(stroke.coords_3d) for stroke
            in strokes_3d]

        # 添加第四维齐次坐标
        all_coords_homog = np.hstack((
                                     all_coords_3d,
                                     np.ones(
                                         (
                                         all_coords_3d.shape[
                                             0],
                                         1),
                                         dtype=np.float32)))  # (Total_N, 4)

        # 计算 Clip 坐标
        clip_coords = (
                    mvp_matrix @ all_coords_homog.T).T  # (Total_N, 4)

        # 透视除法
        ndc = clip_coords[:,
              :3] / clip_coords[:,
                    3].reshape(-1,
                               1)  # (Total_N, 3)

        # 转换为屏幕坐标
        x_screen = (ndc[:,
                    0] * 0.5 + 0.5) * w
        y_screen = (1.0 - (ndc[:,
                           1] * 0.5 + 0.5)) * h  # Y轴翻转
        screen_coords = np.stack(
            (x_screen, y_screen),
            axis=-1)  # (Total_N, 2)

        # 将屏幕坐标分配回各个笔画
        start = 0
        for stroke, length in zip(
                strokes_3d, stroke_lengths):
            stroke.screen_coords = screen_coords[
                                   start:start + length]
            start += length
# 辅助函数
def perspective(fov_deg, aspect, znear, zfar):
    f = 1.0 / np.tan(np.radians(fov_deg)/2)
    mat = np.zeros((4,4), dtype=np.float32)
    mat[0,0] = f/aspect
    mat[1,1] = f
    mat[2,2] = (zfar+znear)/(znear-zfar)
    mat[2,3] = (2*zfar*znear)/(znear-zfar)
    mat[3,2] = -1
    return mat

def look_at(eye, center, up):
    f = center - eye
    f /= np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)

    mat = np.eye(4, dtype=np.float32)
    mat[0,0:3] = s
    mat[1,0:3] = u
    mat[2,0:3] = -f

    trans = np.eye(4, dtype=np.float32)
    trans[0,3] = -eye[0]
    trans[1,3] = -eye[1]
    trans[2,3] = -eye[2]

    return mat @ trans

def polar_to_cartesian(r, yaw_deg, pitch_deg):
    yaw = np.radians(yaw_deg)
    pitch = np.radians(pitch_deg)
    x = r * np.sin(yaw) * np.cos(pitch)
    y = r * np.sin(pitch)
    z = r * np.cos(yaw) * np.cos(pitch)
    return np.array([x,y,z], dtype=np.float32)

