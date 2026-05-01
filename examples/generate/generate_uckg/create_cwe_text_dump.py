import json
import os

# Input from our ETL pipeline (The unfiltered raw data or specific CWE data)
INPUT_FILE = "examples/generate/generate_uckg/cwe_raw_data.jsonl"
# Output for GraphGen
OUTPUT_FILE = "examples/generate/generate_uckg/uckg_cwe_text_dump_test.jsonl"

def format_list(item_list):
    """Helper to format lists into bullet points or return empty string."""
    if not item_list or item_list == "None specified.":
        return "None specified."
    
    # We do NOT parse nested JSON objects. If it's a list, we format it as bullet points.
    if isinstance(item_list, list):
        nl = chr(10)
        return nl.join(f"- {item}" for item in item_list)
    
    # For nested raw strings (like "{mitigation=[...]}") we just return them as they are
    return str(item_list)

def convert_to_cwe_text_dump(limit=None, skip=0, filter_val=None):
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Please ensure it exists.")
        return

    print(f"Reading from {INPUT_FILE}... (Filter: {filter_val if filter_val else 'None'})")
    
    count = 0
    with open(INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for i, line in enumerate(fin):
            if i < skip:
                continue
                
            row = json.loads(line)
            
            # Assume CWE node is in 'c'
            c = row.get("c", {})
            
            # Skip if it is not a CWE node (check if it has ucocweID or label contains CWE)
            cwe_id = c.get("ucocweID", "")
            label = c.get("label", "")
            c_name = c.get("ucocweName", c.get("Name", "Unknown Weakness"))
            
            if not cwe_id and "CWE" not in label:
                continue

            # Apply Filter if provided
            if filter_val:
                if filter_val.lower() not in cwe_id.lower() and filter_val.lower() not in c_name.lower():
                    continue

            # Extract Names
            c_id = c.get("ucocweID", "Unknown ID")

            nl = chr(10)

            # Extract Descriptions
            c_desc = c.get("ucodescription", c.get("ucocweSummary", "No description."))
            
            c_extended_desc_raw = c.get("ucocweExtendedSummary", [])
            if c_extended_desc_raw:
                c_extended_desc = f"The weakness '{c_name}' has the following extended summary:{nl}{format_list(c_extended_desc_raw)}{nl}"
            else:
                c_extended_desc = f"The weakness '{c_name}' does not have an extended summary.{nl}"

            c_example_raw = c.get("ucodemonstrativeExamples", [])
            if c_example_raw:
                c_example = f"The weakness '{c_name}' has the following demonstrative example:{nl}{format_list(c_example_raw)}{nl}"
            else:
                c_example = f"The weakness '{c_name}' does not have a demonstrative example.{nl}"

            # Extract CWE Rich Metadata
            c_abstraction = c.get("ucoabstraction", "Unknown")
            c_structure = c.get("ucostructure", "Unknown")
            c_likelihood = c.get("ucolikelihoodOfExploit", "Unknown")
            c_modes = format_list(c.get("ucomodesOfIntroduction", []))
            c_platforms = format_list(c.get("ucoapplicablePlatform", []))
            c_cons = format_list(c.get("ucocommonConsequences", []))
            c_detection = format_list(c.get("ucodetectionMethods", []))
            c_mitigations = format_list(c.get("ucopotentialMitigations", []))
            c_related_patterns = format_list(c.get("ucorelatedAttackPatterns", []))
            c_status = c.get("ucostatus", "Unknown")

            # --- REPORT: THE CWE MASTER STORY ---
            report = (
                f"# Weakness Intelligence Report: {c_name}{nl}{nl}"
                f"**Executive Summary for {c_name}:**{nl}"
                f"The weakness '{c_name}' is described as follows: {c_desc}{nl}"
                f"{c_extended_desc}"
                f"{c_example}"
                f"This weakness is categorized at the {c_abstraction} abstraction level with a {c_structure} structure.{nl}{nl}"
                f"**Threat Profile for {c_name}:**{nl}"
                f"The likelihood of exploit for this weakness is {c_likelihood}.{nl}{nl}"
                f"This weakness is typically introduced during the following phases:{nl}{c_modes}{nl}{nl}"
                f"The platforms applicable to this weakness are:{nl}{c_platforms}{nl}{nl}"
                f"**Detection Methods for {c_name}:**{nl}"
                f"The following methods can be used to detect this weakness:{nl}{c_detection}{nl}{nl}"
                f"**Impact & Consequences of {c_name}:**{nl}"
                f"If the weakness '{c_name}' is exploited, it results in the following consequences for the target system:{nl}{c_cons}{nl}{nl}"
                f"**Mitigations for {c_name}:**{nl}"
                f"The following actions can mitigate this weakness:{nl}{c_mitigations}{nl}{nl}"
                f"**Taxonomy & Reference IDs:**{nl}"
                f"Related Attack Patterns:{nl}{c_related_patterns}{nl}{nl}"
                f"The official identifier for the weakness '{c_name}' is CWE ID: **{c_id}**.{nl}"
                f"Furthermore, the status of this weakness is {c_status}."
            )

            fout.write(json.dumps({"type": "text", "content": report}, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} CWE Master Reports.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    # Process only the specific CWE node for now
    convert_to_cwe_text_dump(filter_val="Improper Resource Shutdown or Release")
