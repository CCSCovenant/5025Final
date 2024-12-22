# logic/stroke_processor.py

from data.stroke_2d import Stroke2D
from data.stroke_3d import Stroke3D


class StrokeProcessor:
    """
    StrokeProcessor 维护一份 pipelineList (一系列modifier_id的顺序)，
    以及一个modifier_pool (所有可能的Modifier实例)。

    提供三个处理函数:
      - process_2d_stroke
      - process_2dto3d_stroke
      - process_3d_stroke

    对应地会从 pipelineList 中依次找可用的modifier，并调用对应 apply_xxx 方法。
    """

    def __init__(self,
                 feature_toggle_manager):
        self.feature_toggle_manager = feature_toggle_manager

        # pipelineList: 例如 ["smooth_2d", "basic_2dto3d", "snap3d_x"]
        # 具体由外部进行配置/赋值
        self.pipelineList_2d = []
        self.pipelineList_2d_to_3d = []
        self.pipelineList_3d = []



        # modifier_pool: key=modifier_id, val=BaseModifier子类实例
        self.modifier_pool = {}

    def register_modifier(self,
                          modifier):
        """
        把modifier对象加入pool
        :param modifier: BaseModifier子类实例
        """
        self.modifier_pool[
            modifier.mod_id] = modifier

    def process_2d_stroke(self,
                          stroke2d,canvas_widget):
        """
        依照 pipelineList 的顺序，调用2D Modifiers
        """
        for mod_id in self.pipelineList_2d:
            mod = self.modifier_pool.get(
                mod_id, None)
            if mod is None:
                continue
            # 检查feature toggles
            if not mod.check_enabled(
                    self.feature_toggle_manager):
                continue
            # 调用 apply_2d
            stroke2d = mod.apply_2d(
                stroke2d,canvas_widget)
        return stroke2d

    def process_2dto3d_stroke(self,
                              stroke2d,
                              canvas_widget):
        """
        依照 pipelineList 的顺序，查找2d->3d类型的mod并执行。
        这里的做法是一旦找到第一个 2d->3d 的mod并执行，得到的 Stroke3D 就进入后续 3D pipeline (process_3d_stroke)？
        具体逻辑看业务需求，这里给一个示例流程。
        """
        stroke3d = None

        # 找第一个2d->3d mod
        for mod_id in self.pipelineList_2d_to_3d:
            mod = self.modifier_pool.get(
                mod_id, None)
            if mod is None:
                continue
            if not mod.check_enabled(
                    self.feature_toggle_manager):
                continue
            # 调用 apply_2dto3d
            possible_3d = mod.apply_2dto3d(
                stroke2d,
                canvas_widget
            )
            if possible_3d is not None:
                stroke3d = possible_3d
                break

        return stroke3d

    def process_3d_stroke(self,
                          stroke3d,
                          canvas_width,
                          canvas_height,
                          projection_matrix,
                          view_matrix,
                          model_matrix):
        """
        依照 pipelineList 的顺序，调用3D Modifiers
        """
        for mod_id in self.pipelineList_3d:
            mod = self.modifier_pool.get(
                mod_id, None)
            if mod is None:
                continue
            if not mod.check_enabled(
                    self.feature_toggle_manager):
                continue
            stroke3d = mod.apply_3d(
                stroke3d,
                canvas_width,
                canvas_height,
                projection_matrix,
                view_matrix,
                model_matrix
            )
        return stroke3d
