import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx.drawing.nx_agraph import graphviz_layout

import utils
from Node import Node


def build_conditional_tree(root: Node, source, sink):
    if not utils.is_spg(root.data):
        grf: nx.MultiGraph = root.data
        for edge in grf.edges(data='r', default=1.0, keys=True):
            if edge[1] == source or edge[1] == sink:
                g_good = nx.contracted_nodes(grf, edge[1], edge[0], False)
            else:
                g_good = nx.contracted_nodes(grf, edge[0], edge[1], False)
            child_good = Node(g_good, edge, True)

            g_bad = nx.MultiGraph(grf)
            g_bad.remove_edge(edge[0], edge[1], edge[2])
            to_remove = []
            for node in g_bad.nodes:
                if g_bad.degree[node] == 1 and node != source and node != sink:
                    to_remove.append(node)
            g_bad.remove_nodes_from(to_remove)
            child_bad = Node(g_bad, edge, False)

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


def main(g):
    g.add_node(2, name='source')
    g.add_node(5, name='sink')

    root = Node(g, None, None)
    build_conditional_tree(root, 2, 5)

    print(f'Path: {find_best_path(root)}')

    tree = nx.DiGraph()
    tree.add_node('root')
    build_tree_graph(root, tree, 'root')
    pos = graphviz_layout(tree, prog='dot')
    nx.draw(tree, pos, with_labels=True, arrows=True)
    plt.show()


if __name__ == '__main__':
    main(nx.read_edgelist('graph.txt', create_using=nx.MultiGraph, nodetype=int, data=(('r', float),)))
