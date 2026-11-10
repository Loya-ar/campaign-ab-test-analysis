"""CUPED (Deng et al., 2013): reduce metric variance with a pre-period covariate."""
from __future__ import annotations

from typing import Sequence

import numpy as np


def cuped_theta(y: Sequence[float], x: Sequence[float]) -> float:
    """theta = cov(y, x) / var(x), the OLS slope of y on x.

    Estimate it on treatment and control pooled, so both groups get the same adjustment.
    Because x is measured before assignment, the adjustment can't absorb the treatment effect.
    """
    y, x = np.asarray(y, dtype=float), np.asarray(x, dtype=float)
    vx = x.var(ddof=1)
    if vx == 0:
        raise ValueError("covariate has zero variance")
    return float(np.cov(y, x, ddof=1)[0, 1] / vx)


def cuped_adjust(
    y: Sequence[float], x: Sequence[float], theta: float | None = None, x_mean: float | None = None,
) -> np.ndarray:
    """y_adj = y - theta * (x - mean(x)). Keeps the mean of y; variance falls by about rho^2."""
    y, x = np.asarray(y, dtype=float), np.asarray(x, dtype=float)
    theta = cuped_theta(y, x) if theta is None else theta
    x_mean = x.mean() if x_mean is None else x_mean
    return y - theta * (x - x_mean)
