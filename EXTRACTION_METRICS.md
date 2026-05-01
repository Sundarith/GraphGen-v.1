# UCKG Extraction Metrics & Benchmarks

This document tracks the mathematical performance, time, and yield of the KuzuDB Knowledge Graph extraction pipeline. Every single parameter change and metric is recorded below to prove the mathematical progression of the graph.

---

## 🟢 Run 1: The Foundation (Paths 1 - 100)
**Objective:** Establish the foundational Knowledge Graph from scratch.

### Engine Configuration
*   **LLM Model:** `gemini-3-flash-preview`
*   **Prompt Type:** Custom UCKG Extraction (Cybersecurity Schema)
*   **Chunk Size:** 1024 Tokens
*   **Max Interrogation Loops:** 3 (`max_loop: 3`)
*   **Batch Size:** 16 (Sent 16 chunks concurrently to Google API)

### Extraction Metrics
*   **Input Data:** 100 "Fat Paragraph" Incident Reports
*   **Start Time:** 13:08:24
*   **End Time:** 14:27:19
*   **Total Execution Time:** 1 hour, 19 minutes (79 minutes)
*   **New Nodes Extracted:** 2,949
*   **New Edges Extracted:** 4,361
*   **Current Graph Total (Nodes):** 2,949
*   **Current Graph Total (Edges):** 4,361

---

## 🟢 Run 2: The Merge (Paths 101 - 200)
**Objective:** Test KuzuDB's "Layer 2 Deduplication" by merging new paths into the existing network.

### Engine Configuration
*   **LLM Model:** `gemini-3-flash-preview`
*   **Prompt Type:** Custom UCKG Extraction (Cybersecurity Schema)
*   **Chunk Size:** 1024 Tokens
*   **Max Interrogation Loops:** 3 (`max_loop: 3`)
*   **Batch Size:** 16 (Sent 16 chunks concurrently to Google API)

### Extraction Metrics
*   **Input Data:** 100 "Fat Paragraph" Incident Reports
*   **Start Time:** 16:04:18
*   **End Time:** 16:29:06
*   **Total Execution Time:** 24 minutes, 48 seconds
*   **New Nodes Added:** 1,526
*   **New Edges Added:** 2,771
*   **Current Graph Total (Nodes):** 4,475
*   **Current Graph Total (Edges):** 7,132

### Analytical Takeaway
Run 2 successfully proved the graph's deduplication logic. It only created 1,526 new nodes (a 48% reduction compared to Run 1) because it seamlessly identified overlapping Mitigations and Threat Actors, opting to draw 2,771 new edges to existing nodes rather than creating messy duplicates.

---

## 🏛️ Architectural Defense: Ontology Drift vs Structural Integrity
During extraction, Generative AI models (like Gemini or Qwen) occasionally suffer from **Ontology Drift** (e.g., ignoring the strict 8-category schema and inventing messy labels like `DETECTIONS_BASED_ON_NON-STANDARD_PATHS` or `MITIGATION(ENTITY)`).

### Why this is Harmless to the GraphGen Pipeline:
1. **KuzuDB (The Warehouse):** KuzuDB completely ignores label syntax. It stores all nodes in a generic `Entity` table and all relationships in a generic `Relation` table. The hallucinated labels are safely stored as raw JSON strings, so the database never crashes.
2. **Structural Deduplication:** KuzuDB enforces strict primary keys based on the *Node Name* (not the label). If "BlueSmacking" appears 50 times across 50 different reports, KuzuDB perfectly deduplicates it into a single structural node, guaranteeing a flawless, interconnected topological web regardless of the messy labels.
3. **Leiden Partitioning:** The Leiden algorithm is blind to text labels. It calculates communities purely based on the physical density of the mathematical edges (the bridges).

### The Neo4j UI Fix (The Python Bouncer):
The *only* system that breaks when encountering hallucinated labels is Neo4j, because its Cypher query language cannot process hyphens or parentheses in Label syntax. 
To solve this purely cosmetic UI issue, a **Regex Ontology Bouncer** was engineered into the `export_kuzu_to_neo4j.py` script. It strictly intercepts hallucinated labels, strips invalid characters, and forces them into the approved 8-color ontology (`ATTACK_PATTERN`, `MITIGATION`, etc.) before rendering the visual graph.