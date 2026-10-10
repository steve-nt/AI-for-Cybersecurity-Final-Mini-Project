# Mini Project: An Explainable and Robust Cyber-Defence Model

AI for Cybersecurity (D7084E / D7041E), Stefanos Ntentopoulos (stente-5@student.ltu.se), a one-person
group.

Is a network flow an attack or normal traffic? We train a decision tree, a logistic regression and
gradient boosting on all 305,105 clean flows of CIC-UNSW-NB15, and work through Parts A to G of the
brief in order: the problem, the data and the always-benign baseline (A); the supervised models (B);
learning with 10% of the labels plus pseudo-labelling (C); SHAP and LIME explanations with fidelity and
stability checks (D); measurement noise and missing features (E); a belief rule base on the two most
important features (F); and an attack type (Fuzzers) hidden from training and then adapted to (G).
The main finding is a shortcut: the models recognise the attacker machines' TCP settings
(`Fwd Seg Size Min`, `FWD Init Win Bytes`) rather than attack behaviour.

- **Notebook to hand in:** `mini_project_unsw_nb15.ipynb`. It runs from top to bottom in about
  2 minutes (see [Run time](#run-time)) and holds Parts A to G in order.
- **Report:** `report/` (PDF built from the Markdown source).

## Dataset

**CIC-UNSW-NB15**: the UNSW-NB15 traffic recordings, turned into flows with CICFlowMeter by the
Canadian Institute for Cybersecurity. It has 76 numeric flow features (the same kind as CICIDS2017)
and nine attack types. This is not the original 49-feature UNSW-NB15 table.

- **Where to get it:** https://www.unb.ca/cic/datasets/cic-unsw-nb15.html (the download page asks for a
  name and e-mail address).
- **Files needed**, in a folder `UNSW-NB15/` in the project root. The data are **not in git**
  (196 MB, over GitHub's file limit):

  | File | Contents | SHA-256 |
  |---|---|---|
  | `Data.csv` | 447,915 flows x 76 features (the 80/20 benign/attack set) | `60d55f4f8f1e72bdfa2e0c1c74c03ac301bd880af321fdad1ba453950a7aa16a` |
  | `Label.csv` | One label code per flow, 0 (benign) to 9 | `5b2fcf31dc2d03ac6a07f8791858e55d86306f05442c3a4528bcc67301956a56` |
  | `Readme.txt` | The names of the label codes (`Fuzzers 5`, ...) | |

  `CICFlowMeter_out.csv` (1.9 GB, also on the page) is **not used**: it contains IP addresses, and all
  attacks come from one address range, so the address alone gives the label away.
- **Cleaning** (in the notebook, Part A): 141,742 exact duplicate rows and 1,068 rows whose features
  appear with both labels are dropped, leaving **305,105 flows, 26.3% attacks**. All of them are used.
  They are split 60/20/20 into training, validation and test (183,063 / 61,021 / 61,021 flows),
  stratified on the attack type. Nine features that never change are dropped, leaving 67.

Please cite:

- H. Mohammadian, A. H. Lashkari, A. A. Ghorbani. "Poisoning and Evasion: Deep Learning-Based NIDS under
  Adversarial Attacks." *21st Annual International Conference on Privacy, Security and Trust (PST)*,
  2024. (Required by the dataset page.)
- N. Moustafa, J. Slay. "UNSW-NB15: a comprehensive data set for network intrusion detection systems
  (UNSW-NB15 network data set)." *Military Communications and Information Systems Conference (MilCIS)*,
  2015. (The original recording.) https://research.unsw.edu.au/projects/unsw-nb15-dataset

## Setup

```bash
uv venv --python 3.13 .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
sha256sum UNSW-NB15/Data.csv UNSW-NB15/Label.csv   # must match the table above
python -m pytest src                   # optional: tests of the helpers in src/, "16 passed"
```

Python 3.13.7 (3.11 to 3.13 should work). Pinned versions: scikit-learn 1.6.1, shap 0.52.0,
lime 0.2.0.1, numpy 2.5.3, pandas 3.0.6, scipy 1.18.1, matplotlib 3.11.2, joblib 1.6.0, plus Jupyter,
nbformat and nbconvert. fpdf2 and markdown are only needed to build the report PDF, pytest only for the
tests. No `uv`? Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`, or use
`python -m venv .venv` and `pip install -r requirements.txt` instead.

## How to run

Run every command from the project root, with the environment active.

| What | Command |
|---|---|
| Run the hand-in notebook, top to bottom | `jupyter nbconvert --to notebook --execute --inplace mini_project_unsw_nb15.ipynb` (or *Run All* in Jupyter) |
| Rebuild the hand-in notebook from the part notebooks, and run it | `python tools/assemble.py --strict` |
| Also include the optional extras (not part of the hand-in) | `python tools/assemble.py --with-extras --output extras_run.ipynb` |
| Rebuild the feature glossary table | `python tools/feature_glossary.py` |

The notebook needs three things next to it, besides the data:

- **`src/`**: Parts D and F import `src/xai_tools.py` (SHAP and LIME helpers) and `src/brbes.py` (the
  belief rule base engine). Keep the folder next to the notebook.
- **`results/tables/T4_feature_glossary.csv`**: the plain-language meaning of every feature, read by
  Parts D, E and F. It is in git; `tools/feature_glossary.py` rebuilds it.
- **`models/`**: the saved models (see below). Optional, but without it the run is slow.

### Run time

On an 8-core machine with 19 GB RAM the hand-in notebook runs in **107 seconds** with the saved models
in `models/`, and in **about 25 minutes** without them. The brief's limit is 5 minutes, so `models/` is
shipped with the code.

`models/` holds every trained model and the slow results (the LIME runs, the noise and missing-feature
sweeps, the retrained models of Parts F and G): 74 files, 13 MB. The first run creates them and later
runs load them. They sit in a sub-folder named after a fingerprint of the feature list, the split sizes,
the seed and the scikit-learn version, so a different setup never loads old results; it retrains
instead. Delete `models/` to force a full retraining. `random_state=42` is used everywhere, so a run
with or without the saved models gives the same numbers.

**Google Colab:** upload the notebook, `Data.csv`, `Label.csv` and `Readme.txt` next to it (the notebook
uses them there when `UNSW-NB15/` does not exist), the `src/` folder, and
`results/tables/T4_feature_glossary.csv`. Upload `models/` as well to keep the run short. The first cell
installs shap and lime if they are missing.

## How the code is organised

The work is split into part notebooks, one per part of the brief. Each cell starts with the step it
belongs to (`# STEP C2`, or `<!-- STEP C2 -->` in Markdown). Cells that only stand in for another
notebook's step during development are marked `# STANDIN`. `tools/assemble.py` collects the `STEP`
cells from all part notebooks, puts them in order (A0 to G4), drops the stand-ins and the optional
extras, and writes and runs the hand-in notebook.

| Path | Contents |
|---|---|
| `mini_project_unsw_nb15.ipynb` | The hand-in notebook (built by `tools/assemble.py`) |
| `parts/00_setup.ipynb` | Setup: libraries, scores, loading, cleaning, the split, the model cache |
| `parts/10_baseline_models.ipynb` | Part A (problem, baseline) and Part B (tree, logistic regression, gradient boosting) |
| `parts/20_few_labels.ipynb` | Part C: 10% of the labels, pseudo-labelling |
| `parts/30_explanation.ipynb` | Part D: SHAP, LIME, the deletion test, stability, why they disagree |
| `parts/40_robustness.ipynb` | Part E: noise, missing features, what an attacker could fake |
| `parts/50_brb.ipynb` | Part F: the belief rule base and its comparison with small trees |
| `parts/60_adaptability.ipynb` | Part G: Fuzzers hidden from training, then adapted to |
| `parts/70_extras.ipynb` | Optional extras: fewer labels (1%, 5%), a model without the shortcut features, bootstrap confidence intervals |
| `src/` | `xai_tools.py` and `brbes.py` (from the course labs) and their tests |
| `tools/` | `assemble.py`, `feature_glossary.py` |
| `results/tables/`, `results/figures/` | Every table and figure, named after the step that made it |
| `models/` | Saved models and slow results (see [Run time](#run-time)) |
| `reference/` | Earlier course labs used as models for structure and code |
| `report/` | Report source and the scripts that build the PDF and Word versions |
| `requirements.txt` | Pinned library versions |
