"""
create_capec_property_qa.py

Reads raw_data.jsonl and generates one atomic Q&A pair per CAPEC property.
Output is a ShareGPT-format JSONL file ready for LLM fine-tuning.

Usage:
    python3 examples/generate/generate_uckg/create_capec_property_qa.py
"""

import json
import os
from pathlib import Path

INPUT_FILE = "examples/generate/generate_uckg/raw_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/bluesmacking_property_qa.jsonl"

TARGET_CAPEC_IDS = {"666"}

SKIP_KEYS = {"elementId", "id", "embedding", "embedding_failed", "embedding_processed", "label", "uri"}

# Each entry: property_key → (name_questions[], id_questions[], answer_formatter)
# name_questions: phrasings using {name}
# id_questions:   phrasings using CAPEC-{id}  (None = skip id variant entirely)
PROPERTY_QA_TEMPLATES = {
    "ucoexCAPEC_name": (
        ["What is the name of the attack pattern identified as CAPEC-{id}?"],
        None,
        lambda v: v,
    ),
    "ucoexCAPEC_id": (
        ["What is the CAPEC ID of the {name} attack?"],
        None,
        lambda v: f"CAPEC-{v}",
    ),
    "ucoexAbstraction": (
        ["What is the abstraction level of the {name} attack?"],
        ["What is the abstraction level of CAPEC-{id}?"],
        lambda v: v,
    ),
    "ucoexSeverity": (
        ["What is the severity level of the {name} attack?"],
        ["What is the severity level of CAPEC-{id}?"],
        lambda v: v,
    ),
    "ucoexLikelihood": (
        ["What is the likelihood of a {name} attack being exploited?"],
        ["What is the likelihood of CAPEC-{id} being exploited?"],
        lambda v: v,
    ),
    "ucoexDescription": (
        ["What does the {name} attack describe?"],
        ["What does CAPEC-{id} describe?"],
        lambda v: v,
    ),
    "ucoexMitigations": (
        ["What are the recommended mitigations for a {name} attack?"],
        ["What are the recommended mitigations for CAPEC-{id}?"],
        lambda v: " ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexConsequences": (
        ["What are the security consequences of a {name} attack?"],
        ["What are the security consequences of CAPEC-{id}?"],
        lambda v: "; ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexRelatedWeaknesses": (
        ["What CWE weaknesses are associated with a {name} attack?"],
        ["What CWE weaknesses are associated with CAPEC-{id}?"],
        lambda v: ", ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexTaxonomyMappingATTACK": (
        ["Which MITRE ATT&CK techniques map to the {name} attack?"],
        ["Which MITRE ATT&CK techniques map to CAPEC-{id}?"],
        lambda v: ", ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexRelatedAttPattern": (
        ["What are the related attack patterns for {name}?"],
        ["What are the related attack patterns for CAPEC-{id}?"],
        lambda v: "; ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexExecutionFlowTechnique": (
        ["What is the step-by-step execution flow of a {name} attack?"],
        ["What is the step-by-step execution flow of CAPEC-{id}?"],
        lambda v: " ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexSkills_Required": (
        ["What skill level is required to execute a {name} attack?"],
        ["What skill level is required to execute CAPEC-{id}?"],
        lambda v: " ".join(v) if isinstance(v, list) else v,
    ),
    "ucoexPrerequisites": (
        ["What prerequisites must be in place before a {name} attack can succeed?"],
        ["What prerequisites must be in place before CAPEC-{id} can be executed?"],
        lambda v: " ".join(v) if isinstance(v, list) else v,
    ),
}


def generate_qa_pairs(capec: dict) -> list[dict]:
    """Generate multiple Q&A variants per CAPEC property (name-based + id-based phrasings)."""
    capec_id = capec.get("ucoexCAPEC_id", "unknown")
    name = capec.get("ucoexCAPEC_name", f"CAPEC-{capec_id}")
    pairs = []

    for key, (q_names, q_ids, formatter) in PROPERTY_QA_TEMPLATES.items():
        val = capec.get(key)
        if not val:
            continue

        answer = str(formatter(val)).strip()
        if not answer:
            continue

        # Name-based question variants
        for q in q_names:
            question = q.replace("{id}", capec_id).replace("{name}", name)
            pairs.append({
                "conversations": [
                    {"from": "human", "value": question},
                    {"from": "gpt", "value": answer},
                ]
            })

        # ID-based question variants (skip if None)
        if q_ids:
            for q in q_ids:
                question = q.replace("{id}", capec_id).replace("{name}", name)
                pairs.append({
                    "conversations": [
                        {"from": "human", "value": question},
                        {"from": "gpt", "value": answer},
                    ]
                })

    return pairs


def main():
    # Deduplicate CAPEC nodes by ID (raw_data.jsonl is relational, many rows = same CAPEC)
    seen_ids = set()
    capec_nodes = []

    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            capec = row.get("c", {})
            capec_id = capec.get("ucoexCAPEC_id")
            if TARGET_CAPEC_IDS and capec_id not in TARGET_CAPEC_IDS:
                continue
            if capec_id and capec_id not in seen_ids:
                seen_ids.add(capec_id)
                capec_nodes.append(capec)

    print(f"Found {len(capec_nodes)} unique CAPEC nodes.")

    total_qa = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for capec in capec_nodes:
            pairs = generate_qa_pairs(capec)
            for pair in pairs:
                out.write(json.dumps(pair, ensure_ascii=False) + "\n")
                total_qa += 1

    print(f"Generated {total_qa} atomic Q&A pairs → {OUTPUT_FILE}")
    print(f"Average: {total_qa / len(capec_nodes):.1f} Q&As per CAPEC node")


if __name__ == "__main__":
    main()
