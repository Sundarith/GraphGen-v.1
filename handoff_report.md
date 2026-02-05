# Handoff Report: UCKG Knowledge Graph & LLM Training Strategy

**Date:** 2026-02-02
**Project:** Unified Cybersecurity Knowledge Graph (UCKG)
**Goal:** Train an LLM to act as a Cybersecurity Incident Responder.

## 1. Current Status
We have successfully analyzed the Neo4j database structure, data quality, and connectivity.

*   **Database:** Neo4j (running in Docker `uckg--neo4j-1`).
*   **Data Health:**
    *   **Nodes:** ~828k nodes (CVE, CPE, CAPEC, CWE, ATT&CK).
    *   **Connectivity:** The graph is **fully connected** in a logical chain:
        `CPE` (Software) -> `CVE` (Vuln) -> `ObservedExample` -> `CWE` (Weakness) -> `CAPEC` (Attack Pattern) -> `ATT&CK` (Tactic).
    *   **Issue:** Some direct relationships (e.g., `CWE` -> `CAPEC`) are missing in the direct sense but are connected via the long chain or strictly as text properties due to RML mapping issues (see `mapping/DEBUG_RML_CONNECTIONS.md`).

## 2. LLM Training Strategy
We agreed to build a **User-Centric Incident Responder Bot**.
The training data extraction will focus on translation: **User Language (Symptoms) -> Technical Reality (Attack Pattern).**

### Primary Data Source: **CAPEC (UcoexCAPEC)**
CAPEC is the "Goldilocks" node—not too technical (like CVE), not too abstract (like ATT&CK). It maps perfectly to user actions.

| Data Field | Purpose | Prompt Strategy |
| :--- | :--- | :--- |
| **`ucoexDescription`** | **Primary Source** | "I am worried about [Description Keywords]. What attack is this?" |
| **`ucoexExample`** | **Scenario Validation** | "Here is a story: [Example Text]. What attack happened?" |
| **`ucoexExecutionFlowTechnique`** | **Technical Verification** | "How does the [Attack Name] actually work step-by-step?" |

### Secondary Data Source: **Mitigations (UcoexMITIGATIONS)**
Linked via: `(CAPEC) -> (ATT&CK) <- (Mitigation)`
*   **Purpose:** The "Answer" to the user's problem.
*   **Prompt Strategy:** "How do I stop [Attack Name]?" -> [List of Mitigations]

## 3. Work Completed
*   Verified the graph path: `CPE -> CVE -> ObservedExample -> CWE -> CAPEC -> ATT&CK`.
*   Verified data quality for `ucoexDescription` and `ucoexExample` (Excellent/Rich text).
*   Verified relationship names (e.g., `UCOEXMITIGATES` instead of `MITIGATES`).
*   Designed the Python extraction logic (but did not run it yet).

## 4. Next Steps (For the Next Agent)
1.  **Run the Extraction Script:** Create and run `extract_capec_training_data.py`.
    *   *Goal:* Generate `capec_user_intent.jsonl`.
    *   *Logic:* Iterate `UcoexCAPEC`, extract `Description` and `Example`, format as User Q&A.
2.  **Add Mitigation Data:** Extend the script to join with `UcoexMITIGATIONS`.
    *   *Goal:* Add the "Solution" part to the training data.
3.  **Refine Prompts:** (Optional) Use an LLM to paraphrase the formal CAPEC descriptions into casual "User Complaints" for better realism.

## 5. Key Cypher Queries Identified
*   **User Intent Data:**
    ```cypher
    MATCH (n:UcoexCAPEC) RETURN n.ucoexCAPEC_name, n.ucoexDescription, n.ucoexExample
    ```
*   **Full Context (Attack + Defense):**
    ```cypher
    MATCH (capec:UcoexCAPEC)-[:UCOEXHASTAXONOMYMAPPING]->(attack:UcoexMITREATTACK)<-[:UCOEXMITIGATES]-(mitigation:UcoexMITIGATIONS)
    RETURN capec.ucoexCAPEC_name, capec.ucoexDescription, collect(mitigation.ucoexNAME)
    ```
