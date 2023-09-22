from typing import Hashable, List, Union

import networkx as nx

from .helper import get_node_keys

NodeType = Union[int, str, Hashable]


def rsph_tree(
    connection_graph: nx.Graph,
    sinks: List[NodeType],
    from_type: str = "building",
    to_type: str = "wwtp",
    skip_nodes: List[NodeType] = [],
) -> nx.DiGraph:
    """
    Returns the directed routed steiner tree that connects all terminal nodes to the sink using the repeated shortest path heuristic.

    Parameters
    ----------
    connection_graph : nx.Graph
        The graph representing the sewer network.
    sinks : List[NodeType]
        The nodes representing the sinks in the sewer network.
    from_type : str, optional
        The type of the source nodes, by default "building".
    to_type : str, optional
        The type of the sink nodes, by default "wwtp".
    skip_nodes : List[NodeType], optional
        The nodes to skip in the routing, by default [].

    Returns
    -------
    nx.DiGraph
        The directed routed steiner tree that connects all terminal nodes to the sink using the repeated shortest path heuristic.
    """
    sewer_graph = nx.DiGraph(nx.create_empty_copy(connection_graph))
    terminals = get_node_keys(connection_graph, field="node_type", value=from_type)
    terminals = [n for n in terminals if n not in skip_nodes]
    subgraph_nodes = sinks

    # sageguard against sinks not being in the connection graph
    for sink in sinks:
        if sink not in connection_graph.nodes:
            raise ValueError(f"Sink {sink} not found in the connection graph.")

    # Handling single sink case
    if len(subgraph_nodes) == 1:
        subgraph_nodes = sinks + sinks
    all_paths = dict(nx.all_pairs_dijkstra_path(connection_graph))
    all_lengths = dict(nx.all_pairs_dijkstra_path_length(connection_graph))

    while len(terminals) > 0:
        try:
            path = find_rsph_path(
                connection_graph, subgraph_nodes, terminals, all_paths, all_lengths
            )
        except ValueError as e:
            print(f"Error finding path: {e}")
            break  # exit the loop if no viable terminal is found

        # add edges of path to sewer graph while keeping edge attributes
        nx.add_path(sewer_graph, path)

        edgesinpath = zip(path[:-1], path[1:])
        for edge in edgesinpath:
            nx.set_edge_attributes(
                sewer_graph,
                {
                    (edge[0], edge[1]): connection_graph.get_edge_data(
                        edge[0], edge[1]
                    )[0]
                },
            )
        subgraph_nodes = subgraph_nodes + path[1:-1]
        terminals.remove(path[0])

    return sewer_graph


def find_rsph_path(
    connection_graph: nx.Graph,
    subgraph_nodes: List,
    terminals: List,
    all_paths: dict,
    all_lengths: dict,
) -> List[NodeType]:
    """
    Identifies the closest terminal node to the growing tree and returns the connection path.

    Parameters
    ----------
    connection_graph : nx.Graph
        The graph representing the entire network.
    subgraph_nodes : List[NodeType]
        The nodes in the subgraph being grown.
    terminals : List[NodeType]
        The terminal nodes in the network.
    all_paths : dict
        A dictionary containing all the shortest paths between terminal nodes.
    all_lengths : dict
        A dictionary containing the lengths of all the shortest paths between terminal nodes.

    Returns
    -------
    List[NodeType]
        The shortest path between the closest terminal node and the growing subgraph.

    Raises
    ------
    ValueError
        If there is no recorded path from the closest terminal node to the growing subgraph in the all_paths dictionary.
    """
    terminal_distances = []
    closest_tree_node = []
    for terminal in terminals:
        # check if there is a recorded distance between the terminal and nodes in the subgraph
        missing_nodes = [
            node for node in subgraph_nodes if node not in all_lengths[terminal]
        ]
        if missing_nodes:
            print(f"Terminal {terminal} missing distances to nodes: {missing_nodes}.")
            continue
        # if any(node not in all_lengths[terminal] for node in subgraph_nodes):
        #     continue  # Skip this terminal as it doesn't have distances to all subgraph_nodes
        # get distances from the terminal node to all nodes in the subgraph
        distances = [all_lengths[terminal][node] for node in subgraph_nodes]
        min_dist = min(distances)
        tree_node = subgraph_nodes[distances.index(min_dist)]
        terminal_distances.append(min_dist)
        closest_tree_node.append(tree_node)

    # safe guard if no terminal distances are found
    if not terminal_distances:
        raise ValueError(
            f"No viable terminal found to connect to the subgraph nodes: {subgraph_nodes}."
        )
    min_dist_global = min(terminal_distances)
    result_index = terminal_distances.index(min_dist_global)
    closest_terminal = terminals[result_index]
    tree_node = closest_tree_node[result_index]

    if tree_node not in all_paths[closest_terminal]:
        raise ValueError(
            f"No recorded path from {closest_terminal} to {tree_node} in the all_paths dictionary."
        )
    return all_paths[closest_terminal][tree_node]
