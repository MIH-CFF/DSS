#!/usr/bin/env python3
"""
Comprehensive test script for DSS analysis methods using all datasets.
Tests all four analysis methods with all available datasets to identify dimension issues.
"""

import os
import sys
import traceback
import numpy as np
from typing import List, Dict, Tuple, Any
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.plugin_loader import plugin_loader
from src.core.plugin_registry import plugin_registry
from src.core.interfaces import SequenceData
from src.adapters.biopython_adapter import BioPythonSequenceLoader

class DatasetTester:
    """Comprehensive tester for all datasets and methods"""
    
    def __init__(self):
        self.loader = BioPythonSequenceLoader()
        self.dataset_paths = {
            '16sRiboDNA': 'Datasets/16sRiboDNA',
            '18EutherianMammal': 'Datasets/18EutherianMammal', 
            '21 HIV-1': 'Datasets/21 HIV-1',
            '48 HEV': 'Datasets/48 HEV',
            # Add more datasets as needed
        }
        self.test_results = {}
        
    def load_dataset_sequences(self, dataset_path: str, max_sequences: int = None) -> Tuple[List[SequenceData], List[str]]:
        """Load sequences from a dataset directory"""
        sequences = []
        fasta_files = []
        
        if not os.path.exists(dataset_path):
            print(f"❌ Dataset path does not exist: {dataset_path}")
            return [], []
            
        # Find all FASTA files
        for filename in os.listdir(dataset_path):
            if filename.endswith('.fasta') and not filename.startswith('desktop'):
                fasta_files.append(os.path.join(dataset_path, filename))
        
        # Sort for consistent ordering
        fasta_files.sort()
        
        # Limit number of files if specified
        if max_sequences:
            fasta_files = fasta_files[:max_sequences]
        
        print(f"  Found {len(fasta_files)} FASTA files")
        
        # Load sequences
        for i, fasta_file in enumerate(fasta_files):
            try:
                file_sequences = self.loader.load_sequences(fasta_file)
                sequences.extend(file_sequences)
                print(f"    Loaded {len(file_sequences)} sequences from {os.path.basename(fasta_file)}")
                
                # Limit total sequences if needed
                if max_sequences and len(sequences) >= max_sequences:
                    sequences = sequences[:max_sequences]
                    break
                    
            except Exception as e:
                print(f"    ⚠️  Failed to load {fasta_file}: {e}")
        
        print(f"  Total sequences loaded: {len(sequences)}")
        
        return sequences, [os.path.basename(f) for f in fasta_files]
    
    def analyze_sequence_properties(self, sequences: List[SequenceData]) -> Dict[str, Any]:
        """Analyze properties of loaded sequences"""
        if not sequences:
            return {}
        
        lengths = [len(seq.sequence) for seq in sequences]
        
        properties = {
            'count': len(sequences),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'avg_length': np.mean(lengths),
            'std_length': np.std(lengths),
            'length_variance': max(lengths) - min(lengths)
        }
        
        return properties
    
    def test_method_with_dataset(self, method_name: str, processor, sequences: List[SequenceData], dataset_name: str) -> Dict[str, Any]:
        """Test a specific method with a dataset"""
        result = {
            'success': False,
            'error': None,
            'execution_time': 0,
            'distance_matrix_shape': None,
            'feature_dimension': None,
            'metadata': {}
        }
        
        try:
            print(f"    Testing {method_name}...")
            
            # Get default configuration
            config = processor.get_default_config()
            
            # Adjust configuration based on sequence properties if needed
            seq_properties = self.analyze_sequence_properties(sequences)
            config = self._adjust_config_for_dataset(config, seq_properties, dataset_name)
            
            # Start timing
            import time
            start_time = time.time()
            
            # Run the analysis
            analysis_result = processor.process_sequences(sequences, config)
            
            # Record timing
            result['execution_time'] = time.time() - start_time
            
            # Extract results
            result['success'] = True
            result['distance_matrix_shape'] = analysis_result.distance_matrix.shape if analysis_result.distance_matrix is not None else None
            result['feature_dimension'] = analysis_result.metadata.get('feature_dimension', 'N/A')
            result['metadata'] = analysis_result.metadata
            
            print(f"      ✅ Success: {result['distance_matrix_shape']}, Features: {result['feature_dimension']}")
            
        except Exception as e:
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()
            print(f"      ❌ Failed: {e}")
            
        return result
    
    def _adjust_config_for_dataset(self, config, seq_properties, dataset_name):
        """Adjust configuration parameters based on dataset characteristics"""
        if not seq_properties:
            return config
        
        params = config.parameters.copy()
        avg_length = seq_properties.get('avg_length', 1000)
        min_length = seq_properties.get('min_length', 100)
        
        # Adjust parameters based on sequence length and dataset type
        if config.name == "Template Matching":
            # Adjust template length based on sequence length
            if avg_length < 500:
                params['template_length'] = min(15, max(5, int(avg_length * 0.05)))
                params['sliding_window_step'] = max(1, params['template_length'] // 3)
            elif avg_length > 10000:
                params['template_length'] = min(50, max(20, int(avg_length * 0.002)))
                params['sliding_window_step'] = max(5, params['template_length'] // 4)
                
        elif config.name == "Chaos Game Frequency":
            # Adjust window size based on sequence length
            if avg_length < 1000:
                params['window_size'] = max(100, min(int(avg_length * 0.8), 500))
                params['step_size'] = max(10, params['window_size'] // 4)
                params['grid_resolution'] = 16  # Smaller grid for short sequences
            elif avg_length > 5000:
                params['window_size'] = min(2000, max(1000, int(avg_length * 0.3)))
                params['step_size'] = max(100, params['window_size'] // 10)
                
        elif config.name == "Part-wise Template Matching":
            # Adjust part size based on sequence length
            if avg_length < 500:
                params['part_size'] = min(int(avg_length * 0.4), 100)
                params['overlap'] = max(5, params['part_size'] // 3)
                params['template_length'] = min(10, max(5, params['part_size'] // 4))
            elif avg_length > 5000:
                params['part_size'] = min(200, max(50, int(avg_length * 0.02)))
                params['overlap'] = params['part_size'] // 2
                params['template_length'] = min(25, max(10, params['part_size'] // 5))
        
        # Create new config with adjusted parameters
        from src.core.interfaces import MethodConfig
        return MethodConfig(
            name=config.name,
            parameters=params,
            description=config.description
        )
    
    def run_comprehensive_tests(self, max_sequences_per_dataset: int = 10):
        """Run comprehensive tests on all datasets and methods"""
        print("🧬 Starting Comprehensive DSS Dataset Testing...")
        print("=" * 60)
        
        # Load all plugins
        plugin_loader.load_all_plugins()
        processors = plugin_registry.get_processors()
        
        print(f"Loaded {len(processors)} processors:")
        for processor in processors:
            print(f"  - {processor.get_method_name()}")
        print()
        
        # Test each dataset
        for dataset_name, dataset_path in self.dataset_paths.items():
            print(f"📂 Testing Dataset: {dataset_name}")
            print(f"   Path: {dataset_path}")
            
            # Load sequences
            sequences, file_list = self.load_dataset_sequences(dataset_path, max_sequences_per_dataset)
            
            if not sequences:
                print(f"   ❌ No sequences loaded, skipping dataset")
                continue
            
            # Analyze sequence properties
            seq_properties = self.analyze_sequence_properties(sequences)
            print(f"   📊 Sequence Properties:")
            print(f"      Count: {seq_properties['count']}")
            print(f"      Length Range: {seq_properties['min_length']}-{seq_properties['max_length']} (avg: {seq_properties['avg_length']:.1f})")
            print(f"      Length Variance: {seq_properties['length_variance']}")
            
            # Initialize results for this dataset
            self.test_results[dataset_name] = {
                'sequences': sequences,
                'properties': seq_properties,
                'file_list': file_list,
                'method_results': {}
            }
            
            # Test each method
            for processor in processors:
                method_name = processor.get_method_name()
                result = self.test_method_with_dataset(method_name, processor, sequences, dataset_name)
                self.test_results[dataset_name]['method_results'][method_name] = result
            
            print()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        
        for dataset_name, dataset_results in self.test_results.items():
            print(f"\n📂 Dataset: {dataset_name}")
            print(f"   Sequences: {dataset_results['properties']['count']}")
            print(f"   Avg Length: {dataset_results['properties']['avg_length']:.1f}")
            
            for method_name, result in dataset_results['method_results'].items():
                total_tests += 1
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                
                if result['success']:
                    successful_tests += 1
                    print(f"   {status} {method_name}")
                    print(f"      Distance Matrix: {result['distance_matrix_shape']}")
                    print(f"      Features: {result['feature_dimension']}")
                    print(f"      Time: {result['execution_time']:.2f}s")
                else:
                    failed_tests += 1
                    print(f"   {status} {method_name}")
                    print(f"      Error: {result['error']}")
        
        print(f"\n📊 SUMMARY")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Report specific issues
        self._report_dimension_issues()
        self._report_performance_issues()
        
    def _report_dimension_issues(self):
        """Report dimension-related issues"""
        print(f"\n🔍 DIMENSION ANALYSIS")
        print("-" * 40)
        
        dimension_issues = []
        
        for dataset_name, dataset_results in self.test_results.items():
            for method_name, result in dataset_results['method_results'].items():
                if not result['success'] and result['error']:
                    error_msg = result['error'].lower()
                    if any(keyword in error_msg for keyword in ['dimension', 'shape', 'matrix', 'array', 'size']):
                        dimension_issues.append({
                            'dataset': dataset_name,
                            'method': method_name,
                            'error': result['error'],
                            'sequences': dataset_results['properties']['count'],
                            'avg_length': dataset_results['properties']['avg_length']
                        })
        
        if dimension_issues:
            print("Found dimension-related issues:")
            for issue in dimension_issues:
                print(f"  ❌ {issue['dataset']} -> {issue['method']}")
                print(f"     Sequences: {issue['sequences']}, Avg Length: {issue['avg_length']:.1f}")
                print(f"     Error: {issue['error']}")
                print()
        else:
            print("✅ No dimension issues detected")
    
    def _report_performance_issues(self):
        """Report performance-related issues"""
        print(f"\n⏱️  PERFORMANCE ANALYSIS")
        print("-" * 40)
        
        slow_tests = []
        
        for dataset_name, dataset_results in self.test_results.items():
            for method_name, result in dataset_results['method_results'].items():
                if result['success'] and result['execution_time'] > 30:  # > 30 seconds
                    slow_tests.append({
                        'dataset': dataset_name,
                        'method': method_name,
                        'time': result['execution_time'],
                        'sequences': dataset_results['properties']['count']
                    })
        
        if slow_tests:
            print("Slow tests (>30s):")
            for test in sorted(slow_tests, key=lambda x: x['time'], reverse=True):
                print(f"  ⏰ {test['dataset']} -> {test['method']}: {test['time']:.1f}s ({test['sequences']} seqs)")
        else:
            print("✅ All tests completed in reasonable time")

def main():
    """Main test execution"""
    tester = DatasetTester()
    
    # Run tests with limited sequences for initial testing
    # tester.run_comprehensive_tests(max_sequences_per_dataset=5)  # Start with 5 sequences per dataset
    tester.run_comprehensive_tests()  # Start with 5 sequences per dataset
    
    # Generate report
    tester.generate_report()
    
    print("\n🎯 Next Steps:")
    print("1. Review any dimension issues reported above")
    print("2. Check specific error tracebacks for failed tests")
    print("3. Adjust algorithm parameters for problematic datasets")
    print("4. Re-run tests with full datasets once issues are resolved")

if __name__ == "__main__":
    main()
