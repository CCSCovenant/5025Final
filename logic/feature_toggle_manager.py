# coding=utf-8
# logic/feature_toggle_manager.py
# 功能开关管理器：用于统一管理系统内各种可开关式特性（如防抖、辅助线对齐等）

class FeatureToggleManager:
    """
    A manager for feature toggles (on/off switches for certain functionalities).
    功能开关管理器，用于统一管理各种布尔型特性开关。

    Example:
        toggle_manager = FeatureToggleManager()
        toggle_manager.set_feature("debounce", True)
        toggle_manager.is_enabled("debounce") -> True
    """

    def __init__(self):
        # 内部使用字典存储特性名称和布尔值
        self.features = {
            "debounce": False,  # 防抖开关
            "assist_lines": False
            # 辅助线/对齐开关
        }

    def set_feature(self, feature_name,
                    enabled):
        """
        Set a given feature to enabled/disabled.
        设置指定特性开关状态。

        :param feature_name: str - The name of the feature.
        :param enabled: bool - True to enable, False to disable.
        """
        if feature_name in self.features:
            self.features[
                feature_name] = enabled

    def is_enabled(self, feature_name):
        """
        Check if a given feature is enabled.
        检查指定特性是否开启。

        :param feature_name: str
        :return: bool
        """
        return self.features.get(
            feature_name, False)
