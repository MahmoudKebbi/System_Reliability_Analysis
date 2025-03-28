import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from src.models.system import SystemGraph


class ReliabilityStatistics:
    """
    Statistical analysis of reliability simulation results
    """

    def __init__(self, simulation_results: pd.DataFrame):
        """
        Initialize with simulation results dataframe

        Args:
            simulation_results: DataFrame with simulation results
        """
        self.results = simulation_results

    def mean_time_to_failure(self) -> float:
        """
        Calculate Mean Time To Failure (MTTF)

        Returns:
            MTTF estimate
        """
        # Numerical integration using the trapezoidal rule
        times = self.results["time"].values
        reliability = self.results["reliability"].values

        if len(times) < 2:
            return 0.0

        # Calculate MTTF = integral of R(t) dt
        mttf = np.trapz(reliability, times)
        return mttf

    def availability(self, time_point: float) -> float:
        """
        Calculate system availability at a specific time

        Args:
            time_point: Time to calculate availability

        Returns:
            Availability estimate
        """
        # If exact time point exists, return its reliability
        if time_point in self.results["time"].values:
            return self.results.loc[
                self.results["time"] == time_point, "reliability"
            ].iloc[0]

        # Otherwise interpolate
        idx = np.searchsorted(self.results["time"].values, time_point)

        # If time_point is beyond our simulation range
        if idx == 0:
            return self.results["reliability"].iloc[0]
        if idx == len(self.results):
            return self.results["reliability"].iloc[-1]

        # Linear interpolation between two closest points
        t1 = self.results["time"].iloc[idx - 1]
        t2 = self.results["time"].iloc[idx]
        r1 = self.results["reliability"].iloc[idx - 1]
        r2 = self.results["reliability"].iloc[idx]

        # Linear interpolation formula
        return r1 + (r2 - r1) * (time_point - t1) / (t2 - t1)

    def reliability_summary(self) -> Dict:
        """
        Generate a summary of reliability statistics

        Returns:
            Dictionary with reliability metrics
        """
        if len(self.results) == 0:
            return {}

        mttf = self.mean_time_to_failure()

        # Find time at which reliability falls below certain thresholds
        thresholds = [0.9, 0.5, 0.1]
        threshold_times = {}

        for threshold in thresholds:
            # Find first time where reliability falls below threshold
            below_threshold = self.results[self.results["reliability"] <= threshold]
            if len(below_threshold) > 0:
                threshold_times[f"time_to_{int(threshold * 100)}%"] = below_threshold[
                    "time"
                ].iloc[0]
            else:
                threshold_times[f"time_to_{int(threshold * 100)}%"] = (
                    "Beyond simulation range"
                )

        summary = {
            "mttf": mttf,
            "max_time": self.results["time"].max(),
            "min_reliability": self.results["reliability"].min(),
            **threshold_times,
        }

        return summary
