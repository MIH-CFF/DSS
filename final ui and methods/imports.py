import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QComboBox, QListWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QLineEdit, QFileDialog, QRadioButton, QButtonGroup, QSpinBox, QMenu,QMessageBox,
    QDialog, QProgressBar
)
from PyQt6.QtCore import Qt,QThread, pyqtSignal,QSize
from PyQt6.QtGui import QPixmap,QIcon,QMovie,QGuiApplication
from qt_material import apply_stylesheet
from matplotlib import pyplot as plt
import os
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor, DistanceCalculator
import time
from Bio import Phylo, SeqIO
from scipy.spatial.distance import pdist
import warnings
import random
warnings.filterwarnings("ignore")
from io import StringIO

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

        
import DPTM_func
import DPTM_ui

import CGR_func
import CGR_ui

import PTM_func
import PTM_ui

import TM_func
import TM_ui

