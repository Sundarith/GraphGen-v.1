import json
import os
import glob
import sys

def view_latest_qa():
    # Find all generate folders
    search_path = "cache/output/*/generate"
    folders = glob.glob(search_path)
    
    if not folders:
        print("No generation folders found in cache/output/")
        return
        
    # Sort by the integer value of the folder name (the GraphGen unique ID timestamp)
    latest_folder = max(folders, key=lambda x: int(os.path.basename(os.path.dirname(x))))
    print(f"Reading from directory: {latest_folder}\n")
    print("="*60)
    
    # Get all jsonl files in that folder
    jsonl_files = glob.glob(os.path.join(latest_folder, "*.jsonl"))
    
    qa_count = 0
    for file_path in jsonl_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    q = data['conversations'][0]['value']
                    a = data['conversations'][1]['value']
                    
                    qa_count += 1
                    print(f"\n[QA PAIR {qa_count}]")
                    print(f"QUESTION:\n{q}\n")
                    print(f"ANSWER:\n{a}\n")
                    print("-" * 60)
                except Exception as e:
                    print(f"Error parsing line: {e}")

if __name__ == "__main__":
    view_latest_qa()
