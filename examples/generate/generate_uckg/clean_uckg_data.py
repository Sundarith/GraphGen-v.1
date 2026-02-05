import json
import argparse
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_messy_uckg_field(value):
    """Parses {key=[{json}]} strings into clean text."""
    if not isinstance(value, str):
        return value
    
    try:
        # Regex to find content between [ ... ]
        # Handling the specific format: key=[ ... ]}
        match = re.search(r'=\[(.*)\]\}?$', value)
        if match:
            inner_json = f"[{match.group(1)}]")
            data = json.loads(inner_json)
            
            text_lines = []
            for item in data:
                if isinstance(item, dict):
                    item_text = ", ".join(f"{k}: {v}" for k, v in item.items() if v)
                    text_lines.append(item_text)
                else:
                    text_lines.append(str(item))
            return "; ".join(text_lines)
    except Exception:
        pass
    return value

def clean_dict(d):
    """Recursively clean dictionary: remove embeddings, parse messy fields."""
    cleaned = {}
    excluded_keys = {'embedding', 'embeddings', 'vector', 'vectors', 'text_embedding'}
    messy_fields = {'ucopotentialMitigations', 'ucodetectionMethods', 'ucocommonConsequences', 'ucomodesOfIntroduction'}

    for k, v in d.items():
        if k in excluded_keys:
            continue
        
        # Heuristic for embeddings (long list of floats)
        if isinstance(v, list) and len(v) > 10 and isinstance(v[0], float):
            continue
            
        if k in messy_fields and isinstance(v, str):
            cleaned[k] = parse_messy_uckg_field(v)
        else:
            cleaned[k] = v
    return cleaned

def clean_data(input_file, output_file):
    logger.info(f"Cleaning data from {input_file}...")
    
    count = 0
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        
        for line in fin:
            raw_row = json.loads(line)
            
            # Clean each node/rel dictionary in the row
            clean_row = {
                "c": clean_dict(raw_row["c"]),
                "a": clean_dict(raw_row["a"]),
                "m": clean_dict(raw_row["m"]),
                "r1": raw_row["r1"], # Relationships usually don't have embeddings/messy JSON, but can clean if needed
                "r2": raw_row["r2"],
                "c_id": raw_row["c_id"],
                "a_id": raw_row["a_id"],
                "m_id": raw_row["m_id"]
            }
            
            fout.write(json.dumps(clean_row) + "\n")
            count += 1
            if count % 1000 == 0:
                logger.info(f"Cleaned {count} rows...")
                
    logger.info(f"Done. Cleaned {count} rows. Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Raw UCKG Data")
    parser.add_argument("--input", default="examples/generate/generate_uckg/raw_data.jsonl")
    parser.add_argument("--output", default="examples/generate/generate_uckg/clean_data.jsonl")
    args = parser.parse_args()
    
    clean_data(args.input, args.output)
