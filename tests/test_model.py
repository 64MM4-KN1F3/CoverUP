import unittest
import os
from PIL import Image, ImageDraw, ImageFont
from src.model.model import ImageContainer

class TestImageContainer(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (400, 200), color = 'white')
        draw = ImageDraw.Draw(self.image)
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        try:
            # Use a specific font and size for better OCR accuracy
            font = ImageFont.truetype(self.font_path, 40)
        except IOError:
            font = ImageFont.load_default() # Fallback to default font

        draw.text((20, 20), "Hello World", fill="black", font=font)
        self.container = ImageContainer(self.image, size=(400, 200))

    def test_search_text(self):
        # Test searching for a word that exists
        search_results = self.container.search_text("Hello")
        self.assertGreater(len(search_results), 0, "Should find the word 'Hello'")

        # Test searching for a word that does not exist
        search_results = self.container.search_text("Goodbye")
        self.assertEqual(len(search_results), 0, "Should not find the word 'Goodbye'")

    @unittest.skipIf(not os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), "DejaVu font not found")
    def test_ocr_search_text(self):
        # Test OCR on a specific region
        draw = ImageDraw.Draw(self.image)
        try:
            font = ImageFont.truetype(self.font_path, 40)
        except IOError:
            font = ImageFont.load_default()

        # Bounding box around "Hello"
        hello_bbox = draw.textbbox((20, 20), "Hello", font=font)
        hello_bbox_padded = (hello_bbox[0] - 5, hello_bbox[1] - 5, hello_bbox[2] + 5, hello_bbox[3] + 5)
        ocr_text = self.container.ocr_search_text(hello_bbox_padded)
        self.assertIn("Hello", ocr_text, "Should find 'Hello' in the specified region")

        # Bounding box around "World"
        world_offset = draw.textlength("Hello ", font=font)
        world_bbox = draw.textbbox((20 + world_offset, 20), "World", font=font)
        world_bbox_padded = (world_bbox[0] - 5, world_bbox[1] - 5, world_bbox[2] + 5, world_bbox[3] + 5)
        ocr_text_world = self.container.ocr_search_text(world_bbox_padded)
        self.assertIn("World", ocr_text_world, "Should find 'World' in the specified region")

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
