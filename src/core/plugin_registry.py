"""
Plugin registry implementation for managing analysis plugins.
"""
from typing import Dict, List, Optional
from src.core.interfaces import (
    IPluginRegistry, ISequenceProcessor, ISequenceLoader, 
    ITreeVisualizer
)


class PluginRegistry(IPluginRegistry):
    """Central registry for all plugins"""
    
    def __init__(self):
        self._processors: Dict[str, ISequenceProcessor] = {}
        self._loaders: List[ISequenceLoader] = []
        self._visualizers: List[ITreeVisualizer] = []
    
    def register_processor(self, processor: ISequenceProcessor) -> None:
        """Register a sequence processor plugin"""
        name = processor.get_method_name()
        self._processors[name] = processor
        print(f"Registered processor: {name}")
    
    def register_loader(self, loader: ISequenceLoader) -> None:
        """Register a sequence loader plugin"""
        self._loaders.append(loader)
        print(f"Registered loader: {loader.__class__.__name__}")
    
    def register_visualizer(self, visualizer: ITreeVisualizer) -> None:
        """Register a tree visualizer plugin"""
        self._visualizers.append(visualizer)
        print(f"Registered visualizer: {visualizer.__class__.__name__}")
    
    def get_processors(self) -> List[ISequenceProcessor]:
        """Get all registered processors"""
        return list(self._processors.values())
    
    def get_loaders(self) -> List[ISequenceLoader]:
        """Get all registered loaders"""
        return self._loaders.copy()
    
    def get_visualizers(self) -> List[ITreeVisualizer]:
        """Get all registered visualizers"""
        return self._visualizers.copy()
    
    def get_processor_by_name(self, name: str) -> Optional[ISequenceProcessor]:
        """Get processor by name"""
        return self._processors.get(name)
    
    def get_processor_names(self) -> List[str]:
        """Get names of all registered processors"""
        return list(self._processors.keys())
    
    def find_suitable_loader(self, file_path: str) -> Optional[ISequenceLoader]:
        """Find a loader that supports the given file"""
        for loader in self._loaders:
            if loader.supports_format(file_path):
                return loader
        return None


# Global plugin registry instance
plugin_registry = PluginRegistry()
