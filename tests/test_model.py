import unittest
from PIL import Image
from src.model.model import ImageContainer

class TestImageContainer(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (100, 100))
        self.container = ImageContainer(self.image, size=(100, 100))

    def test_increase_zoom(self):
        initial_zoom = self.container.zoom_factor
        self.container.increase_zoom()
        self.assertEqual(self.container.zoom_factor, initial_zoom + 20)

    def test_decrease_zoom(self):
        self.container.zoom_factor = 100
        initial_zoom = self.container.zoom_factor
        self.container.decrease_zoom()
        self.assertEqual(self.container.zoom_factor, initial_zoom - 20)

    def test_undo(self):
        self.container.draw_rectangle((0, 0), (10, 10))
        self.assertEqual(len(self.container.rectangles), 1)
        self.container.undo()
        self.assertEqual(len(self.container.rectangles), 0)

if __name__ == '__main__':
    unittest.main()
