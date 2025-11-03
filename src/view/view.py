import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QProgressBar, QComboBox
from PyQt6.QtGui import QIcon
from src.view.custom_graphics_view import CustomGraphicsView

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_theme = 'dark'  # 'dark' or 'light'
        self.setWindowTitle('CoverUP PDF')
        self.setGeometry(100, 100, 1300, 900)

        # Define themes
        self.themes = {
            'dark': """
                /* Main window background */
                QMainWindow {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                }

                /* Central widget */
                QWidget {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                }

                /* Buttons */
                QPushButton {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    icon-size: 20px;
                }

                QPushButton:hover {
                    background-color: #45475a;
                    border: 1px solid #585b70;
                }

                QPushButton:pressed {
                    background-color: #585b70;
                }

                /* Line edits and combo boxes */
                QLineEdit, QComboBox {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }

                QLineEdit:focus, QComboBox:focus {
                    border: 1px solid #89b4fa;
                }

                QComboBox::drop-down {
                    border: none;
                    background-color: #45475a;
                }

                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #cdd6f4;
                    margin-right: 8px;
                }

                /* Labels */
                QLabel {
                    color: #cdd6f4;
                    font-size: 12px;
                }

                /* Progress bar */
                QProgressBar {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                    text-align: center;
                }

                QProgressBar::chunk {
                    background-color: #89b4fa;
                    border-radius: 2px;
                }

                /* Graphics view */
                QGraphicsView {
                    background-color: #181825;
                    border: 1px solid #45475a;
                    border-radius: 4px;
                }

                /* Scroll bars */
                QScrollBar:vertical {
                    background-color: #313244;
                    width: 12px;
                    border-radius: 6px;
                }

                QScrollBar::handle:vertical {
                    background-color: #585b70;
                    border-radius: 6px;
                    min-height: 20px;
                }

                QScrollBar::handle:vertical:hover {
                    background-color: #6c7086;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                    border: none;
                }

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """,
            'light': """
                /* Main window background */
                QMainWindow {
                    background-color: #eff1f5;
                    color: #4c4f69;
                }

                /* Central widget */
                QWidget {
                    background-color: #eff1f5;
                    color: #4c4f69;
                }

                /* Buttons */
                QPushButton {
                    background-color: #bcc0cc;
                    color: #4c4f69;
                    border: 1px solid #acb0be;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    icon-size: 20px;
                }

                QPushButton:hover {
                    background-color: #acb0be;
                    border: 1px solid #9ca0b0;
                }

                QPushButton:pressed {
                    background-color: #9ca0b0;
                }

                /* Line edits and combo boxes */
                QLineEdit, QComboBox {
                    background-color: #bcc0cc;
                    color: #4c4f69;
                    border: 1px solid #acb0be;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }

                QLineEdit:focus, QComboBox:focus {
                    border: 1px solid #1e66f5;
                }

                QComboBox::drop-down {
                    border: none;
                    background-color: #acb0be;
                }

                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #4c4f69;
                    margin-right: 8px;
                }

                /* Labels */
                QLabel {
                    color: #4c4f69;
                    font-size: 12px;
                }

                /* Progress bar */
                QProgressBar {
                    background-color: #bcc0cc;
                    color: #4c4f69;
                    border: 1px solid #acb0be;
                    border-radius: 4px;
                    text-align: center;
                }

                QProgressBar::chunk {
                    background-color: #1e66f5;
                    border-radius: 2px;
                }

                /* Graphics view */
                QGraphicsView {
                    background-color: #e6e9ef;
                    border: 1px solid #acb0be;
                    border-radius: 4px;
                }

                /* Scroll bars */
                QScrollBar:vertical {
                    background-color: #bcc0cc;
                    width: 12px;
                    border-radius: 6px;
                }

                QScrollBar::handle:vertical {
                    background-color: #9ca0b0;
                    border-radius: 6px;
                    min-height: 20px;
                }

                QScrollBar::handle:vertical:hover {
                    background-color: #8c8fa1;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    background: none;
                    border: none;
                }

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """
        }

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        main_layout.addLayout(toolbar_layout)

        # Add buttons to toolbar
        self.open_button = QPushButton()
        self.open_button.setToolTip('Open PDF')
        self.save_button = QPushButton()
        self.save_button.setToolTip('Save PDF')
        self.export_button = QPushButton()
        self.export_button.setToolTip('Export PDF')
        self.undo_button = QPushButton()
        self.undo_button.setToolTip('Undo')
        self.edit_mode_button = QPushButton()
        self.edit_mode_button.setToolTip('Edit Mode')
        self.delete_all_button = QPushButton()
        self.delete_all_button.setToolTip('Delete All')
        self.color_button = QPushButton()
        self.color_button.setToolTip('Color')
        self.quality_button = QPushButton()
        self.quality_button.setToolTip('Quality')
        self.search_button = QPushButton()
        self.search_button.setToolTip('Search')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍text/regex...')
        self.search_input.setFixedWidth(150)
        self.search_scope_combo = QComboBox()
        self.search_scope_combo.addItems(['All pages', 'Current page'])
        self.search_scope_combo.setCurrentText('All pages')
        self.redact_search_button = QPushButton()
        self.redact_search_button.setToolTip('Redact Search')
        self.prev_page_button = QPushButton()
        self.prev_page_button.setToolTip('Previous Page')
        self.next_page_button = QPushButton()
        self.next_page_button.setToolTip('Next Page')
        self.zoom_in_button = QPushButton()
        self.zoom_in_button.setToolTip('Zoom In')
        self.zoom_out_button = QPushButton()
        self.zoom_out_button.setToolTip('Zoom Out')
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.setToolTip('Toggle Theme')
        self.about_button = QPushButton()
        self.about_button.setToolTip('About')

        # Apply initial theme (after buttons are created)
        self.apply_theme()

        # Connect theme toggle button (only once)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)

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
        toolbar_layout.addWidget(self.theme_toggle_button)
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

    def apply_theme(self):
        """Apply the current theme to the UI"""
        self.setStyleSheet(self.themes[self.current_theme])
        self.update_icons()

    def update_icons(self):
        """Update all button icons based on current theme"""
        icon_suffix = '_light' if self.current_theme == 'dark' else ''

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(script_dir, 'icons')

        # Define icon mappings
        icon_map = {
            'folder_open': self.open_button,
            'save': self.save_button,
            'article': self.export_button,
            'undo': self.undo_button,
            'edit': self.edit_mode_button,
            'delete': self.delete_all_button,
            'palette': self.color_button,
            'high_quality': self.quality_button,
            'search': self.search_button,
            'edit_off': self.redact_search_button,
            'arrow_back': self.prev_page_button,
            'arrow_forward': self.next_page_button,
            'zoom_in': self.zoom_in_button,
            'zoom_out': self.zoom_out_button,
            'info': self.about_button,
        }

        # Special handling for theme toggle button
        theme_icon = 'sun_light' if self.current_theme == 'dark' else 'moon'
        icon_path = os.path.join(icons_dir, f'{theme_icon}.svg')
        self.theme_toggle_button.setIcon(QIcon(icon_path))

        # Set theme toggle button icon and text
        # Icons are set in the icon_map below

        # Apply icons to buttons
        for icon_name, button in icon_map.items():
            icon_path = os.path.join(icons_dir, f'{icon_name}{icon_suffix}.svg')
            button.setIcon(QIcon(icon_path))

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()
