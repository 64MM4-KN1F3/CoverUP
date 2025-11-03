import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import Qt
from src.view.custom_graphics_view import CustomGraphicsView

class TestView(unittest.TestCase):
    def setUp(self):
        self.app = QApplication([])
        self.scene = QGraphicsScene()
        self.controller = Mock()
        self.view = CustomGraphicsView(self.scene, self.controller)

    @patch.object(CustomGraphicsView, 'fitInView')
    def test_resizeEvent_calls_fitInView_with_keepAspectRatio(self, mock_fitInView):
        # Create a mock event
        event = Mock()

        # Call the resizeEvent method
        self.view.resizeEvent(event)

        # Assert that fitInView was called with the correct arguments
        mock_fitInView.assert_called_with(self.view.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

if __name__ == '__main__':
    unittest.main()
