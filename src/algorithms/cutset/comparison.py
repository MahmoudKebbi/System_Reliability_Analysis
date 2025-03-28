import time
from typing import Dict, List, Set, Tuple
from src.models.system import SystemGraph
from src.algorithms.cutset.mocus import MOCUSAnalyzer
from src.algorithms.cutset.bdd import BDDAnalyzer


class CutSetComparison:
    """
    Compare different cut set analysis algorithms in terms of
    performance and results.
    """

    def __init__(self, system: SystemGraph):
        self.system = system

    def run_comparison(self) -> Dict:
        """
        Run performance comparison between algorithms

        Returns:
            Dictionary with performance metrics and results
        """
        results = {}

        # MOCUS algorithm
        start_time = time.time()
        mocus = MOCUSAnalyzer(self.system)
        mocus_cut_sets = mocus.find_minimal_cut_sets()
        mocus_time = time.time() - start_time

        # BDD algorithm
        start_time = time.time()
        bdd = BDDAnalyzer(self.system)
        bdd_cut_sets = bdd.find_minimal_cut_sets()
        bdd_time = time.time() - start_time

        # Verify results match
        results_match = self._compare_cut_sets(mocus_cut_sets, bdd_cut_sets)

        results = {
            "mocus": {
                "time": mocus_time,
                "cut_sets": mocus_cut_sets,
                "count": len(mocus_cut_sets),
            },
            "bdd": {
                "time": bdd_time,
                "cut_sets": bdd_cut_sets,
                "count": len(bdd_cut_sets),
            },
            "match": results_match,
        }

        return results

    def _compare_cut_sets(self, cs1: List[Set[str]], cs2: List[Set[str]]) -> bool:
        """
        Compare if two lists of cut sets contain the same minimal cut sets
        """
        # Convert to frozenset for set operations
        fs1 = {frozenset(cs) for cs in cs1}
        fs2 = {frozenset(cs) for cs in cs2}
        return fs1 == fs2
