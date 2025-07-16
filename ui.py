import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLineEdit, QFileDialog, QRadioButton, QSpinBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap,QIcon
from qt_material import apply_stylesheet


class BAUSimilarityWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BAU Similarity")
        self.setWindowIcon(QIcon("images/demo_logo.png"))
        self.resize(900, 600)
    

        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        
        logo_h_layout = QHBoxLayout()
        
        # Added BAU logo- ASIF
        bau_logo_label = QLabel()
        bau_logo_pixmap = QPixmap("images/bau_logo.png") 
        bau_logo_label.setFixedSize(130, 50)
        bau_logo_label.setPixmap(bau_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        bau_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bau_logo_label.setStyleSheet("background-color: transparent;""border:none;")
        logo_h_layout.addWidget(bau_logo_label)
        
        # Added ict ministry logo on right
        ict_logo_label = QLabel()
        ict_logo_pixmap = QPixmap("images/ict_min_logo.png") 
        ict_logo_label.setFixedSize(130, 50)
        ict_logo_label.setPixmap(ict_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ict_logo_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ict_logo_label.setStyleSheet("background-color: transparent;""border:none;")
        title = QLabel("BAU Similarity")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:30px;" "font-weight:bold;")
        logo_h_layout.addWidget(title,stretch=1)
        logo_h_layout.addWidget(ict_logo_label)
        main_v.addLayout(logo_h_layout)
        
        title.setObjectName("TitleLabel")
        bau_logo_label.setProperty("logo", True)
        ict_logo_label.setProperty("logo", True)

        # Content
        content = QVBoxLayout()
        
        # method selection
        select = QFrame()
        select.setFrameShape(QFrame.Shape.StyledPanel)
        select_v = QHBoxLayout(select)
        select.setStyleSheet("border:None;""margin-left:10px;""width:100px;""background-color:transparent;")
        select_v.addWidget(QLabel("Select Method"))
        self.method_combo = QComboBox()
        
        self.method_combo.addItems(["Method 1", "Method 2", "Method 3", "Method 4"])
        self.method_combo.setCurrentIndex(0)
        self.method_combo.setStyleSheet("""
                                        border: 1px solid #abadaf;
                                        color: #00acc1;
                                        font-weight: bold;
                                        padding: 4px;
                                        border-radius: 4px;
                                        background-color:white;
                                        """)
        select_v.addWidget(self.method_combo)
        select_v.addStretch(0)
        content.addWidget(select, 0)

        # Main panel
        main_panel = QFrame()
        main_panel.setFrameShape(QFrame.Shape.StyledPanel)
        mp_l = QVBoxLayout(main_panel)

        view = QFrame()
        view.setFrameShape(QFrame.Shape.Box)
        v_l = QVBoxLayout(view)
        v_l.addStretch()
        h_l = QHBoxLayout()
        h_l.addStretch()
        preview = QFrame()
        preview.setFrameShape(QFrame.Shape.Box)
        preview.setFixedSize(150, 100)
        h_l.addWidget(preview)
        h_l.addStretch()
        v_l.addLayout(h_l)
        v_l.addStretch()

        mp_l.addWidget(view, stretch=1)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(QPushButton("Text View"))
        mp_l.addLayout(bottom)

        content.addWidget(main_panel, 1)
        main_v.addLayout(content)


class PhyloTreeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phylogenetic Tree")
        self.setWindowIcon(QIcon("images/demo_logo.png"))
        self.resize(900, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        
        logo_h_layout = QHBoxLayout()
        
        # Added BAU logo- ASIF
        bau_logo_label = QLabel()
        bau_logo_pixmap = QPixmap("images/bau_logo.png") 
        bau_logo_label.setFixedSize(130, 50)
        bau_logo_label.setPixmap(bau_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        bau_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bau_logo_label.setStyleSheet("background-color: transparent;""border:none;")
        logo_h_layout.addWidget(bau_logo_label)
        
        # Added ict ministry logo on right
        ict_logo_label = QLabel()
        ict_logo_pixmap = QPixmap("images/ict_min_logo.png") 
        ict_logo_label.setFixedSize(130, 50)
        ict_logo_label.setPixmap(ict_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ict_logo_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ict_logo_label.setStyleSheet("background-color: transparent;""border:none;")
        
        title = QLabel("BAU Similarity")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_h_layout.addWidget(title,stretch=1) 
        
        logo_h_layout.addWidget(ict_logo_label)
        logo_h_layout.setContentsMargins(0, 5, 0, 20)
        layout.addLayout(logo_h_layout)

        title.setObjectName("TitleLabel")
        bau_logo_label.setProperty("logo", True)
        ict_logo_label.setProperty("logo", True)
        # Top controls
        top_h = QHBoxLayout()

        # Browse Fasta
        browse_h = QHBoxLayout()
        browse_h.addWidget(QLabel("Browse Fasta"))
        self.path_edit = QLineEdit()
        self.path_edit.setStyleSheet("width:200px;")
        self.path_edit.setReadOnly(True)
        browse_h.addWidget(self.path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_fasta)
        browse_btn.setStyleSheet("margin-left:5px;")
        browse_h.addWidget(browse_btn)
        browse_h.addWidget(QLabel("Count:"))
        self.count_label = QLabel("0")
        browse_h.addWidget(self.count_label)
        browse_h.addStretch()
        top_h.addLayout(browse_h,stretch=1)

        # Select k
        select_h = QHBoxLayout()
        select_h.addWidget(QLabel("Select k"))
        self.rb_default = QRadioButton("Default")
        self.rb_default.setChecked(True)
        self.rb_custom = QRadioButton("Custom")
        self.spin_k = QSpinBox()
        self.spin_k.setRange(1, 100)
        self.spin_k.setEnabled(False)
        self.rb_default.toggled.connect(lambda checked: self.spin_k.setEnabled(not checked))

        select_h.addWidget(self.rb_default)
        select_h.addWidget(self.rb_custom)
        select_h.addWidget(self.spin_k)
        select_h.addStretch()
        top_h.addLayout(select_h)

        layout.addLayout(top_h)

        # Options button
        opts_h = QHBoxLayout()
        opts_btn = QToolButton()
        opts_btn.setText("Options")
        opts_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        opts_menu = QMenu()
        opts_btn.setStyleSheet("width:100px;")
        opts_menu.addAction("Option 1")
        opts_menu.addAction("Option 2")
        opts_btn.setMenu(opts_menu)
        opts_h.addWidget(opts_btn)
        opts_h.addStretch()
        layout.addLayout(opts_h)

        # Tree frame
        tree_frame = QFrame()
        tree_frame.setFrameShape(QFrame.Shape.Box)
        tf_l = QVBoxLayout(tree_frame)
        lbl = QLabel("Phylogenetic Tree")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf_l.addWidget(lbl)
        layout.addWidget(tree_frame, stretch=4)

        # Bottom row
        bottom_h2 = QHBoxLayout()
        bottom_h2.addStretch(1)
        bottom_h2.addWidget(QLabel("Box"))
        bottom_h2.addWidget(QPushButton("Rotate"))
        
        layout.addLayout(bottom_h2)
        
        # Newic Tree frame
        newick_tree_frame = QFrame()
        newick_tree_frame.setFrameShape(QFrame.Shape.Box)
        ntf_l = QVBoxLayout(newick_tree_frame)
        n_lbl = QLabel("Newick Tree")
        n_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ntf_l.addWidget(n_lbl)
        layout.addWidget(newick_tree_frame, stretch=1)

    def browse_fasta(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Open FASTA", "", "FASTA Files (*.fa *.fasta);;All Files (*)"
        )
        if not fname:
            return
        self.path_edit.setText(fname)
        count = 0
        try:
            with open(fname) as f:
                for line in f:
                    if line.startswith(">"):
                        count += 1
        except Exception:
            count = 0
        self.count_label.setText(str(count))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    with open("style.qss", "r") as file:
        app.setStyleSheet(file.read())
    bau = BAUSimilarityWindow()
    phylo = PhyloTreeWindow()
    bau.show()
    phylo.show()
    sys.exit(app.exec())