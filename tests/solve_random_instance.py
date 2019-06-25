import os
import sys
lib_path = os.path.abspath(os.path.join(__file__, '..', '..'))
sys.path.append(lib_path)
import biclustpy as bc
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Computes biclusters for randomly generated instance with weight between 0 and 1.")
parser.add_argument("num_rows", type=int, help="Number of rows in the instance.")
parser.add_argument("num_cols", type=int, help="Number of columns in the instance.")
parser.add_argument("threshold", type=float, help="Edges whose weight is lower than the threshold are absent.")
parser.add_argument("--time_limit", type=float, help="Time limit in seconds for optimizing the subproblems. Default = 60.")
args = parser.parse_args()

weights = np.random.rand(args.num_rows, args.num_cols)
threshold = .99
algorithm = bc.Algorithm()
if (args.time_limit):
    algorithm.ilp_time_limit = args.time_limit
bi_clusters, obj_val, is_optimal = bc.compute_bi_clusters(weights, args.threshold, algorithm)