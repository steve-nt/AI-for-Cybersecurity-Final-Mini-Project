"""Build the feature glossary: what each CIC-UNSW-NB15 feature means, in plain words (task T4).

The meanings are written by hand below (from the CICFlowMeter feature documentation). Everything
else is measured on the training split, so it always matches the data:
  - direction (forward / backward / both) and unit,
  - distinct values, minimum, median and maximum in the training set,
  - the "twin" group: features linked by |correlation| > 0.95, directly or through a chain.

The data are cleaned and split exactly as in parts/00_setup.ipynb (duplicates and conflicting rows
removed, stratified 60/20/20 split, seed 42, columns constant in training dropped), so the glossary
describes the same 67 features the models see.

The group column is only a *proposal* (Free / Costly / Fixed: how easily an attacker could change the
feature), used as the starting point of step E4.

Writes results/tables/T4_feature_glossary.csv and results/tables/T4_feature_glossary.md.

Usage (from the project root, environment active):
    python tools/feature_glossary.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "UNSW-NB15"
OUT_CSV = ROOT / "results" / "tables" / "T4_feature_glossary.csv"
OUT_MD = ROOT / "results" / "tables" / "T4_feature_glossary.md"
SEED = 42
TWIN_THRESHOLD = 0.95

US = "microseconds"
# name: (unit, plain-language meaning). "Initiator" = the side that opened the conversation (for an
# attack: the attacker); "responder" = the other side.
MEANING = {
    "Flow Duration": (US, "How long the whole conversation lasted, first packet to last"),
    "Total Fwd Packet": ("packets", "Number of packets the initiator (client/attacker) sent"),
    "Total Bwd packets": ("packets", "Number of packets the responder (server/victim) sent back"),
    "Total Length of Fwd Packet": ("bytes", "Total payload bytes the initiator sent"),
    "Total Length of Bwd Packet": ("bytes", "Total payload bytes the responder sent back"),
    "Fwd Packet Length Max": ("bytes", "Largest packet payload the initiator sent"),
    "Fwd Packet Length Min": ("bytes", "Smallest packet payload the initiator sent"),
    "Fwd Packet Length Mean": ("bytes", "Average packet payload the initiator sent"),
    "Fwd Packet Length Std": ("bytes", "How much the initiator's packet sizes vary"),
    "Bwd Packet Length Max": ("bytes", "Largest packet payload the responder sent"),
    "Bwd Packet Length Min": ("bytes", "Smallest packet payload the responder sent"),
    "Bwd Packet Length Mean": ("bytes", "Average packet payload the responder sent"),
    "Bwd Packet Length Std": ("bytes", "How much the responder's packet sizes vary"),
    "Flow Bytes/s": ("bytes per second", "Data rate of the whole conversation (bytes / duration)"),
    "Flow Packets/s": ("packets per second", "Packet rate of the whole conversation (packets / duration)"),
    "Flow IAT Mean": (US, "Average gap between two consecutive packets, either direction"),
    "Flow IAT Std": (US, "How much the gaps between packets vary"),
    "Flow IAT Max": (US, "Longest gap between two consecutive packets"),
    "Flow IAT Min": (US, "Shortest gap between two consecutive packets"),
    "Fwd IAT Total": (US, "Sum of the gaps between the initiator's packets"),
    "Fwd IAT Mean": (US, "Average gap between two packets of the initiator"),
    "Fwd IAT Std": (US, "How much the gaps between the initiator's packets vary"),
    "Fwd IAT Max": (US, "Longest gap between two packets of the initiator"),
    "Fwd IAT Min": (US, "Shortest gap between two packets of the initiator"),
    "Bwd IAT Total": (US, "Sum of the gaps between the responder's packets"),
    "Bwd IAT Mean": (US, "Average gap between two packets of the responder"),
    "Bwd IAT Std": (US, "How much the gaps between the responder's packets vary"),
    "Bwd IAT Max": (US, "Longest gap between two packets of the responder"),
    "Bwd IAT Min": (US, "Shortest gap between two packets of the responder"),
    "Fwd PSH Flags": ("0/1", "Whether the initiator set the PSH flag (\"deliver this data now\")"),
    "Bwd PSH Flags": ("0/1", "Whether the responder set the PSH flag"),
    "Fwd URG Flags": ("0/1", "Whether the initiator set the URG flag (\"urgent data\"); almost never used"),
    "Bwd URG Flags": ("0/1", "Whether the responder set the URG flag"),
    "Fwd Header Length": ("bytes", "Total header bytes of the initiator's packets"),
    "Bwd Header Length": ("bytes", "Total header bytes of the responder's packets"),
    "Fwd Packets/s": ("packets per second", "How fast the initiator sent packets"),
    "Bwd Packets/s": ("packets per second", "How fast the responder sent packets"),
    "Packet Length Min": ("bytes", "Smallest packet payload in the conversation, either direction"),
    "Packet Length Max": ("bytes", "Largest packet payload in the conversation, either direction"),
    "Packet Length Mean": ("bytes", "Average packet payload, both directions together"),
    "Packet Length Std": ("bytes", "How much packet sizes vary, both directions together"),
    "Packet Length Variance": ("bytes squared", "Packet Length Std squared (same information)"),
    "FIN Flag Count": ("packets", "Packets with the FIN flag (\"I am finished, close the connection\")"),
    "SYN Flag Count": ("packets", "Packets with the SYN flag (\"let us start a connection\")"),
    "RST Flag Count": ("packets", "Packets with the RST flag (\"abort the connection\"); 0 or 1 in our data"),
    "PSH Flag Count": ("packets", "Packets with the PSH flag (\"deliver this data now\")"),
    "ACK Flag Count": ("packets", "Packets with the ACK flag (\"I received your data\")"),
    "URG Flag Count": ("packets", "Packets with the URG flag (\"urgent data\")"),
    "CWR Flag Count": ("packets", "Packets with the CWR flag (congestion window reduced)"),
    "ECE Flag Count": ("packets", "Packets with the ECE flag (network congestion warning)"),
    "Down/Up Ratio": ("ratio", "Responder packets divided by initiator packets (download vs. upload)"),
    "Average Packet Size": ("bytes", "Average packet size over the conversation"),
    "Fwd Segment Size Avg": ("bytes", "Average data per initiator packet (practically Fwd Packet Length Mean)"),
    "Bwd Segment Size Avg": ("bytes", "Average data per responder packet (practically Bwd Packet Length Mean)"),
    "Fwd Bytes/Bulk Avg": ("bytes", "Average bytes in a bulk transfer (a burst of data) from the initiator"),
    "Fwd Packet/Bulk Avg": ("packets", "Average packets in a bulk transfer from the initiator"),
    "Fwd Bulk Rate Avg": ("bytes per second", "Average speed of the initiator's bulk transfers"),
    "Bwd Bytes/Bulk Avg": ("bytes", "Average bytes in a bulk transfer (a burst of data) from the responder"),
    "Bwd Packet/Bulk Avg": ("packets", "Average packets in a bulk transfer from the responder"),
    "Bwd Bulk Rate Avg": ("bytes per second", "Average speed of the responder's bulk transfers"),
    "Subflow Fwd Packets": ("packets", "Initiator packets per sub-conversation (bursts split by idle time)"),
    "Subflow Fwd Bytes": ("bytes", "Initiator bytes per sub-conversation"),
    "Subflow Bwd Packets": ("packets", "Responder packets per sub-conversation"),
    "Subflow Bwd Bytes": ("bytes", "Responder bytes per sub-conversation"),
    "FWD Init Win Bytes": ("bytes", "TCP window size in the initiator's first packet: how much data it accepts "
                                    "at once. Set by the initiator's operating system (0 = not TCP or not "
                                    "recorded)"),
    "Bwd Init Win Bytes": ("bytes", "TCP window size in the responder's first packet, set by the responder's "
                                    "operating system (0 = not TCP or not recorded)"),
    "Fwd Act Data Pkts": ("packets", "Initiator packets that carried at least 1 byte of data"),
    "Fwd Seg Size Min": ("bytes", "Smallest header size seen in the initiator's packets; depends on the "
                                  "initiator's operating system and TCP options"),
    "Active Mean": (US, "Average length of a busy period (packets flowing) before the flow went quiet"),
    "Active Std": (US, "How much the busy periods vary"),
    "Active Max": (US, "Longest busy period"),
    "Active Min": (US, "Shortest busy period"),
    "Idle Mean": (US, "Average length of a quiet period between busy periods"),
    "Idle Std": (US, "How much the quiet periods vary"),
    "Idle Max": (US, "Longest quiet period"),
    "Idle Min": (US, "Shortest quiet period"),
}

# Features describing the TCP settings of a machine (its "fingerprint"), not the attack itself.
TCP_SETTINGS = {
    "FWD Init Win Bytes": "TCP setting of the initiator's machine: identifies the machine, not the attack. "
                          "An attacker can change it on their own machine",
    "Bwd Init Win Bytes": "TCP setting of the responder's machine (the victim): the attacker cannot change it",
    "Fwd Seg Size Min": "TCP setting of the initiator's machine: identifies the machine, not the attack. "
                        "An attacker can change it on their own machine",
}

COSTLY = {"Total Fwd Packet", "Total Length of Fwd Packet", "Subflow Fwd Packets", "Subflow Fwd Bytes",
          "Fwd Act Data Pkts", "Fwd Packet/Bulk Avg", "Fwd Bytes/Bulk Avg"}
FREE_SIZES = {"Fwd Header Length", "Fwd Segment Size Avg", "Fwd Seg Size Min", "FWD Init Win Bytes"}


def direction(name):
    lower = name.lower()
    if "bwd" in lower or "backward" in lower:
        return "backward"
    if "fwd" in lower or "forward" in lower:
        return "forward"
    return "both"


def proposed_group(name):
    """How easily the attacker could change the feature (a proposal; step E4 decides)."""
    if direction(name) == "backward" or "Flag" in name:
        return "Fixed"                     # produced by the victim, or by the network software
    if any(k in name for k in ("IAT", "Idle", "Active")) or name in ("Flow Duration", "Fwd Packets/s"):
        return "Free"                      # timing: the attacker can wait longer or send more slowly
    if name.startswith("Fwd Packet Length") or name in FREE_SIZES:
        return "Free"                      # forward sizes and the attacker's own TCP settings
    if name in COSTLY:
        return "Costly"                    # more forward packets or bytes: a louder attack
    return "Fixed"                         # mixes both directions or is derived: Fixed to be safe


def load_train():
    """The training part of the split, cleaned exactly as in parts/00_setup.ipynb."""
    X = pd.read_csv(DATA_DIR / "Data.csv")
    X = pd.DataFrame(X.to_numpy(dtype=float), columns=X.columns)
    labels = pd.read_csv(DATA_DIR / "Label.csv")["Label"]
    df = X.assign(attack_type=labels)
    df = df[~pd.util.hash_pandas_object(df, index=False).duplicated().to_numpy()]
    row_key = pd.util.hash_pandas_object(df[X.columns], index=False).to_numpy()
    df = df[~(df.groupby(row_key)["attack_type"].transform("nunique").to_numpy() > 1)]
    assert len(df) == 305_105, len(df)

    types = df["attack_type"]
    pos_rest, _ = train_test_split(np.arange(len(df)), test_size=0.20, stratify=types, random_state=SEED)
    pos_train, _ = train_test_split(pos_rest, test_size=0.25, stratify=types.iloc[pos_rest],
                                    random_state=SEED)
    X_train = df.iloc[pos_train][list(X.columns)]
    constant = [c for c in X_train.columns if X_train[c].min() == X_train[c].max()]
    X_train = X_train.drop(columns=constant)
    assert X_train.shape == (183_063, 67), X_train.shape
    return X_train


def twin_groups(X_train):
    """Group id per feature: connected components of the graph |corr| > TWIN_THRESHOLD."""
    corr = np.abs(np.corrcoef(X_train.to_numpy(dtype=float), rowvar=False))
    linked = corr > TWIN_THRESHOLD
    np.fill_diagonal(linked, False)
    _, labels = connected_components(linked, directed=False)
    labels = pd.Series(labels, index=X_train.columns)
    sizes = labels.map(labels.value_counts())
    # Number the real groups (2+ members) 1, 2, ... in column order; singletons get no group.
    order = {g: i + 1 for i, g in enumerate(dict.fromkeys(labels[sizes > 1]))}
    group = labels.map(order)
    members = {g: ", ".join(group.index[group == g]) for g in order.values()}
    return group, group.map(members)


def main():
    X_train = load_train()
    unknown = set(X_train.columns) - set(MEANING)
    assert not unknown, f"no meaning written for: {sorted(unknown)}"

    twin, twin_members = twin_groups(X_train)
    table = pd.DataFrame({
        "feature": X_train.columns,
        "meaning": [MEANING[c][1] for c in X_train.columns],
        "unit": [MEANING[c][0] for c in X_train.columns],
        "direction": [direction(c) for c in X_train.columns],
        "group_proposed": [proposed_group(c) for c in X_train.columns],
        "distinct_values": X_train.nunique().to_numpy(),
        "train_min": X_train.min().to_numpy(),
        "train_median": X_train.median().to_numpy(),
        "train_max": X_train.max().to_numpy(),
        "twin_group": twin.astype("Int64").to_numpy(),
        "twin_members": twin_members.fillna("").to_numpy(),
        "note": [TCP_SETTINGS.get(c, "") for c in X_train.columns],
    })
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_CSV, index=False)
    write_markdown(table)

    print(f"Wrote {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)} ({len(table)} features)")
    print("Proposed groups:", table.group_proposed.value_counts().to_dict())
    print("Direction:", table.direction.value_counts().to_dict())
    n_groups = table.twin_group.nunique()
    print(f"Twin groups (|corr| > {TWIN_THRESHOLD}): {n_groups}, covering "
          f"{int(table.twin_group.notna().sum())} features")


def fmt(x):
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:.3g}"


def write_markdown(table):
    lines = [
        "# Feature glossary (CIC-UNSW-NB15, 67 features)",
        "",
        "*Generated by `tools/feature_glossary.py` from the training split; do not edit by hand.*",
        "",
        "**Initiator** = the side that opened the conversation (for an attack: the attacker).",
        "**Responder** = the other side (for an attack: the victim). In the names, `Fwd` means sent by the",
        "initiator and `Bwd` sent by the responder. IAT = inter-arrival time, the gap between two packets.",
        "Times are in microseconds.",
        "",
        "The *proposed group* says how easily an attacker could change the feature: **Free** = cheaply",
        "(timing, own packet sizes, own TCP settings), **Costly** = with effort (more packets or bytes, a",
        "louder attack), **Fixed** = not at all (the victim's replies, flags set by the network software,",
        "features that mix both directions). Step E4 checks and finalises these groups.",
        "",
        "**TCP-settings (\"fingerprint\") features.** `FWD Init Win Bytes`, `Fwd Seg Size Min` and",
        "`Bwd Init Win Bytes` are set by each machine's operating system when the conversation starts.",
        "They describe *which machine* is talking, not *what it is doing*. In UNSW-NB15 all attacks come",
        "from a few attacker machines, so these features can identify the attacks without describing them",
        "(a shortcut).",
        "",
        "## All features",
        "",
        "| Feature | Meaning | Unit | Dir. | Proposed group | Train min / median / max | Distinct values | Twin group |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        twin = "" if pd.isna(r.twin_group) else str(int(r.twin_group))
        lines.append(f"| `{r.feature}` | {r.meaning} | {r.unit} | {r.direction} | {r.group_proposed} | "
                     f"{fmt(r.train_min)} / {fmt(r.train_median)} / {fmt(r.train_max)} | "
                     f"{r.distinct_values:,} | {twin} |")

    lines += ["", f"## Twin groups (|correlation| > {TWIN_THRESHOLD} on the training set)", "",
              "Features in one group carry almost the same information. SHAP and LIME may split the credit",
              "between twins differently (step D6), and removing one twin alone changes little because the",
              "others still carry the signal (step D4).", "",
              "| Group | Members | Proposed groups of the members |", "|---|---|---|"]
    groups = table.dropna(subset=["twin_group"]).drop_duplicates("twin_group")
    for r in groups.itertuples():
        groups_in = table.loc[table.twin_group == r.twin_group, "group_proposed"].unique()
        mixed = " (**mixed**: the attacker controls only part of it)" if len(groups_in) > 1 else ""
        lines.append(f"| {int(r.twin_group)} | {r.twin_members} | {', '.join(sorted(groups_in))}{mixed} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
