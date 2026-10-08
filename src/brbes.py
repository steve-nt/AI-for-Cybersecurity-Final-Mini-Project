"""TASK T6: Belief Rule-Based Expert System (BRBES) inference engine.

Implements the five belief-rule steps of RIMER plus the decision:
  1. Knowledge representation  RuleBase (rules with belief degrees beta, rule weights theta,
                               attribute weights delta)
  2. Input transformation      input_transform()      Yang (2001), rule/utility-based transformation
  3. Rule activation weight    activation_weights()   Yang et al. (2006), RIMER
  4. Belief update             belief_update()        Yang et al. (2006), RIMER
  5. Rule aggregation          er_aggregate()         analytical ER algorithm, as in
                                                      Wang, Yang & Xu (2006) and RIMER
  Decision                     utility(), choose_threshold()

References: Yang, J.-B. (2001), EJOR 131(1); Yang, J.-B., Liu, J., Wang, J., Sii, H.-S., Wang, H.-W.
(2006), IEEE Trans. SMC-A 36(2) (RIMER); Wang, Y.-M., Yang, J.-B., Xu, D.-L. (2006), EJOR 174(3);
course lecture "Expert Systems and Rule-Based Reasoning for Cyber Defense" (Prof. M. S. Hossain).
The formulas are written out in TASKLIST.md section 4. Everything is vectorised over rows (flows).
"""
import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

LEVEL_NAMES = ("Low", "Medium", "High")
RISK_NAMES = ("Low", "Medium", "High")
UTILITIES = (0.0, 50.0, 100.0)


# ---------------------------------------------------------------------------
# Step 1: knowledge representation
# ---------------------------------------------------------------------------
@dataclass
class RuleBase:
    """One rule per combination of feature levels.

    features     T feature names (the antecedent attributes)
    levels       per feature, its strictly increasing referential values (e.g. Low, Medium, High)
    antecedents  (L, T) level index each rule uses for each feature
    beta         (L, N) belief degrees over the risk levels; each row sums to <= 1, the rest is ignorance
    theta        (L,) rule weights
    delta        (T,) attribute weights
    support, attack_share   (L,) how much training data backs each rule (filled by build_rule_base)
    """
    features: list
    levels: list
    antecedents: np.ndarray
    beta: np.ndarray
    theta: np.ndarray
    delta: np.ndarray
    level_names: tuple = LEVEL_NAMES
    risk_names: tuple = RISK_NAMES
    utilities: np.ndarray = field(default_factory=lambda: np.array(UTILITIES))
    support: np.ndarray = None
    attack_share: np.ndarray = None

    def __post_init__(self):
        self.levels = [np.asarray(v, dtype=float) for v in self.levels]
        self.antecedents = np.asarray(self.antecedents, dtype=int)
        self.beta = np.asarray(self.beta, dtype=float)
        self.theta = np.broadcast_to(np.asarray(self.theta, dtype=float), (len(self.antecedents),)).copy()
        self.delta = np.asarray(self.delta, dtype=float)
        self.utilities = np.asarray(self.utilities, dtype=float)
        L, T = self.antecedents.shape
        assert T == len(self.features) == len(self.levels) == len(self.delta), "one level set and delta per feature"
        assert self.beta.shape == (L, len(self.utilities)), "beta must be (rules, risk levels)"
        assert np.all(self.beta >= -1e-12) and np.all(self.beta.sum(1) <= 1 + 1e-9), "beliefs in [0, 1], sum <= 1"
        for v in self.levels:
            assert np.all(np.diff(v) > 0), f"levels must be strictly increasing: {v}"


def all_combinations(levels):
    """(L, T) antecedents: every combination of the features' levels (3 x 3 = 9 rules for 2 features)."""
    return np.array(list(itertools.product(*(range(len(v)) for v in levels))), dtype=int)


def make_levels(x_train, q=(0.05, 0.50, 0.95)):
    """Referential values of one feature from training percentiles (TASKLIST P7).

    If two coincide (many zeros or many -1 values), Low becomes the repeated value and the other
    levels are taken from the values above it.
    """
    x = np.asarray(x_train, dtype=float)
    x = x[np.isfinite(x)]
    levels = np.quantile(x, q)
    if np.all(np.diff(levels) > 0):
        return levels
    low = levels[0]
    above = x[x > low]
    if above.size:
        levels = np.concatenate([[low], np.quantile(above, q[1:])])
    if not np.all(np.diff(levels) > 0):
        raise ValueError(f"Cannot place {len(q)} distinct levels on this feature: {levels}. "
                         "Choose the levels by hand (expert judgment).")
    return levels


# ---------------------------------------------------------------------------
# Step 2: input transformation
# ---------------------------------------------------------------------------
def input_transform(x, levels):
    """Crisp values (n,) -> matching degrees (n, J) over the J levels.

    A value between two levels belongs partly to both; below the first level it is fully the first,
    above the last it is fully the last. A missing value (NaN) matches no level (all zeros).
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    levels = np.asarray(levels, dtype=float)
    J = len(levels)
    alpha = np.zeros((len(x), J))
    present = ~np.isnan(x)
    xc = np.clip(x[present], levels[0], levels[-1])
    j = np.clip(np.searchsorted(levels, xc, side="right") - 1, 0, J - 2)
    upper = (xc - levels[j]) / (levels[j + 1] - levels[j])
    rows = np.flatnonzero(present)
    alpha[rows, j] = 1.0 - upper
    alpha[rows, j + 1] = upper
    return alpha


def matching_degrees(rb, X):
    """X (n, T) in the order of rb.features (a DataFrame is reordered) -> list of T arrays (n, J_t)."""
    if isinstance(X, pd.DataFrame):
        X = X[rb.features].to_numpy()
    X = np.asarray(X, dtype=float).reshape(-1, len(rb.features))
    return [input_transform(X[:, t], rb.levels[t]) for t in range(len(rb.features))]


# ---------------------------------------------------------------------------
# Step 3: rule activation weight
# ---------------------------------------------------------------------------
def activation_weights(rb, alphas):
    """(n, L) activation weights, each row summing to 1.

    w_k = theta_k * prod_t (alpha_t^k)^(delta_t / max delta), normalised over the rules.
    A missing feature is left out of the product (otherwise every rule would get weight 0);
    belief_update() then turns its absence into ignorance. If every feature is missing, all weights are 0.
    """
    dbar = rb.delta / rb.delta.max()
    raw = np.tile(rb.theta, (len(alphas[0]), 1))
    for t, alpha in enumerate(alphas):
        present = alpha.sum(1) > 0
        factor = alpha[:, rb.antecedents[:, t]] ** dbar[t]
        raw *= np.where(present[:, None], factor, 1.0)
    total = raw.sum(1, keepdims=True)
    return np.divide(raw, total, out=np.zeros_like(raw), where=total > 0)


# ---------------------------------------------------------------------------
# Step 4: belief update
# ---------------------------------------------------------------------------
def belief_update(rb, alphas):
    """(n, L, N) beliefs, each rule's beta scaled by the share of its input information that is present.

    beta'_jk = beta_jk * sum_t tau(t,k) sum_i alpha_ti / sum_t tau(t,k). Every rule here uses every
    feature (tau = 1), so the factor is the mean over features of their summed matching degrees:
    1 for complete input, 0.5 when one of two features is missing.
    """
    factor = np.mean([alpha.sum(1) for alpha in alphas], axis=0)
    return rb.beta[None, :, :] * factor[:, None, None]


# ---------------------------------------------------------------------------
# Step 5: rule aggregation with the analytical Evidential Reasoning algorithm
# ---------------------------------------------------------------------------
def er_aggregate(w, beta):
    """w (n, L) activation weights, beta (n, L, N) updated beliefs -> (n, N + 1): N beliefs + ignorance.

    mu     = [ sum_j prod_k (w_k b_jk + 1 - w_k S_k) - (N - 1) prod_k (1 - w_k S_k) ]^-1
    beta_j = mu [ prod_k (w_k b_jk + 1 - w_k S_k) - prod_k (1 - w_k S_k) ] / [ 1 - mu prod_k (1 - w_k) ]
    with S_k = sum_j b_jk. Rows where no rule is active get full ignorance.
    """
    w = np.asarray(w, dtype=float)
    beta = np.asarray(beta, dtype=float)
    if beta.ndim == 2:
        beta = np.broadcast_to(beta, (len(w), *beta.shape))
    N = beta.shape[2]
    ws = w * beta.sum(2)                                              # (n, L)  w_k S_k
    prod_j = np.prod(w[:, :, None] * beta + (1.0 - ws)[:, :, None], axis=1)   # (n, N)
    prod_d = np.prod(1.0 - ws, axis=1)                                # (n,)
    prod_w = np.prod(1.0 - w, axis=1)                                 # (n,)
    active = w.sum(1) > 0
    out = np.zeros((len(w), N + 1))
    out[~active, N] = 1.0
    mu = 1.0 / (prod_j[active].sum(1) - (N - 1) * prod_d[active])
    b = mu[:, None] * (prod_j[active] - prod_d[active, None]) / (1.0 - mu * prod_w[active])[:, None]
    out[active, :N] = b
    out[active, N] = 1.0 - b.sum(1)
    return np.clip(out, 0.0, 1.0)


def infer(rb, X):
    """Steps 2-5 for every row of X (n, T) -> (n, N + 1): belief in Low, Medium, High and ignorance."""
    alphas = matching_degrees(rb, X)
    return er_aggregate(activation_weights(rb, alphas), belief_update(rb, alphas))


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------
def utility(rb, belief):
    """(u_min, u_max, u_avg), each (n,). Ignorance counted as the worst level, the best, and halfway."""
    belief = np.atleast_2d(belief)
    N = len(rb.utilities)
    base = belief[:, :N] @ rb.utilities
    ignorance = belief[:, N]
    u_min = base + rb.utilities.min() * ignorance
    u_max = base + rb.utilities.max() * ignorance
    return u_min, u_max, (u_min + u_max) / 2.0


def choose_threshold(u_val, y_val, grid=None):
    """Threshold tau on the utility (Attack if u >= tau) that maximises macro-F1 on validation data.
    Ties go to the lowest threshold, which keeps attack recall highest."""
    grid = np.arange(0.0, 100.5, 0.5) if grid is None else np.asarray(grid)
    u_val, y_val = np.asarray(u_val), np.asarray(y_val)
    scores = [f1_score(y_val, (u_val >= t).astype(int), average="macro") for t in grid]
    return float(grid[int(np.argmax(scores))])


# ---------------------------------------------------------------------------
# Step 1 from data (TASKLIST P7)
# ---------------------------------------------------------------------------
def share_to_belief(p, utilities=UTILITIES):
    """Attack share p in [0, 1] -> beliefs over the risk levels whose expected utility is 100 * p.
    For utilities 0/50/100: p <= 0.5 -> (1 - 2p, 2p, 0); p > 0.5 -> (0, 2 - 2p, 2p - 1)."""
    utilities = np.asarray(utilities, dtype=float)
    target = utilities.min() + np.asarray(p, dtype=float) * (utilities.max() - utilities.min())
    return input_transform(target, utilities)


def build_rule_base(X2_train, y_train, levels, theta=1.0, delta=None, n0=20.0, sample_weight=None,
                    features=None, level_names=LEVEL_NAMES):
    """Rule base whose beliefs come from the training data (TASKLIST P7).

    For each rule: soft support n_k = sum alpha_A alpha_B, soft attack count a_k = sum y alpha_A alpha_B,
    attack share p_k = (a_k + 1) / (n_k + 2), beliefs = share_to_belief(p_k), then scaled by
    n_k / (n_k + n0) so that rules backed by little data keep visible ignorance.
    sample_weight lets pseudo-labelled rows count less (e.g. 0.5, as in Lab 2).
    """
    if features is None:
        features = list(X2_train.columns) if isinstance(X2_train, pd.DataFrame) else \
            [f"feature {t + 1}" for t in range(np.shape(X2_train)[1])]
    levels = [np.asarray(v, dtype=float) for v in levels]
    antecedents = all_combinations(levels)
    delta = np.ones(len(levels)) if delta is None else np.asarray(delta, dtype=float)
    shell = RuleBase(features, levels, antecedents, np.zeros((len(antecedents), len(UTILITIES))),
                     theta, delta, level_names=tuple(level_names))

    alphas = matching_degrees(shell, X2_train)
    membership = np.ones((len(alphas[0]), len(antecedents)))
    for t, alpha in enumerate(alphas):
        membership *= alpha[:, antecedents[:, t]]
    weight = np.ones(len(membership)) if sample_weight is None else np.asarray(sample_weight, dtype=float)
    y = np.asarray(y_train, dtype=float)
    support = (weight[:, None] * membership).sum(0)
    attacks = ((weight * y)[:, None] * membership).sum(0)
    share = (attacks + 1.0) / (support + 2.0)
    beta = share_to_belief(share) * (support / (support + n0))[:, None]

    shell.beta, shell.support, shell.attack_share = beta, support, share
    return shell


# ---------------------------------------------------------------------------
# Reading the system (for the report)
# ---------------------------------------------------------------------------
def level_name(rb, t, index):
    """Readable name of level `index` of feature `t` ("Low"/"Medium"/"High", or the number if unnamed)."""
    return rb.level_names[index] if len(rb.level_names) == len(rb.levels[t]) else str(index)


def _rule_text(rb, k):
    conditions = " AND ".join(f"{f} is {level_name(rb, t, rb.antecedents[k, t])}"
                              for t, f in enumerate(rb.features))
    return f"IF {conditions}"


def rules_table(rb):
    """Readable IF-THEN rules with their beliefs, ignorance, weights and data support."""
    rows = []
    for k in range(len(rb.antecedents)):
        row = {"rule": k + 1, "if": _rule_text(rb, k)}
        for j, name in enumerate(rb.risk_names):
            row[f"belief_{name}"] = round(float(rb.beta[k, j]), 4)
        row["ignorance"] = round(float(1 - rb.beta[k].sum()), 4)
        row["theta"] = float(rb.theta[k])
        row["delta"] = tuple(float(v) for v in rb.delta)
        if rb.support is not None:
            row["support"] = round(float(rb.support[k]), 1)
            row["attack_share"] = round(float(rb.attack_share[k]), 4)
        rows.append(row)
    return pd.DataFrame(rows)


def trace(rb, x2, threshold=None):
    """Step-by-step explanation of one flow: matching degrees, firing rules, ER belief, utility, decision."""
    x2 = np.asarray(x2, dtype=float).reshape(1, -1)
    alphas = matching_degrees(rb, x2)
    w = activation_weights(rb, alphas)[0]
    belief = er_aggregate(activation_weights(rb, alphas), belief_update(rb, alphas))
    u_min, u_max, u_avg = (float(u[0]) for u in utility(rb, belief))
    lines = ["Step 2  matching degrees"]
    for t, f in enumerate(rb.features):
        value = "missing" if np.isnan(x2[0, t]) else f"{x2[0, t]:g}"
        degrees = ", ".join(f"{level_name(rb, t, i)} {a:.3f}" for i, a in enumerate(alphas[t][0]))
        lines.append(f"  {f} = {value}  ->  {degrees}")
    lines.append("Step 3  firing rules (activation weight)")
    for k in np.flatnonzero(w > 0):
        lines.append(f"  rule {k + 1}: {_rule_text(rb, k)}  w = {w[k]:.3f}")
    factor = np.mean([a.sum() for a in alphas])
    lines.append(f"Step 4  belief update factor {factor:.2f}" + ("" if factor == 1 else "  (missing input -> ignorance)"))
    lines.append("Step 5  ER belief  " + ", ".join(f"{n} {b:.4f}" for n, b in zip(rb.risk_names, belief[0]))
                 + f", ignorance {belief[0, -1]:.4f}")
    lines.append(f"Utility  min {u_min:.2f}, max {u_max:.2f}, avg {u_avg:.2f}")
    if threshold is not None:
        lines.append(f"Decision  {'ATTACK' if u_avg >= threshold else 'normal'} (threshold {threshold:g})")
    return "\n".join(lines)
