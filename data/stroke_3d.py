import numpy as np


class Stroke3D:
    def __init__(self,
                 coords_3d: np.ndarray):
        """
        coords_3d: shape=(N,3)，每一行是一个3D点
        """
        self.coords_3d = coords_3d

    def __len__(self):
        return len(self.coords_3d)

    def get_points(self):
        return self.coords_3d
