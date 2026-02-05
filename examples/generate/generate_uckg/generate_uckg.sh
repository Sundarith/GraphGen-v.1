#!/bin/bash
set -e

echo "=== Step 1: Extract Raw Data (Neo4j -> JSONL) ==="
python3 examples/generate/generate_uckg/extract_uckg_raw.py --limit 1000

echo "=== Step 2: Clean & Transform Data (Parsing JSON fields, Removing Embeddings) ==="
python3 examples/generate/generate_uckg/clean_uckg_data.py

echo "=== Step 3: Load to GraphGen (JSONL -> KuzuDB) ==="
python3 examples/generate/generate_uckg/load_to_graphgen.py --dir cache

echo "=== Step 4: Run GraphGen Pipeline (Atomic Generation) ==="
# Ensure config uses atomic method
python3 -m graphgen.run --config_file examples/generate/generate_uckg/uckg_config.yaml