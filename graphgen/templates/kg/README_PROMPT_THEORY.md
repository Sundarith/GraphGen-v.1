# Knowledge Graph Extraction Prompts: Theory & Mechanics

This directory contains the critical LLM prompts used to transform unstructured text into structured mathematical graphs.

## 1. The Extraction Prompt (`kg_extraction.py`)

### The "Code-Like" Output Constraint
LLMs naturally want to write conversational paragraphs. However, a database cannot parse a paragraph. 
To solve this, the `TEMPLATE_EN` uses strict few-shot examples to force the LLM to output data as delimited tuples.
*   **Format:** `("entity"{tuple_delimiter}<name>{tuple_delimiter}<type>{tuple_delimiter}<description>){record_delimiter}`
*   **Example Output:** `("entity"<|>"Firewall"<|>"technology"<|>"Blocks packets")##`

This ugly, strict formatting guarantees that the Python script (`light_rag_kg_builder.py`) can safely split the string using Regex without crashing on stray commas or newlines.

### Runtime Injection
The prompt contains empty `{variables}`. When the engine runs, it injects the actual data:
*   `{input_text}`: The 500-word chunk of text being analyzed.
*   `{entity_types}`: The whitelist of allowed node types (e.g., `concept, organization, technology`).

## 2. The Iterative Loop (`CONTINUE_EN` & `IF_LOOP_EN`)

LLMs are inherently lazy. If given a massive document, they will often extract the first 5 entities they see and stop. 

GraphGen solves this using an "Iterative Refinement" loop:
1.  **Extract:** The LLM does its first pass.
2.  **Verify (`IF_LOOP_EN`):** The engine asks, *"Did you miss anything? YES or NO."*
3.  **Force (`CONTINUE_EN`):** If the LLM says "YES", the engine commands it to keep extracting.
**Crucially:** The Python engine sends the *entire conversation history* back to the LLM during this loop, so the LLM remembers exactly what it already extracted and what text it is reading.

## 3. The Summarization Prompt (`kg_summarization.py`)

When the engine processes a whole book, it might find the entity "Apple" in Chapter 1 and again in Chapter 10. 
*   Chapter 1 says: "Apple is a red fruit."
*   Chapter 10 says: "Apple is used to make pie."

Instead of overwriting the data or creating two nodes, the engine merges them into a single string and sends them to the **Summarization Prompt**. This prompt instructs the LLM to read the conflicting/overlapping descriptions and write one cohesive, unified dictionary definition for the node.
