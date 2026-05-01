import json
import os
import sys

def view_text_dump():
    # Default to the CAPEC file, but allow user to pass another file as an argument
    default_file = "examples/generate/generate_uckg/uckg_cpe_text_dump_test.jsonl"
    
    if len(sys.argv) > 1:
        dump_file = sys.argv[1]
    else:
        dump_file = default_file

    if not os.path.exists(dump_file):
        print(f"Error: Could not find {dump_file}")
        return

    print(f"--- Viewing Reports from {dump_file} ---\n")
    
    count = 0
    with open(dump_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                content = data.get("content", "No content found.")
                
                print("=" * 80)
                print(f"REPORT #{count + 1}")
                print("=" * 80)
                print(content)
                print("\n")
                
                count += 1
            except json.JSONDecodeError:
                print("Error decoding JSON line.")
                
    print(f"--- Finished viewing {count} reports. ---")

if __name__ == "__main__":
    view_text_dump()
