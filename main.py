
import math
import time
import random
class BinaryHeap:
    def __init__(self):
        self.heap = []
        self.position = {}
        self.operations = 0

    def __len__(self):
        return len(self.heap)

    def insert(self, vertex, priority):
        if vertex in self.position:
            self.decrease_key(vertex, priority)
            return

        self.heap.append([priority, vertex])
        i = len(self.heap) - 1
        self.position[vertex] = i
        self.operations += 1

        while i > 0:
            parent = (i - 1) // 2
            if self.heap[parent][0] <= self.heap[i][0]:
                break
            self._swap(i, parent)
            i = parent

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.position[self.heap[i][1]] = i
        self.position[self.heap[j][1]] = j
        self.operations += 1

    def decrease_key(self, vertex, priority):
        i = self.position[vertex]

        if priority >= self.heap[i][0]:
            return

        self.heap[i][0] = priority
        self.operations += 1

        while i > 0:
            parent = (i - 1) // 2
            if self.heap[parent][0] <= self.heap[i][0]:
                break
            self._swap(i, parent)
            i = parent

    def extract_min(self):
        if not self.heap:
            return None

        result = self.heap[0]
        last = self.heap.pop()
        del self.position[result[1]]
        self.operations += 1

        if self.heap:
            self.heap[0] = last
            self.position[last[1]] = 0
            i = 0

            while True:
                left = 2 * i + 1
                right = 2 * i + 2
                smallest = i

                if (left < len(self.heap)
                        and self.heap[left][0]
                        < self.heap[smallest][0]):
                    smallest = left

                if (right < len(self.heap)
                        and self.heap[right][0]
                        < self.heap[smallest][0]):
                    smallest = right

                if smallest == i:
                    break

                self._swap(i, smallest)
                i = smallest

        return tuple(result)

class FibNode:
    def __init__(self, vertex, key):
        self.vertex = vertex
        self.key = key
        self.degree = 0
        self.mark = False
        self.parent = None
        self.child = None
        self.left = self
        self.right = self

class FibonacciHeap:
    def __init__(self):
        self.minimum = None
        self.nodes = {}
        self.count = 0
        self.operations = 0

    def __len__(self):
        return self.count

    def _add_root(self, node):
        node.parent = None
        node.mark = False

        if self.minimum is None:
            node.left = node.right = node
            self.minimum = node
        else:
            node.left = self.minimum
            node.right = self.minimum.right
            self.minimum.right.left = node
            self.minimum.right = node

            if node.key < self.minimum.key:
                self.minimum = node

        self.operations += 1

    def insert(self, vertex, priority):
        if vertex in self.nodes:
            self.decrease_key(vertex, priority)
            return

        node = FibNode(vertex, priority)
        self.nodes[vertex] = node
        self._add_root(node)
        self.count += 1

    def _remove_from_ring(self, node):
        node.left.right = node.right
        node.right.left = node.left
        node.left = node.right = node

    def _link(self, child, parent):
        self._remove_from_ring(child)
        child.parent = parent
        child.mark = False

        if parent.child is None:
            parent.child = child
        else:
            child.left = parent.child
            child.right = parent.child.right
            parent.child.right.left = child
            parent.child.right = child

        parent.degree += 1
        self.operations += 1

    def _consolidate(self):
        if self.minimum is None:
            return
        roots = []
        node = self.minimum
        while True:
            roots.append(node)
            node = node.right
            if node == self.minimum:
                break
        for root in roots:
            self._remove_from_ring(root)
        degree_table = {}

        for node in roots:
            if node.parent is not None:
                continue
            x = node
            degree = x.degree
            while degree in degree_table:
                y = degree_table.pop(degree)

                if y.key < x.key:
                    x, y = y, x

                self._link(y, x)
                degree = x.degree

            degree_table[degree] = x

        self.minimum = None

        for node in degree_table.values():
            node.left = node.right = node
            self._add_root(node)

    def extract_min(self):
        z = self.minimum

        if z is None:
            return None

        if z.child is not None:
            children = []
            child = z.child
            while True:
                children.append(child)
                child = child.right
                if child == z.child:
                    break

            for child in children:
                self._remove_from_ring(child)
                child.parent = None
                self._add_root(child)

            z.child = None
            z.degree = 0

        next_root = z.right
        self._remove_from_ring(z)
        self.count -= 1
        del self.nodes[z.vertex]
        self.operations += 1

        if self.count == 0:
            self.minimum = None
        else:
            self.minimum = next_root
            self._consolidate()

        return z.key, z.vertex

    def _cut(self, node, parent):
        if parent.child == node:
            parent.child = (
                node.right if node.right != node else None
            )

        self._remove_from_ring(node)
        parent.degree -= 1
        self._add_root(node)
        node.mark = False
        self.operations += 1

    def _cascading_cut(self, node):
        parent = node.parent

        if parent is None:
            return

        if not node.mark:
            node.mark = True
        else:
            self._cut(node, parent)
            self._cascading_cut(parent)

    def decrease_key(self, vertex, priority):
        node = self.nodes[vertex]

        if priority > node.key:
            raise ValueError("New priority cannot increase the key")

        node.key = priority
        parent = node.parent

        if parent is not None and node.key < parent.key:
            self._cut(node, parent)
            self._cascading_cut(parent)

        if self.minimum is None or node.key < self.minimum.key:
            self.minimum = node

        self.operations += 1

def dijkstra(graph, source, destination, heap_type):
    if source not in graph or destination not in graph:
        raise ValueError("Source and destination must be graph vertices")

    distance = {v: math.inf for v in graph}
    previous = {v: None for v in graph}
    distance[source] = 0

    queue = heap_type()
    queue.insert(source, 0)
    visited = set()

    while len(queue):
        item = queue.extract_min()
        if item is None:
            break

        current_distance, u = item

        if u in visited:
            continue

        visited.add(u)

        if u == destination:
            break

        for v, weight in graph[u]:
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative weights")

            if v not in graph:
                raise ValueError(f"Unknown neighbour: {v}")

            if v in visited:
                continue

            new_distance = current_distance + weight

            if new_distance < distance[v]:
                distance[v] = new_distance
                previous[v] = u

                if v in queue.nodes if isinstance(
                    queue, FibonacciHeap
                ) else v in queue.position:
                    queue.decrease_key(v, new_distance)
                else:
                    queue.insert(v, new_distance)

    if distance[destination] == math.inf:
        return None, math.inf, queue.operations

    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return path, distance[destination], queue.operations

graph = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 5)],
    "C": [("A", 2), ("E", 3)],
    "D": [("B", 5), ("E", 2)],
    "E": [("C", 3), ("D", 2)]
}


def run_demo():
    source = input("Enter source (A, B, C, D, E): ").strip().upper()
    destination = input(
        "Enter destination (A, B, C, D, E): "
    ).strip().upper()

    for heap_type in (BinaryHeap, FibonacciHeap):
        start = time.perf_counter()

        path, cost, operations = dijkstra(
            graph, source, destination, heap_type
        )

        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n{heap_type.__name__}")
        print("Path:", " -> ".join(path) if path else "No route")
        print("Distance:", cost)
        print(f"Execution time: {elapsed:.4f} ms")
        print("Heap operation counter:", operations)


if __name__ == "__main__":
    run_demo()
