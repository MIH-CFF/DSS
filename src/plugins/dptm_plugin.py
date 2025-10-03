"""
Dynamic Part-wise Template Matching (DPTM) plugin implementation.
"""
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from Bio.Seq import Seq
from Bio import Phylo
from io import StringIO
from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class DPTMProcessor(ISequenceProcessor):
    """Dynamic Part-wise Template Matching processor plugin"""
    
    def __init__(self):
        self._dict_mapping = {"aa": 0}  # Cache for template matching results
    
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Dynamic Part-wise Template Matching"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Dynamic Part-wise Template Matching algorithm for DNA sequence "
                "similarity analysis using dynamic template generation and part-wise matching.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'k_length': 4,
                'threshold_percent': 50,
                'part_length': 10,
                'histogram_reduction_rate': 1
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['k_length', 'threshold_percent', 'part_length']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (1 <= params['k_length'] <= 10):
            return False
        
        if not (0 <= params['threshold_percent'] <= 100):
            return False
        
        if not (1 <= params['part_length'] <= 50):
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences and return analysis results"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        params = config.parameters
        k_length = params['k_length']
        threshold_percent = params['threshold_percent']
        part_length = params['part_length']
        construction_method=params['construction_method']
        hist_reduction_rate = params.get('histogram_reduction_rate', 1)
        
        # Generate ideal sequence template
        ideal_sequence = self._generate_template(k_length)
        
        # Calculate feature size
        feature_size = int(pow(2, (len(ideal_sequence) / k_length) * 2))
        
        # Initialize descriptor matrix
        descriptor = np.zeros((len(sequences), int(feature_size / hist_reduction_rate)))
        sequence_names = []
        
        # Process each sequence
        for i, seq_data in enumerate(sequences):
            sequence_names.append(seq_data.name)
            
            # Calculate dynamic features
            features = self._calculate_dynamic_features(
                seq_data.sequence, ideal_sequence, part_length, threshold_percent
            )
            
            # Create histogram
            hist = np.histogram(features, int(feature_size / hist_reduction_rate))
            descriptor[i] = hist[0]
        
        # Calculate distance matrix
        distances = pairwise_distances(descriptor, metric='euclidean')
        
        # Convert to lower triangular format for BioPython
        distances_list = distances.tolist()
        self._to_lower_triangular_del(distances_list)
        
        # Create BioPython distance matrix
        dist_matrix = DistanceMatrix(sequence_names, matrix=distances_list)
        
        # Construct phylogenetic tree
        constructor = DistanceTreeConstructor()
        if construction_method.lower() == 'upgma':
            tree = constructor.upgma(dist_matrix)
        elif construction_method.lower() == 'nj':
            tree = constructor.nj(dist_matrix)
        tree = constructor.nj(dist_matrix)
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
                'feature_size': feature_size
            },
            newick=newic
        )
    
    def _generate_template(self, k: int) -> str:
        """Generate ideal sequence template"""
        id_seq = ''
        bases = 'AG'
        
        for i in range(k + 1):
            for j in range(len(bases)):
                for _ in range(i):
                    id_seq += bases[j]
        
        return id_seq
    
    def _calculate_dynamic_features(self, sequence: str, template: str, part_length: int, threshold_percent: float) -> np.ndarray:
        """Calculate dynamic part-wise features for a sequence"""
        n = len(sequence)
        t = len(template)
        feature = np.array([])
        
        try:
            for i in range(0, n - t):
                dec_num = 0
                dec_pos_count = 0
                
                for j in range(0, t, part_length):
                    ideal_part = template[j:j + part_length]
                    seq_part = sequence[i + j: i + j + part_length]
                    
                    # Use caching for template matching results
                    cache_key = ideal_part + seq_part
                    if cache_key not in self._dict_mapping:
                        count = self._dynamic_match(ideal_part, seq_part, part_length, threshold_percent)
                        self._dict_mapping[cache_key] = count
                    else:
                        count = self._dict_mapping[cache_key]
                    
                    # Calculate decimal representation
                    if count == 3:
                        dec_num = dec_num + 2 ** dec_pos_count
                        dec_num = dec_num + 2 ** (dec_pos_count + 1)
                    elif count == 2:
                        dec_num = dec_num + 2 ** (dec_pos_count + 1)
                    elif count == 1:
                        dec_num = dec_num + 2 ** dec_pos_count
                
                feature = np.append(feature, dec_num)
                
        except Exception as e:
            print(f"Error in dynamic feature calculation: {e}")
        
        return feature
    
    def _dynamic_match(self, ideal: str, seq: str, part_length: int, threshold_percent: float) -> int:
        """Perform dynamic matching between ideal and sequence parts"""
        try:
            # Convert to BioPython Seq objects for complement calculation
            seq_obj = Seq(seq)
            comp_seq = seq_obj.complement()
            
            dc = cc = 0
            
            # Count direct and complement matches
            for i in range(min(part_length, len(ideal), len(seq))):
                if i < len(ideal) and i < len(seq):
                    if ideal[i] == seq[i]:
                        dc += 1
                    if ideal[i] == str(comp_seq)[i]:
                        cc += 1
            
            doc = dc + cc
            
            # Calculate percentages
            dcpercent = (dc / part_length) * 100
            ccpercent = (cc / part_length) * 100
            docpercent = (doc / part_length) * 100
            
            # Determine match type
            if dcpercent >= threshold_percent:
                return 3  # Direct match
            elif ccpercent >= threshold_percent:
                return 2  # Complement match
            elif docpercent >= threshold_percent:
                return 1  # Combined match
            else:
                return 0  # No significant match
                
        except Exception as e:
            print(f"Error in dynamic match: {e}")
            return 0
    
    def _to_lower_triangular_del(self, matrix: List[List[float]]) -> None:
        """Convert matrix to lower triangular format by deleting upper triangle"""
        n = len(matrix)
        for i in range(n):
            del matrix[i][i + 1:n]
