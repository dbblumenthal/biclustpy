import networkx as nx

def col_to_node(col, num_rows):
    """Returns node ID of a column in the instance.
    
    Args:
        col (int): The column ID.
        num_rows (int): The number of rows in the instance.
    
    Returns:
        int: The node ID of the column col.
    """
    return num_rows + col

def node_to_col(node, num_rows):
    """Returns column ID of a node in the intance's graph representation that represents a column.
    
    Args:
        node (int): The node ID of the column in the graph representation.
        num_rows (int): The number of rows in the instance.
    
    Returns:
        int: Column ID of the node. If negative, the node is not a column but a row.
    """
    return node - num_rows

def is_row(node, num_rows):
    """Checks if a node in the graph representation of the instance is a row.
    
    Args:
        node (int): The node ID in the graph representation.
        num_rows (int): The number of rows in the instance.
    
    Returns:
        bool: True if and only if node is a row.
    """
    return node < num_rows

def is_col(node, num_rows):
    """Checks if a node in the graph representation of the instance is a column.
    
    Args:
        node (int): The node ID in the graph representation.
        num_rows (int): The number of rows in the instance.
    
    Returns:
        bool: True if and only if node is a column.
    """
    return node >= num_rows
    
def build_graph_from_weights(weights, nodes):
    """Builds NetworkX graph for given weights, threshold, and subset of nodes.
    
    Args:
        weights (numpy.array): The overall problem instance.
        nodes (list of int): The set of nodes for which the graph should be build. 
            Must be a subset of range(weights.shape[0] + weights.shape[1]).
    
    Returns:
        networkx.Graph: The induced subgraph in the specified set of nodes.
    """
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    num_rows = weights.shape[0]
    for row in nodes:
        if is_col(row, num_rows):
            continue
        for col in nodes:
            if is_row(col, num_rows):
                continue
            if weights[row, node_to_col(col, num_rows)] > 0:
                graph.add_edge(row, col)
    return graph

def connected_components(graph):
    """Decomposes graph into connected components.
    
    Args:
        graph (networkx.Graph): Graph that should be decomposed.
    
    Returns:
        list of networkx.Graph: List of connected components.
    """
    nodes_of_components = list(nx.connected_components(graph))
    num_components = len(nodes_of_components)
    components = [nx.Graph() for i in range(num_components)]
    labels = {}
    for i in range(num_components):
        components[i].add_nodes_from(nodes_of_components[i])
        for node in nodes_of_components[i]:
            labels[node] = i
    for (node_1, node_2) in graph.edges:
        i = labels[node_1]
        if labels[node_2] == i:
            components[i].add_edge(node_1, node_2)
    return components
    
def is_bi_clique(graph, num_rows):
    """Checks if a bipartite graph is a bi-clique.
    
    Args:
        graph (networkx.Graph): Bipartite graph.
        num_rows (int): The number of nodes in the original instance. 
            Nodes are in the left partition of graph if and only if their ID is smaller than num_rows.
    
    Returns:
         bool: True if and only if the graph is a bi-clique.
    """
    size_left = 0
    size_right = 0
    for node in graph.nodes:
        if is_row(node, num_rows):
            size_left = size_left + 1
        else:
            size_right = size_right + 1
    return graph.number_of_edges() == size_left * size_right
    
def is_singleton(bi_cluster):
    return (len(bi_cluster[0]) == 0) or (len(bi_cluster[1]) == 0)