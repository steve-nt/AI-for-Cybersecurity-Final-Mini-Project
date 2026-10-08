# Dataset choice: UNSW-NB15

**We use UNSW-NB15.** Of the two datasets we have (UNSW-NB15 and CIC-DDoS2019), it is faster to build with and easier to explain, and it covers every part of the brief, including the parts needed for grade 5.

## What is in the folders

| | **UNSW-NB15** | **CIC-DDoS2019** |
|---|---|---|
| Size | `Data.csv` is 188 MB (plus a 1.8 GB `CICFlowMeter_out.csv` we don't need) | 29 GB unzipped, across 18 CSVs, some over 2 GB each (`TFTP.csv` is 9.3 GB) |
| Rows | 447,915 flows | Tens of millions |
| Features | 76 numeric columns, with no IPs, ports or timestamps | 88 columns, including `Unnamed: 0`, Flow ID, IPs and timestamps; column names start with spaces |
| Labels | Separate `Label.csv`, 10 classes (0 = Benign) | A text label in the last column of each file |
| Class balance | 80% benign, 20% attacks | Almost all attack: `Portmap.csv` has 4,734 benign vs 186,960 attack rows |

**UNSW-NB15 label counts** (codes from `UNSW-NB15/Readme.txt`):

| Code | Class | Rows |
|---|---|---|
| 0 | Benign | 358,332 |
| 1 | Analysis | 385 |
| 2 | Backdoor | 452 |
| 3 | DoS | 4,467 |
| 4 | Exploits | 30,951 |
| 5 | Fuzzers | 29,613 |
| 6 | Generic | 4,632 |
| 7 | Reconnaissance | 16,735 |
| 8 | Shellcode | 2,102 |
| 9 | Worms | 246 |

## Why UNSW-NB15

- **Fast.** Load `Data.csv` and `Label.csv` side by side (they have the same 447,915 rows), set `attack = Label != 0`, and take a 5,000-row stratified sample. Every column is already numeric, so there are no text columns to encode.
- **Easy to explain.** The attack types are clearly different from each other: scanning, exploits, backdoors, worms. That makes the SHAP discussion and Part G easy to tell as a story. CIC-DDoS2019 is mostly reflection floods (DNS, LDAP, NTP, SSDP and so on) that look almost the same in flow statistics.
- **Sensible baseline.** "Always predict benign" gives 80% accuracy and 0 attack recall, which is a clear comparison point. In CIC-DDoS2019 the majority class is *attack*, so the trivial baseline already gets about 98% accuracy and 100% recall, which makes Part A confusing.
- **Part G works well.** Hide **Reconnaissance** (16,735 rows) or **DoS** (4,467). Avoid Worms, Analysis and Backdoor, which are too small to give 50–100 labelled rows for the adaptation step plus some left over for testing. If we hide Reconnaissance, take more of it in the sample than a plain stratified sample would give. At its natural 3.7% share, 5,000 rows would contain only about 190 Reconnaissance rows.
- **Part F is straightforward.** The features are numeric flow statistics (packet lengths, flow duration, flag counts, window sizes), so the top two SHAP features give a simple 3×3 BRB with nine rules.

## Things to watch

1. **Use `Data.csv`, not `CICFlowMeter_out.csv`.** The first row of each holds the same numbers. The big file just adds Flow ID, IPs, ports and timestamp. IP addresses would leak the answer: in UNSW-NB15 the attackers are on the `175.45.176.x` hosts.
2. **This isn't the original UNSW-NB15 feature set.** The original has 49 features (`sbytes`, `sttl` and so on). This copy was rebuilt from the original pcaps with CICFlowMeter, so its features are the same kind as CICIDS. The report should say exactly which version we used. Don't describe it with the brief's line about "a different feature set from CICIDS", because that doesn't apply to this copy.
3. **Clean infinite values.** `Flow Bytes/s` and `Flow Packets/s` can be `inf` or empty. Replace them with NaN, then fill with the training median, which takes a couple of lines. The file hasn't been scanned for these yet, so treat this as likely rather than confirmed.
4. **Say that we subsampled.** The brief allows 4,000–5,000 rows as long as it has a mix of attack and normal traffic. The report and README should state the sample size, how it was drawn and the random seed.

## Why not CIC-DDoS2019

- About 29 GB unzipped across 18 files, so even drawing a sample means reading multi-GB files.
- Benign traffic is only a few per cent, so the trivial baseline is misleading and the class balance is the opposite of a normal network.
- The attack types are similar reflection floods, which makes the explanation and adaptability parts harder to interpret.
- It needs more cleaning: an index column, identifier columns (Flow ID, IPs, timestamp) that must be dropped, and column names with leading spaces.

The CIC-DDoS2019 folder is not needed for the project.
