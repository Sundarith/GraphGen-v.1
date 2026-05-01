import json

INPUT_FILE = "examples/generate/generate_uckg/filtered_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/raw_uckg_train_3.jsonl"

def build_mitigation_dataset():
    print(f"Reading filtered data from {INPUT_FILE}...")
    
    # Dictionary to deduplicate mitigations
    # Key: (m_name, m_domain), Value: m_description
    mitigation_map = {}

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                m = data.get("m", {})
                
                m_name = m.get("ucoexNAME")
                m_domain = m.get("ucoexDOMAIN", "unknown")
                m_desc = m.get("ucoexDESCRIPTION", "No description provided.")

                if m_name:
                    mitigation_map[(m_name, m_domain)] = m_desc

    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run the filter script first!")
        return

    print(f"Deduplicated {len(mitigation_map)} unique mitigation contexts.")
    
    training_rows = []
    
    for (m_name, m_domain), m_desc in mitigation_map.items():
        # Create the ShareGPT row with the Context-Aware Leading Phrase
        row = {
            "conversations": [
                {
                    "from": "system",
                    "value": "You are an expert Cybersecurity Analyst. Provide accurate defensive strategy definitions based on the requested domain."
                },
                {
                    "from": "human",
                    "value": f"Explain the defensive mitigation strategy known as '{m_name}' within the {m_domain} domain."
                },
                {
                    "from": "gpt",
                    "value": f"Within the {m_domain} context, the mitigation strategy '{m_name}' is technically defined as follows: {m_desc}"
                }
            ]
        }
        training_rows.append(row)

    # Write the final JSONL file
    print(f"Writing {len(training_rows)} mitigation lessons to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for row in training_rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nSUCCESS! Your Mitigation Baseline is ready at: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_mitigation_dataset()
