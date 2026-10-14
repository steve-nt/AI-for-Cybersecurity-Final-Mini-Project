# Live demo: running the notebook during the talk

The brief: "Run your code during the presentation or show a demo of it running. A slide showing results
you obtained earlier is not enough. If a full run is too slow, run a reduced version live, or play a
recording of the real run and say which it is." A talk without a run or a demo is an F.

**The plan:** run the full hand-in notebook, `mini_project_unsw_nb15.ipynb`, on all 305,105 flows, live.
Press *Restart Kernel and Run All* at the start of the talk; it finishes in about 4 minutes while the
slides go on. Show it twice: the test scores on slide 4, and one extra cell on slide 14. A screen
recording of a real run is the backup.

## What to say about the saved models

Kirill says it once, on slide 1, so nobody thinks results are being replayed:

> "The trained models and the slowest sweeps load from a saved cache, because training everything from
> scratch takes about 25 minutes. Everything else, the cleaning, the split, the scores, the tables and
> the figures, is computed now."

This is true: the cache (`models/`) is keyed on the feature list, the split sizes, the seed and the
scikit-learn version, and a run without it gives the same numbers (`random_state=42` everywhere).

## Measured run times

| Run | Machine | Time |
|---|---|---|
| Hand-in notebook, current version with the additional checks at the end (11 Oct, evening, quiet machine) | 8 cores, 19 GB RAM | 240 s |
| Earlier version without the additional checks, quiet machine | same | 107 s and 116 s |
| Earlier version, other programs busy | same | 239 s and 245 s |
| Earlier version plus the demo cell (11 Oct, afternoon) | same | 142 s |
| Without `models/` (full retraining) | same | about 25 minutes for Parts A to G, more with the additional checks |

So close everything else before the talk (browser tabs, IDE indexing, other notebooks): a busy laptop
doubles the run time. The additional checks add about 60 s at the end of the run. The test set is
opened (step T0) and the test table of Part B appears about 95 s into the run, in time for slide 4, and even on a busy laptop the run finishes well before
slide 14 (at about 10:45).

## The day before (Wednesday 14 October)

- [ ] Laptop charged, charger packed. Check the video output (HDMI or USB-C adapter) on a projector or a second screen.
- [ ] Turn off notifications, automatic updates and the screen lock for the afternoon.
- [ ] Check the data and the environment, from the project root:
  ```bash
  source .venv/bin/activate
  sha256sum UNSW-NB15/Data.csv UNSW-NB15/Label.csv    # must match the README
  ls models/*/ | wc -l                               # about 100 files
  python -m pytest src                               # 16 passed
  ```
- [ ] One full rehearsal run in Jupyter exactly as in the talk (below), timed. Note the time here: ______
- [ ] Record the backup video (below) and play it back once to check it has sound off, is sharp, and is complete.
- [ ] Copy the backup video and the slides (PPTX and a PDF export) to a USB stick as well.

## Setting up before the talk (15 minutes before)

1. Close every other program. Plug in the charger.
2. Start Jupyter from the project root: `source .venv/bin/activate` then `jupyter lab`.
3. Open `mini_project_unsw_nb15.ipynb`. Run *Kernel > Restart Kernel and Clear Outputs of All Cells*,
   so the audience sees empty cells being filled (the proof that it runs now). Do **not** save afterwards;
   the handed-in file keeps its outputs.
4. Zoom the notebook to about 150% (`Ctrl` and `+`) so tables can be read from the back.
5. In the table of contents (left sidebar), the headings "Final evaluation on the test set" (with "Part
   B: scores on the test set, next to the trivial baseline" just below it) and "Part G: what we would
   do" are the places to jump to.
6. Open the slides in presenter view on the other window. Practise the window switch (`Alt+Tab`) once.
7. Have the demo cell (below) ready to paste: open `presentation/demo.md` in a text editor, or keep the
   code in the clipboard.

## During the talk

The person who is not speaking drives the laptop (slides and notebook), except on slide 14.

| Clock | Slide | Action |
|---|---|---|
| 0:00 | 1 | Stefanos (not speaking) switches to Jupyter and presses *Run > Run All Cells* (the kernel is fresh) while Kirill says so, then switches back to the slides. |
| about 2:40 | 4 | Kirill talks; Stefanos switches to Jupyter. Jump to "Final evaluation on the test set": Kirill says that every setting was chosen before this point, on validation, then points at the test table just below (gradient boosting 0.9718) and at the `[*]` running further down. Switch back; Stefanos takes over. |
| about 10:45 | 14 | Stefanos talks and also drives the laptop on this slide, to paste and run the cell. Switch to Jupyter. Scroll to the end: the last cells have numbers and the G3 figure. Add a cell at the very end, paste the demo cell, run it with `Shift+Enter`. Switch back; Kirill closes. |

### The demo cell (slide 14)

Paste this into a new cell at the end of the notebook, after the run has finished:

```python
# Live demo: the test attack the model is most sure about, before and after copying a benign machine's TCP settings
flow = X_test.iloc[[CASES["detection"]]].copy()
print("Attack type:", type_test.iloc[CASES["detection"]])
print(f"Attack probability, as recorded:       {boost.predict_proba(flow)[0, 1]:.4f}")
flow["Fwd Seg Size Min"] = 32                  # the most common value among benign training flows
print(f"After changing Fwd Seg Size Min to 32: {boost.predict_proba(flow)[0, 1]:.4f}")
flow["FWD Init Win Bytes"] = 5792              # and the most common benign TCP window
print(f"And FWD Init Win Bytes to 5792:        {boost.predict_proba(flow)[0, 1]:.4f}")
```

Expected output (checked on 11 October on a real run of the hand-in notebook):

```
Attack type: Exploits
Attack probability, as recorded:       0.9996
After changing Fwd Seg Size Min to 32: 0.0032
And FWD Init Win Bytes to 5792:        0.0000
```

What it shows: the same shortcut as slides 6 to 10, on one flow, live. The flow is the "detection" case
of Part D (an Exploits attack, probability 0.9996), and 32 and 5792 are the TCP settings most common
among benign training flows (Part E).

After the talk, close the notebook **without saving**, so the demo cell does not end up in the hand-in.

## If something goes wrong

| Problem | What to do |
|---|---|
| At slide 4 the run has not reached the final evaluation yet | Show the `[*]` on the cell that is running and the filled cells above it, say "it is still choosing settings on validation", and go on. Show the test table on slide 14 instead. |
| At slide 14 the run is still going | Show where it is (the `[*]`) and say how far it got. A new cell would only wait in the queue behind the run, so paste the demo cell anyway and let it run when the run ends, during the questions. If there is no time, play the demo cell part of the backup video and say it is a recording. |
| An error stops the run | Do not debug in front of the audience. Say "the live run stopped here; this is a recording of a full real run from Wednesday", and play the backup video from the right point. |
| The laptop or the projector fails | Play the backup video from the USB stick on the room computer, and say it is a recording. |
| Jupyter does not start | Run it from the terminal instead, where the progress is visible: `jupyter nbconvert --to notebook --execute --output /tmp/live_run.ipynb mini_project_unsw_nb15.ipynb`, and show the finished file. |

## The backup recording

Record one full, real run with the demo cell at the end, exactly as in the talk, on Wednesday.

- **Tool:** OBS Studio, or the GNOME screenshot tool (`Print`, then the camera icon, then select the
  window). Check that the recording does not stop by itself after 30 seconds (the old GNOME shortcut
  `Ctrl+Shift+Alt+R` does).
- **Content:** restart and clear outputs, Run All, scroll along as cells fill, show the test table, wait
  for the end, paste and run the demo cell. About 3 to 4 minutes.
- **File:** `presentation/backup_run.mp4`, plus a copy on the USB stick. It is a large file; leave it out
  of git and of the Canvas zip.
- **In the talk:** if it is used, say clearly "this is a recording of a full real run from 14 October".
  The brief allows that, but only if you say which it is.
