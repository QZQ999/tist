#!/usr/bin/env python3
"""
Export FAO Trade Network to Gephi-compatible GEXF format
GEXF is Gephi's native format and supports node/edge attributes
"""
import sys
import os
import networkx as nx

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'algorithms'))
sys.path.insert(0, os.path.join(current_dir, 'data'))

from fao_data_loader import FAODataLoader


def export_to_gephi():
    """Export FAO network to Gephi GEXF format"""

    # Load FAO data
    print("Loading FAO Trade Network data...")
    fao_data_dir = os.path.join(current_dir, 'data', 'FAO_Multiplex_Trade', 'Dataset')
    loader = FAODataLoader(data_dir=fao_data_dir)

    # Select top 10 products
    top_layers = loader.select_top_layers(top_k=10, by='total_weight')

    # Build aggregated network
    G, capacities = loader.build_aggregated_network(selected_layers=top_layers)

    print(f"\nNetwork Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.4f}")

    # Get country names mapping from loader
    country_names = loader.nodes  # node_id -> country_name mapping
    print(f"  Country names: {len(country_names)} loaded")

    # Calculate network metrics for visualization
    print("\nCalculating network metrics...")

    # Degree centrality
    degree_centrality = nx.degree_centrality(G)

    # Betweenness centrality (sample for large networks)
    if G.number_of_nodes() > 200:
        betweenness = nx.betweenness_centrality(G, k=100)
    else:
        betweenness = nx.betweenness_centrality(G)

    # Clustering coefficient
    clustering = nx.clustering(G)

    # Eigenvector centrality (alternative to PageRank, no scipy needed)
    print("  Computing eigenvector centrality...")
    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=100)
    except:
        # Fallback: use degree centrality as proxy
        print("  Eigenvector centrality failed, using degree centrality")
        eigenvector = degree_centrality.copy()

    # Add node attributes
    print("Adding node attributes...")
    for node in G.nodes():
        # Use actual country name from FAO data
        country_name = country_names.get(node, f"Unknown_{node}")
        G.nodes[node]['label'] = country_name
        G.nodes[node]['name'] = country_name  # Also set 'name' attribute for GEXF
        G.nodes[node]['capacity'] = float(capacities.get(node, 10))
        G.nodes[node]['degree'] = G.degree(node)
        G.nodes[node]['degree_centrality'] = float(degree_centrality[node])
        G.nodes[node]['betweenness_centrality'] = float(betweenness[node])
        G.nodes[node]['clustering_coefficient'] = float(clustering[node])
        G.nodes[node]['eigenvector_centrality'] = float(eigenvector[node])

        # Capacity tier classification
        cap = capacities.get(node, 10)
        if cap < 50:
            tier = "Low"
        elif cap < 100:
            tier = "Medium"
        elif cap < 150:
            tier = "High"
        else:
            tier = "Very High"
        G.nodes[node]['capacity_tier'] = tier

    # Detect communities for coloring in Gephi
    print("Detecting communities...")
    try:
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(G)

        # Assign community IDs
        for idx, comm in enumerate(communities):
            for node in comm:
                G.nodes[node]['community'] = idx
                G.nodes[node]['modularity_class'] = idx  # Gephi uses this

        print(f"  Found {len(communities)} communities")
    except Exception as e:
        print(f"  Community detection skipped: {e}")
        for node in G.nodes():
            G.nodes[node]['community'] = 0
            G.nodes[node]['modularity_class'] = 0

    # Identify hub nodes (top 5% by degree)
    print("Identifying hub nodes...")
    degrees = sorted([(node, G.degree(node)) for node in G.nodes()],
                     key=lambda x: x[1], reverse=True)
    top_5_percent = max(1, int(0.05 * len(degrees)))
    hub_nodes = set([node for node, _ in degrees[:top_5_percent]])

    for node in G.nodes():
        G.nodes[node]['is_hub'] = node in hub_nodes

    # Export to GEXF format
    output_dir = os.path.join(current_dir, 'results', 'gephi')
    os.makedirs(output_dir, exist_ok=True)

    gexf_file = os.path.join(output_dir, 'gephi.gexf')

    print(f"\nExporting to GEXF format...")
    nx.write_gexf(G, gexf_file)

    print(f"\n✓ Network exported successfully!")
    print(f"\nOutput file: {gexf_file}")
    print(f"\nGephi Import Instructions:")
    print("1. Open Gephi")
    print("2. File -> Open -> Select 'gephi.gexf'")
    print("3. In the 'Import report' dialog, click 'OK'")
    print("\nVisualization Tips:")
    print("- Node size: Use 'degree_centrality' or 'capacity'")
    print("- Node color: Use 'modularity_class' (communities)")
    print("- Layout: Try 'Force Atlas 2' or 'Yifan Hu'")
    print("- Edge weight: Already included in file")
    print("\nNode Attributes Available:")
    print("  - capacity: Trade capacity (normalized 10-200)")
    print("  - capacity_tier: Low/Medium/High/Very High")
    print("  - degree: Number of connections")
    print("  - degree_centrality: Normalized degree centrality")
    print("  - betweenness_centrality: Betweenness centrality")
    print("  - clustering_coefficient: Local clustering")
    print("  - eigenvector_centrality: Eigenvector centrality score")
    print("  - community/modularity_class: Community assignment")
    print("  - is_hub: Boolean flag for hub nodes (top 5%)")

    # Also export as CSV for alternative import
    print(f"\nAlso creating CSV format (alternative)...")

    # Export nodes
    nodes_csv = os.path.join(output_dir, 'gephi_nodes.csv')
    with open(nodes_csv, 'w') as f:
        f.write("Id,Label,Capacity,CapacityTier,Degree,DegreeCentrality,BetweennessCentrality,ClusteringCoefficient,EigenvectorCentrality,Community,IsHub\n")
        for node in G.nodes():
            attrs = G.nodes[node]
            f.write(f"{node},{attrs['label']},{attrs['capacity']},{attrs['capacity_tier']},{attrs['degree']},"
                   f"{attrs['degree_centrality']:.6f},{attrs['betweenness_centrality']:.6f},"
                   f"{attrs['clustering_coefficient']:.6f},{attrs['eigenvector_centrality']:.6f},"
                   f"{attrs['community']},{attrs['is_hub']}\n")

    # Export edges
    edges_csv = os.path.join(output_dir, 'gephi_edges.csv')
    with open(edges_csv, 'w') as f:
        f.write("Source,Target,Weight,Type\n")
        for source, target, data in G.edges(data=True):
            weight = data.get('weight', 1.0)
            f.write(f"{source},{target},{weight},Undirected\n")

    print(f"  Nodes CSV: {nodes_csv}")
    print(f"  Edges CSV: {edges_csv}")
    print("\nCSV Import Instructions (alternative to GEXF):")
    print("1. In Gephi: File -> Import Spreadsheet")
    print("2. Import nodes first (gephi_nodes.csv)")
    print("3. Then import edges (gephi_edges.csv)")


if __name__ == "__main__":
    export_to_gephi()
