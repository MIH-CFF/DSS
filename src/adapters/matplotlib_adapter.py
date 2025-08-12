"""
Adapter for matplotlib/BioPython tree visualization.
"""
import os
from typing import List
import matplotlib.pyplot as plt
from Bio import Phylo
from src.core.interfaces import ITreeVisualizer, AnalysisResult


class MatplotlibTreeVisualizer(ITreeVisualizer):
    """Adapter for visualizing phylogenetic trees using matplotlib"""
    
    def visualize(self, result: AnalysisResult, output_path: str, **kwargs) -> str:
        """Visualize the phylogenetic tree and return the image path"""
        
        # Extract visualization parameters
        figsize = kwargs.get('figsize', (16, 10))
        dpi = kwargs.get('dpi', 100)
        format_type = kwargs.get('format', 'png')
        
        try:
            # Create matplotlib figure
            fig = plt.figure(figsize=figsize, dpi=dpi)
            axes = fig.add_subplot(1, 1, 1)
            
            # Draw the phylogenetic tree
            Phylo.draw(result.tree, axes=axes, do_show=False)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the figure
            plt.savefig(output_path, format=format_type, dpi=dpi, bbox_inches='tight')
            plt.close(fig)  # Close to free memory
            
            return output_path
            
        except Exception as e:
            plt.close('all')  # Ensure cleanup on error
            raise Exception(f"Failed to visualize tree: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """Return supported output formats"""
        return ['png', 'jpg', 'jpeg', 'pdf', 'svg', 'eps']
    
    def show_tree(self, result: AnalysisResult, **kwargs) -> None:
        """Display the tree interactively"""
        try:
            figsize = kwargs.get('figsize', (12, 8))
            fig = plt.figure(figsize=figsize)
            axes = fig.add_subplot(1, 1, 1)
            
            Phylo.draw(result.tree, axes=axes, do_show=True)
            plt.show()
            
        except Exception as e:
            plt.close('all')
            raise Exception(f"Failed to display tree: {str(e)}")
