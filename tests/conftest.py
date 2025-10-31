"""
Pytest configuration and shared fixtures for all tests
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Import application components
from src.core.plugin_registry import plugin_registry
from src.core.plugin_loader import plugin_loader
from src.adapters.biopython_adapter import BioPythonSequenceLoader


# Fixtures for PyQt Application
@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """
    Create a QApplication instance for the entire test session.
    This is crucial for PyQt testing - must be session-scoped.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Clean up at end of session
    app.quit()


@pytest.fixture(scope="function")
def qapp_isolated(qtbot):
    """
    Provides an isolated QApplication for tests that need complete isolation.
    Use this for tests that modify global application state.
    """
    # qtbot fixture from pytest-qt handles the app lifecycle
    return QApplication.instance()


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_fasta_file(temp_directory: Path) -> Path:
    """Create a sample FASTA file for testing"""
    fasta_content = """>Sample_Sequence_1
ATCGATCGATCGATCG
>Sample_Sequence_2
GCTAGCTAGCTAGCTA
>Sample_Sequence_3
TTAATTAATTAATTAA
"""
    fasta_path = temp_directory / "test_sequences.fasta"
    fasta_path.write_text(fasta_content)
    return fasta_path


@pytest.fixture
def sample_sequences():
    """Provide sample DNA sequences for testing"""
    from src.core.interfaces import SequenceData
    
    sequences = [
        SequenceData(name="Sequence 1", sequence="ATCGATCGATCG" * 10),
        SequenceData(name="Sequence 2", sequence="GCTAGCTAGCTA" * 10),
        SequenceData(name="Sequence 3", sequence="TTAATTAATTAA" * 10),
    ]
    return sequences


@pytest.fixture(scope="session")
def plugins_loaded():
    """Load all plugins once for the session"""
    plugin_loader.load_all_plugins()
    return plugin_registry


@pytest.fixture(autouse=True)
def reset_plugin_state():
    """Reset plugin state before each test to ensure isolation"""
    # Yield to run the test
    yield
    # Cleanup after test
    # Note: We don't clear the registry as it's expensive to reload


@pytest.fixture
def mock_analysis_result():
    """Provide a mock analysis result"""
    import numpy as np
    from src.core.interfaces import AnalysisResult
    
    distance_matrix = np.random.rand(5, 5)
    # Make it symmetric
    distance_matrix = (distance_matrix + distance_matrix.T) / 2
    np.fill_diagonal(distance_matrix, 0)
    
    return AnalysisResult(
        tree=None,
        distance_matrix=distance_matrix,
        sequence_names=["seq1", "seq2", "seq3", "seq4", "seq5"],
        newick="((seq1:0.1,seq2:0.2):0.3,(seq3:0.15,seq4:0.25):0.35,seq5:0.4);",
        metadata={"method": "Test Method", "execution_time": 1.5}
    )


# Memory tracking fixtures
@pytest.fixture
def memory_tracker():
    """Track memory usage during tests"""
    import tracemalloc
    
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()
    
    yield
    
    snapshot_after = tracemalloc.take_snapshot()
    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    
    # Log top 10 memory allocations
    print("\n[ Top 10 Memory Allocations ]")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()


# Resource cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_resources():
    """Ensure resources are cleaned up after each test"""
    yield
    # Force garbage collection
    import gc
    gc.collect()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "memory: Memory leak tests")
    config.addinivalue_line("markers", "gui: GUI-related tests")
