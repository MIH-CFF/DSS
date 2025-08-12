"""
Base UI components and progress handling.
"""
from typing import Optional
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QMovie
from src.core.interfaces import IProgressCallback
from src.utils.resources import resource_path


class ProgressCallback(IProgressCallback):
    """Progress callback implementation for UI updates"""
    
    def __init__(self, progress_dialog: Optional['ProgressDialog'] = None):
        self.progress_dialog = progress_dialog
        
    def update_progress(self, progress: float, message: str = "") -> None:
        """Update progress (0.0 to 1.0)"""
        if self.progress_dialog:
            self.progress_dialog.update_progress(int(progress * 100), message)
    
    def set_status(self, status: str) -> None:
        """Set status message"""
        if self.progress_dialog:
            self.progress_dialog.set_status(status)


class ProgressDialog(QDialog):
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing...")
        self.setWindowIcon(QIcon(resource_path("images/demo_logo.png")))
        self.setStyleSheet("background-color:white")
        self.setFixedSize(300, 150)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def update_progress(self, value: int, message: str = "") -> None:
        """Update progress value and optional message"""
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
    
    def set_status(self, status: str) -> None:
        """Set status message"""
        self.status_label.setText(status)


class LoadingDialog(QDialog):
    """Simple loading dialog with animated GIF"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading...")
        self.setWindowIcon(QIcon(resource_path("images/demo_logo.png")))
        self.setStyleSheet("background-color:white")
        self.setFixedSize(200, 200)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel("")
        self.movie = QMovie(resource_path("images/loading.gif"))
        self.label.setStyleSheet("border:none")
        self.movie.setScaledSize(QSize(200, 200))
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)


class WorkerThread(QThread):
    """Generic worker thread for background operations"""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)
    progress = pyqtSignal(float, str)
    
    def __init__(self, work_function, *args, **kwargs):
        super().__init__()
        self.work_function = work_function
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            # Create progress callback for this thread
            progress_callback = ThreadProgressCallback(self)
            
            # Check if the function accepts progress_callback parameter
            if 'progress_callback' in self.work_function.__code__.co_varnames:
                # Add progress callback to kwargs, not as positional argument
                self.kwargs['progress_callback'] = progress_callback
            
            result = self.work_function(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


class ThreadProgressCallback(IProgressCallback):
    """Progress callback that emits signals for thread communication"""
    
    def __init__(self, thread: WorkerThread):
        self.thread = thread
    
    def update_progress(self, progress: float, message: str = "") -> None:
        """Update progress (0.0 to 1.0)"""
        self.thread.progress.emit(progress, message)
    
    def set_status(self, status: str) -> None:
        """Set status message"""
        self.thread.progress.emit(-1, status)  # Use -1 to indicate status only
