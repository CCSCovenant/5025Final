# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QSpinBox, QVBoxLayout, QWidget, QFileDialog
from .canvas_widget import CanvasWidget

from tools.drawing_tool import DrawingTool
from tools.selection_tool import SelectionTool
from tools.view_tool import ViewTool
from logic.selection_manager import SelectionManager

# 新增 import
from data.file_manager import StrokeFileManager

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Drawing App - Tools Refactor")

        self.canvas_widget = CanvasWidget(self)
        self.resize(800, 600)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # toolbar
        self.toolbar = self.addToolBar("Tools")

        # Drawing Tool
        self.draw_action = QAction("Drawing Tool", self, checkable=True)
        self.draw_action.setChecked(True)
        self.toolbar.addAction(self.draw_action)
        self.draw_tool = DrawingTool(
            self.canvas_widget.stroke_manager_2d,
            self.canvas_widget.stroke_manager_3d
        )

        # Selection Tool
        self.select_action = QAction("Selection Tool", self, checkable=True)
        self.toolbar.addAction(self.select_action)
        self.select_tool = SelectionTool(
            self.canvas_widget.selection_manager, radius=50
        )

        # View Tool
        self.view_action = QAction("View Tool", self, checkable=True)
        self.toolbar.addAction(self.view_action)
        self.view_tool = ViewTool()

        # 圆形选择半径 spin
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 300)
        self.radius_spin.setValue(50)
        self.toolbar.addWidget(self.radius_spin)

        # 加入 undo/redo
        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)

        # **新增** 保存/加载 按钮
        self.save_action = QAction("Save", self)
        self.load_action = QAction("Load", self)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.load_action)

        # 信号槽
        self.draw_action.triggered.connect(self.on_tool_changed)
        self.select_action.triggered.connect(self.on_tool_changed)
        self.view_action.triggered.connect(self.on_tool_changed)
        self.radius_spin.valueChanged.connect(self.on_radius_changed)
        self.undo_action.triggered.connect(self.canvas_widget.undo_stroke)
        self.redo_action.triggered.connect(self.canvas_widget.redo_stroke)
        self.save_action.triggered.connect(self.on_save_strokes)
        self.load_action.triggered.connect(self.on_load_strokes)

        # 默认先选中 DrawingTool
        self.canvas_widget.set_tool(self.draw_tool)

        # 初始化 FileManager
        self.file_manager = StrokeFileManager(
            self.canvas_widget.stroke_manager_2d,
            self.canvas_widget.stroke_manager_3d
        )

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
            self.file_manager.save_strokes(filepath, cam_rot, cam_dist)

    def on_load_strokes(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Strokes", "", "JSON Files (*.json)")
        if filepath:
            camera_rot, camera_dist = self.file_manager.load_strokes(filepath)
            # 恢复到canvas
            if camera_rot is not None:
                self.canvas_widget.camera_rot = list(camera_rot)
            if camera_dist is not None:
                self.canvas_widget.camera_distance = camera_dist
            self.canvas_widget.update()
