"""
Plugin loader for automatic plugin discovery and registration.
"""
import importlib
import pkgutil
from typing import Type, List
from src.core.interfaces import ISequenceProcessor, ISequenceLoader, ITreeVisualizer
from src.core.plugin_registry import plugin_registry


class PluginLoader:
    """Automatic plugin discovery and loading"""
    
    def __init__(self):
        self.loaded_plugins = set()
    
    def load_all_plugins(self):
        """Load all available plugins"""
        self._load_core_plugins()
        self._load_adapter_plugins()
        # Future: Add automatic discovery from plugin directories
    
    def _load_core_plugins(self):
        """Load core analysis plugins"""
        try:
            from src.plugins.dptm_plugin import DPTMProcessor
            plugin_registry.register_processor(DPTMProcessor())
            self.loaded_plugins.add("DPTMProcessor")
        except ImportError as e:
            print(f"Failed to load DPTM plugin: {e}")
        
        try:
            from src.plugins.template_matching_plugin import TemplateMatchingProcessor
            from src.plugins.chaos_game_plugin import ChaosGameFrequencyProcessor
            from src.plugins.partwise_template_matching_plugin import PartWiseTemplateMatchingProcessor
            
            plugin_registry.register_processor(ChaosGameFrequencyProcessor())
            plugin_registry.register_processor(TemplateMatchingProcessor())
            plugin_registry.register_processor(PartWiseTemplateMatchingProcessor())
            
            self.loaded_plugins.update([
                "ChaosGameFrequencyProcessor",
                "TemplateMatchingProcessor", 
                "PartWiseTemplateMatchingProcessor"
            ])
        except ImportError as e:
            print(f"Failed to load stub plugins: {e}")
        
        # Load new enhanced plugins
        try:
            from src.plugins.cgr_plugin import CGRProcessor
            from src.plugins.template_matching_v2_plugin import TemplateMatchingV2Processor
            from src.plugins.partwise_template_matching_v2_plugin import PartWiseTemplateMatchingV2Processor
            
            plugin_registry.register_processor(CGRProcessor())
            plugin_registry.register_processor(TemplateMatchingV2Processor())
            plugin_registry.register_processor(PartWiseTemplateMatchingV2Processor())
            
            self.loaded_plugins.update([
                "CGRProcessor",
                "TemplateMatchingV2Processor", 
                "PartWiseTemplateMatchingV2Processor"
            ])
        except ImportError as e:
            print(f"Failed to load enhanced plugins: {e}")
    
    def _load_adapter_plugins(self):
        """Load adapter plugins"""
        try:
            from src.adapters.biopython_adapter import BioPythonSequenceLoader
            plugin_registry.register_loader(BioPythonSequenceLoader())
            self.loaded_plugins.add("BioPythonSequenceLoader")
        except ImportError as e:
            print(f"Failed to load BioPython adapter: {e}")
        
        try:
            from src.adapters.matplotlib_adapter import MatplotlibTreeVisualizer
            plugin_registry.register_visualizer(MatplotlibTreeVisualizer())
            self.loaded_plugins.add("MatplotlibTreeVisualizer")
        except ImportError as e:
            print(f"Failed to load Matplotlib adapter: {e}")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of successfully loaded plugins"""
        return list(self.loaded_plugins)
    
    def load_external_plugin(self, plugin_module_path: str):
        """Load an external plugin from a module path"""
        try:
            module = importlib.import_module(plugin_module_path)
            
            # Look for processor classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, ISequenceProcessor) and 
                    attr is not ISequenceProcessor):
                    plugin_registry.register_processor(attr())
                    self.loaded_plugins.add(attr_name)
                
                # Look for loader classes
                if (isinstance(attr, type) and 
                    issubclass(attr, ISequenceLoader) and 
                    attr is not ISequenceLoader):
                    plugin_registry.register_loader(attr())
                    self.loaded_plugins.add(attr_name)
                
                # Look for visualizer classes
                if (isinstance(attr, type) and 
                    issubclass(attr, ITreeVisualizer) and 
                    attr is not ITreeVisualizer):
                    plugin_registry.register_visualizer(attr())
                    self.loaded_plugins.add(attr_name)
            
            print(f"Successfully loaded external plugin: {plugin_module_path}")
            
        except Exception as e:
            print(f"Failed to load external plugin {plugin_module_path}: {e}")


# Global plugin loader instance
plugin_loader = PluginLoader()
