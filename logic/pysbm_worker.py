# coding=utf-8
# logic/pysbm_worker.py

import time
from PyQt5.QtCore import QThread, \
    pyqtSignal


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
                 parent=None):
        super().__init__(parent)
        self.strokes = strokes  # 要处理的笔画
        self._is_cancelled = False  # 如果想支持取消，可以加一个标志

    def cancel(self):
        """让外部可以请求取消"""
        self._is_cancelled = True

    def run(self):
        """
        在这里执行耗时过程。例如调用外部建模工具。
        模拟: 对 self.strokes 做循环处理，每处理一个stroke耗时1秒，并发送进度。
        """
        total = len(self.strokes)
        if total == 0:
            self.finished.emit(None)
            return

        # 假设要收集一个结果(如3D模型), 这里只是简化
        results = []

        for i, stroke in enumerate(
                self.strokes):
            if self._is_cancelled:
                # 被取消了，提前结束
                self.finished.emit(None)
                return

            # 在这里执行真正的外部工具操作，如:
            #   subprocess.run(["external_tool", ...])
            #   或者  time-consuming function call
            time.sleep(1)  # 模拟耗时

            # 生成一点假数据
            result_item = f"model_of_stroke_{i}"
            results.append(result_item)

            # 发送进度
            progress_percentage = (
                                              i + 1) * 100.0 / total
            self.progress_changed.emit(
                progress_percentage)

        # 处理完成
        # 把最终的模型或结果返回给主线程
        self.finished.emit(results)
