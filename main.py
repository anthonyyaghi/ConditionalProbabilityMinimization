import matplotlib.pyplot as plt
import networkx as nx
import utils

g: nx.MultiGraph = nx.read_edgelist('graph.txt', create_using=nx.MultiGraph, nodetype=int, data=(('r', float),))
g.add_node(2, name='source')
g.add_node(5, name='sink')

print(utils.is_spg(g))

pos = nx.spring_layout(g)
nx.draw(g, pos, with_labels=True)
plt.show()
