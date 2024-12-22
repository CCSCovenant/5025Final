# coding=utf-8
# axis_indicator_widget.py

import numpy as np
from PyQt5.QtWidgets import \
    QOpenGLWidget
from PyQt5.QtCore import Qt
import OpenGL.GL as gl


def make_arrow():
    """
    简单返回一个“箭头”模型的顶点列表 + 颜色/索引等
    这里仅示意，可以画一条线 + 三角锥体
    """
    # 这只是最简化的：一条线+末端一个小cone等
    # 先返回顶点 (demo)
    # 你可写更复杂的VBO
    line_vertices = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],  # X轴长1
    ]
    # 箭头(三角形扇形)
    cone_vertices = [
        [1.0, 0.0, 0.0],  # 基点(连接线的末端)
        [0.8, 0.05, 0.05],
        [0.8, -0.05, 0.05],
        [0.8, -0.05, -0.05],
        [0.8, 0.05, -0.05],
    ]
    return line_vertices, cone_vertices


class AxisIndicatorWidget(
    QOpenGLWidget):
    """
    一个小部件，用于在左下角显示XYZ轴方向箭头。
    会从外部(如CanvasWidget)获取相机旋转信息，并将其应用到此小部件的视图变换中。
    """

    def __init__(self, canvas_widget,
                 parent=None):
        super().__init__(parent)
        self.canvas_widget = canvas_widget
        self.setFixedSize(100,
                          100)  # 小部件大小可自定

        # 预先构建 X/Y/Z 三条箭头的顶点数据
        # 让X是红色, Y是绿色, Z是蓝色
        self.arrow_data = {}
        # X
        lineX, coneX = make_arrow()  # 它默认沿X正方向
        self.arrow_data['x'] = (
        lineX, coneX, (1.0, 0.0, 0.0))
        # Y
        lineY, coneY = make_arrow()  # 需要旋转成沿Y
        # 后面渲染时再做一个额外旋转
        self.arrow_data['y'] = (
        lineY, coneY, (0.0, 1.0, 0.0))
        # Z
        lineZ, coneZ = make_arrow()  # 需要旋转成沿Z
        self.arrow_data['z'] = (
        lineZ, coneZ, (0.0, 0.0, 1.0))

    def initializeGL(self):
        gl.glClearColor(0.0, 0.0, 0.0,
                        0.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        # 这里设置一个小透视或正交都行，这里选择正交
        gl.glMatrixMode(
            gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # 为了看清箭头，取个小范围
        # 例如正交 [-1.2, 1.2] * [-1.2,1.2] in XY
        gl.glOrtho(-1.2, 1.2, -1.2, 1.2,
                   -2.0, 2.0)

        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # 1) 读取canvas_widget的camera_rot(或view_matrix)
        #    这里假设canvas_widget.camera_rot = [yaw, pitch]
        #    你可能需要做相应的变换
        yaw, pitch = \
        self.canvas_widget.camera_rot[
            0], \
        self.canvas_widget.camera_rot[1]

        # 2) 应用一个与canvas_widget相同的旋转(仅旋转, 不做平移/缩放)
        #    这里演示: 先绕Y转 yaw, 再绕X转 pitch
        #    (你也可用glMultMatrixf对view_matrix简化)
        gl.glRotatef(-pitch, 1, 0,
                     0)  # 注意方向可能要反
        gl.glRotatef(-yaw, 0, 1, 0)

        # 3) 绘制坐标轴(每个轴都做相应的旋转让它正确指向)
        #    X轴: 不需要额外旋转
        self.draw_arrow(
            *self.arrow_data['x'],
            axis='x')
        #    Y轴: 绕Z轴+90度 => 让原先X正方向对齐Y
        gl.glPushMatrix()
        gl.glRotatef(90, 0, 0, 1)
        self.draw_arrow(
            *self.arrow_data['y'],
            axis='y')
        gl.glPopMatrix()
        #    Z轴: 绕Y轴,-90度 => 让X对齐Z
        gl.glPushMatrix()
        gl.glRotatef(-90, 0, 1, 0)
        self.draw_arrow(
            *self.arrow_data['z'],
            axis='z')
        gl.glPopMatrix()

    def draw_arrow(self, line_data,
                   cone_data, color_rgb,
                   axis='x'):
        """
        line_data: [(x0,y0,z0), (x1,y1,z1)]
        cone_data: ...
        color_rgb: (r,g,b)
        """
        gl.glColor3f(*color_rgb)
        gl.glBegin(gl.GL_LINES)
        for v in line_data:
            gl.glVertex3f(v[0], v[1],
                          v[2])
        gl.glEnd()

        # 画箭头(cone)
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        for v in cone_data:
            gl.glVertex3f(v[0], v[1],
                          v[2])
        gl.glEnd()
