# logic/modifiers/base_modifier.py

class BaseModifier:
    """
    所有Modifier的基类。包含：
      - mod_id: 唯一标识
      - enable_toggle_list: 依赖的FeatureToggle名称列表
    并提供apply_2d, apply_2dto3d, apply_3d三个方法的空实现。
    """
    def __init__(self, mod_id, enable_toggle_list=None):
        self.mod_id = mod_id
        # 该Modifier依赖哪些toggle；只有在feature_toggle都满足时才执行
        self.enable_toggle_list = enable_toggle_list if enable_toggle_list else []

    def check_enabled(self, feature_toggle_manager):
        """
        返回本Modifier是否应该执行（前提是所有依赖的feature toggles都为True）
        """
        for toggle_name in self.enable_toggle_list:
            if not feature_toggle_manager.is_enabled(toggle_name):
                return False
        return True

    def apply_2d(self, stroke2d,canvas_widget):
        """
        对2D笔画的处理。默认不做任何处理。
        """
        return stroke2d

    def apply_2dto3d(self, stroke2d, canvas_width, canvas_height,
                     projection_matrix, view_matrix, model_matrix):
        """
        将2D笔画映射到3D笔画。默认无动作。
        返回: None 或 Stroke3D
        """
        return None

    def apply_3d(self, stroke3d, canvas_width, canvas_height,
                 projection_matrix, view_matrix, model_matrix):
        """
        对3D笔画的处理。默认不做任何处理。
        """
        return stroke3d
