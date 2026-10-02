# Cloud Task Placement Optimizer

DAA project implementation for:

- Servers as graph nodes
- Link latencies as edge weights
- MST for network backbone
- Dijkstra for shortest-path routing
- Dynamic Programming for capacity-aware VM placement
- Experiments and visualization

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application generates a connected synthetic cloud network, computes an MST,
finds all-pairs shortest paths with Dijkstra, and solves a small exact
capacity-aware VM placement problem using memoized dynamic programming.

## Important modelling assumption

Each VM has a source server representing where its traffic originates.
Placement cost is the shortest-path latency from that source to the selected
hosting server. The DP minimizes the sum of these latencies subject to server
capacity constraints.

The DP implementation is intentionally designed for small/medium project
instances. Larger capacities or many servers can increase the state space.
This is useful for demonstrating the time/space trade-off in the DAA report.
