import sys
import pypdfium2 as pdfium
from PIL import Image
from fpdf import FPDF
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QGraphicsRectItem, QMessageBox, QDialog, QVBoxLayout, QLabel, QRadioButton, QButtonGroup, QDialogButtonBox
from PyQt6.QtGui import QPixmap, QImage, QColor, QBrush
from PyQt6.QtCore import QRectF
from src.view.view import MainWindow
from src.model.model import ImageContainer

class Controller:
    def __init__(self):
        self._images = []
        self._current_page = 0
        self._scene = QGraphicsScene()
        self._edit_mode = 'draw'
        self._fill_color = 'black'
        self._output_quality = 'high'
        self._view = MainWindow(self)
        self._view.graphics_view.setScene(self._scene)
        self._search_mode = False
        self._search_scope = 'all'  # 'all' or 'current'
        self._connect_signals()

    def _connect_signals(self):
        self._view.open_button.clicked.connect(self.open_file)
        self._view.save_button.clicked.connect(self.save_file)
        self._view.export_button.clicked.connect(self.export_page)
        self._view.undo_button.clicked.connect(self.undo)
        self._view.edit_mode_button.clicked.connect(self.toggle_edit_mode)
        self._view.delete_all_button.clicked.connect(self.delete_all)
        self._view.color_button.clicked.connect(self.toggle_color)
        self._view.quality_button.clicked.connect(self.toggle_quality)
        self._view.prev_page_button.clicked.connect(self.prev_page)
        self._view.next_page_button.clicked.connect(self.next_page)
        self._view.zoom_in_button.clicked.connect(self.zoom_in)
        self._view.zoom_out_button.clicked.connect(self.zoom_out)
        self._view.about_button.clicked.connect(self.about)
        self._view.page_num_input.returnPressed.connect(self.go_to_page)
        self._view.search_button.clicked.connect(self.search_text)
        self._view.ocr_search_button.clicked.connect(self.ocr_search)
        self._view.redact_search_button.clicked.connect(self.redact_search_results)
        self._view.search_scope_combo.currentTextChanged.connect(self.update_search_scope)

    def ocr_search(self):
        if not self._images:
            return

        image_container = self._images[self._current_page]
        selected_items = self._scene.selectedItems()

        if not selected_items:
            QMessageBox.information(self._view, "OCR Search", "Please select a region to perform OCR on.")
            return

        # Assuming the first selected item is the region of interest
        selection_rect = selected_items[0].rect()

        # Convert the selection rectangle to image coordinates
        factor = image_container.zoom_factor / 100
        bbox = (
            int(selection_rect.x() / factor),
            int(selection_rect.y() / factor),
            int((selection_rect.x() + selection_rect.width()) / factor),
            int((selection_rect.y() + selection_rect.height()) / factor),
        )

        # Perform OCR on the selected region
        ocr_text = image_container.ocr_search_text(bbox)

        # Display the OCR text in a message box
        QMessageBox.information(self._view, "OCR Result", ocr_text)

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self._view,
            "Open file",
            "",
            "All supported (*.pdf *.PDF *.jpg *.JPG *.png *.PNG);;PDF (*.pdf *.PDF);;Images (*.jpg *.JPG *.png *.PNG)",
        )
        if filepath:
            self._view.progress_bar.setValue(0)
            self._images = []
            if filepath.lower().endswith('.pdf'):
                pdf = pdfium.PdfDocument(filepath)
                total_pages = len(pdf)
                for i in range(total_pages):
                    pil_image = pdf[i].render(scale=150/72).to_pil()
                    self._images.append(ImageContainer(pil_image, pdf[i].get_size()))
                    self._view.progress_bar.setValue(int((i + 1) * 100 / total_pages))
            else:
                pil_image = Image.open(filepath)
                width, height = pil_image.size
                width_ppi=int(width/(150/72))
                height_ppi=int(height/(150/72))
                self._images.append(ImageContainer(pil_image, (width_ppi, height_ppi)))
                self._view.progress_bar.setValue(100)

            self._current_page = 0
            self.update_view()
            self._view.progress_bar.setValue(0)


    def update_view(self):
        if not self._images:
            return

        image_container = self._images[self._current_page]
        image_container.scale_image()
        pil_image = image_container.scaled_image

        qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        self._scene.clear()
        self._scene.addPixmap(pixmap)

        for rect_data in image_container.rectangles:
            start_point, end_point, color, _ = rect_data
            factor = image_container.zoom_factor / 100
            scaled_start = (start_point[0] * factor, start_point[1] * factor)
            scaled_end = (end_point[0] * factor, end_point[1] * factor)
            rect_item = QGraphicsRectItem(QRectF(scaled_start[0], scaled_start[1], scaled_end[0] - scaled_start[0], scaled_end[1] - scaled_start[1]))
            rect_item.setBrush(QBrush(QColor(color)))
            self._scene.addItem(rect_item)

        # Highlight search results
        for bbox, text in image_container.search_results:
            factor = image_container.zoom_factor / 100
            scaled_bbox = (bbox[0] * factor, bbox[1] * factor, bbox[2] * factor, bbox[3] * factor)
            highlight_item = QGraphicsRectItem(QRectF(scaled_bbox[0], scaled_bbox[1], scaled_bbox[2] - scaled_bbox[0], scaled_bbox[3] - scaled_bbox[1]))
            highlight_item.setBrush(QBrush(QColor(255, 255, 0, 100)))  # Semi-transparent yellow
            highlight_item.setPen(QColor(255, 255, 0))  # Yellow border
            self._scene.addItem(highlight_item)


        self._view.graphics_view.fitInView(self._scene.itemsBoundingRect())
        self._view.page_num_input.setText(str(self._current_page + 1))
        self._view.total_pages_label.setText(f"/ {len(self._images)}")

    def draw_rectangle(self, start_point, end_point):
        if self._images and self._edit_mode == 'draw':
            image_container = self._images[self._current_page]

            start_scene = self._view.graphics_view.mapToScene(start_point)
            end_scene = self._view.graphics_view.mapToScene(end_point)

            image_container.draw_rectangle((start_scene.x(), start_scene.y()), (end_scene.x(), end_scene.y()), self._fill_color)
            self.update_view()

    def erase_rectangle(self, pos):
        if self._images:
            items = self._view.graphics_view.items(pos)
            for item in items:
                if isinstance(item, QGraphicsRectItem):
                    # This is a bit of a hack, but it works for now. A better solution would be to store the rectangles in a way that they can be easily looked up.
                    rect_to_remove = None
                    for rect in self._images[self._current_page].rectangles:
                        if item.rect().x() == rect[0][0] * (self._images[self._current_page].zoom_factor/100) and item.rect().y() == rect[0][1] * (self._images[self._current_page].zoom_factor/100):
                            rect_to_remove = rect
                            break
                    if rect_to_remove:
                        self._images[self._current_page].rectangles.remove(rect_to_remove)
                    self.update_view()
                    break

    def save_file(self, export_current_page=False):
        if not self._images:
            return

        save_file_path, _ = QFileDialog.getSaveFileName(
            self._view, "Save PDF file", "", "PDF (*.pdf)"
        )

        if save_file_path:
            try:
                self._view.progress_bar.setValue(0)
                out_pdf = FPDF(unit="pt")
                out_pdf.set_creator('CoverUp PDF')
                # Note: fpdf2 doesn't have set_creation_date method, metadata is set differently

                import tempfile
                import os

                if export_current_page:
                    image_container = self._images[self._current_page]
                    out_pdf.add_page()
                    include_image = image_container.finalized_image() if self._output_quality == 'high' else image_container.finalized_image('JPEG', image_quality=75, scale=0.90)
                    # Save PIL image to temp file for fpdf2
                    if isinstance(include_image, Image.Image):
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                            include_image.save(tmp_file, format='PNG')
                            temp_path = tmp_file.name
                        try:
                            out_pdf.image(temp_path, x=0, y=0, w=out_pdf.w)
                        finally:
                            os.unlink(temp_path)
                    else:
                        out_pdf.image(include_image, x=0, y=0, w=out_pdf.w)
                    self._view.progress_bar.setValue(100)
                else:
                    total_pages = len(self._images)
                    for i, item in enumerate(self._images):
                        out_pdf.add_page()
                        include_image = item.finalized_image() if self._output_quality == 'high' else item.finalized_image('JPEG', image_quality=50, scale=0.80)
                        # Save PIL image to temp file for fpdf2
                        if isinstance(include_image, Image.Image):
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                                include_image.save(tmp_file, format='PNG')
                                temp_path = tmp_file.name
                            try:
                                out_pdf.image(temp_path, x=0, y=0, w=out_pdf.w)
                            finally:
                                os.unlink(temp_path)
                        else:
                            out_pdf.image(include_image, x=0, y=0, w=out_pdf.w)
                        self._view.progress_bar.setValue(int((i + 1) * 100 / total_pages))

                out_pdf.output(save_file_path)
                self._view.progress_bar.setValue(0)
            except Exception as e:
                QMessageBox.critical(self._view, "Error", f"Failed to save PDF: {e}")
                self._view.progress_bar.setValue(0)


    def export_page(self):
        self.save_file(export_current_page=True)


    def undo(self):
        if self._images:
            self._images[self._current_page].undo()
            self.update_view()


    def toggle_edit_mode(self):
        self._edit_mode = 'erase' if self._edit_mode == 'draw' else 'draw'


    def delete_all(self):
        if self._images:
            reply = QMessageBox.question(self._view, 'Delete All', 'Do you really want to delete all bars on all pages? This operation cannot be undone.', QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Ok:
                for image_container in self._images:
                    image_container.rectangles = []
                self.update_view()


    def toggle_color(self):
        self._fill_color = 'white' if self._fill_color == 'black' else 'black'


    def toggle_quality(self):
        self._output_quality = 'low' if self._output_quality == 'high' else 'high'

    def prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.update_view()


    def next_page(self):
        if self._current_page < len(self._images) - 1:
            self._current_page += 1
            self.update_view()


    def zoom_in(self):
        if self._images:
            self._images[self._current_page].increase_zoom()
            self.update_view()

    def zoom_out(self):
        if self._images:
            self._images[self._current_page].decrease_zoom()
            self.update_view()

    def about(self):
        about_text = "CoverUP PDF\n\nFree software licensed under the terms of the GPL V3.0"
        QMessageBox.about(self._view, "About CoverUP PDF", about_text)


    def go_to_page(self):
        try:
            page_num = int(self._view.page_num_input.text())
            if 1 <= page_num <= len(self._images):
                self._current_page = page_num - 1
                self.update_view()
        except ValueError:
            pass

    def search_text(self):
        if not self._images:
            return

        search_term = self._view.search_input.text()
        self._search_scope = self._view.search_scope_combo.currentText().lower().replace(' ', '')

        total_matches = 0
        if self._search_scope == 'currentpage':
            matches = self._images[self._current_page].search_text(search_term)
            total_matches = len(matches) if matches else 0
            scope_text = "current page"
        else:  # 'allpages'
            for image_container in self._images:
                matches = image_container.search_text(search_term)
                if matches:
                    total_matches += len(matches)
            scope_text = "all pages"

        # Update search results label
        if total_matches > 0:
            self._view.search_results_label.setText(f"Found {total_matches} match(es) on {scope_text}")
        else:
            self._view.search_results_label.setText(f"No matches found on {scope_text}")

        self.update_view()

    def update_search_scope(self):
        """Update search scope when combo box changes"""
        self._search_scope = self._view.search_scope_combo.currentText().lower().replace(' ', '')

    def redact_search_results(self):
        if not self._images:
            return

        total_redacted = 0
        for image_container in self._images:
            for bbox, text in image_container.search_results:
                # Convert bbox (x1,y1,x2,y2) to start and end points
                start_point = (bbox[0], bbox[1])
                end_point = (bbox[2], bbox[3])
                image_container.draw_rectangle(start_point, end_point, self._fill_color)
                total_redacted += 1
            image_container.clear_search_results()

        self._view.search_results_label.setText(f"Redacted {total_redacted} text region(s)")
        self.update_view()


# SearchOptionsDialog class is no longer needed since we use a combo box instead

def main():
    app = QApplication(sys.argv)
    controller = Controller()
    controller._view.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
