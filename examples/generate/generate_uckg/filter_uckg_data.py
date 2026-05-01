import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define which properties to KEEP for each node type
WHITELIST = {
    "a": { # ATT&CK
        "ucoexNAME", 
        "ucoexDESCRIPTION",
        "ucoexDOMAIN"
    },
    "m": { # MITIGATION
        "ucoexNAME", 
        "ucoexDESCRIPTION",
        "ucoexDOMAIN"
    }
}

def filter_dict(d, node_key):
    """Keep only whitelisted keys from the dictionary in a specific order."""
    if not d:
        return {}

    # Manually define order for cleaner output
    filtered = {}
    if "ucoexNAME" in d:
        filtered["ucoexNAME"] = d.get("ucoexNAME")
    if "ucoexDOMAIN" in d:
        filtered["ucoexDOMAIN"] = d.get("ucoexDOMAIN")
    if "ucoexDESCRIPTION" in d:
        filtered["ucoexDESCRIPTION"] = d.get("ucoexDESCRIPTION")

    return filtered

def filter_data(input_file, output_file):
    logger.info(f"Filtering data from {input_file}...")
    
    count = 0
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            raw_row = json.loads(line)
            
            # Apply filter to each node (Attack and Mitigation only)
            filtered_row = {
                "a": filter_dict(raw_row.get("a"), "a"),
                "m": filter_dict(raw_row.get("m"), "m"),
                "r": raw_row.get("r"),
                "a_id": raw_row.get("a_id"),
                "m_id": raw_row.get("m_id")
            }
            
            fout.write(json.dumps(filtered_row) + "\n")
            count += 1
            if count % 1000 == 0:
                logger.info(f"Filtered {count} rows...")
                
    logger.info(f"Done. Filtered {count} rows. Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter UCKG Data Properties")
    parser.add_argument("--input", default="examples/generate/generate_uckg/raw_data.jsonl")
    parser.add_argument("--output", default="examples/generate/generate_uckg/filtered_data.jsonl")
    args = parser.parse_args()
    
    filter_data(args.input, args.output)
