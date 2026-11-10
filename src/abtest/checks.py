"""Sanity checks run before reading any outcome: sample ratio mismatch and covariate balance."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class SRMResult:
    observed: tuple[int, ...]
    expected: tuple[float, ...]
    chi2: float
    p_value: float

    def mismatch(self, threshold: float = 0.001) -> bool:
        """SRM is usually flagged at a strict threshold such as p < 0.001."""
        return self.p_value < threshold


def srm_test(counts: Sequence[int], ratios: Sequence[float] | None = None) -> SRMResult:
    """Chi-square goodness-of-fit test of group sizes against the planned allocation."""
    obs = np.asarray(counts, dtype=float)
    if obs.ndim != 1 or len(obs) < 2 or (obs < 0).any():
        raise ValueError("counts must be at least two non-negative numbers")
    r = np.full(len(obs), 1 / len(obs)) if ratios is None else np.asarray(ratios, dtype=float)
    if len(r) != len(obs) or not np.isclose(r.sum(), 1):
        raise ValueError("ratios must match counts and sum to 1")
    exp = r * obs.sum()
    chi2, p = stats.chisquare(obs, exp)
    return SRMResult(tuple(int(c) for c in obs), tuple(exp), float(chi2), float(p))


def standardized_mean_difference(treatment: Sequence[float], control: Sequence[float]) -> float:
    """(mean_t - mean_c) / sqrt((var_t + var_c) / 2). |SMD| < 0.1 is the usual balance bar."""
    t, c = np.asarray(treatment, dtype=float), np.asarray(control, dtype=float)
    pooled = np.sqrt((t.var(ddof=1) + c.var(ddof=1)) / 2)
    if pooled == 0:
        return 0.0
    return float((t.mean() - c.mean()) / pooled)
