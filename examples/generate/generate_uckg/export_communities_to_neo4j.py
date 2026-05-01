import json
import glob
import os
import re
from neo4j import GraphDatabase

# Configuration for Sandbox 2 (Communities Only)
NEO4J_URI = "bolt://localhost:7689"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword2"

def export_communities():
    search_path = "cache/output/*/partition/*.jsonl"
    files = glob.glob(search_path)
    
    if not files:
        print("No partition files found! Run bash run_partition.sh first.")
        return
        
    latest_file = max(files, key=os.path.getmtime)
    print(f"Reading communities from: {latest_file}")
    
    print(f"Connecting to Community Sandbox at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return

    with driver.session() as session:
        with open(latest_file, 'r', encoding='utf-8') as f:
            total_communities = 0
            
            for community_id, line in enumerate(f, start=1):
                data = json.loads(line)
                nodes = json.loads(data['nodes'])
                edges = json.loads(data['edges'])
                total_communities += 1
                
                # 1. Insert Nodes for this community
                for node in nodes:
                    node_name = node[0].replace('"', '')
                    raw_type = node[1].get('entity_type', 'CONCEPT').replace('"', '').replace(' ', '_').replace('-', '_').upper()
                    cleaned_type = re.sub(r'[^A-Z0-9_]', '', raw_type)
                    
                    allowed_labels = ['ATTACK_PATTERN', 'CATEGORY', 'MITIGATION', 'VULNERABILITY', 'SOFTWARE', 'THREAT_ACTOR', 'TOOL', 'CONCEPT']
                    if cleaned_type in allowed_labels:
                        node_type = cleaned_type
                    else:
                        node_type = "CONCEPT"

                    node_desc = node[1].get('description', '').replace('"', "'")
                    
                    # Ensure node_type is first for coloring
                    query = f"""
                    MERGE (n:{node_type} {{id: $node_name, community_id: $community_id}})
                    SET n.name = $node_name, n.description = $desc
                    """
                    session.run(query, node_name=node_name, community_id=community_id, desc=node_desc)
                
                # 2. Insert Edges for this community
                for edge in edges:
                    src = edge[0].replace('"', '')
                    tgt = edge[1].replace('"', '')
                    desc = edge[2].get('description', '').replace('"', "'")
                    
                    query = """
                    MATCH (a {id: $src, community_id: $community_id})
                    MATCH (b {id: $tgt, community_id: $community_id})
                    MERGE (a)-[r:RELATED_TO]->(b)
                    SET r.description = $desc
                    """
                    session.run(query, src=src, tgt=tgt, community_id=community_id, desc=desc)
                    
        print(f"\nSUCCESS! Exported {total_communities} isolated communities into Sandbox 2.")
    
    driver.close()

if __name__ == "__main__":
    export_communities()
