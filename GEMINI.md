# GraphGen + UCKG Integration Project

This workspace contains two distinct but potentially integrated projects:

1.  **GraphGen:** A framework for generating knowledge-driven synthetic data for LLM fine-tuning.
2.  **UCKG (Unified Cybersecurity Knowledge Graph):** A cybersecurity knowledge graph project with a QA engine, nested within the `UCKG/` directory.

---

## 1. GraphGen (Root Project)

**GraphGen** enhances Supervised Fine-Tuning (SFT) for LLMs by constructing fine-grained knowledge graphs from source text and generating high-quality QA pairs (Atomic, CoT, Multi-hop, etc.).

### Key Technologies
*   **Core:** Python, Ray (distributed computing)
*   **Storage:** RocksDB (KV store), KuzuDB / NetworkX (Graph backend)
*   **LLM Integration:** OpenAI, vLLM, Ollama, HuggingFace
*   **Search:** Google, Bing, Wikipedia

### Directory Structure
*   `graphgen/`: Core library (engine, models, operators).
*   `examples/`: Scripts and configs for generating different data types (CoT, Atomic, etc.).
*   `baselines/`: Implementations of baseline methods.
*   `webui/`: A Gradio-based web interface.

### Quick Start (GraphGen)

**Installation:**
```bash
# Using uv (recommended)
uv venv --python 3.10
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Running the Web UI:**
```bash
python -m webui.app
```

**Generating Data (CLI):**
Check `examples/generate/` for specific scripts. Example for Chain-of-Thought (CoT) data:
```bash
# Customize config first: examples/generate/generate_cot_qa/cot_config.yaml
bash examples/generate/generate_cot_qa/generate_cot.sh
```

---

## 2. UCKG (Nested Project)

**Location:** `./UCKG`

**UCKG** builds a unified cybersecurity knowledge graph and provides a Question Answering (QA) engine leveraging GraphRAG and Text2Cypher.

### Key Technologies
*   **Database:** Neo4j (Graph DB)
*   **Infrastructure:** Docker, Airflow
*   **Backend:** FastAPI (QA Engine), Express.js (UI Backend)
*   **Frontend:** React
*   **LLM:** Ollama (Local inference)

### Directory Structure
*   `UCKG/qa-engine/`: The core logic for answering questions (GraphRAG, Text2Cypher).
*   `UCKG/data/`: Data sources (CVE, CWE, CAPEC, etc.).
*   `UCKG/UI/`: Web interface (React + Express).
*   `UCKG/docker-compose.yml`: Main entry point for orchestration.

### Quick Start (UCKG)

**Building & Running:**
```bash
cd UCKG
docker-compose up --build
```
*   **Frontend:** http://localhost:3000
*   **QA Engine:** http://localhost:8000
*   **Neo4j:** http://localhost:7474

**QA Engine Development:**
The QA engine is a FastAPI app located in `UCKG/qa-engine/`.
```bash
cd UCKG/qa-engine
# Install deps
pip install -r requirements.txt
# Run locally
python main.py
```

### Integration Notes
*   **Goal:** Use **GraphGen** to generate synthetic QA pairs based on the data or ontology from **UCKG**, or use UCKG's graph as a source for GraphGen.
*   **Cross-Project Work:** When working in the terminal, be mindful of your current directory (`root` vs `root/UCKG`).
