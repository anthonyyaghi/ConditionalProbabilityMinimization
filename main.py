import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx.drawing.nx_agraph import graphviz_layout
import sys

import utils
from Node import Node


def when_n_is_good(g, edge, source, sink):
    if (edge[1] == source or edge[1] == sink) and (edge[0] == source or edge[0] == sink):
        g_good = nx.MultiGraph()
        g_good.add_node(source, name='source')
        g_good.add_node(sink, name='sink')
        g_good.add_edge(source, sink, r=1.0)
    elif edge[1] == source or edge[1] == sink:
        g_good = nx.contracted_nodes(g, edge[1], edge[0], False)
    else:
        g_good = nx.contracted_nodes(g, edge[0], edge[1], False)
    return g_good


def when_n_is_bad(g, edge, source, sink):
    g_bad = nx.MultiGraph(g)
    g_bad.remove_edge(edge[0], edge[1], edge[2])
    to_remove = []
    for node in g_bad.nodes:
        if g_bad.degree[node] == 1 and node != source and node != sink:
            to_remove.append(node)
    g_bad.remove_nodes_from(to_remove)
    return g_bad


def build_conditional_tree(root: Node, source, sink):
    if not utils.is_spg(root.data, source, sink):
        grf: nx.MultiGraph = root.data
        for edge in grf.edges(data='r', default=1.0, keys=True):
            child_good = Node(when_n_is_good(grf, edge, source, sink), edge, True)

            child_bad = Node(when_n_is_bad(grf, edge, source, sink), edge, False)

            build_conditional_tree(child_good, source, sink)
            build_conditional_tree(child_bad, source, sink)
            root.add_child(child_good)
            root.add_child(child_bad)


def find_best_path(root: Node):
    if len(root.children) == 0:
        return 0
    else:
        paths = []
        for c in root.children:
            score = find_best_path(c) + 1
            for other in root.children:
                if other != c and other.element == c.element:
                    score += find_best_path(other) + 1
            paths.append((score, c))
        scores = [t[0] for t in paths]
        good_element = paths[np.argmin(scores)][1].element
        to_remove = []
        for c in root.children:
            if c.element != good_element:
                to_remove.append(c)
        for c in to_remove:
            root.children.remove(c)
        return np.min(scores)


def build_tree_graph(root: Node, grf: nx.DiGraph, root_id):
    for c in root.children:
        condition = 'good' if c.good else 'bad'
        new_root = f'{c.element[0]}-{c.element[1]} is {condition}'
        grf.add_node(new_root)
        grf.add_edge(root_id, new_root)
        build_tree_graph(c, grf, new_root)


def solve_graph(g: nx.MultiGraph):
    source = None
    sink = None

    for n in g.nodes(data='name', default='none'):
        if n[1] == 'source':
            source = n[0]
        elif n[1] == 'sink':
            sink = n[0]

    if source is None or sink is None:
        print("Cant find the source and sink of the graph")
        return

    root = Node(g, None, None)
    build_conditional_tree(root, source, sink)

    print(f'Path: {find_best_path(root)}')

    tree = nx.DiGraph()
    tree.add_node('root')
    build_tree_graph(root, tree, 'root')
    pos = graphviz_layout(tree, prog='dot')
    nx.draw(tree, pos, with_labels=True, arrows=True)
    plt.show()


def build_graph_from_tgf(file_path):
    nodes = None
    edges = None

    with open(file_path) as f:
        lines = f.read().splitlines()
        split_index = lines.index("#")
        nodes = lines[0:split_index]
        edges = lines[split_index + 1:]

    g = nx.MultiGraph()
    if nodes is not None:
        for node in nodes:
            params = node.split(" ")
            name = params[0] if len(params) == 1 else params[1]
            g.add_node(params[0], name=name)

    if edges is not None:
        for edge in edges:
            params = edge.split(" ")
            if len(params) < 3:
                print("Invalid edge, reliability could be missing")
                exit(0)
            g.add_edge(params[0], params[1], r=float(params[2]))

    return g


if __name__ == '__main__':
    if len(sys.argv) == 2:
        g = build_graph_from_tgf(sys.argv[1])
        solve_graph(g)
    elif len(sys.argv) == 3:
        g = build_graph_from_tgf(sys.argv[1])
        source = None
        sink = None
        edge = None

        for n in g.nodes(data='name', default='none'):
            if n[1] == 'source':
                source = n[0]
            elif n[1] == 'sink':
                sink = n[0]

        edge_nodes = str(sys.argv[2]).split("-")
        if len(edge_nodes) != 2:
            print("Incorrect edge format")
            exit(0)
        for e in g.edges(data=True, keys=True):
            if e[0] == edge_nodes[0] and e[1] == edge_nodes[1] or e[0] == edge_nodes[1] and e[1] == edge_nodes[0]:
                edge = e
        if edge is None:
            print("Specified edge not found")
            exit(0)

        if source is None or sink is None:
            print("Cant find the source and sink of the graph")
            exit(0)
        g_good = when_n_is_good(g, edge, source, sink)
        utils.simplify_shorted_elements(g_good, source, sink)
        g_bad = when_n_is_bad(g, edge, sink, source)

        plt.subplot(2, 2, 1)
        fixed_positions = {source: (-10, 10), sink: (10, 10)}
        fixed_nodes = fixed_positions.keys()
        pos = nx.spring_layout(g, pos=fixed_positions, fixed=fixed_nodes)
        nx.draw(g, pos, with_labels=True)
        plt.title("Initial graph")

        plt.subplot(2, 2, 3)
        pos2 = nx.spring_layout(g_good, pos=fixed_positions, fixed=fixed_nodes)
        nx.draw(g_good, pos2, with_labels=True)
        plt.title(f'{sys.argv[2]} is good')

        plt.subplot(2, 2, 4)
        pos3 = nx.spring_layout(g_bad, pos=fixed_positions, fixed=fixed_nodes)
        nx.draw(g_bad, pos3, with_labels=True)
        plt.title(f'{sys.argv[2]} is bad')

        plt.show()
    else:
        print("Incorrect usage")
