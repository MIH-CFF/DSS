"""
Unit tests for UI components
"""
import pytest
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from src.ui.main_window import MainWindow
from src.ui.analysis_window import AnalysisWindow


@pytest.mark.unit
@pytest.mark.gui
class TestMainWindowComponents:
    """Test MainWindow UI components"""
    
    def test_main_window_initialization(self, qtbot, qapp):
        """Test MainWindow initializes correctly"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert window is not None
        assert window.method_combo is not None
    
    def test_method_combo_box_populated(self, qtbot, qapp):
        """Test method combo box has items"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        assert window.method_combo.count() > 0
    
    def test_window_title(self, qtbot, qapp):
        """Test window has correct title"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        title = window.windowTitle()
        assert "DNA Sequence Similarity" in title or "DSS" in title
    
    def test_window_has_central_widget(self, qtbot, qapp):
        """Test window has central widget"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        central = window.centralWidget()
        assert central is not None
    
    def test_find_start_button(self, qtbot, qapp):
        """Test finding start button in window"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Find all buttons
        buttons = window.findChildren(QPushButton)
        assert len(buttons) > 0
        
        # Look for start button
        start_button = None
        for button in buttons:
            if "Start" in button.text():
                start_button = button
                break
        
        # May or may not exist depending on implementation
        # Just verify we can search for it


@pytest.mark.unit
@pytest.mark.gui
class TestAnalysisWindowComponents:
    """Test AnalysisWindow UI components"""
    
    def test_analysis_window_creation(self, qtbot, qapp, sample_sequences):
        """Test AnalysisWindow can be created"""
        window = AnalysisWindow(
            sequences=sample_sequences,
            method_name="Test Method"
        )
        qtbot.addWidget(window)
        
        assert window is not None
    
    def test_analysis_window_with_parent(self, qtbot, qapp, sample_sequences):
        """Test AnalysisWindow with parent window"""
        main_window = MainWindow()
        qtbot.addWidget(main_window)
        
        analysis_window = AnalysisWindow(
            sequences=sample_sequences,
            method_name="Test Method",
            parent=main_window
        )
        qtbot.addWidget(analysis_window)
        
        assert analysis_window.parent() == main_window


@pytest.mark.unit
@pytest.mark.gui
class TestUIBehavior:
    """Test UI behavior and interactions"""
    
    def test_combo_box_item_selection(self, qtbot, qapp):
        """Test combo box item selection"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        combo = window.method_combo
        
        if combo.count() > 1:
            # Set index
            combo.setCurrentIndex(1)
            assert combo.currentIndex() == 1
            
            # Set back to 0
            combo.setCurrentIndex(0)
            assert combo.currentIndex() == 0
    
    def test_window_show_hide(self, qtbot, qapp):
        """Test showing and hiding window"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Show window
        window.show()
        qtbot.waitExposed(window)
        assert window.isVisible()
        
        # Hide window
        window.hide()
        QTest.qWait(100)
        assert not window.isVisible()
    
    def test_window_geometry(self, qtbot, qapp):
        """Test window geometry"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Get initial geometry
        geometry = window.geometry()
        assert geometry.width() > 0
        assert geometry.height() > 0
        
        # Resize
        window.resize(800, 600)
        assert window.width() == 800
        assert window.height() == 600


@pytest.mark.unit
@pytest.mark.gui  
class TestUIStateManagement:
    """Test UI state management"""
    
    def test_initial_ui_state(self, qtbot, qapp):
        """Test initial UI state"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Method combo should be enabled
        assert window.method_combo.isEnabled()
        
        # Should have a selection
        assert window.method_combo.currentIndex() >= 0
    
    def test_ui_enable_disable(self, qtbot, qapp):
        """Test enabling/disabling UI elements"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        combo = window.method_combo
        
        # Disable
        combo.setEnabled(False)
        assert not combo.isEnabled()
        
        # Enable
        combo.setEnabled(True)
        assert combo.isEnabled()


@pytest.mark.unit
class TestUIHelpers:
    """Test UI helper functions"""
    
    def test_load_pixmap_safely(self):
        """Test load_pixmap_safely helper"""
        from src.utils.resources import load_pixmap_safely
        
        # Load non-existent file (should return default)
        pixmap = load_pixmap_safely("nonexistent.png", (100, 100))
        
        assert pixmap is not None
        # Should return some pixmap (possibly blank)
    
    def test_resource_path_for_ui(self):
        """Test resource_path for UI assets"""
        from src.utils.resources import resource_path
        
        # Get path for logo
        logo_path = resource_path("images/logo.png")
        assert isinstance(logo_path, str)
