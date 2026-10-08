"""TASK T7: explanation toolkit.

SHAP and LIME helpers, plus the measurements used to judge them (lab step 4), identical for every model:
  faithfulness  deletion_test()        remove each explanation's top-k features -> how much the prediction drops
  stability     lime_stability()       rerun LIME with different seeds -> do we get the same top features?
                shap_rerun_difference() TreeSHAP is exact, so reruns must give identical values
  agreement     rank_agreement()       SHAP vs LIME global rankings; topk_overlap() for single flows
  readability   features_for_share()   how many features an analyst must read; READABILITY_RUBRIC

Every model is handed over as predict_fn: numpy array (n, 68) -> class probabilities (n, 2).
Libraries: shap (Lundberg & Lee 2017; TreeSHAP, Lundberg et al. 2020), lime (Ribeiro et al. 2016).
"""
import itertools

import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer
from scipy.stats import spearmanr

SEED = 42   # was config.SEED in Lab 3; this project has no config module

CLASS_NAMES = ["normal", "attack"]
ATTACK = 1


# ---------------------------------------------------------------------------
# SHAP
# ---------------------------------------------------------------------------
def shap_attack_values(explainer, X):
    """(n, features) SHAP values for the attack class, whatever the model.

    Random Forest: TreeExplainer returns (n, features, 2) in probability units -> take class 1.
    HistGradientBoosting: returns (n, features) in log-odds already. Because the units differ,
    compare models by rank or normalised importance, never by raw SHAP values.
    """
    values = explainer.shap_values(X)
    if isinstance(values, list):                   # older shap: one array per class
        values = values[ATTACK]
    values = np.asarray(values)
    return values[:, :, ATTACK] if values.ndim == 3 else values


def attack_explanation(explainer, X):
    """shap.Explanation for the attack class, ready for shap.plots.beeswarm / bar / waterfall."""
    explanation = explainer(X)
    return explanation[:, :, ATTACK] if explanation.values.ndim == 3 else explanation


def shap_rerun_difference(explainer, X):
    """Largest difference between two SHAP runs on the same rows (0.0 means perfectly stable)."""
    return float(np.max(np.abs(shap_attack_values(explainer, X) - shap_attack_values(explainer, X))))


def importance_table(values, feature_names):
    """Global ranking from per-row attributions (SHAP values or LIME weights), shape (n, features).

    mean_abs = mean absolute attribution; share = mean_abs / total, comparable across models.
    """
    values = np.abs(np.asarray(values, dtype=float))
    mean_abs = values.mean(0)
    table = pd.DataFrame({"feature": list(feature_names), "mean_abs": mean_abs,
                          "share": mean_abs / mean_abs.sum() if mean_abs.sum() > 0 else mean_abs})
    table = table.sort_values("mean_abs", ascending=False, kind="stable").reset_index(drop=True)
    table["rank"] = np.arange(1, len(table) + 1)
    return table


# ---------------------------------------------------------------------------
# LIME
# ---------------------------------------------------------------------------
def make_lime(X_background, feature_names, seed=SEED):
    """LIME explainer. X_background = training rows (TASKLIST: 10,000 rows drawn with seed 42)."""
    return LimeTabularExplainer(np.asarray(X_background, dtype=float), feature_names=list(feature_names),
                                class_names=CLASS_NAMES, discretize_continuous=True,
                                random_state=seed)


def lime_explain(lime, predict_fn, x, num_features=10, num_samples=5000):
    """One flow. Returns the lime Explanation (for exp.as_pyplot_figure(label=1)) and a summary:
    weights (Series over all features, 0 = not picked; positive pushes toward attack),
    conditions (LIME's readable rules, e.g. 'Bwd Packet Length Std > 429.00'),
    score (R^2 of LIME's local linear model), local_pred and model_prob (attack probability)."""
    exp = lime.explain_instance(np.asarray(x, dtype=float), predict_fn, labels=(ATTACK,),
                                num_features=num_features, num_samples=num_samples)
    weights = pd.Series(0.0, index=lime.feature_names)
    for index, weight in exp.as_map()[ATTACK]:
        weights.iloc[index] = weight
    summary = {
        "weights": weights,
        "conditions": exp.as_list(label=ATTACK),
        "score": float(exp.score[ATTACK] if isinstance(exp.score, dict) else exp.score),
        "local_pred": float(np.ravel(exp.local_pred[ATTACK] if isinstance(exp.local_pred, dict)
                                     else exp.local_pred)[0]),
        "model_prob": float(predict_fn(np.asarray(x, dtype=float).reshape(1, -1))[0, ATTACK]),
    }
    return exp, summary


def lime_weights(lime, predict_fn, X_rows, num_features=10, num_samples=5000):
    """LIME on many flows -> DataFrame (rows x features) of weights, 0 = feature not picked.
    LIME's local fit per row is kept in weights.attrs["fit"] (score, local_pred, model_prob)."""
    X_rows = np.asarray(X_rows, dtype=float)
    rows, fits = [], []
    for x in X_rows:
        _, summary = lime_explain(lime, predict_fn, x, num_features, num_samples)
        rows.append(summary["weights"])
        fits.append({k: summary[k] for k in ("score", "local_pred", "model_prob")})
    weights = pd.DataFrame(rows).reset_index(drop=True)
    weights.attrs["fit"] = pd.DataFrame(fits)
    return weights


# ---------------------------------------------------------------------------
# Faithfulness
# ---------------------------------------------------------------------------
def deletion_test(predict_fn, X_rows, rankings, fill_values, ks=(1, 3, 5), seed=SEED):
    """Does removing the features an explanation calls important actually change the prediction?

    rankings: {method name: (n, features) attributions for the same rows}, e.g. {"SHAP": ..., "LIME": ...}.
    For each row, its top-k features (by absolute attribution) are replaced with fill_values (the
    training median) and we measure the drop in the probability of the class the model predicted.
    "random" (k random features) is added as the baseline. A bigger drop = a more faithful explanation.
    Limitation: replaced values can produce unrealistic flows.
    """
    X_rows = np.asarray(X_rows, dtype=float)
    fill_values = np.asarray(fill_values, dtype=float)
    n, d = X_rows.shape
    original = predict_fn(X_rows)
    predicted = original.argmax(1)
    p_before = original[np.arange(n), predicted]
    rng = np.random.default_rng(seed)
    orders = {name: np.argsort(-np.abs(np.asarray(a, dtype=float)), axis=1, kind="stable")
              for name, a in rankings.items()}
    orders["random"] = np.array([rng.permutation(d) for _ in range(n)])

    records = []
    for name, order in orders.items():
        for k in ks:
            masked = X_rows.copy()
            rows = np.repeat(np.arange(n), k)
            cols = order[:, :k].ravel()
            masked[rows, cols] = fill_values[cols]
            p_after = predict_fn(masked)[np.arange(n), predicted]
            drop = p_before - p_after
            records.append({"method": name, "k": k, "mean_drop": drop.mean(), "std_drop": drop.std(),
                            "share_flipped": float(np.mean(predict_fn(masked).argmax(1) != predicted))})
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Stability
# ---------------------------------------------------------------------------
def _top_k(weights, k):
    return set(np.argsort(-np.abs(np.asarray(weights)), kind="stable")[:k])


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def lime_stability(predict_fn, X_background, x, seeds=range(10), k=5, feature_names=None,
                   num_features=10, num_samples=5000):
    """Rerun LIME on the same flow with different seeds.

    jaccard_mean: mean pairwise overlap of the top-k features (1.0 = always the same features);
    weight_cv: spread of the weights of those features across runs (std / |mean|, lower = more stable).
    """
    names = list(feature_names) if feature_names is not None else \
        [f"f{i}" for i in range(np.shape(X_background)[1])]
    runs = []
    for seed in seeds:
        _, summary = lime_explain(make_lime(X_background, names, seed), predict_fn, x, num_features, num_samples)
        runs.append(summary["weights"].to_numpy())
    runs = np.array(runs)
    tops = [_top_k(r, k) for r in runs]
    union = sorted(set().union(*tops))
    mean = runs[:, union].mean(0)
    return {
        "jaccard_mean": float(np.mean([_jaccard(a, b) for a, b in itertools.combinations(tops, 2)])),
        "weight_cv": float(np.mean(runs[:, union].std(0) / np.maximum(np.abs(mean), 1e-12))),
        "top_k_features": [names[i] for i in sorted(set.intersection(*tops))],
        "runs": pd.DataFrame(runs, columns=names),
    }


# ---------------------------------------------------------------------------
# Agreement
# ---------------------------------------------------------------------------
def _as_series(importance):
    if isinstance(importance, pd.DataFrame):
        return importance.set_index("feature")["mean_abs"]
    return pd.Series(importance)


def rank_agreement(importance_a, importance_b, k=5):
    """Agreement of two global rankings (importance_table outputs or Series feature -> importance).

    spearman: rank correlation over all features (1 = same order); top_k_jaccard / top_k_common: overlap
    of the two top-k lists."""
    a, b = _as_series(importance_a), _as_series(importance_b)
    common = a.index.intersection(b.index)
    rho = spearmanr(a[common], b[common]).statistic
    top_a, top_b = set(a.nlargest(k).index), set(b.nlargest(k).index)
    return {"spearman": float(rho), "top_k_jaccard": _jaccard(top_a, top_b),
            "top_k_common": sorted(top_a & top_b)}


def topk_overlap(attribution_a, attribution_b, k=3):
    """For one flow: how many of the top-k features two explanations share (0..k)."""
    return len(_top_k(attribution_a, k) & _top_k(attribution_b, k))


# ---------------------------------------------------------------------------
# Readability
# ---------------------------------------------------------------------------
READABILITY_RUBRIC = {
    "size": "How many features must a person read to follow the explanation? (5 = very few)",
    "terms": "Is it in network terms an analyst knows, like LIME's 'Bwd Packet Length Std > 429', "
             "or as abstract contributions? (5 = plain network terms)",
    "checkable": "Could an analyst check it against the flow record? (5 = directly)",
}


def features_for_share(values, share=0.8):
    """Mean number of features needed to cover `share` of a flow's total absolute attribution.
    The measurable part of readability: fewer features = easier to read."""
    values = np.sort(np.abs(np.asarray(values, dtype=float)), axis=1)[:, ::-1]
    totals = values.sum(1, keepdims=True)
    cumulative = np.divide(values.cumsum(1), totals, out=np.ones_like(values), where=totals > 0)
    return float(np.mean((cumulative < share).sum(1) + 1))
