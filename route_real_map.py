
import osmnx as ox
from main import BinaryHeap, FibonacciHeap, dijkstra

file_path = "data/vellore_roads.graphml"

if not __import__("os").path.exists(file_path):
    raise FileNotFoundError(
        "Road map not found. Run python download_roads.py first."
    )

print("Loading the saved Vellore road network...")
G = ox.io.load_graphml(file_path)

print("Road network loaded successfully.")
print("Intersections:", len(G.nodes))
print("Directed road edges:", len(G.edges))


road_graph = {node: [] for node in G.nodes}

for u, v, data in G.edges(data=True):
    length = float(data.get("length", 1.0))
    road_graph[u].append((v, length))



print("\nEnter coordinates inside the downloaded map.")
print("Latitude example: 12.9165")
print("Longitude example: 79.1325")

try:
    source_lat = float(input("Source latitude: "))
    source_lon = float(input("Source longitude: "))

    dest_lat = float(input("Destination latitude: "))
    dest_lon = float(input("Destination longitude: "))
except ValueError:
    raise SystemExit("Please enter valid numeric coordinates.")


source = ox.distance.nearest_nodes(
    G, X=source_lon, Y=source_lat
)

destination = ox.distance.nearest_nodes(
    G, X=dest_lon, Y=dest_lat
)

print("\nNearest source road node:", source)
print("Nearest destination road node:", destination)



results = {}

for heap_type in (BinaryHeap, FibonacciHeap):
    print(f"\nRunning {heap_type.__name__}...")

    import time
    start = time.perf_counter()

    path, distance, operations = dijkstra(
        road_graph, source, destination, heap_type
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    results[heap_type.__name__] = {
        "path": path,
        "distance": distance,
        "operations": operations,
        "time_ms": elapsed_ms
    }

    print("Distance in metres:", distance)
    print("Execution time (ms):", round(elapsed_ms, 4))
    print("Heap operation counter:", operations)

    if path:
        print("Number of route nodes:", len(path))
    else:
        print("No route found.")


binary_result = results["BinaryHeap"]
fib_result = results["FibonacciHeap"]

if binary_result["distance"] != fib_result["distance"]:
    raise RuntimeError(
        "Error: the two heaps returned different distances."
    )

print("\nBoth implementations returned the same distance.")


route = binary_result["path"]

if route:
    print("Displaying the shortest route...")

    fig, ax = ox.plot_graph_route(
        G,
        route,
        route_linewidth=3,
        node_size=0,
        bgcolor="white",
        show=False,
        close=False
    )

    import matplotlib.pyplot as plt
    plt.show()
else:
    print("Cannot display a route because no path was found.")
