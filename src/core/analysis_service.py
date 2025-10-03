"""
Main application service that orchestrates the analysis workflow.
"""
import os
from typing import List, Optional
from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, 
    MethodConfig, IProgressCallback
)
from src.core.plugin_registry import plugin_registry


class AnalysisService:
    """Main service for orchestrating DNA sequence analysis"""
    
    def __init__(self):
        self.registry = plugin_registry
        self._current_result: Optional[AnalysisResult] = None
    
    def get_available_methods(self) -> List[str]:
        """Get list of available analysis methods"""
        return self.registry.get_processor_names()
    
    def get_method_config(self, method_name: str) -> Optional[MethodConfig]:
        """Get default configuration for a method"""
        processor = self.registry.get_processor_by_name(method_name)
        if processor:
            return processor.get_default_config()
        return None
    
    def load_sequences_from_directory(self, directory_path: str) -> List[SequenceData]:
        """Load all sequences from a directory"""
        sequences = []
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Find suitable loader
        loader = self.registry.find_suitable_loader(directory_path)
        if not loader:
            raise ValueError("No suitable loader found for the given directory")
        
        try:
            sequences = loader.load_sequences(directory_path)
            print(f"Loaded {len(sequences)} sequences from {directory_path}")
        except Exception as e:
            raise Exception(f"Failed to load sequences: {str(e)}")
        
        return sequences
    
    def analyze_sequences(
        self, 
        sequences: List[SequenceData], 
        method_name: str, 
        config: MethodConfig,
        progress_callback: Optional[IProgressCallback] = None
    ) -> AnalysisResult:
        """Analyze sequences using the specified method"""
        
        if progress_callback:
            progress_callback.set_status("Initializing analysis...")
            progress_callback.update_progress(0.0)
        
        # Get processor
        processor = self.registry.get_processor_by_name(method_name)
        if not processor:
            raise ValueError(f"Unknown analysis method: {method_name}")
        
        # Validate configuration
        if not processor.validate_config(config):
            raise ValueError("Invalid configuration for the selected method")
        
        if progress_callback:
            progress_callback.set_status("Processing sequences...")
            progress_callback.update_progress(0.2)
        
        try:
            # Run analysis
            result = processor.process_sequences(sequences, config)
            self._current_result = result

            if progress_callback:
                progress_callback.set_status("Analysis completed")
                progress_callback.update_progress(1.0)
            
            return result
            
        except Exception as e:
            if progress_callback:
                progress_callback.set_status(f"Analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def visualize_result(
        self, 
        result: AnalysisResult, 
        output_path: str,
        visualizer_name: str = "default",
        **kwargs
    ) -> str:
        """Visualize the analysis result"""
        
        visualizers = self.registry.get_visualizers()
        if not visualizers:
            raise ValueError("No visualizers available")
        
        # Use first available visualizer as default
        visualizer = visualizers[0]
        
        try:
            image_path = visualizer.visualize(result, output_path, **kwargs)
            print(f"Tree visualization saved to: {image_path}")
            return image_path
        except Exception as e:
            raise Exception(f"Visualization failed: {str(e)}")
    
    def get_current_result(self) -> Optional[AnalysisResult]:
        """Get the current analysis result"""
        return self._current_result
    
    def count_fasta_files(self, directory_path: str) -> int:
        """Count FASTA files in a directory"""
        if not os.path.exists(directory_path):
            return 0
        
        count = 0
        try:
            for file in os.listdir(directory_path):
                if file.lower().endswith('.fasta'):
                    count += 1
        except Exception:
            count = 0
        
        return count
