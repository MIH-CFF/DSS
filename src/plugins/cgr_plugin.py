"""
Chaos Game Representation (CGR) plugin implementation.
"""
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from Bio import Phylo
from io import StringIO

from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class CGRProcessor(ISequenceProcessor):
    """Chaos Game Representation processor plugin"""
    
    def __init__(self):
        pass
    
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Chaos Game Frequency Representation"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Chaos Game Representation algorithm for DNA sequence "
                "similarity analysis using k-mer frequency patterns in CGR space.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'kmer_length': 4,
                'construction_method': 'nj'
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        if 'kmer_length' not in params:
            return False
        
        # Validate parameter ranges
        if not (1 <= params['kmer_length'] <= 8):
            return False
        
        # Validate tree method
        tree_method = params['construction_method'].lower()
        if tree_method not in ['nj', 'upgma']:
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences and return analysis results"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        params = config.parameters
        kmer_length = params['kmer_length']
        tree_method = params['construction_method'].lower()
        
        # Generate descriptors for all sequences
        descriptors = []
        sequence_names = []
        
        for seq_data in sequences:
            sequence_names.append(seq_data.name)
            
            # Generate CGR image and extract features
            cgr_image = self._cgr_original(seq_data.sequence, kmer_length)
            descriptor = cgr_image.flatten()
            descriptors.append(descriptor)
        
        descriptors = np.array(descriptors)
        
        # Calculate distance matrix
        distances = pairwise_distances(descriptors, metric='euclidean')
        
        # Convert to lower triangular format for BioPython
        n = len(sequence_names)
        dist_matrix = []
        for i in range(n):
            dist_matrix.append(distances[i, :i+1].tolist())
        
        # Create BioPython distance matrix
        dm = DistanceMatrix(sequence_names, matrix=dist_matrix)
        
        # Construct phylogenetic tree
        constructor = DistanceTreeConstructor()
        if tree_method == 'upgma':
            tree = constructor.upgma(dm)
        else:
            tree = constructor.nj(dm)
        handle=StringIO()
        Phylo.write(tree,handle,'newick')
        newic=handle.getvalue()
        handle.close()
        return AnalysisResult(
            tree=tree,
            distance_matrix=distances,
            sequence_names=sequence_names,
            metadata={
                'method': self.get_method_name(),
                'config': config.parameters,
                'kmer_length': kmer_length,
                'tree_method': tree_method
            },
            newick=newic
        )
    
    def _cgr_k_mer(self, sequence: str) -> tuple:
        """
        Calculate the CGR coordinates for a given k-mer sequence.
        
        Parameters:
        sequence (str): DNA sequence string
        
        Returns:
        tuple: (lx, ly) coordinates in the CGR space
        """
        z = len(sequence)
        lx, ly = 1, 1
        
        for i in range(z):
            if i == 0:
                nuec_base = sequence[-1]  # Last character in sequence
                if nuec_base == 'A':
                    lx, ly = 1, 1
                elif nuec_base == 'G':
                    lx, ly = 2, 1
                elif nuec_base == 'C':
                    lx, ly = 1, 2
                elif nuec_base == 'T':
                    lx, ly = 2, 2
            else:
                baseInterval = 2**i / 2
                nuec_base = sequence[z-i-1]  # Reverse order processing
                
                if nuec_base == 'G':
                    lx += baseInterval
                elif nuec_base == 'C':
                    ly += baseInterval
                elif nuec_base == 'T':
                    lx += baseInterval
                    ly += baseInterval
                    
        return int(lx-1), int(ly-1)  # Convert to 0-indexed coordinates
    
    def _cgr_image_kmer_count(self, sequence: str, kmer: int) -> np.ndarray:
        """
        Generate a CGR image matrix for a given sequence and k-mer length.
        
        Parameters:
        sequence (str): DNA sequence string
        kmer (int): Length of k-mers to consider
        
        Returns:
        numpy.ndarray: 2D array representing the CGR image
        """
        seqLength = len(sequence)
        
        # Matrix size estimation and assign with zero
        dimension = 2**kmer
        image = np.zeros((dimension, dimension), dtype=np.uint16)
        
        for i in range(seqLength - kmer + 1):
            kmerSeq = sequence[i:i+kmer]
            # CGR Matrix position calculation
            lx, ly = self._cgr_k_mer(kmerSeq)
            # Image generation from counting
            if lx < dimension and ly < dimension:  # Ensure within bounds
                image[ly, lx] += 1
                
        return image
    
    def _cgr_original(self, sequence: str, kmer: int) -> np.ndarray:
        """
        Generate the original CGR image for a sequence.
        
        Parameters:
        sequence (str): DNA sequence
        kmer (int): k-mer length
        
        Returns:
        numpy.ndarray: CGR image
        """
        return self._cgr_image_kmer_count(sequence, kmer)