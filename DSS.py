from imports import *

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_pixmap_safely(image_path, default_size=(130, 50)):
    """Load pixmap safely with fallback"""
    full_path = resource_path(image_path)
    if os.path.exists(full_path):
        return QPixmap(full_path)
    else:
        # Create a colored rectangle as fallback
        pixmap = QPixmap(*default_size)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return pixmap

class BAUSimilarityWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BAU Similarity")
        # Set window icon safely
        icon_path = resource_path("images/demo_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(900, 600)
    

        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        
        logo_h_layout = QHBoxLayout()
        
        # Added BAU logo- ASIF
        bau_logo_label = QLabel()
        bau_logo_pixmap = load_pixmap_safely("images/bau_logo.png", (130, 50))
        bau_logo_label.setFixedSize(130, 50)
        bau_logo_label.setPixmap(bau_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        bau_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo_h_layout.addWidget(bau_logo_label)
        
        # Added ict ministry logo on right
        ict_logo_label = QLabel()
        ict_logo_pixmap = load_pixmap_safely("images/ict_min_logo.png", (130, 50))
        ict_logo_label.setFixedSize(130, 50)
        ict_logo_label.setPixmap(ict_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ict_logo_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        title = QLabel("BAU Similarity")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        select.setStyleSheet("""QFrame{
            border:None;
            background-color:transparent;
            }""")
        select_v = QHBoxLayout(select)
        
        select_lbl=QLabel("Select Method")
        select_lbl.setStyleSheet("border:None;""margin-left:10px;""width:100px;""background-color:transparent;")
        select_v.addWidget(select_lbl)
        self.method_combo = QComboBox()
        
        self.method_combo.addItems(["Chaos Game Frequency", "Template Matching", "Part-wise Template Matching", "Dynamic Part-wise TePart-wise Template Matching"])
        self.method_combo.setCurrentIndex(0)
        self.method_combo.setStyleSheet("background-color:white;")
        select_v.addWidget(self.method_combo)
        method_btn = QPushButton("Start")
        method_btn.clicked.connect(self.go_to_method)
        select_v.addWidget(method_btn)
        select_v.addStretch(0)
        content.addWidget(select)

        # Main panel
        main_panel = QFrame()
        main_panel.setFrameShape(QFrame.Shape.StyledPanel)
        mp_l = QVBoxLayout(main_panel)

        view = QLabel("Pylogenetic tree")
        view_pix = load_pixmap_safely("images/tree.png", (700, 400))
        view.setPixmap(view_pix.scaled(700, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        view.setFrameShape(QFrame.Shape.Box)
        view.setAlignment(Qt.AlignmentFlag.AlignCenter )
        mp_l.addWidget(view, stretch=1)

        
        content.addWidget(main_panel, 1)
        main_v.addLayout(content)
    def go_to_method(self):
        method=self.method_combo.currentText()
        try:
            if(method=='Dynamic Part-wise TePart-wise Template Matching'):
                DPTM_ui.run()
            else:
                QMessageBox.information(self, "Information", "The method is currently being implemented!")
        except:
            QMessageBox.information(self, "Error", "Please check everything and try again!")

       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    
    # Load stylesheet safely
    style_path = resource_path("style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as file:
            app.setStyleSheet(file.read())
    
    bau = BAUSimilarityWindow()
    bau.show()
    sys.exit(app.exec())