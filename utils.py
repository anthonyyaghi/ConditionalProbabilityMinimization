import networkx as nx


def is_source(node):
    if node[1] == 'source':
        return True
    return False


def is_sink(node):
    if node[1] == 'sink':
        return True
    return False


def are_parallel(a, b):
    return min(a[0], a[1]) == min(b[0], b[1]) and max(a[0], a[1]) == max(b[0], b[1]) and a[2] != b[2]


def simplify(grf: nx.MultiGraph):
    simplified = False
    nodes_to_remove = []
    for node in grf.nodes(data='name', default='none'):
        if grf.degree[node[0]] == 2 and not is_source(node) and not is_sink(node):
            series_edges = list(grf.edges(node, keys=True, data='r'))
            from_node = series_edges[0][0] if series_edges[0][0] != node[0] else series_edges[0][1]
            to_node = series_edges[1][0] if series_edges[1][0] != node[0] else series_edges[1][1]

            grf.remove_edge(series_edges[0][0], series_edges[0][1], series_edges[0][2])
            grf.remove_edge(series_edges[1][0], series_edges[1][1], series_edges[1][2])
            nodes_to_remove.append(node[0])

            req = series_edges[0][3] * series_edges[1][3]
            grf.add_edge(from_node, to_node, r=req)
            simplified = True

    grf.remove_nodes_from(nodes_to_remove)

    do = True
    while do:
        do = False
        edges_to_remove = []
        edge_to_add = []

        for edge in grf.edges(data='r', keys=True, default=1.0):
            for other in grf.edges(data='r', keys=True, default=1.0):
                if are_parallel(edge, other):
                    req = edge[3] + other[3] - edge[3] * other[3]
                    edge_to_add.append(edge[0])
                    edge_to_add.append(edge[1])
                    edge_to_add.append(req)

                    edges_to_remove.append((edge[0:3]))
                    edges_to_remove.append((other[0:3]))

                    do = True
                    break
            if do:
                break

        if len(edge_to_add) != 0:
            grf.remove_edges_from(edges_to_remove)
            grf.add_edge(edge_to_add[0], edge_to_add[1], r=edge_to_add[2])
            simplified = True

    return simplified


def is_spg(graph: nx.MultiGraph):
    g = nx.MultiGraph(graph)
    while simplify(g):
        pass
    return g.number_of_nodes() == 2