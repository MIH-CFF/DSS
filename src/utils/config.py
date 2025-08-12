"""
Application configuration and constants.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class UIConfig:
    """UI configuration settings"""
    window_title: str = "BAU Similarity"
    window_size: tuple = (900, 600)
    logo_size: tuple = (130, 50)
    tree_display_size: tuple = (700, 400)
    tree_output_size: tuple = (16, 10)
    tree_dpi: int = 100
    

@dataclass
class PathConfig:
    """Path configuration"""
    images_dir: str = "images"
    assets_dir: str = "asset"
    datasets_dir: str = "Datasets"
    phylo_output_dir: str = "phylogenetic_tree"
    
    # Image files
    bau_logo: str = "images/bau_logo.png"
    ict_logo: str = "images/ict_min_logo.png"
    demo_logo: str = "images/demo_logo.png"
    tree_placeholder: str = "images/tree.png"
    loading_gif: str = "images/loading.gif"
    app_icon: str = "images/icon.ico"
    
    # Style files
    style_qss: str = "asset/style.qss"


@dataclass
class AnalysisConfig:
    """Analysis configuration defaults"""
    default_k_length: int = 4
    default_threshold: int = 50
    k_length_range: tuple = (1, 10)
    threshold_range: tuple = (0, 100)


class AppConfig:
    """Main application configuration"""
    
    def __init__(self):
        self.ui = UIConfig()
        self.paths = PathConfig()
        self.analysis = AnalysisConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'ui': self.ui.__dict__,
            'paths': self.paths.__dict__,
            'analysis': self.analysis.__dict__
        }


# Global configuration instance
app_config = AppConfig()
