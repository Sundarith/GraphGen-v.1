import json
import os

# Input from our ETL pipeline (The unfiltered raw data)
INPUT_FILE = "examples/generate/generate_uckg/raw_data.jsonl"
# Output for GraphGen (A separate file for Defense Briefs)
OUTPUT_FILE = "examples/generate/generate_uckg/defense_brief_dump.jsonl"

def convert_to_defense_brief(limit=1, skip=0):
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
            
            a = row.get("a", {})
            m = row.get("m", {})

            # Extract Shared Bridge: Technique ID (from URI like ...#T1498.001)
            uri = a.get("uri", "")
            technique_id = uri.split("#")[-1] if "#" in uri else "Unknown ID"
            
            # Extract Mitigation ID (from URL like .../mitigations/M1037)
            m_url = m.get("ucoexURL", "")
            mitigation_id = m_url.split("/")[-1] if "mitigations" in m_url else "Unknown M-ID"

            # Extract Names
            a_name = a.get("ucoexNAME", "Unknown Technique")
            m_name = m.get("ucoexNAME", "Unknown Mitigation")

            # Extract Descriptions & Domains
            a_desc = a.get("ucoexDESCRIPTION", "No description.")
            m_desc = m.get("ucoexDESCRIPTION", "No description.")
            a_domain = a.get("ucoexDOMAIN", "Unknown Domain")
            m_domain = m.get("ucoexDOMAIN", "Unknown Domain")

            nl = chr(10)
            
            # --- REPORT: THE TECHNIQUE & MITIGATION DEFENSE BRIEF ---
            report = (
                f"# Security Mitigation Brief for {m_name}{nl}{nl}"
                f"**Tactical Threat Context for {a_name}:**{nl}"
                f"Within the {a_domain} domain, adversaries utilize the attack technique '{a_name}'. This technique is described as follows: {a_desc}{nl}{nl}"
                f"**Recommended Defensive Response:**{nl}"
                f"To counter the tactical threat of the attack technique '{a_name}', organizations must implement the defensive mitigation: '{m_name}'.{nl}{nl}"
                f"**Implementation Details for {m_name}:**{nl}"
                f"Specifically within the {m_domain} domain, the defensive mitigation '{m_name}' is implemented through the following technical measures:{nl}"
                f"{m_desc}{nl}{nl}"
                f"**Taxonomy & Reference IDs:**{nl}"
                f"The official identifier for the attack technique '{a_name}' is MITRE ATT&CK Technique ID: **{technique_id}**.{nl}"
                f"The official identifier for the defensive mitigation '{m_name}' is Mitigation ID: **{mitigation_id}**."
            )

            # Wrap it in the strict schema GraphGen expects
            graphgen_format = {
                "type": "text",
                "content": report
            }
            
            fout.write(json.dumps(graphgen_format, ensure_ascii=False) + nl)
            
            count += 1
            if limit and count >= limit:
                break
                
    print(f"Success! Generated {count} Technique & Mitigation Defense Briefs.")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_to_defense_brief(limit=1, skip=0)
