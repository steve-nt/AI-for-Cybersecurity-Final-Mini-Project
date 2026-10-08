"""Tests for the explanation toolkit (TASK T7), on small synthetic models so they run in seconds.

The attack label depends only on features 0 and 1, so a working toolkit must rank those two first.

Run:  python -m pytest src/test_xai_tools.py
"""
import numpy as np
import pytest
import shap
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier

import xai_tools

NAMES = [f"f{i}" for i in range(6)]


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(3000, 6))
    y = ((X[:, 0] + 0.8 * X[:, 1]) > 0.5).astype(int)
    return X, y


@pytest.fixture(scope="module", params=["rf", "hgb"])
def model(request, data):
    X, y = data
    if request.param == "rf":
        return RandomForestClassifier(n_estimators=30, max_depth=6, random_state=42).fit(X, y)
    return HistGradientBoostingClassifier(max_iter=60, random_state=42).fit(X, y)


def test_shap_values_and_importance(model, data):
    X, _ = data
    explainer = shap.TreeExplainer(model)
    values = xai_tools.shap_attack_values(explainer, X[:200])
    assert values.shape == (200, 6)                      # one shape for RF (n, 6, 2) and HGB (n, 6)
    table = xai_tools.importance_table(values, NAMES)
    assert set(table.feature[:2]) == {"f0", "f1"}
    assert table["share"].sum() == pytest.approx(1.0) and list(table["rank"]) == list(range(1, 7))
    assert xai_tools.attack_explanation(explainer, X[:5]).values.shape == (5, 6)
    assert xai_tools.shap_rerun_difference(explainer, X[:50]) == 0.0


def test_lime_faithfulness_stability_agreement(model, data):
    X, _ = data
    lime = xai_tools.make_lime(X[:1000], NAMES)
    exp, summary = xai_tools.lime_explain(lime, model.predict_proba, X[0], num_features=4, num_samples=500)
    assert len(summary["weights"]) == 6 and (summary["weights"] != 0).sum() == 4
    assert 0 <= summary["model_prob"] <= 1 and summary["conditions"]

    weights = xai_tools.lime_weights(lime, model.predict_proba, X[:20], num_features=4, num_samples=500)
    assert weights.shape == (20, 6) and len(weights.attrs["fit"]) == 20
    lime_table = xai_tools.importance_table(weights, NAMES)
    shap_values = xai_tools.shap_attack_values(shap.TreeExplainer(model), X[:20])
    shap_table = xai_tools.importance_table(shap_values, NAMES)
    agreement = xai_tools.rank_agreement(shap_table, lime_table, k=2)
    assert agreement["top_k_common"] == ["f0", "f1"] and -1 <= agreement["spearman"] <= 1
    assert 0 <= xai_tools.topk_overlap(shap_values[0], weights.iloc[0], k=3) <= 3

    faith = xai_tools.deletion_test(model.predict_proba, X[:20], {"SHAP": shap_values, "LIME": weights},
                                    np.median(X, axis=0), ks=(1, 2))
    assert set(faith.method) == {"SHAP", "LIME", "random"} and len(faith) == 6
    at_2 = faith[faith.k == 2].set_index("method")["mean_drop"]
    assert at_2["SHAP"] > at_2["random"]               # removing the real signal hurts more than noise

    stability = xai_tools.lime_stability(model.predict_proba, X[:1000], X[0], seeds=range(4), k=2,
                                         feature_names=NAMES, num_features=4, num_samples=500)
    assert 0 <= stability["jaccard_mean"] <= 1 and stability["runs"].shape == (4, 6)


def test_features_for_share():
    assert xai_tools.features_for_share([[10, 0, 0], [1, 1, 1]], share=0.8) == pytest.approx((1 + 3) / 2)
