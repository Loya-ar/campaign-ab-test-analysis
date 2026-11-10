"""Sample-size and minimum-detectable-effect calculations (normal approximation)."""
from __future__ import annotations

import math

from scipy import optimize, stats


def _z(alpha: float, power: float, two_sided: bool) -> tuple[float, float]:
    z_alpha = stats.norm.ppf(1 - alpha / 2) if two_sided else stats.norm.ppf(1 - alpha)
    return z_alpha, stats.norm.ppf(power)


def _n_raw_proportions(p_control, p_treatment, alpha, power, two_sided) -> float:
    if not (0 < p_control < 1 and 0 < p_treatment < 1):
        raise ValueError("rates must be strictly between 0 and 1")
    if p_control == p_treatment:
        raise ValueError("rates must differ")
    z_a, z_b = _z(alpha, power, two_sided)
    p_bar = (p_control + p_treatment) / 2
    num = (
        z_a * math.sqrt(2 * p_bar * (1 - p_bar))
        + z_b * math.sqrt(p_control * (1 - p_control) + p_treatment * (1 - p_treatment))
    ) ** 2
    return num / (p_treatment - p_control) ** 2


def n_per_group_proportions(
    p_control: float, p_treatment: float, alpha: float = 0.05, power: float = 0.8,
    two_sided: bool = True,
) -> int:
    """Customers needed per group to detect p_control -> p_treatment (equal group sizes).

    Uses the standard formula with the pooled variance under H0 and the
    unpooled variance under H1.
    """
    return math.ceil(_n_raw_proportions(p_control, p_treatment, alpha, power, two_sided))


def mde_proportions(
    p_control: float, n_per_group: int, alpha: float = 0.05, power: float = 0.8,
    two_sided: bool = True,
) -> float:
    """Smallest absolute lift (p_treatment - p_control > 0) detectable with n per group."""
    def gap(delta: float) -> float:
        return _n_raw_proportions(p_control, p_control + delta, alpha, power, two_sided) - n_per_group

    # n falls as delta grows, so find where the required n crosses the available n.
    return optimize.brentq(gap, 1e-9, 1 - p_control - 1e-9, xtol=1e-10)


def n_per_group_means(
    sd: float, delta: float, alpha: float = 0.05, power: float = 0.8, two_sided: bool = True,
) -> int:
    """Customers per group to detect a difference in means of `delta` (common SD)."""
    if sd <= 0 or delta == 0:
        raise ValueError("sd must be positive and delta non-zero")
    z_a, z_b = _z(alpha, power, two_sided)
    return math.ceil(2 * ((z_a + z_b) * sd / delta) ** 2)
