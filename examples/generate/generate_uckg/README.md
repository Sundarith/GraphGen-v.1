# UCKG Synthetic Data Generation Integration

This directory contains the integration workflow for generating synthetic Q&A data using the **Unified Cybersecurity Knowledge Graph (UCKG)** as the source.

## Overview

Unlike standard GraphGen workflows that extract entities from raw text, this workflow leverages the existing, high-quality knowledge graph stored in UCKG's Neo4j database. It bridges the gap between Neo4j and GraphGen's internal KuzuDB storage to enable advanced synthetic data generation (e.g., Chain-of-Thought, Multi-hop QA).

### Workflow Architecture

1.  **Bridge (Import):** Connects to the local UCKG Neo4j instance, reads nodes and relationships, and imports them into GraphGen's internal KuzuDB storage.
    *   *Optimization:* Automatically filters out high-dimensional embedding vectors to keep the cache lightweight.
    *   *Context:* Synthesizes a "description" field for each entity by combining `name`, `summary`, and `definition` properties, which is crucial for the LLM's context.
2.  **Partition:** Uses the Leiden community detection algorithm to group related cybersecurity entities into communities.
3.  **Generate:** Feeds these communities to the `CoTGenerator` (Chain-of-Thought) to produce high-quality Q&A pairs.

## File Structure

*   `import_uckg.py`: The bridge script. Connects to Neo4j via the Bolt driver, cleans properties (removing embeddings), and populates the KuzuDB.
*   `uckg_config.yaml`: GraphGen pipeline configuration. It defines the `partition` and `generate` steps, skipping the usual extraction phase.
*   `generate_uckg.sh`: The master execution script. Runs the import followed by the generation pipeline.
*   `dummy.txt`: A placeholder file required to initialize the GraphGen source operator.

## Usage

### Prerequisites
Ensure the UCKG Neo4j database is running and accessible.
```bash
# Install dependencies
pip install neo4j kuzu
```

### Running the Pipeline
Execute the shell script to start the import and generation process:

```bash
bash examples/generate/generate_uckg/generate_uckg.sh
```

**Note:** By default, the script imports **all** nodes from Neo4j. To test with a smaller subset, you can modify `generate_uckg.sh` to add the `--limit` flag:
```bash
python3 examples/generate/generate_uckg/import_uckg.py --dir cache --limit 1000
```

## Research Notes regarding Embeddings

The UCKG Neo4j database contains pre-computed embedding vectors for semantic search. This integration workflow **explicitly excludes** these vectors during the import phase (`clean_properties` function in `import_uckg.py`).

**Reasoning:**
1.  **Storage Efficiency:** Storing thousands of high-dimensional float vectors in the intermediate KuzuDB cache would significantly bloat file size and slow down I/O.
2.  **Relevance:** The generation phase relies on textual metadata (descriptions, names, types) to prompt the LLM. The raw vectors are not interpretable by the LLM in this context and are thus unnecessary for synthetic text generation.
