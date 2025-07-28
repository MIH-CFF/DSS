from imports import *
class PhyloTreeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phylogenetic Tree")
        self.setWindowIcon(QIcon("images/demo_logo.png"))
        self.resize(900, 600)
        self.move(100,50)
        
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
        logo_h_layout.addWidget(bau_logo_label)
        
        # Added ict ministry logo on right
        ict_logo_label = QLabel()
        ict_logo_pixmap = QPixmap("images/ict_min_logo.png") 
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
        self.rb_default = QRadioButton("Default")
        self.rb_default.setChecked(True)
        self.rb_custom = QRadioButton("Custom")
        self.spin_k = QSpinBox()
        self.spin_k.setRange(1, 10)
        self.spin_k.setValue(4)
        self.spin_k.setEnabled(False)
        self.rb_default.toggled.connect(lambda checked: self.spin_k.setEnabled(not checked))
        self.button_k=QButtonGroup(self)
        self.button_k.addButton(self.rb_custom)
        self.button_k.addButton( self.rb_default)
        select_h.addWidget(self.rb_default)
        select_h.addWidget(self.rb_custom)
        select_h.addWidget(self.spin_k)
        select_h.addStretch()
        top_h.addLayout(select_h)

        layout.addLayout(top_h)

        # Options button
        opts_h = QHBoxLayout()
        draw_btn = QPushButton("Generate Phylogenetic tree")
        draw_btn.clicked.connect(self.draw_phylo)
        #draw_btn.setStyleSheet("Width:50px;")
        opts_h.addWidget(draw_btn)
        opts_h.addStretch()
        opts_lbl=QLabel("Select Thresh percent (%) : ")
        opts_lbl.setStyleSheet("border:none;""background-color:transparent")
        opts_h.addWidget(opts_lbl)
        self.t_df_default = QRadioButton("Default")
        self.t_df_default.setChecked(True)
        self.t_cm_custom = QRadioButton("Custom")
        self.t_spin = QSpinBox()
        
        self.t_spin.setRange(0, 100)
        self.t_spin.setValue(50)
        self.t_spin.setEnabled(False)
        self.t_df_default.toggled.connect(lambda checked: self.t_spin.setEnabled(not checked))
        self.button_t=QButtonGroup(self)
        self.button_t.addButton( self.t_df_default)
        self.button_t.addButton(self.t_cm_custom)
        opts_h.addWidget(self.t_df_default)
        opts_h.addWidget(self.t_cm_custom)
        opts_h.addWidget(self.t_spin)
        
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
        n_lbl = QLabel("Newick Tree")
        n_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ntf_l.addWidget(n_lbl)
        layout.addWidget(newick_tree_frame, stretch=1)
        self.fname=None

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
        else:
            try:
                dtm = DPTM_func.DynamicTM
                
                if self.rb_default.isChecked():
                    k_len=4
                else:
                    k_len=self.spin_k.value()
                
                if self.t_df_default.isChecked():
                    thresh=50
                else:
                    thresh=self.t_spin.value()
                    
                tree_rcv = dtm.read_fas1(self.fname,k_len,thresh,self=None)

                current_directory = os.getcwd()
                fig = plt.figure(figsize=(16,10), dpi=100)
                axes = fig.add_subplot(1, 1, 1)
                Phylo.draw(tree_rcv, axes=axes, do_show=False)
                fig_name = current_directory + '/phylogenetic_tree/' + 'phylo.png'
                #plt.savefig('v5.png')
                plt.savefig(fig_name)
                plt.show()
                plt.close()
                phylo_tree_path = 'phylogenetic_tree/phylo.png'
                lbl_pix=QPixmap(phylo_tree_path)
                self.real_img=lbl_pix
                lbl_pix=lbl_pix.scaled(800,500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl.setPixmap(lbl_pix)
                # Set the file pointer to the beginning of the stream
            except Exception as e:
                print(e)
            
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
def run():

    phylo = PhyloTreeWindow()
    phylo.show()
if __name__ == "__main__":
    run()