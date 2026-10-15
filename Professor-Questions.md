# Possible questions from the professor, with answers

The brief says: "Expect questions about any part of the work, not only your own part." So both of you
should be able to answer every question here. The name after each section heading is who answers first,
as the one who built that part; the other adds to it if needed.

How to answer: **one or two sentences, then the number that backs it.** If you do not know, say so and
say how you would find out; do not guess. All numbers come from the report and the result tables. For
background on any topic, see [Plain-English-Guide.md](Plain-English-Guide.md).

## 1. The big picture (both)

**In one sentence, what did you find?**
The models score 0.972 macro-F1, but mostly by recognising the TCP settings of the few lab machines that
launched the attacks, so they are excellent on this dataset and easy to fool in the real world.

**Who is the user of your detector, and what does a mistake cost them?**
A SOC analyst. A false alarm costs their time, and with millions of flows a day even 1% false alarms
buries the real alerts (alert fatigue). A missed attack costs more per case, because the attacker goes
unnoticed. So we want high recall and a low false alarm rate.

**What was the hardest part?**
Understanding why SHAP and LIME disagreed. We tested four possible reasons; the main one was that LIME
fits a straight line, and our model behaves like a switch.

**What would you do with another month?**
Build features over many flows (for example per host over a time window), which one attacker cannot
easily shape; test on a second dataset recorded elsewhere; and run the detector with the BRB as a second
opinion on a realistic 2.5% attack share.

## 2. Data and preparation (Kirill)

**Why this dataset?**
It has flow features of the CICFlowMeter kind (76 numeric features), nine attack types, and is small
enough to use every row within the 5-minute run limit.

**Why not the larger `CICFlowMeter_out.csv`?**
It has IP addresses, and all attacks come from one address range, so the address alone would give the
label away.

**Why did you remove duplicates?**
141,742 rows were exact copies. A copy in training and another in test lets the model remember instead of
generalise, so the test score would be too high. 1,068 more rows had identical features but different
labels; no model can get both right, so we dropped them too.

**Did you subsample?**
No. All 305,105 clean flows are used, and the notebook still runs in about 4 minutes.

**Why stratify the split on the attack type, not just on attack or benign?**
So that even the small types (Worms has only 47 test flows) appear in training, validation and test in
the same proportions.

**Is your split realistic? Could flows from the same attack session be in both training and test?**
Yes, they could; the split is random, not by time or by host. Removing duplicates removes exact copies,
not near copies. A split by time or by attacker machine would be a harder and more honest test, and the
shortcut we found suggests it would lower the scores. This is a limitation.

**Why drop nine features?**
They are constant in the training set, so they carry no information. 67 remain.

**Is 26% attacks a class imbalance problem?**
Mild. The bigger problem is that real traffic has about 2.5% attacks, so our test set flatters every
model. That is why we judge with macro-F1 and PR-AUC rather than accuracy, and why we estimated the
realistic case separately.

## 3. Metrics (Kirill)

**Why not accuracy?**
Calling everything benign already gives 0.737 accuracy while catching zero attacks.

**Why these four scores?**
Recall says how many attacks we catch, FAR how many benign flows we wrongly flag, macro-F1 balances both
classes, and PR-AUC judges the ranking without a fixed threshold.

**Why macro-F1 and not the ordinary F1 of the attack class?**
Macro-F1 averages the F1 of both classes with equal weight, so a model cannot score well by being good at
only one of them.

**What does your 0.028 FAR mean in practice?**
At a realistic 2.5% attack share and 1,000,000 flows a day, boosting would catch about 25,100 attacks
but raise about 26,900 false alarms: only 48% of the alerts would be real, against 93% on our test set.

## 4. The models (Kirill)

**Why these three models?**
The brief asks for glass boxes and a black box. A decision tree and logistic regression can be read by a
human; gradient boosting cannot.

**Why gradient boosting and not a random forest?**
Speed. In a trial run, a 300-tree forest took about 8 minutes to train and SHAP on 300 flows over 12
minutes, against seconds for boosting, and later parts retrain and explain the black box many times.

**Why not a neural network?**
On tabular flow features, tree ensembles are usually as good or better, train in seconds, and SHAP
explains them exactly. A neural network would also have made the 5-minute run limit hard to meet.

**How did you choose the settings?**
Each candidate was trained on a 20% part of the training set and scored on validation; the best macro-F1
won and was retrained on all training rows. Tree depth 12, logistic regression C = 10, boosting learning
rate 0.1 with 31 leaves. All four boosting settings were within 0.001 of each other.

**Did you ever look at the test set while choosing?**
No, and the code enforces it. The notebook has two phases: every setting is chosen on validation while
the test set is sealed (a cell that used it would stop with an error), then the step "Final evaluation on
the test set" opens it, and after that the notebook only reports. Validation and test agree within 0.003
on every score.

**Is boosting really better than the tree?**
By 0.003 macro-F1. A paired bootstrap over the test flows (200 resamples) gives 95% intervals of about
plus or minus 0.002, so the lead is small but real. The fact that a depth-12 tree comes this close is
itself a warning: a few strong signals are doing the work.

**Which attacks does boosting miss?**
124 attacks in total; about half are Fuzzers, its weakest large type (recall 0.988). Every type has
recall of at least 0.957 for every model.

## 5. Fewer labels (Stefanos)

**What is the lower line and the upper line?**
Lower: boosting trained only on the 10% of flows that keep their labels (18,306). Upper: boosting with all
labels. Lower scores 0.969, upper 0.972.

**How does pseudo-labelling work?**
The lower-line model labels the unlabelled flows it is very sure about, those guesses join the training
data, and the model is retrained, for two rounds. The confidence cutoff, 0.95, was chosen on validation.

**Why did it not help?**
There was little to win back (0.003). In round 1 the guesses were 99.5% right but were flows the model
already classified correctly, so they taught it nothing. Round 2 added borderline flows, and only 90% of
those were right. On test it ended slightly below the lower line (0.9685 against 0.9688).

**Did you use the hidden labels anywhere?**
Only afterwards, to count how many pseudo-labels were right. Never for training or choosing.

**When would it help?**
When labels are really scarce: with 1% of the labels (1,830 flows) it gave +0.003 macro-F1 and +0.012
recall.

## 6. Explanation (Stefanos)

**How does SHAP work?**
It splits one prediction among the features as a fair share, using Shapley values from game theory: each
feature's average contribution over all orders in which features could be added. For trees,
TreeExplainer computes this exactly, so repeated runs give identical values.

**What does SHAP show?**
Three features carry 76% of the weight. The top two, `Fwd Seg Size Min` (42%) and `FWD Init Win Bytes`
(21%), are TCP settings of the machine that opens the connection. 95% of training attacks announce a
window of exactly 16,383 bytes. The model recognises the attacker machines: a shortcut.

**Is the shortcut a bug in your code?**
No, it is in the data. UNSW-NB15 attacks were generated from a few attacker machines. Arp et al. (2022),
"Dos and don'ts of machine learning in computer security", describe exactly this kind of spurious
correlation.

**How do you know SHAP is right and not just plausible?**
The deletion test: on 500 flows called attacks, replacing each flow's top SHAP feature with the training
median flipped 100% of them to benign, against 2.8% for one random feature and 25.4% for ten random
features.

**Isn't the deletion test unfair, since the median is the benign value?**
Partly, and that is the point: giving an attack a normal machine's TCP setting is enough to make the model
call it benign. A limitation is that the edited flows can be unrealistic.

**Explain your most confident mistake.**
A benign flow called an attack with probability 0.999. It carries the attacker fingerprint (value 20 and
window 16,383), which alone adds +5.7 and +3.5 log-odds. 1,197 of the 1,241 false alarms on the test set
are benign flows with the fingerprint.

**How does LIME work, and why does it disagree with SHAP?**
It perturbs the flow, asks the model, and fits a weighted straight line around it. It shared only 1 or 2
of SHAP's top 3. Main reason: poor local fit (R² 0.06 to 0.29), because the model acts like a switch on one
TCP value. Its quartile ranges also lumped together values the model treats oppositely. Without ranges
and with samples around the flow, its top 3 for the detection became exactly SHAP's.

**Is LIME stable?**
No. Over 10 seeds the most common top 3 appeared in only 5 to 8 runs, and the same top 3 came out for all
three flows: it was describing the model in general, not the flow.

**Which would you show an analyst?**
SHAP: exact, stable and shown to be faithful here.

## 7. Robustness (Stefanos)

**How did you add noise?**
Gaussian noise scaled to each feature's training standard deviation, clipped at 0, on the 65 continuous
features of the test set, at 10 levels from 0.001 to 1.

**Why does tiny noise break the trees?**
They test for a narrow interval around the exact fingerprint (the tree isolates a window between 16,368.5
and 16,406.5). Noise of one thousandth of a standard deviation moves values out of it: boosting's recall
falls from 0.992 to 0.513. Logistic regression has no such thresholds and holds up to noise 0.02.

**How did you simulate missing features?**
A share of each flow's features is replaced by the training median, from 1 to 34 per flow. One missing
field is tolerated; two or three are not.

**What was your rule for "stop trusting"?**
Fixed before the tests: recall more than 0.05 below the clean value, or FAR more than twice the clean
value.

**What breaks first, recall or false alarms?**
Recall, every time. The models fail silently, with fewer alerts, which looks like good news on a
dashboard.

**What would an attacker fake?**
Their own TCP settings: 69% of the SHAP weight is on features they control for free. Giving all 16,052
test attacks the common benign settings drops boosting's recall to 0.000. A greedy search allowed only
attacker-controlled changes needed one change to fool boosting on all 50 attacks tried.

**How did you decide what the attacker controls?**
Each feature was put in a group: free (timing, the attacker's own packet sizes and TCP settings), costly
(more packets or bytes, a louder attack) or fixed (the victim's replies).

**Isn't noise unrealistic? Real sensors do not add Gaussian noise.**
It is a simple stand-in for measurement differences, for example another flow tool or clock. Its value is
showing how close to a cliff the models sit, not predicting a real error rate.

## 8. The belief rule base (Kirill)

**What is a BRB?**
A set of if-then rules with beliefs. Each input is graded Low, Medium or High; with two inputs that is 9
rules. Each rule gives a belief over Low, Medium and High risk, plus an Unknown part.

**How does it reach a decision?**
Each input activates the nearby rules with weights; evidential reasoning combines their beliefs into one
belief; the risk score is Low 0, Medium 50, High 100, with Unknown counted halfway. Above 48.5 (chosen on
validation) is an alert.

**Where do the rule beliefs come from?**
From the training data: each rule's attack share becomes its belief, and rules with little data keep part
of it as Unknown.

**Why these two features, and not the top SHAP feature?**
The BRB needs three distinct levels (5th percentile, median, 95th percentile). For `Fwd Seg Size Min` two
of them coincide, so we took the next two: `FWD Init Win Bytes` and `Bwd Packets/s`.

**Why is it worse than a tree on the same features?**
Three levels cannot isolate the exact window 16,383, which a tree can. Cost: 0.953 against 0.962
macro-F1.

**Then why use it?**
Nine readable rules, a traceable reason for each decision, much better noise robustness (0.897 against
0.472 for the small tree at noise 0.05), and an honest "cannot decide": with `Bwd Packets/s` missing,
Unknown rose to 0.43 and the risk became a range (16.9 to 59.6) across the threshold. On the whole test
set, a missing window leaves the BRB undecided for 65% of flows, while boosting, given the median
instead, misses 79% of attacks with no sign of doubt.

**Is the comparison fair?**
Yes: the tree (depth 4, chosen on validation) and a 100-tree random forest got the same two features and
the same test set.

**Why only two features?**
The rules grow as 3 to the power of the number of features: 3 features need 27 rules, 5 need 243, which no
human can read or check.

## 9. Adaptability (Stefanos)

**Why Fuzzers?**
In a trial on the validation set, hiding it lowered its own recall the most. It is also large: 15,606
training flows, a third of the training attacks.

**What happened when it was hidden?**
Fuzzers recall fell from 0.988 to 0.688; recall on the other types barely moved. The false alarm rate
fell (0.028 to 0.019), so the dashboard looked better.

**Where did the new labels come from?**
From the removed Fuzzers training flows, never from the test set.

**Why weight 100? Did you tune it?**
Not tuned; tuning would need Fuzzers labels the analyst does not have. Weights 1, 10 and 100 are all
shown. 100 weighted labels give 0.845; unweighted only 0.706. With 500 weighted labels it reaches 0.956.

**How would you notice a new attack without labels?**
The share of unsure predictions (probability between 0.1 and 0.9) nearly doubled, 43% to 82% on Fuzzers,
and needs no labels. Also compare incoming feature distributions with training, label a small random
sample every week, and retrain regularly.

## 10. Reproducibility and the notebook (both)

**Does the notebook run top to bottom in 5 minutes?**
Yes, in about 4 minutes with the saved models in `models/`.

**Are the saved models cheating?**
No. They are keyed on the features, the split sizes, the seed and the scikit-learn version, so a
different setup retrains instead of loading old results. Deleting `models/` retrains everything in about
25 minutes with the same numbers, because the seed is fixed at 42.

**Why is the code split into part notebooks?**
So each of us could work on our own parts. `tools/assemble.py` builds the single hand-in notebook from
them, and in strict mode it refuses to build if any cell before the test set is opened uses it.

**How do you know the report matches the code?**
`tools/check_report_numbers.py` checks all 446 numbers in the report against the tables the notebook
writes.

## 11. Judgement (both)

**Would you deploy this?**
Not as it is. We would use the model trained without the three TCP-settings features (0.971 instead of
0.972, and far more robust to noise), with the BRB as a readable second opinion that sends undecided
flows to an analyst, plus the monitoring of Part G. Even that model was fooled in 34 of 50 attacks by
cheap timing and padding changes, so it should not be trusted alone.

**Which numbers do you trust least?**
The 0.972 itself (it measures recognising the lab machines), the 0.028 FAR (made at 26% attacks), recall
on the small types (Worms 47 test flows, Analysis 77, Backdoor 90), and every LIME explanation.

**Where would it fail outside this dataset?**
Where attackers and normal users run the same operating systems, behind NAT or proxies that rewrite TCP
settings, with another flow tool, and on modern encrypted traffic. The data are from a 2015 lab with
synthetic normal traffic.

**If removing the shortcut features costs almost nothing, why not do it from the start?**
We only knew about the shortcut because of the explanation work in Part D. That is the lesson: the scores
hid the weakness, and explanation found it.

**What is the one thing an attacker cannot easily fake?**
The victim's replies, for example how fast it answers. That is why an unrestricted attack search, which
changes those too, overstates what a real attacker can do.

## 12. Process and AI use (both)

**Did you use AI?**
Yes, declared in the report: Claude (Anthropic), through Claude Code, to compare datasets, plan, explain
concepts, write and review code, run experiments, check numbers and draft text. The project decisions and
the responsibility are ours.

**How do we know you understand the code the AI wrote?**
By opening any cell and explaining it line by line. The five cells below are the most likely to be asked
about, because each one carries a key claim of the report. Practise them out loud, with the notebook open.
Each section below says where to find the cell, what each line does, and the follow-up questions to
expect.

**How to find a cell quickly:** every cell starts with its step label, so press `Ctrl+F` in Jupyter and
search for it (for example `# STEP C2`). The cell numbers below count every cell of
`mini_project_unsw_nb15.ipynb` from the top, title included (155 in total). Jupyter does not show these
numbers, but they tell you roughly how far down to scroll.

### Practice cell 1: the data cleaning (Kirill)

**Where:** heading "Part A: load and clean the data", step `# STEP A2`, cell 10 (the cell that starts
`raw_counts = ...`).

| Code | What it does |
|---|---|
| `raw_counts = df["attack_type"].value_counts()` | Counts the flows of each type before cleaning, for the class-balance table in the next cell |
| `pd.util.hash_pandas_object(df, index=False)` | Turns each whole row (the 76 features and the label) into one number, a "hash". Identical rows get identical hashes |
| `.duplicated()` and `df[~...]` | Marks every row whose hash was already seen, and keeps only the first copy. 447,915 rows become 306,173 |
| `row_key = pd.util.hash_pandas_object(df[feature_columns], ...)` | The same trick, but on the 76 features only, without the label |
| `df.groupby(row_key)["attack_type"].transform("nunique") > 1` | For each group of rows with identical features, counts how many different labels it has. More than one label is a contradiction |
| `df = df[~conflict]` | Drops **all** rows of a contradictory group, both labels. 306,173 become 305,105 |
| `assert CLEAN_COUNTS == {...}` | Stops the notebook if the counts are ever different, so the numbers in the report cannot silently change |

**Follow-up questions:**
- *Why a hash and not `drop_duplicates()`?* Same result (the comment says this was checked), but 4
  seconds instead of 21.
- *Could two different rows get the same hash?* In theory, yes, but with 64-bit hashes the chance is
  negligible for 448,000 rows, and the result was checked against `drop_duplicates()`.
- *Why drop both rows of a contradiction and not keep the majority label?* No model can get both right,
  and we cannot know which label is the true one. It is only 1,068 rows.

### Practice cell 2: the sealed test set (Kirill, and both should know it)

**Where:** two places.
- **The seal:** heading "Part A: split 60 / 20 / 20", step `# STEP A3`, cell 17, at the very end of the
  cell (it starts with the comment "Everything the later parts rely on").
- **The opening:** heading "Final evaluation on the test set", step `# STEP T0`, cell 56.

| Code | What it does |
|---|---|
| `N_TEST, TEST_INDEX = len(X_test), X_test.index` (earlier, in the split cell) | Keeps only the test set's size and row numbers. The model cache needs the size, and Part C needs the row numbers to check that its labelled flows are not test flows |
| `_SEALED_TEST = (X_test, y_test, type_test)` | Puts the test features, labels and attack types into one box with an unusual name |
| `del X_test, y_test, type_test` | Deletes the usual names. Any later cell that writes `X_test` stops with a `NameError` |
| In T0: `X_test, y_test, type_test = _SEALED_TEST` | Takes them out of the box again |
| `del _SEALED_TEST` | Removes the box |
| `assert len(X_test) == N_TEST and X_test.index.equals(TEST_INDEX) ...` | Checks that what came out is exactly what went in: same size, same rows, same columns |

**Follow-up questions:**
- *Couldn't a cell just use `_SEALED_TEST` and peek?* Yes; Python cannot truly lock a variable. That is
  why `tools/assemble.py --strict` also reads every code cell between the seal and T0, and refuses to
  build the notebook if any of them mentions `X_test`, `y_test`, `type_test` or `_SEALED_TEST`. The two
  checks together make an accidental peek impossible.
- *Why not simply put the test cells at the end?* The whole point is to prove the order: everything chosen
  first, then opened. The seal turns the order into something the code checks, not something we promise.

### Practice cell 3: the pseudo-labelling loop (Stefanos)

**Where:** heading "Part C: pseudo-labelling (semi-supervised learning)", step `# STEP C2`, cell 34 (it
starts `def pseudo_label(cutoff, rounds=2):`).

| Code | What it does |
|---|---|
| `X_now, y_now = X_lab, y_lab` | Starts from the 18,306 labelled flows (10% of training) |
| `pool = X_unlab` | The 164,757 unlabelled flows still to be guessed |
| `model = make_boost().fit(X_now, y_now)` | Trains a fresh boosting model, with the settings chosen in Part B, on what we have so far |
| `p = model.predict_proba(pool)[:, 1]` | The attack probability of every unlabelled flow |
| `sure = (p >= cutoff) \| (p <= 1 - cutoff)` | "Very sure": at least 95% attack, or at least 95% benign (cutoff 0.95) |
| `guess = ... (p[sure] >= 0.5)` | The guessed label of each sure flow: attack if more than half |
| `right = guess == y_hidden.loc[guess.index]` | **Only for counting** how many guesses are right; `y_hidden` is never used for training |
| `X_now = pd.concat([X_now, pool[sure]])`, `y_now = pd.concat([y_now, guess])` | The sure flows join the training data, with their guessed labels |
| `pool = pool[~sure]` | They leave the pool, so round 2 only looks at the flows that were not sure in round 1 |
| `model = make_boost().fit(X_now, y_now)` (after the loop) | The final model, trained on the real labels plus the guesses |
| `for cutoff in [0.99, 0.95, 0.90]:` and `CUTOFF = ...idxmax()` | Tries three cutoffs, scores each on **validation**, keeps the best macro-F1 (on a tie, the strictest): 0.95 |

**Follow-up questions:**
- *Why two rounds?* Round 1 adds the easiest flows, round 2 the next easiest. Round 2 already got worse
  (90% right instead of 99.5%), so more rounds would add more wrong labels.
- *Why do the confident guesses not help?* They are flows the model already gets right, so they teach it
  nothing new.
- *What does `cached(...)` do here?* It loads the trained models from `models/` if they exist, otherwise
  trains and saves them. The result is the same either way.

### Practice cell 4: the deletion test (Stefanos)

**Where:** heading "Part D: fidelity, the deletion test", step `# STEP D4`, cell 79. The calculation
itself is the function `deletion_test()` in `src/xai_tools.py`.

In the notebook cell:

| Code | What it does |
|---|---|
| `attack_called = np.flatnonzero(pred_test == 1)` | All test flows the model calls an attack |
| `rng.choice(attack_called, size=500, replace=False)` | 500 of them at random, with seed 42 |
| `shap_del = explainer(X_del).values` | The SHAP values of each of the 500 flows: how much each feature pushed that flow's decision |
| `xai_tools.deletion_test(..., TRAIN_MEDIAN[...], ks=(1, 3, 5, 10))` | Runs the test, replacing features with their training median (a "typical" value) |
| `first = ...np.abs(shap_del).argmax(axis=1)` | Which feature SHAP names first for each flow, and its median. Answer: `Fwd Seg Size Min` for all 500, median 32 |

Inside `deletion_test()`:

| Code | What it does |
|---|---|
| `original = predict_fn(X_rows)`, `predicted = original.argmax(1)` | The model's decision for each flow before any change |
| `p_before = original[np.arange(n), predicted]` | How sure it was of that decision |
| `np.argsort(-np.abs(a), axis=1)` | For each flow, its features sorted from most to least important by SHAP |
| `orders["random"] = ... rng.permutation(d)` | The fair comparison: the same test with features in random order |
| `masked[rows, cols] = fill_values[cols]` | Replaces each flow's top k features with their training median |
| `drop = p_before - p_after` | How much the model's confidence fell |
| `share_flipped` | The share of flows whose decision changed. SHAP, k = 1: 100%. One random feature: 2.8% |

**Follow-up questions:**
- *Why compare with random features?* Without a baseline, "the probability dropped" means nothing; any
  change might lower it a little. SHAP's features matter far more than random ones, so SHAP is faithful.
- *Is the median fair?* Not entirely: the median 32 is the benign machines' value, which is also why it
  flips everything. That is the shortcut shown as cause and effect. Edited flows can also be unrealistic,
  which the report names as a limitation.

### Practice cell 5: the BRB, from building to a decision (Kirill)

**Where:** three cells, plus the engine in `src/brbes.py`.
- **Building:** heading "Part F: building the BRB", step `# STEP F2`, cell 50.
- **The threshold:** the next code cell, cell 51.
- **One decision, step by step:** heading "Part F: the belief output for one flow, step by step", step
  `# STEP F4`, cell 111. Its printed trace is the easiest way to explain it.

Building (cell 50 and `build_rule_base()`):

| Code | What it does |
|---|---|
| `brbes.make_levels(X_train[f])` | Low, Medium and High for each feature: the training 5th percentile, median and 95th percentile |
| `brbes.build_rule_base(X_train[TOP2], y_train, levels)` | Makes the 3 × 3 = 9 rules and fills in their beliefs from the training data |
| `support`, `attacks` (inside) | For each rule: how many training flows match it, and how many of those are attacks (a flow between two levels counts partly for both) |
| `share = (attacks + 1.0) / (support + 2.0)` | The rule's attack share, with +1 and +2 so that a rule with no data says 50%, not 0/0 |
| `share_to_belief(share)` | Turns the share into beliefs over Low, Medium and High risk, for example 80% attack becomes Medium 0.4, High 0.6 |
| `* (support / (support + n0))` with `n0 = 20` | Shrinks the beliefs of rules with little data; the rest becomes **Unknown**. A rule with 20 flows keeps half of its belief as Unknown, one with 20,000 almost none |

Deciding (`infer()` and `utility()`, used in cells 51 and 111):

| Step | What it does |
|---|---|
| `input_transform()` | Matches each input to the levels. A value between Low and Medium belongs partly to both; a missing value matches nothing |
| `activation_weights()` | How strongly each rule fires: the product of its inputs' matches, scaled so all weights add up to 1. A missing input is left out of the product |
| `belief_update()` | If one of the two inputs is missing, every rule's beliefs are halved; the other half becomes Unknown |
| `er_aggregate()` | Evidential reasoning: combines the beliefs of all firing rules into one belief over Low, Medium, High and Unknown |
| `utility()` | The risk score: Low 0, Medium 50, High 100. Unknown is counted as 0 (`u_min`), as 100 (`u_max`) and halfway (`u_avg`) |
| `brbes.choose_threshold(u_val, y_val)` (cell 51) | The alert line with the best macro-F1 on **validation**: 48.5 |
| `undecided = (u_min < BRB_THRESHOLD) & (u_max >= BRB_THRESHOLD)` (cell 114) | "Cannot decide": the range from best to worst case crosses the alert line |

**Follow-up questions:**
- *Why +1 and +2?* So that a rule nobody has seen says "50%, no idea" instead of dividing by zero. It is
  Laplace smoothing.
- *Why n0 = 20?* A hand-made choice, not tuned: below about 20 flows a rule should visibly admit doubt.
  It hardly matters here, because most rules have thousands of flows.
- *What happens if both inputs are missing?* No rule fires, and the answer is 100% Unknown: the risk could
  be anything from 0 to 100.
- *Where did the engine come from?* From our Lab 3, with its own tests in `src/test_brbes.py` (for
  example, that a missing input gives exactly the expected Unknown).

**Who did what?**
Kirill: Parts A, B and F. Stefanos: Parts C, D, E and G. Each made the additional checks for their own
parts; the dataset choice, the notebook, the README and the report were done together.
