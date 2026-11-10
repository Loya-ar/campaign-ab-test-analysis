import numpy as np
import pytest

from abtest.cuped import cuped_adjust, cuped_theta


def make(rho, n=50_000, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    y = rho * x + np.sqrt(1 - rho**2) * rng.standard_normal(n)
    return y, x


def test_theta_is_ols_slope():
    y, x = make(0.6)
    assert cuped_theta(y, x) == pytest.approx(np.polyfit(x, y, 1)[0])


def test_variance_falls_by_rho_squared_and_mean_kept():
    y, x = make(0.7)
    ya = cuped_adjust(y, x)
    assert ya.mean() == pytest.approx(y.mean())
    assert 1 - ya.var() / y.var() == pytest.approx(0.49, abs=0.01)


def test_unrelated_covariate_changes_little():
    y, x = make(0.0)
    assert 1 - cuped_adjust(y, x).var() / y.var() < 0.001


def test_effect_estimate_unbiased_across_simulations():
    rng = np.random.default_rng(3)
    est = []
    for _ in range(300):
        x = rng.standard_normal(2000)
        t = np.arange(2000) < 1000
        y = 0.8 * x + 0.6 * rng.standard_normal(2000) + 0.2 * t
        ya = cuped_adjust(y, x)
        est.append(ya[t].mean() - ya[~t].mean())
    assert np.mean(est) == pytest.approx(0.2, abs=0.01)


def test_constant_covariate_raises():
    with pytest.raises(ValueError):
        cuped_theta([1, 2, 3], [5, 5, 5])
