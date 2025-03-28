import networkx as nx
from typing import List, Set, Dict, Tuple, Optional
from src.models.system import SystemGraph
import dd.autoref as _bdd  # Using the 'dd' package for BDDs


class BDDAnalyzer:
    """
    Implements Binary Decision Diagram (BDD) approach for finding
    minimal cut sets in reliability systems.
    """

    def __init__(self, system: SystemGraph):
        self.system = system
        self.bdd_manager = _bdd.BDD()
        # Create variables for each component
        for comp_id in self.system.components:
            self.bdd_manager.declare(comp_id)

    def find_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Find all minimal cut sets using BDD approach.

        Returns:
            List of minimal cut sets, where each cut set is a set of component IDs
        """
        # Get all paths
        paths = self.system.get_all_paths()

        # Create BDD for system structure function
        structure_function = self._create_structure_function(paths)

        # Find minimal cut sets from BDD
        min_cut_sets = self._extract_minimal_cut_sets(structure_function)

        return min_cut_sets

    def _create_structure_function(self, paths: List[List[str]]) -> _bdd.Function:
        """Create BDD for system structure function"""
        # For each path, create a function representing path success
        path_functions = []
        for path in paths:
            # Filter out source and sink nodes
            components = [
                node
                for node in path
                if node != self.system.source and node != self.system.sink
            ]

            if not components:
                continue

            # Success of a path requires all components to work
            path_func = self.bdd_manager.true
            for comp in components:
                # In a BDD, variables represent component working state
                path_func = self.bdd_manager.apply(
                    "and", path_func, self.bdd_manager.var(comp)
                )

            path_functions.append(path_func)

        if not path_functions:
            return self.bdd_manager.false

        # System success requires at least one path to work (OR)
        system_func = self.bdd_manager.false
        for path_func in path_functions:
            system_func = self.bdd_manager.apply("or", system_func, path_func)

        # Get the system failure function (complement)
        failure_func = self.bdd_manager.apply("not", system_func)

        return failure_func

    def _extract_minimal_cut_sets(self, failure_func: _bdd.Function) -> List[Set[str]]:
        """Extract minimal cut sets from BDD failure function"""
        # Get paths to terminal 1 (failure) in the BDD
        paths = self.bdd_manager.pick_iter(failure_func)

        cut_sets = []
        for path in paths:
            cut_set = set()
            for var, val in path.items():
                # In a cut set, we include components that are failed (0)
                if val == 0:
                    cut_set.add(var)
            cut_sets.append(cut_set)

        # Remove non-minimal cut sets
        minimal_cs = []
        for cs in cut_sets:
            if not any(cs1.issubset(cs) for cs1 in minimal_cs if cs1 != cs):
                minimal_cs.append(cs)

        return minimal_cs
