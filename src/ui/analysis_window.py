"""
Analysis window for configuring and running sequence analysis.
"""
import os
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QRadioButton, QButtonGroup, QSpinBox, QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from src.core.analysis_service import AnalysisService
from src.core.interfaces import AnalysisResult, MethodConfig
from src.ui.base_components import WorkerThread, ProgressDialog, ProgressCallback
from src.utils.resources import resource_path, load_pixmap_safely, get_phylo_tree_directory
from src.utils.config import app_config


class AnalysisWindow(QMainWindow):
    """Window for configuring and running sequence analysis"""
    
    def __init__(self, analysis_service: AnalysisService, method_name: str):
        super().__init__()
        self.analysis_service = analysis_service
        self.method_name = method_name
        self.current_directory: Optional[str] = None
        self.current_result: Optional[AnalysisResult] = None
        self.worker_thread: Optional[WorkerThread] = None
        self.progress_dialog: Optional[ProgressDialog] = None
        
        self._setup_ui()
        self._load_method_config()
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(f"BAU Similarity - {self.method_name}")
        self.setWindowIcon(QIcon(resource_path(app_config.paths.demo_logo)))
        self.resize(1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Logo layout
        self._create_logo_layout(layout)
        
        # Configuration controls
        self._create_config_controls(layout)
        
        # Tree display and download
        self._create_tree_display(layout)
        
        # Newick tree display (placeholder for future implementation)
        self._create_newick_display(layout)
    
    def _create_logo_layout(self, main_layout: QVBoxLayout):
        """Create logo layout (similar to main window)"""
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
        logo_h_layout.addWidget(bau_logo_label)
        
        # Title
        title = QLabel("BAU Similarity")
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
        logo_h_layout.addWidget(ict_logo_label)
        
        # Set properties
        bau_logo_label.setProperty("logo", True)
        ict_logo_label.setProperty("logo", True)
        
        logo_h_layout.setContentsMargins(0, 5, 0, 20)
        main_layout.addLayout(logo_h_layout)
    
    def _create_config_controls(self, main_layout: QVBoxLayout):
        """Create configuration controls"""
        # Top controls
        top_h = QHBoxLayout()
        
        # Browse for FASTA files
        self._create_browse_controls(top_h)
        
        # K-length selection (for DPTM method)
        if self.method_name == "Dynamic Part-wise Template Matching":
            self._create_k_selection_controls(top_h)
        
        # Template length selection (for Template Matching method)
        if self.method_name == "Template Matching":
            self._create_template_selection_controls(top_h)
        
        main_layout.addLayout(top_h)
        
        # Options and generation button
        opts_h = QHBoxLayout()
        
        # Generate button
        self.generate_btn = QPushButton("Generate Phylogenetic tree")
        self.generate_btn.clicked.connect(self._generate_tree)
        opts_h.addWidget(self.generate_btn)
        
        opts_h.addStretch()
        
        # Threshold selection (for DPTM method)
        if self.method_name == "Dynamic Part-wise Template Matching":
            self._create_threshold_controls(opts_h)
        
        # Similarity threshold selection (for Template Matching method)
        if self.method_name == "Template Matching":
            self._create_similarity_threshold_controls(opts_h)
        
        main_layout.addLayout(opts_h)
    
    def _create_browse_controls(self, layout: QHBoxLayout):
        """Create file browsing controls"""
        browse_h = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setStyleSheet("width:200px;")
        self.path_edit.setReadOnly(True)
        browse_h.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        browse_h.addWidget(browse_btn)
        
        cnt_lbl = QLabel("Count:")
        cnt_lbl.setStyleSheet("border:none; background-color:transparent")
        browse_h.addWidget(cnt_lbl)
        
        self.count_label = QLabel("0")
        browse_h.addWidget(self.count_label)
        
        browse_h.addStretch()
        layout.addLayout(browse_h, stretch=1)
    
    def _create_k_selection_controls(self, layout: QHBoxLayout):
        """Create k-length selection controls"""
        select_h = QHBoxLayout()
        
        select_lbl = QLabel("Select k : ")
        select_lbl.setStyleSheet("border:none; background-color:transparent")
        select_h.addWidget(select_lbl)
        
        self.rb_k_default = QRadioButton("Default")
        self.rb_k_default.setChecked(True)
        self.rb_k_custom = QRadioButton("Custom")
        
        self.spin_k = QSpinBox()
        self.spin_k.setRange(*app_config.analysis.k_length_range)
        self.spin_k.setValue(app_config.analysis.default_k_length)
        self.spin_k.setEnabled(False)
        
        self.rb_k_default.toggled.connect(
            lambda checked: self.spin_k.setEnabled(not checked)
        )
        
        self.button_k = QButtonGroup(self)
        self.button_k.addButton(self.rb_k_custom)
        self.button_k.addButton(self.rb_k_default)
        
        select_h.addWidget(self.rb_k_default)
        select_h.addWidget(self.rb_k_custom)
        select_h.addWidget(self.spin_k)
        select_h.addStretch()
        
        layout.addLayout(select_h)
    
    def _create_threshold_controls(self, layout: QHBoxLayout):
        """Create threshold selection controls"""
        opts_lbl = QLabel("Select Thresh percent (%) : ")
        opts_lbl.setStyleSheet("border:none; background-color:transparent")
        layout.addWidget(opts_lbl)
        
        self.rb_t_default = QRadioButton("Default")
        self.rb_t_default.setChecked(True)
        self.rb_t_custom = QRadioButton("Custom")
        
        self.spin_t = QSpinBox()
        self.spin_t.setRange(*app_config.analysis.threshold_range)
        self.spin_t.setValue(app_config.analysis.default_threshold)
        self.spin_t.setEnabled(False)
        
        self.rb_t_default.toggled.connect(
            lambda checked: self.spin_t.setEnabled(not checked)
        )
        
        self.button_t = QButtonGroup(self)
        self.button_t.addButton(self.rb_t_default)
        self.button_t.addButton(self.rb_t_custom)
        
        layout.addWidget(self.rb_t_default)
        layout.addWidget(self.rb_t_custom)
        layout.addWidget(self.spin_t)
    
    def _create_template_selection_controls(self, layout: QHBoxLayout):
        """Create template length selection controls for Template Matching"""
        select_h = QHBoxLayout()
        
        select_lbl = QLabel("Template Length : ")
        select_lbl.setStyleSheet("border:none; background-color:transparent")
        select_h.addWidget(select_lbl)
        
        self.rb_template_default = QRadioButton("Default (20)")
        self.rb_template_default.setChecked(True)
        self.rb_template_custom = QRadioButton("Custom")
        
        self.spin_template = QSpinBox()
        self.spin_template.setRange(5, 100)
        self.spin_template.setValue(20)
        self.spin_template.setEnabled(False)
        
        self.rb_template_default.toggled.connect(
            lambda checked: self.spin_template.setEnabled(not checked)
        )
        
        self.button_template = QButtonGroup(self)
        self.button_template.addButton(self.rb_template_custom)
        self.button_template.addButton(self.rb_template_default)
        
        select_h.addWidget(self.rb_template_default)
        select_h.addWidget(self.rb_template_custom)
        select_h.addWidget(self.spin_template)
        select_h.addStretch()
        
        layout.addLayout(select_h)
    
    def _create_similarity_threshold_controls(self, layout: QHBoxLayout):
        """Create similarity threshold selection controls for Template Matching"""
        opts_lbl = QLabel("Similarity Threshold : ")
        opts_lbl.setStyleSheet("border:none; background-color:transparent")
        layout.addWidget(opts_lbl)
        
        self.rb_sim_default = QRadioButton("Default (0.75)")
        self.rb_sim_default.setChecked(True)
        self.rb_sim_custom = QRadioButton("Custom")
        
        self.spin_sim = QSpinBox()
        self.spin_sim.setRange(50, 100)
        self.spin_sim.setValue(75)
        self.spin_sim.setSuffix("%")
        self.spin_sim.setEnabled(False)
        
        self.rb_sim_default.toggled.connect(
            lambda checked: self.spin_sim.setEnabled(not checked)
        )
        
        self.button_sim = QButtonGroup(self)
        self.button_sim.addButton(self.rb_sim_default)
        self.button_sim.addButton(self.rb_sim_custom)
        
        layout.addWidget(self.rb_sim_default)
        layout.addWidget(self.rb_sim_custom)
        layout.addWidget(self.spin_sim)
    
    def _create_tree_display(self, main_layout: QVBoxLayout):
        """Create tree display area"""
        tree_frame = QFrame()
        tree_frame.setFrameShape(QFrame.Shape.Box)
        tf_l = QVBoxLayout(tree_frame)
        
        self.tree_label = QLabel("Phylogenetic Tree")
        self.tree_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf_l.addWidget(self.tree_label)
        
        main_layout.addWidget(tree_frame, stretch=1)
        
        # Download button
        bottom_h = QHBoxLayout()
        bottom_h.addStretch(1)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self._save_tree)
        self.download_btn.setEnabled(False)
        bottom_h.addWidget(self.download_btn)
        
        main_layout.addLayout(bottom_h)
    
    def _create_newick_display(self, main_layout: QVBoxLayout):
        """Create Newick tree display area (placeholder)"""
        newick_frame = QFrame()
        newick_frame.setFrameShape(QFrame.Shape.Box)
        ntf_l = QVBoxLayout(newick_frame)
        
        n_lbl = QLabel("Newick Tree")
        n_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ntf_l.addWidget(n_lbl)
        
        main_layout.addWidget(newick_frame, stretch=1)
    
    def _load_method_config(self):
        """Load configuration for the current method"""
        config = self.analysis_service.get_method_config(self.method_name)
        if config:
            # Method-specific UI adjustments can be made here
            pass
    
    def _browse_directory(self):
        """Browse for directory containing FASTA files"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Folder", "", QFileDialog.Option.ShowDirsOnly
        )
        
        if not directory:
            return
        
        self.current_directory = directory
        self.path_edit.setText(directory)
        
        # Update file count
        count = self.analysis_service.count_fasta_files(directory)
        self.count_label.setText(str(count))
    
    def _generate_tree(self):
        """Generate phylogenetic tree"""
        if not self.current_directory:
            QMessageBox.critical(self, "Error", "Select File First")
            return
        
        # Build configuration
        config = self._build_config()
        
        # Setup progress dialog
        self.progress_dialog = ProgressDialog(self)
        progress_callback = ProgressCallback(self.progress_dialog)
        
        # Create worker thread
        self.worker_thread = WorkerThread(
            self._run_analysis,
            self.current_directory,
            config
        )
        
        self.worker_thread.finished.connect(self._handle_analysis_result)
        self.worker_thread.error.connect(self._handle_analysis_error)
        
        # Start analysis
        self.progress_dialog.show()
        self.worker_thread.start()
    
    def _build_config(self) -> MethodConfig:
        """Build configuration based on UI settings"""
        base_config = self.analysis_service.get_method_config(self.method_name)
        
        if self.method_name == "Dynamic Part-wise Template Matching":
            # Update DPTM-specific parameters
            base_config.parameters['k_length'] = (
                app_config.analysis.default_k_length 
                if self.rb_k_default.isChecked() 
                else self.spin_k.value()
            )
            base_config.parameters['threshold_percent'] = (
                app_config.analysis.default_threshold 
                if self.rb_t_default.isChecked() 
                else self.spin_t.value()
            )
        elif self.method_name == "Template Matching":
            # Update Template Matching-specific parameters
            base_config.parameters['template_length'] = (
                20 
                if self.rb_template_default.isChecked() 
                else self.spin_template.value()
            )
            base_config.parameters['similarity_threshold'] = (
                0.75 
                if self.rb_sim_default.isChecked() 
                else self.spin_sim.value() / 100.0
            )
        
        return base_config
    
    def _run_analysis(self, directory: str, config: MethodConfig, **kwargs):
        """Run the analysis (executed in worker thread)"""
        progress_callback = kwargs.get('progress_callback')
        
        # Load sequences
        sequences = self.analysis_service.load_sequences_from_directory(directory)
        
        # Analyze sequences
        result = self.analysis_service.analyze_sequences(
            sequences, self.method_name, config, progress_callback
        )
        
        # Generate visualization
        output_path = os.path.join(
            get_phylo_tree_directory(), 
            'phylo.png'
        )
        
        image_path = self.analysis_service.visualize_result(
            result, output_path,
            figsize=app_config.ui.tree_output_size,
            dpi=app_config.ui.tree_dpi
        )
        
        return result, image_path
    
    def _handle_analysis_result(self, result_data):
        """Handle successful analysis result"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        try:
            result, image_path = result_data
            self.current_result = result
            
            # Display the tree image
            lbl_pix = QPixmap(image_path)
            self.tree_pixmap = lbl_pix  # Store original for saving
            
            # Scale for display
            scaled_pix = lbl_pix.scaled(
                800, 500, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.tree_label.setPixmap(scaled_pix)
            
            # Enable download button
            self.download_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error displaying results: {str(e)}"
            )
    
    def _handle_analysis_error(self, error: Exception):
        """Handle analysis error"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.critical(
            self, "Error", 
            f"An error occurred during analysis:\n{str(error)}"
        )
    
    def _save_tree(self):
        """Save the tree image"""
        if not hasattr(self, 'tree_pixmap'):
            QMessageBox.critical(
                self, "Error", 
                "Generate Tree first"
            )
            return
        
        try:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", 
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            
            if save_path:
                self.tree_pixmap.save(save_path)
                QMessageBox.information(
                    self, "Success", 
                    f"Image saved to: {save_path}"
                )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error saving image: {str(e)}"
            )
    
    def set_method(self, method_name: str):
        """Set the analysis method"""
        self.method_name = method_name
        self.setWindowTitle(f"BAU Similarity - {method_name}")
        self._load_method_config()
