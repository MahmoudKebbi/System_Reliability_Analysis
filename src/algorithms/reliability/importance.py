"""
Implementation of component importance measures for reliability analysis.
"""

import numpy as np
from typing import Dict, List, Set
from src.models.system import SystemGraph


class ImportanceMeasures:
    """
    Calculate various importance measures for components in a reliability system.
    """

    def __init__(self, system: SystemGraph, cut_sets: List[Set[str]]):
        """
        Initialize with system and its minimal cut sets.

        Args:
            system: The reliability system
            cut_sets: List of minimal cut sets
        """
        self.system = system
        self.cut_sets = cut_sets

    def birnbaum_importance(self, time: float) -> Dict[str, float]:
        """
        Calculate Birnbaum importance for each component.

        Birnbaum importance = ∂R/∂ri = P(system works | component i works) -
                                       P(system works | component i fails)

        Args:
            time: Time point for calculation

        Returns:
            Dictionary mapping component IDs to Birnbaum importance values
        """
        result = {}

        for comp_id in self.system.components:
            # Calculate system reliability with component working (ri = 1)
            working_probs = {}
            for c_id in self.system.components:
                if c_id == comp_id:
                    working_probs[c_id] = 1.0
                else:
                    working_probs[c_id] = 1.0 - self.system.components[
                        c_id
                    ].probability_of_failure(time)

            # Use symbolic expression for reliability calculation
            rel_working = self._evaluate_reliability(working_probs)

            # Calculate system reliability with component failed (ri = 0)
            failed_probs = working_probs.copy()
            failed_probs[comp_id] = 0.0
            rel_failed = self._evaluate_reliability(failed_probs)

            # Birnbaum importance is the difference
            result[comp_id] = rel_working - rel_failed

        return result

    def criticality_importance(self, time: float) -> Dict[str, float]:
        """
        Calculate Criticality importance for each component.

        Criticality importance = Birnbaum importance * component unreliability / system unreliability

        Args:
            time: Time point for calculation

        Returns:
            Dictionary mapping component IDs to Criticality importance values
        """
        # First, calculate Birnbaum importances
        birnbaum = self.birnbaum_importance(time)

        # Calculate component unreliabilities
        comp_unreliabilities = {}
        for comp_id, component in self.system.components.items():
            comp_unreliabilities[comp_id] = component.probability_of_failure(time)

        # Calculate system unreliability
        sys_probs = {
            c_id: 1.0 - comp_unreliabilities[c_id] for c_id in self.system.components
        }
        system_reliability = self._evaluate_reliability(sys_probs)
        system_unreliability = 1.0 - system_reliability

        # Calculate criticality importance
        result = {}
        for comp_id in self.system.components:
            if abs(system_unreliability) < 1e-10:  # Avoid division by zero
                result[comp_id] = 0.0
            else:
                result[comp_id] = (
                    birnbaum[comp_id]
                    * comp_unreliabilities[comp_id]
                    / system_unreliability
                )

        return result

    def _evaluate_reliability(self, component_reliabilities: Dict[str, float]) -> float:
        """
        Evaluate system reliability given component reliabilities.

        This is a simplified implementation. For a more accurate calculation,
        use the system's symbolic expression or cut set based evaluation.

        Args:
            component_reliabilities: Dictionary mapping component IDs to reliabilities

        Returns:
            System reliability
        """
        # Convert to component failure probabilities
        component_probs = {
            c_id: 1.0 - rel for c_id, rel in component_reliabilities.items()
        }

        # Calculate probability for each cut set
        cut_set_probs = []
        for cs in self.cut_sets:
            # Probability of a cut set is the product of component failure probabilities
            cs_prob = 1.0
            for comp_id in cs:
                if comp_id in component_probs:
                    cs_prob *= component_probs[comp_id]
                else:
                    cs_prob = (
                        0.0  # Component not in dict means we assume it always works
                    )
            cut_set_probs.append(cs_prob)

        # Apply inclusion-exclusion to get system unreliability
        from src.algorithms.reliability.inclusion_exclusion import InclusionExclusion

        system_unreliability = InclusionExclusion.calculate_probability(cut_set_probs)

        # Return system reliability
        return 1.0 - system_unreliability
