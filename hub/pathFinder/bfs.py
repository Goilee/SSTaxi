import networkx as nx

def bfs(graph: nx.MultiGraph, node, point):
    len_1 = dict()
    find = []
    visited = [node]
    queue = [node]
    len_1[node] = [node]
    while queue:
        if queue == [] : break
        s = queue.pop(0)
        for neighbor in graph.adj[s]:
            if neighbor not in visited:
                find.append(neighbor)
                len_1[neighbor] = [*len_1[s], neighbor]
                visited.append(neighbor)
                queue.append(neighbor)

            if neighbor == point:
                queue.clear()
                return len_1[point]