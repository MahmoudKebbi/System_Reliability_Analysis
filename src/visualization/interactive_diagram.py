import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from src.models.system import SystemGraph
from src.models.components import Component, ExponentialDistribution
import json


class InteractiveSystemBuilder:
    """
    Interactive system builder using Streamlit
    """

    def __init__(self):
        self.system = SystemGraph()

    def render(self):
        """Render the interactive system builder interface"""
        st.title("Interactive Reliability System Builder")

        col1, col2 = st.columns([1, 2])

        with col1:
            self._render_component_editor()
            self._render_connection_editor()
            self._render_system_actions()

        with col2:
            self._render_system_diagram()

    def _render_component_editor(self):
        """Render the component editor section"""
        st.subheader("Add Component")

        component_id = st.text_input(
            "Component ID", value=f"C{len(self.system.components) + 1}"
        )
        component_name = st.text_input(
            "Component Name", value=f"Component {len(self.system.components) + 1}"
        )
        component_desc = st.text_area("Description", height=68)

        col1, col2 = st.columns(2)
        with col1:
            failure_rate = st.number_input(
                "Failure Rate (λ)", min_value=0.0001, value=0.01, format="%.4f"
            )

        if st.button("Add Component"):
            try:
                failure_dist = ExponentialDistribution(failure_rate)
                component = Component(
                    id=component_id,
                    name=component_name,
                    description=component_desc,
                    failure_distribution=failure_dist,
                )
                self.system.add_component(component)
                st.success(f"Added component {component_name}")
            except Exception as e:
                st.error(f"Error adding component: {str(e)}")

    def _render_connection_editor(self):
        """Render the connection editor section"""
        st.subheader("Add Connection")

        # Get all node IDs (including source and sink)
        node_ids = list(self.system.graph.nodes)

        col1, col2 = st.columns(2)
        with col1:
            from_node = st.selectbox("From", node_ids, key="from_node")
        with col2:
            to_node = st.selectbox("To", node_ids, key="to_node")

        if st.button("Add Connection"):
            try:
                self.system.add_connection(from_node, to_node)
                st.success(f"Added connection from {from_node} to {to_node}")
            except Exception as e:
                st.error(f"Error adding connection: {str(e)}")

    def _render_system_actions(self):
        """Render system actions section"""
        st.subheader("System Actions")

        if st.button("Clear System"):
            self.system = SystemGraph()
            st.success("System cleared")

        # Template systems (series, parallel, etc.)
        st.subheader("Create Template")
        template_type = st.selectbox(
            "System Template",
            [
                "Series System (3 components)",
                "Parallel System (3 components)",
                "Series-Parallel System",
                "Bridge System",
            ],
        )

        if st.button("Create Template"):
            self.system = self._create_template_system(template_type)
            st.success(f"Created {template_type}")

    def _render_system_diagram(self):
        """Render the system diagram"""
        st.subheader("System Diagram")

        # Use networkx and matplotlib for visualization
        fig, ax = plt.subplots(figsize=(10, 6))

        # Custom layout to make source and sink at opposite ends
        pos = nx.spring_layout(self.system.graph)

        # Adjust source and sink positions if they exist
        if self.system.source in pos:
            pos[self.system.source] = (-1, 0)
        if self.system.sink in pos:
            pos[self.system.sink] = (1, 0)

        # Color nodes
        node_colors = []
        for node in self.system.graph.nodes:
            if node == self.system.source:
                node_colors.append("green")
            elif node == self.system.sink:
                node_colors.append("red")
            else:
                node_colors.append("skyblue")

        # Draw the graph
        nx.draw(
            self.system.graph,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=1500,
            font_size=10,
            arrowsize=20,
            ax=ax,
        )

        # Display component count
        st.caption(
            f"System has {len(self.system.components)} components and "
            f"{len(list(self.system.graph.edges))} connections"
        )

        # Display the diagram
        st.pyplot(fig)

        # Display JSON representation
        if st.checkbox("Show System JSON"):
            system_data = {
                "components": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "failure_rate": (
                            c.failure_distribution.failure_rate
                            if hasattr(c.failure_distribution, "failure_rate")
                            else None
                        ),
                    }
                    for c in self.system.components.values()
                ],
                "connections": [
                    {"from": u, "to": v} for u, v in self.system.graph.edges
                ],
            }
            st.json(system_data)

    def _create_template_system(self, template_type: str) -> SystemGraph:
        """Create a template system based on the selected type"""
        system = SystemGraph()

        # Common failure rate for all components
        failure_rate = 0.01

        if template_type == "Series System (3 components)":
            # Add components
            for i in range(1, 4):
                component = Component(
                    id=f"C{i}",
                    name=f"Component {i}",
                    failure_distribution=ExponentialDistribution(failure_rate),
                )
                system.add_component(component)

            # Connect components in series
            system.add_connection(system.source, "C1")
            system.add_connection("C1", "C2")
            system.add_connection("C2", "C3")
            system.add_connection("C3", system.sink)

        elif template_type == "Parallel System (3 components)":
            # Add components
            for i in range(1, 4):
                component = Component(
                    id=f"C{i}",
                    name=f"Component {i}",
                    failure_distribution=ExponentialDistribution(failure_rate),
                )
                system.add_component(component)

            # Connect components in parallel
            for i in range(1, 4):
                system.add_connection(system.source, f"C{i}")
                system.add_connection(f"C{i}", system.sink)

        elif template_type == "Series-Parallel System":
            # Add components
            for i in range(1, 5):
                component = Component(
                    id=f"C{i}",
                    name=f"Component {i}",
                    failure_distribution=ExponentialDistribution(failure_rate),
                )
                system.add_component(component)

            # Connect components in series-parallel
            system.add_connection(system.source, "C1")
            system.add_connection("C1", "C2")
            system.add_connection("C1", "C3")
            system.add_connection("C2", "C4")
            system.add_connection("C3", "C4")
            system.add_connection("C4", system.sink)

        elif template_type == "Bridge System":
            # Add components
            for i in range(1, 6):
                component = Component(
                    id=f"C{i}",
                    name=f"Component {i}",
                    failure_distribution=ExponentialDistribution(failure_rate),
                )
                system.add_component(component)

            # Create bridge structure
            system.add_connection(system.source, "C1")
            system.add_connection(system.source, "C3")
            system.add_connection("C1", "C2")
            system.add_connection("C1", "C4")
            system.add_connection("C3", "C4")
            system.add_connection("C3", "C5")
            system.add_connection("C2", system.sink)
            system.add_connection("C4", "C2")
            system.add_connection("C5", system.sink)

        return system
