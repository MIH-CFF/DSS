"""
Part-wise Template Matching plugin implementation.
This implements a part-wise template matching algorithm for DNA sequence analysis.
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Set
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from Bio.Seq import Seq

from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class PartWiseTemplateMatchingProcessor(ISequenceProcessor):
    """
    Part-wise Template Matching processor for DNA sequence analysis.
    
    This method divides sequences into parts and performs template matching
    on each part separately, then combines the results for phylogenetic analysis.
    """
    
    def __init__(self):
        self._match_cache = {}  # Cache for template match results
        
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Part-wise Template Matching"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Part-wise Template Matching algorithm divides sequences into "
                "overlapping parts and performs template matching on each part. "
                "This approach captures local sequence patterns while maintaining "
                "global sequence relationships for phylogenetic reconstruction.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'part_size': 50,
                'overlap': 25,
                'template_length': 15,
                'similarity_threshold': 0.75,
                'use_complement': True,
                'min_matches_per_part': 3,
                'normalize_scores': True,
                'weight_by_position': False,
                'max_parts_per_sequence': 100
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['part_size', 'overlap', 'template_length', 'similarity_threshold']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (20 <= params['part_size'] <= 500):
            return False
        
        if not (0 <= params['overlap'] < params['part_size']):
            return False
        
        if not (5 <= params['template_length'] <= params['part_size']):
            return False
        
        if not (0.0 <= params['similarity_threshold'] <= 1.0):
            return False
        
        min_matches = params.get('min_matches_per_part', 3)
        if not (1 <= min_matches <= 50):
            return False
        
        max_parts = params.get('max_parts_per_sequence', 100)
        if not (10 <= max_parts <= 1000):
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences using part-wise template matching"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        if len(sequences) < 2:
            raise ValueError("At least 2 sequences are required for comparison")
        
        params = config.parameters
        part_size = params['part_size']
        overlap = params['overlap']
        template_length = params['template_length']
        similarity_threshold = params['similarity_threshold']
        use_complement = params.get('use_complement', True)
        min_matches = params.get('min_matches_per_part', 3)
        normalize_scores = params.get('normalize_scores', True)
        weight_by_position = params.get('weight_by_position', False)
        max_parts = params.get('max_parts_per_sequence', 100)
        
        print(f"Processing {len(sequences)} sequences with Part-wise Template Matching...")
        
        # Extract part-wise features
        features = []
        sequence_names = []
        
        for i, seq_data in enumerate(sequences):
            sequence_names.append(seq_data.name)
            print(f"  Processing sequence {i+1}/{len(sequences)}: {seq_data.name}")
            
            # Calculate part-wise features
            part_features = self._extract_partwise_features(
                seq_data.sequence,
                part_size,
                overlap,
                template_length,
                similarity_threshold,
                use_complement,
                min_matches,
                weight_by_position,
                max_parts
            )
            
            features.append(part_features)
        
        # Normalize features if requested
        if normalize_scores:
            features = self._normalize_features(features)
        
        # Calculate distance matrix
        print("Calculating distance matrix from part-wise features...")
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
                'cache_size': len(self._match_cache)
            }
        )
    
    def _extract_partwise_features(
        self,
        sequence: str,
        part_size: int,
        overlap: int,
        template_length: int,
        similarity_threshold: float,
        use_complement: bool,
        min_matches: int,
        weight_by_position: bool,
        max_parts: int
    ) -> np.ndarray:
        """Extract part-wise template matching features from a sequence"""
        
        sequence = sequence.upper()
        
        # Divide sequence into overlapping parts
        parts = self._create_sequence_parts(sequence, part_size, overlap, max_parts)
        
        if not parts:
            # Return standardized feature vector size
            return np.zeros(max_parts * 8)  # 8 features per part
        
        all_features = []
        features_per_part = 8  # Fixed number of features per part
        
        for part_idx, part_seq in enumerate(parts):
            # Extract templates from this part
            templates = self._extract_part_templates(part_seq, template_length)
            
            # Calculate part-wise matching features
            part_features = self._calculate_part_features(
                part_seq,
                templates,
                similarity_threshold,
                use_complement,
                min_matches,
                part_idx if weight_by_position else None
            )
            
            # Ensure exactly 8 features per part
            if len(part_features) < features_per_part:
                part_features.extend([0.0] * (features_per_part - len(part_features)))
            elif len(part_features) > features_per_part:
                part_features = part_features[:features_per_part]
            
            all_features.extend(part_features)
        
        # Ensure consistent feature vector size across all sequences
        target_size = max_parts * features_per_part
        final_features = np.array(all_features)
        
        if len(final_features) < target_size:
            # Pad with zeros if fewer parts
            final_features = np.pad(final_features, (0, target_size - len(final_features)), mode='constant')
        elif len(final_features) > target_size:
            # Truncate if more parts (should not happen with max_parts limit)
            final_features = final_features[:target_size]
        
        return final_features
    
    def _create_sequence_parts(
        self,
        sequence: str,
        part_size: int,
        overlap: int,
        max_parts: int
    ) -> List[str]:
        """Divide sequence into overlapping parts"""
        
        parts = []
        seq_len = len(sequence)
        step_size = part_size - overlap
        
        if step_size <= 0:
            step_size = 1
        
        for i in range(0, seq_len - part_size + 1, step_size):
            if len(parts) >= max_parts:
                break
                
            part = sequence[i:i + part_size]
            if len(part) == part_size:
                parts.append(part)
        
        # If no complete parts, use the whole sequence (truncated if necessary)
        if not parts and seq_len > 0:
            if seq_len > part_size:
                parts.append(sequence[:part_size])
            else:
                parts.append(sequence)
        
        return parts
    
    def _extract_part_templates(self, part_seq: str, template_length: int) -> List[str]:
        """Extract templates from a sequence part"""
        
        templates = []
        part_len = len(part_seq)
        
        # Extract all possible templates of the specified length
        for i in range(part_len - template_length + 1):
            template = part_seq[i:i + template_length]
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
        max_templates = min(20, len(unique_templates))
        return unique_templates[:max_templates]
    
    def _calculate_part_features(
        self,
        part_seq: str,
        templates: List[str],
        similarity_threshold: float,
        use_complement: bool,
        min_matches: int,
        position_weight: int = None
    ) -> List[float]:
        """Calculate features for a sequence part based on template matching"""
        
        if not templates:
            return [0.0] * 8  # Return default features
        
        # Collect all match statistics
        total_matches = 0
        total_similarity = 0.0
        max_similarity = 0.0
        complement_matches = 0
        position_variance = 0.0
        template_diversity = len(templates)
        
        match_positions = []
        
        for template in templates:
            matches = self._find_template_matches_in_part(
                part_seq, template, similarity_threshold, use_complement
            )
            
            if len(matches) >= min_matches:
                total_matches += len(matches)
                
                for match in matches:
                    total_similarity += match['similarity']
                    max_similarity = max(max_similarity, match['similarity'])
                    match_positions.append(match['position'])
                    
                    if match['match_type'] == 'complement':
                        complement_matches += 1
        
        # Calculate statistics
        part_length = len(part_seq)
        
        # Basic match statistics
        match_density = total_matches / part_length if part_length > 0 else 0
        avg_similarity = total_similarity / total_matches if total_matches > 0 else 0
        complement_ratio = complement_matches / total_matches if total_matches > 0 else 0
        
        # Positional statistics
        if match_positions:
            position_variance = np.var(match_positions)
            position_range = (max(match_positions) - min(match_positions)) / part_length
        else:
            position_variance = 0
            position_range = 0
        
        # Template diversity
        template_usage = template_diversity / len(templates) if templates else 0
        
        # Combine features
        features = [
            total_matches,
            match_density,
            avg_similarity,
            max_similarity,
            complement_ratio,
            position_variance,
            position_range,
            template_usage
        ]
        
        # Apply position weighting if requested
        if position_weight is not None:
            weight_factor = 1.0 / (1.0 + position_weight * 0.1)  # Decay with position
            features = [f * weight_factor for f in features]
        
        return features
    
    def _find_template_matches_in_part(
        self,
        part_seq: str,
        template: str,
        similarity_threshold: float,
        use_complement: bool
    ) -> List[Dict[str, Any]]:
        """Find template matches within a sequence part"""
        
        # Use caching to avoid redundant calculations
        cache_key = f"{part_seq}_{template}_{similarity_threshold}_{use_complement}"
        if cache_key in self._match_cache:
            return self._match_cache[cache_key]
        
        matches = []
        part_len = len(part_seq)
        template_len = len(template)
        
        # Create complement template if needed
        complement_template = None
        if use_complement:
            try:
                complement_template = str(Seq(template).complement())
            except:
                complement_template = None
        
        # Slide template across the part
        for i in range(part_len - template_len + 1):
            window = part_seq[i:i + template_len]
            
            # Check direct match
            similarity = self._calculate_sequence_similarity(template, window)
            if similarity >= similarity_threshold:
                matches.append({
                    'position': i,
                    'similarity': similarity,
                    'match_type': 'direct',
                    'matched_sequence': window
                })
            
            # Check complement match if enabled
            if complement_template:
                comp_similarity = self._calculate_sequence_similarity(complement_template, window)
                if comp_similarity >= similarity_threshold:
                    matches.append({
                        'position': i,
                        'similarity': comp_similarity,
                        'match_type': 'complement',
                        'matched_sequence': window
                    })
        
        # Cache the result
        self._match_cache[cache_key] = matches
        
        return matches
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate similarity between two sequences"""
        
        if len(seq1) != len(seq2) or not seq1 or not seq2:
            return 0.0
        
        # Simple nucleotide match percentage
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        return matches / len(seq1)
    
    def _normalize_features(self, features: List[np.ndarray]) -> List[np.ndarray]:
        """Normalize feature vectors across all sequences"""
        
        if not features:
            return features
        
        # Convert to matrix
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
        """Calculate distance matrix between feature vectors"""
        
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
        self._match_cache.clear()
