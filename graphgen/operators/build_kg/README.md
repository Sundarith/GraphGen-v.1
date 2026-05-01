# Build KG Operator: Architectural Trace

The `build_kg` module is the most complex component of the GraphGen engine. It is responsible for transforming raw, unstructured text chunks into a mathematically rigorous, deduplicated Knowledge Graph.

Below is the exact, file-by-file execution path that occurs when a text chunk enters this phase of the pipeline.

## Phase 1: The Orchestration Layer
1. **`engine.py` (Root Level)**
   * **Role:** The master controller. It triggers the `build_kg` operator and passes it the Ray Dataset containing the pre-chopped text chunks (from the `chunk` operator).
2. **`operators/build_kg/build_kg_service.py`**
   * **Role:** The traffic cop. It analyzes the incoming chunks, determines whether they are pure text or multimodal (images/tables), and routes them to the appropriate builder.
3. **`operators/build_kg/build_text_kg.py`**
   * **Role:** The parallel manager. It utilizes `run_concurrent` to spin up dozens of asynchronous threads, allowing the system to process hundreds of text chunks simultaneously rather than waiting for them one-by-one.

## Phase 2: The LLM Interaction Layer
4. **`models/kg_builder/light_rag_kg_builder.py`**
   * **Role:** The core "Brain" of the extraction process. It takes a raw text chunk and injects it into the prompt variables. It also manages the "Iterative Loop" (asking the LLM "Did you miss anything?" until the chunk is fully extracted).
5. **`templates/kg/kg_extraction.py`**
   * **Role:** The prompt repository. This file contains the strict formatting instructions (using `<|>` and `##` delimiters) and the "You are an NLP Expert" persona that guides the LLM.
6. **`models/llm/api/openai_client.py` (or equivalent)**
   * **Role:** The network messenger. It takes the fully assembled prompt payload from the builder, transmits it securely over the internet to the LLM API (e.g., Gemini, OpenAI), and awaits the string response.

## Phase 3: The Parsing & Deduplication Layer
7. **`utils/format.py`**
   * **Role:** The parser. The `light_rag_kg_builder` relies on utility functions here (like `split_string_by_multi_markers`) to apply Regex logic. This strips away the weird formatting delimiters and converts the LLM's raw text string into clean Python dictionaries representing Nodes and Edges.
8. **`templates/kg/kg_summarization.py`**
   * **Role:** The referee. If the builder detects that two different text chunks extracted different descriptions for the exact same entity (e.g., "Firewall"), it loads this secondary prompt. It sends both conflicting descriptions back to the LLM and asks it to synthesize them into one cohesive paragraph.

## Phase 4: The Database Layer
9. **`models/storage/graph/kuzu_storage.py`**
   * **Role:** The final destination. Once the Python dictionaries are parsed and deduplicated, they are handed to this storage class. It translates the Python objects into raw KuzuDB Cypher commands (e.g., `UPSERT`) and physically writes the finalized graph to the `cache/graph_kuzu/` directory on the local disk.

---
**Summary:** The `build_kg` operator does not execute sequentially in a single file. It is a highly modular, event-driven pipeline that passes data up and down the abstraction stack to ensure maximum speed and LLM accuracy.
