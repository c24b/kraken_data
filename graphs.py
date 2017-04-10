#/usr/bin/env python3
#coding: utf-8
'''
filename: graphs.py
Scripts to build and draw graphs
'''
import networkx as nx
import matplotlib.pyplot as plt
from itertools import chain

def build_graph_cotypes(resources, types):
    '''Show the graph of common types
    predicates are shown as **nodes**
    '''
    co_types = get_common_types(resources, types)
    g = nx.DiGraph()

    nodes = resources
    targets = [n[1] for n  in co_types]

    for nodes, edge in co_types:

        for node in nodes:
            g.add_edge(node, edge)
    pos = nx.spring_layout(g)

    # nx.draw_networkx_nodes(g,pos,
    #                        nodelist=resources,
    #                        node_color='red')
    # #
    # nx.draw_networkx_nodes(g,pos,
    #                        nodelist=targets,
    #                        node_color='blue')
    #
    #

    nx.draw(g,pos, with_labels = True)
    plt.savefig("level0.png") # save as png
    plt.show()

def build_edges(resource="Louis_de_Funès"):
    '''build edges for one ressource'''
    types = get_type_label(resource)
    tags = get_tags(types)
    edges = [(resource,t,w) for t,w in tags.items() if w > 1]
    return edges

def build_graph(resources,edges):
    g2 = nx.Graph()

    for e in edges:
        # print(e[0])
        g2.add_edge(e[0], e[1])
    return g2

def draw_graph(g, resources):
    node_path = get_commons_tags(g,resources)
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=g.nodes(),
                       node_color='grey',
                       node_size=100,
                   alpha=0.6, with_labels=True)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=node_path,
                       node_color='green',
                       node_size=300,
                   alpha=0.7, with_labels=True)
    nx.draw_networkx_nodes(g,pos,
                       nodelist=resources,
                       node_color='r',
                       node_size=500,
                   alpha=0.8, with_labels=True)
    labels = {}
    for i,n in enumerate(g.nodes()):
        labels[n] = n
    nx.draw_networkx_labels(g,pos,labels,font_size=10)
    nx.draw_networkx_edges(g, pos=pos)

    plt.savefig("digraph.png") # save as png
    plt.show()
    return g

# def get_edges(resources):
#     return list(chain.from_iterable(build_edges(n) for n in resources))
