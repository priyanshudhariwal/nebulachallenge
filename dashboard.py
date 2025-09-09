import networkx as nx
import matplotlib.pyplot as plt
import random
import csv

# --- Performance Constants (remain the same across sizes) ---
LATENCY_PER_HOP_STANDARD = 5
LATENCY_PER_HOP_OPTIMIZED = 3

# --- Topology Creation Functions ---
def create_mesh_topology(rows, cols):
    """Creates a standard 2D mesh topology."""
    return nx.grid_2d_graph(rows, cols)

def add_small_world_links(graph, num_shortcuts):
    """Adds long-range shortcut links to an existing mesh graph."""
    new_graph = graph.copy()
    nodes = list(new_graph.nodes())
    added_edges = 0
    print(f"Adding {num_shortcuts} small-world shortcuts...")
    while added_edges < num_shortcuts:
        # Ensure we don't run into an infinite loop if the graph is dense
        if len(list(nx.non_edges(new_graph))) == 0:
            break
        u, v = random.sample(nodes, 2)
        # Ensure link is long-range and doesn't already exist
        if not new_graph.has_edge(u, v) and abs(u[0] - v[0]) + abs(u[1] - v[1]) > 1:
            new_graph.add_edge(u, v)
            added_edges += 1
    return new_graph

# --- Simulation Core Classes and Functions ---
class Packet:
    def __init__(self, packet_id, source, destination, start_time):
        self.id = packet_id
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.end_time = 0
        self.hop_count = 0

def generate_workload(num_packets, nodes):
    """Generates a synthetic workload."""
    workload = []
    for i in range(num_packets):
        source, destination = random.sample(nodes, 2)
        packet = Packet(packet_id=i, source=source, destination=destination, start_time=i*2)
        workload.append(packet)
    return workload

def simulate_network(topology, workload, latency_per_hop, topology_name):
    """Runs a simplified simulation to calculate latency and throughput."""
    results = []
    simulation_end_time = 0
    packets_delivered = 0
    for packet in workload:
        try:
            path = nx.shortest_path(topology, source=packet.source, target=packet.destination)
            hop_count = len(path) - 1
            packet_travel_time = hop_count * latency_per_hop
            end_time = packet.start_time + packet_travel_time
            simulation_end_time = max(simulation_end_time, end_time)
            packets_delivered += 1
            results.append({
                "packet_id": packet.id,
                "latency": packet_travel_time,
                "hop_count": hop_count,
            })
        except nx.NetworkXNoPath:
            pass # Ignore if no path exists

    average_latency = sum(r['latency'] for r in results) / len(results) if results else 0
    throughput = packets_delivered / simulation_end_time if simulation_end_time > 0 else 0
    return {"topology_name": topology_name, "average_latency": average_latency, "throughput_pps": throughput * 1e9}, results

# --- Visualization and Data Saving Functions ---
def plot_topology_layout(topology, title, filename_prefix):
    """Visualizes the network topology layout and saves it to a file."""
    plt.figure(figsize=(10, 10))
    pos = {node: (node[1], -node[0]) for node in topology.nodes()} # Grid layout
    nx.draw(topology, pos, with_labels=False, node_color='#a0cbe2', node_size=100)
    plt.title(title, fontsize=16)
    
    output_filename = f"{filename_prefix}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: Graph saved locally to file: {output_filename}")
    plt.close() # Close figure to free memory

def plot_comparison_graphs(summaries, filename_prefix):
    """Plots bar charts comparing performance and saves them to a file."""
    labels = [s['topology_name'] for s in summaries]
    latencies = [s['average_latency'] for s in summaries]
    throughputs = [s['throughput_pps'] for s in summaries]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

    ax1.bar(labels, latencies, color=['#003f5c', '#7a5195', '#ef5675'])
    ax1.set_ylabel('Average Packet Latency (cycles)')
    ax1.set_title('Performance Comparison: Latency')
    for i, v in enumerate(latencies):
        ax1.text(i, v, f"{v:.2f}", ha='center', va='bottom')

    ax2.bar(labels, throughputs, color=['#003f5c', '#7a5195', '#ef5675'])
    ax2.set_ylabel('Throughput (Packets per Billion Cycles)')
    ax2.set_title('Performance Comparison: Throughput')
    for i, v in enumerate(throughputs):
        ax2.text(i, v, f"{v:.2e}", ha='center', va='bottom')

    fig.suptitle(f'NoC Architecture Benchmarking Results ({filename_prefix.split("_")[-1]})', fontsize=18)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_filename = f"{filename_prefix}.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: Comparison graph saved locally to file: {output_filename}")
    plt.close() # Close figure to free memory

# --- Simulation Runner for a Specific Size ---
def run_simulation_for_size(rows, cols):
    """Encapsulates the full simulation and plotting for a given grid size."""
    grid_size_str = f"{rows}x{cols}"
    num_nodes = rows * cols
    
    # Scale parameters based on grid size for meaningful results
    num_packets_to_simulate = 250 * num_nodes
    num_small_world_shortcuts = num_nodes // 4 # Add shortcuts proportional to size

    # 1. Setup topologies
    mesh_topology = create_mesh_topology(rows, cols)
    small_world_topology = add_small_world_links(mesh_topology, num_small_world_shortcuts)

    # 2. Generate workload
    workload = generate_workload(num_packets_to_simulate, list(mesh_topology.nodes()))

    # 3. Run simulations for all architectures
    all_summaries = []
    summary1, _ = simulate_network(mesh_topology, workload, LATENCY_PER_HOP_STANDARD, "Regular Mesh")
    all_summaries.append(summary1)
    summary2, _ = simulate_network(small_world_topology, workload, LATENCY_PER_HOP_STANDARD, "Small-World Mesh")
    all_summaries.append(summary2)
    summary3, _ = simulate_network(small_world_topology, workload, LATENCY_PER_HOP_OPTIMIZED, "Small-World + Optimized Router")
    all_summaries.append(summary3)

    # 4. Generate visualizations and save files
    plot_topology_layout(mesh_topology, f"Standard {grid_size_str} Mesh Topology", f"topology_mesh_layout_{grid_size_str}")
    plot_topology_layout(small_world_topology, f"Small-World {grid_size_str} Mesh ({num_small_world_shortcuts} shortcuts)", f"topology_small_world_layout_{grid_size_str}")
    plot_comparison_graphs(all_summaries, f"simulation_comparison_results_{grid_size_str}")

# --- Main Execution Flow ---
def main():
    """Main function to run simulations for all specified grid sizes."""
    grid_sizes_to_test = [(4, 4), (6, 6), (8, 8)]
    
    for rows, cols in grid_sizes_to_test:
        print(f"\n{'='*25} RUNNING SIMULATION FOR {rows}x{cols} GRID {'='*25}\n")
        run_simulation_for_size(rows, cols)
        print(f"\n{'='*25} COMPLETED SIMULATION FOR {rows}x{cols} GRID {'='*25}\n")

# Run all simulations
if __name__ == "__main__":
    main()
