import json
import os
import glob

def view_latest_communities():
    # Find the most recent partition file
    search_path = "cache/output/*/partition/*.jsonl"
    files = glob.glob(search_path)
    
    if not files:
        print("No partition files found in cache/output/")
        return
        
    # Sort by modification time to get the latest
    latest_file = max(files, key=os.path.getmtime)
    print(f"Reading from: {latest_file}\n")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            nodes = json.loads(data['nodes'])
            
            print(f"--- COMMUNITY {i+1} ---")
            print(f"Total Nodes: {len(nodes)}")
            print("Nodes Included:")
            for node in nodes:
                name = node[0].replace('"', '')
                print(f"  - {name}")
            print("\n")

if __name__ == "__main__":
    view_latest_communities()
