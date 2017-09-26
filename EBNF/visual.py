
pgv = None

try:
    import pygraphviz as pgv
except Exception:
    print "pygraphviz module is not available"
finally:
    pass

import parser as ebnf
import random

def draw_graph(tree, filename):
    if not pgv:
        print "pygraphviz module is not available"
        return
    if not tree:
        return
    graph = pgv.AGraph(directed = True, strict = True)
    draw_tree(tree, graph = graph, parent_node = None)
    graph.layout('dot') # ??? layout with dot
    graph.draw(filename)

def draw_tree(tree, graph = None, parent_node = None):
    node = random.randint(1,10000000)
    if isinstance(tree, ebnf.RepeatTree):
        graph.add_node(node, color='#FFA07A', shape='polygon', sides=5, style='filled', label=str(tree))
        graph.add_edge(node, node)
        if parent_node:
            graph.add_edge(parent_node, node)
        draw_tree(tree.L, graph=graph, parent_node=node)
        draw_tree(tree.R, graph=graph, parent_node=node)
    elif isinstance(tree, ebnf.OrTree):
        graph.add_node(node, color='#98FB98', shape='polygon', sides=3, style='filled', label=str(tree))
        if parent_node:
            graph.add_edge(parent_node, node)
        draw_tree(tree.L, graph=graph, parent_node=node)
        draw_tree(tree.R, graph=graph, parent_node=node)
    elif isinstance(tree, ebnf.AndTree):
        graph.add_node(node, color='#AFEEEE', shape='box', style='filled', label=str(tree))
        if parent_node:
            graph.add_edge(parent_node, node)
        draw_tree(tree.L, graph=graph, parent_node=node)
        draw_tree(tree.R, graph=graph, parent_node=node)
    elif isinstance(tree, ebnf.Leaf):
        graph.add_node(node, label=str(tree), color='#F0E68C', style='filled')
        if parent_node:
            graph.add_edge(parent_node, node)
    else:
        pass
