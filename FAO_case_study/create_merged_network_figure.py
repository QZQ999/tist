#!/usr/bin/env python3
"""
Create merged network topology and capacity distribution figure
Left panel: Network topology with community structure and hub identification
Right panel: Capacity distribution histogram with statistics
"""
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import numpy as np
import networkx as nx

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'algorithms'))
sys.path.insert(0, os.path.join(current_dir, 'data'))

from fao_data_loader import FAODataLoader

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10


def create_merged_network_capacity_figure():
    """Create merged figure with network topology (left) and capacity distribution (right)"""

    # Load FAO data
    fao_data_dir = os.path.join(current_dir, 'data', 'FAO_Multiplex_Trade', 'Dataset')
    loader = FAODataLoader(data_dir=fao_data_dir)

    print("Loading FAO data...")
    top_layers = loader.select_top_layers(top_k=10, by='total_weight')
    G, capacities = loader.build_aggregated_network(selected_layers=top_layers)

    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Create figure with 1 row, 2 columns
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 7))

    # ====== LEFT PANEL: Network Topology with Community & Hubs ======
    print("Computing network metrics...")
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))

    # Detect communities
    print("Detecting communities...")
    try:
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(G)
        node_to_community = {}
        for idx, comm in enumerate(communities):
            for node in comm:
                node_to_community[node] = idx
    except:
        node_to_community = {node: 0 for node in G.nodes()}
        communities = [set(G.nodes())]

    # Compute layout using spring layout (no scipy required)
    print("Computing layout...")
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

    # Prepare node colors based on capacity (gradient)
    capacities_array = np.array([capacities.get(node, 10) for node in G.nodes()])
    norm = Normalize(vmin=capacities_array.min(), vmax=capacities_array.max())
    cmap = cm.YlOrRd  # Yellow-Orange-Red colormap

    # Node sizes based on degree centrality
    node_sizes = np.array([degree_centrality[node] * 2500 + 80 for node in G.nodes()])

    # Draw network
    nx.draw_networkx_edges(G, pos, alpha=0.12, width=0.3, edge_color='gray', ax=ax_left)

    # Draw nodes with capacity coloring
    scatter = ax_left.scatter([pos[node][0] for node in G.nodes()],
                             [pos[node][1] for node in G.nodes()],
                             s=node_sizes, c=capacities_array, cmap=cmap,
                             alpha=0.85, edgecolors='black', linewidths=0.6,
                             zorder=5)

    # Highlight top 5 hub nodes with golden stars
    top_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    for hub_node, cent in top_hubs:
        x, y = pos[hub_node]
        ax_left.scatter(x, y, s=1800, marker='*', c='gold', edgecolors='darkred',
                       linewidths=2.5, zorder=10, alpha=0.95)

    ax_left.set_title('(a) FAO Trade Network Topology\n' +
                      f'({G.number_of_nodes()} countries, {G.number_of_edges()} trade connections)',
                      fontsize=12, fontweight='bold', pad=10)
    ax_left.axis('off')

    # Add colorbar for capacity
    cbar = plt.colorbar(scatter, ax=ax_left, fraction=0.046, pad=0.04)
    cbar.set_label('Trade Capacity', fontweight='bold', fontsize=10)

    # Add legend for hub stars
    legend_elements = [
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gold',
                  markeredgecolor='darkred', markeredgewidth=2, markersize=15,
                  label='Top-5 Trading Hubs')
    ]
    ax_left.legend(handles=legend_elements, loc='upper left', frameon=True,
                  fontsize=10, framealpha=0.9)

    # ====== RIGHT PANEL: Capacity Distribution ======
    capacities_list = list(capacities.values())

    # Create histogram with colored bins
    n, bins, patches = ax_right.hist(capacities_list, bins=25, edgecolor='black',
                                     linewidth=1.2, alpha=0.8)

    # Color bins by capacity group
    for i, patch in enumerate(patches):
        bin_center = (bins[i] + bins[i+1]) / 2
        if bin_center < 50:
            patch.set_facecolor('#FDB462')  # Light Orange (Low capacity)
        elif bin_center < 100:
            patch.set_facecolor('#80B1D3')  # Light Blue (Medium capacity)
        elif bin_center < 150:
            patch.set_facecolor('#8DD3C7')  # Cyan (High capacity)
        else:
            patch.set_facecolor('#FB8072')  # Salmon (Very High capacity)

    # Calculate statistics
    mean_cap = np.mean(capacities_list)
    median_cap = np.median(capacities_list)
    std_cap = np.std(capacities_list)
    cv_cap = std_cap / mean_cap

    # Add vertical lines for mean and std
    ax_right.axvline(mean_cap, color='red', linestyle='--', linewidth=2.5,
                    label=f'Mean: {mean_cap:.2f}', alpha=0.9)
    ax_right.axvline(mean_cap - std_cap, color='orange', linestyle=':', linewidth=2,
                    label=f'Mean ± Std: {std_cap:.2f}', alpha=0.7)
    ax_right.axvline(mean_cap + std_cap, color='orange', linestyle=':', linewidth=2, alpha=0.7)

    ax_right.set_xlabel('Country Capacity (Normalized Trade Volume)', fontweight='bold', fontsize=11)
    ax_right.set_ylabel('Frequency (Number of Countries)', fontweight='bold', fontsize=11)
    ax_right.set_title(f'(b) Country Capacity Distribution\n' +
                      f'(Mean={mean_cap:.1f}, Std={std_cap:.1f}, CV={cv_cap:.2f})',
                      fontsize=12, fontweight='bold', pad=10)
    ax_right.grid(axis='y', alpha=0.3, linestyle='--')

    # Add capacity group legend
    legend_capacity_groups = [
        mpatches.Patch(facecolor='#FDB462', edgecolor='black', label='Low ($<$50)'),
        mpatches.Patch(facecolor='#80B1D3', edgecolor='black', label='Medium (50-100)'),
        mpatches.Patch(facecolor='#8DD3C7', edgecolor='black', label='High (100-150)'),
        mpatches.Patch(facecolor='#FB8072', edgecolor='black', label='Very High ($\\geq$150)')
    ]

    # Combine with statistical lines
    handles, labels = ax_right.get_legend_handles_labels()
    all_handles = legend_capacity_groups + handles
    ax_right.legend(handles=all_handles, loc='upper right', frameon=True,
                   fontsize=9, title='Capacity Groups', framealpha=0.95)

    plt.tight_layout()

    # Save figure
    output_dir = os.path.join(current_dir, 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    save_path_pdf = os.path.join(output_dir, 'network_and_capacity.pdf')
    save_path_png = os.path.join(output_dir, 'network_and_capacity.png')

    plt.savefig(save_path_pdf, bbox_inches='tight', dpi=300)
    plt.savefig(save_path_png, bbox_inches='tight', dpi=300)
    plt.close()

    print(f"\n✓ Saved merged figure:")
    print(f"  {save_path_pdf}")
    print(f"  {save_path_png}")


if __name__ == "__main__":
    create_merged_network_capacity_figure()
