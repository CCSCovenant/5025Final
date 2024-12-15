# tools/base_tool.py

class BaseTool:
    """
    所有工具的抽象基类。定义统一的接口：
      mouse_press(event, canvas)
      mouse_move(event, canvas)
      mouse_release(event, canvas)
    """
    def mouse_press(self, event, canvas_widget):
        pass

    def mouse_move(self, event, canvas_widget):
        pass

    def mouse_release(self, event, canvas_widget):
        pass
