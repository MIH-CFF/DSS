"""
Chaos Game Frequency plugin implementation.
This implements Chaos Game Representation (CGR) for DNA sequence analysis.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import pairwise_distances
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor

from src.core.interfaces import (
    ISequenceProcessor, SequenceData, AnalysisResult, MethodConfig
)


class ChaosGameFrequencyProcessor(ISequenceProcessor):
    """
    Chaos Game Representation (CGR) processor for DNA sequence analysis.
    
    CGR maps DNA sequences to 2D coordinates using a chaos game approach,
    then analyzes frequency distributions in different regions of the CGR space.
    """
    
    def __init__(self):
        # CGR coordinate mapping for nucleotides
        self.nucleotide_coords = {
            'A': (0, 0),     # Bottom-left
            'T': (1, 0),     # Bottom-right
            'G': (0, 1),     # Top-left
            'C': (1, 1)      # Top-right
        }
        
    def get_method_name(self) -> str:
        """Return the name of the processing method"""
        return "Chaos Game Frequency"
    
    def get_description(self) -> str:
        """Return a description of the method"""
        return ("Chaos Game Representation (CGR) based frequency analysis. "
                "Maps DNA sequences to 2D space using chaos game rules and "
                "analyzes frequency distributions in different regions for "
                "phylogenetic reconstruction.")
    
    def get_default_config(self) -> MethodConfig:
        """Return default configuration for this method"""
        return MethodConfig(
            name=self.get_method_name(),
            parameters={
                'window_size': 1000,
                'step_size': 500,
                'grid_resolution': 64,
                'min_frequency': 1,
                'normalize_frequencies': True,
                'use_sliding_window': True,
                'cgr_iterations': None  # None means use full sequence
            },
            description=self.get_description()
        )
    
    def validate_config(self, config: MethodConfig) -> bool:
        """Validate configuration parameters"""
        params = config.parameters
        
        # Check required parameters
        required_params = ['window_size', 'step_size', 'grid_resolution']
        for param in required_params:
            if param not in params:
                return False
        
        # Validate parameter ranges
        if not (100 <= params['window_size'] <= 10000):
            return False
        
        if not (10 <= params['step_size'] <= params['window_size']):
            return False
        
        if not (8 <= params['grid_resolution'] <= 256):
            return False
        
        min_freq = params.get('min_frequency', 1)
        if not (0 <= min_freq <= 100):
            return False
        
        cgr_iter = params.get('cgr_iterations')
        if cgr_iter is not None and not (100 <= cgr_iter <= 50000):
            return False
        
        return True
    
    def process_sequences(self, sequences: List[SequenceData], config: MethodConfig) -> AnalysisResult:
        """Process sequences using Chaos Game Representation"""
        
        if not sequences:
            raise ValueError("No sequences provided for analysis")
        
        if len(sequences) < 2:
            raise ValueError("At least 2 sequences are required for comparison")
        
        params = config.parameters
        window_size = params['window_size']
        step_size = params['step_size']
        grid_resolution = params['grid_resolution']
        min_frequency = params.get('min_frequency', 1)
        normalize_freq = params.get('normalize_frequencies', True)
        use_sliding = params.get('use_sliding_window', True)
        cgr_iterations = params.get('cgr_iterations')
        
        print(f"Processing {len(sequences)} sequences with Chaos Game Representation...")
        
        # Extract CGR-based features
        features = []
        sequence_names = []
        
        for i, seq_data in enumerate(sequences):
            sequence_names.append(seq_data.name)
            print(f"  Processing sequence {i+1}/{len(sequences)}: {seq_data.name}")
            
            # Calculate CGR features
            cgr_features = self._extract_cgr_features(
                seq_data.sequence,
                window_size,
                step_size,
                grid_resolution,
                min_frequency,
                normalize_freq,
                use_sliding,
                cgr_iterations
            )
            
            features.append(cgr_features)
        
        # Calculate distance matrix
        print("Calculating distance matrix from CGR features...")
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
                'grid_resolution': grid_resolution
            }
        )
    
    def _extract_cgr_features(
        self,
        sequence: str,
        window_size: int,
        step_size: int,
        grid_resolution: int,
        min_frequency: int,
        normalize_freq: bool,
        use_sliding: bool,
        cgr_iterations: int = None
    ) -> np.ndarray:
        """Extract CGR-based features from a sequence"""
        
        sequence = sequence.upper()
        
        if use_sliding:
            # Use sliding window approach
            windows = self._create_sliding_windows(sequence, window_size, step_size)
        else:
            # Use entire sequence
            windows = [sequence]
        
        all_features = []
        
        for window in windows:
            # Generate CGR coordinates for this window
            cgr_points = self._generate_cgr_coordinates(window, cgr_iterations)
            
            # Calculate frequency distribution in grid
            freq_grid = self._calculate_frequency_grid(
                cgr_points, grid_resolution, min_frequency
            )
            
            # Convert grid to feature vector
            if normalize_freq:
                freq_grid = self._normalize_frequencies(freq_grid)
            
            # Flatten grid to 1D feature vector
            features = freq_grid.flatten()
            all_features.extend(features)
        
        return np.array(all_features)
    
    def _create_sliding_windows(
        self, 
        sequence: str, 
        window_size: int, 
        step_size: int
    ) -> List[str]:
        """Create sliding windows from sequence"""
        windows = []
        seq_len = len(sequence)
        
        for i in range(0, seq_len - window_size + 1, step_size):
            window = sequence[i:i + window_size]
            if len(window) == window_size:
                windows.append(window)
        
        # If no complete windows, use the entire sequence
        if not windows:
            windows.append(sequence)
        
        return windows
    
    def _generate_cgr_coordinates(
        self, 
        sequence: str, 
        max_iterations: int = None
    ) -> List[Tuple[float, float]]:
        """Generate CGR coordinates for a sequence"""
        
        # Filter sequence to valid nucleotides
        valid_sequence = ''.join([base for base in sequence if base in self.nucleotide_coords])
        
        if not valid_sequence:
            return [(0.5, 0.5)]  # Return center point if no valid nucleotides
        
        # Limit iterations if specified
        if max_iterations and len(valid_sequence) > max_iterations:
            valid_sequence = valid_sequence[:max_iterations]
        
        # Start at center of unit square
        current_pos = (0.5, 0.5)
        coordinates = [current_pos]
        
        # Apply chaos game rules
        for nucleotide in valid_sequence:
            if nucleotide in self.nucleotide_coords:
                corner = self.nucleotide_coords[nucleotide]
                
                # Move halfway towards the corner
                new_x = (current_pos[0] + corner[0]) / 2
                new_y = (current_pos[1] + corner[1]) / 2
                
                current_pos = (new_x, new_y)
                coordinates.append(current_pos)
        
        return coordinates
    
    def _calculate_frequency_grid(
        self, 
        coordinates: List[Tuple[float, float]], 
        resolution: int,
        min_frequency: int
    ) -> np.ndarray:
        """Calculate frequency distribution in a grid"""
        
        # Create frequency grid
        freq_grid = np.zeros((resolution, resolution))
        
        # Map coordinates to grid cells
        for x, y in coordinates:
            # Convert to grid indices (handle edge cases)
            grid_x = min(int(x * resolution), resolution - 1)
            grid_y = min(int(y * resolution), resolution - 1)
            
            # Increment frequency
            freq_grid[grid_y, grid_x] += 1
        
        # Apply minimum frequency filter
        freq_grid[freq_grid < min_frequency] = 0
        
        return freq_grid
    
    def _normalize_frequencies(self, freq_grid: np.ndarray) -> np.ndarray:
        """Normalize frequency grid"""
        total_freq = np.sum(freq_grid)
        
        if total_freq > 0:
            return freq_grid / total_freq
        else:
            return freq_grid
    
    def _calculate_distance_matrix(self, features: List[np.ndarray]) -> np.ndarray:
        """Calculate distance matrix between CGR feature vectors"""
        
        if not features:
            raise ValueError("No features provided for distance calculation")
        
        # Convert to matrix
        feature_matrix = np.array(features)
        
        # Use Jensen-Shannon divergence for frequency distributions
        # But fallback to Euclidean if normalization issues
        try:
            distances = self._jensen_shannon_distance_matrix(feature_matrix)
        except:
            # Fallback to Euclidean distance
            distances = pairwise_distances(feature_matrix, metric='euclidean')
        
        return distances
    
    def _jensen_shannon_distance_matrix(self, feature_matrix: np.ndarray) -> np.ndarray:
        """Calculate Jensen-Shannon distance matrix"""
        n_samples = feature_matrix.shape[0]
        distances = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(i + 1, n_samples):
                # Calculate Jensen-Shannon divergence
                p = feature_matrix[i] + 1e-10  # Add small epsilon to avoid log(0)
                q = feature_matrix[j] + 1e-10
                
                # Normalize to probability distributions
                p = p / np.sum(p)
                q = q / np.sum(q)
                
                # Calculate JS divergence
                m = (p + q) / 2
                js_div = 0.5 * self._kl_divergence(p, m) + 0.5 * self._kl_divergence(q, m)
                
                # JS distance is sqrt of JS divergence
                js_distance = np.sqrt(js_div)
                
                distances[i, j] = js_distance
                distances[j, i] = js_distance
        
        return distances
    
    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Kullback-Leibler divergence"""
        # Avoid log(0) by adding small epsilon
        p_safe = np.where(p > 0, p, 1e-10)
        q_safe = np.where(q > 0, q, 1e-10)
        
        return np.sum(p_safe * np.log(p_safe / q_safe))
    
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
