# Neo4j AI Graph Sandbox: Quick Reference

This document explains how to set up, access, and visualize the temporary Neo4j Sandbox used to view the AI-generated Knowledge Graphs produced by GraphGen.

## Why a Sandbox?
We strictly isolate the AI-generated graph (`KuzuDB`) from your production UCKG Neo4j database to prevent data corruption or overlapping labels. The sandbox runs entirely in memory/temporary containers.

---

## 1. Start the Sandbox (Docker)
If the sandbox is not running, spin up a fresh, empty Neo4j container on alternative ports using this command:

```bash
docker run -d --name neo4j_sandbox \
    -p 7475:7474 -p 7688:7687 \
    -e NEO4J_AUTH=neo4j/testpassword \
    neo4j:5
```

## 2. Export Kuzu to the Sandbox
Once GraphGen finishes the `build_kg` step, the graph lives in the local Kuzu database (`cache/graph_kuzu`). Push it to the visual Sandbox by running:

```bash
python3 examples/generate/generate_uckg/export_kuzu_to_neo4j.py
```
*(Note: This script automatically tags every node with the `:AIGeneratedNode` label for safety).*

---

## 3. How to View the Graph
Open your web browser and navigate to the Neo4j Browser UI:
👉 **URL:** `http://localhost:7475` *(Note the 5!)*

**Login Credentials:**
*   **Connection URL:** `neo4j://localhost:7688`
*   **Database:** *(leave blank)*
*   **Username:** `neo4j`
*   **Password:** `testpassword`

## 4. Useful Cypher Queries
Once logged in, paste these into the command bar at the top:

**View the entire AI Graph:**
```cypher
MATCH (n) RETURN n
```

**View only the 'BlueSmacking' Attack Family:**
```cypher
MATCH (n)-[r]-(m) 
WHERE n.name = 'BLUESMACKING' 
RETURN n, r, m
```

**Clear the Sandbox (Delete everything to start fresh):**
```cypher
MATCH (n) DETACH DELETE n
```
