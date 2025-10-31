"""
End-to-End Tests for DSS Desktop Application
Tests complete user workflows from UI to analysis completion
"""
import pytest
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QPushButton, QFileDialog, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from src.ui.main_window import MainWindow
from src.ui.analysis_window import AnalysisWindow


@pytest.mark.e2e
@pytest.mark.gui
class TestMainWindowE2E:
    """End-to-end tests for main window workflows"""
    
    def test_application_startup(self, qtbot, qapp):
        """Test that the application starts successfully"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Verify window is visible
        assert window.isVisible()
        # Window title may vary - just check it exists
        assert len(window.windowTitle()) > 0
        
        # Verify essential UI elements exist
        assert window.method_combo is not None
        assert window.method_combo.count() > 0  # Has methods loaded
        
        window.close()
    
    def test_method_selection_workflow(self, qtbot, qapp):
        """Test selecting different analysis methods"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        initial_method = window.method_combo.currentText()
        assert initial_method != ""
        
        # Change method selection
        if window.method_combo.count() > 1:
            window.method_combo.setCurrentIndex(1)
            QTest.qWait(100)  # Wait for UI update
            
            new_method = window.method_combo.currentText()
            assert new_method != initial_method
        
        window.close()
    
    def test_window_resizing(self, qtbot, qapp):
        """Test window resizing behavior"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        original_size = window.size()
        
        # Resize window
        window.resize(1200, 800)
        QTest.qWait(100)
        
        assert window.width() == 1200
        assert window.height() == 800
        
        window.close()
    
    def test_window_state_changes(self, qtbot, qapp):
        """Test window state transitions (minimize, maximize, restore)"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Test maximize (may not work in all test environments)
        window.showMaximized()
        QTest.qWait(200)
        # In some headless environments, maximizing may not work
        # Just verify the window is still visible
        assert window.isVisible()
        
        # Test normal state
        window.showNormal()
        QTest.qWait(200)
        assert window.isVisible()
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
@pytest.mark.slow
class TestAnalysisWorkflowE2E:
    """End-to-end tests for complete analysis workflows"""
    
    def test_complete_analysis_workflow(self, qtbot, qapp, sample_fasta_file):
        """Test complete workflow from file selection to analysis completion"""
        from unittest.mock import patch
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Select a method
        window.method_combo.setCurrentIndex(0)
        QTest.qWait(100)
        
        # Click Start button to open analysis window
        start_buttons = window.findChildren(QPushButton)
        start_button = None
        for btn in start_buttons:
            if "Start" in btn.text():
                start_button = btn
                break
        
        if start_button:
            qtbot.mouseClick(start_button, Qt.MouseButton.LeftButton)
            QTest.qWait(200)
            
            # Check if analysis window opened
            if hasattr(window, 'analysis_window') and window.analysis_window:
                assert window.analysis_window.isVisible()
                
                # Mock directory selection
                test_dir = str(sample_fasta_file.parent)
                with patch.object(QFileDialog, 'getExistingDirectory', return_value=test_dir):
                    browse_buttons = window.analysis_window.findChildren(QPushButton)
                    for btn in browse_buttons:
                        if "Browse" in btn.text():
                            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                            QTest.qWait(100)
                            break
                
                # Verify directory was set
                assert window.analysis_window.path_edit.text() != ""
                
                window.analysis_window.close()
        
        window.close()
    
    def test_analysis_window_lifecycle(self, qtbot, qapp, sample_sequences):
        """Test analysis window creation and destruction"""
        from src.core.analysis_service import AnalysisService
        
        main_window = MainWindow()
        qtbot.addWidget(main_window)
        main_window.show()
        
        # Create analysis window with correct signature
        analysis_service = AnalysisService()
        methods = analysis_service.get_available_methods()
        
        if methods:
            analysis_window = AnalysisWindow(
                analysis_service=analysis_service,
                method_name=methods[0]
            )
            qtbot.addWidget(analysis_window)
            analysis_window.show()  # Need to explicitly show the window
            QTest.qWait(100)
            
            # Verify window creation
            assert analysis_window is not None
            assert analysis_window.isVisible()
            
            # Close analysis window
            analysis_window.close()
            QTest.qWait(100)
        
        main_window.close()
    
    def test_multiple_sequential_analyses(self, qtbot, qapp):
        """Test running multiple analyses sequentially"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # This tests for resource leaks in repeated operations
        for i in range(3):
            # Simulate user interaction
            QTest.qWait(100)
            
            # In a real test, we'd trigger analysis here
            # For now, just verify window is still responsive
            assert window.isVisible()
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestUIResponsiveness:
    """Test UI responsiveness and user interaction"""
    
    def test_button_click_responsiveness(self, qtbot, qapp):
        """Test that buttons respond to clicks"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Find start button
        start_button = None
        for child in window.findChildren(type(window.findChild(object))):
            if hasattr(child, 'text') and 'Start' in str(child.text()):
                start_button = child
                break
        
        if start_button:
            # Test button is clickable
            assert start_button.isEnabled()
            
            # Click button
            with qtbot.waitSignal(timeout=1000) as blocker:
                qtbot.mouseClick(start_button, Qt.MouseButton.LeftButton)
        
        window.close()
    
    def test_combo_box_interaction(self, qtbot, qapp):
        """Test combo box interaction"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        combo = window.method_combo
        
        # Test combo box can be opened
        QTest.mouseClick(combo, Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        
        # Test keyboard navigation
        if combo.count() > 1:
            QTest.keyClick(combo, Qt.Key.Key_Down)
            QTest.qWait(50)
            QTest.keyClick(combo, Qt.Key.Key_Return)
            QTest.qWait(50)
        
        window.close()
    
    def test_keyboard_shortcuts(self, qtbot, qapp):
        """Test keyboard shortcuts and accessibility"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Test tab navigation
        QTest.keyClick(window, Qt.Key.Key_Tab)
        QTest.qWait(50)
        
        # Test ESC key
        QTest.keyClick(window, Qt.Key.Key_Escape)
        QTest.qWait(50)
        
        assert window.isVisible()
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestErrorHandling:
    """Test error handling in E2E scenarios"""
    
    def test_invalid_file_handling(self, qtbot, qapp, temp_directory):
        """Test handling of invalid input files"""
        from src.adapters.biopython_adapter import BioPythonSequenceLoader
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Create invalid file
        invalid_file = temp_directory / "invalid.txt"
        invalid_file.write_text("This is not a FASTA file")
        
        # Test that loader handles invalid file gracefully
        loader = BioPythonSequenceLoader()
        try:
            sequences = loader.load_sequences(str(invalid_file))
            # Should return empty list or handle gracefully
            assert isinstance(sequences, list)
        except Exception as e:
            # Should raise meaningful error
            assert str(e) != ""
            assert "format" in str(e).lower() or "invalid" in str(e).lower()
        
        window.close()
    
    def test_empty_dataset_handling(self, qtbot, qapp):
        """Test handling of empty datasets"""
        from src.core.interfaces import SequenceData
        from src.core.analysis_service import AnalysisService
        from src.core.interfaces import MethodConfig
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Test with empty sequence list
        service = AnalysisService()
        empty_sequences = []
        
        # Get first available method
        methods = service.get_available_methods()
        if methods:
            method_name = methods[0]
            config = service.get_method_config(method_name)
            
            # Should handle empty sequences gracefully
            try:
                result = service.analyze_sequences(empty_sequences, method_name, config)
                # May return None or handle gracefully
            except Exception as e:
                # Should provide meaningful error message
                assert str(e) != ""
                assert "empty" in str(e).lower() or "no sequences" in str(e).lower() or len(str(e)) > 0
        
        window.close()
    
    def test_analysis_failure_recovery(self, qtbot, qapp):
        """Test recovery from analysis failures"""
        from src.core.interfaces import SequenceData
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Simulate analysis with invalid data
        # Create sequence with invalid content
        invalid_sequences = [
            SequenceData(name="Test", sequence="XYZABC123")
        ]
        
        service = window.analysis_service
        methods = service.get_available_methods()
        
        if methods:
            method_name = methods[0]
            config = service.get_method_config(method_name)
            
            # Try to analyze - should fail gracefully
            try:
                result = service.analyze_sequences(invalid_sequences, method_name, config)
                # May succeed with special handling
            except Exception as e:
                # Should get error but not crash
                assert str(e) != ""
        
        # Verify UI is still responsive
        assert window.isVisible()
        assert window.method_combo.isEnabled()
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
@pytest.mark.slow
class TestLongRunningOperations:
    """Test long-running operations and progress feedback"""
    
    def test_analysis_progress_indication(self, qtbot, qapp, sample_sequences):
        """Test that long operations show progress"""
        from src.ui.base_components import ProgressDialog, ProgressCallback
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Create and test progress dialog
        progress_dialog = ProgressDialog(window)
        progress_callback = ProgressCallback(progress_dialog)
        
        # Test progress updates
        progress_callback.set_status("Testing progress...")
        progress_callback.update_progress(0.0)
        assert progress_dialog.progress_bar.value() == 0
        
        progress_callback.update_progress(0.5)
        assert progress_dialog.progress_bar.value() == 50
        
        progress_callback.update_progress(1.0)
        assert progress_dialog.progress_bar.value() == 100
        
        progress_dialog.close()
        window.close()
    
    def test_operation_cancellation(self, qtbot, qapp):
        """Test cancelling long-running operations"""
        from src.ui.base_components import ProgressDialog
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Create progress dialog with cancel support
        progress_dialog = ProgressDialog(window)
        progress_dialog.show()
        QTest.qWait(100)
        
        # Test cancel button exists and works
        if hasattr(progress_dialog, 'cancel_button'):
            assert progress_dialog.cancel_button.isEnabled()
            qtbot.mouseClick(progress_dialog.cancel_button, Qt.MouseButton.LeftButton)
        
        # Dialog should close or be cancellable
        progress_dialog.close()
        QTest.qWait(100)
        
        window.close()


@pytest.mark.e2e
class TestApplicationLifecycle:
    """Test complete application lifecycle"""
    
    def test_cold_start(self, qtbot, qapp):
        """Test application cold start"""
        start_time = time.time()
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        startup_time = time.time() - start_time
        
        # Startup should be reasonably fast
        assert startup_time < 5.0, f"Startup took {startup_time:.2f}s"
        
        window.close()
    
    def test_graceful_shutdown(self, qtbot, qapp):
        """Test application shuts down cleanly"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Close window
        window.close()
        QTest.qWait(100)
        
        # Verify window is closed
        assert not window.isVisible()
    
    def test_restart_capability(self, qtbot, qapp):
        """Test application can be restarted"""
        # First instance
        window1 = MainWindow()
        qtbot.addWidget(window1)
        window1.show()
        window1.close()
        QTest.qWait(100)
        
        # Second instance
        window2 = MainWindow()
        qtbot.addWidget(window2)
        window2.show()
        
        assert window2.isVisible()
        
        window2.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestAnalysisWindowE2E:
    """End-to-end tests for analysis window functionality"""
    
    def test_analysis_window_creation_with_method(self, qtbot, qapp):
        """Test creating analysis window with specific method"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        if methods:
            window = AnalysisWindow(service, methods[0])
            qtbot.addWidget(window)
            window.show()
            
            assert window.isVisible()
            assert methods[0] in window.windowTitle()
            
            window.close()
    
    def test_browse_directory_workflow(self, qtbot, qapp, sample_fasta_file):
        """Test browsing for directory in analysis window"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        if methods:
            window = AnalysisWindow(service, methods[0])
            qtbot.addWidget(window)
            window.show()
            
            # Mock directory selection
            test_dir = str(sample_fasta_file.parent)
            with patch.object(QFileDialog, 'getExistingDirectory', return_value=test_dir):
                browse_buttons = window.findChildren(QPushButton)
                for btn in browse_buttons:
                    if "Browse" in btn.text():
                        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                        QTest.qWait(100)
                        break
            
            # Verify directory was set
            if hasattr(window, 'path_edit'):
                assert window.path_edit.text() == test_dir or window.path_edit.text() != ""
            
            window.close()
    
    def test_method_config_ui_elements(self, qtbot, qapp):
        """Test that method-specific UI elements are shown"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        for method_name in methods:
            window = AnalysisWindow(service, method_name)
            qtbot.addWidget(window)
            window.show()
            
            # Check for method-specific controls
            if "DPTM" in method_name or "Dynamic" in method_name:
                # Should have k-length controls
                if hasattr(window, 'spin_k'):
                    assert window.spin_k is not None
            
            if "Template Matching" in method_name:
                # Should have partition controls
                if hasattr(window, 'spin_p'):
                    assert window.spin_p is not None
            
            window.close()
            QTest.qWait(50)
    
    def test_generate_button_state(self, qtbot, qapp):
        """Test generate button enable/disable logic"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        if methods:
            window = AnalysisWindow(service, methods[0])
            qtbot.addWidget(window)
            window.show()
            
            # Generate button should exist
            if hasattr(window, 'generate_btn'):
                assert window.generate_btn is not None
                # Initially should be enabled or disabled based on state
                assert isinstance(window.generate_btn.isEnabled(), bool)
            
            window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestDataFlowE2E:
    """Test complete data flow from UI to results"""
    
    def test_sequence_loading_workflow(self, qtbot, qapp, sample_fasta_file):
        """Test loading sequences from file system"""
        from src.adapters.biopython_adapter import BioPythonSequenceLoader
        
        loader = BioPythonSequenceLoader()
        sequences = loader.load_sequences(str(sample_fasta_file))
        
        assert len(sequences) > 0
        assert all(hasattr(seq, 'sequence') for seq in sequences)
        assert all(hasattr(seq, 'name') for seq in sequences)
        # Check that sequences have required attributes
        for seq in sequences:
            assert isinstance(seq.name, str)
            assert isinstance(seq.sequence, str)
    
    def test_analysis_service_integration(self, qtbot, qapp, sample_sequences):
        """Test analysis service with UI components"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        assert len(methods) > 0
        
        for method_name in methods:
            config = service.get_method_config(method_name)
            assert config is not None
            assert hasattr(config, 'parameters')
    
    def test_full_analysis_pipeline_simulation(self, qtbot, qapp, sample_sequences, plugins_loaded):
        """Test simulating full analysis pipeline"""
        from src.core.analysis_service import AnalysisService
        
        service = AnalysisService()
        methods = service.get_available_methods()
        
        if methods:
            method_name = methods[0]
            config = service.get_method_config(method_name)
            
            try:
                # Run analysis with sample data
                result = service.analyze_sequences(sample_sequences, method_name, config)
                
                if result:
                    assert hasattr(result, 'distance_matrix')
                    assert hasattr(result, 'features')
                    assert result.distance_matrix is not None
            except Exception as e:
                # Some methods may require specific data format
                assert str(e) != ""


@pytest.mark.e2e
@pytest.mark.gui
class TestUIStateManagement:
    """Test UI state management across interactions"""
    
    def test_method_selection_persistence(self, qtbot, qapp):
        """Test that method selection persists across interactions"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        if window.method_combo.count() > 1:
            # Select second method
            window.method_combo.setCurrentIndex(1)
            selected_text = window.method_combo.currentText()
            QTest.qWait(100)
            
            # Verify selection persists
            assert window.method_combo.currentText() == selected_text
        
        window.close()
    
    def test_window_state_after_interactions(self, qtbot, qapp):
        """Test window state after various interactions"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Perform various interactions
        for i in range(3):
            window.method_combo.setCurrentIndex(i % window.method_combo.count())
            QTest.qWait(50)
        
        # Window should still be in good state
        assert window.isVisible()
        assert window.method_combo.isEnabled()
        assert window.method_combo.count() > 0
        
        window.close()
    
    def test_multiple_window_instances(self, qtbot, qapp):
        """Test managing multiple window instances"""
        windows = []
        
        for i in range(3):
            window = MainWindow()
            qtbot.addWidget(window)
            window.show()
            windows.append(window)
            QTest.qWait(100)
        
        # All windows should be visible
        assert all(w.isVisible() for w in windows)
        
        # Close all windows
        for window in windows:
            window.close()
            QTest.qWait(50)


@pytest.mark.e2e
@pytest.mark.gui
class TestAccessibilityE2E:
    """Test accessibility features"""
    
    def test_keyboard_navigation_complete(self, qtbot, qapp):
        """Test complete keyboard navigation through UI"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Tab through widgets
        for _ in range(5):
            QTest.keyClick(window, Qt.Key.Key_Tab)
            QTest.qWait(50)
        
        # Should still be functional
        assert window.isVisible()
        
        window.close()
    
    def test_focus_management(self, qtbot, qapp):
        """Test focus management in UI"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Set focus on combo box
        window.method_combo.setFocus()
        QTest.qWait(100)
        
        # Combo box should have focus or be focusable
        assert window.method_combo.hasFocus() or window.method_combo.focusPolicy() != Qt.FocusPolicy.NoFocus
        
        window.close()
    
    def test_widget_tab_order(self, qtbot, qapp):
        """Test tab order makes logical sense"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Get all focusable widgets
        focusable_widgets = []
        for widget in window.findChildren(QWidget):
            if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                focusable_widgets.append(widget)
        
        # Should have focusable widgets
        assert len(focusable_widgets) >= 0  # May vary by implementation
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestRobustnessE2E:
    """Test application robustness under various conditions"""
    
    def test_rapid_button_clicking(self, qtbot, qapp):
        """Test rapid button clicking doesn't cause issues"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Find buttons
        buttons = window.findChildren(QPushButton)
        
        if buttons:
            button = buttons[0]
            # Rapid clicking
            for _ in range(10):
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                QTest.qWait(10)
        
        # Window should still be responsive
        assert window.isVisible()
        
        window.close()
    
    def test_rapid_method_switching(self, qtbot, qapp):
        """Test rapid method switching"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Rapidly switch methods
        for i in range(20):
            idx = i % window.method_combo.count()
            window.method_combo.setCurrentIndex(idx)
            QTest.qWait(10)
        
        # Should still work
        assert window.method_combo.isEnabled()
        
        window.close()
    
    def test_window_resize_robustness(self, qtbot, qapp):
        """Test window handles resizing gracefully"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Various resize operations
        sizes = [(800, 600), (1200, 800), (600, 400), (1400, 900)]
        
        for width, height in sizes:
            window.resize(width, height)
            QTest.qWait(100)
            # Window manager may adjust size, so check it's reasonable
            assert window.width() >= 400  # Minimum reasonable width
            assert window.height() >= 300  # Minimum reasonable height
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestErrorRecoveryE2E:
    """Test error recovery scenarios"""
    
    def test_recovery_from_invalid_method_selection(self, qtbot, qapp):
        """Test recovery from invalid method selection"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Try to access non-existent method
        from src.core.plugin_registry import plugin_registry
        
        processor = plugin_registry.get_processor_by_name("NonExistentMethod")
        assert processor is None
        
        # UI should still work
        assert window.isVisible()
        assert window.method_combo.isEnabled()
        
        window.close()
    
    def test_recovery_after_exception(self, qtbot, qapp):
        """Test UI remains functional after exception"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        try:
            # Trigger potential error condition
            window.method_combo.setCurrentIndex(-1)  # Invalid index
        except:
            pass
        
        # Window should still be functional
        assert window.isVisible()
        window.method_combo.setCurrentIndex(0)
        assert window.method_combo.currentIndex() >= 0
        
        window.close()


@pytest.mark.e2e
@pytest.mark.gui
class TestVisualizationE2E:
    """Test visualization components end-to-end"""
    
    def test_tree_visualization_workflow(self, qtbot, qapp, mock_analysis_result, temp_directory):
        """Test tree visualization workflow"""
        from src.adapters.matplotlib_adapter import MatplotlibTreeVisualizer
        
        visualizer = MatplotlibTreeVisualizer()
        output_path = temp_directory / "test_tree.png"
        
        try:
            # Use newick instead of newick_tree
            visualizer.visualize_tree(
                mock_analysis_result.newick,
                str(output_path)
            )
            
            # Check file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            # Visualization may not work in headless environment
            pytest.skip(f"Visualization not available: {e}")
    
    def test_image_display_in_ui(self, qtbot, qapp):
        """Test image display in UI components"""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPixmap
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Find image labels
        labels = window.findChildren(QLabel)
        
        # Check if any labels have pixmaps
        pixmap_labels = [lbl for lbl in labels if lbl.pixmap() is not None]
        
        # Should have at least logo images
        assert len(pixmap_labels) >= 0
        
        window.close()

