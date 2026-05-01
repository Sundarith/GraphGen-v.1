import json
from collections import defaultdict

INPUT_FILE = "examples/generate/generate_uckg/filtered_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/raw_uckg_train_final.jsonl"

def build_final_dataset():
    print(f"Reading filtered data from {INPUT_FILE}...")
    
    # Dictionary to group mitigations by (Attack Name, Attack Domain)
    # Key: (a_name, a_domain), Value: List of Mitigation Dictionaries
    attack_map = defaultdict(list)

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                a = data.get("a", {})
                m = data.get("m", {})
                
                a_name = a.get("ucoexNAME")
                a_domain = a.get("ucoexDOMAIN", "unknown")
                
                m_name = m.get("ucoexNAME")
                m_desc = m.get("ucoexDESCRIPTION", "No description provided.")
                m_domain = m.get("ucoexDOMAIN", "unknown")

                if a_name:
                    attack_map[(a_name, a_domain)].append({
                        "name": m_name,
                        "description": m_desc,
                        "domain": m_domain
                    })

    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run the filter script first!")
        return

    print(f"Aggregating {len(attack_map)} unique attacks...")
    
    training_rows = []
    
    for (a_name, a_domain), mitigations in attack_map.items():
        # Deduplicate mitigations for the same attack (in case of matrix overlap)
        unique_mitigations = []
        seen_m_names = set()
        for m in mitigations:
            if m["name"] not in seen_m_names:
                unique_mitigations.append(m)
                seen_m_names.add(m["name"])
        
        m_count = len(unique_mitigations)
        
        # Build the bulleted list of mitigations
        mitigation_text_list = []
        for i, m in enumerate(unique_mitigations, start=1):
            mitigation_text_list.append(f"{i}. {m['name']}")
        
        all_mitigations_str = "\n".join(mitigation_text_list)
        
        # Create the ShareGPT row
        row = {
            "conversations": [
                {
                    "from": "system",
                    "value": "You are an expert Cybersecurity Analyst. Provide accurate threat intelligence and defensive strategies based on the requested domain."
                },
                {
                    "from": "human",
                    "value": f"What are the defensive mitigation strategies for '{a_name}' within the {a_domain} domain?"
                },
                {
                    "from": "gpt",
                    "value": f"Within the {a_domain} domain, to mitigate the attack '{a_name}', you must implement the following {m_count} strategies:\n\n{all_mitigations_str}"
                }
            ]
        }
        training_rows.append(row)

    # Write the final JSONL file
    print(f"Writing {len(training_rows)} training lessons to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for row in training_rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nSUCCESS! Your final 8-color Baseline Dataset is ready at: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_final_dataset()
