class StrokeManager:
    def __init__(self):
        self.strokes_3d = []
        self.undo_stack = []

    def add_stroke(self, stroke_3d):
        self.strokes_3d.append(
            stroke_3d)
        # 清空undo_stack，因为新的操作出现了
        self.undo_stack.clear()

    def get_all_3d_strokes(self):
        return self.strokes_3d

    def undo(self):
        if self.strokes_3d:
            stroke = self.strokes_3d.pop()
            self.undo_stack.append(
                stroke)

    def redo(self):
        if self.undo_stack:
            stroke = self.undo_stack.pop()
            self.strokes_3d.append(
                stroke)
