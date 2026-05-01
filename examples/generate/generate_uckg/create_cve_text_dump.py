import json
import os

INPUT_FILE = "examples/generate/generate_uckg/cve_raw_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/uckg_cve_text_dump_test.jsonl"

def convert_to_cve_text_dump(limit=None, skip=0, filter_val=None):
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
            c = row.get("c", {})
            
            c_name = c.get("label", "Unknown")
            if c_name == "Unknown":
                uri = c.get("uri", "")
                if uri:
                    c_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
            
            # Apply Filter if provided
            if filter_val and filter_val.lower() not in c_name.lower():
                continue

            # Extract properties
            severity = c.get("ucobaseSeverity", "N/A")
            exploitability = c.get("ucoexploitabilityScore", "N/A")
            impact = c.get("ucoimpactScore", "N/A")
            status = c.get("ucovulnStatus", "N/A")
            vector = c.get("ucovectorString", "N/A")
            privilege = c.get("ucoobtainAllPrivilege", "N/A")
            interaction = c.get("ucouserInteractionRequired", "N/A")
            solution = c.get("ucoevaluatorSolution", "")

            nl = chr(10)

            # --- REPORT: THE CVE MASTER STORY ---
            report = (
                f"# Common Vulnerability Report: {c_name}{nl}{nl}"
                f"**Executive Summary for {c_name}:**{nl}"
                f"The vulnerability '{c_name}' has a Base Severity of {severity}.{nl}"
                f"The Exploitability Score for this vulnerability is {exploitability}, with an Impact Score of {impact}.{nl}"
                f"Its CVSS Vector String is represented as {vector}.{nl}"
                f"Currently, the Vulnerability Status is marked as {status}.{nl}"
                f"Does this vulnerability obtain all privileges? {privilege}.{nl}"
                f"Is user interaction required? {interaction}.{nl}"
            )
            
            if solution and solution.strip():
                report += f"{nl}**Evaluator Solution for {c_name}:**{nl}{solution.strip()}{nl}"

            fout.write(json.dumps({"type": "text", "content": report}, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} CVE Master Reports.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_to_cve_text_dump(filter_val="CVE-2001-0830")
