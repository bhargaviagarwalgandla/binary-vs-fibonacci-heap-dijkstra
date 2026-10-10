
import random
import time
import statistics

from main import BinaryHeap, FibonacciHeap, dijkstra
def make_random_graph(n, extra_edges, seed=42):
    rng = random.Random(seed)
    graph = {i: [] for i in range(n)}

    for i in range(n - 1):
        w = rng.randint(1, 20)
        graph[i].append((i + 1, w))
        graph[i + 1].append((i, w))

    possible = [
        (u, v)
        for u in range(n)
        for v in range(u + 2, n)
        if not any(x == v for x, _ in graph[u])
    ]
    rng.shuffle(possible)

    for u, v in possible[:extra_edges]:
        w = rng.randint(1, 20)
        graph[u].append((v, w))
        graph[v].append((u, w))

    return graph

def benchmark(n, extra_edges, repetitions=5):
    g = make_random_graph(n, extra_edges)
    results = {}
    for heap_type in (BinaryHeap, FibonacciHeap):
        times = []
        last_distance = None
        last_operations = None
        for _ in range(repetitions):
            start = time.perf_counter()
            _, distance, operations = dijkstra(
                g, 0, n - 1, heap_type
            )
            times.append(time.perf_counter() - start)
            last_distance = distance
            last_operations = operations

        results[heap_type.__name__] = (
            statistics.mean(times) * 1000,
            last_distance,
            last_operations,
        )
    binary = results["BinaryHeap"]
    fib = results["FibonacciHeap"]
    assert binary[1] == fib[1], "Shortest distances differ!"
    print(f"\nVertices: {n}, extra edges: {extra_edges}")
    print(f"{'Heap':<18} {'Avg ms':>12} {'Operations':>14}")
    for name, result in results.items():
        print(f"{name:<18} {result[0]:>12.4f} {result[2]:>14}")
    print("Shortest distance:", binary[1])
if __name__ == "__main__":
    benchmark(100, 200)
    benchmark(500, 1000)
    benchmark(1000, 5000)
