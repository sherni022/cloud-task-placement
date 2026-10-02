import time
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from algorithms import (
    prim_mst,
    dijkstra,
    reconstruct_path,
    all_pairs_shortest_paths,
    dp_place_vms,
)
from data_generator import generate_cloud_data


st.set_page_config(
    page_title="Cloud Task Placement Optimizer",
    page_icon="☁️",
    layout="wide",
)

st.title("☁️ Cloud Task Placement Optimizer")
st.caption(
    "DAA Project — MST for backbone • Dijkstra for routing • Dynamic Programming for placement"
)

with st.sidebar:
    st.header("Experiment Controls")
    num_servers = st.slider("Number of servers", 4, 12, 8)
    num_vms = st.slider("Number of VMs", 3, 10, 8)
    seed = st.number_input("Random seed", min_value=1, value=42, step=1)
    run = st.button("Run Optimization", type="primary")

if "result" not in st.session_state:
    run = True

if run:
    graph, edges, capacities, vms = generate_cloud_data(
        num_servers=num_servers, num_vms=num_vms, seed=int(seed)
    )

    start = time.perf_counter()
    mst_edges, mst_cost = prim_mst(graph)
    mst_time = time.perf_counter() - start

    start = time.perf_counter()
    distances, predecessors = all_pairs_shortest_paths(graph)
    shortest_time = time.perf_counter() - start

    start = time.perf_counter()
    placements, total_latency, dp_info = dp_place_vms(
        vms, capacities, distances
    )
    dp_time = time.perf_counter() - start

    st.session_state.result = {
        "graph": graph,
        "edges": edges,
        "capacities": capacities,
        "vms": vms,
        "mst_edges": mst_edges,
        "mst_cost": mst_cost,
        "distances": distances,
        "predecessors": predecessors,
        "placements": placements,
        "total_latency": total_latency,
        "mst_time": mst_time,
        "shortest_time": shortest_time,
        "dp_time": dp_time,
        "dp_states": dp_info.currsize,
    }

r = st.session_state.result
capacities = r["capacities"]
vms = r["vms"]
placements = r["placements"]

if placements is None:
    st.error(
        "No feasible placement was found for this generated workload. "
        "Increase the number of servers or reduce the VM workload."
    )
    st.stop()

avg_latency = r["total_latency"] / len(placements)

used = {s: 0 for s in capacities}
for p in placements:
    vm = next(x for x in vms if x["id"] == p["vm_id"])
    used[p["server"]] += vm["demand"]

total_capacity = sum(capacities.values())
total_used = sum(used.values())
utilization = 100 * total_used / total_capacity

c1, c2, c3, c4 = st.columns(4)
c1.metric("VMs Placed", len(placements))
c2.metric("Average Latency", f"{avg_latency:.2f} ms")
c3.metric("Capacity Utilization", f"{utilization:.1f}%")
c4.metric("MST Cost", f"{r['mst_cost']:.0f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("1. Cloud Network Model")
    edge_df = pd.DataFrame(r["edges"], columns=["Server A", "Server B", "Latency (ms)"])
    st.dataframe(edge_df, use_container_width=True, hide_index=True)

with right:
    st.subheader("2. Server Capacities")
    capacity_df = pd.DataFrame(
        [{"Server": s, "Capacity": capacities[s], "Used": used[s],
          "Available": capacities[s] - used[s]}
         for s in capacities]
    )
    st.dataframe(capacity_df, use_container_width=True, hide_index=True)

st.subheader("3. MST Backbone")
mst_df = pd.DataFrame(r["mst_edges"], columns=["Server A", "Server B", "Latency (ms)"])
st.dataframe(mst_df, use_container_width=True, hide_index=True)

st.subheader("4. DP-Based VM Placement")
placement_df = pd.DataFrame(placements)
placement_df.columns = ["VM", "Assigned Server", "Routing Latency (ms)"]
st.dataframe(placement_df, use_container_width=True, hide_index=True)

st.subheader("5. Network Visualization")

fig, ax = plt.subplots(figsize=(10, 6))

# Simple circular layout without requiring NetworkX.
servers = list(capacities.keys())
n = len(servers)
positions = {}
import math
for i, s in enumerate(servers):
    angle = 2 * math.pi * i / n
    positions[s] = (math.cos(angle), math.sin(angle))

mst_pairs = {frozenset((u, v)) for u, v, _ in r["mst_edges"]}

for u, v, w in r["edges"]:
    x1, y1 = positions[u]
    x2, y2 = positions[v]
    is_mst = frozenset((u, v)) in mst_pairs
    ax.plot(
        [x1, x2], [y1, y2],
        linewidth=3 if is_mst else 1,
        alpha=0.9 if is_mst else 0.35,
    )
    ax.text((x1+x2)/2, (y1+y2)/2, f"{w}ms", fontsize=8)

for s, (x, y) in positions.items():
    ax.scatter([x], [y], s=650)
    ax.text(x, y, s, ha="center", va="center", fontsize=10)

ax.set_title("Cloud Network — Bold edges are MST backbone")
ax.axis("off")
st.pyplot(fig, use_container_width=True)
plt.close(fig)

st.subheader("6. Performance")
performance = pd.DataFrame({
    "Component": ["MST", "Shortest Paths", "DP Placement"],
    "Execution Time (ms)": [
        r["mst_time"] * 1000,
        r["shortest_time"] * 1000,
        r["dp_time"] * 1000,
    ],
})
st.bar_chart(performance.set_index("Component"))

st.info(
    "Interpretation: the system minimizes the total routing latency of the VM "
    "placements while never exceeding a server's available capacity."
)
