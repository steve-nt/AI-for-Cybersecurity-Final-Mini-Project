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
Be ready to open any cell and explain it line by line. Good ones to practise: the data cleaning, the
sealed test set, the pseudo-labelling loop, the deletion test, and the BRB inference.

**Who did what?**
Kirill: Parts A, B and F. Stefanos: Parts C, D, E and G. Each made the additional checks for their own
parts; the dataset choice, the notebook, the README and the report were done together.
