"""
Various failure distribution models for reliability analysis.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional


class FailureDistribution(ABC):
    """Base abstract class for component failure distributions"""

    @abstractmethod
    def probability_of_failure(self, time: float) -> float:
        """Calculate probability of failure at given time"""
        pass

    @abstractmethod
    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times based on distribution"""
        pass

    @abstractmethod
    def hazard_rate(self, time: float) -> float:
        """Calculate hazard rate (failure rate) at given time"""
        pass


class ExponentialDistribution(FailureDistribution):
    """Exponential failure distribution with constant failure rate"""

    def __init__(self, failure_rate: float):
        """
        Args:
            failure_rate: Constant failure rate (λ)
        """
        if failure_rate <= 0:
            raise ValueError("Failure rate must be positive")
        self.failure_rate = failure_rate

    def probability_of_failure(self, time: float) -> float:
        """F(t) = 1 - exp(-λt)"""
        return 1 - np.exp(-self.failure_rate * time)

    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times"""
        return np.random.exponential(1 / self.failure_rate, size=size)

    def hazard_rate(self, time: float) -> float:
        """Return constant hazard rate λ"""
        return self.failure_rate


class WeibullDistribution(FailureDistribution):
    """Weibull failure distribution"""

    def __init__(self, shape: float, scale: float):
        """
        Args:
            shape: Weibull shape parameter (β)
            scale: Weibull scale parameter (η)
        """
        if shape <= 0 or scale <= 0:
            raise ValueError("Shape and scale parameters must be positive")
        self.shape = shape  # β
        self.scale = scale  # η

    def probability_of_failure(self, time: float) -> float:
        """F(t) = 1 - exp(-(t/η)^β)"""
        return 1 - np.exp(-((time / self.scale) ** self.shape))

    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times"""
        return self.scale * np.random.weibull(self.shape, size=size)

    def hazard_rate(self, time: float) -> float:
        """h(t) = (β/η) * (t/η)^(β-1)"""
        return (self.shape / self.scale) * ((time / self.scale) ** (self.shape - 1))


class LogNormalDistribution(FailureDistribution):
    """Log-normal failure distribution"""

    def __init__(self, mu: float, sigma: float):
        """
        Args:
            mu: Location parameter (mean of log(T))
            sigma: Scale parameter (standard deviation of log(T))
        """
        if sigma <= 0:
            raise ValueError("Sigma must be positive")
        self.mu = mu
        self.sigma = sigma

    def probability_of_failure(self, time: float) -> float:
        """F(t) = Φ((ln(t) - μ) / σ)"""
        from scipy.stats import norm

        if time <= 0:
            return 0.0
        return norm.cdf((np.log(time) - self.mu) / self.sigma)

    def random_failure_time(self, size: int = 1) -> np.ndarray:
        """Generate random failure times"""
        return np.random.lognormal(mean=self.mu, sigma=self.sigma, size=size)

    def hazard_rate(self, time: float) -> float:
        """h(t) = f(t) / (1 - F(t))"""
        from scipy.stats import norm

        if time <= 0:
            return 0.0
        # PDF of lognormal
        pdf_value = (1 / (time * self.sigma * np.sqrt(2 * np.pi))) * np.exp(
            -((np.log(time) - self.mu) ** 2) / (2 * self.sigma**2)
        )
        # CDF of lognormal
        cdf_value = norm.cdf((np.log(time) - self.mu) / self.sigma)
        # Hazard rate
        return pdf_value / (1 - cdf_value)
