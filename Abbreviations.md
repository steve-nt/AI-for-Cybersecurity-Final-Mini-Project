# Abbreviations and short names used in this project

Every abbreviation that appears in the notebook, the report, the README, the presentation and the guides,
with what it stands for and what it means here. For the ideas behind them, see
[Plain-English-Guide.md](Plain-English-Guide.md).

## 1. Course, project and data

| Short | Stands for | What it means here |
|---|---|---|
| **AI** | Artificial intelligence | The course subject; also "Use of AI" (our statement on using Claude) |
| **D7084E / D7041E** | Course codes | The two LTU course codes under which AI for Cybersecurity is given |
| **LTU** | Luleå University of Technology | Our university (the e-mail addresses end in `ltu.se`) |
| **UNSW** | University of New South Wales | The Australian university (UNSW Canberra) that recorded the traffic |
| **NB15** | Part of the dataset name | The 15 stands for 2015, the year UNSW-NB15 was recorded |
| **CIC** | Canadian Institute for Cybersecurity | The institute that turned UNSW-NB15 into flows with 76 features: **CIC-UNSW-NB15**, our dataset |
| **CICFlowMeter** | CIC flow meter | The tool that turns raw packets into flows and computes the features |
| **CICIDS2017** | CIC intrusion detection dataset, 2017 | Another dataset with the same kind of features (named in the README for comparison) |
| **NSL-KDD, CIC-IoT2023, Bot-IoT, CIC-DDoS2019** | Other datasets | Datasets the brief suggested; we did not use them |
| **CSV** | Comma-separated values | The file format of the data (`Data.csv`, `Label.csv`) and of our result tables |
| **IP** | Internet Protocol | An IP address identifies a computer; the reason we did not use `CICFlowMeter_out.csv` |

## 2. Security and networking

| Short | Stands for | What it means here |
|---|---|---|
| **SOC** | Security Operations Centre | The team that watches alerts; its analysts are the users of our detector |
| **NIDS** | Network intrusion detection system | What we built: a program that flags attacks in network traffic |
| **DoS** | Denial of service | An attack type in the data: flooding a service so it stops working |
| **DDoS** | Distributed denial of service | A DoS from many machines at once (in a dataset name only) |
| **TCP** | Transmission Control Protocol | The protocol most flows use; the shortcut features are TCP settings |
| **NAT** | Network address translation | A router that rewrites addresses, and sometimes TCP settings; one reason the shortcut would fail elsewhere |
| **IoT** | Internet of Things | Smart devices (only in dataset names) |
| **SMS** | Short Message Service | Text messages (only in the brief's dataset list) |

The attack types are written out in full: Exploits, Fuzzers, Reconnaissance, Generic, DoS, Shellcode,
Backdoor, Analysis, Worms.

## 3. Short words inside the feature names

The 67 features are named by CICFlowMeter. Their names are built from these short words. The full
meaning of every feature is in `results/tables/T4_feature_glossary.csv`.

| Short | Stands for | What it means |
|---|---|---|
| **Fwd / FWD** | Forward | Sent by the computer that opened the connection (the client, or the attacker) |
| **Bwd** | Backward | Sent back by the other computer (the server, or the victim) |
| **IAT** | Inter-arrival time | Time between two packets (in microseconds) |
| **Init Win Bytes** | Initial window bytes | The TCP window size announced at the start: how much data the computer will accept before it must acknowledge |
| **Seg Size Min** | Minimum segment size | The smallest TCP segment seen; `Fwd Seg Size Min` is the number one shortcut feature |
| **Pkts** | Packets | As in `Fwd Act Data Pkts` (forward packets that carry actual data) |
| **Act** | Actual | See above |
| **Std** | Standard deviation | How much a value varies within the flow |
| **Avg** | Average | Mean value |
| **/s** | Per second | Rates, such as `Bwd Packets/s` |
| **Down/Up Ratio** | Download/upload ratio | Data received divided by data sent |
| **Bulk** | Bulk transfer | Runs of many packets sent in a row without waiting |
| **Subflow** | Sub-flow | A part of a flow, split at idle gaps |
| **Active / Idle** | Active and idle time | How long the flow was busy, and how long it was quiet |

TCP flag names, counted in features such as `RST Flag Count`:

| Short | Stands for | What the flag does |
|---|---|---|
| **SYN** | Synchronise | Opens a connection |
| **ACK** | Acknowledge | Confirms that data arrived |
| **FIN** | Finish | Closes a connection politely |
| **RST** | Reset | Aborts a connection abruptly (common in scans) |
| **PSH** | Push | Asks the receiver to pass the data on at once |

## 4. Scores and statistics

| Short | Stands for | What it means here |
|---|---|---|
| **F1** | F1 score | Balances precision (how many alerts are real) and recall (how many attacks are caught), from 0 to 1 |
| **Macro-F1** | Macro-averaged F1 | The F1 of the benign class and of the attack class, averaged with equal weight; our main score |
| **FAR** | False alarm rate | The share of benign flows wrongly called attacks; lower is better |
| **PR-AUC** | Area under the precision-recall curve | How well the model ranks flows from "surely attack" to "surely benign", without a fixed threshold; 1 is perfect, the attack share (0.263) is chance level |
| **AUC** | Area under the curve | See PR-AUC |
| **TN, FP** | True negative, false positive | Boxes of the confusion matrix: benign called benign, benign called attack. FAR = FP / (FP + TN) |
| **R²** | R-squared, coefficient of determination | How well LIME's straight line fits the model; 1 is perfect, ours was 0.06 to 0.29 |
| **p** | Probability | The model's attack probability for a flow, as in "p = 0.9996" |
| **val** | Validation | In table headings, "val / test" |
| **±** | Plus or minus | The width of a confidence interval, as in "about ±0.002" |

## 5. Models and methods

| Short | Stands for | What it means here |
|---|---|---|
| **ML** | Machine learning | Programs that learn from examples |
| **HistGradientBoostingClassifier** | Histogram-based gradient boosting classifier | The scikit-learn class for our black box; it bins each feature into a histogram to train fast |
| **C** | Inverse regularisation strength | The setting of logistic regression we tuned (C = 10 won); larger C means a weaker penalty |
| **SHAP** | SHapley Additive exPlanations | Splits each prediction among the features as a fair share, from game theory (Shapley values) |
| **TreeExplainer / TreeSHAP** | SHAP for tree models | The exact, fast version of SHAP for trees; same answer every run |
| **LIME** | Local Interpretable Model-agnostic Explanations | Explains one prediction by nudging the flow and fitting a straight line to how the model reacts |
| **BRB** | Belief rule base | Our readable model: 9 if-then rules with beliefs over Low, Medium and High risk, plus Unknown |
| **RIMER** | Belief Rule-base Inference Methodology using the Evidential Reasoning approach | The method our BRB follows (Yang et al., 2006) |
| **ER** | Evidential reasoning | The way the BRB combines the beliefs of several rules into one |
| **Log-odds** | Logarithm of the odds | The scale SHAP uses for boosting; positive pushes towards attack, negative towards benign |
| **Seed** | Random seed | The number (42) that fixes all randomness so every run gives the same numbers |

## 6. Step names in the notebook

Every cell of the notebook starts with the step it belongs to (`# STEP C2`). The letter is the part of
the brief; **X** is an additional check; a **T** at the end means "the test half of a step whose setting
was chosen earlier".

| Step | What it does |
|---|---|
| **A0** | Setup: libraries, folders and the scores we report |
| **A1** | The security problem |
| **A2** | Load and clean the data |
| **A3** | Split 60/20/20; the test set is sealed at the end of this step |
| **A4** | The trivial baseline (always benign) on validation |
| **B1** | Glass boxes: decision tree and logistic regression |
| **B2** | Black box: gradient boosting |
| **C1** | Keep 10% of the labels |
| **C2** | Pseudo-labelling |
| **C3** | Did the unlabelled data help? |
| **X2** | Additional check: the pseudo-label cutoffs for 1%, 5% and 10% of the labels |
| **D1** | Global explanation with SHAP (on validation) |
| **F1, F2** | Choosing and building the BRB |
| **F3** | Choosing the fair comparison (a small tree on the BRB's features) |
| **T0** | "Final evaluation on the test set": the test set is opened |
| **A4T** | The trivial baseline on the test set |
| **B3** | Test scores of all models next to the baseline |
| **B4** | Where the models go wrong |
| **C4** | The results table on the test set |
| **D2 to D6** | Three flows to explain; SHAP and LIME on them; the deletion test; LIME's stability; why SHAP and LIME disagree |
| **E1 to E4** | Noise; missing features; what broke first and the trust rule; what an attacker could change |
| **F3T** | The fair comparison of the BRB on the test set |
| **F4, F5** | The BRB's belief output for one flow, step by step; what the BRB gives and costs |
| **G1 to G4** | Hiding Fuzzers; what it costs; adapting with a few labels; what we would do |
| **X2T** | Additional check: fewer labels (1% and 5%) on the test set |
| **X3** | Additional check: a constrained evasion attack |
| **X4** | Additional check: the learning curve for the hidden attack |
| **X6** | Additional check: boosting without the attacker fingerprint features |
| **X7** | Additional check: the BRB with missing inputs, and an expert who edits a rule |
| **X9** | Additional check: bootstrap confidence intervals for the test scores |

There are no steps X1, X5 or X8 in the notebook. **STANDIN** marks cells in a part notebook that only
stand in for another part during development; the assembler leaves them out.

## 7. Files, tools and formats

| Short | Stands for | What it means here |
|---|---|---|
| **README** | "Read me" | The file that explains the dataset, the libraries and how to run |
| **.ipynb** | IPython notebook | A Jupyter notebook file |
| **.md** | Markdown | Plain text files with light formatting, like this one |
| **PDF** | Portable Document Format | The report as handed in |
| **.docx** | Word document | The report's Word version, exported to PDF |
| **PPTX** | PowerPoint file | The slide deck |
| **sklearn** | scikit-learn | The machine learning library (version 1.6.1) |
| **uv** | (a name, not an abbreviation) | A fast Python package installer used in the setup |
| **venv / .venv** | Virtual environment | A private folder of Python libraries for this project |
| **nbconvert** | Notebook convert | The Jupyter tool that runs the notebook from the command line |
| **joblib** | (library name) | Saves and loads the trained models in `models/` |
| **SHA-256** | Secure Hash Algorithm, 256 bits | A fingerprint of a file; the README lists them so you can check the downloaded data |
| **RAM** | Random-access memory | Computer memory (the run time is measured with 19 GB) |
| **MB, GB** | Megabyte, gigabyte | File sizes |
| **ms** | Millisecond | One thousandth of a second |
| **CHANGELOG** | Change log | The history of every change to the project |
| **noqa: E402** | "No quality assurance", error code E402 | A code comment telling the style checker that an import below the top of the file is intentional |

## 8. Reference venues

| Short | Stands for |
|---|---|
| **PST** | Annual International Conference on Privacy, Security and Trust |
| **MilCIS** | Military Communications and Information Systems Conference |
| **NeurIPS** | Conference on Neural Information Processing Systems |
| **ICML** | International Conference on Machine Learning |
| **KDD, SIGKDD** | Knowledge Discovery and Data Mining; the ACM Special Interest Group on it |
| **ACM** | Association for Computing Machinery |
| **IEEE** | Institute of Electrical and Electronics Engineers |
| **USENIX** | The Advanced Computing Systems Association (organiser of the USENIX Security Symposium) |

## 9. Presentation day

| Short | Stands for | What it means here |
|---|---|---|
| **USB** | Universal Serial Bus | The USB stick with the slides and the backup video |
| **HDMI** | High-Definition Multimedia Interface | The cable to the projector |
| **OBS** | Open Broadcaster Software | A screen recorder, for the backup video |
| **GNOME** | (desktop name) | The Linux desktop; its screenshot tool can also record the screen |
