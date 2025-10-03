"""
Template Matching (TM) plugin implementation.
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


class TMProcessor(ISequenceProcessor):
    """Template Matching V2 processor plugin"""
    
    def __init__(self):
        pass
    
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Template Matching"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Enhanced Template Matching algorithm using binary encoding "
                "and complement-based sequence analysis for phylogenetic reconstruction.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'partition': 10,
                'construction_method': 'nj'  # nj or upgma
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['partition']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (1 <= params['partition'] <= 10):
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
        partition = params['partition']
        ideal_seq_length = 12
        tree_method = params['construction_method'].lower()
        
        # Generate ideal sequence template
        ideal_sequence = self._generate_ideal_sequence(ideal_seq_length)
        
        # Process sequences to generate descriptors
        descriptors = []
        sequence_names = []
        
        for seq_data in sequences:
            sequence_names.append(seq_data.name)
            
            # Calculate sequence difference features
            features = self._seq_diff(seq_data.sequence, ideal_sequence, partition)
            descriptors.append(features)
        
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
                'ideal_sequence': ideal_sequence,
                'partition': partition
            },
            newick=newic
        )
    
    def _complement(self, base: str) -> str:
        """Get complement of a DNA base"""
        complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return complements.get(base, 'N')
    
    def _generate_ideal_sequence(self, length: int) -> str:
        """Generate an ideal sequence template"""
        # Simple pattern-based ideal sequence
        bases = 'ATCG'
        ideal = ''
        for i in range(length):
            ideal += bases[i % 4]
        return ideal
    
    def _seq_diff(self, sequence: str, ideal_seq: str, partition: int) -> np.ndarray:
        """
        Calculate sequence difference features using binary encoding
        
        Parameters:
        sequence (str): DNA sequence
        ideal_seq (str): Ideal reference sequence
        partition (int): Number of partitions
        
        Returns:
        numpy.ndarray: Feature vector
        """
        w = len(sequence)
        distances = np.zeros(w)
        ideal_seq_length = len(ideal_seq)
        
        # Iterate through the whole sequence
        for i in range(w):
            dec_num = 0
            t = 0
            
            # Match full template
            for j in range(ideal_seq_length):
                # Calculate similarity for right side sequences
                if (i + ideal_seq_length - j) <= w:
                    ideal_seq_base = ideal_seq[ideal_seq_length - 1 - j]
                    seq_base = sequence[i + ideal_seq_length - 1 - j]
                    
                    # Check for match or complement match
                    if seq_base == ideal_seq_base or seq_base == self._complement(ideal_seq_base):
                        dec_num += pow(2, j)
                        t += 1
            
            distances[i] = dec_num
        
        # Partition the distances and create histogram
        partition_size = w // partition
        features = []
        
        for p in range(partition):
            start_idx = p * partition_size
            end_idx = min((p + 1) * partition_size, w)
            partition_data = distances[start_idx:end_idx]
            
            # Create histogram for this partition
            hist, _ = np.histogram(partition_data, bins=50)
            features.extend(hist)
        
        return np.array(features)