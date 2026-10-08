# Lab 4.1: Explaining Phishing Detectors

**AI for Cybersecurity (D7084E / D7041E), Group 6** · Kirill Silchenko (kirsil-5@student.ltu.se) · Stefanos Ntentopoulos (stente-5@student.ltu.se) · September 2026

## 1. Problem

A detector that says "this URL is phishing" is only useful to an analyst who can see *why* before
blocking a site or warning users. We build detectors for one question, *is this web address a phishing
site?*, in the three ways from Labs 1–3: **supervised** (every URL labelled), **semi-supervised**
(5% labelled, pseudo-labels for the other 95%) and **self-supervised** (a network first learns from the
URLs alone, then a classifier uses the 5% labels). We then explain them in two ways. **Glass boxes** (a
small tree, a logistic regression) can be read directly. For the **black boxes** (forests, the
self-supervised model) we use **post-hoc** explanations: SHAP and LIME. Finally we turn the two most
important features into a Belief Rule-Based expert system (BRB) and check whether SHAP and LIME agree
with its rules.

## 2. Setup

**Data.** Web Page Phishing Detection (Hannousse & Yahiouche, 2021): 11,430 URLs, exactly half
phishing, 87 features (56 from the URL text, 24 from the page, 7 external lookups). Split 60/20/20,
stratified, `random_state=42`: 6,858 training, 2,286 validation (to choose settings) and 2,286 test URLs
(final scores only; every model is scored on the same test set). **Label budget:** 342 training URLs
(5%, stratified, taken from the training set only) keep their label. The other 6,516 labels are hidden
and are only used to count how many pseudo-labels were right, never for training. We report macro-F1,
recall (share of phishing caught) and FAR (share of legitimate URLs wrongly flagged). Table 1 lists the
models and how each is explained.

*Table 1. Models and explainers.*

| Way of learning | Models | Explained with |
|---|---|---|
| Supervised, all labels | tree (depth 3/4, chosen on validation), logistic regression, forest (300 trees) | rules, weights, SHAP, LIME |
| Semi-supervised, 5% | forest on the 5% (lower line); forest + 3 rounds of pseudo-labels (CUTOFF 0.9) | SHAP TreeExplainer |
| Self-supervised, 5% | logreg on the 5% (lower line); fill-in network (32 units) + logreg on the 5% | SHAP permutation (seed 42) |
| Rules | BRB on the top two SHAP features, 9 rules from training data | the rules, LIME, SHAP |

## 3. Results

*Table 2. All seven detectors on the same 2,286 test URLs.*

[[table A10_test_scores | model, macro_F1, recall, ROC_AUC, FAR | Model, Macro-F1, Recall, ROC-AUC, FAR]]

The forest with all labels is best on every metric (Table 2). With 5% of the labels, the plain forest stays closest
to it. The pseudo-labels were mostly right ({{X1_cutoff_sweep:#3:guess_accuracy:.1%}} of
{{X1_cutoff_sweep:#3:guesses_added}}), but less so each round
({{A8_pseudo_label_rounds:#1:accuracy:.1%}} → {{A8_pseudo_label_rounds:#3:accuracy:.1%}}).

*Table 3. The ten most important features per model: tree importance, absolute logistic-regression weight, and mean |SHAP value| for the three black boxes.*

[[table B4_top10_lists | rank, tree, logreg, SHAP forest, SHAP semi, SHAP self | #, Tree, Logistic regression, SHAP forest (100%), SHAP semi-supervised, SHAP self-supervised | rows=10]]

[[figures results/figures/B2_shap_forest_beeswarm.png ; results/figures/B6_lime_wrong.png | Figure 1. Left: SHAP for the supervised forest on 500 test URLs (one dot per URL; red = high value, right = toward phishing). Right: LIME for the forest's most confident mistake, `graphicsfairy.blogspot.ru` (legitimate, P(phishing) = {{B5_three_urls:wrong:P_phishing}}); LIME fit score {{B6_shap_vs_lime_top3:wrong:LIME_fit_score}}.]]

*Table 4. Testing the detector and the explanation. Ablation: forest without the 7 external features. Stability: how many of 5 LIME runs (seeds 0–4) give the same top-3 features; SHAP gave identical values 5 of 5 times on every URL.*

| Test | Result |
|---|---|
| Ablation, macro-F1 / recall / FAR | with external: {{C1_ablation:with external (87 features):macro_F1}} / {{C1_ablation:with external (87 features):recall}} / {{C1_ablation:with external (87 features):FAR}}; without: {{C1_ablation:without external (80 features):macro_F1}} / {{C1_ablation:without external (80 features):recall}} / {{C1_ablation:without external (80 features):FAR}} |
| New top 5 without external features | `nb_hyperlinks`, `nb_www`, `phish_hints`, `safe_anchor`, `ratio_extHyperlinks` |
| LIME stability (fit score) | surest phishing URL {{X2_lime_stability_three_urls:phishing:LIME_same_top3_of_5:.0f}} of 5 ({{X2_lime_stability_three_urls:phishing:LIME_fit_min:.2f}}); surest legitimate {{X2_lime_stability_three_urls:legitimate:LIME_same_top3_of_5:.0f}} of 5 ({{X2_lime_stability_three_urls:legitimate:LIME_fit_min:.2f}}); the mistake {{X2_lime_stability_three_urls:wrong:LIME_same_top3_of_5:.0f}} of 5 ({{X2_lime_stability_three_urls:wrong:LIME_fit_min:.2f}}) |

**BRB.** The top SHAP feature, `google_index`, is 0/1 and cannot have Low/Medium/High levels, so the
antecedents are the next two: **`page_rank`** (how well-linked the site is) and **`nb_hyperlinks`** (how
many links the page has). To keep the test set for scoring only, this ranking is computed with SHAP on
500 validation URLs; on the test URLs it is the same top 10 in the same order. Referential values are the 5th
percentile, median and 95th percentile of the training data (`page_rank` 0 / 3 / 8, `nb_hyperlinks`
0 / 33 / 325). Each rule's beliefs come from the share of phishing among the training URLs that activate
it; the smallest rule is backed by {{D3_rules:R3:support:.0f}} URLs (Table 5). Table 6 compares the BRB with
models that see the same two features.

*Table 5. The nine belief rules (beliefs in Low / Medium / High phishing risk) and their support in the training data.*

[[table D3_rules | rule, page_rank, nb_hyperlinks, belief_Low, belief_Medium, belief_High, support | Rule, page_rank, nb_hyperlinks, Low, Medium, High, Support]]

*Table 6. The BRB against models that see the same two features, and the full forest (test set).*

[[table D4_brb_scores | model, macro_F1, recall, ROC_AUC, FAR | Model, Macro-F1, Recall, ROC-AUC, FAR]]

## 4. Discussion

**Did the unlabelled data help? No.** The semi-supervised forest is below its lower line (macro-F1
{{A10_test_scores:semi-supervised:macro_F1}} vs {{A10_test_scores:forest (5%):macro_F1}}) and raises
more false alarms (FAR {{A10_test_scores:semi-supervised:FAR}} vs {{A10_test_scores:forest (5%):FAR}}):
the few wrong pseudo-labels cost more than the extra data gains. This does not depend on the cutoff: with
0.85, 0.90 or 0.95 no version beats the forest on the 5% on validation. The self-supervised model is only
slightly above its lower line ({{A10_test_scores:self-supervised:macro_F1}} vs
{{A10_test_scores:logreg (5%):macro_F1}}), a gap that one split and one seed cannot separate from noise.
As the lab warned, a forest is already strong with 342 labels.

**Do the models look at the same clues? Mostly.** `google_index`, `page_rank` and `nb_www` are in all
five top-10 lists (Table 3), and `nb_hyperlinks` and `phish_hints` in four. The tree's first question is "has Google
indexed this page?", and in the beeswarm the red dots of `google_index` (1 = *not* indexed) are on the
right: not being indexed is the forest's strongest reason to say phishing. The two forests share 8 of
their top 10 features, which is expected because the pseudo-labels came from a forest. The self-supervised
model shares only 5 with the forest and adds URL-text features (`nb_hyphens`, `prefix_suffix`,
`shortening_service`). Surprisingly, in its SHAP plot more hyphens push toward *legitimate*. The logistic
regression is the odd one out (top weight `longest_words_raw`) and uses 79 of its 87 weights, so this
"glass box" is harder to read than its top 10 suggests. The tree, with {{A4_tree_depth:#2:leaves:.0f}} leaves, really is readable, but it
misses more attacks (recall {{A10_test_scores:tree:recall}}).

**What does the mistake show?** `graphicsfairy.blogspot.ru` is a real blog on a free hosting service. It is
not indexed by Google, has only 5 links, no "www" and no traffic rank: exactly the profile of a throw-away
phishing page (Figure 1). SHAP and LIME agree on `google_index` and `nb_www` but share only 2 of their top
3 features, and LIME's fit score is below 0.5. On the two URLs with a fit below 0.5, LIME also changed its
top 3 between seeds (Table 4), while SHAP never changed.
The BRB is fooled too (phishing score {{X3_brb_pairs:#1:score_on_mistake_url}}): its two strongest rules,
R4 and R1, both have "few links". A BRB built on a pair chosen by hand, `domain_age` + `length_url`,
is not fooled (score {{X3_brb_pairs:#3:score_on_mistake_url}}, an old domain with a short URL), but it is
much weaker overall (macro-F1 {{X3_brb_pairs:#3:macro_F1}}). Here SHAP chose better features than
intuition, but different features make different mistakes.

**Which top features can an attacker fake?** Everything in the URL text or the page is in the attacker's
hands: adding "www" to the host name (`nb_www`), avoiding words such as "login" (`phish_hints`), or
putting hundreds of hidden links on the page (`nb_hyperlinks`), which would move a phishing page into the
BRB's low-risk "many links" rules. The external lookups (`google_index`, `page_rank`, `web_traffic`,
`domain_age`) are much harder to fake quickly. Without them the forest's macro-F1 falls from
{{C1_ablation:with external (87 features):macro_F1}} to {{C1_ablation:without external (80 features):macro_F1}}
and its FAR rises from {{C1_ablation:with external (87 features):FAR}} to
{{C1_ablation:without external (80 features):FAR}}, and every one of its new top features is one the
attacker controls.

**Which model would we deploy?** The forest with all labels and its SHAP explanations: it is the most
accurate, SHAP TreeExplainer is exact and stable, and the analyst gets a waterfall per alert. We would
run it without waiting for the live lookups as a fast first filter (it still catches
{{C1_ablation:without external (80 features):recall:.0%}} of phishing), and let the full model decide when
the lookups arrive. We would not show LIME explanations with a fit score below 0.5. If labels are
expensive, a plain forest on 5% of the labels comes close (macro-F1 {{A10_test_scores:forest (5%):macro_F1}}
against {{A10_test_scores:forest (100%):macro_F1}}); the unlabelled data did not add anything on top of that.

**The BRB and the explanations.** The rules make sense: R1 (low page rank, few links) is {{D3_rules:R1:belief_High:.2f}} High risk,
R9 (high page rank, many links) {{D3_rules:R9:belief_Low:.2f}} Low, and risk falls when either feature grows. As the lab predicted,
the BRB and a depth-2 tree have almost the same macro-F1 ({{D4_brb_scores:BRB, 2 features:macro_F1}} vs
{{D4_brb_scores:tree (depth 2), 2 features:macro_F1}}), but the tree flags
{{D4_brb_scores:tree (depth 2), 2 features:FAR:.0%}} of legitimate URLs against the BRB's
{{D4_brb_scores:BRB, 2 features:FAR:.0%}}; a security team would prefer the BRB, because an alarm on every
third legitimate site gets ignored. Editing R4 by hand (Medium/High → 0.2/0.8) raises recall to 0.818 but
also FAR to 0.183, and makes the mistake above worse. For the mistake, SHAP agrees with the rules: the few
links push High risk up most (+0.15). LIME (fit 0.74) ranks `page_rank` slightly first, because without
discretisation its weights are local slopes rather than contributions. The BRB reports a large Unknown
(0.315) for this URL. Checking the lab's recursive Evidential Reasoning against the analytical ER algorithm
from our Lab 3 code gave identical phishing scores on all test URLs (difference below 1e-15). But the
analytical version reports no Unknown, so here Unknown means "several rules fire partly" rather than "the
rules disagree".

## 5. Who did what

Kirill Silchenko and Stefanos Ntentopoulos each worked through the complete lab (Parts A–D, the extra
checks and the report), compared the results, and chose this version to hand in.

**Use of AI and sources.** An AI assistant (Claude, by Anthropic, used through Claude Code) was used to
plan the work, write and run the notebook code, and draft this report. We used the lab's example code,
scikit-learn (Pedregosa et al., 2011), SHAP (Lundberg & Lee, 2017), LIME (Ribeiro et al., 2016), the RIMER
BRB method (Yang et al., 2006), the analytical ER algorithm (Wang et al., 2006) as implemented in our
Lab 3 code, and the dataset of Hannousse & Yahiouche (2021, Mendeley Data, doi:10.17632/c2gw7fy2j4.3,
CC BY 4.0).

*References.* Hannousse, A. & Yahiouche, S. (2021). Towards benchmark datasets for machine learning based
website phishing detection: An experimental study. *Engineering Applications of Artificial Intelligence*,
104, 104347. · Lundberg, S. M. & Lee, S.-I. (2017). A unified approach to interpreting model predictions.
*NeurIPS 30*. · Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. *JMLR*, 12,
2825–2830. · Ribeiro, M. T., Singh, S. & Guestrin, C. (2016). "Why should I trust you?" Explaining the
predictions of any classifier. *KDD 2016*. · Wang, Y.-M., Yang, J.-B. & Xu, D.-L. (2006). Environmental
impact assessment using the evidential reasoning approach. *EJOR*, 174(3). · Yang, J.-B., Liu, J., Wang,
J., Sii, H.-S. & Wang, H.-W. (2006). Belief rule-base inference methodology using the evidential reasoning
approach (RIMER). *IEEE Trans. SMC-A*, 36(2).

[[pagebreak]]

## Appendix: code

The notebook `lab4_1_explaining_phishing_detectors.ipynb` runs from top to bottom and writes every number
and figure in this report. Below (Figures 2 and 3): excerpts of two of its cells, the pseudo-labelling with
the check of the guesses against the hidden labels (step A8), and the referential values and data-driven
rules of the BRB (step D3).

[[code A8 1-27 | Figure 2. Step A8, first 27 lines: pseudo-labelling; the hidden labels are only used to count correct guesses.]]

[[code D3 1-24 | Figure 3. Step D3, first 24 lines: referential values from the training data and the nine rules.]]
