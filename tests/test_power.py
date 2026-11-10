import math

import pytest
from statsmodels.stats.power import NormalIndPower, tt_ind_solve_power
from statsmodels.stats.proportion import proportion_effectsize

from abtest.power import mde_proportions, n_per_group_means, n_per_group_proportions


def test_textbook_example():
    # 10% -> 12%, alpha 0.05 two-sided, power 0.8: the standard formula gives 3,841 per group.
    assert n_per_group_proportions(0.10, 0.12) == 3841


def test_close_to_statsmodels_arcsine_method():
    ours = n_per_group_proportions(0.05, 0.06, alpha=0.05, power=0.8)
    h = proportion_effectsize(0.06, 0.05)
    theirs = NormalIndPower().solve_power(h, alpha=0.05, power=0.8)
    assert abs(ours / theirs - 1) < 0.01


def test_more_power_or_smaller_alpha_needs_more_customers():
    base = n_per_group_proportions(0.05, 0.06)
    assert n_per_group_proportions(0.05, 0.06, power=0.9) > base
    assert n_per_group_proportions(0.05, 0.06, alpha=0.01) > base
    assert n_per_group_proportions(0.05, 0.06, two_sided=False) < base


def test_mde_inverts_sample_size():
    n = n_per_group_proportions(0.0057, 0.0057 * 1.5)
    mde = mde_proportions(0.0057, n)
    assert mde == pytest.approx(0.0057 * 0.5, rel=1e-3)


def test_means_matches_formula_and_statsmodels():
    n = n_per_group_means(sd=10, delta=1, alpha=0.05, power=0.8)
    assert n == math.ceil(2 * (1.959964 + 0.841621) ** 2 * 100)
    t_based = tt_ind_solve_power(effect_size=0.1, alpha=0.05, power=0.8)
    assert abs(n - t_based) <= 2  # normal vs t approximation


@pytest.mark.parametrize("p1,p2", [(0, 0.1), (0.1, 0.1), (0.5, 1.0)])
def test_invalid_rates_raise(p1, p2):
    with pytest.raises(ValueError):
        n_per_group_proportions(p1, p2)
