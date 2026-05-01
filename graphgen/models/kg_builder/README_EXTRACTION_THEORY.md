# How GraphGen Builds Connected Graphs from Isolated Text

This document explains the core architectural mechanism inside `light_rag_kg_builder.py` that allows GraphGen to take hundreds of completely isolated text chunks and automatically stitch them together into a highly connected Knowledge Graph.

## The Problem
When the LLM reads the input data, it only reads **one chunk at a time**. It has no memory of the previous chunks. So how does it know that the "Firewall" mentioned in Chunk 1 is the exact same "Firewall" mentioned in Chunk 500?

## The Secret: "String-Based Deduplication" as Global Memory

The magic does not happen inside the LLM; it happens right here in the **Python Storage Script** (`light_rag_kg_builder.py` -> `KuzuStorage`).

1. **Extraction:** The LLM extracts entities from the text and gives them human-readable names (e.g., `"Firewall"`).
2. **The ID System:** GraphGen uses the **exact English string** (`"Firewall"`) as the absolute Database ID (Primary Key) for that node.
3. **The Merge (`merge_nodes` / `merge_edges`):** 
   - When Chunk 1 is processed, the script creates a node with ID `"Firewall"`.
   - When Chunk 500 is processed, the LLM again extracts `"Firewall"`. 
   - The Python script checks KuzuDB and sees: *"Wait, ID 'Firewall' already exists!"*
   - Instead of creating a duplicate, the script **merges** the new relationships into the existing `"Firewall"` node.
   - If the new chunk has a different description for the same entity, the script calls a **Summarization LLM Prompt** to combine the two descriptions into one.

## Why This is Powerful
Because of this mechanism, the developer doesn't need to manually map the ontology. 

If ten different paragraphs all mention "Denial of Service" in their text, the system will automatically create a single, massive "Denial of Service" Super-Hub node, and draw ten separate lines pointing to it. 

The isolated paragraphs automatically knit themselves into a massive web.
