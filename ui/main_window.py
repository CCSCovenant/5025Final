# coding=utf-8
# ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, \
    QToolBar, QAction, QSpinBox, \
    QVBoxLayout, QWidget, QFileDialog, \
    QMenu, QMenuBar, QHBoxLayout, \
    QButtonGroup, QRadioButton,QProgressBar

from data.file_manager import \
    StrokeFileManager
from logic.Modifier.axis_2dto3d_modifier import \
    Axis2Dto3DModifier
from logic.Modifier.free_hand_line import \
    FreeHandModifier
from logic.Modifier.smoothing_2d_modifier import \
    Smoothing2DModifier
from .AxisIndicatorWidget import \
    AxisIndicatorWidget

#from logic.pysbm_worker import pySBMWorker
from .canvas_widget import CanvasWidget

from tools.drawing_tool import DrawingTool
from tools.selection_tool import SelectionTool
from tools.view_tool import ViewTool
from logic.selection_manager import SelectionManager

import numpy as np
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
        self.resize(1280, 800)

        self.stroke_filemanager = None
        self.canvas_widget = CanvasWidget(self)
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.axis_widget = AxisIndicatorWidget(self.canvas_widget)
        self.canvas_widget.axis = self.axis_widget
        layout.addWidget(self.axis_widget)
        # 添加参考模式选择的RadioButton
        '''
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
        '''
        # Feature Toggles
        self.feature_toggle_manager = FeatureToggleManager()

        # Stroke Preprocessor
        self.stroke_processor = StrokeProcessor(self.feature_toggle_manager)

        m_smooth2d = Smoothing2DModifier()
        m_axis_2d_to_3d = Axis2Dto3DModifier()
        free_hand_line =  FreeHandModifier()

        self.stroke_processor.register_modifier(m_smooth2d)
        self.stroke_processor.register_modifier(m_axis_2d_to_3d)
        self.stroke_processor.register_modifier(free_hand_line)

        self.stroke_processor.pipelineList_2d = [
            "smooth_2d",
            "axis_2d_to_3d",
            "free_hand_line"
        ]
        self.stroke_processor.pipelineList_2d_to_3d =[
            "axis_2d_to_3d",
            "free_hand_line"
        ]




        # Tools
        self.toolbar = self.addToolBar("Tools")

        layout.addWidget(self.toolbar)

        self.draw_action = QAction("Drawing Tool", self, checkable=True)
        self.draw_action.setChecked(True)
        self.toolbar.addAction(self.draw_action)

        # 创建DrawingTool时传入processor
        self.draw_tool = DrawingTool(
            self.canvas_widget.stroke_manager_2d,
            self.canvas_widget.stroke_manager_3d,
            self.stroke_processor,
            self.feature_toggle_manager
        )

        self.select_action = QAction("Selection Tool", self, checkable=True)
        self.toolbar.addAction(self.select_action)
        self.select_tool = SelectionTool(self.canvas_widget.selection_manager, radius=50)
        '''
        self.view_action = QAction("View Tool", self, checkable=True)
        self.toolbar.addAction(self.view_action)
        self.view_tool = ViewTool()
        '''
        '''
        self.adv_sbm_action = QAction(
            "Enable ADV_SBM", self,
            checkable=True)
        self.adv_sbm_action.setChecked(
            False)
        self.adv_sbm_action.triggered.connect(
            self.on_adv_sbm_toggled)
        self.toolbar.addAction(
            self.adv_sbm_action)
        '''
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 300)
        self.radius_spin.setValue(20)
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
        #self.view_action.triggered.connect(self.on_tool_changed)
        self.radius_spin.valueChanged.connect(self.on_radius_changed)
        self.undo_action.triggered.connect(self.canvas_widget.undo_stroke)
        self.redo_action.triggered.connect(self.canvas_widget.redo_stroke)
        self.save_action.triggered.connect(self.on_save_strokes)
        self.load_action.triggered.connect(self.on_load_strokes)

        self.canvas_widget.set_tool(self.draw_tool)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0,
                                   100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(
            False)  # 初始隐藏

        layout.addWidget(
            self.progress_bar)

        # 菜单增加feature toggles选项
        self.toolbar2 = self.addToolBar(
            "drawing")

        layout.addWidget(self.toolbar2)
        self.debounce_action = QAction("Enable Debounce", self, checkable=True)
        self.debounce_action.setChecked(False)
        self.debounce_action.triggered.connect(self.toggle_debounce)

        self.assist_action = QAction("Enable Assist Lines", self, checkable=True)
        self.assist_action.setChecked(True)
        self.assist_action.triggered.connect(self.toggle_assist_lines)
        '''
        self.toolbar2.addAction(
            self.debounce_action)
        '''
        self.toolbar2.addAction(
            self.assist_action)


        self.worker = None  # 用于保存线程对象


    def on_tool_changed(self):
        sender = self.sender()
        self.draw_action.setChecked(False)
        self.select_action.setChecked(False)
        #self.view_action.setChecked(False)
        sender.setChecked(True)

        if sender == self.draw_action:
            self.canvas_widget.set_tool(self.draw_tool)
        elif sender == self.select_action:
            self.canvas_widget.set_tool(self.select_tool)
        #elif sender == self.view_action:
        #    self.canvas_widget.set_tool(self.view_tool)

    def on_radius_changed(self, val):
        self.select_tool.set_radius(val)

    def on_save_strokes(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Strokes", "", "JSON Files (*.json)")
        if filepath:
            self.canvas_widget.stroke_manager_2d.undo_stack.clear() # 清空以免未同步
            self.canvas_widget.stroke_manager_3d.undo_stack.clear()
            self.stroke_filemanager.save_strokes(filepath)
            pass

    def on_load_strokes(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Strokes", "", "JSON Files (*.json)")
        if filepath:
            self.stroke_filemanager.load_strokes(filepath)
            self.canvas_widget.update()
            pass

    def toggle_debounce(self, checked):
        self.feature_toggle_manager.set_feature("debounce", checked)

    def toggle_assist_lines(self, checked):
        self.feature_toggle_manager.set_feature("axis_enabled", checked)
        self.feature_toggle_manager.set_feature("free_hand_line", not checked)


    def on_vp_mode_changed(self, mode):
        self.canvas_widget.vanishing_point_manager.set_mode(mode)
        self.canvas_widget.vanishing_point_manager.save_config()
        self.canvas_widget.update()

    '''
    def on_adv_sbm_toggled(self,
                           checked):
        # set feature
        self.feature_toggle_manager.set_feature(
            "adv_sbm", checked)
        if checked:
            # disable selection tool, view tool

            self.draw_action.setChecked(
                True)
            self.select_action.setChecked(
                False)
            self.view_action.setChecked(
                False)

            self.canvas_widget.set_tool(self.draw_tool)

            self.select_action.setEnabled(
                False)
            self.view_action.setEnabled(
                False)

        else:
            # enable them
            self.select_action.setEnabled(
                True)
            self.view_action.setEnabled(
                True)
            # 把 stroke_manager_2d 里的数据全部 -> 3D
            self.on_start_modeling()

        self.canvas_widget.update()

    def batch_convert_2d_to_3d(self):
        """
        在关闭 adv_sbm 时, 调用外部工具(缺失)或者 stroke_processor 的 convert_2d_to_3d,
        把 stroke_manager_2d 里的所有 stroke2d 转成 stroke3d.
        """
        strokes_2d = self.canvas_widget.viewable2d_stroke
        s3ds = []
        # 用 stroke_processor
        for s2d in strokes_2d:
            s3d = self.stroke_processor.process_2dto3d_stroke(
                s2d,
                canvas_width=self.canvas_widget.width(),
                canvas_height=self.canvas_widget.height(),
                projection_matrix=self.canvas_widget.renderer.projection_matrix,
                view_matrix=self.canvas_widget.renderer.view_matrix,
                model_matrix=np.eye(
                    4,
                    dtype=np.float32)
                )
            if s3d:
                self.canvas_widget.stroke_manager_3d.add_stroke(
                    s3d)
    def on_start_modeling(self,):
        if self.worker is not None and self.worker.isRunning():
            return
        self.progress_bar.setVisible(
            True)
        self.progress_bar.setValue(0)
        self.disable_gui()
        self.worker = pySBMWorker(
            strokes = self.canvas_widget.viewable2d_stroke,
            canvas_width = self.canvas_widget.width(),
            canvas_height = self.canvas_widget.height(),
            projection_matrix = self.canvas_widget.renderer.projection_matrix,
            view_matrix = self.canvas_widget.renderer.view_matrix,
            model_matrix=np.eye(
                4,
                dtype=np.float32),
            stroke_processor = self.stroke_processor
        )

        self.worker.progress_changed.connect(
            self.on_progress_changed)
        self.worker.finished.connect(
            self.on_modeling_finished)
        self.worker.start()

    def on_progress_changed(self,
                            value):
        """
        接收工作线程发来的进度值(0~100)，更新进度条
        """
        self.progress_bar.setValue(
            int(value))
    def on_modeling_finished(self,
                             result):
        """
        当工作线程完成后，会带着结果调用这个槽函数
        """
        self.enable_gui()
        self.progress_bar.setVisible(
            False)  # 隐藏进度条

        if result is None:
            print("modeling is canceled or something goes wrong")
        else:
            print("finish modeling")
            for s3d in result:
                self.canvas_widget.stroke_manager_3d.add_stroke(s3d)
                print("current lens"+str(len(self.canvas_widget.stroke_manager_3d.get_all_strokes())))
                self.canvas_widget.viewable2d_stroke = []
                self.canvas_widget.update()
            # 这里可以把 result 存到 stroke_manager_3d 或做其他处理

        # 线程结束后，可以把 worker 置为 None
        self.worker = None

    '''
    def disable_gui(self):
        """
        禁用整个GUI，阻止用户输入（鼠标、键盘等）
        """
        self.setEnabled(False)

    def enable_gui(self):
        """
        恢复GUI可交互
        """
        self.setEnabled(True)
    def closeEvent(self, event):
        # 保存当前设置
        self.canvas_widget.vanishing_point_manager.save_config()
        super().closeEvent(event)