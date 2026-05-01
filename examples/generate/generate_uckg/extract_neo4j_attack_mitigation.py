import json
from neo4j import GraphDatabase

# Live UCKG Database Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "abcd90909090"
OUTPUT_FILE = "examples/generate/generate_uckg/clean_data_attack_mitigation.jsonl"

def extract_raw_data():
    print(f"Connecting to Live UCKG Database at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return

    # Cypher Query to pull ONLY Attack Patterns and their Mitigations
    query = """
    MATCH (a:UcoexMITREATTACK)<-[r:UCOEXMITIGATES]-(m:UcoexMITIGATIONS)
    RETURN a, m
    """

    print("Running Cypher query to extract Attack -> Mitigation paths...")
    
    with driver.session() as session:
        results = session.run(query)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            count = 0
            for record in results:
                # Filter Neo4j Node objects to only the requested properties
                a_node = record["a"]
                m_node = record["m"]
                
                a_data = {
                    "ucoexNAME": a_node.get("ucoexNAME"),
                    "ucoexDESCRIPTION": a_node.get("ucoexDESCRIPTION"),
                    "ucoexURL": a_node.get("ucoexURL")
                }
                
                m_data = {
                    "ucoexNAME": m_node.get("ucoexNAME"),
                    "ucoexDESCRIPTION": m_node.get("ucoexDESCRIPTION"),
                    "ucoexURL": m_node.get("ucoexURL")
                }
                
                row = {
                    "a": a_data,
                    "m": m_data
                }
                
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1
                
                if count % 100 == 0:
                    print(f"Extracted {count} paths...")

    driver.close()
    print(f"\nSUCCESS! Extracted {count} total Attack-Mitigation paths.")
    print(f"Saved fresh dataset to: {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_raw_data()
