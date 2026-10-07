# Dataset choice: the easiest option

**NSL-KDD is the easiest option.** It also covers every part of the brief, including the parts needed for grade 5.

## Why NSL-KDD

- **Small and clean.** It comes as ready-made CSVs (KDDTrain+ is about 125k rows, 41 features) with no gigabyte downloads and very little cleaning. The brief lets you use 4,000–5,000 rows, so the whole notebook will run well inside the 5-minute limit.
- **Tabular, like the labs.** The tree and forest models, SHAP, LIME, the deletion test, Gaussian noise and median replacement all work as they did in class.
- **Part G works directly.** Each row is labelled with a specific attack (neptune, smurf, satan, portsweep and so on), and these group into four categories: DoS, Probe, R2L and U2R. You can hide one type without needing the "time split" fallback.
- **Part F is easy.** The top features are usually `src_bytes`, `dst_bytes`, `same_srv_rate` or `flag`. These are numeric and easy for a security person to read, so a 3×3 BRB with nine rules is simple to build.

## The catches

- **It is old (1999 traffic).** The brief says you must say so in the report. Make that part of your "which numbers do I least trust" discussion.
- **Three text columns** (`protocol_type`, `service`, `flag`) need one-hot or label encoding. That's a few lines of code.
- **Part G needs enough rows of the hidden attack.** In a 5,000-row sample, hide **Probe** (or a large single attack like `satan`/`portsweep`). Don't hide U2R or R2L, which are too rare to give you 50–100 labelled rows for the adaptation step plus some left over for testing. Make sure your subsample keeps enough of whichever attack you hide.

## Why not the others

- **SMS spam** looks simple but is harder here. It has only ham/spam labels, so Part G falls back to an index split. Noise, missing features and the BRB also make little sense on text features.
- **UNSW-NB15** is a good second choice: 9 attack categories and provided train/test files. It needs a bit more cleaning and has more features.
- **CIC-DDoS2019 and CIC-IoT2023** are multi-GB downloads with heavy cleaning, so they're not the easy route.

One exception: if your group's seminar paper used a manageable tabular dataset, reusing it may be just as easy, since you already know the problem.
