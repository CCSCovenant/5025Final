from PyQt5.QtWidgets import QMainWindow, \
    QMenuBar, QMenu, QAction, \
    QVBoxLayout, QWidget
from .canvas_widget import CanvasWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            "3D Drawing App")

        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu(
            "File")
        edit_menu = menubar.addMenu(
            "Edit")
        view_menu = menubar.addMenu(
            "View")

        # 可以添加各种动作
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

        # 中心部件：包含自定义Canvas/OpenGL部件
        self.canvas_widget = CanvasWidget(
            self)
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(
            self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(
            central_widget)

        # 在这里绑定一些信号和槽，如撤销、重做、打开、保存等
        undo_action.triggered.connect(
            self.canvas_widget.undo_stroke)
        redo_action.triggered.connect(
            self.canvas_widget.redo_stroke)
        open_action.triggered.connect(
            self.on_open)
        save_action.triggered.connect(
            self.on_save)

    def on_open(self):
        # 打开文件逻辑
        pass

    def on_save(self):
        # 保存文件逻辑
        pass
