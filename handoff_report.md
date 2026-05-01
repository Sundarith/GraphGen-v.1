# UCKG Synthetic Data Pipeline: Progress Report

## 1. Goal & Context
The objective was to integrate a highly scalable Supervised Fine-Tuning (SFT) synthetic data generation pipeline directly into the UCKG repository. This replaces the legacy, manual Ground Truth generation scripts previously used by the team, moving from a manual proof-of-concept to a production-grade automated pipeline.

## 2. The Automated ETL Pipeline (`run_etl_pipeline.sh`)
We successfully built and deployed Phase 1 of the architecture. This automated script replaces manual database querying by executing four steps:

1.  **Extract:** Automatically pulls complete "Incident Response Triads" (`[CAPEC] -> [ATT&CK] <- [MITIGATION]`) directly from the live Neo4j database.
2.  **Filter:** Strips unnecessary system properties to optimize the downstream LLM context window.
3.  **Clean:** Parses nested stringified JSON arrays into readable Markdown bullet points.
4.  **Load & Separate (The "Clean Graph" Strategy):** We initialize a highly-optimized local `KuzuDB` staging database. Crucially, we shifted from a "Fat Node" approach to a **Clean Topological Graph**. We keep the CAPEC, ATT&CK, and MITIGATION nodes structurally distinct and connect them via explicitly defined relationships (`IS_A`, `MITIGATES`). This strictly enables complex **Multi-Hop Reasoning** for the LLM during generation.

## 3. Current Status & Results
*   **Data Staged:** The ETL pipeline successfully extracted **644 complete paths** spanning **559 unique CAPEC nodes**. 
*   **Visualized:** We built a custom diagnostic tool (`visualize_kuzu.py`) that successfully mapped the staged KuzuDB data, proving the topological connections are intact and ready for traversal.
*   **Deployed:** The ETL pipeline, custom scripts, and the `sft_engine` have been successfully committed and pushed to the remote `qa-engine` branch.
*   **Data Integrity:** A strict `.gitignore` was implemented to ensure the massive KuzuDB staging area and intermediate JSONL data files are never accidentally pushed to the remote repository.

## 4. Next Steps
With the data successfully separated and staged in KuzuDB, the next phase is to build the **Generation Pipeline** (`run_generation.sh`). This script will utilize the `sft_engine` to traverse the database, apply community partitioning algorithms, and generate the final Multi-Hop Q&A pairs for LLM fine-tuning.
