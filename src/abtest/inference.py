"""Hypothesis tests and confidence intervals for treatment vs control comparisons."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class ProportionResult:
    p_treatment: float
    p_control: float
    diff: float              # absolute lift, p_t - p_c
    ci_diff: tuple[float, float]
    rel_lift: float          # p_t / p_c - 1
    ci_rel: tuple[float, float]
    z: float
    p_value: float


def two_proportion_test(
    x_t: int, n_t: int, x_c: int, n_c: int, alpha: float = 0.05,
) -> ProportionResult:
    """Two-sided z-test for p_t = p_c.

    The p-value uses the pooled standard error (the null hypothesis); the CI for the
    absolute difference uses the unpooled (Wald) standard error; the CI for the relative
    lift is built on the log risk ratio and transformed back.
    """
    if min(n_t, n_c) <= 0 or not (0 <= x_t <= n_t and 0 <= x_c <= n_c):
        raise ValueError("need 0 <= x <= n and n > 0")
    if x_t == 0 or x_c == 0:
        raise ValueError("need at least one success per group for the relative-lift CI")
    p_t, p_c = x_t / n_t, x_c / n_c
    z_crit = stats.norm.ppf(1 - alpha / 2)
    p_pool = (x_t + x_c) / (n_t + n_c)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_t + 1 / n_c))
    z = (p_t - p_c) / se_pool
    p_value = 2 * stats.norm.sf(abs(z))
    diff = p_t - p_c
    se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    log_rr = np.log(p_t / p_c)
    se_log = np.sqrt((1 - p_t) / x_t + (1 - p_c) / x_c)
    return ProportionResult(
        p_t, p_c, diff, (diff - z_crit * se, diff + z_crit * se),
        p_t / p_c - 1,
        (float(np.exp(log_rr - z_crit * se_log) - 1), float(np.exp(log_rr + z_crit * se_log) - 1)),
        float(z), float(p_value),
    )


@dataclass(frozen=True)
class MeanResult:
    mean_treatment: float
    mean_control: float
    diff: float
    ci_diff: tuple[float, float]
    rel_lift: float
    statistic: float
    df: float
    p_value: float


def welch_test(treatment: Sequence[float], control: Sequence[float], alpha: float = 0.05) -> MeanResult:
    """Welch's unequal-variance t-test with a Welch-Satterthwaite CI for mean_t - mean_c."""
    t, c = np.asarray(treatment, dtype=float), np.asarray(control, dtype=float)
    if len(t) < 2 or len(c) < 2:
        raise ValueError("need at least two observations per group")
    vt, vc = t.var(ddof=1) / len(t), c.var(ddof=1) / len(c)
    se = np.sqrt(vt + vc)
    df = (vt + vc) ** 2 / (vt**2 / (len(t) - 1) + vc**2 / (len(c) - 1))
    diff = t.mean() - c.mean()
    stat = diff / se
    p = 2 * stats.t.sf(abs(stat), df)
    q = stats.t.ppf(1 - alpha / 2, df)
    return MeanResult(float(t.mean()), float(c.mean()), float(diff),
                      (float(diff - q * se), float(diff + q * se)),
                      float(t.mean() / c.mean() - 1), float(stat), float(df), float(p))


def bootstrap_diff_means(
    treatment: Sequence[float], control: Sequence[float], n_boot: int = 10_000,
    alpha: float = 0.05, seed: int = 0, chunk: int = 500,
) -> tuple[float, tuple[float, float], np.ndarray]:
    """Percentile bootstrap CI for mean_t - mean_c, resampling each group independently.

    Returns (observed difference, (lower, upper), bootstrap distribution).
    """
    t, c = np.asarray(treatment, dtype=float), np.asarray(control, dtype=float)
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot)
    for start in range(0, n_boot, chunk):
        k = min(chunk, n_boot - start)
        mt = t[rng.integers(0, len(t), size=(k, len(t)))].mean(axis=1)
        mc = c[rng.integers(0, len(c), size=(k, len(c)))].mean(axis=1)
        out[start:start + k] = mt - mc
    lo, hi = np.quantile(out, [alpha / 2, 1 - alpha / 2])
    return float(t.mean() - c.mean()), (float(lo), float(hi)), out


def holm(p_values: Sequence[float]) -> np.ndarray:
    """Holm-Bonferroni adjusted p-values (step-down, monotone, capped at 1)."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj_sorted = np.maximum.accumulate((m - np.arange(m)) * p[order])
    adj = np.empty(m)
    adj[order] = np.minimum(adj_sorted, 1.0)
    return adj


def benjamini_hochberg(p_values: Sequence[float]) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (controls the false discovery rate)."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)[::-1]                      # largest first
    ranks = m - np.arange(m)                         # rank of each, largest p has rank m
    adj_sorted = np.minimum.accumulate(p[order] * m / ranks)
    adj = np.empty(m)
    adj[order] = np.minimum(adj_sorted, 1.0)
    return adj


def heterogeneity_q(effects: Sequence[float], ses: Sequence[float]) -> tuple[float, int, float]:
    """Cochran's Q test that several independent effect estimates are equal.

    Returns (Q, degrees of freedom, p-value).
    """
    d, s = np.asarray(effects, dtype=float), np.asarray(ses, dtype=float)
    if len(d) < 2 or (s <= 0).any():
        raise ValueError("need at least two estimates with positive standard errors")
    w = 1 / s**2
    pooled = (w * d).sum() / w.sum()
    q = float((w * (d - pooled) ** 2).sum())
    dof = len(d) - 1
    return q, dof, float(stats.chi2.sf(q, dof))
