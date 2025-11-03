from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, controller):
        super().__init__(scene)
        self._controller = controller
        self._start_point = None
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._controller._edit_mode == 'draw':
                self._start_point = event.pos()
            elif self._controller._edit_mode == 'erase':
                self._controller.erase_rectangle(event.pos())


    def mouseMoveEvent(self, event):
        if self._start_point:
            # Draw temporary rectangle
            pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._start_point:
            end_point = event.pos()
            self._controller.draw_rectangle(self._start_point, end_point)
            self._start_point = None
