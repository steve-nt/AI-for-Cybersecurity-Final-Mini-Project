# The project in plain English

This guide explains the whole mini project without jargon: what we built, what we found, and how the
files fit together. Every number comes from the report and the result tables. Read it before the
presentation, or when you need to explain something you did not build yourself.

## 1. The project in one paragraph

We built a computer program that looks at network traffic and decides, for each connection, "normal"
or "attack". We trained three such programs (models) on a public dataset, and they are right about 97%
of the time by the measure we use. Then we asked harder questions: does it still work with far fewer
labelled examples, can we see *why* it decides what it decides, does it break when the data are a bit
messy, can we build a version a human can read, and what happens when a brand new kind of attack shows
up? The most important finding came from the "why" question: the models mostly recognise **the
attackers' computers**, not the attacks themselves. That makes them look excellent on this dataset and
easy to fool in real life.

## 2. The words you need

| Word | What it means |
|---|---|
| **Flow** | One conversation between two computers on a network, summarised as numbers: how many packets, how big, how fast, which settings. Our data has 305,105 of them. |
| **Feature** | One of those numbers, for example "packets per second sent back". We use 67 features. |
| **Label** | The right answer for a flow: benign (normal) or attack, and which attack type. |
| **Model** | A program that learns from labelled flows and then guesses the label of new flows. |
| **Training, validation and test sets** | We split the flows three ways. The model learns from the **training** set (60%). We compare settings on the **validation** set (20%). The **test** set (20%) is the final exam, used only once all choices are made. |
| **Recall** | Of all real attacks, how many we caught. 0.99 means 99 out of 100. |
| **FAR (false alarm rate)** | Of all normal flows, how many we wrongly flagged as attacks. Lower is better. |
| **Macro-F1** | One score from 0 to 1 that balances "catching attacks" and "not crying wolf", giving the normal class and the attack class equal weight. Our main score. |
| **PR-AUC** | How well the model *ranks* flows from "surely attack" to "surely normal", without picking a cut-off. |
| **Glass box / black box** | A glass-box model can be read by a human (a decision tree, a weighted sum). A black-box model is too complex to read (gradient boosting, hundreds of small trees). |
| **SOC analyst** | The person in a Security Operations Centre who receives the alerts and decides what to do. They are the "user" of our detector. |

## 3. The data (Part A)

- **What it is.** CIC-UNSW-NB15: network traffic recorded in 2015 in a university lab in Australia, with
  normal traffic and nine attack types, turned into flows with 76 features by a tool called
  CICFlowMeter.
- **Why not the bigger file.** The dataset also has a larger file with IP addresses. All attacks come from
  one group of addresses, so a model could just read the address and know the answer. That would be
  cheating, so we did not use it.
- **Cleaning.** 141,742 rows were exact copies of other rows. If one copy lands in training and another
  in test, the model has "seen the exam answers", so we removed the copies. Another 1,068 rows had
  identical numbers but different labels (the data contradicts itself), so we removed those too.
- **What is left.** 305,105 flows, all used (no sampling down). 26.3% are attacks. The largest attack
  types are Exploits (10.1%) and Fuzzers (8.5%); four types are tiny (under 1% each).
- **The silly baseline.** A "model" that calls everything normal is right 73.7% of the time, because
  most traffic is normal. That is why plain accuracy is useless here: it catches zero attacks. Its
  macro-F1 is 0.424, and every real model has to beat that.

## 4. The three models (Part B)

| Model | What it is, simply | Test macro-F1 |
|---|---|---|
| Decision tree | A flowchart of yes/no questions ("is this number above 20?") | 0.969 |
| Logistic regression | Gives each feature a weight, adds them up, turns the sum into a probability | 0.961 |
| Gradient boosting | Hundreds of small trees, each fixing the mistakes of the ones before | **0.972** |

- **How settings were picked.** Each model has knobs (how deep the tree, how strong the penalty, how fast
  boosting learns). We tried a few values for each, scored them on the validation set, and kept the best.
- **What the results say.** All three are far above the silly baseline. Boosting wins, but by only 0.003
  over the simple tree. Logistic regression catches the most attacks but raises the most false alarms.
  A statistical check (the bootstrap, see section 10) shows the 0.003 lead is small but real.
- **Why the small lead is a warning.** If a simple flowchart is almost as good as the most complex model,
  the problem is probably being solved by a few very strong clues. Part D found out which clues.
- **Real-world reality check.** In our data 26% of flows are attacks. In real traffic it is closer to
  2.5%. At that rate, only about **half** of boosting's alerts would be real attacks (48%), against 93%
  on our test set. The scores flatter every model.

## 5. Fewer labels (Part C)

- **The question.** Labelling traffic costs expert time. What if we only had labels for 10% of the
  training flows?
- **The answer.** Boosting trained on 10% of the labels scores 0.969, only 0.003 below the version with
  all labels. So labels are not the bottleneck here.
- **Pseudo-labelling.** A trick to use the unlabelled 90%: let the model label the flows it is very sure
  about, add those guesses to the training data, retrain, and repeat. It **did not help** (0.969 before
  and after).
- **Why not.** In the first round the model's confident guesses were 99.5% right, but they were flows it
  already got right, so it learned nothing new. In the second round it added the borderline flows, and
  only 90% of those guesses were right.
- **With 1% of the labels** (1,830 flows) the trick gave a small real gain. It only helps when labels are
  really scarce.

## 6. Why the model decides what it decides (Part D)

This is the heart of the project.

- **SHAP** is a method that splits each decision into "how much did each feature push towards attack or
  normal". Think of it as a fair way of sharing credit among the features. For tree models it is exact
  and gives the same answer every time.
- **The discovery.** Three features carry 76% of the model's reasoning, and the top two are **TCP
  settings of the computer that starts the connection** (`Fwd Seg Size Min` and `FWD Init Win Bytes`).
  These are like a fingerprint of the computer's operating system, not a sign of attack behaviour. 95% of
  the training attacks use a window size of exactly 16,383. All attacks in this dataset were launched from
  a few lab machines, so the model learned to **recognise those machines**. This is called a
  **shortcut**: a clue that works in the dataset but not in the real world.
- **The scariest mistake.** A normal flow that happened to have the same TCP settings was called an attack
  with 99.9% certainty. 1,197 of the 1,241 false alarms on the test set are normal flows with this
  fingerprint.
- **Is SHAP telling the truth? (fidelity)** We took 500 flows the model called attacks and replaced each
  one's most important feature (by SHAP) with a normal value. **All 500 flipped to "normal".** Replacing a
  random feature flipped only 2.8%. So SHAP points at what really drives the model, and the test proves
  the shortcut is the cause.
- **LIME** is a second explanation method. It nudges the flow many times, watches how the model reacts,
  and draws a straight line through the reactions. It **only partly agreed** with SHAP and gave different
  answers on different runs.
- **Why LIME struggles here.** The model behaves like a light switch (one TCP value flips the answer from
  "attack" to "normal"), and a straight line cannot describe a switch. LIME's fit was poor (R² from 0.06
  to 0.29, where 1 is perfect). We would show analysts SHAP, not LIME.

## 7. Does it break easily? (Part E)

- **Noise.** We added small random errors to the numbers, as a slightly faulty sensor would. With an
  error of just **one thousandth** of a typical value, boosting's recall fell from 0.992 to 0.513: it
  missed half the attacks. Logistic regression survived errors twenty times bigger.
- **Why.** The tree models look for a very narrow window around the exact fingerprint value 16,383. Even
  a tiny wobble moves the value out of the window.
- **Missing fields.** We blanked out some features and filled in a typical value. One missing field per
  flow is fine; two or three are not. If the top TCP feature goes missing, boosting misses **every**
  attack, because the typical value filled in is the normal machines' value.
- **Silent failure.** In every case the model failed by raising *fewer* alarms. On a dashboard that looks
  like good news.
- **What would an attacker fake?** 69% of the model's reasoning sits on features an attacker can change
  for free (their own TCP settings). Giving every test attack the normal machines' settings, and changing
  nothing else, drops boosting's recall to **0.000**. A search for the cheapest disguise needed just
  **one** change to fool boosting on all 50 attacks it tried.
- **The trust rule.** Before testing, we decided: stop trusting a model when recall drops more than 0.05
  or the false alarm rate doubles. Deciding this in advance stops us from moving the goalposts later.

## 8. A model a human can read: the belief rule base (Part F)

- **What a BRB is.** A small set of "if, then" rules, like an expert's rules of thumb, but with
  uncertainty built in. Each input is graded Low, Medium or High. With two inputs that gives 3 × 3 = 9
  rules, for example "if the window is High and the reply rate is Low, then the risk is mostly High".
- **Where the rules come from.** From the training data: for each rule we count how often its flows were
  attacks. Rules with little data keep part of their belief as **Unknown**.
- **The output.** A risk score from 0 to 100. Above 48.5 (picked on the validation set) is an alert.
- **How good is it?** Macro-F1 0.953, against 0.962 for a tree or a forest given the same two features.
  It is a little worse because three levels (Low, Medium, High) cannot pinpoint the exact value 16,383.
- **What it buys.** You can read all nine rules and trace every decision. It is far more robust to noise
  (0.897 against 0.472 for the small tree). And it can say **"I cannot decide"**: with one input missing,
  its Unknown part rose to 0.43 and its risk became a range from 16.9 to 59.6, across the alert line.
  On the whole test set with the window missing, the BRB says "undecided" for 65% of flows, while
  boosting quietly misses 79% of the attacks.

## 9. A brand new attack (Part G)

- **The test.** We removed all **Fuzzers** attacks from training (a third of the training attacks) and
  retrained, as if Fuzzers had never been seen. Fuzzers was picked because, in a trial, hiding it hurt
  its own detection the most.
- **What happened.** Recall on Fuzzers fell from 0.988 to 0.688. The false alarm rate **went down**, so
  the alert count suggested everything was fine. But the model was visibly unsure: 82% of Fuzzers flows
  got a probability between 0.1 and 0.9, against 43% before.
- **Adapting.** An analyst labels 50 or 100 Fuzzers flows (taken from the removed training flows, never
  from the test set). Added as ordinary examples they barely help (0.706 with 100). Given **100 times the
  weight** of other examples, the same 100 labels raise Fuzzers recall to 0.845. With 500 weighted labels
  it reaches 0.956.
- **How you would notice in real life.** Watch the share of unsure predictions (it nearly doubled and
  needs no labels), compare incoming traffic with the training data, have analysts label a small random
  sample every week, and retrain regularly.

## 10. The additional checks

At the end of the notebook are extra experiments the report quotes. In plain words:

- **Fewer labels still (1% and 5%):** where pseudo-labelling starts to help a little.
- **Bootstrap confidence intervals:** we resample the test set 200 times to see how much each score
  would wobble by chance. About ±0.002 on macro-F1, so boosting's 0.003 lead over the tree is real.
- **A realistic attacker search:** an attacker who may only change what they really control. One change
  fools boosting every time.
- **A learning curve for Fuzzers:** how recall grows with 25 up to 500 labels.
- **A model without the shortcut:** boosting retrained **without the three TCP-settings features**. It
  scores 0.971 (almost the same!), handles noise far better (recall 0.831 instead of 0.513) and reasons
  with behaviour features instead. But the attacker search still fools it on 34 of 50 attacks, by waiting
  about 10 ms longer between packets or padding them.
- **The BRB with missing inputs and an edited rule:** how the "I cannot decide" answer behaves on the
  whole test set, and that a human can change one rule and see the effect.

## 11. The bottom line: would we deploy this?

**Not as it is.** The 0.972 score mostly measures how well the model recognises a few lab machines, which
says nothing about real attackers. We would:

1. use the model **without** the shortcut features, which loses almost nothing;
2. run the BRB next to it as a readable second opinion that sends undecided flows to a human;
3. monitor for new attacks as in Part G;
4. add features computed over many flows, which one attacker cannot easily shape.

**The numbers we trust least:** the 0.972 itself (shortcut), the 0.028 false alarm rate (made with 26%
attacks instead of a realistic 2.5%), recall on the tiny attack types (Worms has only 47 test flows), and
every LIME explanation.

**Where it would fail:** on networks where attackers and normal users run the same operating systems,
behind proxies that rewrite TCP settings, with a different flow tool, and on modern encrypted traffic.
The data are from a 2015 lab with simulated normal traffic.

## 12. How the notebook is built and why it is fair

- **One notebook, assembled from parts.** Each part of the brief has its own notebook in `parts/`
  (`00_setup`, `10_baseline_models` for A and B, `20_few_labels` for C, and so on up to `70_extras`).
  `tools/assemble.py` glues them into the hand-in notebook `mini_project_unsw_nb15.ipynb`.
- **Two phases, so the test set really is the final exam.**
  1. **Development phase:** every choice (model settings, pseudo-label cutoffs, the BRB's features and
     threshold) is made on the validation set. The test set is locked away; any cell that tried to use
     it would stop with an error.
  2. **"Final evaluation on the test set":** the test set is unlocked.
  3. **Evaluation phase:** only reports test scores. Nothing is chosen here.

  This answers the obvious examiner question "did you peek at the test set?" with "no, and the code
  proves it". Validation and test scores agree within 0.003, another sign nothing was over-tuned.
- **Saved models.** Training everything from scratch takes about 25 minutes, but the brief allows 5. So
  the trained models are saved in `models/`, and the notebook loads them, running in about 4 minutes.
  The save folder is named after a fingerprint of the setup (features, split, seed, library version), so
  a different setup never loads the wrong models. The seed is fixed at 42, so the numbers are the same
  with or without the saved models.
- **Number check.** `tools/check_report_numbers.py` checks every number in the report (446 of them)
  against the result tables the notebook writes, so the report cannot drift from the code.

## 13. Who did what

- **Kirill Silchenko:** Parts A (problem, data, baseline), B (the three models) and F (the BRB).
- **Stefanos Ntentopoulos:** Parts C (fewer labels), D (explanations), E (robustness) and G (new attack).
- Each made the additional checks for their own parts. Both chose the dataset and wrote the notebook,
  the README and the report together.

At the presentation either of you can be asked about any part, so each should be able to explain every
section of this guide.

## 14. What gets handed in

Two uploads on Canvas before **Thursday 15 October, 08:00**: the report as a PDF, and a zip with the
notebook, README, requirements, `src/`, `tools/`, `parts/`, `results/` and `models/`. The exact steps and
the zip command are in [Files-To-Submit.md](Files-To-Submit.md). The talk is on 15 October from 14:45;
its plan is in [presentation/](presentation/).
