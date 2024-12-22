#data/stroke_manager_3d.py

from data.stroke_3d import Stroke3D

class StrokeManager3D:
    def __init__(self):
        # 用字典存放 stroke_id -> stroke_3d
        self.strokes_3d = {}
        # 记录已生效操作（可被撤销）
        self.undo_stack = []
        # 记录已被撤销操作（可被重做）
        self.redo_stack = []

    def add_stroke(self, stroke_3d):
        """
        添加新的笔画到管理器，并记录到 undo_stack。
        一旦有新操作发生，需要清空 redo_stack。
        """
        self.strokes_3d[stroke_3d.stroke_id] = stroke_3d
        # 将本次操作("add", stroke对象)压入 undo 栈
        self.undo_stack.append(("add", stroke_3d))
        # 新操作使得之前的 redo 历史失效
        self.redo_stack.clear()

    def remove_stroke(self, stroke_id):
        """
        移除现有笔画，并记录到 undo_stack。
        同时清空 redo_stack。
        """
        if stroke_id in self.strokes_3d:
            stroke = self.strokes_3d.pop(stroke_id)
            # 将本次操作("remove", stroke对象)压入 undo 栈
            self.undo_stack.append(("remove", stroke))
            # 同样清空 redo 栈
            self.redo_stack.clear()

    def get_stroke_by_id(self, stroke_id):
        return self.strokes_3d.get(stroke_id, None)

    def get_all_strokes(self):
        return list(self.strokes_3d.values())

    def undo(self):
        """
        撤销最近一次操作：
          - 如果是添加操作，则在字典中删除该笔画
          - 如果是移除操作，则在字典中重新添加该笔画
        同时将“反向操作”压入 redo_stack
        """
        if not self.undo_stack:
            return  # 没有可撤销的操作

        op_type, stroke = self.undo_stack.pop()

        if op_type == "add":
            # 原操作是 add，这里需要“撤销添加”，即把它从字典中删掉
            if stroke.stroke_id in self.strokes_3d:
                self.strokes_3d.pop(stroke.stroke_id)
            # 并且将对应的反向操作 ("add", stroke) 推入 redo_stack
            # 注意：反向操作是让“下次 redo”可以把它重新加回来
            self.redo_stack.append(("add", stroke))

        elif op_type == "remove":
            # 原操作是 remove，这里需要“撤销移除”，把该笔画重新加回来
            self.strokes_3d[stroke.stroke_id] = stroke
            # 将对应的反向操作 ("remove", stroke) 推入 redo_stack
            # 这样下次 redo 时可以再次删掉它
            self.redo_stack.append(("remove", stroke))

    def redo(self):
        """
        重做最近被撤销的操作：
          - 如果是添加操作，则在字典中再次添加
          - 如果是移除操作，则在字典中再次删除
        同时将这个操作（同样是它自身）压回 undo_stack
        """
        if not self.redo_stack:
            return  # 没有可重做的操作

        op_type, stroke = self.redo_stack.pop()

        if op_type == "add":
            # 把这个笔画添加回来
            self.strokes_3d[stroke.stroke_id] = stroke
            # 将本操作压回到 undo_stack
            self.undo_stack.append(("add", stroke))

        elif op_type == "remove":
            # 把这个笔画删除
            if stroke.stroke_id in self.strokes_3d:
                self.strokes_3d.pop(stroke.stroke_id)
            # 将本操作压回到 undo_stack
            self.undo_stack.append(("remove", stroke))

