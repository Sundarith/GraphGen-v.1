import os
import glob
import json

def main():
    datasets = {
        "bluesmacking_1hop.jsonl": "cache/output/1776622680/generate/*.jsonl",
        "bluesmacking_2hop.jsonl": "cache/output/1776481730-bluesmacking-2hop-bidirectional/generate/*.jsonl",
        "bluesmacking_3hop.jsonl": "cache/output/1776460551-bluesmacking-3hop-bidirectional/generate/*.jsonl",
        "bluesmacking_4hop.jsonl": "cache/output/1776530114-bluesmacking-4hops-bidirectional/generate/*.jsonl",
        "bluesmacking_5hop.jsonl": "cache/output/1776531090-bluesmacking-5hops-bidirectional/generate/*.jsonl"
    }

    out_dir = "examples/generate/generate_uckg"
    os.makedirs(out_dir, exist_ok=True)

    for out_name, pattern in datasets.items():
        out_path = os.path.join(out_dir, out_name)
        merged_count = 0
        with open(out_path, 'w', encoding='utf-8') as outfile:
            for filepath in glob.glob(pattern):
                with open(filepath, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        if line.strip():
                            outfile.write(line.strip() + '\n')
                            merged_count += 1
        print(f"Created {out_path} with {merged_count} QA pairs.")

if __name__ == '__main__':
    main()
