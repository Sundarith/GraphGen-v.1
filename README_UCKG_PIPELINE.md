# UCKG Synthetic Data Pipeline: Master Architecture

This document serves as the master blueprint for the UCKG synthetic data generation factory. We have successfully re-engineered the GraphGen academic framework into a production-grade, "Text-to-Graph" cybersecurity pipeline.

---

## 1. The Core Problem & Solution
**The Problem:** The original UCKG Neo4j database suffers from poor, sparse ontology (broken links between attacks and mitigations). Standard graph extraction fails because the underlying data is disconnected.
**The Solution (Text-to-Graph):** We bypass the broken Neo4j ontology by flattening the data into rich "Fat Paragraphs" (Incident Reports) and utilizing Gemini to hallucinate a *perfect, mathematically connected* graph from scratch in KuzuDB.

---

## 2. The 5-Step Pipeline Workflow

### Step 1: The ETL Data Dump
*   **Script:** `examples/generate/generate_uckg/create_text_dump.py`
*   **Action:** Reads the raw Neo4j JSON export and weaves 8+ distinct CAPEC properties (Techniques, Mitigations, Skill Levels) into a single, dense "Incident Report" paragraph.
*   **Output:** `uckg_text_dump_test.jsonl`

### Step 2: The `build_kg` Extraction (Monkey-Patched)
*   **Script:** `run_uckg_pipeline.py` (Called via `bash run_test.sh`)
*   **Action:** A custom wrapper script that "Monkey-Patches" the GraphGen engine in memory. It swaps out the engine's original biology prompts for our custom **Cybersecurity Extraction Prompt** (`kg_extraction_uckg.py`). 
*   **Result:** Gemini reads the Fat Paragraphs and mathematically extracts perfectly typed entities (`attack_pattern`, `mitigation`, `software`) and edges into the `cache/graph_kuzu` database.

### Step 3: The `partition` Algorithm
*   **Script:** `bash run_partition.sh`
*   **Action:** Runs the **Leiden Algorithm** on the KuzuDB graph. It groups the hundreds of nodes into tight, semantic "Communities" (e.g., separating the "Reconnaissance" nodes from the "Exploit" nodes).
*   **Key Parameters (`uckg_partition_test.yaml`):**
    *   `max_size: 15-20` (Prevents the LLM from getting overwhelmed).
    *   `random_seed` (Changing this alters the community borders, allowing us to generate completely new training data from the exact same graph without overfitting).

### Step 4: The `generate` Module (Chain-of-Thought)
*   **Prompt:** `multi_hop_generation_uckg.py`
*   **Action:** Takes the partitioned communities and feeds them to the LLM (`gemini-3.1-pro-preview`) with a "Strict Professor" prompt. 
*   **The CoT Upgrade:** The prompt forces the LLM to use transition words (`First`, `Because of this`, `Therefore`), resulting in pure Chain-of-Thought (CoT) reasoning traces that connect 3-5 nodes per answer.
*   **Output:** `cache/output/*/generate/sharegpt.jsonl`

---

## 3. The Modular Execution Scripts
Instead of running a monolithic pipeline that crashes easily, we broke the factory into modular Bash scripts for ultimate control:

*   `bash run_test.sh`: Runs **only** the `build_kg` extraction. (Use this when processing new text data into KuzuDB).
*   `bash run_partition.sh`: Runs **only** the Partition and Generate steps on the existing KuzuDB graph. (Use this when farming new Q&A pairs by changing the `random_seed`).
*   `bash run_generate.sh`: Runs **only** the Generation step on an existing partition file. (Use this for quickly testing new Prompt instructions without waiting for Leiden to run).

---

## 4. Visualizing the Engine (Neo4j Sandboxes)
To visually verify the AI's math without corrupting the production UCKG database, we use isolated Docker Sandboxes.

*   **Export the Main Graph:** `python3 examples/generate/generate_uckg/export_kuzu_to_neo4j.py` (Pushes the massive KuzuDB web to Sandbox 1 on port 7688).
*   **Export Isolated Communities:** `python3 examples/generate/generate_uckg/export_communities_to_neo4j.py` (Pushes the severed, partitioned islands to Sandbox 2 on port 7689 so you can see exactly what the LLM sees).
