"""Copy the notebook figures the report uses into report/figures/, without their plot titles.

The notebook's figure titles start with the label of the notebook step that made them. In the report the
caption below each figure says what it shows, so the title strip is painted over with the background
colour and the empty rows at the top are trimmed. Everything else in the figure is unchanged.

Run from the repository root (after the hand-in notebook has been run):
    .venv/bin/python report/report_figures.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "results" / "figures"
TARGET = ROOT / "report" / "figures"

# figure -> the boxes its title covers, each (first row, last row, last column) in pixels;
# None = to the right edge.
TITLES = {
    # the title's last rows sit next to the colour bar's "High" label, so they stop left of it
    "D1_shap_beeswarm.png": [(10, 35, None), (36, 37, 1236)],
    "D3_shap_mistake.png": [(10, 38, None)],
    "E3_robustness.png": [(0, 31, None)],
    "G3_adapt.png": [(18, 46, None)],
}
MARGIN = 8                                       # background rows kept above the first content


def without_title(name, boxes):
    picture = np.asarray(Image.open(SOURCE / name).convert("RGB")).copy()
    background = picture[-1, -1].copy()
    for first, last, right in boxes:
        picture[first:last + 1, :right] = background
    content = (np.abs(picture.astype(int) - background.astype(int)).sum(axis=2) > 40).any(axis=1)
    top = max(0, int(np.argmax(content)) - MARGIN)
    return Image.fromarray(picture[top:])


def main():
    TARGET.mkdir(exist_ok=True)
    for name, boxes in TITLES.items():
        out = without_title(name, boxes)
        out.save(TARGET / name)
        print(f"report/figures/{name}: {out.size[0]} x {out.size[1]}")


if __name__ == "__main__":
    main()
