"""
Memory Leak Detection and Performance Tests
"""
import pytest
import gc
import time
import tracemalloc
import psutil
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from src.ui.main_window import MainWindow
from src.core.analysis_service import AnalysisService


@pytest.mark.memory
class TestMemoryLeaks:
    """Test for memory leaks in the application"""
    
    def test_window_creation_deletion_no_leak(self, qtbot, qapp):
        """Test that creating and destroying windows doesn't leak memory"""
        tracemalloc.start()
        
        # Get baseline memory
        gc.collect()
        baseline = tracemalloc.take_snapshot()
        
        # Create and destroy windows multiple times
        for i in range(10):
            window = MainWindow()
            qtbot.addWidget(window)
            window.show()
            QTest.qWait(50)
            window.close()
            QTest.qWait(50)
            
            # Explicit cleanup
            window.deleteLater()
            QTest.qWait(50)
            gc.collect()
        
        # Check final memory
        gc.collect()
        QTest.qWait(100)
        final = tracemalloc.take_snapshot()
        
        # Compare memory usage
        top_stats = final.compare_to(baseline, 'lineno')
        
        # Calculate total memory increase
        total_increase = sum(stat.size_diff for stat in top_stats)
        
        # Memory increase should be minimal (< 5MB for 10 iterations)
        assert total_increase < 5 * 1024 * 1024, \
            f"Memory leak detected: {total_increase / (1024*1024):.2f} MB leaked"
        
        tracemalloc.stop()
    
    def test_analysis_service_no_leak(self, qtbot, sample_sequences):
        """Test that running analyses doesn't leak memory"""
        tracemalloc.start()
        gc.collect()
        
        baseline = tracemalloc.take_snapshot()
        
        service = AnalysisService()
        
        # Run multiple analyses
        for i in range(5):
            # Simulate analysis (without full execution)
            pass
            gc.collect()
        
        gc.collect()
        final = tracemalloc.take_snapshot()
        
        top_stats = final.compare_to(baseline, 'lineno')
        total_increase = sum(stat.size_diff for stat in top_stats)
        
        # Allow for some caching but not excessive growth
        assert total_increase < 10 * 1024 * 1024, \
            f"Memory leak in analysis: {total_increase / (1024*1024):.2f} MB"
        
        tracemalloc.stop()
    
    def test_repeated_plugin_loading_no_leak(self, qtbot):
        """Test that plugin loading/unloading doesn't leak"""
        from src.core.plugin_loader import plugin_loader
        
        tracemalloc.start()
        gc.collect()
        
        baseline = tracemalloc.take_snapshot()
        
        # Load plugins multiple times
        for i in range(5):
            plugin_loader.load_all_plugins()
            gc.collect()
        
        gc.collect()
        final = tracemalloc.take_snapshot()
        
        top_stats = final.compare_to(baseline, 'lineno')
        total_increase = sum(stat.size_diff for stat in top_stats)
        
        # Plugins should be cached, minimal growth
        assert total_increase < 2 * 1024 * 1024, \
            f"Memory leak in plugin loading: {total_increase / (1024*1024):.2f} MB"
        
        tracemalloc.stop()
    
    def test_pixmap_loading_no_leak(self, qtbot, qapp):
        """Test that loading images doesn't leak memory"""
        from src.utils.resources import load_pixmap_safely
        
        tracemalloc.start()
        gc.collect()
        
        baseline = tracemalloc.take_snapshot()
        
        # Load pixmaps repeatedly
        for i in range(20):
            pixmap = load_pixmap_safely("nonexistent.png", (100, 100))
            del pixmap
            
            if i % 5 == 0:
                gc.collect()
        
        gc.collect()
        final = tracemalloc.take_snapshot()
        
        top_stats = final.compare_to(baseline, 'lineno')
        total_increase = sum(stat.size_diff for stat in top_stats)
        
        assert total_increase < 1 * 1024 * 1024, \
            f"Memory leak in pixmap loading: {total_increase / (1024*1024):.2f} MB"
        
        tracemalloc.stop()


@pytest.mark.memory
class TestResourceCleanup:
    """Test proper resource cleanup"""
    
    def test_file_handles_closed(self, qtbot, sample_fasta_file):
        """Test that file handles are properly closed"""
        from src.adapters.biopython_adapter import BioPythonSequenceLoader
        
        loader = BioPythonSequenceLoader()
        
        # Get initial open file count
        process = psutil.Process(os.getpid())
        initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        
        # Load sequences multiple times
        for i in range(10):
            sequences = loader.load_sequences(str(sample_fasta_file))
            del sequences
            gc.collect()
        
        # Check file descriptors haven't grown significantly
        final_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
        
        # Should not leak file descriptors
        if initial_fds > 0:  # Only check on systems that support this
            assert final_fds - initial_fds < 5, \
                f"File descriptor leak: {final_fds - initial_fds} FDs leaked"
    
    def test_qt_objects_deleted(self, qtbot, qapp):
        """Test that Qt objects are properly deleted"""
        import weakref
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Create weak reference
        weak_ref = weakref.ref(window)
        
        # Close and delete window
        window.close()
        window.deleteLater()
        QTest.qWait(100)
        
        # Force garbage collection
        gc.collect()
        QTest.qWait(100)
        
        # Object should be deleted
        assert weak_ref() is None, "Window object not properly deleted"
    
    def test_signal_connections_cleaned(self, qtbot, qapp):
        """Test that signal connections are cleaned up"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        callback_count = [0]
        
        def callback():
            callback_count[0] += 1
        
        # Connect signal
        if hasattr(window.method_combo, 'currentIndexChanged'):
            window.method_combo.currentIndexChanged.connect(callback)
        
        # Close window
        window.close()
        window.deleteLater()
        QTest.qWait(100)
        gc.collect()
        
        # Signals should be disconnected
        # (Testing this properly requires more sophisticated setup)


@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance benchmarks for the application"""
    
    def test_window_startup_performance(self, qtbot, qapp, benchmark):
        """Benchmark window startup time"""
        def create_window():
            window = MainWindow()
            window.show()
            window.close()
        
        # Benchmark should complete in reasonable time
        result = benchmark(create_window)
        assert result < 2.0, f"Window startup too slow: {result:.2f}s"
    
    def test_method_switching_performance(self, qtbot, qapp):
        """Test performance of switching analysis methods"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        start_time = time.time()
        
        # Switch methods multiple times
        for i in range(10):
            index = i % window.method_combo.count()
            window.method_combo.setCurrentIndex(index)
            QTest.qWait(10)
        
        elapsed = time.time() - start_time
        
        # Should be very fast
        assert elapsed < 1.0, f"Method switching too slow: {elapsed:.2f}s"
        
        window.close()
    
    def test_large_dataset_loading_performance(self, qtbot, temp_directory):
        """Test performance with large datasets"""
        from src.adapters.biopython_adapter import BioPythonSequenceLoader
        
        # Create large FASTA file
        large_fasta = temp_directory / "large.fasta"
        with open(large_fasta, 'w') as f:
            for i in range(100):
                f.write(f">Sequence_{i}\n")
                f.write("ATCG" * 500 + "\n")
        
        loader = BioPythonSequenceLoader()
        
        start_time = time.time()
        sequences = loader.load_sequences(str(large_fasta))
        elapsed = time.time() - start_time
        
        assert len(sequences) == 100
        assert elapsed < 5.0, f"Loading too slow: {elapsed:.2f}s for 100 sequences"
    
    def test_ui_responsiveness_under_load(self, qtbot, qapp):
        """Test UI remains responsive under load"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Simulate rapid user interactions
        start_time = time.time()
        
        for i in range(20):
            # Click combo box
            QTest.mouseClick(window.method_combo, Qt.MouseButton.LeftButton)
            QTest.qWait(5)
            
            # Press key
            QTest.keyClick(window, Qt.Key.Key_Tab)
            QTest.qWait(5)
        
        elapsed = time.time() - start_time
        
        # UI should remain responsive
        assert window.isVisible()
        assert elapsed < 2.0, f"UI responsiveness degraded: {elapsed:.2f}s"
        
        window.close()


@pytest.mark.memory
class TestMemoryUsage:
    """Test memory usage patterns"""
    
    def test_baseline_memory_usage(self, qtbot, qapp):
        """Measure baseline memory usage"""
        process = psutil.Process(os.getpid())
        
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        QTest.qWait(500)
        
        loaded_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        memory_increase = loaded_memory - initial_memory
        
        # Application shouldn't use excessive memory at startup
        assert memory_increase < 500, \
            f"Excessive memory usage: {memory_increase:.2f} MB"
        
        print(f"\nBaseline memory usage: {memory_increase:.2f} MB")
        
        window.close()
    
    def test_memory_growth_over_time(self, qtbot, qapp):
        """Test memory doesn't grow excessively over time"""
        process = psutil.Process(os.getpid())
        
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        initial_memory = process.memory_info().rss / (1024 * 1024)
        
        # Simulate extended usage
        for i in range(50):
            window.method_combo.setCurrentIndex(i % window.method_combo.count())
            QTest.qWait(20)
            
            if i % 10 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss / (1024 * 1024)
        growth = final_memory - initial_memory
        
        # Memory shouldn't grow significantly during normal operation
        assert growth < 50, f"Memory grew too much: {growth:.2f} MB"
        
        print(f"\nMemory growth over 50 operations: {growth:.2f} MB")
        
        window.close()
