import os
import sys

# Add root directory to python path so we can import graphgen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from graphgen.models.generator.multi_hop_generator_uckg import MultiHopGeneratorUCKG

def test_prompt_building():
    # 1. Mock Data (Simulating what PartitionService outputs from KuzuDB)
    # nodes format: list of tuples (node_id, property_dict)
    mock_nodes = [
        (
            "4:uuid-1234", 
            {
                "Name": "BlueSmacking", 
                "description": "An adversary uses Bluetooth flooding to transfer large packets..."
            }
        ),
        (
            "4:uuid-5678", 
            {
                "Name": "Denial of Service", 
                "description": "Adversaries may perform Denial of Service (DoS) attacks..."
            }
        ),
        (
            "4:uuid-9012", 
            {
                "Name": "Filter Network Traffic", 
                "description": "Employ network appliances to filter ingress and egress traffic..."
            }
        )
    ]

    # edges format: list of tuples (source_id, target_id, property_dict)
    mock_edges = [
        ("4:uuid-1234", "4:uuid-5678", {"description": "IS_A"}),
        ("4:uuid-9012", "4:uuid-5678", {"description": "MITIGATES"})
    ]

    # Combine into a batch
    mock_batch = (mock_nodes, mock_edges)

    # 2. Run the Generator's Prompt Builder
    print("--- GENERATING PROMPT FROM MOCK DATA ---")
    try:
        final_prompt = MultiHopGeneratorUCKG.build_prompt(mock_batch)
        print(final_prompt)
    except Exception as e:
        print(f"Error building prompt: {e}")

if __name__ == "__main__":
    test_prompt_building()
