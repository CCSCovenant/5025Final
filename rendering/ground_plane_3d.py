# data/ground_plane_3d.py

import numpy as np
import OpenGL.GL as gl

class GroundPlane3D:
    """
    Represents a ground plane in the 3D scene.
    For example, a large plane on Z=0 with a checkerboard pattern.
    """

    def __init__(self, size=10.0, divisions=10):
        """
        :param size: float - total size (extent) of the plane (half-extends in +/- X, +/- Y)
        :param divisions: how many checker squares in each dimension
        """
        self.size = size
        self.divisions = divisions
        self.color1 = (0.8, 0.8, 0.8)
        self.color2 = (0.4, 0.4, 0.4)
        self.active = True

    def render(self, model_matrix, view_matrix, projection_matrix):
        """
        用OpenGL绘制平面，并呈现网格或棋盘格。
        在Renderer3D中调用时，会先设置好MVP矩阵或使用glLoadMatrixf。
        """
        if not self.active:
            return
        # 构建MVP = projection_matrix @ view_matrix @ model_matrix
        mvp = projection_matrix @ view_matrix @ model_matrix

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadMatrixf(mvp.T)

        # 在Y=0平面上画一个棋盘，size大小 [-size, size] in X, [-size, size] in Z
        # divisions表示在X/Y方向上切分多少格
        step = (2.0*self.size) / self.divisions

        # 逐格绘制
        z_start = -self.size
        for iz in range(self.divisions):
            x_start = -self.size
            for ix in range(self.divisions):
                # 计算小方格 corners
                x0 = x_start + ix*step
                z0 = z_start + iz*step
                x1 = x0 + step
                z1 = z0 + step
                # 交错颜色
                if (ix + iz) % 2 == 0:
                    gl.glColor3f(*self.color1)
                else:
                    gl.glColor3f(*self.color2)
                gl.glBegin(gl.GL_QUADS)
                gl.glVertex3f(x0, 0.0, z0)
                gl.glVertex3f(x1, 0.0, z1)
                gl.glVertex3f(x1, 0.0, z0)
                gl.glVertex3f(x0, 0.0, z1)
                gl.glEnd()

        gl.glPopMatrix()
