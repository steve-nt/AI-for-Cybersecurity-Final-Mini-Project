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
