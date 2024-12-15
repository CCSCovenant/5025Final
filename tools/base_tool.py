# tools/base_tool.py
import OpenGL.GL as gl

class BaseTool:
    """
    所有工具的抽象基类。定义统一的接口：
      mouse_press(event, canvas)
      mouse_move(event, canvas)
      mouse_release(event, canvas)
      render_tool_icon(self,render):

    """
    def mouse_press(self, event, canvas_widget):
        pass

    def mouse_move(self, event, canvas_widget):
        pass

    def mouse_release(self, event, canvas_widget):
        pass

    def render_tool_icon(self,render,viewport_size):
        pass
