import json

INPUT_FILE = "examples/generate/generate_uckg/filtered_data.jsonl"
OUTPUT_FILE = "examples/generate/generate_uckg/raw_uckg_train_natural.jsonl"

def build_natural_dataset():
    print(f"Reading filtered data from {INPUT_FILE}...")
    
    # Dictionary to deduplicate attacks
    # Key: (a_name, a_domain), Value: a_description
    attack_map = {}

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                a = data.get("a", {})
                
                a_name = a.get("ucoexNAME")
                a_domain = a.get("ucoexDOMAIN", "unknown")
                a_desc = a.get("ucoexDESCRIPTION", "No description provided.")

                if a_name:
                    attack_map[(a_name, a_domain)] = a_desc

    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run the filter script first!")
        return

    print(f"Deduplicated {len(attack_map)} unique attacks.")
    
    training_rows = []
    
    for (a_name, a_domain), a_desc in attack_map.items():
        # Create the ShareGPT row with the "Natural Leading Phrase"
        row = {
            "conversations": [
                {
                    "from": "system",
                    "value": "You are an expert Cybersecurity Analyst. Provide accurate threat intelligence and technical definitions based on the requested domain."
                },
                {
                    "from": "human",
                    "value": f"Provide the technical threat intelligence details for the '{a_name}' attack within the {a_domain} domain."
                },
                {
                    "from": "gpt",
                    "value": f"Within the {a_domain} domain, the {a_name} technique is technically defined as follows: {a_desc}"
                }
            ]
        }
        training_rows.append(row)

    # Write the final JSONL file
    print(f"Writing {len(training_rows)} natural lessons to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        for row in training_rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nSUCCESS! Your Natural Factual Baseline is ready at: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_natural_dataset()
