$ python3 test_all_datasets.py 
Registered processor: Dynamic Part-wise Template Matching
Registered processor: Chaos Game Frequency Representation
Registered processor: Template Matching
Registered processor: Part-wise Template Matching
Registered loader: BioPythonSequenceLoader
Registered visualizer: MatplotlibTreeVisualizer
🧬 Starting Comprehensive DSS Dataset Testing...
============================================================
Registered processor: Dynamic Part-wise Template Matching
Registered processor: Chaos Game Frequency Representation
Registered processor: Template Matching
Registered processor: Part-wise Template Matching
Registered loader: BioPythonSequenceLoader
Registered visualizer: MatplotlibTreeVisualizer
Loaded 4 processors:
  - Dynamic Part-wise Template Matching
  - Chaos Game Frequency Representation
  - Template Matching
  - Part-wise Template Matching

📂 Testing Dataset: 16sRiboDNA
   Path: Datasets/16sRiboDNA
  Found 10 FASTA files
    Loaded 1 sequences from J01859.fasta
    Loaded 1 sequences from KP317497.fasta
    Loaded 1 sequences from NR037066.fasta
    Loaded 1 sequences from NR040849.fasta
    Loaded 1 sequences from NR117152.fasta
    Loaded 1 sequences from NR132306.fasta
    Loaded 1 sequences from NR134817.fasta
    Loaded 1 sequences from NR134818.fasta
    Loaded 1 sequences from NR136784.fasta
    Loaded 1 sequences from NR148244.fasta
  Total sequences loaded: 10
   📊 Sequence Properties:
      Count: 10
      Length Range: 1513-1541 (avg: 1519.7)
      Length Variance: 28
    Testing Dynamic Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 1024
    Testing Chaos Game Frequency Representation...
      ✅ Success: (10, 10), Features: 256
    Testing Template Matching...
      ✅ Success: (10, 10), Features: 500
    Testing Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 100

📂 Testing Dataset: 18EutherianMammal
   Path: Datasets/18EutherianMammal
  Found 10 FASTA files
    Loaded 1 sequences from D38113.fasta
    Loaded 1 sequences from D38114.fasta
    Loaded 1 sequences from D38115.fasta
    Loaded 1 sequences from D38116.fasta
    Loaded 1 sequences from U20753.fasta
    Loaded 1 sequences from V00654.fasta
    Loaded 1 sequences from V00662.fasta
    Loaded 1 sequences from V00711.fasta
    Loaded 1 sequences from X14848.fasta
    Loaded 1 sequences from X61145.fasta
  Total sequences loaded: 10
   📊 Sequence Properties:
      Count: 10
      Length Range: 16295-17009 (avg: 16477.9)
      Length Variance: 714
    Testing Dynamic Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 1024
    Testing Chaos Game Frequency Representation...
      ✅ Success: (10, 10), Features: 256
    Testing Template Matching...
      ✅ Success: (10, 10), Features: 500
    Testing Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 100

📂 Testing Dataset: 21 HIV-1
   Path: Datasets/21 HIV-1
  Found 10 FASTA files
    Loaded 1 sequences from a1-AF004885.fasta
    Loaded 1 sequences from a2-AF069671.fasta
    Loaded 1 sequences from a3-U51190.fasta
    Loaded 1 sequences from a4-AF069672.fasta
    Loaded 1 sequences from a5-AF107771.fasta
    Loaded 1 sequences from a6-M62320.fasta
    Loaded 1 sequences from a7-AF069670.fasta
    Loaded 1 sequences from b1-AF042101.fasta
    Loaded 1 sequences from b2-U37270.fasta
    Loaded 1 sequences from b3-U43096.fasta
  Total sequences loaded: 10
   📊 Sequence Properties:
      Count: 10
      Length Range: 8791-9739 (avg: 9083.6)
      Length Variance: 948
    Testing Dynamic Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 1024
    Testing Chaos Game Frequency Representation...
      ✅ Success: (10, 10), Features: 256
    Testing Template Matching...
      ✅ Success: (10, 10), Features: 500
    Testing Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 100

📂 Testing Dataset: 48 HEV
   Path: Datasets/48 HEV
  Found 10 FASTA files
    Loaded 1 sequences from Arkell.fasta
    Loaded 1 sequences from B1(Bur-82).fasta
    Loaded 1 sequences from B2(Bur-86).fasta
    Loaded 1 sequences from C1(CHT-88).fasta
    Loaded 1 sequences from C2(KS2-87).fasta
    Loaded 1 sequences from C3(CHT-87).fasta
    Loaded 1 sequences from C4(Uigh179).fasta
    Loaded 1 sequences from CCC220.fasta
    Loaded 1 sequences from China_Hebei.fasta
    Loaded 1 sequences from HE-JA1.fasta
  Total sequences loaded: 10
   📊 Sequence Properties:
      Count: 10
      Length Range: 7176-7258 (avg: 7210.5)
      Length Variance: 82
    Testing Dynamic Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 1024
    Testing Chaos Game Frequency Representation...
      ✅ Success: (10, 10), Features: 256
    Testing Template Matching...
      ✅ Success: (10, 10), Features: 500
    Testing Part-wise Template Matching...
      ✅ Success: (10, 10), Features: 100

📋 COMPREHENSIVE TEST REPORT
============================================================

📂 Dataset: 16sRiboDNA
   Sequences: 10
   Avg Length: 1519.7
   ✅ PASS Dynamic Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 1024
      Time: 0.09s
   ✅ PASS Chaos Game Frequency Representation
      Distance Matrix: (10, 10)
      Features: 256
      Time: 0.04s
   ✅ PASS Template Matching
      Distance Matrix: (10, 10)
      Features: 500
      Time: 0.05s
   ✅ PASS Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 100
      Time: 0.02s

📂 Dataset: 18EutherianMammal
   Sequences: 10
   Avg Length: 16477.9
   ✅ PASS Dynamic Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 1024
      Time: 1.44s
   ✅ PASS Chaos Game Frequency Representation
      Distance Matrix: (10, 10)
      Features: 256
      Time: 0.35s
   ✅ PASS Template Matching
      Distance Matrix: (10, 10)
      Features: 500
      Time: 0.48s
   ✅ PASS Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 100
      Time: 0.09s

📂 Dataset: 21 HIV-1
   Sequences: 10
   Avg Length: 9083.6
   ✅ PASS Dynamic Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 1024
      Time: 0.57s
   ✅ PASS Chaos Game Frequency Representation
      Distance Matrix: (10, 10)
      Features: 256
      Time: 0.20s
   ✅ PASS Template Matching
      Distance Matrix: (10, 10)
      Features: 500
      Time: 0.28s
   ✅ PASS Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 100
      Time: 0.05s

📂 Dataset: 48 HEV
   Sequences: 10
   Avg Length: 7210.5
   ✅ PASS Dynamic Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 1024
      Time: 0.49s
   ✅ PASS Chaos Game Frequency Representation
      Distance Matrix: (10, 10)
      Features: 256
      Time: 0.16s
   ✅ PASS Template Matching
      Distance Matrix: (10, 10)
      Features: 500
      Time: 0.22s
   ✅ PASS Part-wise Template Matching
      Distance Matrix: (10, 10)
      Features: 100
      Time: 0.04s

📊 SUMMARY
   Total Tests: 16
   Successful: 16 (100.0%)
   Failed: 0 (0.0%)

🔍 DIMENSION ANALYSIS
----------------------------------------
✅ No dimension issues detected

⏱️  PERFORMANCE ANALYSIS
----------------------------------------
✅ All tests completed in reasonable time

🎯 Next Steps:
1. Review any dimension issues reported above
2. Check specific error tracebacks for failed tests
3. Adjust algorithm parameters for problematic datasets
4. Re-run tests with full datasets once issues are resolved
