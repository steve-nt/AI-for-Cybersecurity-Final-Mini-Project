# A guided tour of the project

Welcome! Think of this project folder as a small museum. Each folder is a room, and each file is an
exhibit. On this tour we walk from the entrance to the exit, and at every exhibit we answer four
questions:

- **What is it?**
- **Where is it?**
- **Why is it here?**
- **When is it useful?**

You do not need to know anything about programming. Where a technical word cannot be avoided, it is
explained on the spot. For the words, see [Abbreviations.md](Abbreviations.md); for the findings, see
[Plain-English-Guide.md](Plain-English-Guide.md).

## Before we start: what is this museum about?

The museum tells the story of a **burglar alarm for computer networks**. Computers constantly talk to
each other; each conversation is called a **flow**. Our alarm looks at a flow's numbers (how many
messages, how big, how fast) and decides "normal" or "attack".

We taught the alarm by showing it about 183,000 old conversations whose answers we knew, then tested it on
61,000 it had never seen. It got about 97% right by our main score. Then we asked the more interesting
questions:

- Can we see *why* it decides?
- Does it break easily?
- Can a human read its reasoning?
- What happens when a new kind of attack appears?

The surprise of the exhibition: the alarm mostly learned to **recognise the burglars' cars, not the
burglary**. In this dataset, all attacks came from a few lab computers with a recognisable "fingerprint",
and the alarm learned that fingerprint.

## The floor plan

```
AI-for-Cybersecurity-Final-Mini-Project/          the museum building
│
├── README.md                          Room 1: the entrance hall and information desk
├── UNSW-NB15/                         Room 2: the vault with the raw material
├── mini_project_unsw_nb15.ipynb       Room 3: the main exhibition hall
├── parts/                             Room 4: the workshops where the exhibits were made
├── src/                               Room 5: the toolbox of special instruments
├── models/                            Room 6: the storage room with the trained alarms
├── results/                           Room 7: the gallery of tables and pictures
├── tools/                             Room 8: the machine room
├── report/                            Room 9: the library
├── presentation/                      Room 10: the theatre
├── reference/, PreviousLabs/          Room 11: the archive
├── requirements.txt                   Room 12: the shopping list
└── the guides and logbooks            Room 13: the visitor centre
```

The tour follows the order a visitor would naturally need things: first how to get in, then the raw
material, then the main show, then the rooms behind the scenes.

## Room 1: the entrance hall (`README.md`)

**What is it?** A short text file that says what the project is, where to get the data, which software
to install, and how to run everything.

**Why is it here?** The assignment requires it. It is also the first thing anyone opens: a teacher, a
classmate, or ourselves in a year.

**When is it useful?** Whenever someone wants to rerun the project on their own computer. It also explains
the "run time" (about 4 minutes) and how the code is organised: a map of this museum for technical
visitors.

## Room 2: the vault (`UNSW-NB15/`)

**What is it?** The raw data: three files from a public dataset called CIC-UNSW-NB15.

| Exhibit | What it holds |
|---|---|
| `Data.csv` | 447,915 network conversations, each described by 76 numbers. Think of a huge spreadsheet: one row per conversation, one column per measurement |
| `Label.csv` | The right answer for each row: 0 for normal, or a number from 1 to 9 for the kind of attack |
| `Readme.txt` | The key that says which number means which attack (for example "Fuzzers 5") |

**Why is it here?** Everything is learned from these files. They were recorded in 2015 in a university lab
in Australia, where researchers ran normal traffic and real attacks on purpose.

**Why is the door locked?** The data are **not** included in the hand-in or in our shared code storage
(git), because they are too big (196 MB). The README says where to download them, and gives a
"fingerprint" of each file (called a SHA-256 hash) so you can check you got exactly the same files.

**Not on display:** a bigger file, `CICFlowMeter_out.csv`, which also holds the computers' addresses. All
attacks came from one group of addresses, so using it would be like an exam where the answers are
written on the question sheet. We left it out on purpose.

## Room 3: the main exhibition hall (`mini_project_unsw_nb15.ipynb`)

**What is it?** The **notebook**: the single most important file, and the one the teacher will open.
A notebook is a document that mixes explanations in plain text with small blocks of program code. When
you press "Run All", every code block runs from top to bottom, and its results (numbers, tables,
pictures) appear right under it.

**Why is it here?** The assignment asks for exactly one notebook that runs from top to bottom without
errors, in under 5 minutes. Ours runs in about 4.

**How is the hall laid out?** It has 155 blocks (called **cells**), and every cell starts with a small
label such as `STEP C2`. The letter says which part of the assignment it belongs to (A to G), and X means
an additional check. The hall is split into **two wings with a locked door between them**.

### The west wing: getting ready and making every choice

Here the alarm is built and every decision is made, **without ever looking at the final exam**.

| Exhibit (steps) | What happens | Why it matters |
|---|---|---|
| **Setup (A0)** | Loads the software, defines how we score an alarm (the five scores) and checks the scoring on a tiny made-up example | Everyone uses the same ruler; a wrong ruler would make every later number wrong |
| **The problem (A1)** | Explains who uses the alarm (a security team) and what a mistake costs | Tells us what "good" means before we measure anything |
| **Cleaning (A2)** | Reads the vault, removes 141,742 exact copies and 1,068 contradictory rows | Copies would let the alarm "remember" exam questions; contradictions cannot be learned |
| **The split (A3)** | Divides the 305,105 conversations into three piles: 60% to learn from (training), 20% to compare choices (validation), 20% as the final exam (test). **Then the final exam is locked in a safe** | A fair exam needs questions the student has never seen |
| **The silly baseline (A4)** | An "alarm" that always says "normal" | Gives a floor: it is right 73.7% of the time and catches nothing, which shows why "% right" alone is misleading |
| **The three alarms (B1, B2)** | Builds a decision tree (a flowchart of yes/no questions), a logistic regression (a weighted checklist) and gradient boosting (hundreds of small flowcharts voting). For each it tries a few settings and keeps the best one, judged on the validation pile | The first two can be read by a person; the third is stronger but unreadable. The assignment asks for both kinds |
| **Fewer labels (C1 to C3)** | Pretends we only know the answers for 10% of the conversations, and tries a trick (pseudo-labelling: let the alarm label the ones it is sure about, and learn from those too) | Labelling costs expert time; this tells us how much we really need |
| **Cutoffs for the extra check (X2)** | Picks the settings of the same trick with 1% and 5% of the labels | Every choice must be made in this wing, so it lives here |
| **What the alarm looks at (D1)** | Uses SHAP (a method that shares the credit for each decision among the measurements) on the validation pile | This is where the "burglars' car" discovery is made |
| **The readable alarm (F1 to F3)** | Builds a belief rule base: nine "if this, then that" rules a person can read, and picks its alarm threshold. Also picks a small flowchart to compare it with fairly | The assignment asks for a model built from human-style knowledge |

### The locked door: "Final evaluation on the test set" (T0)

A single cell unlocks the safe with the final exam. Before this point, **any cell that tried to touch the
exam would stop with an error**, so nobody can peek by accident. A checking machine in Room 8 also
refuses to build the notebook if anything in the west wing uses the exam.

**Why is it here?** Choosing settings after seeing the exam is like a student who sees the questions
first: the grade would be too good to be true. The door proves we did not.

### The east wing: the results, and nothing is chosen any more

| Exhibit (steps) | What it shows |
|---|---|
| **Exam scores (A4T, B3, C4)** | All alarms on the final exam, next to the silly baseline. Best: gradient boosting, 0.972 on our main score, only 0.003 ahead of the simple flowchart |
| **Where the alarms go wrong (B4)** | Which attack types are missed, and how many false alarms a real network would get per day: in realistic traffic only about half the alerts would be real |
| **Three conversations explained (D2, D3)** | One correctly caught attack, one correctly cleared normal conversation, and the most confident mistake: a normal conversation called an attack with 99.9% certainty, because it carried the attackers' fingerprint |
| **Is the explanation honest? (D4 to D6)** | The deletion test: remove what the explanation says matters and see if the decision changes (it flipped all 500 times). Then a second method, LIME, is tested and found unreliable here, with four tested reasons why |
| **Does it break easily? (E1 to E4)** | Adds tiny errors to the measurements, blanks some out, and plays the attacker. A tiny error halves what the best alarm catches; faking two settings makes it catch nothing |
| **The readable alarm on the exam (F3T to F5)** | The rule-based alarm against small flowcharts, and one decision traced step by step. It is a little less accurate, but readable, steadier under errors, and it can say "I cannot decide" |
| **A brand new attack (G1 to G4)** | Hides one attack type (Fuzzers) during learning, then shows how much it is missed, how a few expert labels help, and how a real team would notice |
| **Additional checks (X2T to X9)** | Extra experiments the report quotes: fewer labels still, a realistic attacker who may only change what they control, a learning curve, an alarm trained **without** the fingerprint, the rule-based alarm with missing inputs, and how precise each exam score is |

**When is the hall useful?** At the hand-in (the teacher runs it), at the presentation (we run it live
and point at cells), and whenever someone asks "where does this number come from?".

## Room 4: the workshops (`parts/`)

**What is it?** Eight smaller notebooks, one per part of the assignment. The main hall is **assembled**
from them, like an exhibition put together from pieces made in separate workshops.

| Workshop | What was made here | Made by |
|---|---|---|
| `00_setup.ipynb` | The setup, cleaning, split, the safe for the final exam, and the storage room system | both |
| `10_baseline_models.ipynb` | Parts A and B: the problem, the silly baseline, the three alarms | Kirill |
| `20_few_labels.ipynb` | Part C: fewer labels | Stefanos |
| `30_explanation.ipynb` | Part D: SHAP, LIME, the deletion test | Stefanos |
| `40_robustness.ipynb` | Part E: errors, missing measurements, the attacker | Stefanos |
| `50_brb.ipynb` | Part F: the readable rule-based alarm | Kirill |
| `60_adaptability.ipynb` | Part G: the hidden new attack | Stefanos |
| `70_extras.ipynb` | The additional checks | each for their own parts |

**Why is it here?** Two people could work at the same time without getting in each other's way, and each
part can be run and checked on its own. Every workshop starts by running the setup workshop, so they all
start from the same data.

**When is it useful?** When you change something: you edit the workshop, then rebuild the main hall with
the assembly machine (Room 8). You never edit the main hall by hand.

## Room 5: the toolbox (`src/`)

**What is it?** Two files of reusable instruments, both brought over from our earlier course labs, plus
tests for them.

| Exhibit | What it does | Used in |
|---|---|---|
| `xai_tools.py` | The explanation instruments: compute SHAP, run LIME, run the deletion test, measure how stable LIME is and how much SHAP and LIME agree | Part D, and the additional checks |
| `brbes.py` | The engine of the readable rule-based alarm: turns a measurement into Low, Medium or High, decides which rules fire, combines their beliefs, gives a risk score from 0 to 100, and can print a decision step by step | Part F, and the additional checks |
| `test_xai_tools.py`, `test_brbes.py` | 16 small automatic tests that check the instruments give the right answers on hand-made examples | Run with `python -m pytest src` |

**Why is it here?** Keeping the instruments in their own files keeps the notebook readable: the notebook
says *what* we do, the toolbox holds *how*. The tests are a quality stamp: if someone breaks an instrument,
a test fails.

**When is it useful?** The notebook needs it every run, so it must sit next to the notebook. The tests are
useful after any change to the instruments.

## Room 6: the storage room (`models/`)

**What is it?** 112 saved files (19 MB): every trained alarm and every slow result (for example the LIME
runs and the error experiments), in a sub-folder with a code name like `d8137a9708`.

**Why is it here?** Training everything from scratch takes about 25 minutes, but the assignment allows 5.
So the first run saves its work here, and later runs simply load it, like reheating a meal instead of
cooking it again.

**Is that cheating?** No. The code name of the sub-folder is a fingerprint of the exact setup (the
measurements used, the size of the piles, the random seed and the software version). If anything changes,
the code name changes, and the notebook trains fresh instead of loading old results. Because the
randomness is fixed (seed 42), a run with or without the storage room gives the same numbers. Delete the
folder to prove it.

**When is it useful?** Every run, and especially during the live demo.

## Room 7: the gallery (`results/`)

**What is it?** Everything the notebook produces, saved as files:

- `results/tables/`: 68 files, almost all tables (spreadsheet files, CSV), such as `B3_test_scores.csv`.
- `results/figures/`: 14 pictures, such as `E3_robustness.png`.

Each file name starts with the step that made it, so `D4_deletion.png` came from step D4. One table is
special: `T4_feature_glossary.csv` explains each of the 67 measurements in plain words. The notebook reads
it to label its pictures.

**Why is it here?** The report and the slides quote these files, so every number has a written source.

**When is it useful?** When writing, when checking a number, or when someone asks "show me".

## Room 8: the machine room (`tools/`)

Three machines that keep the museum in order. Visitors rarely see them, but without them things drift
apart.

| Machine | What it does | Why we built it |
|---|---|---|
| `assemble.py` | Collects the cells from the eight workshops, puts them in the right order (west wing, locked door, east wing), leaves out scaffolding cells (marked `STANDIN`), writes the main hall and runs it. In "strict" mode it refuses to build if a west-wing cell touches the final exam | So the main hall is always built the same way, and the exam rule is checked by a machine, not by memory |
| `check_report_numbers.py` | Reads the report and checks all 446 numbers in it against the gallery tables and the notebook's output | A single wrong number in a report can cost trust; this catches it |
| `feature_glossary.py` | Writes the plain-word explanation of each measurement (the glossary table in the gallery) | Explanations are only useful if a person knows what "Fwd Seg Size Min" means |

**When is it useful?** After any change: rebuild with `assemble.py --strict`, then run the number check.

## Room 9: the library (`report/`)

**What is it?** The written report, 6 to 8 pages with the eight headings the assignment asks for.

| Exhibit | What it is |
|---|---|
| `Mini_Project_Report.md` | The report itself, as plain text. This is the one we edit |
| `build_docx.py` | Turns it into a Word file, `Mini_Project_Report.docx`, with the university's title page (from `title_page_template.docx`) |
| `build_report.py` | Turns it into a PDF directly; `build_docx.py` borrows its helpers |
| `report_figures.py` | Copies the four pictures the report uses from the gallery into `report/figures/`, removing their notebook titles because the report has its own captions |
| `fonts/` | The letter shapes the PDF uses, so it looks the same on every computer |

**Why is it here?** The report is half the grade. Keeping one text source and generating the Word file
from it means there is only one version of the truth.

**When is it useful?** At the hand-in: open the Word file and save it as PDF.

## Room 10: the theatre (`presentation/`)

**What is it?** Everything for the 13-minute talk on 15 October.

| Exhibit | What it is |
|---|---|
| `slides.md` | The text of all 15 slides and the speaker notes, with timings |
| `build_slides.py` | Turns `slides.md` into the slide deck, in the style of the course seminar template |
| `Mini_Project_Presentation.pptx` | The finished slide deck |
| `demo.md` | The plan for running the notebook live during the talk, with a backup plan |
| `rehearsal.md` | The timing plan, rules for what to cut if we run long, and expected questions |

**Why is it here?** Both members must present and explain their own parts, and the notebook must be shown
running. Generating the slides from one text file keeps the slides and the speaking notes in agreement.

## Room 11: the archive (`reference/`, `PreviousLabs/`)

**What is it?** Our earlier course labs. The toolbox instruments in Room 5 came from here, and the way
the workshops are organised copies the lab structure.

**Why is it here?** Reuse: the labs had already tested the instruments. It is **not** part of the hand-in,
because it is not this project's work.

## Room 12: the shopping list (`requirements.txt`)

**What is it?** The list of software packages the project needs, each with its exact version number (for
example scikit-learn 1.6.1, the machine learning library).

**Why is it here?** Software changes over time. Pinning the versions means someone installing the
project next year gets the same behaviour and the same numbers.

## Room 13: the visitor centre (guides and logbooks)

| Exhibit | What it is | When it is useful |
|---|---|---|
| `Plain-English-Guide.md` | The whole story and findings in plain words | Preparing to explain any part |
| `Professor-Questions.md` | Likely questions from the examiner, with short answers | Practising for the questions after the talk |
| `Abbreviations.md` | Every abbreviation and short name, explained | When a word is unclear |
| `Museum-Tour.md` | This tour | When you want to know which file does what |
| `Files-To-Submit.md` | Exactly what to upload, and the command that packs the code | The evening before the deadline |
| `Dataset_Choice.md` | Why we chose UNSW-NB15 over the other dataset we considered (CIC-DDoS2019) | If asked "why this dataset?" |
| `TASKLIST.md` | Our internal planning board | Keeping track of what is left (not handed in) |
| `CHANGELOG.md` | A diary of every change, with date and reason | Finding out when and why something changed |

## The life of one number: the full tour in one example

To see how the rooms work together, follow the headline number **0.972** (gradient boosting's main score
on the final exam):

1. **Vault:** the conversations are read from `UNSW-NB15/Data.csv` and `Label.csv`.
2. **Main hall, west wing:** they are cleaned (A2) and split, and the exam is locked away (A3). Gradient
   boosting is trained and its settings chosen on the validation pile (B2). The trained alarm is saved in
   the **storage room** so the next run can load it.
3. **The locked door (T0):** the exam is unlocked.
4. **East wing:** the alarm takes the exam (B3), scoring 0.972 with the ruler defined in the setup (A0).
5. **Gallery:** the score is written to `results/tables/B3_test_scores.csv`.
6. **Machine room:** `check_report_numbers.py` confirms that the 0.972 in the report matches that table.
7. **Library and theatre:** the report and the slides quote it, and the explanation rooms (Part D) show why
   it is less impressive than it looks.

## The way out: what leaves the building

At the hand-in, two packages leave the museum:

- **The report** as a PDF, from the library.
- **A zip file** with the main hall, the entrance hall, the shopping list, the toolbox, the machine room,
  the workshops, the gallery and the storage room.

The vault (the data) stays behind because it is too big; the README tells the teacher where to download
it. The theatre, the archive and the visitor centre stay behind as well, because they are for us, not
part of the work being graded. The exact list and command are in [Files-To-Submit.md](Files-To-Submit.md).

Thank you for visiting!
