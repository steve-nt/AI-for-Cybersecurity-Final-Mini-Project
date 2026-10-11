# Rehearsal: timing, run-throughs and questions

The talk has **13 minutes**, then questions. The plan in [slides.md](slides.md) takes 12:20, so there
are 40 seconds of buffer. Spoken at a calm pace (about 130 words a minute), the speaker notes fit their
target times; if they do not, shorten the notes, not the pace.

## Rules for cutting

- **Cut slides, not parts, and not a speaker.** Every part (A to G) must be covered, both of you must
  speak and explain the parts you built (a member who does not speak gets F), and the live run must be
  shown at least once. Part F is needed for grade 5.
- Cut in this order if a run-through is over 13:00:
  1. Slide 8 (trusting the explanation): say only the deletion result, 100% flipped against 2.8% (saves about 20 s).
  2. Slide 12 (what Unknown buys): merge into slide 11 as one sentence, "it says when it cannot decide" (saves about 30 s).
  3. Slide 5 (fewer labels): drop the sentence on 1% of the labels (saves about 10 s).
  4. Slide 4 (first live look): keep it, but only point at the table and switch back (saves about 10 s).
- Never cut: slide 6 (the shortcut), slide 10 (what an attacker fakes), slide 14 (the live cell), slide 15
  (would we deploy). Together they carry the "real judgement" that grade 5 asks for.

## Clock marks

Glance at the clock at these points. If you are more than 30 seconds late at a mark, use the next cut
from the list above.

| At the end of slide | Clock should read |
|---|---|
| 3 (Part B) | 2:40 |
| 5 (Part C) | 4:10 |
| 8 (Part D) | 6:35 |
| 10 (Part E) | 8:05 |
| 12 (Part F) | 9:45 |
| 14 (live cell) | 11:25 |
| 15 (end) | 12:20 |

## Run-through 1: Wednesday 14 October

Both of you together, standing, out loud, with the real slides and the real notebook run (not a dry run
without the demo), and with the handovers and the laptop driving exactly as planned. The person who is not
speaking keeps a phone stopwatch with laps: one lap per slide. If you cannot meet, each rehearses their
own slides alone with a timer, and you do run-through 2 together.

| # | Slide | Presenter | Target | Run 1 | Run 2 | Notes (what to change) |
|---|---|---|---|---|---|---|
| 1 | Title (press Run All) | Kirill | 0:35 | | | |
| 2 | Problem, data and baseline | Kirill | 1:10 | | | |
| 3 | Three models, one test | Kirill | 0:55 | | | |
| 4 | Live: test scores | Kirill | 0:30 | | | |
| 5 | 10% of the labels | Stefanos | 1:00 | | | |
| 6 | What the model looks at | Stefanos | 0:55 | | | |
| 7 | The most confident mistake | Stefanos | 0:40 | | | |
| 8 | Can we trust the explanation? | Stefanos | 0:50 | | | |
| 9 | Noise and missing fields | Stefanos | 0:45 | | | |
| 10 | What an attacker would fake | Stefanos | 0:45 | | | |
| 11 | A BRB on two features | Kirill | 0:55 | | | |
| 12 | What Unknown buys | Kirill | 0:45 | | | |
| 13 | A new attack: Fuzzers | Stefanos | 1:00 | | | |
| 14 | Live: one attack, two settings | Stefanos | 0:40 | | | |
| 15 | Would we deploy this? | Kirill | 0:55 | | | |
| | **Total** | Kirill 5:45, Stefanos 6:35 | **12:20** | | | |

After run-through 1:

- [ ] Total under 13:00? If not, apply the cuts above and run the slides that changed again.
- [ ] Did the notebook reach Part B by slide 4, and finish by slide 14? Write the run time here: ______
- [ ] Any slide where you read from the screen instead of talking? Make its text shorter.
- [ ] Were the four handovers (after slides 4, 10, 12 and 14) smooth? The next speaker stands ready
      before the last sentence of the previous one.
- [ ] Answer five questions from the list below out loud, without notes.

## Run-through 2: Thursday 15 October, morning

The full talk once more, in the same setup as the afternoon (if possible, with the laptop connected to a
second screen). Then stop rehearsing; a third full run tires more than it helps.

- [ ] Total under 13:00, with the live run.
- [ ] Backup video and slides on the USB stick.
- [ ] The setup steps of [demo.md](demo.md) are clear.

## Questions to expect

The brief: "Expect questions about any part of the work, not only your own part." So **each of you must
be able to answer every question below**, not only those on your own parts. The name after each heading
is who answers first, as the one who built that part; the other adds to it if needed. Short answers, with
the number that backs each one. All numbers are from the report and the result tables.

Before run-through 2, quiz each other: Kirill answers five questions from Stefanos's parts, and Stefanos
five from Kirill's.

### Data and models (Kirill)

**Why did you remove the duplicates?** 141,742 rows were exact copies. A copy in training and another in
test lets the model remember rather than generalise, so the test score would be too high. 1,068 more rows
had identical features but different labels, and were dropped too.

**Why not the larger CICFlowMeter_out.csv?** It contains IP addresses, and all attacks come from one
address range, so the address alone would give the label away.

**Did you subsample?** No. All 305,105 flows are used, and the notebook still runs in about 4 minutes
(with the saved models), including the additional checks.

**How did you choose the settings? Did you touch the test set?** Every candidate was trained on a 20% part
of the training set and scored on validation; the best macro-F1 won. The test set was used once at the
end. Validation and test agree within 0.003 on every score.

**Why gradient boosting and not a random forest?** Speed. In a trial run, a 300-tree forest took about 8
minutes to train and SHAP on 300 flows over 12 minutes, against seconds for boosting, and later parts
retrain and explain the black box many times.

**Is boosting really better than the tree?** By 0.003 macro-F1. A paired bootstrap (200 resamples, in the
additional checks at the end of the notebook) gives intervals of about plus or minus 0.002, so the lead is small but
real.

**Why these four scores?** Accuracy is misleading at 26% attacks (always-benign gets 0.737). Recall says
how many attacks we catch, FAR how many benign flows we flag, macro-F1 balances both classes, and PR-AUC
judges the ranking without a fixed threshold.

### Fewer labels (C) (Stefanos)

**Why did pseudo-labelling not help?** The lower line was already only 0.003 below the full model. The
confident guesses were 99.5% right in round 1, but they were flows the model already classified
correctly, so they added nothing new; round 2 added the borderline flows, and only 90% of those were right.

**Would it help with fewer labels?** A little: with 1% of the labels (1,830 flows) it gave +0.003 macro-F1
and +0.012 recall.

### Explanation (D) (Stefanos)

**How does SHAP work?** It splits a prediction among the features as a fair share (Shapley values from
game theory): each feature's average contribution over all orders in which features could be added.
For tree models, TreeExplainer computes this exactly, which is why reruns give identical values.

**How does LIME work, and why does it disagree?** It perturbs the flow, asks the model, and fits a
weighted straight line around the flow. Its fit here was poor (R² 0.06 to 0.29): the model behaves like a
switch on one TCP value, which a line cannot describe. Its quartile ranges also put values the model
treats oppositely into the same range. Without ranges and with samples drawn around the flow, LIME's top 3 for the detection became exactly SHAP's.

**What is the deletion test?** Replace a flow's top-k features (by the explanation) with the training
median and measure how much the prediction drops; compare with k random features. If the explanation is
right, its features matter more than random ones. Limitation: the edited flows can be unrealistic.

**Is the shortcut a bug in your code?** No, it is in the data: the UNSW-NB15 attacks were generated from a
few attacker machines, and 95% of training attacks announce a TCP window of exactly 16,383 bytes. Dos and
don'ts of ML in security (Arp et al., 2022) describe exactly this kind of spurious correlation.

### Robustness (E) (Stefanos)

**Why does tiny noise break the trees?** They test for a narrow interval around the exact fingerprint
value (the tree's first two questions isolate a window between 16,368.5 and 16,406.5). Noise of a
thousandth of a standard deviation moves values out of it. Logistic regression has no such thresholds.

**What was your rule for "stop trusting"?** Fixed before the tests: recall more than 0.05 below the clean
value, or FAR more than twice the clean value.

**How did you decide what an attacker controls?** Each feature was put in a group: free (timing and the
attacker's own packet sizes and TCP settings), costly (more own packets or bytes, a louder attack) or
fixed (the victim's replies). 69% of the SHAP weight is on free features.

### BRB (F) (Kirill)

**How does the BRB reach a decision?** Each input is matched to its three levels (Low, Medium, High),
which activates the nearby rules with weights. Evidential reasoning combines the activated rules'
beliefs into one belief over Low, Medium and High risk plus an Unknown part. The risk score is the
utility: Low 0, Medium 50, High 100, with Unknown counted halfway. Above 48.5 (chosen on validation) is an
alert.

**Where do the rule beliefs come from?** From the training data: each rule's attack share becomes its
belief, and rules with little data keep part of their belief as Unknown.

**Why these two features, and not the top SHAP feature?** The BRB needs three distinct levels (5th
percentile, median, 95th percentile). For `Fwd Seg Size Min` two of the three coincide, so it was
skipped, and the next two were used: `FWD Init Win Bytes` and `Bwd Packets/s`.

**Why is the BRB worse than the tree on the same features?** Three levels cannot isolate the exact window
value 16,383, which a tree can. The cost is 0.009 macro-F1.

**What is the point of Unknown, then?** It says when the evidence is missing. With `Bwd Packets/s`
missing, Unknown rose to 0.43 and the risk became a range (16.9 to 59.6) across the threshold: "cannot
decide". On the whole test set, a missing window leaves the BRB undecided for 65% of flows, while
boosting, given the median instead, misses 79% of attacks with no sign of doubt.

### Adaptability (G) (Stefanos)

**Why Fuzzers?** In a trial on the validation set, hiding it lowered its own recall the most of all types.
It is also large: 15,606 training flows, a third of the training attacks.

**Where did the 50 or 100 new labels come from?** From the Fuzzers flows removed from training, never from
the test set.

**Why weight 100? Was it tuned?** Not tuned: tuning would need Fuzzers labels the analyst does not have.
Weights 1, 10 and 100 are all shown. A learning curve in the extra notebook reaches 0.956 with 500
weighted labels.

**How would you notice a new attack without labels?** The share of unsure predictions (probability
between 0.1 and 0.9) nearly doubled, 43% to 82% on Fuzzers, and needs no labels. Also: compare incoming
feature distributions with training, label a small random sample every week, retrain regularly.

### Judgement (both)

**Which numbers do you trust least?** The 0.972 itself, because it measures how well the model recognises
the UNSW-NB15 attacker machines. The FAR, because the test set has 26% attacks; at a realistic 2.5%, only
48% of the alerts would be real. Recall on the small types (Worms has 47 test flows). And every LIME
explanation.

**Where would it fail outside this dataset?** Where attackers and normal users share operating systems,
behind NAT or proxies that rewrite TCP settings, with another flow tool, and on modern encrypted traffic;
the data are from a 2015 lab with synthetic normal traffic.

**Did you use AI?** Yes, declared in the report: Claude (Anthropic), through Claude Code, to compare
datasets, plan, explain concepts, write and review code, run experiments, check numbers and draft text.
The project decisions and the responsibility are ours.

**Who did what?** Kirill: Parts A, B and F. Stefanos: Parts C, D, E and G. Each made the additional
checks for their own parts; the dataset choice, the notebook, the README and the report were done
together. This is Section 8 of the report.

**Are the cached models cheating?** No. The cache is keyed on the features, the split, the seed and the
scikit-learn version, and deleting it retrains everything in about 25 minutes with the same numbers.

## On the day

- [ ] Both of you there from the start (a member who is absent gets F). Arrive early enough to connect the laptop and test the projector before 14:45.
- [ ] Setup steps from [demo.md](demo.md), 15 minutes before your slot.
- [ ] Water, a watch or phone stopwatch visible on the desk.
- [ ] After the talk: close the notebook without saving.
