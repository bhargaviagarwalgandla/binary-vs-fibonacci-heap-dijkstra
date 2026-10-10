
import os
import time
import math

import folium
import osmnx as ox
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

from main import BinaryHeap, FibonacciHeap, dijkstra

st.set_page_config(
    page_title="RouteLab | DSA Routing Simulator",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        background: #0b1120;
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: #f1f5f9;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    [data-testid="stMetric"] {
        background: #172338;
        padding: 15px;
        border: 1px solid #293a54;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #a9bad0;
    }

    .hero {
        background: linear-gradient(120deg, #152c4a, #172338);
        padding: 20px 24px;
        border-radius: 14px;
        border: 1px solid #30435f;
        margin-bottom: 20px;
    }

    .subtitle {
        color: #a9bad0;
        font-size: 0.95rem;
    }

    div.stButton > button {
        border-radius: 9px;
        min-height: 44px;
        font-weight: 600;
    }

    hr {
        border-color: #293a54;
    }
</style>
""", unsafe_allow_html=True)

MAP_FILE = os.path.join("data", "vellore_roads.graphml")


@st.cache_resource
def load_network():
    if not os.path.exists(MAP_FILE):
        raise FileNotFoundError(
            "Road network file is missing: " + MAP_FILE
        )

    return ox.io.load_graphml(MAP_FILE)


@st.cache_resource
def create_adjacency_list():
    network = load_network()
    adjacency = {node: [] for node in network.nodes}

    for u, v, data in network.edges(data=True):
        length = float(data.get("length", 1.0))
        adjacency[u].append((v, length))

    return adjacency


try:
    G = load_network()
    road_graph = create_adjacency_list()

except Exception as exc:
    st.error(f"Could not load the road network: {exc}")
    st.info(
        "Check that data/vellore_roads.graphml exists. "
        "If it does not, run python download_roads.py."
    )
    st.stop()


st.markdown("""
<div class="hero">
    <h1>🧭 RouteLab</h1>
    <div class="subtitle">
        Real-World Network Routing Simulator
        &nbsp; | &nbsp; Dijkstra's Algorithm
        &nbsp; | &nbsp; Binary Heap vs Fibonacci Heap
    </div>
</div>
""", unsafe_allow_html=True)


network_nodes = len(G.nodes)
network_edges = len(G.edges)

col1, col2, col3 = st.columns(3)

col1.metric("Road intersections", f"{network_nodes:,}")
col2.metric("Directed road edges", f"{network_edges:,}")
col3.metric("Priority queues", "2")



st.markdown("## 📍 Plan your route")

left, right = st.columns([1, 2.2], gap="large")

with left:
    with st.form("route_form"):
        origin = st.text_input(
            "Starting location",
            value="Vellore New Bus Stand, Vellore, Tamil Nadu, India",
            placeholder="Enter a place, landmark, or address",
        )

        destination = st.text_input(
            "Destination",
            value="Vellore Fort, Vellore, Tamil Nadu, India",
            placeholder="Enter your destination",
        )

        algorithm = st.selectbox(
            "Priority queue",
            [
                "Compare both heaps",
                "Binary Heap",
                "Fibonacci Heap",
            ],
        )

        submitted = st.form_submit_button(
            "🔎 Find Shortest Route",
            type="primary",
            use_container_width=True,
        )

    st.caption(
        "Enter place names. Geocoding requires internet access, "
        "and both places must be within the downloaded road network."
    )



@st.cache_data(ttl=3600, show_spinner=False)
def geocode_place(place):
    return ox.geocode(place)


def nearest_road_node(place):
    lat, lon = geocode_place(place)

    node = ox.distance.nearest_nodes(
        G,
        X=lon,
        Y=lat,
    )

    node_data = G.nodes[node]

    snap_distance = ox.distance.great_circle(
        lat,
        lon,
        float(node_data["y"]),
        float(node_data["x"]),
    )

    if snap_distance > 2000:
        raise ValueError(
            f"{place} is about {snap_distance:.0f} metres "
            "from the nearest road node in your downloaded map. "
            "Download a larger or better-centred road network."
        )

    return node, (lat, lon), snap_distance



if submitted:
    if not origin.strip() or not destination.strip():
        st.error("Enter both the starting location and destination.")
        st.stop()

    try:
        with st.spinner(
            "Finding locations and calculating shortest paths..."
        ):
            source, origin_coords, source_snap = (
                nearest_road_node(origin.strip())
            )

            target, destination_coords, target_snap = (
                nearest_road_node(destination.strip())
            )

            if source == target:
                st.error(
                    "Both places resolved to the same road node. "
                    "Please choose two different locations."
                )
                st.stop()

            available_heaps = {
                "Binary Heap": BinaryHeap,
                "Fibonacci Heap": FibonacciHeap,
            }

            if algorithm == "Compare both heaps":
                selected_heaps = list(available_heaps.items())
            else:
                selected_heaps = [
                    (algorithm, available_heaps[algorithm])
                ]

            results = {}

            for name, heap_type in selected_heaps:
                start = time.perf_counter()

                path, distance, operations = dijkstra(
                    road_graph,
                    source,
                    target,
                    heap_type,
                )

                elapsed_ms = (
                    time.perf_counter() - start
                ) * 1000

                results[name] = {
                    "path": path,
                    "distance": distance,
                    "operations": operations,
                    "time_ms": elapsed_ms,
                }

        if len(results) == 2:
            d1 = results["Binary Heap"]["distance"]
            d2 = results["Fibonacci Heap"]["distance"]

            if not (
                (math.isinf(d1) and math.isinf(d2))
                or math.isclose(d1, d2, rel_tol=1e-9, abs_tol=1e-6)
            ):
                st.error(
                    "The two heaps returned different distances. "
                    "Check the heap implementations before benchmarking."
                )
                st.stop()

        st.session_state["route_results"] = {
            "origin": origin.strip(),
            "destination": destination.strip(),
            "algorithm": algorithm,
            "results": results,
            "source": source,
            "target": target,
            "origin_coords": origin_coords,
            "destination_coords": destination_coords,
            "source_snap": source_snap,
            "target_snap": target_snap,
        }

    except Exception as exc:
        st.error(f"Unable to calculate the route: {exc}")
        st.info(
            "Check your spelling, internet connection, and road "
            "network coverage. The downloaded graph may not include "
            "the locations you entered."
        )



if "route_results" not in st.session_state:
    st.info(
        "Enter two locations and click Find Shortest Route. "
        "The calculated route and performance results will appear here."
    )
    bounds = ox.utils_geo.bbox_from_point(
        (
            sum(float(d["y"]) for _, d in G.nodes(data=True))
            / max(network_nodes, 1),
            sum(float(d["x"]) for _, d in G.nodes(data=True))
            / max(network_nodes, 1),
        ),
        dist=1000,
    )

    initial_map = folium.Map(
        location=[
            sum(float(d["y"]) for _, d in G.nodes(data=True))
            / max(network_nodes, 1),
            sum(float(d["x"]) for _, d in G.nodes(data=True))
            / max(network_nodes, 1),
        ],
        zoom_start=13,
        tiles="OpenStreetMap",
    )

    st_folium(
        initial_map,
        height=420,
        use_container_width=True,
        key="initial_map",
    )

    st.stop()


saved = st.session_state["route_results"]
results = saved["results"]

st.markdown("---")
st.markdown("## 📊 Route results")

binary = results.get("Binary Heap")
fib = results.get("Fibonacci Heap")

chosen_name = (
    "Binary Heap"
    if binary is not None
    else "Fibonacci Heap"
)

chosen = results[chosen_name]
path = chosen["path"]
distance = chosen["distance"]


if path is None or math.isinf(distance):
    st.warning(
        "No route exists between these locations in the downloaded "
        "road network. Try a different destination or download a "
        "larger connected road network."
    )
    st.stop()

m1, m2, m3 = st.columns(3)

m1.metric(
    "Shortest road distance",
    f"{distance / 1000:.2f} km",
)

m2.metric(
    "Road nodes in route",
    f"{len(path):,}",
)

m3.metric(
    "Route selected",
    chosen_name,
)

st.caption(
    f"Origin snap distance: {saved['source_snap']:.0f} m"
    f"  |  Destination snap distance: "
    f"{saved['target_snap']:.0f} m"
)


route_coords = [
    (
        float(G.nodes[node]["y"]),
        float(G.nodes[node]["x"]),
    )
    for node in path
]

route_map = folium.Map(
    location=route_coords[len(route_coords) // 2],
    zoom_start=14,
    tiles="OpenStreetMap",
    control_scale=True,
)

folium.PolyLine(
    route_coords,
    color="#16a34a",
    weight=6,
    opacity=0.9,
    tooltip="Shortest road route",
).add_to(route_map)

folium.Marker(
    route_coords[0],
    tooltip="START",
    popup=saved["origin"],
    icon=folium.Icon(color="green", icon="play"),
).add_to(route_map)

folium.Marker(
    route_coords[-1],
    tooltip="DESTINATION",
    popup=saved["destination"],
    icon=folium.Icon(color="red", icon="flag"),
).add_to(route_map)

min_lat = min(p[0] for p in route_coords)
max_lat = max(p[0] for p in route_coords)
min_lon = min(p[1] for p in route_coords)
max_lon = max(p[1] for p in route_coords)

if len(route_coords) == 1:
    route_map.location = route_coords[0]
    route_map.zoom_start = 16
else:
    route_map.fit_bounds(
        [[min_lat, min_lon], [max_lat, max_lon]],
        padding_top_left=(35, 35),
        padding_bottom_right=(35, 35),
        max_zoom=16,
    )

st.markdown("### 🗺️ Shortest route map")

st_folium(
    route_map,
    height=520,
    use_container_width=True,
    key="route_map",
)



st.markdown("## ⚡ Heap performance comparison")

if len(results) == 2:
    c1, c2 = st.columns(2)

    for col, name in zip(
        [c1, c2],
        ["Binary Heap", "Fibonacci Heap"],
    ):
        result = results[name]

        with col:
            st.markdown(f"### {name}")

            st.metric(
                "Execution time",
                f"{result['time_ms']:.4f} ms",
            )

            st.metric(
                "Heap operation counter",
                f"{result['operations']:,}",
            )

            st.metric(
                "Route distance",
                f"{result['distance'] / 1000:.2f} km",
            )

    st.markdown("### Runtime chart")

    labels = list(results.keys())
    times = [
        results[name]["time_ms"]
        for name in labels
    ]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.bar(labels, times)

    ax.set_ylabel("Execution time (milliseconds)")
    ax.set_title("Dijkstra Runtime by Priority Queue")
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.4f}",
            ha="center",
            va="bottom",
        )

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "This chart shows a single route calculation. "
        "Use repeated runs and multiple graph sizes for a reliable "
        "performance conclusion."
    )

else:
    name = next(iter(results))
    result = results[name]

    st.metric("Execution time", f"{result['time_ms']:.4f} ms")
    st.metric(
        "Heap operation counter",
        f"{result['operations']:,}",
    )

    st.info(
        "Select Compare both heaps to view the side-by-side "
        "performance chart."
    )


with st.expander("View route and graph details"):
    st.write("Origin:", saved["origin"])
    st.write("Destination:", saved["destination"])
    st.write("Source road node:", saved["source"])
    st.write("Destination road node:", saved["target"])
    st.write("Number of route nodes:", len(path))
    st.write("Total distance in metres:", round(distance, 2))

    if st.checkbox("Show route node IDs"):
        st.write(path)



st.markdown("---")

st.caption(
    "RouteLab | DSA Project | Dijkstra's Algorithm | "
    "OpenStreetMap data | Binary Heap vs Fibonacci Heap"
)
