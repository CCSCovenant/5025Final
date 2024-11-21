def compute_curvature(sketch):
    pass


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
