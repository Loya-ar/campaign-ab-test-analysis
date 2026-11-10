import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest

from abtest.inference import (
    benjamini_hochberg,
    bootstrap_diff_means,
    heterogeneity_q,
    holm,
    two_proportion_test,
    welch_test,
)


def test_two_proportion_matches_statsmodels():
    r = two_proportion_test(267, 21307, 122, 21306)
    z, p = proportions_ztest([267, 122], [21307, 21306])
    assert r.z == pytest.approx(z) and r.p_value == pytest.approx(p)
    lo, hi = confint_proportions_2indep(267, 21307, 122, 21306, method="wald")
    assert r.ci_diff == pytest.approx((lo, hi))
    lo_rr, hi_rr = confint_proportions_2indep(267, 21307, 122, 21306, method="log", compare="ratio")
    assert r.ci_rel == pytest.approx((lo_rr - 1, hi_rr - 1))
    assert r.rel_lift == pytest.approx((267 / 21307) / (122 / 21306) - 1)


def test_two_proportion_no_effect():
    r = two_proportion_test(100, 10_000, 100, 10_000)
    assert r.diff == 0 and r.p_value == pytest.approx(1.0)
    assert r.ci_diff[0] < 0 < r.ci_diff[1]


def test_two_proportion_bad_input():
    with pytest.raises(ValueError):
        two_proportion_test(5, 0, 1, 10)
    with pytest.raises(ValueError):
        two_proportion_test(0, 100, 3, 100)


def test_welch_matches_scipy():
    rng = np.random.default_rng(1)
    a, b = rng.exponential(2, 500), rng.exponential(1.5, 800)
    r = welch_test(a, b)
    ref = stats.ttest_ind(a, b, equal_var=False)
    assert r.p_value == pytest.approx(ref.pvalue)
    ci = ref.confidence_interval()
    assert r.ci_diff == pytest.approx((ci.low, ci.high))


def test_bootstrap_is_reproducible_and_close_to_welch():
    rng = np.random.default_rng(2)
    a, b = rng.normal(1.0, 1, 3000), rng.normal(0.8, 1, 3000)
    d1, ci1, _ = bootstrap_diff_means(a, b, n_boot=2000, seed=5)
    _, ci2, _ = bootstrap_diff_means(a, b, n_boot=2000, seed=5)
    assert ci1 == ci2
    w = welch_test(a, b)
    assert d1 == pytest.approx(w.diff)
    assert ci1 == pytest.approx(w.ci_diff, abs=0.01)


def test_holm_and_bh_match_statsmodels():
    p = [0.001, 0.04, 0.03, 0.2, 0.0005, 0.6]
    assert holm(p) == pytest.approx(multipletests(p, method="holm")[1])
    assert benjamini_hochberg(p) == pytest.approx(multipletests(p, method="fdr_bh")[1])


def test_holm_two_tests_by_hand():
    # The smallest p is doubled; the larger keeps its own value unless that breaks the ordering.
    assert holm([0.01, 0.04]) == pytest.approx([0.02, 0.04])
    assert holm([0.03, 0.02]) == pytest.approx([0.04, 0.04])


def test_heterogeneity_q():
    q, dof, p = heterogeneity_q([0.5, 0.5, 0.5], [0.1, 0.2, 0.3])
    assert q == pytest.approx(0) and dof == 2 and p == pytest.approx(1)
    q, dof, p = heterogeneity_q([0.0, 1.0], [0.1, 0.1])
    assert q == pytest.approx(50) and p < 1e-10
