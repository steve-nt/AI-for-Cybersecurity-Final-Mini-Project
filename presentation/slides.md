# Slides: An Explainable and Robust Cyber-Defence Model

Presentation on Thursday 15 October 2026, from 14:45. **13 minutes, then questions.** Two presenters, and
each explains the parts they built, as the brief requires: **Kirill** Parts A, B and F, **Stefanos** Parts C,
D, E and G. Kirill opens and closes. The plan below takes **12:20**, which leaves 40 seconds of buffer:
Kirill speaks about 5:45, Stefanos about 6:35.

**Who drives the laptop:** whoever is *not* speaking changes the slides and switches to the notebook, so
the speaker can face the audience. There are four handovers (after slides 4, 10, 12 and 14); each ends
with one sentence that names the next speaker, already in the notes.

The live run of the notebook is part of the talk: it starts on slide 1 and is shown on slides 4 and 14.
See [demo.md](demo.md) for the steps and [rehearsal.md](rehearsal.md) for the timing and the questions.

## How to build the deck from the template

The deck is `presentation/Mini_Project_Presentation.pptx`, built by `presentation/build_slides.py` from
this file and the seminar deck `AutoPenBench_Seminar.pptx` (its masters and theme are reused, its slides
removed). Titles, source lines, cards, big numbers, tables, takeaway lines and speaker notes are read
from here, so **edit this file and rebuild** rather than editing the PPTX by hand:

```bash
.venv/bin/python presentation/build_slides.py --preview   # needs python-pptx; previews go to /tmp/slide_preview
```

The script keeps the template's look, which is:

| Element | In the template | Keep for this deck |
|---|---|---|
| Size | 16:9 (33.9 x 19.1 cm) | same |
| Font | Century Schoolbook; titles about 33 pt, card headings about 22 pt, body about 21 pt, source line about 12 pt | same |
| Colours | text navy `#17283C`, secondary grey `#526173`, accent blue `#245CC5`, second accent teal `#087F79`, card fill cream `#F5F3ED`, panel light blue `#DFE9F3` | same |
| Top of every slide | title, slide number, and a grey **source line** ("Paper §2.2 and Appendix A") | the source line names the notebook part and the result file, e.g. "Notebook Part B · results/tables/B3_test_scores.csv" |
| Body | either **three cards** (bold heading + one line each) or **one big number** with a label, or a diagram | same three layouts, plus a figure from `results/figures/` |
| Bottom | one **takeaway line** | same: the one sentence the audience should remember |
| Speaker notes | "Target time: N seconds. Presenter: name." then the slide title, then the script | same format; the script below goes into the notes |

Rules: one number per slide that matters, at most two slides per part, and every number on a slide is
one that is in the report (they were all checked against the result tables). Figures come from
`results/figures/` (the report uses the same files).

## Time plan

| # | Slide | Part | Presenter | Time | Clock at end |
|---|---|---|---|---|---|
| 1 | Title (press Run All) | | Kirill | 0:35 | 0:35 |
| 2 | Problem, data and baseline | A | Kirill | 1:10 | 1:45 |
| 3 | Three models, one test | B | Kirill | 0:55 | 2:40 |
| 4 | Live: the test scores, computed now | demo | Kirill | 0:30 | 3:10 |
| 5 | 10% of the labels | C | Stefanos | 1:00 | 4:10 |
| 6 | What the model looks at | D | Stefanos | 0:55 | 5:05 |
| 7 | The most confident mistake | D | Stefanos | 0:40 | 5:45 |
| 8 | Can we trust the explanation? | D | Stefanos | 0:50 | 6:35 |
| 9 | Noise and missing fields | E | Stefanos | 0:45 | 7:20 |
| 10 | What an attacker would fake | E | Stefanos | 0:45 | 8:05 |
| 11 | A belief rule base on two features | F | Kirill | 0:55 | 9:00 |
| 12 | What Unknown buys | F | Kirill | 0:45 | 9:45 |
| 13 | A new attack: Fuzzers | G | Stefanos | 1:00 | 10:45 |
| 14 | Live: one attack, two settings changed | demo | Stefanos | 0:40 | 11:25 |
| 15 | Would we deploy this? | conclusion | Kirill | 0:55 | 12:20 |
| 16 | Questions | | both | | |
| B1 to B4 | Backup slides, only for questions | | whoever is asked | | |

Per part: A 1:10, B 0:55, C 1:00, D 2:25, E 1:30, F 1:40, G 1:00, conclusion 0:55, live demo 1:45
(including slide 1).

---

## Slide 1: Title

**Layout:** title slide, as template slide 1.

- Title: **An Explainable and Robust Cyber-Defence Model**
- Subtitle: Network intrusion detection on CIC-UNSW-NB15
- Question line: *Can we trust a detector that scores 0.97?*
- Footer: Kirill Silchenko and Stefanos Ntentopoulos · AI for Cybersecurity (D7084E / D7041E) · 15 October 2026

**Speaker notes.** Target time: 35 seconds. Presenter: Kirill.

> Before we start, we press Run All in the notebook. It runs everything from the raw CSV files, from top to
> bottom, and takes about two minutes; we will look at it twice during the talk. The trained models load
> from a saved cache, because training them all from scratch takes about 25 minutes.
>
> We are Kirill and Stefanos. Our project is a network intrusion detector on CIC-UNSW-NB15. It scores
> 0.97. The talk is about whether we should trust that number.

---

## Slide 2: Problem, data and baseline (Part A)

**Source line:** Notebook Part A · results/tables/A2_class_balance.csv, A4_baseline.csv

**Layout:** three cards, and the baseline as a big number on the right.

- **Who uses it.** SOC analysts, who get an alert for every flow called an attack.
- **What errors cost.** A false alarm costs analyst time and causes alert fatigue; a missed attack costs more, per case.
- **The data.** 305,105 clean flows (141,742 duplicates removed), 26.3% attacks, nine attack types, split 60/20/20 stratified.
- Big number: **0.737** accuracy for "always benign", with recall 0.

**Takeaway line:** Accuracy is useless here; we report macro-F1, recall, PR-AUC and the false alarm rate (FAR).

**Speaker notes.** Target time: 70 seconds. Presenter: Kirill.

> The problem: for every network flow, one conversation between two computers summarised as numbers
> about packets, sizes and timing, decide whether it is normal or part of an attack. The users are SOC
> analysts. A false alarm costs them time, and with millions of flows a day even 1% false alarms buries
> the real ones. A missed attack costs more per case, because the attacker goes unnoticed. So we want
> high recall at a low false alarm rate.
>
> The data is CIC-UNSW-NB15, flows with 76 features. I removed 141,742 exact duplicates, because a copy
> in training and another in test makes the test too easy, and kept all 305,105 remaining flows; no
> subsample. 26.3% are attacks, of nine types. The split is 60/20/20, stratified on the attack type.
>
> The trivial baseline calls everything benign. It gets 74% accuracy and catches nothing, which is why
> accuracy is not one of my scores.

---

## Slide 3: Three models, one test (Part B)

**Source line:** Notebook Part B · results/tables/B3_test_scores.csv

**Layout:** a small table, and one big number.

| Test set (61,021 flows) | Macro-F1 | Recall | FAR |
|---|---|---|---|
| Always benign | 0.424 | 0.000 | 0.000 |
| Decision tree (depth 12) | 0.969 | 0.985 | 0.028 |
| Logistic regression | 0.961 | 0.996 | 0.041 |
| **Gradient boosting** | **0.972** | 0.992 | **0.028** |

- Big number: **+0.003**, what the black box buys over a readable tree.

**Takeaway line:** Settings chosen on validation; test used once, and it agrees within 0.003.

**Speaker notes.** Target time: 55 seconds. Presenter: Kirill.

> Two glass boxes, a decision tree and logistic regression, and one black box, gradient boosting. Every
> setting, the tree depth, the regularisation and the boosting grid, was chosen on the validation set,
> and the test set was used once at the end. Validation and test agree within 0.003 on every score.
>
> All three are far above the baseline. Boosting is best, but only by 0.003 macro-F1 over a depth-12
> tree. Logistic regression catches the most attacks but raises the most false alarms. I read that small
> gap as a warning, not a success: if a tree solves the problem this well, the model probably relies on a
> few strong signals. Parts D and E show which ones.

---

## Slide 4: Live: the test scores, computed now

**Layout:** a short cue slide ("Live: the notebook"), then switch to the notebook window.

**What to show:** the section "Part B: scores on the test set, next to the trivial baseline". Point at
the test table and at the cell counter on the left. Then switch back. Details in [demo.md](demo.md).

**Speaker notes.** Target time: 30 seconds. Presenter: Kirill.

> This is the notebook we started almost three minutes ago. It is already past Part B: here is the test
> table, computed just now, with the same 0.972 as on the slide. It is now working through the
> explanation part. We come back at the end. Stefanos now takes Parts C, D and E.

---

## Slide 5: 10% of the labels (Part C)

**Source line:** Notebook Part C · results/tables/C2_rounds.csv, C4_all_models_test.csv

**Layout:** big number on the left, three cards on the right.

- Big number: **-0.003** macro-F1, the cost of hiding 90% of the labels (lower line 0.969 against 0.972).
- **Pseudo-labelling.** The model labels the flows it is at least 95% sure of, two rounds (cutoff chosen on validation).
- **Result.** Test macro-F1 0.9685 with pseudo-labels, against 0.9688 without: no gain.
- **Why.** Round 1 added 143,824 guesses, 99.5% right, but all flows the model already got right.

**Takeaway line:** The unlabelled data did not help: the confident guesses were right, but not new.

**Speaker notes.** Target time: 60 seconds. Presenter: Stefanos.

> Part C: what if only 10% of the training flows have labels? The lower line, boosting on those 18,306
> flows, loses only 0.003 macro-F1. So there was very little to win back.
>
> I tried pseudo-labelling: the model labels the unlabelled flows it is very sure about, they join the
> training data, and it retrains, for two rounds. The cutoff, 0.95, was chosen on validation. The answer
> is no: on test it is slightly below the lower line. The reason is in the guesses: the first round added
> 143,824 flows and 99.5% were right, but they were flows the model already classified correctly, so they
> taught it nothing. An extra check with only 1% of the labels did find a small real gain. Unlabelled data
> help only when labels are really scarce.

---

## Slide 6: What the model looks at (Part D)

**Source line:** Notebook Part D · results/figures/D1_shap_beeswarm.png, results/tables/D1_shap_top.csv

**Layout:** the beeswarm figure on the left (large), one big number and two lines on the right.

- Big number: **76%** of the SHAP weight on three features.
- `Fwd Seg Size Min` 42%, `FWD Init Win Bytes` 21%, `Bwd Packets/s` 13%.
- The first two are **TCP settings of the attacker's own machine**: 95% of training attacks announce a window of exactly 16,383 bytes.

**Takeaway line:** The model recognises the attacker machines' TCP fingerprint: a shortcut, not attack behaviour.

**Speaker notes.** Target time: 55 seconds. Presenter: Stefanos.

> Part D. SHAP on 1,000 validation flows. Three features carry 76% of the weight. The top two are not
> properties of an attack. They are TCP settings of the machine that opens the connection: the segment
> size and the initial window. In training, 95% of all attacks announce a window of exactly 16,383 bytes,
> and 89% of flows with a segment size of 20 are attacks.
>
> The UNSW-NB15 attacks were generated from a few attacker machines, so the model has learned to
> recognise those machines. That is a shortcut. You can see it in the plot: the top two features split
> into separate clouds, one value pushes hard to attack, the other to benign.

---

## Slide 7: The most confident mistake (Part D)

**Source line:** Notebook Part D · results/figures/D3_shap_mistake.png, results/tables/D3_shap_values.csv

**Layout:** the waterfall figure (large), with the big number above it.

- Big number: **0.999**, the attack probability of a benign flow.
- The two TCP features alone add **+5.7** and **+3.5** log-odds.
- **1,197 of the 1,241** false alarms on the test set carry the same fingerprint.

**Takeaway line:** The explanation found the weakness that the scores hid.

**Speaker notes.** Target time: 40 seconds. Presenter: Stefanos.

> I explained three test flows: the most confident detection, the most confident correct negative, and
> the most confident mistake. This is the mistake: a benign flow called an attack with probability
> 0.999. It happens to use the attacker's TCP settings, and SHAP shows those two values alone add 5.7 and
> 3.5 log-odds. It is not a one-off: 1,197 of the 1,241 false alarms on the test set are benign flows with
> that fingerprint.

---

## Slide 8: Can we trust the explanation? (Part D)

**Source line:** Notebook Part D · results/tables/D4_deletion.csv, D5_lime_stability.csv, D6_investigation.csv

**Layout:** three cards.

- **Faithful.** Replacing each flow's top SHAP feature with its median flips **100%** of 500 attack decisions; one random feature flips 2.8%.
- **Stable.** TreeSHAP gives identical values on every rerun. LIME's top 3 changed between seeds, and was the same for all three flows.
- **Agreement.** SHAP and LIME share 1 to 2 of 3 features. LIME's local fit R² is 0.06 to 0.29: a straight line cannot fit a switch.

**Takeaway line:** We would show analysts SHAP: exact, stable and faithful here.

**Speaker notes.** Target time: 50 seconds. Presenter: Stefanos.

> Is the explanation itself right? Fidelity: on 500 flows called attacks, replacing the top SHAP feature
> with its training median flipped every single decision to benign; a random feature, 2.8%. So SHAP is
> faithful, and the test confirms the shortcut as cause and effect. Stability: TreeSHAP is exact and gives
> the same values every time. LIME changed with the seed, and gave the same top three for all three flows,
> so it was describing the model in general, not the flow. They agree only partly, and of four reasons I
> tested the main one is fit: the model behaves like a switch, and LIME's straight line cannot describe it.

---

## Slide 9: Noise and missing fields (Part E)

**Source line:** Notebook Part E · results/figures/E3_robustness.png, results/tables/E3_stop_trusting.csv

**Layout:** the robustness figure (large), big number on the right.

- Big number: **0.992 to 0.513**, boosting's recall at noise of one thousandth of a standard deviation.
- Logistic regression stays at 0.98 up to noise 0.02, twenty times more.
- Missing fields: one per flow is tolerated, two or three are not.

**Takeaway line:** The models fail silently: recall falls, the FAR does not, and the dashboard looks calmer.

**Speaker notes.** Target time: 45 seconds. Presenter: Stefanos.

> Part E. I added measurement noise, scaled to each feature's spread, and replaced fields with the
> training median. The rule for when to stop trusting a model was fixed before the tests. What broke
> first: the two tree models under noise. A thousandth of a standard deviation already halves boosting's
> recall. The reason is the shortcut again: the trees test for a narrow interval around the exact
> fingerprint value, and tiny noise moves it out. Logistic regression survives twenty times more. And in
> every case it was recall that broke, not the false alarm rate: fewer alerts, which looks like good news.

---

## Slide 10: What an attacker would fake (Part E)

**Source line:** Notebook Part E · results/tables/E4_feature_groups.csv, E4_whatif_benign_tcp.csv; separate notebook of additional checks

**Layout:** big number on the left, three cards on the right.

- Big number: **0.000**, boosting's recall when all 16,052 test attacks use a benign machine's TCP settings.
- **Cheap to fake.** 69% of the SHAP weight is on features the attacker controls, above all their own TCP settings.
- **All three models fall.** Tree 0.011, logistic regression 0.066.
- **One change is enough.** A greedy search allowed only attacker-controlled changes evades boosting for all 50 attacks it tried, each with one change to `Fwd Seg Size Min`.

**Takeaway line:** One or two system settings, at no cost to the attack, defeat all three models.

**Speaker notes.** Target time: 45 seconds. Presenter: Stefanos.

> What would an attacker fake? I sorted the features by who controls them. 69% of the SHAP weight is on
> features the attacker can change cheaply, above all the TCP settings of their own machine. If every
> test attack simply copies the most common benign settings, and nothing else, boosting's recall drops
> to zero. A greedy attack search, in the separate notebook of extra checks, allowed only changes the
> attacker controls, needed a single change for all 50 attacks it tried. I will show that live after
> Part F, which Kirill presents now.

---

## Slide 11: A belief rule base on two features (Part F)

**Source line:** Notebook Part F · results/tables/F2_rules.csv, F3_brb_comparison.csv

**Layout:** a small diagram on the left (two inputs, each Low / Medium / High, into a 3 x 3 grid of
rules), the comparison table on the right.

- Inputs: `FWD Init Win Bytes` and `Bwd Packets/s` (the top two SHAP features with three distinct levels: 5th percentile, median, 95th percentile). 9 rules, beliefs from the training data, threshold 48.5 chosen on validation.

| Test set, same 2 features | Macro-F1 | Recall | FAR |
|---|---|---|---|
| BRB, 9 rules | 0.953 | 0.982 | 0.044 |
| Decision tree (depth 4) | 0.962 | 0.996 | 0.040 |
| Random forest (100 trees) | 0.962 | 0.996 | 0.040 |

**Takeaway line:** 0.009 behind a fair comparison, because three levels cannot isolate the exact window 16,383.

**Speaker notes.** Target time: 55 seconds. Presenter: Kirill.

> Part F, a knowledge-based layer: a belief rule base with evidential reasoning, the engine from our Lab
> 3. Its inputs are the two most important SHAP features that take three distinct levels; the top
> feature had to be skipped because two of its three levels coincide. Three levels each gives nine rules
> like "if the window is High and the reply rate is Low, then High risk". Each rule's belief comes from the
> attack share of the training flows it covers, and the threshold was chosen on validation.
>
> The fair comparison is against a tree and a forest that see the same two features. The BRB is 0.009
> macro-F1 behind, because three levels are too coarse to isolate the exact fingerprint value.

---

## Slide 12: What Unknown buys (Part F)

**Source line:** Notebook Part F · results/tables/F4_beliefs.csv, F5_brb_vs_forest_checks.csv

**Layout:** three cards.

- **Less certain about the mistake.** For the false alarm of slide 7: Low 0.09, Medium 0.54, High 0.37, utility 63.8; still wrong, but not 0.999 sure.
- **Says when it cannot decide.** With `Bwd Packets/s` missing, Unknown rises to 0.43 and the risk becomes a range, 16.9 to 59.6, across the threshold.
- **Survives noise.** At noise 0.05 its macro-F1 is 0.897, against 0.472 for the 2-feature tree and 0.536 for the forest.

**Takeaway line:** The cost: lower accuracy, only two features (rules grow as 3 to the power of the number of features), and hand-made levels.

**Speaker notes.** Target time: 45 seconds. Presenter: Kirill.

> What does the BRB give for that cost? A traceable reason for each decision, and an explicit Unknown.
> For the false alarm from Part D it still says attack, but with beliefs spread over Medium and High, not
> 0.999. With an input missing, Unknown rises and the risk becomes a range that spans the threshold: the
> honest answer "cannot decide", which should go to an analyst. And it survives noise far better than the
> tree and forest on the same features. The costs are on the slide. Back to Stefanos for Part G.

---

## Slide 13: A new attack: Fuzzers (Part G)

**Source line:** Notebook Part G · results/tables/G2_hidden.csv, G3_adapt_summary.csv, results/figures/G3_adapt.png

**Layout:** big number on the left, the adaptation figure on the right, two cards below.

- Big number: **0.988 to 0.688**, recall on the 5,202 Fuzzers test flows when Fuzzers is hidden from training.
- **The dashboard looked better.** The FAR fell from 0.028 to 0.019; only the share of unsure predictions showed it (43% to 82%).
- **A few labels.** 100 Fuzzers flows labelled by an analyst: 0.706 as ordinary flows, **0.845** weighted 100 times.

**Takeaway line:** Watch the share of unsure predictions: it needs no labels.

**Speaker notes.** Target time: 60 seconds. Presenter: Stefanos.

> Part G. I hid one attack type, Fuzzers, a third of the training attacks, from training only, and
> retrained with the same settings. Recall on Fuzzers fell from 0.988 to 0.688, while the other types
> barely moved. And the false alarm rate went down, so the alert count would suggest things got better.
> The sign was elsewhere: 82% of Fuzzers flows got a probability between 0.1 and 0.9, against 43% before.
>
> Then an analyst labels 100 Fuzzers flows, taken from the removed training flows, never from test. As
> ordinary flows they barely help. Weighted 100 times they bring recall to 0.845: more than half of the
> loss recovered. A learning curve in the extra notebook reaches 0.956 with 500 weighted labels.

---

## Slide 14: Live: one attack, two settings changed

**Layout:** a short cue slide ("Live: the notebook"), then switch to the notebook window.

**What to show:** the end of the finished run, then the demo cell from [demo.md](demo.md): the test
attack the model is most sure about, before and after changing its TCP settings
(0.9996, then 0.0032, then 0.0000 in the last check).

**Speaker notes.** Target time: 40 seconds. Presenter: Stefanos.

> Back to the notebook: the run has finished, all the way to Part G. One more cell. This is the test
> attack the model is most sure about, an Exploits flow, 0.9996. I change one number, the segment size, to
> what normal machines use. Now it is 0.003: benign. That is one system setting on the attacker's side,
> and the attack itself is unchanged. Kirill closes.

---

## Slide 15: Would we deploy this?

**Source line:** Report Section 7 · results/tables/B4_alarms_per_day.csv, X6_clean.csv, X6_noise.csv, X3_attack_summary.csv

**Layout:** three cards, and the answer as the big word: **Not as it is.**

- **The numbers we least trust.** The 0.972 itself (it measures the UNSW-NB15 attacker machines), and the FAR: at a realistic 2.5% attacks only 48% of alerts would be real.
- **A better model.** Without the three TCP features: macro-F1 0.971, recall under noise 0.831 instead of 0.513, but the attack search still evades it for 34 of 50 attacks.
- **How we would run it.** The model without the fingerprint, the BRB as a readable second opinion that sends "cannot decide" to an analyst, monitoring of unsure predictions, and features over many flows.

**Takeaway line:** Where it would fail: shared operating systems, NAT or proxies that rewrite TCP settings, other flow tools, new traffic.

**Speaker notes.** Target time: 55 seconds. Presenter: Kirill.

> Would we deploy this? Not as it is. On this dataset it is excellent, but its accuracy rests on
> recognising a few attacker machines, and that says nothing about attackers elsewhere. Also, the test
> set has 26% attacks; real traffic has about 2.5%, and then fewer than half of the alerts would be real.
>
> Without the three TCP features, the model loses almost nothing, 0.971, and is far more robust to noise.
> We would deploy that one, but not alone: timing and padding are still cheap to fake. So: that model, the
> BRB as a second opinion that sends undecided flows to an analyst, monitoring of the share of unsure
> predictions, and features computed over many flows. Thank you.

---

## Slide 16: Questions

**Layout:** title only: "Questions", with the repository link or the hand-in file names in grey below.

---

## Backup slides (only if a question needs them)

Put them after the Questions slide; they are not part of the 13 minutes.

| # | Slide | Figure or table | For questions about |
|---|---|---|---|
| B1 | Recall per attack type | `results/figures/B4_recall_per_type.png` | small attack types, which types are missed |
| B2 | The deletion test | `results/figures/D4_deletion.png` | how fidelity was measured |
| B3 | The nine rules | `results/tables/F2_rules.csv` (as a 9-row table: rule, beliefs Low/Medium/High, attack share) | how the BRB decides |
| B4 | Learning curve for the hidden attack | `results/figures/X4_learning_curve.png` | how many labels are needed |
