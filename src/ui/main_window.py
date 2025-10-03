"""
Main window implementation with plugin-based architecture.
"""
import sys
import os
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from qt_material import apply_stylesheet

from src.core.analysis_service import AnalysisService
from src.core.plugin_registry import plugin_registry
from src.ui.analysis_window import AnalysisWindow
from src.utils.resources import resource_path, load_pixmap_safely
from src.utils.config import app_config


class MainWindow(QMainWindow):
    """Main application window with method selection"""
    
    def __init__(self):
        super().__init__()
        self.analysis_service = AnalysisService()
        self.analysis_window: Optional[AnalysisWindow] = None
        self._setup_ui()
        self._register_plugins()
        self._load_methods()
    
    def _setup_ui(self):
        """Setup the user interface"""
        config = app_config.ui
        
        self.setWindowTitle(config.window_title)
        self.resize(*config.window_size)
        
        # Set window icon safely
        icon_path = resource_path(app_config.paths.demo_logo)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        
        # Logo layout
        self._create_logo_layout(main_v)
        
        # Content layout
        self._create_content_layout(main_v)
    
    def _create_logo_layout(self, main_layout: QVBoxLayout):
        """Create the logo layout section"""
        logo_h_layout = QHBoxLayout()
        
        # BAU logo
        bau_logo_label = QLabel()
        bau_logo_pixmap = load_pixmap_safely(
            app_config.paths.bau_logo, 
            app_config.ui.logo_size
        )
        bau_logo_label.setFixedSize(*app_config.ui.logo_size)
        bau_logo_label.setPixmap(bau_logo_pixmap.scaled(
            *app_config.ui.logo_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        bau_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo_h_layout.addWidget(bau_logo_label)
        
        # Title
        title = QLabel(app_config.ui.window_title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("TitleLabel")
        logo_h_layout.addWidget(title, stretch=1)
        
        # ICT logo
        ict_logo_label = QLabel()
        ict_logo_pixmap = load_pixmap_safely(
            app_config.paths.ict_logo, 
            app_config.ui.logo_size
        )
        ict_logo_label.setFixedSize(*app_config.ui.logo_size)
        ict_logo_label.setPixmap(ict_logo_pixmap.scaled(
            *app_config.ui.logo_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        ict_logo_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        logo_h_layout.addWidget(ict_logo_label)
        
        # Set properties for styling
        bau_logo_label.setProperty("logo", True)
        ict_logo_label.setProperty("logo", True)
        
        main_layout.addLayout(logo_h_layout)
    
    def _create_content_layout(self, main_layout: QVBoxLayout):
        """Create the main content layout"""
        content = QVBoxLayout()
        
        # Method selection frame
        select_frame = self._create_method_selection_frame()
        content.addWidget(select_frame)

        # Main panel with tree placeholder
        main_panel = self._create_main_panel()
        content.addWidget(main_panel, 1)
        
        main_layout.addLayout(content)
    
    def _create_method_selection_frame(self) -> QFrame:
        """Create the method selection frame"""
        select = QFrame()
        select.setFrameShape(QFrame.Shape.StyledPanel)
        select.setStyleSheet("""QFrame{
            border:None;
            background-color:transparent;
            }""")
        select_v = QHBoxLayout(select)
        
        # Method selection label
        select_lbl = QLabel("Select Method")
        select_lbl.setStyleSheet(
            "border:None;"
            "margin-left:10px;"
            "width:100px;"
            "background-color:transparent;"
        )
        select_v.addWidget(select_lbl)
        
        # Method combo box
        self.method_combo = QComboBox()
        self.method_combo.setCurrentIndex(0)
        self.method_combo.setStyleSheet("background-color:white;")
        select_v.addWidget(self.method_combo)
        
        # Start button
        method_btn = QPushButton("Start")
        method_btn.clicked.connect(self._start_analysis)
        select_v.addWidget(method_btn)
        
        select_v.addStretch(0)
        
        return select
    
    def _create_main_panel(self) -> QFrame:
        """Create the main display panel"""
        main_panel = QFrame()
        main_panel.setFrameShape(QFrame.Shape.StyledPanel)
        mp_l = QVBoxLayout(main_panel)

        view = QLabel("Phylogenetic tree")
        view_pix = load_pixmap_safely(
            app_config.paths.tree_placeholder, 
            app_config.ui.tree_display_size
        )
        view.setPixmap(view_pix.scaled(
            *app_config.ui.tree_display_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        view.setFrameShape(QFrame.Shape.Box)
        view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mp_l.addWidget(view, stretch=1)

        return main_panel
    
    def _register_plugins(self):
        """Register all available plugins"""
        from src.core.plugin_loader import plugin_loader
        plugin_loader.load_all_plugins()
        
        loaded_plugins = plugin_loader.get_loaded_plugins()
        print(f"Loaded plugins: {', '.join(loaded_plugins)}")
    
    def _load_methods(self):
        """Load available analysis methods into the combo box"""
        available_methods = self.analysis_service.get_available_methods()
        self.method_combo.addItems(available_methods)
    
    def _start_analysis(self):
        """Start the analysis with the selected method"""
        method_name = self.method_combo.currentText()
        
        try:
            # Check if method is implemented
            processor = plugin_registry.get_processor_by_name(method_name)
            if not processor:
                QMessageBox.information(
                    self, "Information", 
                    "The selected method is not available!"
                )
                return
            
            # Open analysis window
            if self.analysis_window is None:
                self.analysis_window = AnalysisWindow(
                    self.analysis_service, 
                    method_name
                )
            else:
                self.analysis_window.set_method(method_name)
            
            self.analysis_window.show()
            
        except NotImplementedError:
            QMessageBox.information(
                self, "Information", 
                "The method is currently being implemented!"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Please check everything and try again!\nError: {str(e)}"
            )


def create_application() -> QApplication:
    """Create and configure the QApplication"""
    app = QApplication(sys.argv)
    
    # Apply material theme
    apply_stylesheet(app, theme='light_blue.xml')
    
    # Load custom stylesheet safely
    style_path = resource_path(app_config.paths.style_qss)
    if os.path.exists(style_path):
        with open(style_path, "r") as file:
            app.setStyleSheet(file.read())
    
    return app
 

def main():
    """Main application entry point"""
    app = create_application()
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())
