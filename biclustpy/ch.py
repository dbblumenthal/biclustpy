import networkx as nx
import numpy as np
from progress.bar import Bar
from . import helpers

def run(weights, subgraph):
    """Suboptimally solves the bi-cluster editing problem via a constructive heuristic.
    
    Implements the heuristic CH suggested in: 
    G. F. de Sousa Filho, T. L. B. Junior, L. dos Anjos F. Cabral, L. S. Ochi, and F. Protti:
    New heuristics for the bicluster editing problem. Annals OR 258(2), pp. 781-814, 2017,
    https://doi.org/10.1007/s10479-016-2261-x.
    
    Args:
        weights (numpy.array): The overall problem instance.
        subgraph (networkx.Graph): The subgraph that should be rendered bi-transitive.
    
    Returns:
        networkx.Graph: The obtained bi-transitive graph.
        float: Objective value of obtained solution.
        bool: True if and only if obtained solution is guaranteed to be optimal.
    """
    
    print("Subproblem is solved with CH.")
    
    # Get rows and columns of the sub-problem.
    num_rows = weights.shape[0]
    rows = [node for node in subgraph.nodes if helpers.is_row(node, num_rows)]
    cols = [node for node in subgraph.nodes if helpers.is_col(node, num_rows)]
    
    # Compute g-values for greedily picking pairs of nodes.
    bar = Bar("Computing g-values.", max = len(rows) * len(cols))
    queue = []
    for i in rows:
        n2i = [j for l in subgraph.adj[i] for j in subgraph.adj[l]]
        for k in cols:
            n2k = [l for j in subgraph.adj[k] for l in subgraph.adj[j]]
            g = weights[i, helpers.node_to_col(k, num_rows)]
            g = g + sum([weights[i, helpers.node_to_col(l, num_rows)] for l in n2k if l != k])
            g = g + sum([weights[j, helpers.node_to_col(k, num_rows)] for j in n2i if j != i])
            g = g - sum([weights[i, helpers.node_to_col(l, num_rows)] for l in cols if weights[i, helpers.node_to_col(l, num_rows)] > 0])
            g = g + sum([weights[i, helpers.node_to_col(l, num_rows)] for l in n2k if weights[i, helpers.node_to_col(l, num_rows)] > 0])
            g = g - sum([weights[j, helpers.node_to_col(k, num_rows)] for j in rows if weights[j, helpers.node_to_col(k, num_rows)] > 0])
            g = g + sum([weights[j, helpers.node_to_col(k, num_rows)] for j in n2i if weights[j, helpers.node_to_col(k, num_rows)] > 0])
            queue.append(((i,k),g))
            bar.next()
    bar.finish()
          
    # Sort the queue of all pairs of nodes in decrasing order w.r.t. their g-values.
    queue.sort(key = lambda t: t[1], reverse = True)
    
    # Construct the bi-transitive subgraph.
    print("Constructing the bi-transitive subgraph ...")  
    bi_transitive_subgraph = nx.Graph()
    shrinking_subgraph = nx.Graph(subgraph)
    is_deleted = {node : False for node in shrinking_subgraph.nodes}
    pos = 0
    while len(shrinking_subgraph.edges) > 0:
        # Find the pair (i,k) of undeleted nodes that maximizes the g-value.
        while is_deleted[queue[pos][0][0]] or is_deleted[queue[pos][0][1]]:
            pos = pos + 1
        i = queue[pos][0][0]
        k = queue[pos][0][1]
        # Set the bi-cluster to the union of neighborhoods of i and k.
        bi_cluster_left = set(shrinking_subgraph.adj[k])
        bi_cluster_left.add(i)
        bi_cluster_right = set(shrinking_subgraph.adj[i])
        bi_cluster_right.add(k)
        # Update teh bi-transitive subgraph, the shrinking subgraph, and the deletion flags.
        bi_transitive_subgraph.add_nodes_from(bi_cluster_left)
        bi_transitive_subgraph.add_nodes_from(bi_cluster_right)
        bi_transitive_subgraph.add_edges_from([(j, l) for j in bi_cluster_right for l in bi_cluster_left])
        shrinking_subgraph.remove_nodes_from(bi_cluster_left)
        shrinking_subgraph.remove_nodes_from(bi_cluster_right)
        for node in bi_cluster_left:
            is_deleted[node] = True
        for node in bi_cluster_right:
            is_deleted[node] = True
        pos = pos + 1
    # Add isolated nodes to teh bi-transitive subgraph.
    bi_transitive_subgraph.add_nodes_from(shrinking_subgraph.nodes)
    
    # Compute the objective value of the constructed solution.
    obj_val = 0
    for i in rows:
        for k in cols:
            if subgraph.has_edge(i,k) != bi_transitive_subgraph.has_edge(i,k):
                obj_val = obj_val + abs(weights[i, helpers.node_to_col(k, num_rows)])
                
    # Return the obtained bi-transitive subgraph and the objective value.
    return bi_transitive_subgraph, obj_val, False