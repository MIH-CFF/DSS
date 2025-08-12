"""
Utility functions for resource management and file operations.
"""
import os
import sys
from typing import Tuple
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_pixmap_safely(image_path: str, default_size: Tuple[int, int] = (130, 50)) -> QPixmap:
    """Load pixmap safely with fallback"""
    full_path = resource_path(image_path)
    if os.path.exists(full_path):
        return QPixmap(full_path)
    else:
        # Create a colored rectangle as fallback
        pixmap = QPixmap(*default_size)
        pixmap.fill(Qt.GlobalColor.lightGray)
        return pixmap


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure that a directory exists, create if it doesn't"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def count_files_with_extension(directory_path: str, extension: str) -> int:
    """Count files with a specific extension in a directory"""
    if not os.path.exists(directory_path):
        return 0
    
    count = 0
    try:
        for file in os.listdir(directory_path):
            if file.lower().endswith(extension.lower()):
                count += 1
    except Exception:
        count = 0
    
    return count


def get_phylo_tree_directory() -> str:
    """Get the phylogenetic tree output directory"""
    phylo_dir = "phylogenetic_tree"
    ensure_directory_exists(phylo_dir)
    return phylo_dir
