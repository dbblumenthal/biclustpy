# biclustpy

A Python library for bi-cluster editing.

## The Bi-Cluster Editing Problem

- Task: Given a matrix `weights` with positive and negative weights, transform the bipartite graph induced by `weights` into a disjoint collection of bi-cliques (bi-clusters) via edge insertions and deletions, such that the overall transformation cost is minimal.
- The node sets of the bipartite graph induced by `weights` are the sets of rows and columns. There is an edge between row `i` and column `k` if and only if `weights[i,k] > 0`.
- Deleting an existing edge `(i,k)` incurs cost `weights[i,k]`.
- Inserting a non-existing edge `(i,k)` incurs cost `-weights[i,k]`. 
 
## Installation

1. Download and install [Gurobi](https://www.gurobi.com/) and obtain a license by following the instructions in the installation guide for [Linux](https://www.gurobi.com/documentation/8.0/quickstart_linux/software_installation_guid.html#section:Installation), [Mac OS](https://www.gurobi.com/documentation/8.0/quickstart_mac/software_installation_guid.html#section:Installation), or [Windows](https://www.gurobi.com/documentation/8.0/quickstart_windows/software_installation_guid.html#section:Installation).
2. Open a shell and execute `pip install biclustpy`.

## Library Usage

After installation, `import biclustpy as bp` into your Python application. Then use it as follows: 

- `bp.Algorithm`: Use this class to select the algorithm you want to employ.
  - `bp.Algorithm.algorithm_name`: String you can use to select the algorithm you want to employ. Default: `"ILP"`.
     - Set to `"ILP"` if you want to use Gurobi to solve the ILP formulation suggested in [G. F. de Sousa Filho et al (2017): New heuristics for the bicluster editing problem](https://doi.org/10.1007/s10479-016-2261-x).
     - Set to `"CH"` if you want to use the constructive heuristic suggested in [G. F. de Sousa Filho et al (2017): New heuristics for the bicluster editing problem](https://doi.org/10.1007/s10479-016-2261-x).
     - More algorithms are following soon.
   - `bp.Algorithm.ilp_time_limit`: Integer that specifies a time limit in seconds for the optimization and the tuning phase of the algorithm `"ILP"`. Default: `60`.
   - `bp.Algorithm.ilp_tune`: Boolean flag that indicates whether or not `"ILP"` should be tuned before being optimized. Default: `False`.  
- `bp.compute_bi_clusters(weights, algorithm)`: Use this function  to solve a bi-cluster editing problem.
  -  `weights`: The problem instance given as a `numpy.array`. 
  -  `algorithm`: The selected algorithm given as a `bp.Algorithm` object.
- `bp.save_bi_clusters_as_xml(filename, bi_clusters, obj_val, is_optimal, instance = "")`: Use this function to save the obtained solution as an XML file.
  - `filename`: The name of the XML file.
  - `bi_clusters`: The bi-clusters returned by `bp.compute_bi_clusters`.
  - `obj_val`: The objective value of the bi-clusters returned by `bp.compute_bi_clusters`. 
  - `is_optimal`: A flag returned by `bp.compute_bi_clusters` that indicates whether the computed bi-clusters are guaranteed to be optimal.
  - `instance`: A string that contains information about the problem instance.

### Example

```
import numpy as np
import biclustpy as bp

algorithm = bp.Algorithm
algorithm.algorith_name = "ILP"
algorithm.ilp_time_limit = 100
algorithm.ilp_tune = True

n = 30
m = 40
t = .95
weights = np.random.rand(n, m) - (t * np.ones((n, m)))

bi_clusters, obj_val, is_optimal = bp.compute_bi_clusters(weights, algorithm)

filename = "bi_clusters.xml"
instance = "random instance with 30 rows and 40 columns"
bp.save_bi_clusters_as_xml(filename, bi_clusters, obj_val, is_optimal, instance)
```

## Command Line Usage

Upon installation, you can run `biclustpy` from the command line. Usage:

```
biclustpy [-h]
          (--load input-file | --random num-rows num-cols threshold seed)
          [--save output-file] [--alg {ILP,CH}]
          [--ilp_options time-limit tune]
```

More more information, execute `biclustpy -h`.

## License

You may use and distribute __biclustpy__ under the terms of the [GNU Lesser General Public License](https://www.gnu.org/licenses/lgpl-3.0.html).
