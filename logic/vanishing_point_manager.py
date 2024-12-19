# coding=utf-8
# logic/vanishing_point_manager.py
# VanishingPointManager: 用于管理消失点坐标和参考模式

import json
import os

class VanishingPointManager:
    """
    Manage vanishing points and mode:
      mode: 0 (no reference), 1 (one-point), 2 (two-point), 3 (three-point)
      vanishing_points: list of (x,y), length depends on mode, but we can store up to 3
    This class also handles load/save from a config file.
    管理消失点坐标和当前参考模式，并提供对外访问方法。
    """

    def __init__(self,
                 config_path="config.json"):
        self.config_path = config_path
        self.mode = 0

        # 初始化三套vanishing points的初始坐标
        # 为简化，这里给出默认坐标，可以在加载config后覆盖
        self.default_vp_coords = {
            1: [(200, 200)],
            # 1-point模式的初始坐标
            2: [(200, 200), (400, 200)],
            # 2-point模式
            3: [(200, 200), (400, 200),
                (300, 300)]  # 3-point模式
        }

        self.overlay_manager = None
        self.elements_by_mode = {
            # 存放VanishingPointElement对象列表
            1: [],
            2: [],
            3: []
        }

        # 在 load_config 前先初始化为默认
        self.vp_coords = {
            1: self.default_vp_coords[
                   1][:],
            2: self.default_vp_coords[
                   2][:],
            3: self.default_vp_coords[
                   3][:]
        }

        self.load_config()  # 尝试从配置文件加载

    def set_overlay_manager(self,
                            overlay_manager):
        """
        设置OverlayManager引用，并创建VanishingPointElement对象加入overlay。
        这需要在CanvasWidget或MainWindow中初始化完overlay_manager后调用。
        """
        self.overlay_manager = overlay_manager
        self._create_elements()

    def _create_elements(self):
        """
        根据vp_coords创建VanishingPointElement对象，并添加到overlay_manager中。
        初始全部设为inactive，然后根据当前mode激活对应集合。
        """

        from overlay.vanishing_point_element import \
            VanishingPointElement

        # 创建1-point模式元素
        for i, (x, y) in enumerate(
                self.vp_coords[1]):
            elem = VanishingPointElement(
                x, y, index=i,
                update_callback=self.on_vp_updated)
            elem.set_active(False)
            self.elements_by_mode[
                1].append(elem)
            self.overlay_manager.add_element(
                elem)

        # 创建2-point模式元素
        for i, (x, y) in enumerate(
                self.vp_coords[2]):
            elem = VanishingPointElement(
                x, y, index=i,
                update_callback=self.on_vp_updated)
            elem.set_active(False)
            self.elements_by_mode[
                2].append(elem)
            self.overlay_manager.add_element(
                elem)

        # 创建3-point模式元素
        for i, (x, y) in enumerate(
                self.vp_coords[3]):
            elem = VanishingPointElement(
                x, y, index=i,
                update_callback=self.on_vp_updated)
            elem.set_active(False)
            self.elements_by_mode[
                3].append(elem)
            self.overlay_manager.add_element(
                elem)

        # 根据当前mode激活对应元素
        self._activate_mode_elements()

    def on_vp_updated(self, index, x,
                      y):
        """
        当VanishingPointElement位置更新回调被调用时，
        更新vp_coords中对应的坐标。

        Note: 当拖拽时，实时更新坐标。
        """
        if self.mode in self.elements_by_mode:
            # 更新对应mode集合中的对应点坐标
            vp_list = self.vp_coords[
                self.mode]
            if 0 <= index < len(
                    vp_list):
                vp_list[index] = (x, y)
    def set_mode(self, mode):
        """
        切换模式，激活对应数量的VanishingPointElement，禁用其他。
        """
        self.mode = mode
        self._activate_mode_elements()

    def _activate_mode_elements(self):
        # 全部禁用
        for m in self.elements_by_mode:
            for elem in \
            self.elements_by_mode[m]:
                elem.set_active(False)

        # 根据mode激活对应集合
        if self.mode in self.elements_by_mode and self.mode > 0:
            for elem in \
            self.elements_by_mode[
                self.mode]:
                elem.set_active(True)

    def get_mode(self):
        return self.mode

    def get_vanishing_points(self):
        """
        根据当前模式返回相应的消失点坐标列表，仅返回(x,y)，不返回对象。
        """
        if self.mode == 0:
            return []
        return self.vp_coords[self.mode]

    def load_config(self):
        if os.path.exists(
                self.config_path):
            with open(self.config_path,
                      "r",
                      encoding="utf-8") as f:
                data = json.load(f)
            self.mode = data.get(
                "vanishing_mode", 0)
            # vp_data应为 { "1": [...], "2": [...], "3": [...] }
            loaded_vp_data = data.get(
                "vanishing_points", {})
            for m_str in ["1", "2",
                          "3"]:
                m = int(m_str)
                if m_str in loaded_vp_data:
                    coords = \
                    loaded_vp_data[
                        m_str]
                    # 确保coords长度正确
                    needed_len = len(
                        self.default_vp_coords[
                            m])
                    coords = coords[
                             :needed_len]
                    if len(coords) < needed_len:
                        # 不足则用默认填充
                        coords += \
                        self.default_vp_coords[
                            m][
                        len(coords):]
                    self.vp_coords[
                        m] = coords

    def save_config(self):
        data = {
            "vanishing_mode": self.mode,
            "vanishing_points": {
                "1": self.vp_coords[1],
                "2": self.vp_coords[2],
                "3": self.vp_coords[3]
            }
        }
        with open(self.config_path, "w",
                  encoding="utf-8") as f:
            json.dump(data, f, indent=2,
                      ensure_ascii=False)