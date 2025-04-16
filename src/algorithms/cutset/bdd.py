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

        # Optimize variable ordering based on component connectivity
        # More connected components should be higher in the order
        self._optimize_variable_ordering()

    def _optimize_variable_ordering(self):
        """Optimize BDD variable ordering based on component connectivity"""
        try:
            # Count connections for each component
            connectivity = {}
            for comp_id in self.system.components:
                # Count incoming and outgoing edges
                in_degree = len(list(self.system.graph.predecessors(comp_id)))
                out_degree = len(list(self.system.graph.successors(comp_id)))
                connectivity[comp_id] = in_degree + out_degree

            # Order variables by connectivity (highest first)
            ordered_vars = sorted(
                connectivity.keys(), key=lambda x: connectivity.get(x, 0), reverse=True
            )

            # Set the ordering in the BDD manager
            self.bdd_manager.reorder(ordered_vars)
        except Exception as e:
            print(f"Warning: Could not optimize variable ordering: {e}")

    def find_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Find all minimal cut sets using BDD approach.

        Returns:
            List of minimal cut sets, where each cut set is a set of component IDs
        """
        # Check for direct source-sink connection first
        try:
            if self.system.sink in self.system.graph.successors(self.system.source):
                print("BDD: Direct source-to-sink connection detected!")
                return []  # Perfect reliability - no cut sets
        except Exception as e:
            print(f"BDD: Error checking direct connections: {e}")

        # Get all paths
        paths = self.system.get_all_paths()
        if not paths:
            return []

        # Create BDD for system structure function
        structure_function = self._create_structure_function(paths)

        # Find minimal cut sets from BDD
        min_cut_sets = self._extract_minimal_cut_sets(structure_function)

        return min_cut_sets

    def _create_structure_function(self, paths: List[List[str]]) -> _bdd.Function:
        """Create BDD for system structure function"""
        # Initialize with direct source-sink detection
        has_direct_path = False

        # For each path, create a function representing path success
        path_functions = []
        for path in paths:
            # Check if this is a direct source-sink path
            if len(path) == 2:  # Just source and sink
                has_direct_path = True
                continue

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

        # Special case: if there's a direct path, system cannot fail
        if has_direct_path:
            return self.bdd_manager.false  # No failure scenarios

        # Special case: if no path functions, the system always fails
        if not path_functions:
            return self.bdd_manager.true  # Always fails

        # System success requires at least one path to work (OR)
        system_func = self.bdd_manager.false
        for path_func in path_functions:
            system_func = self.bdd_manager.apply("or", system_func, path_func)

        # Get the system failure function (complement)
        failure_func = self.bdd_manager.apply("not", system_func)

        return failure_func

    def _extract_minimal_cut_sets(self, failure_func: _bdd.Function) -> List[Set[str]]:
        """Extract minimal cut sets from BDD failure function"""
        # If system can't fail, return empty list
        if failure_func == self.bdd_manager.false:
            return []

        # If system always fails, special case
        if failure_func == self.bdd_manager.true:
            return [
                set()
            ]  # Empty cut set means system fails without component failures

        # Get paths to terminal 1 (failure) in the BDD
        paths = list(self.bdd_manager.pick_iter(failure_func))

        if not paths:
            return []

        # Extract cut sets from paths
        cut_sets = []
        for path in paths:
            cut_set = set()
            for var, val in path.items():
                # In a cut set, we include components that are failed (0)
                if val == 0:
                    cut_set.add(var)
            cut_sets.append(cut_set)

        # More efficient minimization algorithm
        return self._minimize_cut_sets(cut_sets)

    def _minimize_cut_sets(self, cut_sets: List[Set[str]]) -> List[Set[str]]:
        """More efficient algorithm to find minimal cut sets"""
        if not cut_sets:
            return []

        # Sort by size for efficiency (check smaller sets first)
        cut_sets.sort(key=len)

        minimal_cs = []
        for i, cs in enumerate(cut_sets):
            # Skip if this set is already known to be non-minimal
            if any(existing_cs.issubset(cs) for existing_cs in minimal_cs):
                continue

            # Check if this set is a subset of any remaining sets
            is_minimal = True
            for j in range(i + 1, len(cut_sets)):
                # If this set is a subset of a larger set, mark the larger as non-minimal
                if cs.issubset(cut_sets[j]):
                    is_minimal = True
                    # No need to check other sets
                    break

            if is_minimal:
                minimal_cs.append(cs)

        return minimal_cs
