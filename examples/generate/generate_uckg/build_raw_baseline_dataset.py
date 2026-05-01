import json

INPUT_FILE = "examples/generate/generate_uckg/clean_data_attack_mitigation.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/raw_uckg_train.jsonl"

def build_baseline_dataset():
    print(f"Reading raw data from {INPUT_FILE}...")
    
    seen_attacks = set()
    seen_mitigations = set()
    training_rows = []

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                a = data.get("a", {})
                m = data.get("m", {})
                
                a_name = a.get("ucoexNAME")
                a_desc = a.get("ucoexDESCRIPTION")
                
                m_name = m.get("ucoexNAME")
                m_desc = m.get("ucoexDESCRIPTION")

                # 1. Generate Q&A for the Attack Pattern (Deduplicated)
                if a_name and a_desc and a_name not in seen_attacks:
                    seen_attacks.add(a_name)
                    
                    row = {
                        "conversations": [
                            {
                                "from": "system",
                                "value": "You are an expert Cybersecurity Analyst. Provide accurate threat intelligence based on the requested topic."
                            },
                            {
                                "from": "human",
                                "value": f"Describe the threat intelligence details for {a_name}."
                            },
                            {
                                "from": "gpt",
                                "value": a_desc
                            }
                        ]
                    }
                    training_rows.append(row)



    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Did you run the extraction script first?")
        return

    # Write the ShareGPT formatted dataset
    print(f"Writing {len(training_rows)} training pairs to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for row in training_rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("SUCCESS! Baseline dataset generated.")

if __name__ == "__main__":
    build_baseline_dataset()
