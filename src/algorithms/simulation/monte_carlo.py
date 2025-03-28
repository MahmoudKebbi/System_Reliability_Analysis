import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Set, Optional
import time
from src.models.system import SystemGraph


class MonteCarloSimulation:
    """
    Monte Carlo simulation engine for reliability analysis
    """

    def __init__(self, system: SystemGraph):
        self.system = system

    def simulate(
        self, time_points: List[float], num_trials: int = 10000, progress_callback=None
    ) -> pd.DataFrame:
        """
        Run Monte Carlo simulation to estimate system reliability

        Args:
            time_points: List of time points to evaluate
            num_trials: Number of simulation trials
            progress_callback: Optional callback for reporting progress

        Returns:
            DataFrame with simulation results
        """
        results = []

        # Get all paths from source to sink
        all_paths = self.system.get_all_paths()
        # Extract only component IDs from paths
        paths = []
        for path in all_paths:
            components = [
                node
                for node in path
                if node != self.system.source and node != self.system.sink
            ]
            if components:
                paths.append(components)

        if not paths:
            raise ValueError("System has no valid paths")

        # For each time point
        for time_point in time_points:
            # Generate failure times for all components for all trials
            failure_times = {}
            for comp_id, component in self.system.components.items():
                if component.failure_distribution is None:
                    raise ValueError(f"Component {comp_id} has no failure distribution")
                # Generate random failure times
                failure_times[comp_id] = (
                    component.failure_distribution.random_failure_time(num_trials)
                )

            # Count system failures
            failure_count = 0

            for trial in range(num_trials):
                # Check if all paths have at least one failed component
                system_failed = True

                for path in paths:
                    path_working = True
                    for comp_id in path:
                        # If component fails before time_point, path is broken
                        if failure_times[comp_id][trial] <= time_point:
                            path_working = False
                            break

                    if path_working:
                        # If at least one path works, system works
                        system_failed = False
                        break

                if system_failed:
                    failure_count += 1

                # Report progress if callback provided
                if progress_callback and trial % (num_trials // 100) == 0:
                    progress_callback(time_point, trial / num_trials * 100)

            # Calculate reliability and confidence interval
            reliability = 1 - (failure_count / num_trials)
            # 95% confidence interval using binomial proportion confidence interval
            margin = 1.96 * np.sqrt((reliability * (1 - reliability)) / num_trials)

            results.append(
                {
                    "time": time_point,
                    "reliability": reliability,
                    "unreliability": 1 - reliability,
                    "ci_lower": max(0, reliability - margin),
                    "ci_upper": min(1, reliability + margin),
                    "trials": num_trials,
                    "failures": failure_count,
                }
            )

        return pd.DataFrame(results)
