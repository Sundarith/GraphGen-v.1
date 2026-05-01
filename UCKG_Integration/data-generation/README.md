# UCKG Synthetic Data Generation Integration

This directory contains the integration workflow for generating synthetic Q&A data using the **Unified Cybersecurity Knowledge Graph (UCKG)**.

## Session Log (Feb 20): Strategy C Pilot & Mapping

### Goal: Align Training Data with UCKG Benchmark
We identified that the UCKG benchmark asks specific questions but evaluates using ROUGE/Recall against the source context. To beat this, our training data must contain specific questions paired with "Full-Context" answers.

### Progress Today:
1.  **Strategy C Implementation:**
    -   Modified `AtomicGenerator.py` to support multiple Q&A pairs per node.
    -   Updated `atomic_generation.py` to prompt for 3 distinct, specific questions per node (Protocol, Goal, Prerequisites).
    -   Forced every answer to include the **Full Technical Description** from the source text.
2.  **Pilot Run (30 Nodes):**
    -   Successfully generated `training_30_nodes.jsonl` containing 90 Q&A pairs.
    -   Verified that answers are rich and comprehensive (e.g., mentioning L2CAP for BlueSmacking).
3.  **Mapping & Traceability:**
    -   Created `training_30_map.csv` which provides the ID-to-Name mapping for the 30 nodes processed.
    -   This mapping is ready to drive the **Test Set Generation** in the UCKG pipeline.

### Current Status:
-   **Training Data:** `training_30_nodes.jsonl` is ready for SFT.
-   **Methodology:** Verified and reproducible.
-   **Transition:** Moving to the **Fine-Tuning Phase (LLaMA-Factory)**.

## File Structure

*   **Scripts:**
    -   `map_ids_to_names.py`: Creates CSV mapping for processed nodes.
    -   `load_rich_atomic.py`: Filtered to load specific CAPEC nodes (Thin Node mode).
*   **Data Artifacts:**
    -   `training_30_map.csv`: The syllabus for the 30-node test.
    -   `training_30_nodes.jsonl`: The SFT dataset.

## Next Steps:
1.  Set up **LLaMA-Factory** environment.
2.  Convert `training_30_nodes.jsonl` to LLaMA-Factory dataset format.
3.  Run first fine-tuning epoch on Qwen2.5-7B or Llama-3.
4.  Generate matching 30-node Test Set using UCKG scripts.
