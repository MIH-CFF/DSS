"""
Template Matching plugin implementation.
This implements a template-based sequence matching algorithm for phylogenetic analysis.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from Bio.Seq import Seq

from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class TemplateMatchingProcessor(ISequenceProcessor):
    """Template Matching processor plugin for DNA sequence analysis"""
    
    def __init__(self):
        self._template_cache = {}  # Cache for template matching results
    
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Template Matching"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Template Matching algorithm for DNA sequence similarity analysis. "
                "Uses sliding window template matching to identify similar patterns "
                "and constructs phylogenetic relationships based on template similarity scores.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'template_length': 20,
                'similarity_threshold': 0.75,
                'sliding_window_step': 5,
                'use_complement': True,
                'normalize_scores': True,
                'min_matches_required': 10
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['template_length', 'similarity_threshold', 'sliding_window_step']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (5 <= params['template_length'] <= 100):
            return False
        
        if not (0.0 <= params['similarity_threshold'] <= 1.0):
            return False
        
        if not (1 <= params['sliding_window_step'] <= params['template_length']):
            return False
        
        min_matches = params.get('min_matches_required', 10)
        if not (1 <= min_matches <= 1000):
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences and return analysis results"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        if len(sequences) < 2:
            raise ValueError("At least 2 sequences are required for comparison")
        
        params = config.parameters
        template_length = params['template_length']
        similarity_threshold = params['similarity_threshold']
        sliding_step = params['sliding_window_step']
        use_complement = params.get('use_complement', True)
        normalize_scores = params.get('normalize_scores', True)
        min_matches = params.get('min_matches_required', 10)
        
        # Extract features using template matching
        features = []
        sequence_names = []
        
        print(f"Processing {len(sequences)} sequences with template matching...")
        
        for i, seq_data in enumerate(sequences):
            sequence_names.append(seq_data.name)
            print(f"  Processing sequence {i+1}/{len(sequences)}: {seq_data.name}")
            
            # Calculate template-based features
            seq_features = self._extract_template_features(
                seq_data.sequence, 
                template_length, 
                sliding_step,
                use_complement,
                similarity_threshold,
                min_matches
            )
            
            features.append(seq_features)
        
        # Normalize features if requested
        if normalize_scores:
            features = self._normalize_features(features)
        
        # Calculate distance matrix
        print("Calculating distance matrix...")
        distance_matrix = self._calculate_distance_matrix(features)
        
        # Build phylogenetic tree
        print("Constructing phylogenetic tree...")
        tree = self._build_phylogenetic_tree(sequence_names, distance_matrix)
        
        return AnalysisResult(
            tree=tree,
            distance_matrix=distance_matrix,
            sequence_names=sequence_names,
            metadata={
                'method': self.get_method_name(),
                'config': config.parameters,
                'sequence_count': len(sequences),
                'feature_dimension': len(features[0]) if features else 0,
                'template_cache_size': len(self._template_cache)
            }
        )
    
    def _extract_template_features(
        self, 
        sequence: str, 
        template_length: int, 
        sliding_step: int,
        use_complement: bool,
        similarity_threshold: float,
        min_matches: int
    ) -> np.ndarray:
        """Extract template-based features from a sequence"""
        
        sequence = sequence.upper()
        seq_len = len(sequence)
        
        # Generate templates from the sequence itself (self-similarity approach)
        templates = self._generate_templates(sequence, template_length, sliding_step)
        
        # Calculate template matching scores
        feature_vector = []
        
        for template in templates:
            # Find matches for this template across the entire sequence
            matches = self._find_template_matches(
                sequence, template, similarity_threshold, use_complement
            )
            
            # Calculate features from matches
            if len(matches) >= min_matches:
                # Use match statistics as features
                match_count = len(matches)
                match_density = match_count / (seq_len - template_length + 1)
                avg_similarity = np.mean([match['similarity'] for match in matches])
                max_similarity = np.max([match['similarity'] for match in matches])
                
                # Position-based features
                positions = [match['position'] for match in matches]
                pos_variance = np.var(positions) if len(positions) > 1 else 0
                pos_spread = (max(positions) - min(positions)) / seq_len if positions else 0
                
                template_features = [
                    match_count,
                    match_density,
                    avg_similarity,
                    max_similarity,
                    pos_variance,
                    pos_spread
                ]
            else:
                # No sufficient matches found
                template_features = [0, 0, 0, 0, 0, 0]
            
            feature_vector.extend(template_features)
        
        return np.array(feature_vector)
    
    def _generate_templates(self, sequence: str, template_length: int, sliding_step: int) -> List[str]:
        """Generate templates from the sequence using sliding window"""
        templates = []
        seq_len = len(sequence)
        
        # Extract templates using sliding window
        for i in range(0, seq_len - template_length + 1, sliding_step):
            template = sequence[i:i + template_length]
            if len(template) == template_length:
                templates.append(template)
        
        # Remove duplicates while preserving order
        unique_templates = []
        seen = set()
        for template in templates:
            if template not in seen:
                unique_templates.append(template)
                seen.add(template)
        
        # Limit number of templates to prevent excessive computation
        max_templates = min(50, len(unique_templates))
        return unique_templates[:max_templates]
    
    def _find_template_matches(
        self, 
        sequence: str, 
        template: str, 
        similarity_threshold: float,
        use_complement: bool
    ) -> List[Dict[str, Any]]:
        """Find all matches of a template in the sequence"""
        
        matches = []
        seq_len = len(sequence)
        template_len = len(template)
        
        # Create complement template if needed
        complement_template = None
        if use_complement:
            try:
                complement_template = str(Seq(template).complement())
            except:
                complement_template = None
        
        # Slide template across sequence
        for i in range(seq_len - template_len + 1):
            window = sequence[i:i + template_len]
            
            # Calculate similarity with original template
            similarity = self._calculate_sequence_similarity(template, window)
            
            if similarity >= similarity_threshold:
                matches.append({
                    'position': i,
                    'similarity': similarity,
                    'match_type': 'direct',
                    'matched_sequence': window
                })
            
            # Check complement similarity if enabled
            if complement_template:
                comp_similarity = self._calculate_sequence_similarity(complement_template, window)
                if comp_similarity >= similarity_threshold:
                    matches.append({
                        'position': i,
                        'similarity': comp_similarity,
                        'match_type': 'complement',
                        'matched_sequence': window
                    })
        
        return matches
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate similarity between two sequences"""
        if len(seq1) != len(seq2):
            return 0.0
        
        if not seq1 or not seq2:
            return 0.0
        
        # Use caching to avoid repeated calculations
        cache_key = f"{seq1}_{seq2}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Simple nucleotide match percentage
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        similarity = matches / len(seq1)
        
        # Cache the result
        self._template_cache[cache_key] = similarity
        
        return similarity
    
    def _normalize_features(self, features: List[np.ndarray]) -> List[np.ndarray]:
        """Normalize feature vectors"""
        if not features:
            return features
        
        # Convert to matrix for easier processing
        feature_matrix = np.array(features)
        
        # Z-score normalization per feature dimension
        normalized_matrix = np.zeros_like(feature_matrix)
        
        for j in range(feature_matrix.shape[1]):
            feature_column = feature_matrix[:, j]
            mean_val = np.mean(feature_column)
            std_val = np.std(feature_column)
            
            if std_val > 0:
                normalized_matrix[:, j] = (feature_column - mean_val) / std_val
            else:
                normalized_matrix[:, j] = feature_column
        
        return [normalized_matrix[i] for i in range(len(features))]
    
    def _calculate_distance_matrix(self, features: List[np.ndarray]) -> np.ndarray:
        """Calculate distance matrix between sequences"""
        
        if not features:
            raise ValueError("No features provided for distance calculation")
        
        # Convert to matrix
        feature_matrix = np.array(features)
        
        # Calculate pairwise distances using Euclidean distance
        distance_matrix = pairwise_distances(feature_matrix, metric='euclidean')
        
        return distance_matrix
    
    def _build_phylogenetic_tree(self, sequence_names: List[str], distance_matrix: np.ndarray):
        """Build phylogenetic tree from distance matrix"""
        
        try:
            # Convert to lower triangular format for BioPython
            distances_list = distance_matrix.tolist()
            for i in range(len(distances_list)):
                del distances_list[i][i + 1:]
            
            # Create BioPython distance matrix
            dist_matrix = DistanceMatrix(sequence_names, matrix=distances_list)
            
            # Build tree using neighbor-joining
            constructor = DistanceTreeConstructor()
            tree = constructor.nj(dist_matrix)
            
            return tree
            
        except Exception as e:
            raise Exception(f"Failed to build phylogenetic tree: {str(e)}")
    
    def clear_cache(self):
        """Clear the template matching cache"""
        self._template_cache.clear()
