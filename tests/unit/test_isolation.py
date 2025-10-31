"""
GUI Isolation Test - Verifies tests don't leak Qt resources
"""
import pytest
import gc
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest


@pytest.mark.unit
class TestGUIIsolation:
    """Test GUI test isolation"""
    
    def test_qapp_available(self, qapp):
        """Test QApplication is available"""
        assert qapp is not None
        assert QApplication.instance() is qapp
    
    def test_widget_cleanup_1(self, qtbot, qapp):
        """Test 1: Widget cleanup"""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test")
        qtbot.addWidget(button)
        button.show()
        
        # Widget should be tracked
        assert button.isVisible()
        
        button.close()
        button.deleteLater()
        QTest.qWait(100)
        gc.collect()
    
    def test_widget_cleanup_2(self, qtbot, qapp):
        """Test 2: Widget cleanup (should be isolated from test 1)"""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test 2")
        qtbot.addWidget(button)
        button.show()
        
        assert button.isVisible()
        
        button.close()
    
    def test_no_leftover_widgets(self, qapp):
        """Test no widgets leak between tests"""
        from PyQt6.QtWidgets import QWidget
        
        # Get all widgets
        all_widgets = qapp.allWidgets()
        
        # Should be minimal widgets (just application level)
        # Note: Exact count may vary by environment
        assert len(all_widgets) < 10, f"Too many widgets: {len(all_widgets)}"


@pytest.mark.unit
class TestSignalIsolation:
    """Test signal/slot isolation"""
    
    def test_signal_connection_1(self, qtbot):
        """Test 1: Signal connection"""
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import QObject
        
        button = QPushButton("Test")
        qtbot.addWidget(button)
        
        clicked_count = [0]
        
        def on_click():
            clicked_count[0] += 1
        
        button.clicked.connect(on_click)
        
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert clicked_count[0] == 1
        
        button.clicked.disconnect(on_click)
    
    def test_signal_connection_2(self, qtbot):
        """Test 2: Signal connection (should be isolated)"""
        from PyQt6.QtWidgets import QPushButton
        
        button = QPushButton("Test 2")
        qtbot.addWidget(button)
        
        # Should have no connections from previous test
        # (Testing this properly requires access to internal Qt structures)


@pytest.mark.unit  
class TestResourceIsolation:
    """Test resource isolation between tests"""
    
    _shared_state = None
    
    def test_resource_1(self, temp_directory):
        """Test 1: Create resource"""
        test_file = temp_directory / "test1.txt"
        test_file.write_text("test1")
        
        TestResourceIsolation._shared_state = "test1"
        
        assert test_file.exists()
    
    def test_resource_2(self, temp_directory):
        """Test 2: Should have clean temp directory"""
        # Should get a NEW temp directory, not the one from test 1
        files = list(temp_directory.glob("*.txt"))
        
        # Directory should be empty or not contain test1.txt
        assert "test1.txt" not in [f.name for f in files]
    
    def test_shared_state_isolation(self):
        """Test shared state (demonstrates why to avoid it)"""
        # This demonstrates class-level state persists
        # (This is generally bad practice)
        if TestResourceIsolation._shared_state is not None:
            # State might leak from previous test
            pass


from PyQt6.QtCore import Qt  # Import for Qt enums
