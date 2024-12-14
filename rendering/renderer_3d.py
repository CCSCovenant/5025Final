import OpenGL.GL as gl
import numpy as np
from PyQt5.QtGui import \
    QOpenGLShaderProgram


class Renderer3D:
    def __init__(self):
        # 如果使用现代OpenGL，需要初始化shader等
        self.shader_program = None
        self.projection_matrix = np.eye(
            4, dtype=np.float32)
        self.view_matrix = np.eye(4,
                                  dtype=np.float32)

    def initialize(self):
        # 初始化OpenGL状态，比如 glClearColor
        gl.glClearColor(0.1, 0.1, 0.1,
                        1.0)
        # 设置深度测试等
        gl.glEnable(gl.GL_DEPTH_TEST)

        # 如果使用自定义shader，可以在这里编译、链接
        # self.shader_program = QOpenGLShaderProgram()
        # ... compile shaders ...

    def resize(self, w, h):
        gl.glViewport(0, 0, w, h)
        # 设置投影矩阵，例如一个简单的正交投影或者透视投影
        aspect = w / h if h != 0 else 1
        # 这里可以用numpy生成投影矩阵
        # 简单演示：正交投影矩阵
        self.projection_matrix = np.eye(
            4, dtype=np.float32)
        # 也可以使用透视投影

    def render(self, strokes_3d,
               camera_rot):
        # 清除颜色和深度缓存
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 构造 view_matrix，用camera_rot来旋转
        # 这里只是简单示意，可以使用成熟的数学库做矩阵旋转
        rx = np.eye(4, dtype=np.float32)
        ry = np.eye(4, dtype=np.float32)
        # 旋转 X 轴
        angle_x = np.radians(
            camera_rot[1])
        rx[1, 1] = np.cos(angle_x)
        rx[1, 2] = -np.sin(angle_x)
        rx[2, 1] = np.sin(angle_x)
        rx[2, 2] = np.cos(angle_x)
        # 旋转 Y 轴
        angle_y = np.radians(
            camera_rot[0])
        ry[0, 0] = np.cos(angle_y)
        ry[0, 2] = np.sin(angle_y)
        ry[2, 0] = -np.sin(angle_y)
        ry[2, 2] = np.cos(angle_y)

        self.view_matrix = rx @ ry  # 先 x 后 y

        # 针对每个stroke_3d进行绘制
        for stroke in strokes_3d:
            points = stroke.get_points()
            # 这里使用最简单的方式画线（GL_LINE_STRIP）
            self.draw_stroke_line(
                points)

    def draw_stroke_line(self, points):
        # 生成 MVP 矩阵 = Projection * View
        # 这里没处理 Model Matrix，假设 Model 是单位矩阵
        mvp = self.projection_matrix @ self.view_matrix

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadMatrixf(
            mvp.T)  # OpenGL需要转置

        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_LINE_STRIP)
        for p in points:
            gl.glVertex3f(p[0], p[1],
                          p[2])
        gl.glEnd()
