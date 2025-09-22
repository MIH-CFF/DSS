from imports import *
class BAUSimilarityWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BAU Similarity")
        self.setWindowIcon(QIcon(resource_path("images\\demo_logo.png")))
        self.resize(900, 600)
    

        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        
        logo_h_layout = QHBoxLayout()
        
        # Added BAU logo- ASIF
        bau_logo_label = QLabel()
        bau_logo_pixmap = QPixmap(resource_path("images\\bau_logo.png"))
        bau_logo_label.setFixedSize(130, 50)
        bau_logo_label.setPixmap(bau_logo_pixmap.scaled(130, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        bau_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo_h_layout.addWidget(bau_logo_label)
        
        # Added ict ministry logo on right
        ict_logo_label = QLabel()
        ict_logo_pixmap = QPixmap(resource_path("images\\ict_min_logo.png"))
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
        select_v.addStretch()
        content.addWidget(select)

        # Main panel
        main_panel = QFrame()
        main_panel.setFrameShape(QFrame.Shape.StyledPanel)
        mp_l = QVBoxLayout(main_panel)

        view = QLabel("Pylogenetic tree")
        view_pix=QPixmap(resource_path("images\\tree.png"))
        view.setPixmap(view_pix.scaled(800, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
            elif(method=='Chaos Game Frequency'):
                CGR_ui.run()
            elif(method=='Part-wise Template Matching'):
                PTM_ui.run()
            elif(method=='Template Matching'):
                TM_ui.run()
        except():
            QMessageBox.information(self, "Error", "Please check everything and try again!")

       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    with open(resource_path("asset\\style.qss"), "r") as file:
        app.setStyleSheet(file.read())
    bau = BAUSimilarityWindow()
    bau.show()
    sys.exit(app.exec())