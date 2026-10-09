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
