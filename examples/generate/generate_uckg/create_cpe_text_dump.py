import json
import os
import urllib.parse

INPUT_FILE = "examples/generate/generate_uckg/cpe_raw_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/uckg_cpe_text_dump_test.jsonl"

def parse_cpe_string(cpe_string):
    """Parse CPE 2.3 string into its basic components."""
    parts = cpe_string.split(":")
    # cpe:2.3:part:vendor:product:version:update:edition:language:sw_edition:target_sw:target_hw:other
    parsed = {
        "part": "Unknown",
        "vendor": "Unknown",
        "product": "Unknown",
        "version": "Unknown"
    }

    if len(parts) >= 6 and parts[0] == "cpe" and parts[1] == "2.3":
        part_map = {"a": "Application", "o": "Operating System", "h": "Hardware"}
        parsed["part"] = part_map.get(parts[2], parts[2])
        parsed["vendor"] = urllib.parse.unquote(parts[3]) if parts[3] != "*" else "Any"
        parsed["product"] = urllib.parse.unquote(parts[4]) if parts[4] != "*" else "Any"
        parsed["version"] = urllib.parse.unquote(parts[5]) if parts[5] != "*" else "Any"

    return parsed

def convert_to_cpe_text_dump(limit=None, skip=0, filter_val=None):
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
            
            cpe_name = c.get("cpeName", "")
            if not cpe_name:
                continue

            if filter_val and filter_val.lower() not in cpe_name.lower():
                continue

            parsed_cpe = parse_cpe_string(cpe_name)
            dictionary_found = c.get("dictionary_found", "Unknown")

            nl = chr(10)

            # Build a multi-section Intelligence Report for the CPE
            report = (
                f"# Component Platform Enumeration (CPE): {cpe_name}{nl}{nl}"
                f"**Executive Summary:**{nl}"
                f"This report covers the precise configuration identity for the component {cpe_name}. "
                f"This enumeration specifically identifies a unique software, OS, or hardware asset configuration within the environment.{nl}{nl}"
                f"**Component Breakdown:**{nl}"
                f"The structured elements of this platform enumeration are as follows:{nl}"
                f"- **Component Type:** {parsed_cpe['part']}{nl}"
                f"- **Vendor:** {parsed_cpe['vendor']}{nl}"
                f"- **Product Name:** {parsed_cpe['product']}{nl}"
                f"- **Version:** {parsed_cpe['version']}{nl}{nl}"
                f"**Reference Information:**{nl}"
                f"Is this component definitely located in the official NIST CPE dictionary? {dictionary_found}.{nl}"
            )

            fout.write(json.dumps({"type": "text", "content": report}, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} CPE Reports.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    # Generate for the specific CPE node only
    convert_to_cpe_text_dump(filter_val="cpe:2.3:a:6tunnel_project:6tunnel")
