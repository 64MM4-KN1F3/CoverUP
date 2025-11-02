import sys
import pypdfium2 as pdfium
from PIL import Image
from fpdf import FPDF
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QGraphicsRectItem, QMessageBox
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

        qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.format.upper())
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
                out_pdf.set_creation_date(datetime.today())

                if export_current_page:
                    image_container = self._images[self._current_page]
                    out_pdf.add_page(format=[image_container.width_in_pt, image_container.height_in_pt])
                    include_image = image_container.finalized_image() if self._output_quality == 'high' else image_container.finalized_image('JPEG', image_quality=75, scale=0.90)
                    out_pdf.image(include_image, x=0, y=0, w=out_pdf.w)
                    self._view.progress_bar.setValue(100)
                else:
                    total_pages = len(self._images)
                    for i, item in enumerate(self._images):
                        out_pdf.add_page(format=[item.width_in_pt, item.height_in_pt])
                        include_image = item.finalized_image() if self._output_quality == 'high' else item.finalized_image('JPEG', image_quality=50, scale=0.80)
                        out_pdf.image(include_image, x=0, y=0, w=out_pdf.w)
                        self._view.progress_bar.setValue(int((i + 1) * 100 / total_pages))

                out_pdf.output(save_file_path)
                self._view.progress_bar.setValue(0)
            except Exception as e:
                QMessageBox.critical(self._view, "Error", f"An error occurred: {e}")
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = Controller()
    controller._view.show()
    sys.exit(app.exec())
