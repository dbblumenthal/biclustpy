from . import main as bp
import numpy as np
import argparse as ap

def main():
    """Provides command line interface of biclustpy.
    """
    
    parser = ap.ArgumentParser(description="Compute bi-clusters using bi-cluster editing.")
    instance = parser.add_mutually_exclusive_group(required=True)
    instance.add_argument("--load", help="Load instance from .npy file.", metavar="input-file")
    instance.add_argument("--random", nargs=4, help="Randomly generate instance with num-rows rows and num-cols columns whose cells are of the form ((random value between 0 and 1) - threshold).", metavar=("num-rows", "num-cols", "threshold", "seed"))
    parser.add_argument("--save", help="Save bi-clusters as XML file.", metavar="output-file")
    parser.add_argument("--alg", default="ILP", help="Employed algorithm. Default = ILP.", choices=["ILP", "CH"])
    parser.add_argument("--ilp_options", nargs=2, type=int, default=[60, 0], help="Options for the algorithm ILP: time limit in second and flag that indicates whether model should be tuned before optimization.", metavar=("time-limit", "tune"))
    args = parser.parse_args()
    
    weights = np.array(0)
    if args.load is not None:
        weights = np.load(args.load)
    
    if args.random is not None:
        np.random.seed(int(args.random[3]))
        num_rows = int(args.random[0])
        num_cols = int(args.random[1])
        threshold = float(args.random[2])
        instance = "random"
        weights = np.random.rand(num_rows, num_cols) - (threshold * np.ones((num_rows, num_cols)))
    
    algorithm = bp.Algorithm()
    algorithm.algorithm_name = args.alg
    algorithm.ilp_time_limit = args.ilp_options[0]
    algorithm.ilp_tune = args.ilp_options[1]
    bi_clusters, obj_val, is_optimal = bp.compute_bi_clusters(weights, algorithm)
    
    if args.save is not None:
        instance = ""
        if args.load is not None:
            instance = args.load
        if args.random is not None:
            instance = "random (threshold=" + args.random[2] + ", seed=" + args.random[3] + ")"
        bp.save_bi_clusters_as_xml(args.save, bi_clusters, obj_val, is_optimal, instance)
        