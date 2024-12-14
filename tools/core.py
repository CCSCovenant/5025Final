import trimesh
import numpy as np

# 计算离散高斯曲率和均值曲率

def compute_curvature():
    pass
def compute_directional_curvature(mesh, point, direction, radius):
    # 高斯曲率
    gaussian_curvature = trimesh.curvature.discrete_gaussian_curvature_measure(
        mesh, [point], radius
    )[0]

    # 均值曲率
    mean_curvature = trimesh.curvature.discrete_mean_curvature_measure(
        mesh, [point], radius
    )[0]

    # 计算主曲率
    H = mean_curvature
    K = gaussian_curvature
    k_min = H - np.sqrt(max(0, H ** 2 - K))  # 确保根号内非负
    k_max = H + np.sqrt(max(0, H ** 2 - K))

    # 近似主方向（假设方向与法向量局部正交）
    # 对离散网格更复杂方向推导需要用PCA或法向量变化分析

    # 计算方向曲率
    # 假设方向是与主方向夹角 theta 的方向
    theta = np.arccos(np.dot(direction, [1, 0, 0]))  # 简单假设方向对齐 x 轴
    k_directional = k_min * np.cos(theta) ** 2 + k_max * np.sin(theta) ** 2

    return k_directional


def compute_displacement(angle,
                         rotation_axis,
                         sketch_curvature,
                         sketch):
    displacement_map = []
    for i in len(sketch):
        sketch_point = sketch[i]  # 2D coordinate of given point in the sketch
        sketch_k = sketch_curvature[i]  # curvature value

        radius = compute_radius(
            sketch_point,
            rotation_axis)
        invariant_curvature = 1 / radius





    return displacement_map


def compute_radius(point,
                   rotation_axis):
    return 1
