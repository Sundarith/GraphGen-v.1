import json
import re
import kuzu
from neo4j import GraphDatabase

# Configuration
KUZU_DB_PATH = "cache/graph_kuzu"
NEO4J_URI = "bolt://localhost:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword"

def export_to_neo4j():
    print(f"Connecting to KuzuDB at {KUZU_DB_PATH}...")
    try:
        db = kuzu.Database(KUZU_DB_PATH)
        conn = kuzu.Connection(db)
    except Exception as e:
        print(f"Failed to connect to KuzuDB: {e}")
        return

    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return

    # Extract Nodes
    print("Extracting nodes from Kuzu...")
    results = conn.execute("MATCH (a:Entity) RETURN a.id, a.data")
    
    nodes = []
    while results.has_next():
        row = results.get_next()
        node_id = row[0].replace('"', '')
        try:
            data = json.loads(row[1])
        except:
            data = {}
        nodes.append({"id": node_id, "data": data})
        
    print(f"Found {len(nodes)} nodes.")

    # Extract Edges
    print("Extracting relationships from Kuzu...")
    results = conn.execute("MATCH (a:Entity)-[r:Relation]->(b:Entity) RETURN a.id, b.id, r.data")
    
    edges = []
    while results.has_next():
        row = results.get_next()
        src = row[0].replace('"', '')
        tgt = row[1].replace('"', '')
        try:
            data = json.loads(row[2])
            desc = data.get("description", "CONNECTED_TO")
        except:
            desc = "CONNECTED_TO"
            
        edges.append({"src": src, "tgt": tgt, "desc": desc})
        
    print(f"Found {len(edges)} relationships.")

    if not nodes:
        print("Nothing to export.")
        return

    print("Uploading to Neo4j...")
    
    with driver.session() as session:
        # 1. Create Nodes
        for n in nodes:
            node_id = n['id']
            # Default to AI_Entity, but use entity_type if Gemini provided one
            raw_label = n['data'].get('entity_type', 'CONCEPT').replace('"', '').replace(' ', '_').replace('-', '_').upper()
            cleaned_label = re.sub(r'[^A-Z0-9_]', '', raw_label)
            
            allowed_labels = ['ATTACK_PATTERN', 'CATEGORY', 'MITIGATION', 'VULNERABILITY', 'SOFTWARE', 'THREAT_ACTOR', 'TOOL', 'CONCEPT']
            
            if cleaned_label in allowed_labels:
                label = cleaned_label
            else:
                label = "CONCEPT"
                
            # Safely create properties
            desc = n['data'].get('description', '').replace('"', "'")
            
            # Using MERGE to avoid duplicates. Using a generic 'AIGeneratedNode' label + specific type
            query = f"""
            MERGE (n:{label} {{id: $node_id}})
            SET n.name = $node_id, n.description = $desc
            """
            session.run(query, node_id=node_id, desc=desc)
            
        print("Nodes uploaded.")

        # 2. Create Relationships
        for e in edges:
            src = e['src']
            tgt = e['tgt']
            rel_type = "AI_CONNECTION" # Default
            
            # Clean up the edge description to use as a Neo4j Relationship Type
            # Neo4j relation types must be alphanumeric and no spaces
            desc = e['desc']
            if len(desc) < 30 and desc.isupper():
                # If Gemini output something like "MITIGATES", use it directly
                rel_type = desc.replace(' ', '_').replace('"', '').replace('-', '_')
                rel_type = re.sub(r'[^A-Z0-9_]', '', rel_type)
            
            query = f"""
            MATCH (a {{id: $src}})
            MATCH (b {{id: $tgt}})
            MERGE (a)-[r:{rel_type}]->(b)
            SET r.description = $desc
            """
            session.run(query, src=src, tgt=tgt, desc=desc)

        print("Relationships uploaded.")

    driver.close()
    print("\nSUCCESS! Open http://localhost:7474 and run:")
    print("MATCH (n:AIGeneratedNode) RETURN n")

if __name__ == "__main__":
    export_to_neo4j()
