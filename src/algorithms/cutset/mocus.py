from typing import List, Set, Dict, FrozenSet
import networkx as nx
from src.models.system import SystemGraph


class MOCUSAnalyzer:
    """
    Implements the Method of Obtaining Cut Sets (MOCUS) algorithm
    for reliability system analysis.
    """

    def __init__(self, system: SystemGraph):
        self.system = system

    def find_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Find all minimal cut sets in the system.

        A cut set is a set of components that, when removed,
        disconnects all paths from source to sink.

        Returns:
            List of minimal cut sets, where each cut set is a set of component IDs
        """
        # Get all paths from source to sink
        paths = self.system.get_all_paths()

        # Filter out source and sink from paths
        component_paths = []
        for path in paths:
            component_path = [
                node
                for node in path
                if node != self.system.source and node != self.system.sink
            ]
            if component_path:  # Only add non-empty paths
                component_paths.append(component_path)

        if not component_paths:
            return []

        # Start with the first path as initial cut sets
        cut_sets = [{comp} for comp in component_paths[0]]

        # Process each remaining path
        for path in component_paths[1:]:
            new_cut_sets = []
            # For each existing cut set
            for cs in cut_sets:
                # For each component in the current path
                for comp in path:
                    # Create a new cut set by adding this component
                    new_cs = cs.copy()
                    new_cs.add(comp)
                    new_cut_sets.append(new_cs)
            cut_sets = new_cut_sets

        # Remove non-minimal cut sets
        minimal_cut_sets = self._remove_non_minimal(cut_sets)
        return minimal_cut_sets

    def _remove_non_minimal(self, cut_sets: List[Set[str]]) -> List[Set[str]]:
        """Remove non-minimal cut sets"""
        # Convert to frozenset for hashability and sort by size
        fs_cut_sets = [frozenset(cs) for cs in cut_sets]
        fs_cut_sets.sort(key=len)

        # Use a set for O(1) lookups
        minimal_cs = set()
        for cs in fs_cut_sets:
            # Check if this set is a superset of any already-found minimal cut set
            if not any(minimal.issubset(cs) for minimal in minimal_cs):
                minimal_cs.add(cs)

        # Convert back to list of sets
        return [set(cs) for cs in minimal_cs]
