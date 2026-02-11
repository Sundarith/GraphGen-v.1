# UCKG Synthetic Data Generation Integration

This directory contains the integration workflow for generating synthetic Q&A data using the **Unified Cybersecurity Knowledge Graph (UCKG)**.

## Overview

This workflow extracts specific **"Incident Response" knowledge triads** from Neo4j, cleans them, and feeds them into GraphGen to generate high-quality Q&A pairs for training a cybersecurity assistant.

### The Knowledge Chain
We specifically target this V-shape relationship structure:
`[Symptom: CAPEC] --[IS_A]--> [Category: ATT&CK] <--(MITIGATES)-- [Solution: MITIGATION]`

*   **CAPEC:** User-facing symptoms ("My server is flooded").
*   **ATT&CK:** Technical category ("Denial of Service").
*   **MITIGATION:** Actionable solution ("Rate Limiting").

### Workflow Architecture (ETL Pipeline)

1.  **Extract (`extract_uckg_raw.py`):** Queries Neo4j for the specific triads. Dumps raw JSONL.
2.  **Filter (`filter_uckg_data.py`):** Whitelists only relevant properties (Name, Description, Example) to reduce noise.
3.  **Clean (`clean_uckg_data.py`):**
    *   Parses messy JSON strings (e.g., `{mitigation=[...]}`).
    *   **Renames Keys:** Standardizes `ucoexNAME` -> `Name`, `ucoexDescription` -> `Description` for clearer LLM prompts.
    *   Polishes formatting (`|` separators -> bullet points).
4.  **Load (`load_to_graphgen.py`):** Reconstructs the graph in GraphGen's internal KuzuDB storage and applies semantic renaming (`IS_A`, `MITIGATES`).
5.  **Generate (`graphgen.run`):** Uses LLM to synthesize Q&A pairs from the curated graph.

## File Structure

*   **Scripts:**
    *   `extract_uckg_raw.py`: Neo4j -> `raw_data.jsonl`
    *   `filter_uckg_data.py`: `raw` -> `filtered_data.jsonl`
    *   `clean_uckg_data.py`: `filtered` -> `clean_data.jsonl`
    *   `load_to_graphgen.py`: `clean` -> KuzuDB
    *   `inspect_kuzu.py`: Verifies KuzuDB content and chain connectivity.
*   **Config:**
    *   `uckg_config.yaml`: GraphGen pipeline configuration (Atomic mode).
*   **Orchestration:**
    *   `generate_uckg.sh`: Master script to run all steps.

## Usage

### Prerequisites
1.  **Environment:** `conda activate graphgen`
2.  **Dependencies:** `pip install -r requirements.txt`
3.  **Neo4j:** Running at `localhost:7687`
4.  **LLM:** `SYNTHESIZER_API_KEY` set in `.env`.

### Running the Full Pipeline
```bash
bash examples/generate/generate_uckg/generate_uckg.sh
```

### Manual Verification
You can inspect the internal database state to verify connectivity:
```bash
python3 examples/generate/generate_uckg/inspect_kuzu.py
```
**Expected Output:**
```text
[SUCCESS] Chain Found:
Chain: [CAPEC: Collect Data...] --[IS_A]--> [ATT&CK: Data from...] <--(MITIGATES)-- [MITIGATION: Filter...]
```

### Step-by-Step Debugging
If you need to debug a specific stage:

```bash
# 1. Extract
python3 examples/generate/generate_uckg/extract_uckg_raw.py --limit 1000

# 2. Filter
python3 examples/generate/generate_uckg/filter_uckg_data.py

# 3. Clean
python3 examples/generate/generate_uckg/clean_uckg_data.py

# 4. Load (Set PYTHONPATH for imports)
# (Recommended: rm -rf cache/graph_kuzu first)
PYTHONPATH=. python3 examples/generate/generate_uckg/load_to_graphgen.py --dir cache

# 5. Generate
python3 -m graphgen.run --config_file examples/generate/generate_uckg/uckg_config.yaml
```
