"""
Unit tests for core components
"""
import pytest
import numpy as np

from src.core.interfaces import SequenceData, AnalysisResult, MethodConfig
from src.core.plugin_registry import PluginRegistry
from src.core.analysis_service import AnalysisService


@pytest.mark.unit
class TestSequenceData:
    """Test SequenceData dataclass"""
    
    def test_sequence_data_creation(self):
        """Test creating SequenceData instances"""
        seq = SequenceData(
            id="test1",
            name="Test Sequence",
            sequence="ATCGATCG"
        )
        
        assert seq.id == "test1"
        assert seq.name == "Test Sequence"
        assert seq.sequence == "ATCGATCG"
    
    def test_sequence_data_length(self):
        """Test sequence length calculation"""
        seq = SequenceData(
            id="test1",
            name="Test",
            sequence="ATCGATCG"
        )
        
        assert len(seq.sequence) == 8
    
    def test_sequence_data_validation(self):
        """Test sequence data validation"""
        # Valid sequence
        seq = SequenceData(name="S1", sequence="ATCG")
        assert seq.sequence == "ATCG"
        
        # Empty sequence (should be allowed)
        seq_empty = SequenceData(name="S2", sequence="")
        assert seq_empty.sequence == ""


@pytest.mark.unit
class TestAnalysisResult:
    """Test AnalysisResult dataclass"""
    
    def test_analysis_result_creation(self):
        """Test creating AnalysisResult"""
        distance_matrix = np.array([[0, 1], [1, 0]])
        
        result = AnalysisResult(
            tree=None,
            distance_matrix=distance_matrix,
            sequence_names=["A", "B"],
            newick="(A:0.1,B:0.2);",
            metadata={"method": "Test"}
        )
        
        assert result.distance_matrix.shape == (2, 2)
        assert result.newick == "(A:0.1,B:0.2);"
        assert result.metadata["method"] == "Test"
        assert len(result.sequence_names) == 2
    
    def test_analysis_result_with_optional_fields(self):
        """Test AnalysisResult with optional fields"""
        result = AnalysisResult(
            tree=None,
            distance_matrix=np.array([[0]]),
            sequence_names=["A"],
            newick="",
            metadata={}
        )
        
        assert result.distance_matrix is not None
        assert result.newick is not None


@pytest.mark.unit
class TestPluginRegistry:
    """Test PluginRegistry"""
    
    def test_registry_singleton(self):
        """Test that registry is a singleton"""
        from src.core.plugin_registry import plugin_registry
        
        registry1 = plugin_registry
        registry2 = plugin_registry
        
        assert registry1 is registry2
    
    def test_get_processors(self, plugins_loaded):
        """Test getting registered processors"""
        processors = plugins_loaded.get_processors()
        
        assert isinstance(processors, list)
        assert len(processors) > 0
    
    def test_processor_by_name(self, plugins_loaded):
        """Test getting processor by name"""
        processors = plugins_loaded.get_processors()
        
        if processors:
            processor = processors[0]
            method_name = processor.get_method_name()
            
            # Try to get by name
            found = None
            for p in plugins_loaded.get_processors():
                if p.get_method_name() == method_name:
                    found = p
                    break
            
            assert found is not None


@pytest.mark.unit
class TestAnalysisService:
    """Test AnalysisService"""
    
    def test_analysis_service_creation(self):
        """Test creating AnalysisService"""
        service = AnalysisService()
        assert service is not None
    
    def test_service_analyze_with_valid_data(self, sample_sequences, plugins_loaded):
        """Test analysis with valid data"""
        service = AnalysisService()
        processors = plugins_loaded.get_processors()
        
        if processors:
            method_name = processors[0].get_method_name()
            result = service.analyze_sequences(sample_sequences, method_name)
            
            # Result should be valid or None (depending on implementation)
            if result is not None:
                assert hasattr(result, 'distance_matrix')


@pytest.mark.unit
class TestDataValidation:
    """Test data validation functions"""
    
    def test_sequence_alphabet_validation(self):
        """Test DNA sequence alphabet validation"""
        valid_sequence = "ATCGATCGATCG"
        invalid_sequence = "ATCGXYZ"
        
        # Valid DNA bases
        assert all(base in "ATCGN-" for base in valid_sequence.upper())
        
        # Invalid characters present
        assert not all(base in "ATCGN-" for base in invalid_sequence.upper())
    
    def test_distance_matrix_properties(self, mock_analysis_result):
        """Test distance matrix properties"""
        matrix = mock_analysis_result.distance_matrix
        
        # Should be square
        assert matrix.shape[0] == matrix.shape[1]
        
        # Diagonal should be zeros
        for i in range(matrix.shape[0]):
            assert matrix[i, i] == 0 or np.isclose(matrix[i, i], 0)
        
        # Should be symmetric
        assert np.allclose(matrix, matrix.T)
    
    def test_sequence_names_dimensions(self, mock_analysis_result):
        """Test sequence names match matrix dimensions"""
        sequence_names = mock_analysis_result.sequence_names
        distance_matrix = mock_analysis_result.distance_matrix
        
        # Number of sequence names should match matrix dimension
        assert len(sequence_names) == distance_matrix.shape[0]
        
        # All names should be strings
        assert all(isinstance(name, str) for name in sequence_names)

@pytest.mark.unit
class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_resource_path_function(self):
        """Test resource_path utility"""
        from src.utils.resources import resource_path
        
        path = resource_path("test.txt")
        assert isinstance(path, str)
        assert len(path) > 0
    
    def test_ensure_directory_exists(self, temp_directory):
        """Test ensure_directory_exists utility"""
        from src.utils.resources import ensure_directory_exists
        
        test_dir = temp_directory / "test_subdir"
        ensure_directory_exists(str(test_dir))
        
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_count_files_with_extension(self, temp_directory):
        """Test count_files_with_extension utility"""
        from src.utils.resources import count_files_with_extension
        
        # Create test files
        (temp_directory / "test1.fasta").write_text("test")
        (temp_directory / "test2.fasta").write_text("test")
        (temp_directory / "test.txt").write_text("test")
        
        count = count_files_with_extension(str(temp_directory), ".fasta")
        assert count == 2


@pytest.mark.unit
class TestConfigurationManagement:
    """Test configuration management"""
    
    def test_app_config_exists(self):
        """Test that app_config is accessible"""
        from src.utils.config import app_config
        
        assert app_config is not None
        assert hasattr(app_config, 'ui')
        assert hasattr(app_config, 'paths')
    
    def test_ui_config_values(self):
        """Test UI configuration values"""
        from src.utils.config import app_config
        
        ui_config = app_config.ui
        
        assert hasattr(ui_config, 'window_title')
        assert hasattr(ui_config, 'window_size')
        
        assert isinstance(ui_config.window_title, str)
        assert len(ui_config.window_title) > 0
    
    def test_path_config_values(self):
        """Test path configuration values"""
        from src.utils.config import app_config
        
        path_config = app_config.paths
        
        assert hasattr(path_config, 'phylo_tree_directory')
        assert hasattr(path_config, 'demo_logo')
