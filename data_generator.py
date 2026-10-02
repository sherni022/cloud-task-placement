import random


def generate_cloud_data(num_servers=8, num_vms=8, seed=42):
    """
    Generate a connected synthetic cloud network and VM workload.
    Returns graph adjacency list, capacities, and VM definitions.
    """
    rng = random.Random(seed)
    servers = [f"S{i}" for i in range(1, num_servers + 1)]

    graph = {s: [] for s in servers}
    edges = []

    # Start with a random spanning tree so the graph is always connected.
    for i in range(1, num_servers):
        u = servers[i]
        v = rng.choice(servers[:i])
        latency = rng.randint(2, 15)
        graph[u].append((v, latency))
        graph[v].append((u, latency))
        edges.append((u, v, latency))

    # Add extra links for a richer topology.
    existing = {tuple(sorted((u, v))) for u, v, _ in edges}
    target_extra = max(2, num_servers // 2)

    candidates = []
    for i in range(num_servers):
        for j in range(i + 1, num_servers):
            pair = tuple(sorted((servers[i], servers[j])))
            if pair not in existing:
                candidates.append(pair)

    rng.shuffle(candidates)
    for u, v in candidates[:target_extra]:
        latency = rng.randint(2, 20)
        graph[u].append((v, latency))
        graph[v].append((u, latency))
        edges.append((u, v, latency))

    capacities = {s: rng.randint(7, 14) for s in servers}

    vms = []
    for i in range(1, num_vms + 1):
        vms.append({
            "id": f"VM{i}",
            "source": rng.choice(servers),
            "demand": rng.randint(1, 4)
        })

    return graph, edges, capacities, vms
