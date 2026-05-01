import json
import os

# Input from our ETL pipeline
INPUT_FILE = "examples/generate/generate_uckg/ucoex_raw_data.jsonl"
# Output for GraphGen
OUTPUT_FILE = "examples/generate/generate_uckg/uckg_ucoex_text_dump_test.jsonl"

def convert_to_ucoex_text_dump(limit=None, skip=0, filter_val=None):
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
            
            # Assume UcoexObservedExample node is in 'u'
            u = row.get("u", {})
            
            uri = u.get("uri", "")
            u_desc = u.get("ucoexDESCRIPTION", "No description available.")
            
            if not uri and not u_desc:
                continue

            # Extract identifier from URI (e.g., CWE-805-CVE-2010-4156) if possible
            u_name = "Unknown Example"
            if uri:
                u_name = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]

            # Parse out CWE and CVE if they are combined in the identifier
            cwe_id = "Unknown"
            cve_id = "Unknown"
            
            if "CWE-" in u_name and "-CVE-" in u_name:
                parts = u_name.split("-CVE-")
                cwe_id = parts[0]
                cve_id = "CVE-" + parts[1]
            elif u_name.startswith("CWE-"):
                cwe_id = u_name
            elif u_name.startswith("CVE-"):
                cve_id = u_name

            # Apply Filter if provided
            if filter_val:
                if filter_val.lower() not in u_name.lower() and filter_val.lower() not in u_desc.lower():
                    continue

            nl = chr(10)

            # Format the title nicely so the AI doesn't get a long concatenated string
            title_name = "Unknown Example"
            if cwe_id != "Unknown" and cve_id != "Unknown":
                title_name = f"{cwe_id} and {cve_id}"
            elif cwe_id != "Unknown":
                title_name = cwe_id
            elif cve_id != "Unknown":
                title_name = cve_id
            else:
                title_name = u_name

            # --- REPORT: THE UCOEX MASTER STORY ---
            report = (
                f"# Observed Example Intelligence Report: {title_name}{nl}{nl}"
                f"**Executive Summary:**{nl}"
                f"This observed example is described as follows:{nl}"
                f"{u_desc}{nl}{nl}"
                f"**Taxonomy & Reference IDs:**{nl}"
                f"Related Weakness (CWE): {cwe_id}{nl}"
                f"Related Vulnerability (CVE): {cve_id}{nl}"
            )

            fout.write(json.dumps({"type": "text", "content": report}, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} Ucoex Master Reports.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_to_ucoex_text_dump(filter_val="Sockets not properly closed when attacker repeatedly connects and disconnects from server.")
