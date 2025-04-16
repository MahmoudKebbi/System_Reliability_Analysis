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
        # First check for direct connection between source and sink
        direct_connection = False

        # Check if there's a direct source-to-sink connection
        try:
            if self.system.sink in self.system.graph.successors(self.system.source):
                print("Direct source-to-sink connection detected!")
                direct_connection = True
        except Exception as e:
            # Handle any potential exceptions with graph access
            print(f"Error checking direct connections: {str(e)}")

        if direct_connection:
            # For a system with a direct connection, return an empty list
            return []

        # Get all paths from source to sink
        paths = self.system.get_all_paths()

        # Filter paths that are just direct source-to-sink connections
        paths = [path for path in paths if len(path) > 2]

        if not paths:
            # If only direct paths exist, return empty list indicating perfect reliability
            return []

        # Identify perfectly reliable components (0 failure rate)
        perfectly_reliable_comps = set()
        for comp_id, comp in self.system.components.items():
            if hasattr(comp.failure_distribution, "failure_rate"):
                if comp.failure_distribution.failure_rate == 0:
                    perfectly_reliable_comps.add(comp_id)

        # Filter out source, sink, and perfectly reliable components from paths
        component_paths = []
        for path in paths:
            component_path = [
                node
                for node in path
                if (
                    node != self.system.source
                    and node != self.system.sink
                    and node not in perfectly_reliable_comps
                )
            ]
            if component_path:  # Only add non-empty paths
                component_paths.append(component_path)

        if not component_paths:
            # If all paths have only perfectly reliable components, system is perfectly reliable
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
