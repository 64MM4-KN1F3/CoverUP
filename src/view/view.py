import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QProgressBar, QComboBox
from PyQt6.QtGui import QIcon
from src.view.custom_graphics_view import CustomGraphicsView

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle('CoverUP PDF')
        self.setGeometry(100, 100, 1300, 900)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        main_layout.addLayout(toolbar_layout)

        # Add buttons to toolbar
        self.open_button = QPushButton()
        self.open_button.setIcon(QIcon('src/view/icons/folder_open.svg'))
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon('src/view/icons/save.svg'))
        self.export_button = QPushButton()
        self.export_button.setIcon(QIcon('src/view/icons/article.svg'))
        self.undo_button = QPushButton()
        self.undo_button.setIcon(QIcon('src/view/icons/undo.svg'))
        self.edit_mode_button = QPushButton()
        self.edit_mode_button.setIcon(QIcon('src/view/icons/edit.svg'))
        self.delete_all_button = QPushButton()
        self.delete_all_button.setIcon(QIcon('src/view/icons/delete.svg'))
        self.color_button = QPushButton()
        self.color_button.setIcon(QIcon('src/view/icons/palette.svg'))
        self.quality_button = QPushButton()
        self.quality_button.setIcon(QIcon('src/view/icons/high_quality.svg'))
        self.search_button = QPushButton()
        self.search_button.setIcon(QIcon('src/view/icons/search.svg'))
        self.ocr_search_button = QPushButton()
        self.ocr_search_button.setIcon(QIcon('src/view/icons/visibility.svg'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search text (supports regex)...')
        self.search_input.setFixedWidth(150)
        self.search_scope_combo = QComboBox()
        self.search_scope_combo.addItems(['All pages', 'Current page'])
        self.search_scope_combo.setCurrentText('All pages')
        self.redact_search_button = QPushButton()
        self.redact_search_button.setIcon(QIcon('src/view/icons/edit_off.svg'))
        self.prev_page_button = QPushButton()
        self.prev_page_button.setIcon(QIcon('src/view/icons/arrow_back.svg'))
        self.next_page_button = QPushButton()
        self.next_page_button.setIcon(QIcon('src/view/icons/arrow_forward.svg'))
        self.zoom_in_button = QPushButton()
        self.zoom_in_button.setIcon(QIcon('src/view/icons/zoom_in.svg'))
        self.zoom_out_button = QPushButton()
        self.zoom_out_button.setIcon(QIcon('src/view/icons/zoom_out.svg'))
        self.about_button = QPushButton()
        self.about_button.setIcon(QIcon('src/view/icons/info.svg'))

        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.export_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.undo_button)
        toolbar_layout.addWidget(self.edit_mode_button)
        toolbar_layout.addWidget(self.delete_all_button)
        toolbar_layout.addWidget(self.color_button)
        toolbar_layout.addWidget(self.quality_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.search_scope_combo)
        toolbar_layout.addWidget(self.search_button)
        toolbar_layout.addWidget(self.ocr_search_button)
        toolbar_layout.addWidget(self.redact_search_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.prev_page_button)
        self.page_num_input = QLineEdit('1')
        self.page_num_input.setFixedWidth(40)
        toolbar_layout.addWidget(self.page_num_input)
        self.total_pages_label = QLabel('/ 0')
        toolbar_layout.addWidget(self.total_pages_label)
        toolbar_layout.addWidget(self.next_page_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.zoom_in_button)
        toolbar_layout.addWidget(self.zoom_out_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.about_button)

        # Graphics View
        self.graphics_view = CustomGraphicsView(controller._scene, controller)
        main_layout.addWidget(self.graphics_view)

        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Search Results Label
        self.search_results_label = QLabel("")
        main_layout.addWidget(self.search_results_label)
