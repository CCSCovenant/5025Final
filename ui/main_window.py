from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QMenu,
    QAction, QVBoxLayout, QWidget,
    QToolBar
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from .canvas_widget import CanvasWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            "3D Drawing App")

        # ========== 菜单栏 ==========
        menubar = self.menuBar()
        file_menu = menubar.addMenu(
            "File")
        edit_menu = menubar.addMenu(
            "Edit")
        view_menu = menubar.addMenu(
            "View")

        # 动作示例
        open_action = QAction("Open",
                              self)
        save_action = QAction("Save",
                              self)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        undo_action = QAction("Undo",
                              self)
        redo_action = QAction("Redo",
                              self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # ========== 工具栏 (QToolBar) ==========
        self.toolbar = self.addToolBar(
            "MainToolBar")

        # 1) 视图模式切换按钮（Checkable）
        self.view_mode_action = QAction(
            "View Mode", self,
            checkable=True)
        self.toolbar.addAction(
            self.view_mode_action)

        # 2) 撤销、重做
        self.undo_action_tb = QAction(
            "Undo", self)
        self.redo_action_tb = QAction(
            "Redo", self)
        self.toolbar.addAction(
            self.undo_action_tb)
        self.toolbar.addAction(
            self.redo_action_tb)

        # ========== 快捷键设置 ==========
        # Ctrl+Z -> Undo
        undo_action.setShortcut(
            QKeySequence("Ctrl+Z"))
        self.undo_action_tb.setShortcut(
            QKeySequence("Ctrl+Z"))
        # Ctrl+Y -> Redo
        redo_action.setShortcut(
            QKeySequence("Ctrl+Y"))
        self.redo_action_tb.setShortcut(
            QKeySequence("Ctrl+Y"))

        # 快捷键切换视图模式 (例：按 "V" 切换)
        self.toggle_view_mode_shortcut = QAction(
            "Toggle View Mode", self)
        self.toggle_view_mode_shortcut.setShortcut(
            QKeySequence("V"))
        self.addAction(
            self.toggle_view_mode_shortcut)

        # ========== 中心绘制区域 ==========
        self.canvas_widget = CanvasWidget(
            self)
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(
            self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(
            central_widget)

        # ========== 信号与槽连接 ==========
        open_action.triggered.connect(
            self.on_open)
        save_action.triggered.connect(
            self.on_save)
        undo_action.triggered.connect(
            self.canvas_widget.undo_stroke)
        redo_action.triggered.connect(
            self.canvas_widget.redo_stroke)
        self.undo_action_tb.triggered.connect(
            self.canvas_widget.undo_stroke)
        self.redo_action_tb.triggered.connect(
            self.canvas_widget.redo_stroke)

        # 视图模式（菜单栏 或 工具栏 的动作）监听
        self.view_mode_action.triggered.connect(
            self.toggle_view_mode)
        self.toggle_view_mode_shortcut.triggered.connect(
            self.toggle_view_mode)

    def toggle_view_mode(self):
        # 根据菜单/工具栏动作的 check 状态，切换canvas的 view_mode
        is_view_mode = self.view_mode_action.isChecked()
        self.canvas_widget.set_view_mode(
            is_view_mode)

    def on_open(self):
        # 打开文件逻辑
        pass

    def on_save(self):
        # 保存文件逻辑
        pass
