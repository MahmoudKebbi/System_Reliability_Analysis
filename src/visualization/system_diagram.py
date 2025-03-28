"""
Basic system diagram visualization for reliability systems.
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import Optional, Dict, Any, Tuple
import numpy as np
from src.models.system import SystemGraph


class SystemDiagram:
    """
    Basic visualization for reliability system diagrams.
    """

    def __init__(self, system: SystemGraph):
        """
        Initialize with system.

        Args:
            system: The reliability system to visualize
        """
        self.system = system

    def draw(
        self,
        figsize: Tuple[int, int] = (10, 6),
        node_size: int = 1500,
        font_size: int = 10,
        with_labels: bool = True,
        **kwargs,
    ) -> plt.Figure:
        """
        Draw the system diagram.

        Args:
            figsize: Figure size as (width, height)
            node_size: Size of nodes
            font_size: Font size for labels
            with_labels: Whether to draw node labels
            **kwargs: Additional arguments for drawing

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Create a spring layout with source and sink at fixed positions
        pos = self._get_layout()

        # Set node colors based on node type
        node_colors = self._get_node_colors()

        # Draw the graph
        nx.draw(
            self.system.graph,
            pos,
            ax=ax,
            with_labels=with_labels,
            node_color=node_colors,
            node_size=node_size,
            font_size=font_size,
            arrows=True,
            arrowsize=15,
            **kwargs,
        )

        # Set title
        if hasattr(self.system, "name") and self.system.name:
            title = f"System: {self.system.name}"
        else:
            title = "Reliability System Diagram"

        ax.set_title(title)

        # Add legend
        import matplotlib.patches as mpatches

        legend_elements = [
            mpatches.Patch(color="green", label="Source"),
            mpatches.Patch(color="red", label="Sink"),
            mpatches.Patch(color="skyblue", label="Component"),
        ]
        ax.legend(handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, 0))

        ax.axis("off")

        return fig

    def _get_layout(self) -> Dict[str, np.ndarray]:
        """
        Get node layout for the graph.

        Returns:
            Dictionary mapping node IDs to positions
        """
        # Start with spring layout
        pos = nx.spring_layout(self.system.graph)

        # Put source on left, sink on right
        if self.system.source in pos:
            pos[self.system.source] = np.array([-1.0, 0.0])
        if self.system.sink in pos:
            pos[self.system.sink] = np.array([1.0, 0.0])

        return pos

    def _get_node_colors(self) -> list:
        """
        Get colors for each node.

        Returns:
            List of colors in the same order as graph.nodes
        """
        colors = []
        for node in self.system.graph.nodes:
            if node == self.system.source:
                colors.append("green")
            elif node == self.system.sink:
                colors.append("red")
            else:
                colors.append("skyblue")

        return colors
