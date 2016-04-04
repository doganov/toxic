#!/usr/bin/env python3

import pydot_ng as pydot

def unquote(quoted):
    if quoted.startswith('"') and quoted.endswith('"'):
        return quoted[1:-1]

    return quoted

def points(edge):
    return (edge.get_source(), edge.get_destination())

def walk(graph, start_node, f):
    neighbours = {}
    def register(key_node_name, value_node_name):
        values = neighbours.get(key_node_name, set())
        values.add(value_node_name)
        neighbours[key_node_name] = values

    for edge in graph.get_edges():
        register(edge.get_source(), edge.get_destination())
        register(edge.get_destination(), edge.get_source())

    visited = set()
    pending = set([start_node.get_name()])
    while pending:
        node_name = pending.pop()
        for node in graph.get_node(node_name):
            f(node)
        visited.add(node_name)
        pending = pending | neighbours.get(node_name, set())
        pending = pending - visited

def gc(graph, gc_roots):

    # "mark" phase
    marked = set()

    def mark(node):
        marked.add(node.get_name())

    for gc_root in gc_roots:
        walk(graph, gc_root, mark)

    # "sweep" phase
    for node in graph.get_nodes():
        if node.get_name() not in marked:
            graph.del_node(node)

    # filter dangling edges
    for edge in graph.get_edges():
        if not (marked & set(points(edge))):
            graph.del_edge(points(edge))

def find_nodes(graph, labels):
    return [node for node in graph.get_nodes() if node.get_label() in labels]

def prune_edges(graph, threshold):
    for e in graph.get_edges():
        weight = float(unquote(e.get_label()))
        if weight < threshold:
            graph.del_edge(points(e))

def prune(graph, threshold, gc_root_labels):
    prune_edges(graph, threshold)
    gc(graph, find_nodes(graph, gc_root_labels))

def transform(dot_data, f):
    graph = pydot.graph_from_dot_data(dot_data)
    f(graph)
    return graph.to_string()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print("toxic.py transforms .dot data from stdin to stdout")

    threshold = 0.09 # FIXME
    gc_root_labels = ['"C6H6"', '"C7H8"', '"C10H12"'] # FIXME
    f = lambda g: prune(g, threshold, gc_root_labels)

    print(transform(sys.stdin.read(), f))
