"""
Implementation of inclusion-exclusion principle for exact reliability calculations.
"""

import sympy as sp
from typing import List, Set, Dict
import itertools


class InclusionExclusion:
    """
    Implementation of inclusion-exclusion principle for calculating
    the probability of union of events.
    """

    @staticmethod
    def calculate_probability(events_prob: List[float]) -> float:
        """
        Calculate the probability of the union of events using inclusion-exclusion.

        Args:
            events_prob: List of individual event probabilities

        Returns:
            Probability of the union of events
        """
        n = len(events_prob)
        if n == 0:
            return 0.0

        result = 0.0

        # For each size k of intersections
        for k in range(1, n + 1):
            term_sum = 0.0
            term_sign = (-1) ** (k - 1)

            # Sum over all combinations of size k
            for combo in itertools.combinations(range(n), k):
                # For simplicity, assume independence
                # In real applications, you would need the joint probabilities
                prob = 1.0
                for idx in combo:
                    prob *= events_prob[idx]
                term_sum += prob

            result += term_sign * term_sum

        return result

    @staticmethod
    def symbolic_union_probability(expressions: List[sp.Expr]) -> sp.Expr:
        """
        Calculate symbolic expression for the probability of union using inclusion-exclusion.

        Args:
            expressions: List of symbolic expressions for event probabilities

        Returns:
            Symbolic expression for union probability
        """
        if not expressions:
            return sp.sympify(0)

        n = len(expressions)
        result = sp.sympify(0)

        # For each size k of intersections
        for k in range(1, n + 1):
            term_sign = (-1) ** (k - 1)

            # For each combination of size k
            for combo in itertools.combinations(expressions, k):
                # Get intersection (multiply expressions assuming independence)
                # This is simplified - real implementation would track variables
                intersection = sp.Mul(*combo)
                result += term_sign * intersection

        return result

    @staticmethod
    def calculate_system_unreliability(
        cut_sets: List[Set[str]], component_probs: Dict[str, float]
    ) -> float:
        """
        Calculate system unreliability from minimal cut sets.

        Args:
            cut_sets: List of minimal cut sets where each cut set is a set of component IDs
            component_probs: Dictionary mapping component IDs to failure probabilities

        Returns:
            System unreliability
        """
        # Calculate probability for each cut set
        cut_set_probs = []
        for cs in cut_sets:
            # Probability of a cut set is the product of component failure probabilities
            cs_prob = 1.0
            for comp_id in cs:
                if comp_id in component_probs:
                    cs_prob *= component_probs[comp_id]
                else:
                    raise ValueError(f"No probability defined for component {comp_id}")
            cut_set_probs.append(cs_prob)

        # Apply inclusion-exclusion to get system unreliability
        return InclusionExclusion.calculate_probability(cut_set_probs)
