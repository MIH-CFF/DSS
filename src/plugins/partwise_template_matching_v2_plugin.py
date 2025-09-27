"""
Part-wise Template Matching (PTM) plugin implementation.
"""
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class PartWiseTemplateMatchingV2Processor(ISequenceProcessor):
    """Part-wise Template Matching V2 processor plugin"""
    
    def __init__(self):
        pass
    
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Part-wise Template Matching V2"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Advanced Part-wise Template Matching with complement consideration "
                "and flexible similarity scoring for phylogenetic analysis.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'partition': 10,
                'base_length': 4,
                'similarity_method': 'four_base',  # 'three_base', 'four_base', 'four_base_comp'
                'tree_method': 'nj'  # nj or upgma
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['partition', 'base_length', 'similarity_method']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (1 <= params['partition'] <= 50):
            return False
        
        if not (3 <= params['base_length'] <= 10):
            return False
        
        # Validate similarity method
        similarity_method = params.get('similarity_method', 'four_base')
        if similarity_method not in ['three_base', 'four_base', 'four_base_comp']:
            return False
        
        # Validate tree method
        tree_method = params.get('tree_method', 'nj').lower()
        if tree_method not in ['nj', 'upgma']:
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences and return analysis results"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        params = config.parameters
        partition = params['partition']
        base_length = params['base_length']
        similarity_method = params['similarity_method']
        tree_method = params.get('tree_method', 'nj').lower()
        
        # Generate ideal sequence template
        ideal_sequence = self._generate_ideal_sequence(base_length)
        
        # Process sequences to generate descriptors
        descriptors = []
        sequence_names = []
        
        for seq_data in sequences:
            sequence_names.append(seq_data.name)
            
            # Calculate sequence features using selected method
            if similarity_method == 'three_base':
                features = self._three_base_seq_diff(seq_data.sequence, ideal_sequence, partition, base_length)
            elif similarity_method == 'four_base':
                features = self._four_base_seq_diff(seq_data.sequence, ideal_sequence, partition, base_length)
            else:  # four_base_comp
                features = self._four_base_comp_seq_diff(seq_data.sequence, ideal_sequence, partition, base_length)
            
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
        
        return AnalysisResult(
            tree=tree,
            distance_matrix=distances,
            sequence_names=sequence_names,
            metadata={
                'method': self.get_method_name(),
                'config': config.parameters,
                'ideal_sequence': ideal_sequence,
                'similarity_method': similarity_method
            }
        )
    
    def _complement(self, base: str) -> str:
        """Get complement of a DNA base"""
        complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return complements.get(base, 'N')
    
    def _generate_ideal_sequence(self, length: int) -> str:
        """Generate an ideal sequence template"""
        bases = 'ATCG'
        ideal = ''
        for i in range(length):
            ideal += bases[i % 4]
        return ideal
    
    def _three_base_state(self, target: str, ideal: str, win_len: int) -> int:
        """Calculate similarity between target and ideal sequences (3-base version)"""
        cont = 0
        for st in range(min(win_len, len(target), len(ideal))):
            if target[st] == ideal[st]:
                cont += 1
        return cont
    
    def _four_base_state(self, target: str, ideal: str, win_len: int) -> int:
        """Calculate similarity between target and ideal sequences (4-base version)"""
        count = 0
        for st in range(min(win_len, len(target), len(ideal))):
            if target[st] == ideal[st]:
                count += 1
        
        if count >= 3:
            return 3
        elif count == 2:
            return 2
        elif count == 1:
            return 1
        else:
            return 0
    
    def _four_base_comp_state(self, target: str, ideal: str, win_len: int) -> int:
        """Calculate similarity considering both forward and complement matches"""
        fcont = 0
        ccont = 0
        
        for st in range(min(win_len, len(target), len(ideal))):
            if target[st] == ideal[st]:
                fcont += 1
            
            complement_base = self._complement(target[st])
            if complement_base == ideal[st]:
                ccont += 1
        
        if fcont == win_len:
            return 3
        elif ccont == win_len:
            return 2
        elif fcont >= 2 or ccont >= 2:
            return 1
        else:
            return 0
    
    def _three_base_seq_diff(self, sequence: str, ideal_seq: str, partition: int, base_length: int) -> np.ndarray:
        """Calculate features using three-base similarity method"""
        w = len(sequence)
        distances = np.zeros(w - base_length + 1)
        
        for i in range(w - base_length + 1):
            target = sequence[i:i + base_length]
            similarity = self._three_base_state(target, ideal_seq, base_length)
            distances[i] = similarity
        
        return self._partition_features(distances, partition)
    
    def _four_base_seq_diff(self, sequence: str, ideal_seq: str, partition: int, base_length: int) -> np.ndarray:
        """Calculate features using four-base similarity method"""
        w = len(sequence)
        distances = np.zeros(w - base_length + 1)
        
        for i in range(w - base_length + 1):
            target = sequence[i:i + base_length]
            similarity = self._four_base_state(target, ideal_seq, base_length)
            distances[i] = similarity
        
        return self._partition_features(distances, partition)
    
    def _four_base_comp_seq_diff(self, sequence: str, ideal_seq: str, partition: int, base_length: int) -> np.ndarray:
        """Calculate features using four-base with complement similarity method"""
        w = len(sequence)
        distances = np.zeros(w - base_length + 1)
        
        for i in range(w - base_length + 1):
            target = sequence[i:i + base_length]
            similarity = self._four_base_comp_state(target, ideal_seq, base_length)
            distances[i] = similarity
        
        return self._partition_features(distances, partition)
    
    def _partition_features(self, distances: np.ndarray, partition: int) -> np.ndarray:
        """Partition the distances and create histogram features"""
        if len(distances) == 0:
            return np.zeros(partition * 10)  # Default feature size
        
        partition_size = len(distances) // partition
        features = []
        
        for p in range(partition):
            start_idx = p * partition_size
            end_idx = min((p + 1) * partition_size, len(distances))
            if start_idx < len(distances):
                partition_data = distances[start_idx:end_idx]
                # Create histogram for this partition
                hist, _ = np.histogram(partition_data, bins=10)
                features.extend(hist)
            else:
                features.extend([0] * 10)  # Empty partition
        
        return np.array(features)