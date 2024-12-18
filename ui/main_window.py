# ui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QSpinBox, QVBoxLayout, QWidget
from .canvas_widget import CanvasWidget

# 引入各种工具
from tools.drawing_tool import DrawingTool
from tools.selection_tool import SelectionTool
from tools.view_tool import ViewTool
from logic.selection_manager import SelectionManager

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Drawing App - Tools Refactor")

        # 中心Widget
        self.canvas_widget = CanvasWidget(self)
        self.resize(800, 600)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 初始化 若需要
        self.selection_manager = SelectionManager()

        # 工具栏
        self.toolbar = self.addToolBar("Tools")

        # Drawing Tool
        self.draw_action = QAction("Drawing Tool", self, checkable=True)
        self.draw_action.setChecked(True)  # 默认绘制模式
        self.toolbar.addAction(self.draw_action)
        self.draw_tool = DrawingTool()

        # Selection Tool
        self.select_action = QAction("Selection Tool", self, checkable=True)
        self.toolbar.addAction(self.select_action)
        self.select_tool = SelectionTool(self.selection_manager, radius=50)

        # View Tool
        self.view_action = QAction("View Tool", self, checkable=True)
        self.toolbar.addAction(self.view_action)
        self.view_tool = ViewTool()

        # 圆形选择半径的SpinBox
        self.toolbar.addWidget(QSpinBox())
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 300)
        self.radius_spin.setValue(50)
        self.toolbar.addWidget(self.radius_spin)

        # 信号槽
        self.draw_action.triggered.connect(self.on_tool_changed)
        self.select_action.triggered.connect(self.on_tool_changed)
        self.view_action.triggered.connect(self.on_tool_changed)
        self.radius_spin.valueChanged.connect(self.on_radius_changed)

        # 默认先选中 DrawingTool
        self.canvas_widget.set_tool(self.draw_tool)

    def on_tool_changed(self):
        """互斥逻辑：只允许一个工具处于active状态"""
        sender = self.sender()
        # 先取消全部
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
        """更新选择工具的半径"""
        self.select_tool.set_radius(val)



