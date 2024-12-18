#data/stroke_manager_3d.py

from data.stroke_3d import Stroke3D

class StrokeManager3D:
    def __init__(self):
        self.strokes_3d = {}
        self.undo_stack = []

    def add_stroke(self, stroke_3d):
        self.strokes_3d[stroke_3d.stroke_id] = stroke_3d
        self.undo_stack.clear()

    def get_stroke_by_id(self, stroke_id):
        return self.strokes_3d.get(stroke_id, None)

    def get_all_strokes(self):
        return list(self.strokes_3d.values())

    def undo(self):
        if self.strokes_3d:
            last_id = list(self.strokes_3d.keys())[-1]
            stroke = self.strokes_3d.pop(last_id)
            self.undo_stack.append(stroke)

    def redo(self):
        if self.undo_stack:
            stroke = self.undo_stack.pop()
            self.strokes_3d[stroke.stroke_id] = stroke
