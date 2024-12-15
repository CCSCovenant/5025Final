import OpenGL.GL as gl
import numpy as np


class Renderer3D:
    def __init__(self):
        self.projection_matrix = np.eye(
            4, dtype=np.float32)
        self.view_matrix = np.eye(4,
                                  dtype=np.float32)

    def initialize(self):
        gl.glClearColor(0.1, 0.1, 0.1,
                        1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resize(self, w, h):
        gl.glViewport(0, 0, w, h)
        aspect = w / h if h != 0 else 1
        # 构建透视投影矩阵 (简单示意)
        fov = np.radians(45.0)
        near = 0.1
        far = 100.0
        self.projection_matrix = perspective(
            fov, aspect, near, far)

    def render(self, strokes_3d,
               camera_rot,
               camera_dist=2.0):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # === 构造 View 矩阵 ===
        # 相机位置：在球坐标下 [r=camera_dist, 旋转角度camera_rot]
        # 以 yaw (camera_rot[0]) 绕 Y 轴, pitch (camera_rot[1]) 绕 X 轴
        eye = polar_to_cartesian(
            camera_dist, camera_rot[0],
            camera_rot[1])
        center = np.array(
            [0.0, 0.0, 0.0],
            dtype=np.float32)  # 看向原点
        up = np.array([0.0, 1.0, 0.0],
                      dtype=np.float32)
        self.view_matrix = look_at(eye,
                                   center,
                                   up)

        # 遍历笔画并绘制
        for stroke in strokes_3d:
            self.draw_stroke_line(
                stroke.get_points())

    def draw_stroke_line(self, points):
        # MVP = Projection * View
        mvp = self.projection_matrix @ self.view_matrix

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadMatrixf(mvp.T)

        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_LINE_STRIP)
        for p in points:
            gl.glVertex3f(p[0], p[1],
                          p[2])
        gl.glEnd()


# ========== 一些辅助函数 ==========
def perspective(fovy, aspect, znear,
                zfar):
    """ 构建透视投影矩阵，返回4x4的numpy数组 """
    f = 1.0 / np.tan(fovy / 2.0)
    mat = np.zeros((4, 4),
                   dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (zfar + znear) / (
                znear - zfar)
    mat[2, 3] = (2.0 * zfar * znear) / (
                znear - zfar)
    mat[3, 2] = -1.0
    return mat


def look_at(eye, center, up):
    """ 构建 LookAt 矩阵，用于 View Matrix """
    f = center - eye
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    mat = np.eye(4, dtype=np.float32)
    mat[0, 0], mat[0, 1], mat[0, 2] = s
    mat[1, 0], mat[1, 1], mat[1, 2] = u
    mat[2, 0], mat[2, 1], mat[2, 2] = -f

    # 平移
    translate = np.eye(4,
                       dtype=np.float32)
    translate[0, 3] = -eye[0]
    translate[1, 3] = -eye[1]
    translate[2, 3] = -eye[2]

    return mat @ translate


def polar_to_cartesian(r, yaw, pitch):
    """
    将极角 yaw,pitch(度) 转换为笛卡尔坐标 (x, y, z).
    yaw 围绕 Y 轴转, pitch 围绕 X 轴转.
    """
    yaw_rad = np.radians(yaw)
    pitch_rad = np.radians(pitch)

    # 先绕Y轴 yaw，再绕X轴 pitch
    # yaw=0, pitch=0时，默认为 (0,0,r)
    x = r * np.sin(yaw_rad) * np.cos(
        pitch_rad)
    y = r * np.sin(pitch_rad)
    z = r * np.cos(yaw_rad) * np.cos(
        pitch_rad)
    return np.array([x, y, z],
                    dtype=np.float32)

