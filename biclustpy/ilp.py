import gurobipy as gp
import networkx as nx
from progress.bar import Bar
from . import helpers

def run(weights, subgraph, time_limit, tune):
    """Calls Gurobi to solve ILP formulation of the bi-cluster editing problem.
    
    Implements the ILP suggested in: 
    G. F. de Sousa Filho, T. L. B. Junior, L. dos Anjos F. Cabral, L. S. Ochi, and F. Protti:
    New heuristics for the bicluster editing problem. Annals OR 258(2), pp. 781-814, 2017,
    https://doi.org/10.1007/s10479-016-2261-x.
    
    Args:
        weights (numpy.array): The overall problem instance.
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
    
    # Get rows and columns of the sub-problem.
    num_rows = weights.shape[0]
    rows = [node for node in subgraph.nodes if helpers.is_row(node, num_rows)]
    cols = [helpers.node_to_col(node, num_rows) for node in subgraph.nodes if helpers.is_col(node, num_rows)]
    
    # Add one binary decision variable x[(i,k)] for each possible edge (i,k) and set objective function.
    x = {}
    bar = Bar("Adding variables.  ", max = len(rows) * len(cols))
    constant = 0
    start = 1.0
    if 2 * len(subgraph.edges) >= len(rows) * len(cols):
        start = 0.0
    for i in rows:
        for k in cols:
            x[(i,k)] = model.addVar(lb = 0.0, ub = 1.0, obj = weights[i,k], vtype = gp.GRB.BINARY)
            x[(i,k)].setAttr(gp.GRB.Attr.Start, start)
            if weights[i,k] <= 0:
                constant = constant - weights[i,k]
            bar.next()
    bar.finish()
    
    # Add contsraints to rule out induced P4s in the solution.
    bar = Bar("Adding constraints.", max = len(rows) * len(rows) * len(cols) * len(cols))
    for i in rows:
        for j in rows:
            for k in cols:
                for l in cols:
                    new_constr = model.addConstr(x[(i,k)] - x[(i,l)] - x[(j,k)] - x[(j,l)] <= 0)
                    bar.next()
    bar.finish()
        
    # Solve the model.
    model.update()
    if tune:
        print("Tuning the model ...")
        model.tune()
    print("Solving the model ...")
    model.optimize()
    
    # Construct the bi-transitive subgraph from the solved model.
    bi_transitive_subgraph = nx.Graph()
    bi_transitive_subgraph.add_nodes_from(subgraph.nodes)
    for (i,k) in x:
        if x[(i,k)].getAttr(gp.GRB.Attr.X) == 0.0:
            bi_transitive_subgraph.add_edge(i, helpers.col_to_node(k, num_rows))
    
    # Return the solution.
    obj_val = model.objVal + constant
    is_optimal = (model.getAttr(gp.GRB.Attr.Status) == 2)
    return bi_transitive_subgraph, obj_val, is_optimal