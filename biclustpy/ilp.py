import numpy as np
import gurobipy as gp
import networkx as nx
from progress.bar import Bar
from scipy.special import binom
from . import helpers

def run(weights, threshold, subgraph, time_limit, tune):
    """Calls Gurobi to solve bi-cluster editing problems.
    
    Args:
        weights (numpy.array): The problem instance.
        threshold (float): Edges whose weights are below the threshold are absent.
        subgraph (networkx.Graph): The subgraph that should be rendered bi-transitive.
        time_limit (float): Time limit in seconds. If negative, no time limit is enforced.
        tune (bool): If True, the model is tuned before optimization.
    
    Returns:
        networkx.Graph: The obtained bi-transitive graph.
        float: Objective value of obtained solution.
        bool: True if and only if obtained solution is guaranteed to be optimal.
    """
    
    # Initialize Gurobi model.
    print("Subproblem is solved with Gurobi ILP.")
    model = gp.Model()
    model.modelSense = gp.GRB.MINIMIZE
    model.Params.OutputFlag = 0
    if (time_limit <= 0):
        model.Params.TimeLimit = gp.GRB.INFINITY
        model.Params.TuneTimeLimit = gp.GRB.INFINITY
    else:
        model.Params.TimeLimit = time_limit
        model.Params.TuneTimeLimit = time_limit
    
    # Get dimension of the problem instance.
    num_rows = weights.shape[0]
    num_cols = weights.shape[1]
    rows = [node for node in subgraph.nodes if helpers.is_row(node, num_rows)]
    cols = [helpers.node_to_col(node, num_rows) for node in subgraph.nodes if helpers.is_col(node, num_rows)]
    n = len(rows)
    m = len(cols)
    
    # Add one binary decision variable x[(i,k)] for each possible edge (i,k) and set objective function.
    constant = sum([weights[i,k] - threshold for i in rows for k in cols if weights[i,k] >= threshold])
    cost_matrix = (threshold * np.ones((num_rows, num_cols))) - weights
    x = {}
    bar = Bar("Adding edge variables.      ", max = n * m)
    for i in rows:
        for k in cols:
            x[(i,k)] = model.addVar(lb = 0.0, ub = 1.0, obj = cost_matrix[i,k], vtype = gp.GRB.BINARY)
            bar.next()
    bar.finish()
    
    # Add one axiliary binary variable y[((i,j),(k,l))] for each subgraph {i,j}x{k,l} of size 4. 
    # If y[((i,j),(k,l))] = 0, the subgraph is a bi-clique. Otherwise it contains at most 2 edges.
    size_4_subgraphs = []
    y = {}
    bar = Bar("Adding subgraph variables.  ", max = binom(n, 2) * binom(m, 2))
    for pos_i in range(n):
        i = rows[pos_i]
        for pos_j in range(pos_i + 1, n):
            j = rows[pos_j]
            for pos_k in range(m):
                k = cols[pos_k]
                for pos_l in range(pos_k + 1, m):
                    l = cols[pos_l]
                    size_4_subgraphs.append(((i,j),(k,l)))
                    y[((i,j),(k,l))] = model.addVar(lb = 0.0, ub = 1.0, obj = 0.0, vtype = gp.GRB.BINARY)
                    bar.next()
    bar.finish()
    
    # Add constraints that forbid P4 subgraphs.
    big_m = 4
    bar = Bar("Adding subgraph constraints.", max = binom(n, 2) * binom(m, 2))
    for ((i,j),(k,l)) in size_4_subgraphs:
        new_constr = model.addConstr(x[(i,k)] + x[(i,l)] + x[(j,k)] + x[(j,l)] + big_m * y[((i,j),(k,l))] >= 4)
        new_constr = model.addConstr(x[(i,k)] + x[(i,l)] + x[(j,k)] + x[(j,l)] + big_m * y[((i,j),(k,l))] <= 2 + big_m)
        bar.next()
    bar.finish()
        
    # Solve the model.
    model.update()
    if tune:
        print("Tuning the model ...")
        model.tune()
    print("Solving the model ...")
    model.optimize()
    
    # Compute the adjacency matrix from the solved model.
    bi_transitive_subgraph = nx.Graph()
    bi_transitive_subgraph.add_nodes_from(subgraph.nodes)
    for (i,k) in x:
        if x[(i,k)].getAttr(gp.GRB.Attr.X) > 0.0:
            bi_transitive_subgraph.add_edge(i, helpers.col_to_node(k, num_rows))
    
    # Return the solution.
    obj_val = model.objVal + constant
    is_optimal = (model.getAttr(gp.GRB.Attr.Status) == 2)
    return bi_transitive_subgraph, obj_val, is_optimal