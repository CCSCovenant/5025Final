# coding=utf-8
# logic/pysbm_worker.py

import time

import pysbm
from PyQt5.QtCore import QThread, \
    pyqtSignal
import numpy as np
import pickle

from data.sketch_builder import \
    build_sketch, extract_fixed_strokes
from data.stroke_3d import Stroke3D


class pySBMWorker(QThread):
    """
    SlowModelingWorker 用于在后台执行一个耗时的外部建模工具过程。
    在模拟中我们只是循环+sleep，实际中可替换为真正的外部命令行或SDK调用。

    信号:
      progress_changed(float) -> 0~100 的进度百分比
      finished(result)        -> 当所有建模完成时，发出带结果的信号
    """

    progress_changed = pyqtSignal(
        float)  # 进度变化信号
    finished = pyqtSignal(
        object)  # 任务完成信号，附带结果

    def __init__(self, strokes,
                 canvas_width,
                 canvas_height,
                 projection_matrix,
                 view_matrix,
                 model_matrix,
                 stroke_processor,
                 parent=None):
        super().__init__(parent)
        self.strokes = strokes  # 要处理的笔画
        self._is_cancelled = False  # 如果想支持取消，可以加一个标志
        self.canvas_width = canvas_width
        self.canvas_height =canvas_height
        self.projection_matrix = projection_matrix
        self.view_matrix = view_matrix
        self.model_matrix =  model_matrix
        self.stroke_processor = stroke_processor

    def cancel(self):
        """让外部可以请求取消"""
        self._is_cancelled = True

    def run(self):


        results = []
        sketch = build_sketch(self.strokes,self.canvas_width,self.canvas_height)
        pysbm.sketching.sketch_clean(
            sketch)
        cam = pysbm.lifting.init_camera(
            sketch)
        pysbm.sketching.preprocessing(
            sketch, cam)
        symm_candidates, corr_scores = pysbm.lifting.compute_symmetry_candidates(
            sketch, cam)
        self.progress_changed.emit(
            0.4)
        batches = pysbm.lifting.compute_batches(
            sketch, symm_candidates)
        self.progress_changed.emit(
            0.5)
        batches_result, batches_result_1 = pysbm.lifting.optimize_symmetry_sketch_pipeline(
            sketch, cam,
            symm_candidates, batches,
            corr_scores)

        file = "../tmp2/batches_result.pkl"
        try:
            with open(file,
                      'wb') as file:
                pickle.dump(batches_result_1, file)
                print("saved")
        except Exception as e:
            pass

        # 处理完成
        # 把最终的模型或结果返回给主线程
        self.finished.emit(results)
