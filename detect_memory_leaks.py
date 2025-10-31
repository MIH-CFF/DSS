#!/usr/bin/env python3
"""
Memory leak detector for DSS Application
Runs targeted memory leak detection tests
"""

import gc
import tracemalloc
import subprocess
import sys
import time
from pathlib import Path


def run_leak_test():
    """Run memory leak detection"""
    print("=" * 60)
    print("DSS Memory Leak Detection")
    print("=" * 60)
    
    # Start memory tracking
    tracemalloc.start()
    
    print("\n1. Running memory leak tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/performance/test_memory_leaks.py",
        "-v",
        "-m", "memory",
        "--tb=short"
    ])
    
    if result.returncode != 0:
        print("\n❌ Memory leak tests failed!")
        return False
    
    print("\n✅ Memory leak tests passed!")
    
    # Take memory snapshot
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    print("\n" + "=" * 60)
    print("Top 10 Memory Allocations:")
    print("=" * 60)
    
    for stat in top_stats[:10]:
        print(f"{stat}")
    
    tracemalloc.stop()
    
    return True


def run_profiling():
    """Run memory profiling on specific components"""
    print("\n" + "=" * 60)
    print("Running Memory Profiling...")
    print("=" * 60)
    
    # Create a simple profiling script
    profile_script = """
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_profiler import profile
from src.ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

@profile
def test_main_window():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.close()

if __name__ == '__main__':
    test_main_window()
"""
    
    # Write temporary script
    script_path = Path("temp_profile.py")
    script_path.write_text(profile_script)
    
    try:
        print("\nProfiling MainWindow creation...")
        subprocess.run([
            sys.executable, "-m", "memory_profiler",
            "temp_profile.py"
        ])
    finally:
        # Clean up
        if script_path.exists():
            script_path.unlink()
    
    print("\n✅ Profiling complete!")


def check_resource_leaks():
    """Check for resource leaks (file handles, etc.)"""
    print("\n" + "=" * 60)
    print("Checking Resource Leaks...")
    print("=" * 60)
    
    try:
        import psutil
        process = psutil.Process()
        
        print(f"\nCurrent Process Stats:")
        print(f"  Open Files: {len(process.open_files())}")
        print(f"  Connections: {len(process.connections())}")
        print(f"  Memory RSS: {process.memory_info().rss / (1024**2):.2f} MB")
        print(f"  Memory VMS: {process.memory_info().vms / (1024**2):.2f} MB")
        
        if hasattr(process, 'num_fds'):
            print(f"  File Descriptors: {process.num_fds()}")
        
    except ImportError:
        print("⚠️  psutil not installed, skipping resource checks")
        print("   Install with: pip install psutil")


def main():
    """Main execution"""
    print("\n🔍 Starting comprehensive memory leak detection...\n")
    
    success = True
    
    # Run leak tests
    if not run_leak_test():
        success = False
    
    # Check resources
    check_resource_leaks()
    
    # Optional: Run profiling
    try:
        import memory_profiler
        run_profiling()
    except ImportError:
        print("\n⚠️  memory_profiler not installed, skipping profiling")
        print("   Install with: pip install memory-profiler")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Memory leak detection complete - No significant leaks found!")
    else:
        print("❌ Memory leak detection found issues!")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
