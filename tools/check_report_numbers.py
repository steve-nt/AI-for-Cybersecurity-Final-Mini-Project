"""Check that every number in report/Mini_Project_Report.md matches the last notebook runs.

The report states its numbers in plain text, so it stays readable as Markdown. This script holds a check
for each of them, tied to the sentence it appears in, and compares it with:
  - the CSV files the notebooks write to results/tables/ (most numbers: the hand-in notebook for Parts A
    to G, parts/70_extras.ipynb for the additional checks marked "separate notebook" in the report);
  - the printed output of the executed hand-in notebook (a few numbers that are only printed);
  - a short list of settings and design choices (seed, grids, levels), which are not results.

Three kinds of check:
  C(fragment, values...)   the fragment, with the run's values filled in, must appear in the report
  P(fragment, printed)     the fragment must appear in the report and `printed` in the notebook output
  A(fragment, condition)   the fragment must appear in the report and the condition must hold
  S(fragment, reason)      a setting or a fact from outside the runs, with the reason

Finally every number in the report text must be covered by one of these fragments, so a number added
later without a check is reported too.

Run from the repository root after running the hand-in notebook and parts/70_extras.ipynb:
    .venv/bin/python tools/check_report_numbers.py
"""
import itertools
import re
import string
import sys
from pathlib import Path

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results" / "tables"
REPORT = ROOT / "report" / "Mini_Project_Report.md"
NOTEBOOK = ROOT / "mini_project_unsw_nb15.ipynb"


def csv(name, **kw):
    return pd.read_csv(TABLES / f"{name}.csv", **kw)


# --- The tables ----------------------------------------------------------------------------------------
balance = csv("A2_class_balance", index_col="attack_type")
split = csv("A3_split", index_col="attack_type")
base = csv("A4_baseline", index_col="set")
b1_tree = csv("B1_tree_depth")
b1_logreg = csv("B1_logreg_C")
b2_grid = csv("B2_boost_grid")
val = csv("B3_val_scores", index_col="model")
test = csv("B3_test_scores", index_col="model")
alarms = csv("B4_alarms_per_day", index_col="model")
confusion = csv("B4_confusion", index_col="model")
per_type = csv("B4_recall_per_type", index_col="attack_type")
c2_cutoff = csv("C2_cutoff")
c2_rounds = csv("C2_rounds")
c3 = csv("C3_did_it_help_val", index_col=0)
c4 = csv("C4_all_models_test", index_col=0)
d1_values = csv("D1_fingerprint_values")
d1_top = csv("D1_shap_top", index_col="feature")
d2_cases = csv("D2_cases", index_col="case")
d2_fp = csv("D2_fingerprint_check")
d3 = csv("D3_top3", index_col="case")
d3_shap = csv("D3_shap_values", index_col="feature")
d4 = csv("D4_deletion")
d5 = csv("D5_lime_stability", index_col="case")
d6 = csv("D6_investigation")
e1_where = csv("E1_noise_where")
e3 = csv("E3_robustness_all_levels")
e3_stop = csv("E3_stop_trusting")
e4 = csv("E4_whatif_benign_tcp", index_col="model")
f1 = csv("F1_feature_choice")
f3 = csv("F3_brb_comparison")
f4 = csv("F4_beliefs", index_col=0)
f4_trace = (TABLES / "F4_trace.txt").read_text(encoding="utf-8")
f5 = csv("F5_brb_vs_forest_checks")
g2 = csv("G2_hidden", index_col=0)
g3 = csv("G3_adapt_summary", header=[0, 1], index_col=[0, 1])
x2 = csv("X2_did_it_help")
x3 = csv("X3_attack_summary", index_col=["model", "run"])
x3_steps = csv("X3_step_sizes", index_col="feature")
x4 = csv("X4_learning_curve", header=[0, 1], index_col=[0, 1])
x6_clean = csv("X6_clean", index_col=["set", "model"])
x6_noise = csv("X6_noise")
x6_shap = csv("X6_shap_top10", index_col="feature")
x7 = csv("X7_missing_inputs", index_col=["inputs", "model"])
x9_ci = csv("X9_confidence_intervals")
x9_diff = csv("X9_differences")


def one(df, **where):
    """The single row of df where every column equals the given value."""
    mask = pd.Series(True, index=df.index)
    for column, value in where.items():
        mask &= df[column] == value
    assert mask.sum() == 1, f"{where} matches {mask.sum()} rows"
    return df[mask].iloc[0]


def level(test_name, model, value, by="level"):
    return one(e3, test=test_name, model=model, **{by: value})


test_attacks = int(split.loc["All rows", "test"] - split.loc["Benign", "test"])
upper, lower = c4.iloc[3], c4.iloc[4]
pseudo = c4.iloc[5]
rnd = d4[d4["method"] == "random features"].set_index("k")
shp = d4[d4["method"] == "SHAP"].set_index("k")
fit_variants = d6[d6["experiment"].str.startswith("1")]
brb_test = f3[f3["set"] == "test"].set_index("model")
brb, tree2, forest2 = brb_test.iloc[0], brb_test.iloc[1], brb_test.iloc[2]
noise05 = f5[f5["test"] == "noise 0.05"].set_index("model")
w1 = g3.loc[1]
w100 = g3.loc[100]
seen, hidden = g2.iloc[0], g2.iloc[1]
x4_w100_500 = x4.loc[(100, 500)]
x3_b2 = x3.loc[("gradient boosting (B2)", "constrained")]
x3_nofp = x3.loc[("without fingerprint (X6)", "constrained")]
x7_window = x7.loc[("FWD Init Win Bytes missing", "BRB")]
x7_window_boost = x7.loc[("FWD Init Win Bytes missing", "gradient boosting (median filled)")]
boost_ci = one(x9_ci, model="gradient boosting", metric="macro_f1")
boost_vs_tree = one(x9_diff, comparison="gradient boosting minus decision tree", metric="macro_f1")
trace_range = re.search(r"Bwd Packets/s missing:.*?Utility  min ([\d.]+), max ([\d.]+)", f4_trace, re.S)


def stop(test_name, model):
    return one(e3_stop, test=test_name, model=model)


def missing_trusted(model):
    """Most missing features per flow at which the model is still trusted (E3)."""
    last = stop("missing", model)["last_trusted_level"]
    return int(level("missing", model, round(last, 4))["features_missing"])


def gap_closed(recall):
    return (recall - hidden["fuzzers_recall"]) / (seen["fuzzers_recall"] - hidden["fuzzers_recall"])


CHECKS, PRINTED, ASSERTED, SETTINGS = [], [], [], []
C = lambda fragment, *values: CHECKS.append((fragment, values))
P = lambda fragment, printed: PRINTED.append((fragment, printed))
A = lambda fragment, condition: ASSERTED.append((fragment, bool(condition)))
S = lambda fragment, reason: SETTINGS.append((fragment, reason))

# --- 1. Problem and data ---------------------------------------------------------------------------------
S("false alarm rate (FAR) of 1% buries", "an illustration, not a result")
P("We use `Data.csv` (447,915 flows", "Raw rows:                      447,915")
P("with 76 numeric features", "Loaded 447,915 flows x 76 features")
P("Removing 141,742 exact duplicates", "Exact duplicates removed:      141,742")
P("and 1,068 conflicting rows", "Conflicting rows removed:        1,068")
P("**305,105 flows, all of which are used**", "Clean rows (all are used):     305,105")
C("**{:.1%} are attacks**: Exploits {:.1%}, Fuzzers {:.1%}, Reconnaissance {:.1%}, Generic and DoS {:.1%} each",
  balance.loc["All attacks", "clean_share"], balance.loc["Exploits", "clean_share"],
  balance.loc["Fuzzers", "clean_share"], balance.loc["Reconnaissance", "clean_share"],
  balance.loc["Generic", "clean_share"])
C("Generic and DoS {:.1%} each", balance.loc["DoS", "clean_share"])
A("with under 1% each", balance.loc[["Shellcode", "Backdoor", "Analysis", "Worms"], "clean_share"].max() < 0.01)
S("The split is 60/20/20, stratified on the attack type (seed 42)", "settings")
C("{:,.0f} training, {:,.0f} validation and {:,.0f} test flows", *split.loc["All rows", ["train", "validation", "test"]])
P("Nine features that are constant", "Dropped 9 constant columns")
P("leaving 67.", "67 features: 65 continuous")
C("accuracy {:.3f}, recall 0, macro-F1 {:.3f}, PR-AUC {:.3f} (the attack share) and FAR 0",
  base.loc["test", "accuracy"], base.loc["test", "macro_f1"], base.loc["test", "pr_auc"])
A("agree to within 0.003 on every score",
  (val.loc[:, ["macro_f1", "recall", "pr_auc", "far"]] - test.loc[val.index, ["macro_f1", "recall", "pr_auc", "far"]])
  .abs().max().max() <= 0.003)
for name, model in [("Always benign", "always benign"), ("Decision tree", "tree"),
                    ("Logistic regression", "logreg"), ("Gradient boosting", "boosting")]:
    v, t = val.loc[model], test.loc[model]
    if model == "always benign":
        C(f"| {name} | {{:.4f}} / {{:.4f}} | 0 / 0 | {{:.4f}} / {{:.4f}} | 0 / 0 |",
          v["macro_f1"], t["macro_f1"], v["pr_auc"], t["pr_auc"])
    else:
        C(f"| {name} | {{:.4f}} / {{:.4f}} | {{:.4f}} / {{:.4f}} | {{:.4f}} / {{:.4f}} | {{:.4f}} / {{:.4f}} |",
          v["macro_f1"], t["macro_f1"], v["recall"], t["recall"], v["pr_auc"], t["pr_auc"], v["far"], t["far"])
C("and the trivial baseline ({:,.0f} flows each)", split.loc["All rows", "test"])

# --- 2. Method -------------------------------------------------------------------------------------------
S("(scikit-learn 1.6.1 [3], seed 42)", "settings")
S("a 300-tree forest on all training rows took about 8 minutes to train and SHAP on 300 flows over 12 minutes",
  "trial run before the final notebook (487 s to train, 756 s for SHAP), stated as such in the report")
S("trained on a stratified 20% part", "setting")
P("training set (36,612 flows)", "TUNE_IDX: 36,612 training rows")
best = lambda df: df.loc[df["macro_f1"].idxmax()]
A("Tree depth from {3, 5, 8, 12, unlimited}: 12",
  list(b1_tree["max_depth"]) == ["3", "5", "8", "12", "none"] and best(b1_tree)["max_depth"] == "12")
A("Logistic regression `C` from {0.01, 0.1, 1, 10}: 10",
  list(b1_logreg["C"]) == [0.01, 0.1, 1, 10] and best(b1_logreg)["C"] == 10)
A("Boosting learning rate {0.05, 0.1} by leaves per tree {31, 63}: 0.1 and 31",
  best(b2_grid)["learning_rate"] == 0.1 and best(b2_grid)["max_leaf_nodes"] == 31 and len(b2_grid) == 4)
A("All four boosting settings were within 0.001 macro-F1", b2_grid["macro_f1"].max() - b2_grid["macro_f1"].min() <= 0.001)
C("We keep the labels of 10% of the training flows ({:,.0f}, stratified)", round(0.1 * split.loc["All rows", "train"]))
C("boosting trained on those {:,.0f} flows alone", round(0.1 * split.loc["All rows", "train"]))
S("for two rounds", "setting")
A("The cutoff (0.99, 0.95 or 0.90) was chosen on validation: 0.95",
  list(c2_cutoff["cutoff"]) == [0.99, 0.95, 0.9] and best(c2_cutoff)["cutoff"] == 0.95)
S("with the engine from our Lab 3", "name of a course lab")
S("training 5th percentile, median and 95th percentile); 3 × 3 = 9 rules", "design of the rule base")
S("(utility: Low 0, Medium 50, High 100, Unknown counted halfway)", "design of the rule base")
P("was chosen on validation: 48.5", "Chosen threshold: utility >= 48.5")

# --- 3. Results ------------------------------------------------------------------------------------------
C("| Model (test set, {:,.0f} flows) |", split.loc["All rows", "test"])
rows3 = [("Always benign (trivial baseline)", c4.iloc[0]), ("Decision tree, all labels", c4.iloc[1]),
         ("Logistic regression, all labels", c4.iloc[2]), ("Gradient boosting, 10% labels (lower line)", lower),
         ("Gradient boosting, 10% labels + pseudo-labels", pseudo), ("BRB, 2 features, 9 rules", brb),
         ("Decision tree, same 2 features (depth 4)", tree2), ("Random forest, same 2 features (100 trees)", forest2)]
for name, r in rows3:
    C(f"| {name} | {{:.3f}} | {{:.3f}} | {{:.3f}} | {{:.3f}} |", r["macro_f1"], r["recall"], r["pr_auc"], r["far"])
C("| **Gradient boosting, all labels (upper line)** | **{:.3f}** | {:.3f} | **{:.3f}** | **{:.3f}** |",
  upper["macro_f1"], upper["recall"], upper["pr_auc"], upper["far"])
C("Gradient boosting is best, but only just: {:.3f} macro-F1 above the decision tree",
  test.loc["boosting", "macro_f1"] - test.loc["tree", "macro_f1"])
C("({:,} against {:,} for boosting)", int(confusion.loc["logreg", "true_benign_called_attack"]),
  int(confusion.loc["boosting", "true_benign_called_attack"]))
C("Recall is at least {:.3f} for every attack type and model",
  per_type.drop("Benign")[["boosting", "tree", "logreg"]].min().min())
C("boosting's weakest large type is Fuzzers ({:.3f})", per_type.loc["Fuzzers", "boosting"])
fuzzers_missed = round(per_type.loc["Fuzzers", "test_flows"] * (1 - per_type.loc["Fuzzers", "boosting"]))
C("about half of the {:,} attacks it misses", int(confusion.loc["boosting", "true_attack_called_benign"]))
A("which accounts for about half of the", 0.4 <= fuzzers_missed / confusion.loc["boosting", "true_attack_called_benign"] <= 0.6)
S("(200 resamples, in the separate notebook", "setting of the bootstrap")
S("gives 95% intervals", "the confidence level of the bootstrap intervals")
C("intervals of about ±{:.3f} on macro-F1", (boost_ci["ci_high"] - boost_ci["ci_low"]) / 2)
C("so the {:.3f} lead over the tree is small but real", boost_vs_tree["difference"])
A("lead over the tree is small but real", boost_vs_tree["ci_low"] > 0)
P("only 2.53% of flows are attacks", "Real traffic: 2.53% attacks; 1,000,000 flows per day")
C("only 2.53% of flows are attacks, not {:.0%}", balance.loc["All attacks", "clean_share"])
P("In a network with 1,000,000 flows a day", "1,000,000 flows per day")
C("boosting would catch about {:,.0f} attacks but raise about {:,.0f} false alarms",
  round(alarms.loc["boosting", "caught_per_day"], -2), round(alarms.loc["boosting", "false_alarms_per_day"], -2))
C("only **{:.0%} of its alerts would be real**, against {:.0%} on our test set",
  alarms.loc["boosting", "precision_real_traffic"], alarms.loc["boosting", "precision_test_set"])
S("Losing 90% of the labels", "the 10% setting of Part C")
C("costs only {:.3f} macro-F1 (Table 2)", upper["macro_f1"] - lower["macro_f1"])
C("raised validation macro-F1 from {:.4f} to {:.4f} ({:.0%} of the gap",
  c3.iloc[0]["macro_f1"], c3.iloc[1]["macro_f1"], c3.loc["share of the gap closed", "macro_f1"])
C("({:.4f} against {:.4f})", pseudo["macro_f1"], lower["macro_f1"])
C("recall rose by {:.3f} to {:.3f}", pseudo["recall"] - lower["recall"], c3.loc["pseudo-labelling minus lower line", "recall"])
r1 = one(c2_rounds, cutoff=0.95, round=1)
r2 = one(c2_rounds, cutoff=0.95, round=2)
C("in the first round {:,} were added and {:.1%} were right", int(r1["added"]), r1["guesses_right"])
C("({:,} benign)", int(r1["added_benign"]))
C("only {:.0%} of those guesses were right", r2["guesses_right"])
x2_test = one(x2, labels="1% (1,830)", set="test")
S("with 1% of the labels (1,830 flows)", "the 1% budget of the additional check: 1% of 183,063 training flows")
C("a small real gain (+{:.3f} macro-F1, +{:.3f} recall)", x2_test["macro_f1"], x2_test["recall"])

# --- 4. Explanation --------------------------------------------------------------------------------------
P("on 1,000 validation flows (Figure 1)", "The 1,000 flows: 260 attacks, 740 benign")
C("three features carry {:.0%} of the model's SHAP weight: `Fwd Seg Size Min` ({:.0%}), `FWD Init Win Bytes` ({:.0%}) and `Bwd Packets/s` ({:.0%})",
  d1_top.iloc[2]["cumulative_share"], *d1_top["share_of_total"].iloc[:3])
fp20 = one(d1_values, feature="Fwd Seg Size Min", value=20)
fp32 = one(d1_values, feature="Fwd Seg Size Min", value=32)
C("{:.0%} of flows with `Fwd Seg Size Min` = 20 are attacks and {:.0%} of those with 32",
  fp20["attack_share"], fp32["attack_share"])
P("95% of all training attacks (45,850 of 48,154) announce a window of exactly 16,383 bytes",
  "Training attacks with FWD Init Win Bytes = 16,383: 45,850 of 48,154 (95.2%)")
C("attack with probability {:.3f}**", d2_cases.loc["mistake", "attack_probability"])
C("(`Fwd Seg Size Min` = {:.0f}, window {:,.0f})", d2_cases.loc["mistake", "Fwd Seg Size Min"],
  d2_cases.loc["mistake", "FWD Init Win Bytes"])
C("these two values alone add +{:.1f} and +{:.1f} log-odds", d3_shap.loc["Fwd Seg Size Min", "mistake"],
  d3_shap.loc["FWD Init Win Bytes", "mistake"])
fp_benign = one(d2_fp, **{"test flows with": "fingerprint", "true label": "benign"})
C("{:,.0f} of the {:,} false alarms", fp_benign["flows"] * fp_benign["called attack"],
  int(confusion.loc["boosting", "true_benign_called_attack"]))
C("(fast replies, −{:.1f})", -d3_shap.loc["Bwd Packets/s", "negative"])
for name, label in [("detection", "Detection (Exploits, p = {:.4f})"), ("mistake", "Mistake (benign, p = {:.4f})")]:
    C(f"| {label} |", d3.loc[name, "attack_probability"])
A("| Negative (benign, p ≈ 0) |", d2_cases.loc["negative", "attack_probability"] < 1e-4)
for name in ["detection", "negative", "mistake"]:
    C(f"| {{:d}} | {{:.2f}} |", int(d3.loc[name, "shared_in_top3"]), d3.loc[name, "LIME_fit_score"])
C("SHAP values of gradient boosting on {:,} validation flows", 1000)
C("a benign test flow called an attack with probability {:.4f}", d2_cases.loc["mistake", "attack_probability"])
P("from the average output (−6.73 log-odds)", "Base value (average model output): -6.73 log-odds")
S("In a deletion test on 500 test flows called attacks", "setting of the deletion test")
C("lowered the attack probability by {:.3f} on average and **flipped {:.0%} of the decisions**",
  shp.loc[1, "mean_drop"], shp.loc[1, "share_flipped"])
C("one random feature lowered it by {:.3f} ({:.1%} flipped), ten random features by {:.3f} ({:.1%})",
  rnd.loc[1, "mean_drop"], rnd.loc[1, "share_flipped"], rnd.loc[10, "mean_drop"], rnd.loc[10, "share_flipped"])
S("for all 500 flows", "setting of the deletion test")
C("and its median, {:.0f}, is the benign machines' value", eval(one(f1, feature="Fwd Seg Size Min")["percentiles_5_50_95"])[1])
S("run 10 times with seeds 0 to 9", "setting")
C("in {:.0f}, {:.0f} and {:.0f} runs of 10", *(d5["same_top3_as_most_common"] * 10))
C("(1 to {:.0f} of 3 shared features)", d3["shared_in_top3"].max())
A("(1 to 2 of 3 shared features)", d3["shared_in_top3"].min() == 1)
C("put the attacker window {:,.0f} and the benign {:,.0f} into neighbouring ranges",
  one(d1_values, feature="FWD Init Win Bytes", value=16383)["value"],
  one(d1_values, feature="FWD Init Win Bytes", value=5792)["value"])
P("put the attacker window 16,383 and the benign 5,792", "5792.00 < FWD Init Win Bytes <= 16383.00")
P("the values 8 and 20 into one range", "Fwd Seg Size Min <= 20.00")
S("(20,000 instead of 5,000)", "settings of the samples experiment")
C("the differing features correlate at most {:.2f}", d6["abs_correlation"].max())
C("LIME's R² stayed between {:.2f} and {:.2f} in every variant", fit_variants["fit_score"].min(),
  fit_variants["fit_score"].max())
C("its own prediction for the detection was {:.2f} where the model says {:.2f}",
  d3.loc["detection", "LIME_local_prediction"], d3.loc["detection", "attack_probability"])
S("(changing one TCP value flips it from 1 to 0)", "probabilities 1 and 0 as words for the switch")

# --- 5. Robustness ---------------------------------------------------------------------------------------
P("on the 65 continuous features of the test set", "67 features: 65 continuous")
noise_levels = sorted(e3.loc[(e3["test"] == "noise") & (e3["level"] > 0), "level"].unique())
miss_counts = sorted(e3.loc[(e3["test"] == "missing") & (e3["features_missing"] > 0), "features_missing"].unique())
C("at {:d} noise levels from {:g} to {:g} and at {:d} to {:d} missing features per flow",
  len(noise_levels), noise_levels[0], noise_levels[-1], int(miss_counts[0]), int(miss_counts[-1]))
S("clipped at 0", "setting of the noise: no negative values")
S("recall more than 0.05 below the clean value, or FAR more than twice the clean value",
  "the trust rule, fixed before the tests")
S("| Recall, noise 0.001 | Noise 0.05 | Noise 0.2 | Last noise level trusted | Recall, 2 / 7 / 34 missing |",
  "levels shown in Table 4")
for name, model in [("Gradient boosting", "boosting"), ("Decision tree", "tree"), ("Logistic regression", "logreg")]:
    trusted = stop("noise", model)["last_trusted_level"]
    trusted_text = "none" if trusted == 0 else f"{trusted:g}"
    C(f"| {name} | {{:.3f}} | {{:.3f}} | {{:.3f}} | {trusted_text} | {{:.3f}} / {{:.3f}} / {{:.3f}} | {{:d}} |",
      level("noise", model, 0.001)["recall"], level("noise", model, 0.05)["recall"],
      level("noise", model, 0.2)["recall"], level("missing", model, 2, by="features_missing")["recall"],
      level("missing", model, 7, by="features_missing")["recall"],
      level("missing", model, 34, by="features_missing")["recall"], missing_trusted(model))
C("(clean recall {:.3f}, {:.3f} and {:.3f})", test.loc["boosting", "recall"], test.loc["tree", "recall"],
  test.loc["logreg", "recall"])
S("Noise of one thousandth of a standard deviation", "the level 0.001 in words")
C("halves boosting's recall ({:.3f} to {:.3f})", test.loc["boosting", "recall"], level("noise", "boosting", 0.001)["recall"])
C("logistic regression stays at {:.2f} up to noise {:g}", level("noise", "logreg", 0.02)["recall"],
  stop("noise", "logreg")["last_trusted_level"])
P("isolate a window between 16,368.5 and 16,406.5", "FWD Init Win Bytes <= 16406.5")
P("a window between 16,368.5", "FWD Init Win Bytes <= 16368.5")
tcp_only = e1_where[e1_where["noise at level 0.05 on"].str.startswith("only")].set_index("model")
tcp_except = e1_where[e1_where["noise at level 0.05 on"].str.startswith("all except")].set_index("model")
C("cut boosting's recall to {:.2f} at level 0.05; noise on all other features to {:.2f}",
  tcp_only.loc["boosting", "recall"], tcp_except.loc["boosting", "recall"])
P("69% of the SHAP weight", "69.1%")
C("Giving all {:,} test attacks", test_attacks)
P("(`Fwd Seg Size Min` = 32, window 5,792)", "{'Fwd Seg Size Min': 32.0, 'FWD Init Win Bytes': 5792.0}")
C("drops recall to **{:.3f} for boosting**, {:.3f} for the tree and {:.3f} for logistic regression",
  *e4.loc[["boosting", "tree", "logreg"], "recall, attacks with benign TCP settings"])
C("evades boosting for all {:.0f} attacks it tried", x3_b2["evaded"])
A("one change to `Fwd Seg Size Min` evades boosting", x3_b2["mean_features_changed"] == 1 and x3_b2["evaded_share"] == 1)

# --- 6. Adaptability -------------------------------------------------------------------------------------
C("({:,.0f} flows, a third of the training attacks)", split.loc["Fuzzers", "train"])
A("a third of the training attacks", 0.3 <= split.loc["Fuzzers", "train"] / (split.loc["All rows", "train"] - split.loc["Benign", "train"]) <= 0.36)
C("On the {:,.0f} Fuzzers test flows, recall fell from **{:.3f} to {:.3f}**; overall recall from {:.3f} to {:.3f}",
  split.loc["Fuzzers", "test"], seen["fuzzers_recall"], hidden["fuzzers_recall"], seen["overall_recall"],
  hidden["overall_recall"])
C("barely moved ({:.3f} to {:.3f})", seen["other_attacks_recall"], hidden["other_attacks_recall"])
C("The FAR *fell* ({:.3f} to {:.3f})", seen["far"], hidden["far"])
C("{:.0%} of the Fuzzers flows got an attack probability between 0.1 and 0.9, against {:.0%} before",
  hidden["fuzzers_uncertain_share"], seen["fuzzers_uncertain_share"])
S("An analyst labels 50 or 100 Fuzzers flows", "settings of the adaptation")
C("barely help: {:.3f} with 50 labels and {:.3f} with 100", w1.loc[50, ("fuzzers_recall", "mean")],
  w1.loc[100, ("fuzzers_recall", "mean")])
C("**Weighted** 100 times, the same 100 labels raise Fuzzers recall to **{:.3f}** ({:.3f} to {:.3f} over the draws) and overall recall to {:.3f}, with FAR {:.3f}",
  w100.loc[100, ("fuzzers_recall", "mean")], w100.loc[100, ("fuzzers_recall", "min")],
  w100.loc[100, ("fuzzers_recall", "max")], w100.loc[100, ("overall_recall", "mean")], w100.loc[100, ("far", "mean")])
C("*Figure 4. Recall on the {:,.0f} Fuzzers test flows after adding 50 or 100 labelled Fuzzers flows to training, with weight 1, 10 or 100 (mean and range of 3 draws). Dotted: never seen; dashed: trained with all {:,.0f}.*",
  split.loc["Fuzzers", "test"], split.loc["Fuzzers", "train"])
A("100 weighted labels recover more than half", gap_closed(w100.loc[100, ("fuzzers_recall", "mean")]) > 0.5)
C("but not all of it ({:.3f} against {:.3f})", w100.loc[100, ("fuzzers_recall", "mean")], seen["fuzzers_recall"])
C("500 labels weighted 100 times reach {:.3f} (FAR {:.3f},", x4_w100_500[("fuzzers_recall", "mean")],
  x4_w100_500[("far", "mean")])
A("25 weighted labels already beat 250 unweighted ones",
  x4.loc[(100, 25), ("fuzzers_recall", "mean")] > x4.loc[(1, 250), ("fuzzers_recall", "mean")])

# --- 7. Discussion ---------------------------------------------------------------------------------------
C("The data hold {:.0%} attacks; real traffic about {:.1%}", balance.loc["All attacks", "clean_share"],
  alarms.loc["boosting", "attacks_per_day"] / 1_000_000)
C("The baseline's {:.3f} accuracy", base.loc["test", "accuracy"])
C("({:.0%} of alerts real) shows that our test-set precision of {:.0%}",
  alarms.loc["boosting", "precision_real_traffic"], alarms.loc["boosting", "precision_test_set"])
C("All three models reach macro-F1 {:.2f} to {:.2f}", test.drop("always benign")["macro_f1"].min(),
  test.drop("always benign")["macro_f1"].max())
C("The black box buys only {:.3f} over a readable tree", test.loc["boosting", "macro_f1"] - test.loc["tree", "macro_f1"])
S("depth-12 tree", "chosen setting, checked in Section 2")
S("10% of the labels are almost as good", "the Part C setting")
S("With 1% of the labels it gave", "the 1% budget of the additional check")
C("the BRB is {:.3f} macro-F1 behind a tree and a forest", tree2["macro_f1"] - brb["macro_f1"])
C("cannot isolate the exact window {:,.0f}", d2_cases.loc["mistake", "FWD Init Win Bytes"])
present, missing = f4.loc["all inputs present"], f4.loc["Bwd Packets/s missing"]
C("belief Low {:.2f}, Medium {:.2f}, High {:.2f} and Unknown {:.4f} (utility {:.1f},",
  present["Low"], present["Medium"], present["High"], present["Unknown"], present["utility"])
C("than boosting's {:.3f})", d2_cases.loc["mistake", "attack_probability"])
C("Unknown rose to {:.2f} and the utility became a range, {:.1f} to {:.1f}", missing["Unknown"],
  float(trace_range.group(1)), float(trace_range.group(2)))
C("at noise 0.05 its macro-F1 is {:.3f}, against {:.3f} for the 2-feature tree and {:.3f} for the forest",
  noise05.loc["BRB", "macro_f1"], noise05.loc["tree, 2 features", "macro_f1"], noise05.loc["forest, 2 features", "macro_f1"])
S("(rules grow as 3 to the power", "the 3 levels of the rule base")
C("leaves the BRB unable to decide {:.0%} of the flows", x7_window["cannot_decide"])
C("misses {:.0%} of the attacks with no sign of doubt", 1 - x7_window_boost["recall"])
C("cost {:.0f} points of recall", -100 * g2.loc["difference", "fuzzers_recall"])
C("five hundred about {:.0%}", round(gap_closed(x4_w100_500[("fuzzers_recall", "mean")]), 1))
A("A hundred weighted labels recovered half of the loss", 0.45 <= gap_closed(w100.loc[100, ("fuzzers_recall", "mean")]) <= 0.6)
with_fp = x6_clean.loc[("test", "with fingerprint (67 features)")]
without_fp = x6_clean.loc[("test", "without fingerprint (64 features)")]
C("test macro-F1 {:.3f} instead of {:.3f}, recall at noise 0.001 {:.3f} instead of {:.3f}",
  without_fp["macro_f1"], with_fp["macro_f1"], one(x6_noise, level=0.001, model="without fingerprint")["recall"],
  one(x6_noise, level=0.001, model="with fingerprint")["recall"])
C("(`Bwd Packets/s`, {:.0%} of the weight)", x6_shap.loc["Bwd Packets/s", "share_of_shap_weight"])
C("still makes **{:.0f} of 50** caught attacks look benign", x3_nofp["evaded"])
A("most with two or three cheap changes", x3_nofp["evaded_with_2_or_3_changes"] > x3_nofp["evaded"] / 2)
A("waiting about 10 ms longer", 9.5 <= x3_steps.loc["Fwd IAT Min", "step"] / 1000 <= 11)
A("in two thirds of the attacks tried", 0.6 <= x3_nofp["evaded_share"] <= 0.73)
C("**The {:.3f} macro-F1 itself**", test.loc["boosting", "macro_f1"])
C("**The {:.3f} FAR**", test.loc["boosting", "far"])
C("from a {:.0%} attack share; at a realistic {:.1%}", balance.loc["All attacks", "clean_share"],
  alarms.loc["boosting", "attacks_per_day"] / 1_000_000)
A("more than half of the alerts would be false", alarms.loc["boosting", "precision_real_traffic"] < 0.5)
C("(Worms {:.0f} test flows, Analysis {:.0f}, Backdoor {:.0f})", split.loc["Worms", "test"],
  split.loc["Analysis", "test"], split.loc["Backdoor", "test"])
A("one flow moves the score by one to two points", 1 <= 100 / split.loc["Backdoor", "test"] and 100 / split.loc["Worms", "test"] <= 2.2)
C("with fit scores of {:.2f} to {:.2f}", fit_variants["fit_score"].min(), fit_variants["fit_score"].max())
S("The data were also recorded in 2015", "year of the recording [2]")


# --- Checking ----------------------------------------------------------------------------------------------
def candidates(spec, value):
    """The texts the report may use for one value: the value itself and, for a value read from a CSV
    with 4 decimals, the two neighbours half a unit of the 4th decimal away (the CSV rounding)."""
    out = {format(value, spec)}
    if isinstance(value, float) and not spec.endswith("d"):
        out |= {format(value + 5e-5, spec), format(value - 5e-5, spec)}
    return out


def expand(fragment, values):
    """Every way the fragment may read with the run's values filled in."""
    pieces = list(string.Formatter().parse(fragment))
    fields = [p for p in pieces if p[1] is not None]
    assert len(fields) == len(values), f"{fragment!r}: {len(fields)} fields, {len(values)} values"
    options = [sorted(candidates(spec, v.item() if hasattr(v, "item") else v))
               for (_, _, spec, _), v in zip(fields, values)]
    for combo in itertools.product(*options):
        texts = iter(combo)
        yield "".join(literal + (next(texts) if field is not None else "") for literal, field, _, _ in pieces)


def flat(text):
    return re.sub(r"\s+", " ", text)


def report_body(text):
    """The report text that holds numbers to check: no title line, no references, no image lines."""
    text = text.split("\n## References")[0]
    lines = [line for line in text.splitlines()[3:] if not line.startswith("![")]
    return flat("\n".join(lines))


# A number: optional sign, digits with thousands commas, decimals, optional %. Not part of a word or name.
NUMBER = re.compile(r"(?<![\w.])[−+±]?\d+(?:,\d{3})*(?:\.\d+)?%?(?![\w])")
# Numbers that are labels, not values: section and step numbers, citations, enumerations.
LABELS = re.compile(r"(?:Table|Figure|Section|Sections|##) \d+\.?|\[\d+(?:, \d+)*\]|\(\d\) |Part [A-G]|top[ -]3")


def main():
    report = report_body(REPORT.read_text(encoding="utf-8"))
    outputs = ""
    for cell in nbformat.read(NOTEBOOK, as_version=4).cells:
        if cell.cell_type == "code":
            for out in cell.get("outputs", []):
                outputs += out.get("text", "") + str(out.get("data", {}).get("text/plain", ""))

    problems, covered = [], []

    def find(fragment):
        start = report.find(flat(fragment))
        if start >= 0:
            covered.append((start, start + len(flat(fragment))))
        return start >= 0

    for fragment, values in CHECKS:
        options = list(expand(fragment, values))
        if not any(find(text) for text in options):
            problems.append(f"value: the run gives {options[0]!r}; not found in the report")
    for fragment, printed in PRINTED:
        if not find(fragment):
            problems.append(f"printed: {fragment!r} not found in the report")
        if printed not in outputs:
            problems.append(f"printed: {printed!r} not found in the notebook output")
    for fragment, condition in ASSERTED:
        if not find(fragment):
            problems.append(f"claim: {fragment!r} not found in the report")
        elif not condition:
            problems.append(f"claim: {fragment!r} does not hold for the run")
    for fragment, _ in SETTINGS:
        if not find(fragment):
            problems.append(f"setting: {fragment!r} not found in the report")

    labels = [(m.start(), m.end()) for m in LABELS.finditer(report)]
    unchecked = []
    for m in NUMBER.finditer(report):
        inside = lambda spans: any(a <= m.start() and m.end() <= b for a, b in spans)
        if not inside(covered) and not inside(labels):
            unchecked.append(f"{m.group()!r} in ...{report[max(0, m.start() - 50):m.end() + 30]}...")

    total = len(list(NUMBER.finditer(report)))
    print(f"Checked {len(CHECKS)} values from results/tables/, {len(PRINTED)} printed values, "
          f"{len(ASSERTED)} claims and {len(SETTINGS)} settings; {total} numbers in the report text.")
    if unchecked:
        problems += [f"unchecked number: {u}" for u in unchecked]
    if problems:
        print(f"{len(problems)} PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("Every number in the report is checked, and all match the last runs.")


if __name__ == "__main__":
    main()
