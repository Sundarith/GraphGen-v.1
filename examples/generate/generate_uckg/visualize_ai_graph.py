import kuzu
import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(db_path="cache/graph_kuzu", output_file="ai_graph_visualization.png"):
    print(f"Connecting to KuzuDB at {db_path}...")
    try:
        db = kuzu.Database(db_path)
        conn = kuzu.Connection(db)
    except Exception as e:
        print(f"Failed to connect to KuzuDB: {e}")
        return

    # Create a directed graph
    G = nx.DiGraph()

    import json
    # Get all relationships (limit to 200 for clean visualization)
    print("Querying graph topology...")
    results = conn.execute("MATCH (a:Entity)-[r:Relation]->(b:Entity) RETURN a.id, b.id, r.data LIMIT 200")
    
    edge_count = 0
    while results.has_next():
        row = results.get_next()
        src = row[0].replace('"', '')
        tgt = row[1].replace('"', '')
        try:
            rel_data = json.loads(row[2])
            desc = rel_data.get("description", "")
        except:
            desc = ""
        
        G.add_edge(src, tgt, label=desc)
        edge_count += 1

    print(f"Extracted {edge_count} edges for visualization.")

    if edge_count == 0:
        print("No edges found to visualize.")
        return

    print("Rendering graph...")
    plt.figure(figsize=(16, 12))
    
    # Use a spring layout for organic clustering
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue', alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.5, edge_color='gray', arrows=True, arrowsize=15)
    
    # Draw labels (Names)
    # We wrap text so it fits in the bubbles
    labels = {node: '\\n'.join(node.split()) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold")

    plt.title("AI-Generated Knowledge Graph Topology", fontsize=16)
    plt.axis('off')
    
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"Success! Visualization saved to {output_file}")

if __name__ == "__main__":
    visualize_graph()
