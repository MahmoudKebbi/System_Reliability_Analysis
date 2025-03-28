import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Set, Dict
import streamlit as st
import random
import colorsys
from src.models.system import SystemGraph


class CutSetVisualizer:
    """
    Visualizes minimal cut sets on the system diagram
    """

    def __init__(self, system: SystemGraph):
        self.system = system

    def visualize_cut_sets(self, cut_sets: List[Set[str]], max_sets: int = 5):
        """
        Create visualizations for minimal cut sets

        Args:
            cut_sets: List of minimal cut sets
            max_sets: Maximum number of cut sets to visualize

        Returns:
            List of matplotlib figures
        """
        if not cut_sets:
            return []

        # Limit the number of cut sets to display
        display_sets = cut_sets[:max_sets]

        figures = []

        # Generate distinct colors for different cut sets
        colors = self._generate_colors(len(display_sets))

        # First, create a figure showing all cut sets together
        fig_all = plt.figure(figsize=(12, 8))
        ax_all = fig_all.add_subplot(111)
        self._draw_system_with_highlighted_components(
            ax_all,
            {i: cs for i, cs in enumerate(display_sets)},
            colors,
            title="All Minimal Cut Sets",
        )
        figures.append(fig_all)

        # Then create individual figures for each cut set
        for i, cs in enumerate(display_sets):
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            self._draw_system_with_highlighted_components(
                ax,
                {i: cs},
                {i: colors[i]},
                title=f"Minimal Cut Set {i+1}: {', '.join(sorted(cs))}",
            )
            figures.append(fig)

        return figures

    def _draw_system_with_highlighted_components(
        self, ax, cut_sets_dict, colors, title=None
    ):
        """
        Draw system graph with highlighted components

        Args:
            ax: Matplotlib axis
            cut_sets_dict: Dictionary mapping cut set index to component set
            colors: Dictionary mapping cut set index to color
            title: Optional title for the plot
        """
        # Spring layout with fixed source and sink positions
        pos = nx.spring_layout(self.system.graph)

        # Adjust source and sink positions
        pos[self.system.source] = (-1, 0)
        pos[self.system.sink] = (1, 0)

        # Draw all edges
        nx.draw_networkx_edges(self.system.graph, pos, ax=ax, alpha=0.7)

        # Draw nodes with default coloring
        node_colors = {}
        for node in self.system.graph.nodes:
            if node == self.system.source:
                node_colors[node] = "green"
            elif node == self.system.sink:
                node_colors[node] = "red"
            else:
                # Check if node is in any cut set
                in_cut_set = False
                for i, cs in cut_sets_dict.items():
                    if node in cs:
                        # Use the color of the first cut set containing this node
                        node_colors[node] = colors[i]
                        in_cut_set = True
                        break

                if not in_cut_set:
                    node_colors[node] = "skyblue"

        # Draw nodes with custom colors
        for node, color in node_colors.items():
            nx.draw_networkx_nodes(
                self.system.graph,
                pos,
                nodelist=[node],
                node_color=[color],
                node_size=1500,
                ax=ax,
            )

        # Draw labels
        nx.draw_networkx_labels(self.system.graph, pos, font_size=10, ax=ax)

        # Add legend for cut sets
        legend_elements = []
        import matplotlib.patches as mpatches

        for i, cs in cut_sets_dict.items():
            legend_elements.append(
                mpatches.Patch(
                    color=colors[i], label=f"Cut Set {i+1}: {', '.join(sorted(cs))}"
                )
            )

        ax.legend(
            handles=legend_elements, loc="upper center", bbox_to_anchor=(0.5, 0), ncol=1
        )

        if title:
            ax.set_title(title)

        ax.axis("off")

    def _generate_colors(self, n: int) -> Dict[int, str]:
        """
        Generate n distinct colors

        Args:
            n: Number of colors to generate

        Returns:
            Dictionary mapping indices to hex color strings
        """
        colors = {}
        for i in range(n):
            # Use HSV color space to generate evenly spaced colors
            h = i / n
            s = 0.7
            v = 0.9
            r, g, b = colorsys.hsv_to_rgb(h, s, v)

            # Convert to hex
            hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            colors[i] = hex_color

        return colors
