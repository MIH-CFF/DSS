"""
Package initialization and imports for the new architecture.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core components
from src.core import (
    AnalysisService, plugin_registry,
    ISequenceProcessor, ISequenceLoader, ITreeVisualizer,
    SequenceData, AnalysisResult, MethodConfig
)

# UI components  
from src.ui import MainWindow, AnalysisWindow, create_application, main

# Plugins
from src.plugins import (
    DPTMProcessor, CGRProcessor,
    TMProcessor, PTMProcessor
)

# Adapters
from src.adapters import BioPythonSequenceLoader, MatplotlibTreeVisualizer

# API components
from src.api import create_app

# Utilities
from src.utils import app_config, resource_path

__version__ = "2.0.0"
__author__ = "BAU Research Team"
__description__ = "DNA Sequence Similarity Analysis with Plugin Architecture"

__all__ = [
    # Core
    'AnalysisService', 'plugin_registry',
    'ISequenceProcessor', 'ISequenceLoader', 'ITreeVisualizer', 
    'SequenceData', 'AnalysisResult', 'MethodConfig',
    
    # UI
    'MainWindow', 'AnalysisWindow', 'create_application', 'main',
    
    # Plugins
    'DPTMProcessor', 'CGRProcessor', 'TMProcessor', 'PTMProcessor',
    
    # Adapters
    'BioPythonSequenceLoader', 'MatplotlibTreeVisualizer',
    
    # API
    'create_app',
    
    # Utils
    'app_config', 'resource_path'
]

# Initialize the phylo directory on import
from src.utils.resources import get_phylo_tree_directory
get_phylo_tree_directory()
