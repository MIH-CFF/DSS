import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLineEdit, QFileDialog, QRadioButton, QSpinBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (QIcon, QPixmap)
def head():
    
    top_bar = QHBoxLayout()
    logo_bau = QLabel()
    # logo_bau.setStyleSheet("background-color: #f0f0f0;")
    logo_bau_pix=QPixmap("images/bau_logo.png")
    logo_bau_pix=logo_bau_pix.scaled(60, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  
    logo_bau.setPixmap(logo_bau_pix) 
    # logo.setFrameShape(QFrame.Shape.Box)
    logo_bau.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo_bau.setFixedSize(60, 50)

    title = QLabel("BAU Similarity")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    logo_ict_min = QLabel()
    logo_ict_pix=QPixmap("images/ict_min_logo.png")
    logo_ict_pix=logo_ict_pix.scaled(90, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  
    logo_ict_min.setPixmap(logo_ict_pix) 
    # logo.setFrameShape(QFrame.Shape.Box)
    logo_ict_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo_ict_min.setFixedSize(90, 50)

    top_bar.addWidget(logo_bau)
    top_bar.addWidget(title, stretch=1)
    top_bar.addWidget(logo_ict_min)    
    
    return top_bar