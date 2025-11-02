import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QProgressBar, QComboBox
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
        self.open_button = QPushButton('Open')
        self.save_button = QPushButton('Save')
        self.export_button = QPushButton('Export Page')
        self.undo_button = QPushButton('Undo')
        self.edit_mode_button = QPushButton('Draw/Erase')
        self.delete_all_button = QPushButton('Delete All')
        self.color_button = QPushButton('Color')
        self.quality_button = QPushButton('Quality')
        self.search_button = QPushButton('Search')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search text (supports regex)...')
        self.search_input.setFixedWidth(150)
        self.search_scope_combo = QComboBox()
        self.search_scope_combo.addItems(['All pages', 'Current page'])
        self.search_scope_combo.setCurrentText('All pages')
        self.redact_search_button = QPushButton('Redact Found')
        self.prev_page_button = QPushButton('<')
        self.next_page_button = QPushButton('>')
        self.zoom_in_button = QPushButton('+')
        self.zoom_out_button = QPushButton('-')
        self.about_button = QPushButton('About')

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
