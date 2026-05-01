# UCKG Project: Handoff & Progress Notes

## What We Accomplished on Day 1 (March 8, 2026)
1. **The "Text-to-Graph" Pivot:** We abandoned the rigid Neo4j mapping (`load_clean_graph.py`) and built a custom Python script (`create_text_dump.py`) to weave 8 specific cybersecurity properties into rich, Markdown-formatted "Fat Paragraphs."
2. **Eliminated "Example Bleed" (Hallucinations):** We successfully reverse-engineered the original `kg_extraction.py` prompt and hard-deleted the biology (Rice/OsDT11) examples, replacing them with a strict `BlueSmacking` example to prevent Gemini from hallucinating non-security data.
3. **The 50-Path Stress Test (Pro Model):** We extracted 50 raw paths, fed them to `gemini-3.1-pro-preview`, and built a highly-connected Kuzu Database containing **1,479 nodes**. 
4. **Partitioning & Generation:** We ran the Leiden algorithm (`max_size: 15`), which split the graph into 132 semantic communities. We then fed these to the Generator using our custom "Strict Professor" prompt to output **132 pure Chain-of-Thought (CoT) reasoning traces**.
5. **Audited LLaMA-Factory Setup:** We reviewed the remote GPU training configuration (`training_args.yaml`) and injected the exact "Golden Settings" needed to stabilize LoRA training (Batch size 8, LR 2e-4, Rank 32, Warmup 50).

---

## What We Accomplished on Day 2 (March 12 & 13, 2026)
### 1. Resolving the API Quota & File Caching Mysteries
We successfully diagnosed why our batch processing stalled:
- **The API Quota (429 Error):** We discovered that the `gemini-3.1-pro-preview` model has a strict 250 Requests Per Day limit. When the limit is hit, the Python engine silently writes "empty" rows instead of crashing. We solved this by switching the builder to the high-quota `gemini-3.1-flash-lite-preview` model.
- **The File Cache Bypass:** We discovered that GraphGen memorizes file names and automatically skips them if reused. We successfully bypassed this bug by injecting `from_scratch: true` into the `uckg_kg_builder_test.yaml` file, allowing us to continuously overwrite `uckg_text_dump_test.jsonl` without the engine ignoring it.

### 2. The Master Graph Completion (The 644-Path Milestone)
We systematically proved the KuzuDB "Seamless Merge" engine by scaling the database incrementally all the way to the absolute end of the dataset. The engine successfully extracted new data and mathematically deduplicated overlapping concepts (like "Firewall" or "Network") across the entire cybersecurity dictionary:
- **Paths 1-10:** Generated **343 Nodes / 323 Edges**.
- **Paths 11-20:** Successfully merged, growing to **625 Nodes / 625 Edges**.
- **Paths 21-50:** Successfully merged, growing to **1,084 Nodes / 1,201 Edges**.
- **Paths 51-100:** Successfully merged, growing to **1,487 Nodes / 1,746 Edges**.
- **Paths 101-150:** Successfully merged, growing to **1,868 Nodes / 2,280 Edges**.
- **Paths 151-200:** Successfully merged, growing to **2,192 Nodes / 2,757 Edges**.
- **Paths 201-250:** Successfully merged, growing to **2,607 Nodes / 3,322 Edges**.
- **Paths 251-300:** Successfully merged, growing to **2,951 Nodes / 3,866 Edges**.
- **Paths 301-350:** Successfully merged, growing to **3,249 Nodes / 4,335 Edges**.
- **Paths 351-400:** Successfully merged, growing to **3,448 Nodes / 4,642 Edges**.
- **Paths 401-450:** Successfully merged, growing to **3,693 Nodes / 5,018 Edges**.
- **Paths 451-500:** Successfully merged, growing to **3,945 Nodes / 5,459 Edges**.
- **Paths 501-600:** Successfully merged, growing to **4,473 Nodes / 6,336 Edges**.
- **Paths 601-644:** Successfully merged, culminating in the **FINAL MASTER GRAPH**: **4,602 Nodes / 6,564 Edges**.

### 3. Model Efficiency Discovery (Flash-Lite vs. Pro)
Comparing Day 1 to Day 2, we discovered a massive difference in Knowledge Graph quality between Google's models:
- **Day 1 (`gemini-3.1-pro-preview`):** Extremely verbose. Extracted **1,479 nodes** for just 50 paths. It often hallucinates tiny variations of the same adjective as distinct nodes.
- **Day 2 (`gemini-3.1-flash-lite-preview`):** Highly strict and concise. Processed **all 644 paths** to generate just **4,602 nodes**. It acts as a much better "Data Entry Clerk," extracting only hard, core intelligence concepts. 
- *Conclusion:* Flash-Lite is vastly superior (and cheaper) for building the actual Graph database, while the Pro model should be reserved exclusively for the final Generation (QA) phase.

---

## Next Steps
1. **Visual Verification:** Run `export_kuzu_to_neo4j.py` to push the final 4,602-node graph to the Neo4j Sandbox for visual inspection.
2. **Upgrade the Python Parser for `<thought>` Tags:** Modify `multi_hop_generator_uckg.py` to force the LLM to output a hidden `<thought>` block before generating the `<answer>`, recreating the DeepSeek-R1 architecture.
3. **Partition & Generate:** Run the Leiden algorithm on the Master Graph to slice it into communities. Then, write a "Sharding Script" to batch the communities, and use the `Pro` model to generate the final SFT reasoning dataset.
4. **Agentic Evaluation:** Build the "LLM-as-a-Judge" pipeline to score the locally fine-tuned Llama-3 model against the baseline.