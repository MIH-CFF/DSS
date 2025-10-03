"""
Core interfaces and abstract base classes for the DNA Sequence Similarity application.
These define the contracts that plugins and adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class SequenceData:
    """Data class for storing sequence information"""
    name: str
    sequence: str
    features: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    """Data class for storing analysis results"""
    tree: Any  # Phylogenetic tree object
    distance_matrix: np.ndarray
    sequence_names: List[str]
    metadata: Dict[str, Any]
    newick:str


@dataclass
class MethodConfig:
    """Configuration for analysis methods"""
    name: str
    parameters: Dict[str, Any]
    description: str = ""


class ISequenceProcessor(ABC):
    """Interface for sequence processing algorithms"""
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of the method"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        pass
    
    @abstractmethod
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        pass
    
    @abstractmethod
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences and return analysis results"""
        pass


class ISequenceLoader(ABC):
    """Interface for loading sequence data"""
    
    @abstractmethod
    def supports_format(self, file_path: str) -> bool:
        """Check if this loader supports the given file format"""
        pass
    
    @abstractmethod
    def load_sequences(self, source_path: str) -> List[SequenceData]:
        """Load sequences from the given source"""
        pass


class ITreeVisualizer(ABC):
    """Interface for tree visualization"""
    
    @abstractmethod
    def visualize(self, result: AnalysisResult, output_path: str, **kwargs) -> str:
        """Visualize the phylogenetic tree and return the image path"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return supported output formats"""
        pass


class IProgressCallback(ABC):
    """Interface for progress reporting"""
    
    @abstractmethod
    def update_progress(self, progress: float, message: str = "") -> None:
        """Update progress (0.0 to 1.0)"""
        pass
    
    @abstractmethod
    def set_status(self, status: str) -> None:
        """Set status message"""
        pass


class IPluginRegistry(ABC):
    """Interface for plugin management"""
    
    @abstractmethod
    def register_processor(self, processor: ISequenceProcessor) -> None:
        """Register a sequence processor plugin"""
        pass
    
    @abstractmethod
    def register_loader(self, loader: ISequenceLoader) -> None:
        """Register a sequence loader plugin"""
        pass
    
    @abstractmethod
    def register_visualizer(self, visualizer: ITreeVisualizer) -> None:
        """Register a tree visualizer plugin"""
        pass
    
    @abstractmethod
    def get_processors(self) -> List[ISequenceProcessor]:
        """Get all registered processors"""
        pass
    
    @abstractmethod
    def get_loaders(self) -> List[ISequenceLoader]:
        """Get all registered loaders"""
        pass
    
    @abstractmethod
    def get_visualizers(self) -> List[ITreeVisualizer]:
        """Get all registered visualizers"""
        pass
    
    @abstractmethod
    def get_processor_by_name(self, name: str) -> Optional[ISequenceProcessor]:
        """Get processor by name"""
        pass
