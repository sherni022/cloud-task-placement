import heapq
from functools import lru_cache

INF = float("inf")


def prim_mst(graph):
    """Return MST edges and total weight for a connected undirected graph."""
    if not graph:
        return [], 0.0

    start = next(iter(graph))
    visited = {start}
    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)

    mst_edges = []
    total = 0.0

    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append((u, v, w))
        total += w

        for nxt, weight in graph[v]:
            if nxt not in visited:
                heapq.heappush(heap, (weight, v, nxt))

    if len(visited) != len(graph):
        raise ValueError("Graph must be connected to construct an MST.")

    return mst_edges, total


def dijkstra(graph, source):
    """Single-source shortest paths for non-negative edge weights."""
    dist = {node: INF for node in graph}
    previous = {node: None for node in graph}
    dist[source] = 0.0
    pq = [(0.0, source)]

    while pq:
        current_dist, u = heapq.heappop(pq)
        if current_dist > dist[u]:
            continue

        for v, weight in graph[u]:
            candidate = current_dist + weight
            if candidate < dist[v]:
                dist[v] = candidate
                previous[v] = u
                heapq.heappush(pq, (candidate, v))

    return dist, previous


def reconstruct_path(previous, source, target):
    if source == target:
        return [source]
    if previous.get(target) is None:
        return []

    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        if cur == source:
            return path[::-1]
        cur = previous[cur]
    return []


def all_pairs_shortest_paths(graph):
    distances = {}
    predecessors = {}
    for source in graph:
        distances[source], predecessors[source] = dijkstra(graph, source)
    return distances, predecessors


def dp_place_vms(vms, capacities, distances):
    """
    Exact capacity-aware placement using memoized DP.

    Each VM has:
      id, source, demand

    State = (VM index, remaining capacities tuple).
    Objective = minimum total latency from VM source to host.

    This is intended for small/medium demonstration instances.
    """
    server_ids = list(capacities.keys())
    cap_tuple = tuple(capacities[s] for s in server_ids)
    n = len(vms)

    @lru_cache(maxsize=None)
    def solve(i, remaining):
        if i == n:
            return 0.0, ()

        vm = vms[i]
        best_cost = INF
        best_assignment = None

        for j, server in enumerate(server_ids):
            if remaining[j] < vm["demand"]:
                continue

            new_remaining = list(remaining)
            new_remaining[j] -= vm["demand"]

            route_cost = distances[vm["source"]][server]
            future_cost, future_assignment = solve(i + 1, tuple(new_remaining))
            total = route_cost + future_cost

            if total < best_cost:
                best_cost = total
                best_assignment = ((vm["id"], server, route_cost),) + future_assignment

        if best_assignment is None:
            return INF, ()

        return best_cost, best_assignment

    total_cost, assignment = solve(0, cap_tuple)

    if total_cost == INF:
        return None, None, solve.cache_info()

    result = []
    for vm_id, server, latency in assignment:
        result.append({
            "vm_id": vm_id,
            "server": server,
            "latency": latency
        })

    return result, total_cost, solve.cache_info()
