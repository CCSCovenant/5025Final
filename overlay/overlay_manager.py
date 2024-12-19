# coding=utf-8
# overlay/overlay_manager.py
# Overlay管理器：维护多个Overlay元素并处理其事件和渲染。

class OverlayManager:
    """
    Manages all overlay elements on top of the canvas.
    Provides:
      - event handling (hit test, drag, etc.)
      - rendering all overlay elements on top of canvas
      - query methods (e.g. get vanishing points)

    管理所有Overlay元素，包括事件分发和渲染。
    """

    def __init__(self):
        self.elements = []

    def add_element(self, elem):
        self.elements.append(elem)

    def render(self, viewport_size):
        """
        Render all overlay elements.
        在画布上层绘制所有Overlay元素。
        """
        for e in self.elements:
            e.render(viewport_size)

    def mouse_press_event(self, event):
        """
        Handle mouse press: test from top to bottom, if hit, select that element.
        鼠标按下事件，检测元素命中。

        :return: bool - True if event is consumed by overlay
        """
        mx, my = event.x(), event.y()
        # 从上至下迭代，找到第一个hit的元素
        for e in reversed(
                self.elements):
            if e.hit_test(mx, my):
                e.on_mouse_press(mx, my)
                return True
        return False

    def mouse_move_event(self, event,
                         last_pos):
        """
        鼠标移动事件，如果有正在拖拽的元素则移动它。
        同时更新hover状态。

        :param event: QMouseEvent
        :param last_pos: QPoint 上次鼠标位置
        :return: bool - True if event consumed
        """
        mx, my = event.x(), event.y()
        dx = mx - last_pos.x()
        dy = my - last_pos.y()

        consumed = False
        dragging_elem = None
        # 先查看有没有在拖拽的元素
        for e in self.elements:
            if getattr(e, 'dragging',
                       False):
                dragging_elem = e
                break
        if dragging_elem:
            dragging_elem.on_mouse_move(
                mx, my, dx, dy)
            consumed = True
        else:
            # 更新hover状态
            hit_any = False
            for e in self.elements:
                hovered = e.hit_test(mx,
                                     my)
                e.is_hovered = hovered
                if hovered:
                    hit_any = True
            if hit_any:
                consumed = True

        return consumed

    def mouse_release_event(self,
                            event):
        mx, my = event.x(), event.y()
        for e in self.elements:
            if getattr(e, 'dragging',
                       False):
                e.on_mouse_release(mx,
                                   my)
        return False

    def get_vanishing_points(self):
        # 返回所有VanishingPointElement
        return [e for e in self.elements
                if
                hasattr(e, "position")]
