#data/stroke_manager_2d.py
class StrokeManager2D:
    def __init__(self):
        # 用一个 dict 来存所有2D笔画： key=stroke_id, val=Stroke2D对象
        self.strokes_2d = {}
        # undo/redo 栈可根据需求来
        self.undo_stack = []

        # 这里可以记录全局的相机信息，也可以每个笔画单独存
        # self.camera_rot = (0.0, 0.0)
        # self.camera_dist = 3.0

        # 或者只存储「(camera_rot, camera_dist, strokes_2d)」快照的历史

    def add_stroke(self, stroke_2d):
        self.strokes_2d[stroke_2d.stroke_id] = stroke_2d
        self.undo_stack.clear()

    def get_stroke_by_id(self, stroke_id):
        return self.strokes_2d.get(stroke_id, None)

    def get_all_strokes(self):
        return list(self.strokes_2d.values())

    def undo(self):
        # 具体逻辑请自行实现，这里示例化
        if self.strokes_2d:
            last_id = list(self.strokes_2d.keys())[-1]
            stroke = self.strokes_2d.pop(last_id)
            self.undo_stack.append(stroke)

    def redo(self):
        if self.undo_stack:
            stroke = self.undo_stack.pop()
            self.strokes_2d[stroke.stroke_id] = stroke
