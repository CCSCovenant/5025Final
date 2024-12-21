# coding=utf-8
# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, \
    QToolBar, QAction, QSpinBox, \
    QVBoxLayout, QWidget, QFileDialog, \
    QMenu, QMenuBar, QHBoxLayout, \
    QButtonGroup, QRadioButton

from logic.Modifier.axis_2dto3d_modifier import \
    Axis2Dto3DModifier
from logic.Modifier.smoothing_2d_modifier import \
    Smoothing2DModifier
from .canvas_widget import CanvasWidget

from tools.drawing_tool import DrawingTool
from tools.selection_tool import SelectionTool
from tools.view_tool import ViewTool
from logic.selection_manager import SelectionManager

# 新增import
from logic.feature_toggle_manager import FeatureToggleManager
from logic.stroke_processor import StrokeProcessor

class MainWindow(QMainWindow):
    """
    Main Window of the application.
    Now includes feature toggles for debounce and assist lines.
    在主窗口中增加特性开关，对DrawingTool传入StrokePreprocessor以实现可选预处理。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Drawing App with Overlay & Preprocessing")
        self.resize(800, 600)

        self.canvas_widget = CanvasWidget(self)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 添加参考模式选择的RadioButton
        radio_layout = QHBoxLayout()
        self.radio_group = QButtonGroup(
            self)
        self.none_radio = QRadioButton(
            "No reference")
        self.one_radio = QRadioButton(
            "1-point")
        self.two_radio = QRadioButton(
            "2-point")
        self.three_radio = QRadioButton(
            "3-point")

        self.radio_group.addButton(
            self.none_radio, 0)
        self.radio_group.addButton(
            self.one_radio, 1)
        self.radio_group.addButton(
            self.two_radio, 2)
        self.radio_group.addButton(
            self.three_radio, 3)

        radio_layout.addWidget(
            self.none_radio)
        radio_layout.addWidget(
            self.one_radio)
        radio_layout.addWidget(
            self.two_radio)
        radio_layout.addWidget(
            self.three_radio)
        layout.addLayout(radio_layout)

        self.radio_group.buttonClicked[
            int].connect(
            self.on_vp_mode_changed)

        central_widget.setLayout(layout)
        self.setCentralWidget(
            central_widget)

        # 根据当前manager模式设置默认选中按钮
        mode = self.canvas_widget.vanishing_point_manager.get_mode()
        btn = self.radio_group.button(
            mode)
        if btn:
            btn.setChecked(True)

        # Feature Toggles
        self.feature_toggle_manager = FeatureToggleManager()

        # Stroke Preprocessor
        self.stroke_processor = StrokeProcessor(self.feature_toggle_manager)

        m_smooth2d = Smoothing2DModifier()
        m_axis_2d_to_3d = Axis2Dto3DModifier()

        self.stroke_processor.register_modifier(m_smooth2d)
        self.stroke_processor.register_modifier(m_axis_2d_to_3d)

        self.stroke_processor.pipelineList_2d = [
            "smooth_2d"
        ]
        self.stroke_processor.pipelineList_2d_to_3d =[
            "axis_2d_to_3d"
        ]




        # Tools
        self.toolbar = self.addToolBar("Tools")
        self.draw_action = QAction("Drawing Tool", self, checkable=True)
        self.draw_action.setChecked(True)
        self.toolbar.addAction(self.draw_action)

        # 创建DrawingTool时传入processor
        self.draw_tool = DrawingTool(
            self.canvas_widget.stroke_manager_2d,
            self.canvas_widget.stroke_manager_3d,
            self.stroke_processor
        )

        self.select_action = QAction("Selection Tool", self, checkable=True)
        self.toolbar.addAction(self.select_action)
        self.select_tool = SelectionTool(self.canvas_widget.selection_manager, radius=50)

        self.view_action = QAction("View Tool", self, checkable=True)
        self.toolbar.addAction(self.view_action)
        self.view_tool = ViewTool()

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 300)
        self.radius_spin.setValue(50)
        self.toolbar.addWidget(self.radius_spin)

        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)

        self.save_action = QAction("Save", self)
        self.load_action = QAction("Load", self)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.load_action)

        self.draw_action.triggered.connect(self.on_tool_changed)
        self.select_action.triggered.connect(self.on_tool_changed)
        self.view_action.triggered.connect(self.on_tool_changed)
        self.radius_spin.valueChanged.connect(self.on_radius_changed)
        self.undo_action.triggered.connect(self.canvas_widget.undo_stroke)
        self.redo_action.triggered.connect(self.canvas_widget.redo_stroke)
        self.save_action.triggered.connect(self.on_save_strokes)
        self.load_action.triggered.connect(self.on_load_strokes)

        self.canvas_widget.set_tool(self.draw_tool)

        # 菜单增加feature toggles选项
        menu_bar = self.menuBar() if self.menuBar() else QMenuBar(self)
        self.setMenuBar(menu_bar)
        feature_menu = menu_bar.addMenu("Features")

        self.debounce_action = QAction("Enable Debounce", self, checkable=True)
        self.debounce_action.setChecked(False)
        self.debounce_action.triggered.connect(self.toggle_debounce)

        self.assist_action = QAction("Enable Assist Lines", self, checkable=True)
        self.assist_action.setChecked(False)
        self.assist_action.triggered.connect(self.toggle_assist_lines)

        feature_menu.addAction(self.debounce_action)
        feature_menu.addAction(self.assist_action)

    def on_tool_changed(self):
        sender = self.sender()
        self.draw_action.setChecked(False)
        self.select_action.setChecked(False)
        self.view_action.setChecked(False)
        sender.setChecked(True)

        if sender == self.draw_action:
            self.canvas_widget.set_tool(self.draw_tool)
        elif sender == self.select_action:
            self.canvas_widget.set_tool(self.select_tool)
        elif sender == self.view_action:
            self.canvas_widget.set_tool(self.view_tool)

    def on_radius_changed(self, val):
        self.select_tool.set_radius(val)

    def on_save_strokes(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Strokes", "", "JSON Files (*.json)")
        if filepath:
            cam_rot = self.canvas_widget.camera_rot
            cam_dist = self.canvas_widget.camera_distance
            # 假设file_manager已在原代码中
            self.canvas_widget.stroke_manager_2d.undo_stack.clear() # 清空以免未同步
            self.canvas_widget.stroke_manager_3d.undo_stack.clear()
            # 使用原先的file_manager逻辑
            # 请根据原工程中file_manager的实现进行调用，如：
            # self.file_manager.save_strokes(filepath, cam_rot, cam_dist)
            pass

    def on_load_strokes(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Strokes", "", "JSON Files (*.json)")
        if filepath:
            # 根据原先file_manager的实现加载并重设camera和strokes
            # cam_rot, cam_dist = self.file_manager.load_strokes(filepath)
            # if cam_rot is not None:
            #    self.canvas_widget.camera_rot = list(cam_rot)
            # if cam_dist is not None:
            #    self.canvas_widget.camera_distance = cam_dist
            # self.canvas_widget.update()
            pass

    def toggle_debounce(self, checked):
        self.feature_toggle_manager.set_feature("debounce", checked)

    def toggle_assist_lines(self, checked):
        self.feature_toggle_manager.set_feature("assist_lines", checked)
    def on_vp_mode_changed(self, mode):
        self.canvas_widget.vanishing_point_manager.set_mode(mode)
        self.canvas_widget.vanishing_point_manager.save_config()
        self.canvas_widget.update()

    def closeEvent(self, event):
        # 保存当前设置
        self.canvas_widget.vanishing_point_manager.save_config()
        super().closeEvent(event)