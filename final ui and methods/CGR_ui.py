from imports import *
from imports import resource_path
class Loading(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading...")
        self.setWindowIcon(QIcon(resource_path("images\\demo_logo.png")))
        self.setStyleSheet("background-color:white")
        self.setFixedSize(200, 200)
        self.setModal(True)  

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("")
        self.movie = QMovie(resource_path("images\\loading.gif"))
        self.label.setStyleSheet("border:none")
        self.movie.setScaledSize(QSize(200,200))
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

class Works(QThread):
    finished = pyqtSignal(object,str)
    error = pyqtSignal(Exception)

    def __init__(self, fname, k_len, method):
        super().__init__()
        self.fname = fname
        self.k_len = k_len
        self.method = method

    def run(self):
        try:
            cgr = CGR_func.CGR()
            result,text = cgr.generate_tree(directory=self.fname,kmer=self.k_len,method=self.method)
            self.finished.emit(result,text)
        except Exception as e:
            self.error.emit(e)
        
class PhyloTreeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chaos Game Frequency Method")
        self.setWindowIcon(QIcon(resource_path("images\\demo_logo.png")))
        self.resize(900, 600)
        self.move(20,50)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        
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
        logo_h_layout.setContentsMargins(0, 5, 0, 20)
        layout.addLayout(logo_h_layout)

        title.setObjectName("TitleLabel")
        bau_logo_label.setProperty("logo", True)
        ict_logo_label.setProperty("logo", True)
        # Top controls
        top_h = QHBoxLayout()

        # Browse Fasta
        browse_h = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setStyleSheet("width:200px;")
        self.path_edit.setReadOnly(True)
        browse_h.addWidget(self.path_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_fasta)
        browse_h.addWidget(browse_btn)
        cnt_lbl=QLabel("Count:")
        cnt_lbl.setStyleSheet("border:none;""background-color:transparent")
        browse_h.addWidget(cnt_lbl)
        self.count_label = QLabel("0")
        browse_h.addWidget(self.count_label)
        browse_h.addStretch()
        top_h.addLayout(browse_h,stretch=1)

        # Select k
        select_h = QHBoxLayout()
        select_lbl=QLabel("Select k : ")
        select_lbl.setStyleSheet("border:none;""background-color:transparent")
        select_h.addWidget(select_lbl)
        self.rb_custom = QRadioButton("Custom")
        self.spin_k = QSpinBox()
        self.spin_k.setRange(1, 10)
        self.spin_k.setValue(4)
        self.spin_k.setEnabled(False)
        self.rb_custom.toggled.connect(lambda checked: self.spin_k.setEnabled(checked))
        self.button_k=QButtonGroup(self)
        self.button_k.addButton(self.rb_custom)
        select_h.addWidget(self.rb_custom)
        select_h.addWidget(self.spin_k)
        select_h.addStretch()
        top_h.addLayout(select_h)

        layout.addLayout(top_h)
        self.loading = Loading()
        # Options button
        opts_h = QHBoxLayout()
        draw_btn = QPushButton("Generate Phylogenetic tree")
        draw_btn.clicked.connect(self.draw_phylo)
        #draw_btn.setStyleSheet("Width:50px;")
        opts_h.addWidget(draw_btn)
        opts_h.addStretch()
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

        # Tree frame
        tree_frame = QFrame()
        tree_frame.setFrameShape(QFrame.Shape.Box)
        tf_l = QVBoxLayout(tree_frame)
        self.lbl = QLabel("Phylogenetic Tree")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf_l.addWidget(self.lbl)
        layout.addWidget(tree_frame, stretch=1)

        # Bottom row
        bottom_h2 = QHBoxLayout()
        bottom_h2.addStretch(1)
        self.download=QPushButton("Download")
        self.download.clicked.connect(self.save_tree)
        bottom_h2.addWidget(self.download)
        
        layout.addLayout(bottom_h2)
        
        # Newic Tree frame
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
        layout.addWidget(newick_tree_frame, stretch=1)
        #download newic tree
        bottom_h3 = QHBoxLayout()
        bottom_h3.addStretch(1)
        self.download_newic=QPushButton("Download")
        self.download_newic.clicked.connect(self.save_newic)
        bottom_h3.addWidget(self.download_newic)
        
        layout.addLayout(bottom_h3)
        self.fname=None
        self.newic=None

    def browse_fasta(self):
        self.fname = QFileDialog.getExistingDirectory(
    self, "Select Folder", "", QFileDialog.Option.ShowDirsOnly
        )
        if not self.fname:
            return
        self.path_edit.setText(self.fname)
        count = 0
        try:
            for file in os.listdir(self.fname):
            # check only text files
                if file.endswith('.fasta'):
                    count+=1
        except Exception:
            count = 0
        self.count_label.setText(str(count))
    def draw_phylo(self):
        if self.fname==None:
            QMessageBox.critical(self,"Error","Select File First")
            return
        k_len = self.spin_k.value() if self.rb_custom.isChecked() else 4
        method='upgma' if self.t_df_upgma.isChecked() else 'nj'
                
        self.loading.show() 
        self.loading.show()

        self.work = Works(self.fname, k_len, method)
        self.work.finished.connect(self.handle_result)
        self.work.error.connect(self.handle_error)
        self.work.start()

    def handle_result(self, tree_rcv,text):
        self.loading.close()

        try:
            current_directory = os.getcwd()
            fig = plt.figure(figsize=(16,10), dpi=100)
            axes = fig.add_subplot(1, 1, 1)
            Phylo.draw(tree_rcv, axes=axes, do_show=False)
            fig_name = current_directory + '/phylogenetic_tree/' + 'phylo.png'
            plt.savefig(fig_name)
            plt.show()
            plt.close()
            self.newic=text
            self.n_lbl.setText(text)
            phylo_tree_path = resource_path('phylogenetic_tree\\phylo.png')
            lbl_pix = QPixmap(phylo_tree_path)
            self.real_img = lbl_pix
            lbl_pix = lbl_pix.scaled(800, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl.setPixmap(lbl_pix)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error Generating image try again")
    def handle_error(self, e):
        self.loading.close()
        QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

   
    def save_tree(self):
        try:
            if self.real_img:
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
                )
                if save_path:
                    self.real_img.save(save_path)
                else:
                    QMessageBox.critical(self,"Error","Error try again")
        except:
            QMessageBox.critical(self,"Error","Generate Tree first")
    def save_newic(self):
        try:
            if self.newic:
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "Save Text","","Text Files (*.txt);;All Files (*)"
                )
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(self.newic)
                else:
                    QMessageBox.critical(self,"Error","Error try again")
        except:
            QMessageBox.critical(self,"Error","Generate Tree first")
def run():

    phylo = PhyloTreeWindow()
    phylo.show()
if __name__ == "__main__":
    run()