from pylowstroke.sketch_tools import *
from pylowstroke.sketch_core import *
def build_sketch(strokes,width,height):
    sketch = Sketch()
    sketch.width = width
    sketch.height = height
    sketch.strokes = []
    sketch.sketch_folder = './tmp'
    for raw_stroke in strokes:
        stroke = load_stroke_from_raw_stroke(raw_stroke)
        sketch.strokes.append(stroke)
    sketch.update_stroke_indices()
    for i, s in enumerate(sketch.strokes):
        s.original_id = [i]
        s.original_points = deepcopy(s.points_list)
        s.original_coords = deepcopy(s.points_list)
        if s.has_data("time"):
            s.average_speed = s.speed()
        else:
            s.average_speed = 0.0
        if s.has_data("pressure"):
            s.mean_pressure = s.get_mean_data("pressure")
        else:
            s.mean_pressure = 0.5
    return sketch

def load_stroke_from_raw_stroke(raw_stroke):


    points_list = [StrokePoint(x[0], x[1]) for x in
              raw_stroke.points_2d]
    for pt_id in range(
            len(points_list)):
        points_list[pt_id].add_data(
            "pressure", 1.0)
    stroke = Stroke(points_list, 1.0)

    return stroke

def extract_fixed_strokes(batches):
    fixed_strokes = batches[-1]["fixed_strokes"]
    proxies = batches[-1]["final_proxies"]
    for p_id, p in enumerate(proxies):
        if p is not None and len(p) > 0:
            fixed_strokes[p_id] = p
    for i, s in enumerate(fixed_strokes):
        fixed_strokes[i] = np.array(s)
    return fixed_strokes
