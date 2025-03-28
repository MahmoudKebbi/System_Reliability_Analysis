import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


class SimulationVisualizer:
    """
    Visualizes results from Monte Carlo simulations
    """

    def __init__(self, simulation_results: pd.DataFrame):
        """
        Initialize with simulation results

        Args:
            simulation_results: DataFrame with simulation results
        """
        self.results = simulation_results

    def plot_reliability_over_time(
        self,
        include_confidence_interval: bool = True,
        comparison_data: Optional[pd.DataFrame] = None,
        comparison_label: str = "Analytical",
    ) -> plt.Figure:
        """
        Plot reliability over time with optional confidence intervals

        Args:
            include_confidence_interval: Whether to include confidence intervals
            comparison_data: Optional analytical data for comparison
            comparison_label: Label for comparison data

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot simulation results
        ax.plot(
            self.results["time"],
            self.results["reliability"],
            marker="o",
            linestyle="-",
            label="Monte Carlo Simulation",
        )

        # Plot confidence intervals if requested
        if include_confidence_interval:
            ax.fill_between(
                self.results["time"],
                self.results["ci_lower"],
                self.results["ci_upper"],
                alpha=0.3,
                label="95% Confidence Interval",
            )

        # Plot comparison data if provided
        if comparison_data is not None:
            ax.plot(
                comparison_data["time"],
                comparison_data["reliability"],
                marker="s",
                linestyle="--",
                color="red",
                label=comparison_label,
            )

        # Add labels and title
        ax.set_xlabel("Time")
        ax.set_ylabel("Reliability")
        ax.set_title("System Reliability Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)

        # Add legend
        ax.legend()

        # Set y-axis limits to [0, 1]
        ax.set_ylim(0, 1.05)

        return fig

    def plot_unreliability_over_time(
        self, include_confidence_interval: bool = True, log_scale: bool = False
    ) -> plt.Figure:
        """
        Plot unreliability over time

        Args:
            include_confidence_interval: Whether to include confidence intervals
            log_scale: Whether to use logarithmic scale for y-axis

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot unreliability
        ax.plot(
            self.results["time"],
            self.results["unreliability"],
            marker="o",
            linestyle="-",
            color="darkred",
            label="Unreliability (1 - Reliability)",
        )

        # Plot confidence intervals if requested
        if include_confidence_interval:
            # For unreliability, confidence intervals are reversed
            unreliability_ci_lower = 1 - self.results["ci_upper"]
            unreliability_ci_upper = 1 - self.results["ci_lower"]

            ax.fill_between(
                self.results["time"],
                unreliability_ci_lower,
                unreliability_ci_upper,
                alpha=0.3,
                color="salmon",
                label="95% Confidence Interval",
            )

        # Add labels and title
        ax.set_xlabel("Time")
        ax.set_ylabel("Unreliability")
        ax.set_title("System Unreliability Over Time")
        ax.grid(True, linestyle="--", alpha=0.7)

        # Set logarithmic scale for y-axis if requested
        if log_scale:
            ax.set_yscale("log")
            ax.set_title("System Unreliability Over Time (Log Scale)")
        else:
            # Set y-axis limits to [0, 1]
            ax.set_ylim(0, 1.05)

        # Add legend
        ax.legend()

        return fig
