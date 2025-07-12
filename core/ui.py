import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLineEdit, QFileDialog, QRadioButton, QSpinBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QIcon, QPixmap)
from head import head

class BAUSimilarityWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BAU Similarity")
        self.setWindowIcon(QIcon("images/demo_logo.png"))
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)

        # Top bar
        # top_bar = QHBoxLayout()
        # logo_bau = QLabel()
        # logo_pix=QPixmap("images/bau_logo.png")
        # logo_pix=logo_pix.scaled(60, 50)  
        # logo_bau.setPixmap(logo_pix) 
        # # logo.setFrameShape(QFrame.Shape.Box)
        # logo_bau.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # logo_bau.setFixedSize(60, 50)

        # title = QLabel("BAU Similarity")
        # title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # logo_ict_min = QLabel()
        # logo_ict_pix=QPixmap("images/ict_min_logo.png")
        # logo_ict_pix=logo_ict_pix.scaled(90, 50)  
        # logo_ict_min.setPixmap(logo_ict_pix) 
        # # logo.setFrameShape(QFrame.Shape.Box)
        # logo_ict_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # logo_ict_min.setFixedSize(90, 50)

        # top_bar.addWidget(logo_bau)
        # top_bar.addWidget(title, stretch=1)
        # top_bar.addWidget(logo_ict_min)
        main_v.addLayout(head())

        # Content
        content = QHBoxLayout()

        # Left panel
        left = QFrame()
        left.setFrameShape(QFrame.Shape.StyledPanel)
        left_l = QVBoxLayout(left)
        left_l.addWidget(QLabel("Select Method"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Method 1", "Method 2", "Method 3", "Method 4"])
        left_l.addWidget(self.method_combo)

        self.method_list = QListWidget()
        self.method_list.addItems(["opt1", "opt2", "opt3", "opt4"])
        left_l.addWidget(self.method_list)
        left_l.addStretch()
        content.addWidget(left, 0)

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
        layout.addLayout(head())
        # Top controls
        top_h = QHBoxLayout()

        # Browse Fasta
        browse_h = QHBoxLayout()
        browse_h.addWidget(QLabel("Browse Fasta"))
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_h.addWidget(self.path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_fasta)
        browse_h.addWidget(browse_btn)
        browse_h.addWidget(QLabel("Count:"))
        self.count_label = QLabel("0")
        browse_h.addWidget(self.count_label)
        browse_h.addStretch()
        top_h.addLayout(browse_h)

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
        layout.addWidget(tree_frame, stretch=1)

        # Bottom row
        bottom_h2 = QHBoxLayout()
        bottom_h2.addWidget(QLabel("Box"))
        bottom_h2.addWidget(QPushButton("Rotate"))
        bottom_h2.addStretch(1)
        bottom_h2.addWidget(QLabel("Movie Tree"))
        bottom_h2.addStretch(2)
        layout.addLayout(bottom_h2)

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
    bau = BAUSimilarityWindow()
    phylo = PhyloTreeWindow()
    bau.show()
    phylo.show()
    sys.exit(app.exec())
