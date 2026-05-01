import json
import os

# Input from our ETL pipeline (The unfiltered raw data)
INPUT_FILE = "examples/generate/generate_uckg/raw_data.jsonl"
# Output for GraphGen
OUTPUT_FILE = "examples/generate/generate_uckg/uckg_text_dump_test.jsonl"

def format_list(item_list):
    """Helper to format lists into bullet points or return empty string."""
    if not item_list or item_list == "None specified.":
        return "None specified."
    if isinstance(item_list, list):
        nl = chr(10)
        return nl.join(f"- {item}" for item in item_list)
    return str(item_list)

def convert_to_text_dump(limit=1, skip=0):
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please ensure it exists.")
        return

    print(f"Reading from {INPUT_FILE}... (Skipping first {skip} paths)")
    
    count = 0
    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for i, line in enumerate(fin):
            if i < skip:
                continue
                
            row = json.loads(line)
            
            c = row.get("c", {})
            a = row.get("a", {})

            # Extract Shared Bridge: Technique ID (from URI like ...#T1498.001)
            uri = a.get("uri", "")
            technique_id = uri.split("#")[-1] if "#" in uri else "Unknown ID"

            # Extract Names
            c_name = c.get("ucoexCAPEC_name", c.get("Name", "Unknown Attack"))
            c_id = c.get("ucoexCAPEC_id", "Unknown ID")

            nl = chr(10)

            # Extract Descriptions
            c_desc = c.get("ucoexDescription", "No description.")
            c_extended_desc_raw = c.get("ucoexExtendedDescription", [])
            c_extended_desc = f"Extended Description:{nl}{format_list(c_extended_desc_raw)}{nl}" if c_extended_desc_raw else ""
            
            c_example_raw = c.get("ucoexExample", [])
            if c_example_raw:
                c_example = f"This attack has the following example:{nl}{format_list(c_example_raw)}{nl}"
            else:
                c_example = f"This attack does not have an example.{nl}"

            # Extract CAPEC Rich Metadata
            c_severity = c.get("ucoexSeverity", "Unknown")
            c_likelihood = c.get("ucoexLikelihood", "Unknown")
            c_abstraction = c.get("ucoexAbstraction", "Unknown")
            c_skill = format_list(c.get("ucoexSkills_Required", []))
            c_prereqs = format_list(c.get("ucoexPrerequisites", []))
            c_tech_flow = format_list(c.get("ucoexExecutionFlowTechnique", []))
            c_cons = format_list(c.get("ucoexConsequences", []))
            c_weaknesses = format_list(c.get("ucoexRelatedWeaknesses", []))
            c_related_patterns = format_list(c.get("ucoexRelatedAttPattern", []))
            c_mitigations = format_list(c.get("ucoexMitigations", []))
            c_taxonomy_attack = format_list(c.get("ucoexTaxonomyMappingATTACK", []))

            # --- REPORT: THE CAPEC MASTER STORY ---
            report = (
                f"# Threat Intelligence Report: {c_name}{nl}{nl}"
                f"**Executive Summary for {c_name}:**{nl}"
                f"The attack pattern '{c_name}' is described as follows: {c_desc}{nl}"
                f"{c_extended_desc}"
                f"{c_example}"
                f"This attack pattern is categorized at the {c_abstraction} abstraction level.{nl}{nl}"
                f"**Threat Profile for {c_name}:**{nl}"
                f"The severity of this attack is {c_severity} and the likelihood of occurrence is {c_likelihood}.{nl}{nl}"
                f"To successfully execute '{c_name}', the target environment must meet the following prerequisites:{nl}{c_prereqs}{nl}{nl}"
                f"The adversary requires the following skill level to execute '{c_name}':{nl}{c_skill}{nl}{nl}"
                f"**Attack Execution Flow for {c_name}:**{nl}"
                f"An adversary typically executes '{c_name}' through the following technical steps:{nl}{c_tech_flow}{nl}{nl}"
                f"**Impact & Consequences of {c_name}:**{nl}"
                f"If the attack pattern '{c_name}' is successful, it results in the following consequences for the target system:{nl}{c_cons}{nl}{nl}"
                f"**Mitigations for {c_name}:**{nl}"
                f"The following actions can mitigate this attack:{nl}{c_mitigations}{nl}{nl}"
                f"**Taxonomy & Reference IDs:**{nl}"
                f"The attack pattern '{c_name}' specifically exploits the following underlying weaknesses:{nl}{c_weaknesses}{nl}{nl}"
                f"Related Attack Patterns:{nl}{c_related_patterns}{nl}{nl}"
                f"The official identifier for the attack pattern '{c_name}' is CAPEC ID: **CAPEC-{c_id}**.{nl}"
                f"Furthermore, the attack pattern '{c_name}' is officially mapped to the following related MITRE ATT&CK Techniques:{nl}{c_taxonomy_attack}"
            )

            fout.write(json.dumps({"type": "text", "content": report}, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} CAPEC Master Reports.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_to_text_dump(limit=1, skip=0)
