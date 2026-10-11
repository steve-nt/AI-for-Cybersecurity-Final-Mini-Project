# Files to submit

**Deadline: Thursday 15 October 2026, 08:00, on Canvas.** Aim for the evening of Wednesday 14 October.

The brief (section 4, "What to hand in") asks for: one notebook that runs from top to bottom, a short
README (dataset, where to get it, libraries, how to run), and a report of 6 to 8 pages with the eight
headings. So Canvas gets **two uploads**: a code zip and the report as PDF.

## 1. The report (PDF)

| File | Where it comes from |
|---|---|
| `report/Mini_Project_Report.pdf` | Open `report/Mini_Project_Report.docx` in Word and save as PDF |

Before exporting:

- [ ] The two who-did-what sentences in section 8 are confirmed by both members ("Each member made the
      additional checks for their own parts." and "Both chose the dataset and wrote the notebook, the
      README and this report together."). If changed, edit `report/Mini_Project_Report.md`, then rebuild
      the Word file with `python report/build_docx.py` and run `python tools/check_report_numbers.py`.
- [ ] Title page: both names and e-mail addresses, Group 6.
- [ ] Length: 6 to 8 pages (the title page not counted). Figures and tables readable, all captioned.

## 2. The code (zip)

**`AI-for-Cybersecurity-Final-Mini-Project.zip`**, built from the project root (about 23 MB, 223 files):

```bash
zip -rq -9 AI-for-Cybersecurity-Final-Mini-Project.zip mini_project_unsw_nb15.ipynb README.md requirements.txt src tools parts results models -x '*/__pycache__/*' '*/.pytest_cache/*' '*.ipynb_checkpoints*'
```

| Path | Why it is in the zip |
|---|---|
| `mini_project_unsw_nb15.ipynb` | **The hand-in notebook.** Parts A to G, then the additional checks the report quotes; runs top to bottom in about 4 minutes with `models/` |
| `README.md` | Required: the dataset, where to get it, the libraries, how to run |
| `requirements.txt` | The libraries with pinned versions |
| `src/` | Needed by the notebook: `xai_tools.py` (Part D) and `brbes.py` (Part F), with their tests |
| `results/` | Needed by the notebook: `results/tables/T4_feature_glossary.csv`. Also every result table and figure the report refers to |
| `models/` | The saved models and slow results. Without them the run takes about 25 minutes or more instead of about 4, over the brief's 5-minute limit |
| `tools/` | `assemble.py` (builds the notebook from `parts/`), `check_report_numbers.py` (checks the report against the tables), `feature_glossary.py` |
| `parts/` | The part notebooks the hand-in notebook is assembled from; the README describes them |

### Not in the zip

| Leave out | Why |
|---|---|
| `UNSW-NB15/` (the data) | 188 MB; the README says where to download it and gives the SHA-256 hashes |
| `.venv/`, `__pycache__/`, `.ipynb_checkpoints/` | Environment and caches; `requirements.txt` recreates the environment |
| `presentation/`, `AutoPenBench_Seminar.pptx`, `presentation/backup_run.mp4` | For the talk, not part of the hand-in |
| `report/` sources (Markdown, build scripts, fonts) | The report goes in as the PDF upload |
| `TASKLIST.md`, `CHANGELOG.md`, `Dataset_Choice.md` | Internal planning and history |
| `reference/`, `PreviousLabs/`, the brief (`15_oct_Final Mini Project.*`) | Course material, not our work |

## 3. Checks before uploading

- [ ] `git status` is clean, so the zip matches the last commit.
- [ ] The notebook in the zip is the executed one with outputs (it is in git with outputs; do not save
      it after a live demo cell).
- [ ] Unzip into a new empty folder, copy the data into `UNSW-NB15/` there, create a fresh environment
      from `requirements.txt`, and run the notebook top to bottom: no errors, under 5 minutes.
- [ ] The PDF opens, has the eight headings in order, the Use of AI statement and the references.

## 4. On Canvas

- [ ] Upload `AI-for-Cybersecurity-Final-Mini-Project.zip` and `Mini_Project_Report.pdf` (one member uploads for the
      group, unless Canvas asks each member to).
- [ ] Download both files again from Canvas and check that the zip opens and the PDF is the final one.
- [ ] Before 15 October, 08:00.
