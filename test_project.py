
import unittest

from main import (
    BinaryHeap,
    FibonacciHeap,
    dijkstra,
    graph,
)


class RoutingTests(unittest.TestCase):

    def test_binary_heap_order(self):
        h = BinaryHeap()
        h.insert("A", 10)
        h.insert("B", 3)
        h.insert("C", 7)
        h.decrease_key("A", 1)

        self.assertEqual(h.extract_min(), (1, "A"))
        self.assertEqual(h.extract_min(), (3, "B"))
        self.assertEqual(h.extract_min(), (7, "C"))

    def test_fibonacci_heap_order(self):
        h = FibonacciHeap()
        h.insert("A", 10)
        h.insert("B", 3)
        h.insert("C", 7)
        h.decrease_key("A", 1)

        self.assertEqual(h.extract_min(), (1, "A"))
        self.assertEqual(h.extract_min(), (3, "B"))
        self.assertEqual(h.extract_min(), (7, "C"))

    def test_shortest_path_both_heaps(self):
        for heap_type in (BinaryHeap, FibonacciHeap):
            path, distance, _ = dijkstra(
                graph, "A", "E", heap_type
            )
            self.assertEqual(distance, 5)
            self.assertEqual(path, ["A", "C", "E"])

    def test_unreachable_destination(self):
        disconnected = {
            "A": [("B", 2)],
            "B": [("A", 2)],
            "C": []
        }

        for heap_type in (BinaryHeap, FibonacciHeap):
            path, distance, _ = dijkstra(
                disconnected, "A", "C", heap_type
            )
            self.assertIsNone(path)
            self.assertEqual(distance, float("inf"))


if __name__ == "__main__":
    unittest.main()
