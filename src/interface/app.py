import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from src.models.system import SystemGraph
from src.models.components import Component, ExponentialDistribution
from src.algorithms.cutset.mocus import MOCUSAnalyzer
from src.algorithms.cutset.bdd import BDDAnalyzer
from src.algorithms.cutset.comparison import CutSetComparison
from src.algorithms.simulation.monte_carlo import MonteCarloSimulation
from src.algorithms.simulation.statistics import ReliabilityStatistics
from src.visualization.interactive_diagram import InteractiveSystemBuilder
from src.visualization.cutset_highlighter import CutSetVisualizer
from src.visualization.simulation_results import SimulationVisualizer
from src.algorithms.reliability.importance import ImportanceMeasures


class ReliabilityAnalyzerApp:
    """
    Main application for reliability system analysis
    """

    def __init__(self):
        # Initialize session state
        if "system" not in st.session_state:
            st.session_state.system = SystemGraph()
            st.session_state.importanceMeasures = None
        if "cut_sets" not in st.session_state:
            st.session_state.cut_sets = None
        if "simulation_results" not in st.session_state:
            st.session_state.simulation_results = None

    def render(self):
        """Render the main application"""
        st.set_page_config(
            page_title="Advanced Reliability Analysis Tool",
            page_icon="⚙️",
            layout="wide",
        )

        st.title("Advanced Reliability Analysis Tool")

        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Select Page", ["System Builder", "Cut Set Analysis", "Simulation Analysis"]
        )

        # Render selected page
        if page == "System Builder":
            self._render_system_builder()
        elif page == "Cut Set Analysis":
            self._render_cut_set_analysis()
        elif page == "Simulation Analysis":
            self._render_simulation_analysis()

    def _render_system_builder(self):
        """Render system builder page"""
        builder = InteractiveSystemBuilder()
        builder.system = st.session_state.system
        builder.render()

        # Update session state system
        st.session_state.system = builder.system

    def _render_cut_set_analysis(self):
        """Render cut set analysis page"""
        st.header("Minimal Cut Set Analysis")

        system = st.session_state.system

        if not system.components:
            st.warning("No system defined. Please build a system first.")
            return

        # Algorithm selection
        algorithm = st.radio(
            "Select Algorithm",
            ["MOCUS", "Binary Decision Diagram (BDD)", "Compare Both"],
        )

        if st.button("Calculate Minimal Cut Sets"):
            with st.spinner("Calculating minimal cut sets..."):
                try:
                    if algorithm == "MOCUS":
                        analyzer = MOCUSAnalyzer(system)
                        cut_sets = analyzer.find_minimal_cut_sets()
                    elif algorithm == "Binary Decision Diagram (BDD)":
                        analyzer = BDDAnalyzer(system)
                        cut_sets = analyzer.find_minimal_cut_sets()
                    else:  # Compare Both
                        comparison = CutSetComparison(system)
                        results = comparison.run_comparison()

                        # Show performance comparison
                        st.subheader("Algorithm Performance")

                        comp_data = {
                            "Algorithm": ["MOCUS", "BDD"],
                            "Time (seconds)": [
                                results["mocus"]["time"],
                                results["bdd"]["time"],
                            ],
                            "Cut Sets Found": [
                                results["mocus"]["count"],
                                results["bdd"]["count"],
                            ],
                        }

                        st.dataframe(pd.DataFrame(comp_data))

                        if results["match"]:
                            st.success("Both algorithms produced the same results.")
                        else:
                            st.error("Algorithms produced different results!")

                        # Use BDD results (usually more reliable for complex systems)
                        cut_sets = results["bdd"]["cut_sets"]

                    st.session_state.cut_sets = cut_sets

                    # Display cut sets
                    self._display_cut_sets(cut_sets)

                except Exception as e:
                    st.error(f"Error calculating cut sets: {str(e)}")

        # Display previously calculated cut sets
        if st.session_state.cut_sets is not None:
            if st.checkbox("Show previously calculated cut sets"):
                self._display_cut_sets(st.session_state.cut_sets)

    def _display_cut_sets(self, cut_sets):
        """Display cut sets with visualizations"""
        if not cut_sets:
            st.warning("No cut sets found.")
            return

        st.subheader(f"Found {len(cut_sets)} Minimal Cut Sets")

        # Display as list
        for i, cs in enumerate(cut_sets):
            st.write(f"{i+1}. {{{', '.join(sorted(cs))}}}")

        # Visualize cut sets
        st.subheader("Cut Set Visualization")

        system = st.session_state.system
        visualizer = CutSetVisualizer(system)

        # Limit the number of cut sets to visualize
        max_sets = min(5, len(cut_sets))
        figures = visualizer.visualize_cut_sets(cut_sets, max_sets=max_sets)

        if figures:
            for fig in figures:
                st.pyplot(fig)
                plt.close(fig)

        # Generate unreliability expression
        st.subheader("System Unreliability Expression")

        try:
            expr = self._generate_unreliability_expression(cut_sets)
            st.latex(sp.latex(expr))
            st.session_state.importanceMeasures = ImportanceMeasures(system, cut_sets)

            # Create component reliabilities dictionary (at t=1.0 as default)
            t = 1.0  # Default time point
            component_reliabilities = {}
            for comp_id, comp in system.components.items():
                if hasattr(comp.failure_distribution, "reliability"):
                    component_reliabilities[comp_id] = (
                        comp.failure_distribution.reliability(t)
                    )
                else:
                    # Default reliability if distribution doesn't have reliability method
                    component_reliabilities[comp_id] = 0.9

            # Pass component_reliabilities to the method
            reliability = st.session_state.importanceMeasures._evaluate_reliability(
                component_reliabilities
            )
            st.metric("System Reliability", f"{reliability:.4f}")
        except Exception as e:
            st.error(f"Error generating unreliability expression: {str(e)}")

    def _render_simulation_analysis(self):
        """Render simulation analysis page"""
        st.header("Monte Carlo Simulation")

        system = st.session_state.system

        if not system.components:
            st.warning("No system defined. Please build a system first.")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Simulation parameters
            st.subheader("Simulation Parameters")

            num_trials = st.number_input(
                "Number of Trials",
                min_value=100,
                max_value=1000000,
                value=10000,
                step=1000,
            )

            max_time = st.number_input(
                "Maximum Time", min_value=1.0, value=100.0, step=10.0
            )

            num_points = st.number_input(
                "Number of Time Points", min_value=5, max_value=100, value=20, step=5
            )

        with col2:
            # System information
            st.subheader("System Information")

            st.write(f"Number of components: {len(system.components)}")
            st.write(f"Number of paths: {len(system.get_all_paths())}")

            # Component failure rates table
            comp_data = {"ID": [], "Name": [], "Failure Rate": []}

            for comp_id, comp in system.components.items():
                comp_data["ID"].append(comp_id)
                comp_data["Name"].append(comp.name)

                if hasattr(comp.failure_distribution, "failure_rate"):
                    comp_data["Failure Rate"].append(
                        comp.failure_distribution.failure_rate
                    )
                else:
                    comp_data["Failure Rate"].append("N/A")

            st.dataframe(pd.DataFrame(comp_data))

        # Run simulation button
        if st.button("Run Monte Carlo Simulation"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(time_point, percent):
                progress_bar.progress(int(percent) / 100)
                status_text.text(
                    f"Simulating time point {time_point:.2f}... {percent:.1f}%"
                )

            with st.spinner("Running simulation..."):
                try:
                    # Generate time points
                    time_points = np.linspace(0.1, max_time, num=num_points)

                    # Run simulation
                    simulator = MonteCarloSimulation(system)
                    results = simulator.simulate(
                        time_points.tolist(),
                        num_trials=num_trials,
                        progress_callback=update_progress,
                    )

                    # Store results in session state
                    st.session_state.simulation_results = results

                    # Clear progress indicators
                    status_text.empty()

                    st.success("Simulation completed!")

                    # Display results
                    self._display_simulation_results(results)
                except Exception as e:
                    st.error(f"Error during simulation: {str(e)}")

        # Display previously run simulation results
        if st.session_state.simulation_results is not None:
            if st.checkbox("Show previous simulation results"):
                self._display_simulation_results(st.session_state.simulation_results)

    def _display_simulation_results(self, results):
        """Display simulation results"""
        st.subheader("Simulation Results")

        # Tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(
            ["Reliability Plot", "Unreliability Plot", "Statistics"]
        )

        visualizer = SimulationVisualizer(results)

        with tab1:
            # Reliability plot
            include_ci = st.checkbox(
                "Include Confidence Intervals", value=True, key="rel_ci"
            )

            fig = visualizer.plot_reliability_over_time(
                include_confidence_interval=include_ci
            )
            st.pyplot(fig)
            plt.close(fig)

            # Show data table
            if st.checkbox("Show Data Table", key="rel_table"):
                st.dataframe(results[["time", "reliability", "ci_lower", "ci_upper"]])

        with tab2:
            # Unreliability plot
            include_ci = st.checkbox(
                "Include Confidence Intervals", value=True, key="unrel_ci"
            )
            log_scale = st.checkbox("Use Logarithmic Scale", value=False)

            fig = visualizer.plot_unreliability_over_time(
                include_confidence_interval=include_ci, log_scale=log_scale
            )
            st.pyplot(fig)
            plt.close(fig)

            # Show data table
            if st.checkbox("Show Data Table", key="unrel_table"):
                st.dataframe(results[["time", "unreliability"]])

        with tab3:
            # Statistics
            stats = ReliabilityStatistics(results)
            summary = stats.reliability_summary()

            st.subheader("Reliability Statistics")

            # Display MTTF
            st.metric("Mean Time To Failure (MTTF)", f"{summary['mttf']:.4f}")

            # Display time to reach reliability thresholds
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Time to 90% Reliability", summary.get("time_to_90%", "N/A"))

            with col2:
                st.metric("Time to 50% Reliability", summary.get("time_to_50%", "N/A"))

            with col3:
                st.metric("Time to 10% Reliability", summary.get("time_to_10%", "N/A"))

            # Display full summary
            st.subheader("Full Summary")
            st.json(summary)

    def _generate_unreliability_expression(self, cut_sets):
        """Generate unreliability expression from minimal cut sets"""
        # Create symbolic variables for each component
        system = st.session_state.system
        symbols = {}
        for comp_id in system.components:
            # Use component failure probability symbols
            symbols[comp_id] = sp.Symbol(f"q_{{{comp_id}}}")

        # For each cut set, multiply component failure probabilities
        cut_set_exprs = []
        for cs in cut_sets:
            if not cs:  # Skip empty cut sets
                continue

            # Multiply probabilities within a cut set
            cs_expr = sp.Mul(*[symbols[comp_id] for comp_id in cs])
            cut_set_exprs.append(cs_expr)

        if not cut_set_exprs:
            return sp.sympify(0)

        # Use inclusion-exclusion principle for accurate calculation
        return self._inclusion_exclusion(cut_set_exprs)

    def _inclusion_exclusion(self, exprs):
        """
        Apply the inclusion-exclusion principle to calculate
        the probability of the union of events
        """
        if not exprs:
            return sp.sympify(0)

        n = len(exprs)

        # We'll use this to store our result
        result = sp.sympify(0)

        # For each size k of intersections
        for k in range(1, n + 1):
            # Get all combinations of size k
            from itertools import combinations

            term_sign = (-1) ** (k - 1)

            for combo in combinations(exprs, k):
                # Calculate the intersection of these events (multiply them)
                intersection = sp.sympify(1)

                # Track which variables we've seen to avoid duplicating them
                seen_vars = set()

                for expr in combo:
                    # For each factor in the expression
                    if isinstance(expr, sp.Mul):
                        for factor in expr.args:
                            if factor.is_Symbol and factor not in seen_vars:
                                intersection *= factor
                                seen_vars.add(factor)
                    elif expr.is_Symbol and expr not in seen_vars:
                        intersection *= expr
                        seen_vars.add(expr)

                # Add or subtract this term according to inclusion-exclusion principle
                result += term_sign * intersection

        return result


def main():
    app = ReliabilityAnalyzerApp()
    app.render()


if __name__ == "__main__":
    main()
