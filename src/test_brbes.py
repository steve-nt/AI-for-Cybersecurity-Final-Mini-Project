"""Unit tests for the BRBES engine (TASK T6).

The expected numbers are the worked example in TASKLIST.md section 4, computed beforehand with two
independent ER implementations (analytical and recursive).

Run:  python -m pytest src/test_brbes.py
"""
import numpy as np
import pytest

import brbes

TOL = 1e-4
LEVELS = [np.array([0.0, 50.0, 100.0]), np.array([0.0, 10.0, 20.0])]
# Attack share per rule: rows = feature A level, columns = feature B level (Low, Medium, High).
SHARE = np.array([[0.02, 0.10, 0.30],
                  [0.10, 0.40, 0.70],
                  [0.30, 0.80, 0.95]])


@pytest.fixture
def rb():
    antecedents = brbes.all_combinations(LEVELS)
    beta = brbes.share_to_belief([SHARE[a, b] for a, b in antecedents])
    return brbes.RuleBase(["A", "B"], LEVELS, antecedents, beta, theta=1.0, delta=[1.0, 1.0])


def test_share_to_belief_matches_the_table():
    expected = {0.02: (0.96, 0.04, 0), 0.10: (0.80, 0.20, 0), 0.30: (0.40, 0.60, 0), 0.40: (0.20, 0.80, 0),
                0.70: (0, 0.60, 0.40), 0.80: (0, 0.40, 0.60), 0.95: (0, 0.10, 0.90)}
    for p, beliefs in expected.items():
        np.testing.assert_allclose(brbes.share_to_belief([p])[0], beliefs, atol=1e-12)
        assert brbes.share_to_belief([p])[0] @ brbes.UTILITIES == pytest.approx(100 * p)


def test_input_transform():
    alpha = brbes.input_transform([75, 50, -5, 130, np.nan], LEVELS[0])
    np.testing.assert_allclose(alpha, [[0, 0.5, 0.5], [0, 1, 0], [1, 0, 0], [0, 0, 1], [0, 0, 0]])


def test_complete_input(rb):
    alphas = brbes.matching_degrees(rb, [[75, 5]])
    np.testing.assert_allclose(alphas[0][0], [0, 0.5, 0.5])
    np.testing.assert_allclose(alphas[1][0], [0.5, 0.5, 0])
    w = brbes.activation_weights(rb, alphas)[0]
    # rules are numbered A-level * 3 + B-level: M/L = 3, M/M = 4, H/L = 6, H/M = 7
    np.testing.assert_allclose(w, [0, 0, 0, 0.25, 0.25, 0, 0.25, 0.25, 0])
    belief = brbes.infer(rb, [[75, 5]])[0]
    np.testing.assert_allclose(belief, [0.3386, 0.5339, 0.1275, 0.0], atol=TOL)
    u_min, u_max, u_avg = brbes.utility(rb, belief)
    assert u_min[0] == pytest.approx(39.44, abs=0.01) and u_max[0] == pytest.approx(39.44, abs=0.01)


def test_missing_input(rb):
    alphas = brbes.matching_degrees(rb, [[75, np.nan]])
    w = brbes.activation_weights(rb, alphas)[0]
    np.testing.assert_allclose(w, [0, 0, 0] + [1 / 6] * 6)
    np.testing.assert_allclose(brbes.belief_update(rb, alphas)[0], rb.beta * 0.5)
    belief = brbes.infer(rb, [[75, np.nan]])[0]
    np.testing.assert_allclose(belief, [0.1294, 0.2649, 0.1787, 0.4270], atol=TOL)
    u_min, u_max, u_avg = (u[0] for u in brbes.utility(rb, belief))
    assert (u_min, u_max, u_avg) == pytest.approx((31.12, 73.82, 52.47), abs=0.01)


def test_single_rule_fires(rb):
    belief = brbes.infer(rb, [[100, 20]])[0]
    np.testing.assert_allclose(belief, [0, 0.10, 0.90, 0], atol=TOL)
    assert brbes.utility(rb, belief)[2][0] == pytest.approx(95.0, abs=0.01)


def test_single_incomplete_rule_keeps_its_ignorance():
    out = brbes.er_aggregate(np.array([[1.0]]), np.array([[[0.1, 0.2, 0.5]]]))[0]
    np.testing.assert_allclose(out, [0.1, 0.2, 0.5, 0.2], atol=1e-12)


def test_all_missing_is_total_ignorance(rb):
    np.testing.assert_allclose(brbes.infer(rb, [[np.nan, np.nan]])[0], [0, 0, 0, 1])


def test_sanity_on_random_inputs(rb):
    rng = np.random.default_rng(42)
    X = np.column_stack([rng.uniform(-20, 120, 2000), rng.uniform(-5, 25, 2000)])
    X[rng.random(2000) < 0.1, 1] = np.nan
    alphas = brbes.matching_degrees(rb, X)
    w = brbes.activation_weights(rb, alphas)
    np.testing.assert_allclose(w.sum(1), 1.0)
    assert ((w > 0).sum(1)[~np.isnan(X[:, 1])] <= 4).all()          # at most 4 of 9 rules fire
    belief = brbes.infer(rb, X)
    assert (belief >= 0).all() and (belief <= 1).all()
    np.testing.assert_allclose(belief.sum(1), 1.0)
    rb_weighted = brbes.RuleBase(rb.features, rb.levels, rb.antecedents, rb.beta, 1.0, [1.0, 0.4])
    np.testing.assert_allclose(brbes.infer(rb_weighted, X).sum(1), 1.0)


def test_build_rule_base_from_data():
    rng = np.random.default_rng(0)
    X = np.column_stack([rng.uniform(0, 100, 5000), rng.uniform(0, 20, 5000)])
    y = ((X[:, 0] > 60) & (X[:, 1] > 12)).astype(int)
    rb = brbes.build_rule_base(X, y, LEVELS, n0=20)
    assert rb.beta.shape == (9, 3)
    assert rb.support.sum() == pytest.approx(5000)                 # every row is shared out once
    assert (rb.beta.sum(1) < 1).all()                              # some ignorance everywhere, never all 0/1
    assert rb.attack_share[8] > 0.5 > rb.attack_share[0]           # High/High risky, Low/Low safe
    table = brbes.rules_table(rb)
    assert list(table["if"])[8] == "IF feature 1 is High AND feature 2 is High"
    u = brbes.utility(rb, brbes.infer(rb, X))[2]
    tau = brbes.choose_threshold(u, y)
    assert brbes.f1_score(y, (u >= tau).astype(int), average="macro") > 0.8


def test_make_levels():
    np.testing.assert_allclose(brbes.make_levels(np.arange(101)), [5, 50, 95])
    x = np.r_[np.zeros(800), np.arange(1, 201)]                    # mostly zeros: naive levels collapse
    levels = brbes.make_levels(x)
    assert levels[0] == 0 and np.all(np.diff(levels) > 0)


def test_trace_mentions_every_step(rb):
    text = brbes.trace(rb, [75, np.nan], threshold=50)
    for part in ("Step 2", "Step 3", "Step 4", "Step 5", "ignorance 0.4270", "Decision  ATTACK"):
        assert part in text
