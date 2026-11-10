"""Peeking: how repeated significance testing inflates false positives, and a fix."""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy import stats


def look_points(n_total: int, n_looks: int) -> np.ndarray:
    """Equally spaced sample sizes (per arm) at which an analyst checks the result."""
    if n_looks < 1 or n_total < n_looks:
        raise ValueError("need 1 <= n_looks <= n_total")
    return np.unique(np.linspace(n_total / n_looks, n_total, n_looks).round().astype(int))


def obrien_fleming_boundaries(n_looks: int, alpha: float = 0.05, n_sim: int = 200_000, seed: int = 0) -> np.ndarray:
    """Two-sided O'Brien-Fleming-shaped z boundaries z_k = c * sqrt(K / k), equal spacing.

    c is calibrated by Monte Carlo on Gaussian random walks so that the chance of ever
    crossing under H0 is `alpha`. With one look this is the usual 1.96.
    """
    if n_looks == 1:
        return np.array([stats.norm.ppf(1 - alpha / 2)])
    rng = np.random.default_rng(seed)
    k = np.arange(1, n_looks + 1)
    z = rng.standard_normal((n_sim, n_looks)).cumsum(axis=1) / np.sqrt(k)  # z-stat at each look
    # max over looks of |z_k| / sqrt(K / k); c is its (1 - alpha) quantile
    c = np.quantile((np.abs(z) / np.sqrt(n_looks / k)).max(axis=1), 1 - alpha)
    return c * np.sqrt(n_looks / k)


def aa_peeking_false_positive_rate(
    outcome: Sequence[float], n_looks: int, n_sim: int = 2_000, alpha: float = 0.05,
    boundaries: Sequence[float] | None = None, seed: int = 0,
) -> float:
    """Share of A/A tests declared significant at ANY look.

    Each simulation shuffles the real outcomes, splits them into two equal arms (so the null
    is true by construction) and runs a pooled two-sample z-test at each look. Without
    `boundaries`, every look uses the fixed critical value for `alpha` (naive peeking).
    """
    y = np.asarray(outcome, dtype=float)
    n_arm = len(y) // 2
    looks = look_points(n_arm, n_looks)
    crit = (np.full(len(looks), stats.norm.ppf(1 - alpha / 2)) if boundaries is None
            else np.asarray(boundaries, dtype=float))
    if len(crit) != len(looks):
        raise ValueError("one boundary per look is required")
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sim):
        perm = rng.permutation(y)[: 2 * n_arm]
        a, b = perm[:n_arm], perm[n_arm:]
        sa, sb = np.cumsum(a)[looks - 1], np.cumsum(b)[looks - 1]
        qa, qb = np.cumsum(a * a)[looks - 1], np.cumsum(b * b)[looks - 1]
        n = looks.astype(float)
        mean_pool = (sa + sb) / (2 * n)
        var_pool = (qa + qb) / (2 * n) - mean_pool**2
        se = np.sqrt(var_pool * 2 / n)
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(se > 0, (sa / n - sb / n) / se, 0.0)
        hits += bool((np.abs(z) >= crit).any())
    return hits / n_sim
