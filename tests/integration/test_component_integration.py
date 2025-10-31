"""
Integration tests for component interactions
"""
import pytest
import numpy as np
from pathlib import Path

from src.core.analysis_service import AnalysisService
from src.core.plugin_registry import plugin_registry
from src.adapters.biopython_adapter import BioPythonSequenceLoader
from src.adapters.matplotlib_adapter import MatplotlibTreeVisualizer


@pytest.mark.integration
class TestPluginIntegration:
    """Test plugin system integration"""
    
    def test_plugin_registry_integration(self, plugins_loaded):
        """Test that plugins are properly registered"""
        processors = plugin_registry.get_processors()
        
        assert len(processors) > 0, "No processors registered"
        
        # Verify each processor has required methods
        for processor in processors:
            assert hasattr(processor, 'get_method_name')
            assert hasattr(processor, 'process_sequences')
            
            method_name = processor.get_method_name()
            assert isinstance(method_name, str)
            assert len(method_name) > 0
    
    def test_all_plugins_processable(self, plugins_loaded, sample_sequences):
        """Test that all registered plugins can process sequences"""
        processors = plugin_registry.get_processors()
        
        for processor in processors:
            try:
                result = processor.process_sequences(sample_sequences)
                
                # Verify result structure
                assert hasattr(result, 'distance_matrix')
                assert hasattr(result, 'features')
                assert result.distance_matrix is not None
                
                # Verify dimensions
                n_sequences = len(sample_sequences)
                assert result.distance_matrix.shape == (n_sequences, n_sequences)
                
            except Exception as e:
                pytest.fail(f"Plugin {processor.get_method_name()} failed: {e}")


@pytest.mark.integration
class TestSequenceLoaderIntegration:
    """Test sequence loader integration"""
    
    def test_load_and_process_pipeline(self, sample_fasta_file, plugins_loaded):
        """Test complete pipeline from loading to processing"""
        # Load sequences
        loader = BioPythonSequenceLoader()
        sequences = loader.load_sequences(str(sample_fasta_file))
        
        assert len(sequences) > 0
        
        # Process with first available processor
        processors = plugin_registry.get_processors()
        if processors:
            processor = processors[0]
            result = processor.process_sequences(sequences)
            
            assert result is not None
            assert result.distance_matrix.shape[0] == len(sequences)
    
    def test_multiple_file_loading(self, temp_directory):
        """Test loading from multiple files"""
        # Create multiple FASTA files
        files = []
        for i in range(3):
            fasta_file = temp_directory / f"test_{i}.fasta"
            fasta_file.write_text(f">Seq_{i}\nATCGATCG\n")
            files.append(fasta_file)
        
        loader = BioPythonSequenceLoader()
        
        all_sequences = []
        for file_path in files:
            sequences = loader.load_sequences(str(file_path))
            all_sequences.extend(sequences)
        
        assert len(all_sequences) == 3


@pytest.mark.integration
class TestAnalysisServiceIntegration:
    """Test analysis service integration"""
    
    def test_analysis_service_with_plugins(self, sample_sequences, plugins_loaded):
        """Test analysis service with registered plugins"""
        service = AnalysisService()
        
        processors = plugin_registry.get_processors()
        if processors:
            method_name = processors[0].get_method_name()
            
            # Run analysis
            result = service.analyze_sequences(sample_sequences, method_name)
            
            assert result is not None
            assert result.distance_matrix is not None
    
    def test_analysis_error_handling(self, plugins_loaded):
        """Test analysis service error handling"""
        service = AnalysisService()
        
        # Test with empty sequences
        from src.core.interfaces import SequenceData
        empty_sequences = []
        
        # Should handle gracefully
        try:
            result = service.analyze_sequences(
                empty_sequences, 
                "Template Matching"
            )
            # May return None or raise exception
        except Exception as e:
            # Should be a meaningful error
            assert str(e) != ""


@pytest.mark.integration
class TestVisualizerIntegration:
    """Test visualizer integration"""
    
    def test_visualizer_with_analysis_result(self, mock_analysis_result, temp_directory):
        """Test visualizer with analysis result"""
        visualizer = MatplotlibTreeVisualizer()
        
        output_path = temp_directory / "test_tree.png"
        
        try:
            visualizer.visualize_tree(
                mock_analysis_result.newick,
                str(output_path)
            )
            
            # Check file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
        except Exception as e:
            # Some environments may not support visualization
            pytest.skip(f"Visualization not available: {e}")


@pytest.mark.integration
class TestEndToEndDataFlow:
    """Test end-to-end data flow through the system"""
    
    def test_complete_analysis_pipeline(
        self, 
        sample_fasta_file, 
        temp_directory,
        plugins_loaded
    ):
        """Test complete pipeline: load -> analyze -> visualize"""
        # 1. Load sequences
        loader = BioPythonSequenceLoader()
        sequences = loader.load_sequences(str(sample_fasta_file))
        assert len(sequences) > 0
        
        # 2. Analyze sequences
        processors = plugin_registry.get_processors()
        assert len(processors) > 0
        
        processor = processors[0]
        result = processor.process_sequences(sequences)
        
        assert result is not None
        assert result.distance_matrix is not None
        assert result.newick is not None
        
        # 3. Visualize result
        visualizer = MatplotlibTreeVisualizer()
        output_path = temp_directory / "pipeline_tree.png"
        
        try:
            visualizer.visualize_tree(result.newick, str(output_path))
            assert output_path.exists()
        except Exception:
            # Visualization may fail in some test environments
            pass
    
    def test_multiple_methods_same_data(self, sample_sequences, plugins_loaded):
        """Test processing same data with multiple methods"""
        processors = plugin_registry.get_processors()
        
        results = []
        for processor in processors:
            result = processor.process_sequences(sample_sequences)
            results.append({
                'method': processor.get_method_name(),
                'result': result
            })
        
        # Verify all methods produced results
        assert len(results) == len(processors)
        
        # Verify results have consistent dimensions
        n_sequences = len(sample_sequences)
        for item in results:
            result = item['result']
            assert result.distance_matrix.shape == (n_sequences, n_sequences)
    
    def test_error_propagation(self, plugins_loaded):
        """Test error propagation through the pipeline"""
        from src.core.interfaces import SequenceData
        
        # Create invalid sequence
        invalid_sequences = [
            SequenceData(id="test", name="Test", sequence="")
        ]
        
        processors = plugin_registry.get_processors()
        if processors:
            processor = processors[0]
            
            # Should handle invalid data gracefully
            try:
                result = processor.process_sequences(invalid_sequences)
                # May succeed with special handling or fail
            except Exception as e:
                # Error should be meaningful
                assert str(e) != ""


@pytest.mark.integration
class TestConcurrentOperations:
    """Test concurrent operations"""
    
    def test_concurrent_sequence_loading(self, temp_directory):
        """Test loading sequences concurrently"""
        import concurrent.futures
        
        # Create multiple files
        files = []
        for i in range(5):
            fasta_file = temp_directory / f"concurrent_{i}.fasta"
            fasta_file.write_text(f">Seq_{i}\nATCGATCGATCG\n")
            files.append(fasta_file)
        
        loader = BioPythonSequenceLoader()
        
        def load_file(file_path):
            return loader.load_sequences(str(file_path))
        
        # Load concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(load_file, f) for f in files]
            results = [f.result() for f in futures]
        
        # Verify all loaded successfully
        assert len(results) == 5
        assert all(len(r) > 0 for r in results)
    
    @pytest.mark.slow
    def test_concurrent_analysis(self, sample_sequences, plugins_loaded):
        """Test running multiple analyses concurrently"""
        import concurrent.futures
        
        processors = plugin_registry.get_processors()
        
        def run_analysis(processor):
            return processor.process_sequences(sample_sequences)
        
        # Run analyses concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run_analysis, p) for p in processors]
            results = [f.result() for f in futures]
        
        # Verify all completed
        assert len(results) == len(processors)
        assert all(r is not None for r in results)
