import uuid
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np


class FailureDistribution:
    """Base class for component failure distributions"""

    def probability_of_failure(self, time: float) -> float:
        """Calculate probability of failure at given time"""
        raise NotImplementedError("Subclasses must implement this method")

    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times based on distribution"""
        raise NotImplementedError("Subclasses must implement this method")


class ExponentialDistribution(FailureDistribution):
    """Exponential failure distribution with constant failure rate"""

    def __init__(self, failure_rate: float):
        """
        Args:
            failure_rate: Constant failure rate (λ)
        """
        self.failure_rate = failure_rate

    def probability_of_failure(self, time: float) -> float:
        """F(t) = 1 - exp(-λt)"""
        return 1 - np.exp(-self.failure_rate * time)

    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times"""
        return np.random.exponential(1 / self.failure_rate, size=size)


@dataclass
class Component:
    """Representation of a system component"""

    id: str
    name: str
    description: Optional[str] = None
    failure_distribution: Optional[FailureDistribution] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def probability_of_failure(self, time: float) -> float:
        """Calculate probability of failure at a given time"""
        if self.failure_distribution is None:
            raise ValueError(f"Component {self.id} has no failure distribution defined")
        return self.failure_distribution.probability_of_failure(time)
