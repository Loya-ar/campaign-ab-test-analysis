import numpy as np
import pytest

from abtest.sequential import aa_peeking_false_positive_rate, look_points, obrien_fleming_boundaries


def test_look_points():
    assert list(look_points(100, 4)) == [25, 50, 75, 100]
    assert list(look_points(100, 1)) == [100]


def test_obf_single_look_is_196_and_5_looks_matches_published_constant():
    assert obrien_fleming_boundaries(1)[0] == pytest.approx(1.96, abs=0.001)
    b = obrien_fleming_boundaries(5, n_sim=200_000, seed=1)
    assert b[-1] == pytest.approx(2.04, abs=0.02)  # published O'Brien-Fleming constant
    assert np.all(np.diff(b) < 0)  # strict early, looser later


def test_peeking_inflates_and_obf_fixes():
    rng = np.random.default_rng(0)
    y = (rng.random(8000) < 0.1).astype(float)
    one = aa_peeking_false_positive_rate(y, 1, n_sim=1500, seed=1)
    many = aa_peeking_false_positive_rate(y, 20, n_sim=1500, seed=1)
    fixed = aa_peeking_false_positive_rate(
        y, 20, n_sim=1500, seed=1, boundaries=obrien_fleming_boundaries(20, seed=1)
    )
    assert one == pytest.approx(0.05, abs=0.02)
    assert many > 0.15
    assert fixed == pytest.approx(0.05, abs=0.02)
