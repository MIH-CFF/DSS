"""
Core package initialization - imports and exports for the core functionality
"""
from .interfaces import (
    ISequenceProcessor, ISequenceLoader, ITreeVisualizer, 
    IProgressCallback, IPluginRegistry,
    SequenceData, AnalysisResult, MethodConfig
)
from .plugin_registry import plugin_registry, PluginRegistry
from .analysis_service import AnalysisService
from .plugin_loader import plugin_loader, PluginLoader

__all__ = [
    'ISequenceProcessor', 'ISequenceLoader', 'ITreeVisualizer', 
    'IProgressCallback', 'IPluginRegistry',
    'SequenceData', 'AnalysisResult', 'MethodConfig',
    'plugin_registry', 'PluginRegistry', 'AnalysisService',
    'plugin_loader', 'PluginLoader'
]
