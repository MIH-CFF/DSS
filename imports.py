import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLineEdit, QFileDialog, QRadioButton, QButtonGroup, QSpinBox, QMenu,QMessageBox,
    QDialog, QProgressBar
)
from PyQt6.QtCore import Qt,QThread, pyqtSignal,QSize
from PyQt6.QtGui import QPixmap,QIcon,QMovie
from qt_material import apply_stylesheet
from matplotlib import pyplot as plt
import os
from Bio import Phylo
from Bio import SeqIO
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor, DistanceCalculator
from Bio.Seq import Seq
import time


        
import DPTM_func
import DPTM_ui
