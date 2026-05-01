import json
import argparse
import logging
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_cpe_data(uri, user, password, output_file, limit):
    logger.info(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # Simple query to get all UcoexCPE nodes
    query = """
        MATCH (c:UcoexCPE)
        RETURN c
    """
    if limit > 0:
        query += f" LIMIT {limit}"
        
    logger.info(f"Executing query (Limit: {limit})...")
    
    count = 0
    with driver.session() as session:
        result = session.run(query)
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in result:
                # Convert Neo4j Node/Rel objects to standard dicts
                row_data = {
                    "c": dict(record["c"]),
                    "c_id": record["c"].element_id if hasattr(record["c"], "element_id") else str(record["c"].id),
                }
                
                # Dump to JSONL
                # Use default=str to handle Datetime objects if any
                f.write(json.dumps(row_data, default=str) + "\n")
                count += 1
                if count % 100 == 0:
                    logger.info(f"Extracted {count} UcoexCPE nodes...")

    logger.info(f"Done. Saved {count} raw UcoexCPE nodes to {output_file}")
    driver.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Raw UCKG UcoexCPE Data to JSONL")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="abcd90909090")
    parser.add_argument("--output", default="examples/generate/generate_uckg/cpe_raw_data.jsonl")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    
    extract_cpe_data(args.uri, args.user, args.password, args.output, args.limit)
