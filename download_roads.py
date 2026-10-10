
import os
import osmnx as ox
os.makedirs("data", exist_ok=True)
print("Downloading the Vellore road network...")
print("Please wait. This requires an internet connection.")

center = (12.9165, 79.1325)
G = ox.graph.graph_from_point(
    center,
    dist=10000,
    network_type="drive",
    simplify=True
)

print("\nDownload successful!")
print("Number of road intersections:", len(G.nodes))
print("Number of directed road edges:", len(G.edges))

file_path = "data/vellore_roads.graphml"
ox.io.save_graphml(G, file_path)

print("\nRoad network saved to:", file_path)

ox.plot_graph(
    G,
    node_size=0,
    edge_linewidth=0.7,
    bgcolor="white"
)
