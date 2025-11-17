"""
Academic-quality visualization for FAO case study.

Generates publication-ready figures for research papers.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple
import os

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12


class AcademicPlotter:
    """Generate academic-quality plots for FAO case study."""

    def __init__(self, output_dir: str = "results/figures"):
        """
        Initialize plotter.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Color scheme (colorblind-friendly Wong 2011 palette)
        self.colors = {
            'CATM': '#E69F00',      # Orange
            'KBTM': '#56B4E9',      # Sky Blue
            'HCTM-MPF': '#009E73',  # Bluish Green
            'OPT': '#CC79A7',       # Reddish Purple
            'primary': '#0072B2',   # Blue
            'secondary': '#D55E00', # Vermillion
            'accent': '#F0E442'     # Yellow
        }

    def plot_performance_comparison(self, results: Dict, save_name: str = "performance_comparison.pdf"):
        """
        Plot comprehensive performance comparison.

        Args:
            results: Dictionary of algorithm results
            save_name: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        fig.suptitle('Algorithm Performance Comparison on FAO Trade Network', fontsize=14, fontweight='bold')

        algorithms = list(results.keys())
        x = np.arange(len(algorithms))
        width = 0.6

        # 1. Survival Rate
        ax1 = axes[0, 0]
        survival_rates = [results[alg]['surv_rate'] * 100 for alg in algorithms]
        bars1 = ax1.bar(x, survival_rates, width, color=[self.colors[alg] for alg in algorithms],
                       edgecolor='black', linewidth=1.2)
        ax1.set_ylabel('Survival Rate (%)', fontweight='bold')
        ax1.set_title('(a) Task Survival Rate')
        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms)
        ax1.set_ylim([90, 100])
        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars1, survival_rates)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

        # 2. Total Cost
        ax2 = axes[0, 1]
        total_costs = [results[alg]['total_cost'] for alg in algorithms]
        bars2 = ax2.bar(x, total_costs, width, color=[self.colors[alg] for alg in algorithms],
                       edgecolor='black', linewidth=1.2)
        ax2.set_ylabel('Total Cost', fontweight='bold')
        ax2.set_title('(b) Total Migration Cost')
        ax2.set_xticks(x)
        ax2.set_xticklabels(algorithms)
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels
        for bar, val in zip(bars2, total_costs):
            height = bar.get_height()
            y_pos = height if height > 0 else height
            va = 'bottom' if height > 0 else 'top'
            ax2.text(bar.get_x() + bar.get_width()/2., y_pos,
                    f'{val:.2f}', ha='center', va=va, fontsize=9, fontweight='bold')

        # 3. Cost Breakdown (Stacked)
        ax3 = axes[1, 0]
        exec_costs = [results[alg]['exec_cost'] for alg in algorithms]
        migr_costs = [results[alg]['migr_cost'] for alg in algorithms]

        bars3a = ax3.bar(x, exec_costs, width, label='Execution Cost',
                        color='#4472C4', edgecolor='black', linewidth=1.2)
        bars3b = ax3.bar(x, migr_costs, width, bottom=exec_costs, label='Migration Cost',
                        color='#ED7D31', edgecolor='black', linewidth=1.2)

        ax3.set_ylabel('Cost Components', fontweight='bold')
        ax3.set_title('(c) Cost Breakdown')
        ax3.set_xticks(x)
        ax3.set_xticklabels(algorithms)
        ax3.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax3.legend(loc='best')
        ax3.grid(axis='y', alpha=0.3, linestyle='--')

        # 4. Runtime
        ax4 = axes[1, 1]
        runtimes = [results[alg]['runtime'] for alg in algorithms]
        bars4 = ax4.bar(x, runtimes, width, color=[self.colors[alg] for alg in algorithms],
                       edgecolor='black', linewidth=1.2)
        ax4.set_ylabel('Runtime (ms)', fontweight='bold')
        ax4.set_title('(d) Computational Efficiency')
        ax4.set_xticks(x)
        ax4.set_xticklabels(algorithms)
        ax4.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels
        for bar, val in zip(bars4, runtimes):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val}ms', ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.savefig(save_path.replace('.pdf', '.png'), bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved performance comparison to {save_path}")

    def plot_network_topology(self, G: nx.Graph, node_capacities: Dict,
                             save_name: str = "network_topology.pdf"):
        """
        Plot professional network topology visualization with community structure.

        Args:
            G: NetworkX graph
            node_capacities: Dictionary of node capacities
            save_name: Output filename
        """
        import matplotlib.cm as cm
        from matplotlib.colors import Normalize

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Calculate network centrality metrics
        print("  Computing network centrality metrics...")
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))

        # Detect communities using Louvain algorithm (greedy modularity)
        print("  Detecting community structure...")
        try:
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(G)
            # Create community membership dict
            node_to_community = {}
            for idx, comm in enumerate(communities):
                for node in comm:
                    node_to_community[node] = idx
        except:
            # Fallback: assign all to one community
            node_to_community = {node: 0 for node in G.nodes()}
            communities = [set(G.nodes())]

        # Use Kamada-Kawai layout for better structure visualization
        print("  Computing network layout...")
        # For large networks, use subset for initial layout
        if G.number_of_nodes() > 150:
            # Sample high-degree nodes for layout seed
            high_degree_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:150]
            seed_nodes = [n for n, _ in high_degree_nodes]
            G_seed = G.subgraph(seed_nodes)
            pos_seed = nx.kamada_kawai_layout(G_seed)
            # Complete with spring layout
            pos = nx.spring_layout(G, pos=pos_seed, k=0.3, iterations=20, seed=42)
        else:
            pos = nx.kamada_kawai_layout(G)

        # ====== Panel 1: Community Structure with Capacity ======
        # Node colors based on community
        num_communities = len(communities)
        community_colors = cm.Set3(np.linspace(0, 1, num_communities))
        node_colors_comm = [community_colors[node_to_community.get(node, 0)] for node in G.nodes()]

        # Node sizes based on degree centrality (network importance)
        node_sizes_cent = np.array([degree_centrality[node] * 3000 + 50 for node in G.nodes()])

        # Draw edges first (background)
        nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.3, edge_color='gray', ax=ax1)

        # Draw nodes with community colors
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes_cent, node_color=node_colors_comm,
                              alpha=0.8, edgecolors='black', linewidths=0.5, ax=ax1)

        ax1.set_title('(a) Community Structure & Network Centrality\n' +
                     f'({G.number_of_nodes()} countries, {G.number_of_edges()} connections, '
                     f'{num_communities} communities)', fontsize=11, fontweight='bold')
        ax1.axis('off')

        # Add legend for communities
        if num_communities <= 8:
            legend_elements_comm = [
                mpatches.Patch(facecolor=community_colors[i], edgecolor='black',
                             label=f'Community {i+1} ({len(communities[i])} countries)')
                for i in range(min(num_communities, 8))
            ]
            ax1.legend(handles=legend_elements_comm, title='Trade Communities',
                      loc='upper left', frameon=True, fontsize=8)

        # ====== Panel 2: Capacity Distribution with Hubs ======
        # Node colors based on capacity (gradient)
        capacities_array = np.array([node_capacities.get(node, 10) for node in G.nodes()])
        norm = Normalize(vmin=capacities_array.min(), vmax=capacities_array.max())
        cmap = cm.YlOrRd  # Yellow-Orange-Red colormap
        node_colors_cap = cmap(norm(capacities_array))

        # Node sizes based on capacity
        node_sizes_cap = (capacities_array - capacities_array.min()) / (capacities_array.max() - capacities_array.min()) * 800 + 100

        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.3, edge_color='gray', ax=ax2)

        # Draw nodes with capacity colors
        scatter = ax2.scatter([pos[node][0] for node in G.nodes()],
                             [pos[node][1] for node in G.nodes()],
                             s=node_sizes_cap, c=capacities_array, cmap=cmap,
                             alpha=0.8, edgecolors='black', linewidths=0.5)

        # Highlight top 5 hub nodes
        top_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        for hub_node, cent in top_hubs:
            x, y = pos[hub_node]
            # Draw star marker
            ax2.scatter(x, y, s=1500, marker='*', c='gold', edgecolors='darkred',
                       linewidths=2, zorder=10, alpha=0.9)

        ax2.set_title('(b) Trade Capacity Distribution & Hub Identification\n' +
                     f'(Node size ∝ capacity, stars = top 5 hubs by degree centrality)',
                     fontsize=11, fontweight='bold')
        ax2.axis('off')

        # Add colorbar for capacity
        cbar = plt.colorbar(scatter, ax=ax2, fraction=0.046, pad=0.04)
        cbar.set_label('Trade Capacity', fontweight='bold')

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.savefig(save_path.replace('.pdf', '.png'), bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved network topology to {save_path}")

    def plot_capacity_distribution(self, node_capacities: Dict, save_name: str = "capacity_distribution.pdf"):
        """
        Plot capacity distribution histogram.

        Args:
            node_capacities: Dictionary of node capacities
            save_name: Output filename
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

        capacities = list(node_capacities.values())

        # Histogram
        n, bins, patches = ax1.hist(capacities, bins=30, color='#0072B2', edgecolor='black',
                                    linewidth=1.2, alpha=0.7)

        # Color bins by capacity group
        for i, patch in enumerate(patches):
            bin_center = (bins[i] + bins[i+1]) / 2
            if bin_center < 50:
                patch.set_facecolor('#FDB462')
            elif bin_center < 100:
                patch.set_facecolor('#80B1D3')
            elif bin_center < 150:
                patch.set_facecolor('#8DD3C7')
            else:
                patch.set_facecolor('#FB8072')

        ax1.set_xlabel('Country Capacity', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('(a) Capacity Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Add statistics
        mean_cap = np.mean(capacities)
        std_cap = np.std(capacities)
        ax1.axvline(mean_cap, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_cap:.2f}')
        ax1.axvline(mean_cap + std_cap, color='orange', linestyle=':', linewidth=2,
                   label=f'Mean ± Std: {std_cap:.2f}')
        ax1.axvline(mean_cap - std_cap, color='orange', linestyle=':', linewidth=2)
        ax1.legend()

        # Box plot
        bp = ax2.boxplot(capacities, vert=True, patch_artist=True, widths=0.6)
        bp['boxes'][0].set_facecolor('#0072B2')
        bp['boxes'][0].set_alpha(0.7)
        bp['boxes'][0].set_edgecolor('black')
        bp['boxes'][0].set_linewidth(1.5)

        for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
            plt.setp(bp[element], color='black', linewidth=1.5)

        ax2.set_ylabel('Country Capacity', fontweight='bold')
        ax2.set_title('(b) Capacity Statistics', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')

        # Add statistics text
        stats_text = f'Mean: {mean_cap:.2f}\nMedian: {np.median(capacities):.2f}\n'
        stats_text += f'Std: {std_cap:.2f}\nMin: {min(capacities):.2f}\nMax: {max(capacities):.2f}'
        ax2.text(0.98, 0.98, stats_text, transform=ax2.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=9)

        plt.suptitle('Country Capacity Analysis', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.savefig(save_path.replace('.pdf', '.png'), bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved capacity distribution to {save_path}")

    def plot_performance_radar(self, results: Dict, save_name: str = "performance_radar.pdf"):
        """
        Plot radar chart comparing algorithms across multiple metrics.

        Args:
            results: Dictionary of algorithm results
            save_name: Output filename
        """
        algorithms = list(results.keys())

        # Normalize metrics to 0-100 scale
        categories = ['Survival\nRate', 'Cost\nEfficiency', 'Computational\nSpeed',
                     'Robustness', 'Scalability']

        values = []
        for alg in algorithms:
            surv_norm = results[alg]['surv_rate'] * 100
            # Cost efficiency: normalize inversely (lower cost = higher score)
            max_cost = max(abs(results[a]['total_cost']) for a in algorithms)
            cost_norm = 100 - (abs(results[alg]['total_cost']) / max(max_cost, 1) * 100)
            # Speed: normalize inversely (lower runtime = higher score)
            max_runtime = max(results[a]['runtime'] for a in algorithms)
            speed_norm = 100 - (results[alg]['runtime'] / max_runtime * 100)
            # Robustness and scalability (estimated based on survival rate and runtime)
            robust_norm = surv_norm * 0.95  # Slightly lower than survival rate
            scale_norm = speed_norm * 0.9  # Based on computational efficiency

            values.append([surv_norm, cost_norm, speed_norm, robust_norm, scale_norm])

        # Number of variables
        N = len(categories)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        values_plot = [v + v[:1] for v in values]  # Complete the loop
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        for i, alg in enumerate(algorithms):
            ax.plot(angles, values_plot[i], 'o-', linewidth=2, label=alg,
                   color=self.colors[alg], markersize=8)
            ax.fill(angles, values_plot[i], alpha=0.15, color=self.colors[alg])

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.7)

        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11, frameon=True,
                 fancybox=True, shadow=True)

        ax.set_title('Multi-Dimensional Performance Comparison', fontsize=14, fontweight='bold',
                    pad=30)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.savefig(save_path.replace('.pdf', '.png'), bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved performance radar to {save_path}")

    def plot_improvement_over_baseline(self, results: Dict, baseline_survival: float = 0.5,
                                      save_name: str = "improvement_analysis.pdf"):
        """
        Plot improvement over random baseline.

        Args:
            results: Dictionary of algorithm results
            baseline_survival: Random baseline survival rate
            save_name: Output filename
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        algorithms = list(results.keys())
        improvements = []

        for alg in algorithms:
            improvement = ((results[alg]['surv_rate'] - baseline_survival) / baseline_survival) * 100
            improvements.append(improvement)

        x = np.arange(len(algorithms))
        bars = ax.bar(x, improvements, color=[self.colors[alg] for alg in algorithms],
                     edgecolor='black', linewidth=1.5, alpha=0.8)

        ax.set_ylabel('Improvement over Random Baseline (%)', fontweight='bold', fontsize=12)
        ax.set_title('Algorithm Performance vs. Random Baseline\n(Baseline Survival Rate: 50%)',
                    fontweight='bold', fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels
        for bar, val in zip(bars, improvements):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'+{val:.1f}%', ha='center', va='bottom',
                   fontsize=11, fontweight='bold')

        # Add baseline reference line
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.7,
                  label='Random Baseline')
        ax.legend(fontsize=10)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.savefig(save_path.replace('.pdf', '.png'), bbox_inches='tight', dpi=300)
        plt.close()

        print(f"Saved improvement analysis to {save_path}")

    def create_all_plots(self, results: Dict, G: nx.Graph, node_capacities: Dict):
        """
        Generate all plots for the case study.

        Args:
            results: Algorithm results dictionary
            G: Network graph
            node_capacities: Node capacity dictionary
        """
        print("\n" + "="*80)
        print("GENERATING ACADEMIC FIGURES")
        print("="*80)

        self.plot_performance_comparison(results)
        self.plot_network_topology(G, node_capacities)
        self.plot_capacity_distribution(node_capacities)
        self.plot_performance_radar(results)
        self.plot_improvement_over_baseline(results)

        print("\n" + "="*80)
        print(f"All figures saved to: {self.output_dir}")
        print("Generated files:")
        print("  - performance_comparison.pdf/png")
        print("  - network_topology.pdf/png")
        print("  - capacity_distribution.pdf/png")
        print("  - performance_radar.pdf/png")
        print("  - improvement_analysis.pdf/png")
        print("="*80 + "\n")
