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
from PyQt6.QtGui import QIcon, QPixmap, QGuiApplication

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
        
        # K-length selection (for CGR method)
        if self.method_name == "Chaos Game Frequency Representation":
            self._create_k_selection_controls(top_h)
        
        # Partition selection (for Template Matching method)
        if self.method_name == "Template Matching":
            self._create_partition_selection_controls(top_h)
            
        # Partition selection (for Part-wise Template Matching method)
        if self.method_name == "Part-wise Template Matching":
            self._create_partition_selection_controls(top_h)
            
        
        main_layout.addLayout(top_h)
        mid_h=QHBoxLayout()
        mid_h.addStretch()
        # Base length selection (for Part-wise Template Matching method)
        if self.method_name == "Part-wise Template Matching":
            self._create_base_length_selection_controls(mid_h)
            main_layout.addLayout(mid_h)
        
        # Thresh(%) selection (for DPTM method)
        if self.method_name == "Dynamic Part-wise Template Matching":
            self._create_threshold_controls(mid_h)  
            main_layout.addLayout(mid_h) 
             
        # Options and generation button
        opts_h = QHBoxLayout()
        
        # Generate button
        self.generate_btn = QPushButton("Generate Phylogenetic tree")
        self.generate_btn.clicked.connect(self._generate_tree)
        opts_h.addWidget(self.generate_btn)
        
        opts_h.addStretch()
        
        
        # Method selection (for all method)
        self._create_construction_method_selection_controls(opts_h)
        
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
        select_lbl=QLabel("Select k : ")
        select_lbl.setStyleSheet("border:none;""background-color:transparent")
        select_h.addWidget(select_lbl)
        self.rb_custom = QRadioButton("Custom")
        self.spin_k = QSpinBox()
        self.spin_k.setRange(*app_config.analysis.k_length_range)
        self.spin_k.setValue(app_config.analysis.default_k_length)
        self.spin_k.setEnabled(False)
        self.rb_custom.toggled.connect(lambda checked: self.spin_k.setEnabled(checked))
        self.button_k=QButtonGroup(self)
        self.button_k.addButton(self.rb_custom)
        select_h.addWidget(self.rb_custom)
        select_h.addWidget(self.spin_k)
        select_h.addStretch()
        
        layout.addLayout(select_h)
    
    def _create_threshold_controls(self, layout: QHBoxLayout):
        """Create threshold selection controls"""
        opts_h = QHBoxLayout()
        opts_lbl=QLabel("Select Thresh percent (%) : ")
        opts_lbl.setStyleSheet("border:none;""background-color:transparent")
        opts_h.addWidget(opts_lbl)
        self.t_cm_custom = QRadioButton("Custom")
        self.t_spin = QSpinBox()
        
        self.t_spin.setRange(*app_config.analysis.threshold_range)
        self.t_spin.setValue(app_config.analysis.default_threshold)
        self.t_spin.setEnabled(False)
        self.t_cm_custom.toggled.connect(lambda checked: self.t_spin.setEnabled(checked))
        self.button_t=QButtonGroup(self)
        self.button_t.addButton(self.t_cm_custom)
        opts_h.addWidget(self.t_cm_custom)
        opts_h.addWidget(self.t_spin)
        
        layout.addLayout(opts_h)
    
    def _create_construction_method_selection_controls(self, layout: QHBoxLayout):
        """Create method selection controls"""
        opts_h = QHBoxLayout()
        opts_lbl=QLabel("Select Method : ")
        opts_lbl.setStyleSheet("border:none;""background-color:transparent")
        opts_h.addWidget(opts_lbl)
        self.t_df_upgma = QRadioButton("UPGMA")
        self.t_df_upgma.setChecked(True)
        self.t_cm_nj = QRadioButton("NJ")
        self.button_t=QButtonGroup(self)
        self.button_t.addButton( self.t_df_upgma)
        self.button_t.addButton(self.t_cm_nj)
        opts_h.addWidget(self.t_df_upgma)
        opts_h.addWidget(self.t_cm_nj)
        layout.addLayout(opts_h)
        
    def _create_partition_selection_controls(self, layout: QHBoxLayout):
        """Create partition selection controls"""
        select_h = QHBoxLayout()
        select_lbl=QLabel("Select partition : ")
        select_lbl.setStyleSheet("border:none;""background-color:transparent")
        select_h.addWidget(select_lbl)
        self.p_custom = QRadioButton("Custom")
        self.spin_p = QSpinBox()
        self.spin_p.setRange(*app_config.analysis.partition_length_range)
        self.spin_p.setValue(app_config.analysis.default_partition_length)
        self.spin_p.setEnabled(False)
        self.p_custom.toggled.connect(lambda checked: self.spin_p.setEnabled(checked))
        self.button_p=QButtonGroup(self)
        self.button_p.addButton(self.p_custom)
        select_h.addWidget(self.p_custom)
        select_h.addWidget(self.spin_p)
        select_h.addStretch()
        layout.addLayout(select_h)
    def _create_base_length_selection_controls(self, layout: QHBoxLayout):
        """Create base length selection controls"""
        select_b = QHBoxLayout()
        select_b.addStretch()
        select_b_lbl=QLabel("Select base length : ")
        select_b_lbl.setStyleSheet("border:none;""background-color:transparent")
        select_b.addWidget(select_b_lbl)
        self.b_custom = QRadioButton("Custom")
        self.spin_b = QSpinBox()
        self.spin_b.setRange(*app_config.analysis.base_length_range)
        self.spin_b.setValue(app_config.analysis.default_base_length)
        self.spin_b.setEnabled(False)
        self.b_custom.toggled.connect(lambda checked: self.spin_b.setEnabled(checked))
        self.button_b=QButtonGroup(self)
        self.button_b.addButton(self.b_custom)
        select_b.addWidget(self.b_custom)
        select_b.addWidget(self.spin_b)
        
        layout.addLayout(select_b)
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
        newick_tree_frame = QFrame()
        newick_tree_frame.setFrameShape(QFrame.Shape.Box)
        ntf_l = QVBoxLayout(newick_tree_frame)
        self.n_lbl = QLabel("Newick Tree")
        screen = QGuiApplication.primaryScreen()
        geometry = screen.geometry()
        screen_width = geometry.width()
        self.n_lbl.setMaximumWidth(screen_width)  
        self.n_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ntf_l.addWidget(self.n_lbl)
        main_layout.addWidget(newick_tree_frame, stretch=1)
        #download newic tree
        bottom_h3 = QHBoxLayout()
        bottom_h3.addStretch(1)
        self.download_newic=QPushButton("Download")
        self.download_newic.clicked.connect(self._save_newic)
        bottom_h3.addWidget(self.download_newic)
        
        main_layout.addLayout(bottom_h3)
    
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
                self.spin_k.value() 
                if self.rb_custom.isChecked() 
                else app_config.analysis.default_k_length 
            )
            base_config.parameters['threshold_percent'] = (
                self.t_spin.value()
                if self.t_cm_custom.isChecked() 
                else app_config.analysis.default_threshold
            )
            base_config.parameters['construction_method'] = (
                "nj"
                if self.t_cm_nj.isChecked() 
                else "upgma"
            )
        elif self.method_name == "Template Matching":
            # Update TM-specific parameters
            base_config.parameters['partition'] = (
                self.spin_p.value()
                if self.p_custom.isChecked() 
                else app_config.analysis.default_partition_length
            )
            base_config.parameters['construction_method'] = (
                "nj"
                if self.t_cm_nj.isChecked() 
                else "upgma"
            )
        elif self.method_name == "Chaos Game Frequency Representation":
            # Update CGR-specific parameters
            base_config.parameters['k_length'] = (
                self.spin_k.value() 
                if self.rb_custom.isChecked() 
                else app_config.analysis.default_k_length 
            )
            base_config.parameters['construction_method'] = (
                "nj"
                if self.t_cm_nj.isChecked() 
                else "upgma"
            )
        elif self.method_name == "Part-wise Template Matching":
            # Update PTM-specific parameters
            base_config.parameters['base_length'] = (
                self.spin_b.value() 
                if self.b_custom.isChecked() 
                else app_config.analysis.default_base_length 
            )
            base_config.parameters['partition'] = (
                self.spin_p.value()
                if self.p_custom.isChecked() 
                else app_config.analysis.default_partition_length
            )
            base_config.parameters['construction_method'] = (
                "nj"
                if self.t_cm_nj.isChecked() 
                else "upgma"
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
            self.newick=result.newick
            self.n_lbl.setText(self.newick)
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
    def _save_newic(self):
        """Save the newic"""
        if not hasattr(self, 'newick'):
            QMessageBox.critical(
                self, "Error", 
                "Generate Tree first"
            )
            return
        try:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Text","","Text Files (*.txt);;All Files (*)"
                )
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(self.newick)
                QMessageBox.information(
                    self, "Success", 
                    f"Newic tree saved to: {save_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error saving Newic tree: {str(e)}"
            )
    def _clear_ui(self):
        """Remove all widgets/layouts from the central widget."""
        central = self.centralWidget()
        if central is not None:
            # Delete children safely
            for child in central.children():
                child.deleteLater()
            central.setParent(None)
    def set_method(self, method_name: str):
        """Set the analysis method"""
        self.method_name = method_name
        self.setWindowTitle(f"BAU Similarity - {method_name}")
        # Clear existing UI
        self._clear_ui()
    
        # Rebuild UI for the new method
        self._setup_ui()
        self._load_method_config()
