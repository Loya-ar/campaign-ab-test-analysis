import numpy as np
import pytest
from scipy import stats

from abtest.checks import srm_test, standardized_mean_difference


def test_srm_matches_scipy_and_flags_imbalance():
    r = srm_test([21306, 21307, 21387])
    assert r.p_value == pytest.approx(stats.chisquare([21306, 21307, 21387]).pvalue)
    assert not r.mismatch()
    assert srm_test([5000, 5400]).mismatch()  # 48/52 on 10,400 users is a real SRM


def test_srm_custom_ratio():
    r = srm_test([9000, 1000], ratios=[0.9, 0.1])
    assert r.expected == pytest.approx((9000.0, 1000.0))
    assert r.p_value == pytest.approx(1.0)


def test_srm_bad_input():
    with pytest.raises(ValueError):
        srm_test([10])
    with pytest.raises(ValueError):
        srm_test([10, 10], ratios=[0.6, 0.6])


def test_smd():
    rng = np.random.default_rng(0)
    a, b = rng.normal(1, 2, 100_000), rng.normal(0, 2, 100_000)
    assert standardized_mean_difference(a, b) == pytest.approx(0.5, abs=0.01)
    assert standardized_mean_difference([1, 1, 1], [1, 1, 1]) == 0.0
