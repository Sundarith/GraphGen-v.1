#!/bin/bash
set -e

echo "=== Step 1: Extract Raw Data (Neo4j -> JSONL) ==="
python3 examples/generate/generate_uckg/extract_uckg_raw.py --limit 1000

echo "=== Step 2: Filter Properties (Keep only Name, Desc, Example) ==="
python3 examples/generate/generate_uckg/filter_uckg_data.py

echo "=== Step 3: Clean Data (Parse JSON strings, Final Cleanup) ==="
python3 examples/generate/generate_uckg/clean_uckg_data.py

echo "=== Step 4: Load to GraphGen (JSONL -> KuzuDB) ==="
# OPTION A: Rich Atomic (Bakes Mitigation into CAPEC Description) - BEST FOR ATOMIC QA
python3 examples/generate/generate_uckg/load_rich_atomic.py --dir cache

# OPTION B: Clean Graph (Keeps nodes separate) - BEST FOR MULTI-HOP
# python3 examples/generate/generate_uckg/load_clean_graph.py --dir cache

echo "=== Step 5: Run GraphGen Pipeline (Atomic Generation) ==="
python3 -m graphgen.run --config_file examples/generate/generate_uckg/uckg_config.yaml