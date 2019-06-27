import os
import sys
lib_path = os.path.abspath(os.path.join(__file__, '..', '..'))
sys.path.append(lib_path)
import biclustpy as bp
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Computes biclusters for randomly generated instance with weight between 0 and 1.")
parser.add_argument("num_rows", type=int, help="Number of rows in the instance.")
parser.add_argument("num_cols", type=int, help="Number of columns in the instance.")
parser.add_argument("threshold", type=float, help="Edges whose weight is lower than the threshold are absent.")
parser.add_argument("--alg", help="Algorithm to be used for solving the subproblems. Default: ILP.", metavar="ILP|CH")
parser.add_argument("--time_limit", type=float, help="Time limit in seconds for optimizing the subproblems using Gurobi. Default: 60.")
parser.add_argument("--seed", type=int, help="Set seed of random number generator instead of drawing it from the system.")
args = parser.parse_args()

if args.seed is not None:
    np.random.seed(args.seed)
weights = np.random.rand(args.num_rows, args.num_cols) - (args.threshold * np.ones((args.num_rows, args.num_cols)))
algorithm = bp.Algorithm()
if (args.alg):
    algorithm.algorithm_name = args.alg
if (args.time_limit):
    algorithm.ilp_time_limit = args.time_limit
bi_clusters, obj_val, is_optimal = bp.compute_bi_clusters(weights, algorithm)
print("\nObtained bi-clusters:")
print(bi_clusters)