# Changelog

History of the changes made in this project, oldest first. Each entry says what changed, why,
and when. New entries are appended at the bottom.

## 2026-10-07 19:48 EEST: Added dataset choice note

**What**
- `Dataset_Choice.md`: created. Recommends NSL-KDD as the easiest dataset for the mini project, with the reasons, the catches (old data, categorical columns, which attack to hide in Part G) and why the other suggested datasets are harder.

**Why**
The user asked which suggested dataset is the easiest option and wanted the answer saved as a Markdown file.

## 2026-10-08 21:00 EEST: Rewrote dataset choice for UNSW-NB15

**What**
- `Dataset_Choice.md`: rewritten. It now recommends UNSW-NB15 over CIC-DDoS2019, with a size and format comparison, the UNSW-NB15 label counts, why it suits each part of the brief, things to watch (use `Data.csv` not `CICFlowMeter_out.csv`, this is the CICFlowMeter version of UNSW-NB15, inf values, state the subsample) and why CIC-DDoS2019 is harder.

**Why**
The group has the UNSW-NB15 and CIC-DDoS2019 datasets locally, not NSL-KDD. After inspecting both folders, UNSW-NB15 is faster and easier to explain, and the user asked for the file to be rewritten for it.

## 2026-10-09 00:20 EEST: Task list, project layout and files copied from earlier labs

**What**
- `TASKLIST.md`: created. Step-by-step tasks for Parts A–G of the brief plus setup, optional extras, presentation and hand-in. Includes a plain-language glossary (programming, security, ML, metrics, SHAP/LIME, BRB, adaptability), facts about the UNSW-NB15 data, results of a trial run, decisions already made, the parallel workflow (part notebooks, step markers, stand-ins, shared names, the test-set rule, git), five work tracks with mappings for 2–4 people, sync points and a day-by-day plan up to 15 Oct, a grading checklist and questions for the teacher.
- Copied from the earlier labs so the project does not depend on `PreviousLabs/`:
  - `requirements.txt` (Lab 4.2; header retitled, `pytest==9.1.1` added for the unit tests)
  - `tools/assemble.py`, `tools/feature_glossary.py`, `tools/check_report_numbers.py` (Lab 4.2, unchanged; the task list says what to edit)
  - `src/brbes.py`, `src/test_brbes.py`, `src/test_xai_tools.py` (Lab 3, unchanged); `src/xai_tools.py` (Lab 3, `import config` replaced by a local `SEED = 42`, because this project has no config module)
  - `report/build_report.py`, `report/build_docx.py`, `report/title_page_template.docx`, `report/fonts/` (Lab 4.2, unchanged)
  - `reference/lab4_1_phishing/` (Lab 4.1 part notebooks and report) and `reference/lab4_2_robustness/` (Lab 4.2 part notebooks, README, report, references), as read-only code examples
- Created empty folders `parts/`, `results/figures/`, `results/tables/`, `report/figures/` (each with `.gitkeep`).
- `.gitignore`: rewritten for this project (data folders `UNSW-NB15/` and `CIC-DDoS2019/`, `PreviousLabs/`, environment and cache folders); removed the Lab 4.2 lines about `data/processed`, `data/raw` and `models/`.
- `Dataset_Choice.md`: corrected three claims after checking the data. `CICFlowMeter_out.csv` holds all 3,540,241 flows, not the same rows as `Data.csv` (which keeps all attacks and about 10% of benign flows). There are no infinite values, but there are 141,742 duplicate rows, 1,068 conflicting rows and 9 constant columns. The Part G advice now recommends Fuzzers instead of Reconnaissance.

**Why**
The user asked for a task list that people with no background can follow, split so several people can work at once, and for everything needed from `PreviousLabs/` to be copied into this folder. Before writing it, the data was profiled and a trial pipeline was run (5,000-row sample, 60/20/20 split, forest, SHAP, hidden attack types) so that the task list gives real counts. The trial showed that hiding Reconnaissance barely lowers its recall (0.974), while hiding Fuzzers drops it to 0.859, so the plan hides Fuzzers. Global SHAP is computed on validation rows so that the Part F feature choice never uses the test set.

**Verified**
`python -m pytest src` passes (16 tests) in a temporary environment built from `requirements.txt`. The split counts, the 66 features and the 300/2,700 label split in the task list come from the trial run. The trial scripts and the temporary environment were in `/tmp` and have been deleted.

## 2026-10-09 08:05 EEST: Task list updated for one person and all rows; dataset citation checked

**What**
- `TASKLIST.md`: rewritten for a one-person group using all 305,105 clean rows. Tracks, branches and sync points replaced by one order of work and a day-by-day plan. Black box changed from random forest to gradient boosting (`HistGradientBoostingClassifier`), with `BOOST_SETTINGS`, `make_boost()` and `boost` as the shared names. Logistic regression moved to an optional extra. Settings searches train candidates on a stratified 20% part of the training set (`TUNE_IDX`) and score them on validation. All counts, split sizes and trial numbers updated to the full data; time budget per part added. Part D notes the SHAP differences for gradient boosting (no class axis, log-odds). Part F keeps a random forest on the two BRB features. Optional extras replaced where the sample no longer exists (X4 learning curve, X8 logistic regression). The dataset citation is recorded in section 5 and T1's citation item is ticked.
- `Dataset_Choice.md`: added an update note on using all rows and gradient boosting.

**Why**
The user said the group is one person and chose to use all rows, then chose the "all rows, lean" option to keep within the brief's 5-minute run limit. Timing trials on the full data showed a 300-tree random forest needs 487 s to train and 756 s for SHAP, while gradient boosting trains in 9–21 s and its SHAP takes under 2 s. Logistic regression takes 48–101 s per setting. On all rows, hiding Fuzzers drops its recall from 0.989 to 0.696 on validation, so Fuzzers stays the hidden type. The dataset page (https://www.unb.ca/cic/datasets/cic-unsw-nb15.html) was checked for the exact name and citation.

**Verified**
The full-data trial (load, clean, split, two models, SHAP, one pseudo-labelling round, six hidden-type models) ran in 107 s and gave the counts in the task list. The temporary environment and trial scripts in `/tmp` were deleted.

## 2026-10-09 09:06 EEST: T2 done: environment created, tests run, assembly script adapted

**What**
- `.venv/`: created with Python 3.13.7 and `requirements.txt` (not in git).
- `tools/assemble.py`: output is now `mini_project_unsw_nb15.ipynb`; `STEP_ORDER` is A0–A4, B1–B4, C1–C4, D1–D6, E1–E4, F1–F5, G1–G4, X1–X9; title cell, docstring, the unknown-step message and the `--strict` messages rewritten for this project.
- `TASKLIST.md`: T2 boxes ticked, result note added, T2 marked done in the overview.

**Why**
The user asked to do T2. The title cell names Stefanos Ntentopoulos, taken from the Lab 4.2 author list and the git user name; the task list says where to change it.

**Verified**
`python -m pytest src`: 16 passed. SHA-256 of `Data.csv` and `Label.csv` match the task list. A dummy part notebook (STEP A1, STANDIN A0, STEP G4) assembled correctly, `--strict` exited with an error listing the 30 missing steps, and the built notebook executed; the dummy and the output notebook were deleted.

## 2026-10-09 09:42 EEST: T3 done: setup notebook

**What**
- `parts/00_setup.ipynb`: created and executed. Steps A0 (install check, imports, seed, working folder, data folder, `score()` and `score_proba()`), A2 (load `Data.csv` and `Label.csv`, label names from `Readme.txt`, remove exact duplicates and conflicting rows, class balance) and A3 (stratified 60/20/20 split, constant columns dropped, `FEATURES`, `FLAG_COLS`, `CONT_COLS`, `TRAIN_MEDIAN`, `TRAIN_STD`, `TUNE_IDX`, split table, check that every shared name exists).
- `results/tables/A2_class_balance.csv`, `results/tables/A3_split.csv`: written by the notebook.
- `TASKLIST.md`: T3, A2 and A3 marked done; result note added; the final check cell is marked STEP A3 instead of A0 (an A0 cell would be sorted to the top of the hand-in notebook); measured setup time added to the time budget.

**Why**
The user asked to do T3. The first version took 68 s, over the 60 s budget. Three speed-ups brought it to 46 s, each checked to give identical results: one float block for the table, hash-based duplicate removal (same rows as `drop_duplicates()`), and splitting row positions before selecting rows.

**Verified**
All asserted counts match the task list (447,915 / 306,173 / 305,105 rows; 183,063 / 61,021 / 61,021 split; 67 features; 15,606 / 5,202 / 5,202 Fuzzers; 16,052 test attacks). `%run 00_setup.ipynb` from a test part notebook gave every shared name, and `tools/assemble.py` built and executed the hand-in notebook. The test notebook, the generated hand-in notebook and the build script in `/tmp` were deleted.

## 2026-10-09 11:22 EEST: Logistic regression back in Part B; T4 done: feature glossary

**What**
- `TASKLIST.md`: logistic regression is a required second glass box again. B1 now trains a tree and a logistic regression (scaled in a Pipeline, `C` from `[0.01, 0.1, 1, 10]` chosen on validation, trained on the 20% part); `logreg` added to the shared names, `MODELS` and the B2 stand-in; B3, C4, E1, E2 and E3 cover all three models. X8 is now "settings searches on all training rows". The decision table, the trial table and the time budget mention it. T4 marked done with a result note.
- `tools/feature_glossary.py`: rewritten for CIC-UNSW-NB15. Meanings for all 76 CICFlowMeter v4 names, the same cleaning and split as `parts/00_setup.ipynb`, case-insensitive direction check (`FWD Init Win Bytes`), flag counts described as packet counts, a note column for the three TCP-settings ("fingerprint") features, proposed Free/Costly/Fixed groups (`Fwd Packets/s` and the attacker's own TCP settings as Free).
- `results/tables/T4_feature_glossary.md`, `results/tables/T4_feature_glossary.csv`: written by the script.

**Why**
The user agreed to correctness first and runtime at the end, asked to add logistic regression back, and asked to do T4.

**Verified**
The script ran and asserted 305,105 clean rows and a 183,063 × 67 training set. Output: 67 features, proposed groups 27 Free / 5 Costly / 35 Fixed, 18 twin groups covering 42 features.

## 2026-10-09 11:42 EEST: A1 done: problem statement

**What**
- `parts/10_baseline_models.ipynb`: created, the notebook for Parts A and B. It holds a `# STANDIN A0` cell (runs `00_setup.ipynb`) and the Markdown cell `<!-- STEP A1 -->`: what is detected, who uses it, the cost of a false alarm and of a missed attack, and the data.
- `TASKLIST.md`: A1 ticked, result note added.

**Why**
The user asked to implement A1.

**Verified**
`tools/assemble.py --no-execute` places A1 between the setup's A0 and A2 cells; the test output was deleted.

## 2026-10-09 12:10 EEST: A4 done: trivial baseline

**What**
- `parts/10_baseline_models.ipynb`: added step A4 (Markdown explanation and code). An always-benign `DummyClassifier` is scored on validation and test, with asserts that accuracy equals the benign share, recall and FAR are 0, and PR-AUC equals the attack share. Executed.
- `results/tables/A4_baseline.csv`: accuracy 0.7369, macro-F1 0.4243, recall 0, PR-AUC 0.2631, FAR 0 (same on validation and test).
- `parts/00_setup.ipynb`: `score_proba()` now calls `f1_score(..., zero_division=0)`, so a model that never predicts "attack" gives no warning. Values are unchanged. Re-executed.
- `TASKLIST.md`: A4 ticked, result note added.

**Why**
The user asked to implement A4. The `zero_division` change avoids an UndefinedMetricWarning for the baseline, whose attack-class F1 is 0 either way.

**Verified**
Both notebooks executed without errors or warnings, and all A4 asserts passed.

## 2026-10-09 14:49 EEST: B1 done: glass boxes (decision tree and logistic regression)

**What**
- `parts/10_baseline_models.ipynb`: added step B1. Tree depth searched over `[3, 5, 8, 12, None]` and logistic regression `C` over `[0.01, 0.1, 1, 10]`, each candidate trained on the 20% part `TUNE_IDX` and scored on validation. The winners are trained on all training rows. The cells print the tree's first three levels and the 10 largest logistic regression weights, and record convergence. An interpretation cell explains the results. Executed.
- `results/tables/B1_tree_depth.csv`, `B1_logreg_C.csv`, `B1_logreg_weights.csv`: written.
- `parts/00_setup.ipynb`: `score_proba()` returns PR-AUC as a plain float (it printed as `np.float64`). Values unchanged. Re-executed.
- `TASKLIST.md`: B1 ticked, result note added.

**Why**
The user asked to implement B1.

**Verified**
Both notebooks ran without errors or warnings. Chosen: tree depth 12 (validation macro-F1 0.9685, recall 0.9844, FAR 0.0282) and logistic regression `C` = 10 (converged; macro-F1 0.9608, recall 0.9965, FAR 0.0414).

## 2026-10-09 17:40 EEST: B2 done: black box (gradient boosting)

**What**
- `parts/10_baseline_models.ipynb`: added step B2 (explanation, settings search, interpretation). `learning_rate` in `[0.05, 0.1]` × `max_leaf_nodes` in `[31, 63]`, each candidate trained on the 20% part and scored on validation. Chosen 0.1 / 31; `BOOST_SETTINGS`, `make_boost()`, `boost` (trained on all training rows) and `MODELS` (tree, logreg, boosting) defined. Executed.
- `results/tables/B2_boost_grid.csv`: written.
- `TASKLIST.md`: B2 ticked, result note added; the B2 stand-in in section 2.3 now holds the chosen settings (tree depth 12, `C` = 10, boosting 0.1 / 31).

**Why**
The user asked to implement B2.

**Verified**
The notebook ran without errors. Validation scores of the final model: macro-F1 0.9713, recall 0.9924, PR-AUC 0.9807, FAR 0.0282. It used all 100 trees allowed (`max_iter` cap); this is noted in the notebook.

## 2026-10-09 19:51 EEST: B3 done: test scores next to the baseline

**What**
- `parts/10_baseline_models.ipynb`: added step B3 (explanation, code, interpretation). The always-benign baseline, tree, logistic regression and gradient boosting are scored on validation and test, and the difference is shown. Executed.
- `results/tables/B3_val_scores.csv`, `results/tables/B3_test_scores.csv`: written.
- `TASKLIST.md`: B3 ticked, result note added.

**Why**
The user asked to implement B3. It is the first use of the test set; all settings were fixed beforehand in B1 and B2.

**Verified**
The notebook ran without errors. Test: gradient boosting macro-F1 0.9718, recall 0.9923, PR-AUC 0.9814, FAR 0.0276; tree 0.9690 / 0.9849 / 0.9677 / 0.0279; logistic regression 0.9608 / 0.9962 / 0.9527 / 0.0413. Test minus validation is at most 0.003 for every score.

## 2026-10-09 20:21 EEST: B4 done: where the models go wrong

**What**
- `parts/10_baseline_models.ipynb`: added step B4 (explanation, three code cells, interpretation): confusion matrices for the three models on the test set, recall per attack type (dot plot), and false alarms per day for a network with 1,000,000 flows a day and 2.53% attacks (the share in the full UNSW-NB15 recording). Defines the project's figure style (`MODEL_COLORS`, `MODEL_MARKERS`, `style_axes`, a blue ramp for heatmaps). Executed.
- `results/figures/B4_confusion.png`, `results/figures/B4_recall_per_type.png`; `results/tables/B4_confusion.csv`, `B4_recall_per_type.csv`, `B4_alarms_per_day.csv`: written.
- `TASKLIST.md`: B4 ticked, result note added.

**Why**
The user asked to implement B4. The model colours come from the dataviz reference palette's first three categorical slots, checked with its validator in all-pairs mode (passes; aqua is below 3:1 contrast, so tables and marker shapes are also provided). After the first render, the recall chart's legend covered two markers, so it was moved above the plot.

**Verified**
The notebook ran without errors or warnings, and both figures were inspected after the fix. Gradient boosting misses 124 attacks and raises 1,241 false alarms on the test set. About 65 of the misses are Fuzzers. At realistic traffic only 48% of its alerts would be real attacks.

## 2026-10-09 20:45 EEST: C1 done: 10% of the labels and the lower line

**What**
- `parts/20_few_labels.ipynb`: created, the notebook for Part C. It holds stand-ins for A0 (setup) and B2 (the three Part B models with the chosen settings), then step C1: an explanation, a stratified 10% / 90% split of the training set into labelled and unlabelled flows (with checks that no validation or test flow is involved), the lower line `boost_few`, its validation scores next to the upper line, and an interpretation. Executed.
- `results/tables/C1_lower_line_val.csv`: written.
- `TASKLIST.md`: C1 ticked, result note added.

**Why**
The user asked to implement C1.

**Verified**
The notebook ran without errors. 18,306 labelled (4,815 attacks) and 164,757 unlabelled flows. Lower line on validation: macro-F1 0.9679, recall 0.9862, PR-AUC 0.9743, FAR 0.0296 (upper line 0.9713 / 0.9924 / 0.9807 / 0.0282).

## 2026-10-09 21:02 EEST: C2 done: pseudo-labelling with the cutoff chosen on validation

**What**
- `parts/20_few_labels.ipynb`: added step C2 (explanation, code, interpretation). `pseudo_label(cutoff, rounds=2)` starts from the labelled 10%, adds confident guesses each round and trains a final model. Per round it records guesses added (attack / benign), still unlabelled, and guesses right (checked against `y_hidden` only after selection). Cutoffs 0.99, 0.95 and 0.90 were tried; 0.95 was chosen on validation macro-F1 (strictest on a tie) and kept as `boost_pseudo`. Executed.
- `results/tables/C2_cutoff.csv`, `results/tables/C2_rounds.csv`: written.
- `TASKLIST.md`: C2 ticked, result note added.

**Why**
The user asked to implement C2.

**Verified**
The notebook ran without errors or warnings. Cutoff 0.95: 150,327 guesses added, 99.1% right; validation macro-F1 0.9681 against 0.9679 for the lower line.

## 2026-10-09 21:22 EEST: C3 done: the unlabelled data did not help

**What**
- `parts/20_few_labels.ipynb`: added step C3. A validation table compares the lower line, pseudo-labelling (cutoff 0.95) and the upper line, with the difference and the share of the gap closed. A verdict cell answers "no", with numbers, the three reasons, and when pseudo-labelling could help (far fewer labels, optional X2). Executed; one number in the text was corrected after the run (about 4% of the gap closed, not 6%).
- `results/tables/C3_did_it_help_val.csv`: written.
- `TASKLIST.md`: C3 ticked, result note added.

**Why**
The user asked to implement C3. The brief requires a plain answer to whether the unlabelled data helped, including when the answer is no.

**Verified**
The notebook ran without errors. Every number in the verdict was checked against the table: macro-F1 0.9679 → 0.9681 (upper 0.9713, 3.9% of the gap closed), recall 0.9862 → 0.9899 (60% closed), FAR 0.0296 → 0.0308, PR-AUC 0.9743 → 0.9727.

## 2026-10-09 21:33 EEST: C4 done: the results table on the test set

**What**
- `parts/20_few_labels.ipynb`: added a `# STANDIN A4` cell (always-benign baseline) and step C4. The test-set table covers all six models of Parts A–C with macro-F1, recall, PR-AUC, FAR and accuracy; an assert checks that the Part B rows equal `B3_test_scores.csv`. The C3 comparison is repeated on test, followed by an interpretation. Executed.
- `results/tables/C4_all_models_test.csv`: written (the report's main results table).
- `TASKLIST.md`: C4 ticked, result note added. Part C is complete.

**Why**
The user asked to implement C4.

**Verified**
The notebook ran without errors; the Part B rows match B3. On test, pseudo-labelling is 0.0003 macro-F1 below the lower line (0.9685 against 0.9688), so the "did not help" verdict holds.

## 2026-10-09 21:55 EEST: D1 done: global SHAP on the black box

**What**
- `parts/30_explanation.ipynb`: created, the notebook for Part D. It holds a stand-in for A0 (setup) and B2 (gradient boosting with the chosen settings), then step D1: an explanation of SHAP and log-odds, `TreeExplainer` on 1,000 random validation flows with a check that base value plus contributions equals the model output, a top-10 table joined with the feature glossary, a bar plot, a beeswarm, and an interpretation. Executed.
- `results/tables/D1_shap_top.csv`, `results/figures/D1_shap_bar.png`, `results/figures/D1_shap_beeswarm.png`: written.
- `TASKLIST.md`: D1 ticked, result note added; the D1 stand-in now samples the same 1,000 validation flows as the real cell.

**Why**
The user asked to implement D1. SHAP runs on validation flows because Part F picks its features from this ranking. The first run printed the base value converted to a probability ("0.1% attack"), which was misleading for an average of log-odds, so the print was reworded.

**Verified**
The notebook ran without errors, and the additivity check passed. Top 3 features: Fwd Seg Size Min 42%, FWD Init Win Bytes 21%, Bwd Packets/s 13% of the SHAP weight. A separate check on the training split found that window 16,383 occurs in 95% of attacks and 0% of the flows with window 5,792; this supports the shortcut written in the notebook.

## 2026-10-09 22:15 EEST: D2 done: the three flows to explain

**What**
- `parts/30_explanation.ipynb`: added step D2 (explanation, case selection, fingerprint check, interpretation). From the black box's test probabilities: the true attack with the highest probability, the true benign flow with the lowest, and the most confident mistake, stored as `CASES` (test positions 50065, 47114, 10048). A check counts how test-set mistakes relate to the attacker fingerprint found in D1 (`Fwd Seg Size Min` = 20 and `FWD Init Win Bytes` = 16,383). Executed.
- `results/tables/D2_cases.csv`, `results/tables/D2_fingerprint_check.csv`: written.
- `TASKLIST.md`: D2 ticked, result note added.

**Why**
The user asked to implement D2. The fingerprint check was added because the chosen mistake turned out to be a benign flow with the attacker fingerprint; it measures how general that is.

**Verified**
The notebook ran without errors, and no ties occurred in the selection. The mistake is a false alarm at p = 0.9989. 1,197 of the 1,241 test false alarms carry the fingerprint. Attacks without it are caught 99.5% of the time.

## 2026-10-10 02:40 EEST: D3 done: SHAP and LIME for the three flows

**What**
- `parts/30_explanation.ipynb`: added step D3 (explanation, code, interpretation). For each of the three flows: a SHAP waterfall and a LIME explanation (`xai_tools.lime_explain`, 8 features, 5,000 samples, seed 42), plus a top-3 comparison table with LIME's fit score and local prediction. `predict_fn`, `lime_explainer` and `plot_lime` are defined here. Executed.
- `results/figures/D3_shap_detection.png`, `D3_shap_negative.png`, `D3_shap_mistake.png`, `D3_lime_detection.png`, `D3_lime_negative.png`, `D3_lime_mistake.png`; `results/tables/D3_top3.csv`: written.
- `TASKLIST.md`: D3 ticked, result note added.

**Why**
The user asked to implement D3. LIME's own plot overlapped its title with ours and used red/green, so the LIME bars are drawn with the project's red/blue (validated: all checks pass) and value labels.

**Verified**
The notebook ran without errors, and all six figures were inspected. SHAP and LIME share 2, 1 and 1 of their top-3 features. LIME's fit scores are 0.24–0.26.

## 2026-10-10 03:02 EEST: D4 done: the deletion test (fidelity)

**What**
- `parts/30_explanation.ipynb`: added step D4 (explanation, test, figure, interpretation). For 500 random test flows that the model calls attacks, each flow's top-k SHAP features (k = 1, 3, 5, 10) are replaced by their training medians with `xai_tools.deletion_test`, and the drop in attack probability and the share of flipped decisions are compared with k random features. Executed.
- `results/tables/D4_deletion.csv`, `results/figures/D4_deletion.png`: written.
- `TASKLIST.md`: D4 ticked, result note added.

**Why**
The user asked to implement D4. From this entry on, new prose follows the user's punctuation rule (no em or en dashes).

**Verified**
The notebook ran without errors and the figure was inspected. Replacing only the top SHAP feature (always `Fwd Seg Size Min`, median 32) flips all 500 decisions; 10 random features flip 25.4%.

## 2026-10-10 03:24 EEST: D5 done: stability of LIME

**What**
- `parts/30_explanation.ipynb`: added step D5 (explanation, code, interpretation). LIME is run with seeds 0 to 9 on each of the three flows (8 features, 5,000 samples). Per flow: the share of runs with the most common top 3, the number of different top-3 sets, the mean pairwise Jaccard overlap, the features in every run's top 3, and the fit score range. SHAP is run twice on each flow for comparison. Executed.
- `results/tables/D5_lime_stability.csv`, `results/tables/D5_lime_runs.csv`: written.
- `TASKLIST.md`: D5 ticked, result note added.

**Why**
The user asked to implement D5. The first execution was cut off by a 590-second limit on the command, so the notebook was run again without a limit.

**Verified**
The notebook ran without errors. Same top 3 in 8, 5 and 8 of 10 runs (detection, negative, mistake), and SHAP reruns are identical. LIME's most common top 3 is the same for all three flows, which the interpretation discusses.

## 2026-10-10 05:39 EEST: D6 done: why SHAP and LIME disagree

**What**
- `parts/30_explanation.ipynb`: added step D6 (explanation, three experiment cells, conclusion). Experiment 1: LIME with and without quartile ranges, and with copies drawn around the training average or around the flow. Experiment 2: 20,000 against 5,000 samples, seeds 0 to 4. Experiment 3: correlation between the features only SHAP or only LIME names. Experiment 4: LIME's fit score and local prediction against the model's probability in every variant. Executed.
- `results/tables/D6_investigation.csv`: written.
- `TASKLIST.md`: D6 ticked, result note added. Part D is complete.

**Why**
The user asked to implement D6 (needed for grade 5). The first run reused D3's LIME explainer, whose random generator had moved on, so the default variant did not match D3. It now uses a fresh explainer with seed 42 and reproduces D3 exactly.

**Verified**
The notebook ran without errors. The default variant matches D3 (2, 1, 1 features shared, fit 0.26, 0.24, 0.25). Every number in the conclusion was checked against the experiment output.

## 2026-10-10 06:29 EEST: E1 done: robustness to noise

**What**
- `parts/40_robustness.ipynb`: created, the notebook for Part E. It holds stand-ins for A0 and B2 (the three Part B models), then step E1: an explanation, `add_noise` (Gaussian noise of level times the training std on the continuous columns, flags untouched, clipped at 0) with checks, a table of what each level means for the main features, scores of all three models at levels 0, 0.05, 0.10, 0.20, 0.50 and 1.00 on the test set, a diagnostic with noise on only the TCP-settings features or only the other features, and an interpretation. Executed.
- `results/tables/E1_noise.csv`, `results/tables/E1_noise_where.csv`: written.
- `TASKLIST.md`: E1 ticked, result note added.

**Why**
The user asked to implement E1. The first run failed with "output array is read-only" (pandas 3 returns read-only arrays), fixed with `to_numpy(copy=True)`. The diagnostic was added to test, rather than guess, why the tree models collapsed.

**Verified**
The notebook ran without errors. At level 0.05, recall is 0.30 for boosting, 0.08 for the tree and 0.85 for logistic regression. Noise on only the three TCP-settings features gives 0.42, 0.08 and 0.996.

## 2026-10-10 10:36 EEST: E2 done: robustness to missing features

**What**
- `parts/40_robustness.ipynb`: added step E2 (explanation, code, split table, interpretation). `missing_mask` and `add_missing` replace round(level x 67) random features per test flow with the training median (seed 42, same choice for all models). All three models are scored at levels 0, 0.10, 0.20, 0.30 and 0.50, and the test attacks are split by whether `Fwd Seg Size Min` was among the missing features. Executed.
- `results/tables/E2_missing.csv`, `results/tables/E2_missing_split.csv`: written.
- `TASKLIST.md`: E2 ticked, result note added.

**Why**
The user asked to implement E2. The split was added because the median of `Fwd Seg Size Min` (32) is the benign machines' value (D4).

**Verified**
The notebook ran without errors, and the checks passed (level 0 changes nothing, exactly 7 features per row at level 0.10). With `Fwd Seg Size Min` missing, gradient boosting recall is 0.000 at every level.

## 2026-10-10 11:00 EEST: E3 done: what broke first and where to stop trusting the models

**What**
- `parts/40_robustness.ipynb`: added a `# STANDIN B4` cell (the project's figure style) and step E3 (rule, finer sweep, rule table, figure, conclusions). The trust rule from the task list (recall more than 0.05 below clean, or FAR more than twice clean) is applied to every model under noise and missing features. A finer sweep (noise 0.001 to 0.02; 1, 2, 3 and 5 missing features) is combined with the E1 and E2 results. Executed.
- `results/tables/E3_robustness_all_levels.csv`, `results/tables/E3_stop_trusting.csv`, `results/figures/E3_robustness.png`: written.
- `TASKLIST.md`: E3 ticked, result note added.

**Why**
The user asked to implement E3. The finer sweep was needed because every model already broke the rule at the first E1 and E2 levels. The figure legend first overlapped the title and was moved below it. The explanation first dated the rule 8 October; the changelog shows the task list was written on 9 October (still before Part E ran), so the date was corrected.

**Verified**
The notebook ran without errors and the figure was inspected. Gradient boosting and the tree fail at noise 0.001, logistic regression at 0.05. With missing features: boosting and the tree fail at 2, logistic regression at 3. The numbers in the conclusions match `E3_stop_trusting.csv`.

## 2026-10-10 11:19 EEST: E4 done: what an attacker would fake

**What**
- `parts/40_robustness.ipynb`: added a `# STANDIN D1` cell (the global SHAP ranking, same 1,000 validation flows as D1) and step E4 (explanation, groups, what-if, interpretation). Every feature gets an attacker group (Free, Costly, Fixed) with a reason: the glossary's proposal plus seven hand-judged overrides. The step reports the 15 most important features and the share of SHAP weight per group, then a what-if that gives every test attack the benign machines' most common TCP settings. Executed.
- `results/tables/E4_feature_groups.csv`, `results/tables/E4_whatif_benign_tcp.csv`: written.
- `TASKLIST.md`: E4 ticked, result note added. Part E is complete.

**Why**
The user asked to implement E4, to prepare "what would an attacker fake?" for the Discussion. The groups are assigned by rule plus overrides rather than by a hard-coded top-15 list, so the table follows the notebook's own SHAP ranking.

**Verified**
The notebook ran without errors, and the stand-in reproduces the D1 ranking exactly. Free features carry 69.1% of the SHAP weight. With benign TCP settings, recall is 0.000, 0.011 and 0.066 (boosting, tree, logistic regression).
