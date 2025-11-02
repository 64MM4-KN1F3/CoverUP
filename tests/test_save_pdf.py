import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from PIL import Image, ImageDraw
from src.model.model import ImageContainer
from src.controller.controller import Controller


class TestSavePDF(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock view
        self.mock_view = Mock()
        self.mock_view.progress_bar = Mock()

        # Create controller with mock view
        self.controller = Controller.__new__(Controller)  # Create without calling __init__
        self.controller._view = self.mock_view
        self.controller._images = []
        self.controller._output_quality = 'high'
        self.controller._current_page = 0  # Add missing attribute

        # Create a test image
        self.test_image = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(self.test_image)
        draw.text((10, 10), "Test", fill='black')

        # Create ImageContainer
        self.image_container = ImageContainer(self.test_image, (100, 100))
        self.controller._images = [self.image_container]

    def test_save_file_full_document(self):
        """Test saving a full document"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Mock QFileDialog.getSaveFileName
            with patch('src.controller.controller.QFileDialog.getSaveFileName', return_value=(temp_path, '')):
                self.controller.save_file(export_current_page=False)

            # Check that file was created and has content
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_file_current_page(self):
        """Test saving current page only"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Mock QFileDialog.getSaveFileName
            with patch('src.controller.controller.QFileDialog.getSaveFileName', return_value=(temp_path, '')):
                self.controller.save_file(export_current_page=True)

            # Check that file was created and has content
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_file_no_images(self):
        """Test saving when no images are loaded"""
        self.controller._images = []

        with patch('src.controller.controller.QFileDialog.getSaveFileName', return_value=('', '')):
            self.controller.save_file(export_current_page=False)

        # Should not crash and should not call progress bar methods
        self.mock_view.progress_bar.setValue.assert_not_called()

    def test_save_file_cancelled(self):
        """Test when user cancels the save dialog"""
        with patch('src.controller.controller.QFileDialog.getSaveFileName', return_value=('', '')):
            self.controller.save_file(export_current_page=False)

        # Should not call progress bar methods
        self.mock_view.progress_bar.setValue.assert_not_called()

    def test_save_file_error_handling(self):
        """Test error handling in save_file method"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Mock QMessageBox to avoid GUI issues in tests
            with patch('src.controller.controller.QFileDialog.getSaveFileName', return_value=(temp_path, '')), \
                 patch('src.controller.controller.FPDF') as mock_fpdf_class, \
                 patch('src.controller.controller.QMessageBox.critical') as mock_critical:
                # Mock FPDF to raise an exception during image addition
                mock_fpdf_instance = Mock()
                mock_fpdf_instance.add_page.side_effect = Exception("Mocked FPDF error")
                mock_fpdf_class.return_value = mock_fpdf_instance

                # This should trigger an error
                self.controller.save_file(export_current_page=False)

                # Should call error dialog
                mock_critical.assert_called()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()