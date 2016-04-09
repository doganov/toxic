#!/usr/bin/env python3

import os
import os.path
import sys

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
    return [n for n in graph.get_nodes() if unquote(n.get_label()) in labels]

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

def transform_file(input_filename, output_filename, f, verbose=False):
    if verbose:
        print("Transforming {} -> {}...".format(input_filename, output_filename),
              file=sys.stderr)

    with open(input_filename, "r") as input_file:
        dot_data = input_file.read()

    dot_data = transform(dot_data, f)

    with open(output_filename, "w") as output_file:
        output_file.write(dot_data)

def transform_dir(input_dirname, output_dirname, f, verbose=False):
    input_basenames = [i
                       for i in os.listdir(input_dirname)
                       if (i.endswith(".dot") or i.endswith(".DOT"))]
    for basename in input_basenames:
        input_filename = os.path.join(input_dirname, basename)
        output_filename = os.path.join(output_dirname, basename)
        transform_file(input_filename, output_filename, f, verbose=verbose)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        usage="[-h] -t THRESHOLD -r GC_ROOT [INPUT OUTPUT]",
        description="Small .dot file transformation utility")
    parser.add_argument(
        "INPUT",
        nargs="?",
        help="input filename or directory")
    parser.add_argument(
        "OUTPUT",
        nargs="?",
        help="output filename or directory")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        required=True,
        help="edge weight threshold value")
    parser.add_argument(
        "-r",
        "--gc-root",
        action="append",
        required=True,
        help="label of the node to be used as a root during the " + \
        "garbage collection (GC) phase. May be used multiple times " + \
        "to specify multiple GC roots.")
    args = parser.parse_args()

    f = lambda g: prune(g, args.threshold, args.gc_root)

    def die(msg):
        print("{}: {}".format(parser.prog, msg), file=sys.stderr)
        sys.exit(-1)

    if (not args.INPUT) and (not args.OUTPUT):
        # pipe mode
        print(transform(sys.stdin.read(), f))
    elif args.INPUT and args.OUTPUT:
        if not os.path.exists(args.INPUT):
            die("{} does not exist".format(args.INPUT))
        if os.path.isfile(args.INPUT):
            # file mode
            transform_file(args.INPUT, args.OUTPUT, f)
        elif os.path.isdir(args.INPUT):
            if os.path.isdir(args.OUTPUT):
                # dir mode
                transform_dir(args.INPUT, args.OUTPUT, f, verbose=True)
            else:
                die("{} is not an exising directory".format(args.OUTPUT))
    else:
        parser.print_usage(file=sys.stderr)
