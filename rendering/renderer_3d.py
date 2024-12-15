# rendering/renderer_3d.py

import OpenGL.GL as gl
import numpy as np

class Renderer3D:
    def __init__(self):
        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.view_matrix = np.eye(4, dtype=np.float32)

    def initialize(self):
        gl.glClearColor(0.1,0.1,0.1,1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resize(self, w, h):
        gl.glViewport(0,0,w,h)
        aspect = w/h if h!=0 else 1.0
        # 构建透视投影
        self.projection_matrix = perspective(45.0, aspect, 0.1, 100.0)

    def render_with_selection(self,
                              strokes_3d,
                              camera_rot,
                              camera_dist,
                              viewport_size,
                              selection_manager):
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
        center = np.array(
            [0.0, 0.0, 0.0],
            dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0],
                      dtype=np.float32)
        self.view_matrix = look_at(
            eye, center, up)

        # 计算 MVP 矩阵
        mvp = self.projection_matrix @ self.view_matrix  # (4,4)

        # 批量投影所有笔画的 3D 坐标到 2D 屏幕坐标
        # 首先收集所有坐标
        if len(strokes_3d) == 0:
            # 没有笔画需要渲染，直接返回
            return
        all_coords_3d = np.vstack(
            [stroke.coords_3d for stroke
             in
             strokes_3d])  # (Total_N, 3)
        num_strokes = len(strokes_3d)
        stroke_lengths = [
            len(stroke.coords_3d) for
            stroke in strokes_3d]

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
                    mvp @ all_coords_homog.T).T  # (Total_N, 4)

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
                strokes_3d,
                stroke_lengths):
            stroke.screen_coords = screen_coords[
                                   start:start + length]
            start += length

        # 遍历所有笔画，设置颜色并绘制
        start = 0
        for stroke, length in zip(
                strokes_3d,
                stroke_lengths):
            # 根据状态设置颜色
            if selection_manager.is_selected(
                    stroke):
                r, g, b = (
                1.0, 1.0, 0.0)  # 选中：黄色
            elif selection_manager.is_hovered(
                    stroke):
                r, g, b = (
                0.0, 1.0, 0.0)  # 悬停：绿色
            else:
                r, g, b = stroke.color  # 普通：白色或自定义颜色

            gl.glColor3f(r, g, b)
            gl.glLoadMatrixf(mvp.T)

            # 批量绘制
            gl.glBegin(gl.GL_LINE_STRIP)
            for p in stroke.coords_3d:
                gl.glVertex3f(p[0],
                              p[1],
                              p[2])
            gl.glEnd()


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

