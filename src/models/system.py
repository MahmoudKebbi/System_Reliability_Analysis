import networkx as nx
from typing import Dict, List, Set, Optional, Tuple
import sympy as sp
from src.models.components import Component


class SystemGraph:
    """Graph-based representation of a reliability system"""

    def __init__(self):
        # Directed graph representing the system structure
        self.graph = nx.DiGraph()
        # Source and sink nodes for reliability path identification
        self.source = "source"
        self.sink = "sink"
        self.graph.add_node(self.source, type="terminal")
        self.graph.add_node(self.sink, type="terminal")
        # Component dictionary
        self.components: Dict[str, Component] = {}

    def add_component(self, component: Component) -> None:
        """Add a component to the system"""
        if component.id in self.components:
            raise ValueError(f"Component with ID {component.id} already exists")

        self.components[component.id] = component
        self.graph.add_node(component.id, type="component", name=component.name)

    def add_connection(self, from_id: str, to_id: str) -> None:
        """Add a connection between components or terminals"""
        if from_id not in self.graph:
            raise ValueError(f"Node {from_id} does not exist in the system")
        if to_id not in self.graph:
            raise ValueError(f"Node {to_id} does not exist in the system")

        self.graph.add_edge(from_id, to_id)

    def visualize(self):
        """Basic visualization of the system graph"""
        # This will be expanded in the visualization module
        import matplotlib.pyplot as plt

        pos = nx.spring_layout(self.graph)

        node_colors = []
        for node in self.graph.nodes:
            if node == self.source:
                node_colors.append("green")
            elif node == self.sink:
                node_colors.append("red")
            else:
                node_colors.append("skyblue")

        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=1500,
            arrowsize=20,
        )
        plt.title("System Reliability Graph")
        return plt.gcf()

    def get_all_paths(self) -> List[List[str]]:
        """Find all paths from source to sink"""
        return list(nx.all_simple_paths(self.graph, self.source, self.sink))

    def to_sympy_expression(self, time: float = None) -> sp.Expr:
        """Convert the system to a symbolic reliability expression"""
        # This will be expanded in the reliability calculation module
        paths = self.get_all_paths()

        # Create symbolic variables for each component
        symbols = {}
        for comp_id in self.components:
            symbols[comp_id] = sp.Symbol(f"R_{{{comp_id}}}")

        # Create reliability expression for each path
        path_expressions = []
        for path in paths:
            # Filter out source and sink
            components = [
                node for node in path if node != self.source and node != self.sink
            ]

            if not components:
                continue

            # For each path, multiply component reliabilities
            path_expr = sp.Mul(*[symbols[comp_id] for comp_id in components])
            path_expressions.append(path_expr)

        # System reliability is 1 minus the probability that all paths fail
        if not path_expressions:
            return sp.sympify(0)

        # Combine paths in parallel (1 - (1-R1)*(1-R2)*...)
        system_expr = 1 - sp.Mul(*[1 - path for path in path_expressions])

        # If time is specified, substitute component reliability values
        if time is not None:
            subs_dict = {}
            for comp_id, component in self.components.items():
                # Reliability = 1 - Probability of failure
                rel = 1 - component.probability_of_failure(time)
                subs_dict[symbols[comp_id]] = rel

            system_expr = system_expr.subs(subs_dict)

        return system_expr
