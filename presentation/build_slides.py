"""Build the slide deck from presentation/slides.md, in the style of the seminar deck.

The text of every slide (title, source line, cards, big numbers, tables, takeaway line and speaker
notes) is read from slides.md, so the deck and the plan cannot drift apart; this script only decides
where things go. The look is copied from AutoPenBench_Seminar.pptx: its slide masters and theme
(Century Schoolbook) are reused, its slides are removed, and the new slides use the same positions,
font sizes and colours (cream background, navy text, blue and teal accents, grey source line).

Run from the repository root:
    .venv/bin/python presentation/build_slides.py            # writes presentation/Mini_Project_Presentation.pptx
    .venv/bin/python presentation/build_slides.py --preview  # also draws PNG previews in /tmp/slide_preview

The preview uses C059, a free font with the metrics of Century Schoolbook, and reports any text that
would not fit its box. Needs python-pptx (not part of requirements.txt; only the slides use it).
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Cm, Pt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "AutoPenBench_Seminar.pptx"
PLAN = ROOT / "presentation" / "slides.md"
OUTPUT = ROOT / "presentation" / "Mini_Project_Presentation.pptx"
FIGURES = ROOT / "results" / "figures"
PREVIEW = Path("/tmp/slide_preview")

NAVY, GREY, BLUE, TEAL = "17283C", "526173", "245CC5", "087F79"
CREAM, PANEL, MID, WHITE = "F5F3ED", "DFE9F3", "9DB8EA", "FFFFFF"
LEFT = 1.91                      # left margin of every template slide, cm
RIGHT = 31.97                    # right edge of the template's title box, cm


# ---------------------------------------------------------------------------
# Reading slides.md
# ---------------------------------------------------------------------------
def inline(text):
    """Markdown inline text -> list of (text, bold) runs; backticks are dropped."""
    text = text.replace("`", "")
    runs = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part:
            runs.append((part, i % 2 == 1))
    return runs


def plain(text):
    return "".join(t for t, _ in inline(text))


def read_plan():
    """{slide number: dict} with title, source, takeaway, bullets, table, notes, presenter, seconds."""
    sections = re.split(r"^## Slide (\d+): (.*)$", PLAN.read_text(encoding="utf-8"), flags=re.M)
    slides = {}
    for i in range(1, len(sections), 3):
        number, title, body = int(sections[i]), sections[i + 1].strip(), sections[i + 2]
        body = body.split("\n## ")[0]
        info = {"title": re.sub(r" \(Part [A-G]\)$", "", title), "bullets": [], "table": [], "notes": []}
        notes_started = False
        for line in body.splitlines():
            if line.startswith("**Speaker notes.**"):
                notes_started = True
                m = re.search(r"Target time: (\d+) seconds\. Presenter: (\w+)\.", line)
                info["seconds"], info["presenter"] = int(m.group(1)), m.group(2)
            elif line.startswith("**Source line:**"):
                info["source"] = plain(line.split(":**", 1)[1].strip())
            elif line.startswith("**Takeaway line:**"):
                info["takeaway"] = line.split(":**", 1)[1].strip()
            elif notes_started and line.startswith(">"):
                info["notes"].append(line[1:].strip())
            elif not notes_started and line.startswith("- "):
                info["bullets"].append(line[2:].strip())
            elif not notes_started and line.startswith("|") and not re.match(r"^\|[-| ]+\|$", line):
                info["table"].append([c.strip() for c in line.strip("|").split("|")])
        slides[number] = info
    return slides


def card(bullet):
    """'**Heading.** body' -> (heading, body)."""
    m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", bullet)
    return m.group(1).rstrip("."), m.group(2)


def big_number(bullet):
    """'Big number: **0.737** label' -> ('0.737', 'label')."""
    m = re.match(r"^Big number: \*\*(.+?)\*\*,?\s*(.*)$", bullet)
    return m.group(1), m.group(2)


def notes_text(number, info):
    paragraphs, current = [], []
    for line in info["notes"]:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    head = f"Target time: {info['seconds']} seconds. Presenter: {info['presenter']}.\nSlide {number}: {info['title']}"
    return head + "\n" + "\n".join(paragraphs)


# ---------------------------------------------------------------------------
# Drawing: every element goes to the PPTX slide and to the preview list
# ---------------------------------------------------------------------------
class Deck:
    def __init__(self):
        self.prs = Presentation(str(TEMPLATE))
        slide_ids = self.prs.slides._sldIdLst
        for slide_id in list(slide_ids):          # keep masters, layouts and theme; drop the old slides
            self.prs.part.drop_rel(slide_id.rId)
            slide_ids.remove(slide_id)
        self.blank = next(l for l in self.prs.slide_layouts if l.name == "Blank")
        self.previews = []

    def new_slide(self, notes=""):
        slide = self.prs.slides.add_slide(self.blank)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor.from_string(CREAM)
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
        self.slide, self.items = slide, []
        self.previews.append(self.items)
        return slide

    def text(self, x, y, w, h, paragraphs, size, color=NAVY, bold=False, align="l", anchor="t",
             font=None, space_after=0):
        """paragraphs: a str, or a list of paragraphs, each a str (markdown inline) or list of runs."""
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]
        paragraphs = [inline(p) if isinstance(p, str) else p for p in paragraphs]
        box = self.slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
        frame = box.text_frame
        frame.word_wrap = True
        frame.auto_size = MSO_AUTO_SIZE.NONE
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        frame.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
        for i, runs in enumerate(paragraphs):
            para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            if space_after and i < len(paragraphs) - 1:
                para.space_after = Pt(space_after)
            for content, run_bold in runs:
                run = para.add_run()
                run.text = content
                run.font.size = Pt(size)
                run.font.bold = bold or run_bold
                run.font.color.rgb = RGBColor.from_string(color)
                if font:
                    run.font.name = font
        self.items.append(("text", x, y, w, h, paragraphs, size, color, bold, align, anchor, space_after))

    def rect(self, x, y, w, h, fill, line=None):
        shape = self.slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill)
        if line:
            shape.line.color.rgb = RGBColor.from_string(line)
            shape.line.width = Pt(1.1)
        else:
            shape.line.fill.background()
        shape.shadow.inherit = False
        self.items.append(("rect", x, y, w, h, fill, line))

    def line(self, x1, y1, x2, y2, color=GREY, width=0.75):
        connector = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x1), Cm(y1), Cm(x2), Cm(y2))
        connector.line.color.rgb = RGBColor.from_string(color)
        connector.line.width = Pt(width)
        self.items.append(("line", x1, y1, x2, y2, color, width))

    def image(self, path, x, y, w=None, h=None):
        """Place a figure inside the box (x, y, w, h), keeping its shape; returns the box it used."""
        width, height = Image.open(path).size
        ratio = width / height
        if w is not None and h is not None:
            if w / h > ratio:
                w = h * ratio
            else:
                h = w / ratio
        elif w is not None:
            h = w / ratio
        else:
            w = h * ratio
        self.rect(x - 0.1, y - 0.1, w + 0.2, h + 0.2, WHITE)          # white mount on the cream page
        self.slide.shapes.add_picture(str(path), Cm(x), Cm(y), Cm(w), Cm(h))
        self.items.append(("image", path, x, y, w, h))
        return x, y, w, h

    # --- the template's fixed parts ---
    def header(self, title, number, source=None):
        self.text(LEFT, 1.46, 30.06, 2.65, title, 33, bold=True)
        self.text(29.96, 17.38, 1.01, 0.66, str(number), 12.5, GREY, align="r")
        if source:
            self.text(LEFT, 17.25, 27.4, 0.93, source, 12, GREY)

    def takeaway(self, text):
        self.text(LEFT, 15.1, 30.06, 1.95, text, 20, BLUE, bold=True)

    def cards(self, items, top=5.03, step=3.45, head_w=9.0, body_x=11.6, body_w=20.3, body_size=20):
        for i, bullet in enumerate(items):
            heading, body = card(bullet)
            y = top + i * step
            self.text(LEFT, y, head_w, step - 0.2, heading, 22.5, BLUE, bold=True)
            self.text(body_x, y, body_w, step - 0.2, body, body_size)

    def stacked_cards(self, items, x, w, top=4.6, step=3.3, body_size=18):
        for i, bullet in enumerate(items):
            heading, body = card(bullet)
            y = top + i * step
            self.text(x, y, w, 1.0, heading, 21, BLUE, bold=True)
            self.text(x, y + 1.05, w, step - 1.15, body, body_size)

    def big(self, x, y, w, number, label, color=BLUE, size=66, label_size=19, label_h=2.6):
        while size > 20 and font(size, True).getlength(number) > w * PX:     # one line, shrink if needed
            size -= 2
        self.text(x, y, w, 2.9, number, size, color, bold=True, anchor="b")
        self.text(x, y + 3.0, w, label_h, label, label_size, NAVY)

    def table(self, rows, x, y, widths, size=18, row_h=1.15, first_bold_col=False):
        """rows[0] is the header; a row whose cells are all **bold** is drawn bold."""
        total = sum(widths)
        for r, row in enumerate(rows):
            cx = x
            for c, (cell, width) in enumerate(zip(row, widths)):
                bold = r == 0
                color = GREY if r == 0 else NAVY
                self.text(cx, y + r * row_h + 0.18, width - 0.3, row_h - 0.2, cell, size if r else size - 2,
                          color, bold=bold, align="l" if c == 0 else "r")
                cx += width
            self.line(x, y + (r + 1) * row_h, x + total, y + (r + 1) * row_h,
                      NAVY if r == 0 else "C9CDD2", 1.0 if r == 0 else 0.75)


# ---------------------------------------------------------------------------
# The slides
# ---------------------------------------------------------------------------
def build(deck, plan):
    def start(n, extra_source=True):
        info = plan[n]
        deck.new_slide(notes_text(n, info))
        deck.header(info["title"], n, info.get("source") if extra_source else None)
        return info

    # 1. Title
    info = plan[1]
    fields = dict(b.split(": ", 1) for b in info["bullets"])
    deck.new_slide(notes_text(1, info))
    deck.text(LEFT, 1.46, 30.06, 2.65, "Mini Project · AI for Cybersecurity", 33, bold=True)
    deck.text(LEFT, 5.0, 29.1, 4.4, ["An Explainable and Robust", "Cyber-Defence Model"], 40, bold=True)
    deck.text(LEFT, 10.0, 27.78, 1.0, fields["Subtitle"], 24, GREY)
    deck.text(LEFT, 11.3, 27.78, 1.85, fields["Question line"].strip("*"), 26, BLUE)
    deck.text(LEFT, 13.9, 27.78, 2.6, ["Group 6: Kirill Silchenko, Stefanos Ntentopoulos",
                                       "AI for Cybersecurity (D7084E / D7041E) · 15 October 2026"], 18.5, GREY)
    deck.text(29.96, 17.38, 1.01, 0.66, "1", 12.5, GREY, align="r")

    # 2. Problem, data and baseline: three cards and the baseline as a big number
    info = start(2)
    cards = [b for b in info["bullets"] if b.startswith("**")]
    deck.cards(cards, top=4.95, step=3.4, head_w=6.9, body_x=9.2, body_w=13.6, body_size=18.5)
    number, label = big_number(next(b for b in info["bullets"] if b.startswith("Big number")))
    deck.rect(24.0, 4.95, 7.97, 9.6, PANEL)
    deck.big(24.6, 5.6, 7.0, number, label, TEAL, size=60, label_size=19, label_h=5.0)
    deck.takeaway(info["takeaway"])

    # 3. Three models: the test table and the black box's gain
    info = start(3)
    deck.table(info["table"], LEFT, 5.0, [9.6, 3.4, 3.0, 2.8], size=19, row_h=1.5)
    number, label = big_number(next(b for b in info["bullets"] if b.startswith("Big number")))
    deck.big(23.0, 5.6, 9.0, number, label, BLUE, size=66, label_size=20, label_h=4.0)
    deck.takeaway(info["takeaway"])

    # 4 and 14. Live cue slides
    def cue(n, lines):
        info = plan[n]
        deck.new_slide(notes_text(n, info))
        deck.text(29.96, 17.38, 1.01, 0.66, str(n), 12.5, GREY, align="r")
        deck.text(LEFT, 17.25, 27.4, 0.93, "mini_project_unsw_nb15.ipynb, running now (Restart Kernel and Run All on slide 1)", 12, GREY)
        deck.rect(LEFT, 4.4, 30.06, 9.9, PANEL, BLUE)
        deck.text(LEFT + 1.2, 5.3, 27.6, 2.3, "Live: the notebook", 48, BLUE, bold=True)
        deck.text(LEFT + 1.2, 8.0, 27.6, 1.5, info["title"].replace("Live: ", "").capitalize(), 28, NAVY, bold=True)
        deck.text(LEFT + 1.2, 9.9, 27.6, 4.0, lines, 21, NAVY, space_after=6)

    cue(4, ["Section \"Part B: scores on the test set, next to the trivial baseline\"",
            "Computed from the raw CSV files during this talk; the trained models load from the saved cache."])

    # 5. Fewer labels: big number and three cards
    info = start(5)
    number, label = big_number(next(b for b in info["bullets"] if b.startswith("Big number")))
    deck.big(LEFT, 5.0, 10.5, number.replace("-", "−"), label, BLUE, size=66, label_size=19, label_h=5.5)
    deck.stacked_cards([b for b in info["bullets"] if b.startswith("**")], 13.6, 18.37)
    deck.takeaway(info["takeaway"])

    # 6 and 7. A figure on the left, the numbers on the right
    def figure_slide(n, figure, right_bullets):
        info = start(n)
        _, _, w, _ = deck.image(FIGURES / figure, LEFT, 4.6, w=18.0, h=9.9)
        x = LEFT + w + 1.0
        number, label = big_number(info["bullets"][0])
        deck.big(x, 4.4, RIGHT - x, number, label, BLUE, size=60, label_size=18.5, label_h=2.4)
        deck.text(x, 9.6, RIGHT - x, 4.9, right_bullets(info["bullets"][1:]), 17, NAVY, space_after=8)
        deck.takeaway(info["takeaway"])

    figure_slide(6, "D1_shap_beeswarm.png", lambda b: b)
    figure_slide(7, "D3_shap_mistake.png", lambda b: b)

    # 8. Three cards
    info = start(8)
    deck.cards(info["bullets"], top=4.95, step=3.4, head_w=7.4, body_x=9.8, body_w=22.1, body_size=19)
    deck.takeaway(info["takeaway"])

    # 9. Robustness figure
    figure_slide(9, "E3_robustness.png", lambda b: b)

    # 10. Big number and three cards
    info = start(10)
    number, label = big_number(info["bullets"][0])
    deck.big(LEFT, 5.0, 10.5, number, label, TEAL, size=66, label_size=19, label_h=5.5)
    deck.stacked_cards(info["bullets"][1:], 13.6, 18.37, body_size=17)
    deck.takeaway(info["takeaway"])

    # 11. The BRB: a 3 x 3 grid of rules and the fair comparison
    info = start(11)
    winner = {  # most believed risk level of each rule, from results/tables/F2_rules.csv
        ("Low", "Low"): "Medium", ("Low", "Medium"): "Low", ("Low", "High"): "Low",
        ("Medium", "Low"): "Medium", ("Medium", "Medium"): "Low", ("Medium", "High"): "Low",
        ("High", "Low"): "High", ("High", "Medium"): "Medium", ("High", "High"): "Low"}
    fills = {"Low": (PANEL, NAVY), "Medium": (MID, NAVY), "High": (BLUE, WHITE)}
    gx, gy, cell = 6.0, 5.9, 2.35
    deck.text(gx, 4.75, 3 * cell, 0.8, "Bwd Packets/s", 15, GREY, bold=True, align="c")
    levels = ["Low", "Medium", "High"]
    for c, level in enumerate(levels):
        deck.text(gx + c * cell, 5.3, cell, 0.6, level, 13, GREY, align="c")
    for r, row_level in enumerate(levels):
        deck.text(LEFT, gy + r * cell, 3.9, cell, row_level, 13, GREY, align="r", anchor="m")
        for c, col_level in enumerate(levels):
            risk = winner[(row_level, col_level)]
            fill, ink = fills[risk]
            deck.rect(gx + c * cell + 0.05, gy + r * cell + 0.05, cell - 0.1, cell - 0.1, fill)
            deck.text(gx + c * cell, gy + r * cell, cell, cell, risk, 13, ink, bold=True, align="c", anchor="m")
    deck.text(LEFT, gy + 3 * cell + 0.2, 11.8, 1.9, ["Rows: FWD Init Win Bytes. Columns: Bwd Packets/s.",
              "Each cell is one rule, showing the risk level it believes most."], 13, GREY)
    deck.table(info["table"], 14.6, 4.95, [8.0, 3.3, 3.1, 2.97], size=17, row_h=1.45)
    deck.text(14.6, 11.0, 17.37, 3.9, "Inputs: the top two SHAP features with three distinct levels "
              "(5th percentile, median, 95th percentile). Rule beliefs from the training data; "
              "threshold 48.5 chosen on validation.", 16, NAVY)
    deck.takeaway(info["takeaway"])

    # 12. Three cards
    info = start(12)
    deck.cards(info["bullets"], top=4.95, step=3.4, head_w=7.4, body_x=9.8, body_w=22.1, body_size=19)
    deck.takeaway(info["takeaway"])

    # 13. The hidden attack: big number, two cards, the adaptation figure
    info = start(13)
    number, label = big_number(info["bullets"][0])
    deck.big(LEFT, 4.4, 11.6, number, label, TEAL, size=54, label_size=17, label_h=1.7)
    deck.stacked_cards(info["bullets"][1:], LEFT, 11.6, top=9.25, step=2.65, body_size=15)
    deck.image(FIGURES / "G3_adapt.png", 14.4, 4.8, w=17.5, h=9.6)
    deck.takeaway(info["takeaway"])

    cue(14, ["The test attack the model is most sure about (an Exploits flow)",
             "Then: Fwd Seg Size Min set to 32, and FWD Init Win Bytes to 5792, the benign machines' values"])

    # 15. Conclusion
    info = start(15)
    deck.text(LEFT, 4.3, 30.06, 1.6, "Not as it is.", 36, TEAL, bold=True)
    deck.cards(info["bullets"], top=6.3, step=2.8, head_w=7.4, body_x=9.8, body_w=22.1, body_size=17)
    deck.takeaway(info["takeaway"])

    # 16. Questions
    deck.new_slide()
    deck.text(LEFT, 1.46, 30.06, 2.65, "Questions", 33, bold=True)
    deck.text(LEFT, 6.5, 29.0, 2.0, "Thank you.", 40, BLUE, bold=True)
    deck.text(LEFT, 9.3, 29.0, 3.0, ["Kirill Silchenko (Parts A, B and F) · Stefanos Ntentopoulos (Parts C, D, E and G)",
                                     "Notebook: mini_project_unsw_nb15.ipynb · Report and README on Canvas"], 19, GREY,
              space_after=6)
    deck.text(29.96, 17.38, 1.01, 0.66, "16", 12.5, GREY, align="r")

    # Backup slides
    def backup(label, title, source, figure=None):
        deck.new_slide()
        deck.header(title, label, source)
        if figure:
            path = FIGURES / figure
            width, height = Image.open(path).size
            w = min(30.06, 11.6 * width / height)
            deck.image(path, LEFT + (30.06 - w) / 2, 4.6, w=w, h=11.6)

    backup("B1", "Backup: recall per attack type", "Notebook Part B · results/figures/B4_recall_per_type.png",
           "B4_recall_per_type.png")
    backup("B2", "Backup: the deletion test", "Notebook Part D · results/figures/D4_deletion.png", "D4_deletion.png")
    backup("B3", "Backup: the nine rules of the BRB", "Notebook Part F · results/tables/F2_rules.csv")
    rules = [["Rule (FWD Init Win Bytes, Bwd Packets/s)", "Low risk", "Medium risk", "High risk", "Attack share"]]
    for line in (ROOT / "results" / "tables" / "F2_rules.csv").read_text().splitlines()[1:]:
        fields = re.findall(r'"[^"]*"|[^,]+', line)
        rule = fields[1].replace("IF FWD Init Win Bytes is ", "").replace(" AND Bwd Packets/s is ", ", ")
        rules.append([f"{fields[0]}. {rule}", f"{float(fields[2]):.2f}", f"{float(fields[3]):.2f}",
                      f"{float(fields[4]):.2f}", f"{float(fields[-1]):.2f}"])
    deck.table(rules, LEFT, 4.5, [12.5, 4.0, 4.0, 4.0, 5.5], size=16, row_h=1.15)
    backup("B4", "Backup: labels needed for the hidden attack",
           "Separate notebook of additional checks · results/figures/X4_learning_curve.png", "X4_learning_curve.png")


# ---------------------------------------------------------------------------
# Preview and fit check
# ---------------------------------------------------------------------------
PX = 40                                            # pixels per cm in the preview
FONTS = {False: "/usr/share/fonts/opentype/urw-base35/C059-Roman.otf",
         True: "/usr/share/fonts/opentype/urw-base35/C059-Bold.otf"}


def font(size, bold):
    return ImageFont.truetype(FONTS[bold], max(1, round(size * 2.54 / 72 * PX)))


def wrap(runs, size, bold, width_px):
    """Greedy word wrap of one paragraph -> list of lines, each a list of (word, bold)."""
    words = [(w, bold or b) for text, b in runs for w in re.split(r"(?<= )", text) if w]
    lines, line, used = [], [], 0
    for word, b in words:
        w = font(size, b).getlength(word)
        if line and used + font(size, b).getlength(word.rstrip()) > width_px:
            lines.append(line)
            line, used = [], 0
        line.append((word, b))
        used += w
    if line:
        lines.append(line)
    return lines


def preview(previews):
    PREVIEW.mkdir(exist_ok=True)
    for old in PREVIEW.glob("*.png"):
        old.unlink()
    problems = []
    for number, items in enumerate(previews, 1):
        image = Image.new("RGB", (round(33.867 * PX), round(19.05 * PX)), "#" + CREAM)
        draw = ImageDraw.Draw(image)
        for item in items:
            kind = item[0]
            if kind == "rect":
                _, x, y, w, h, fill, line = item
                draw.rectangle([x * PX, y * PX, (x + w) * PX, (y + h) * PX], fill="#" + fill,
                               outline="#" + line if line else None, width=2)
            elif kind == "line":
                _, x1, y1, x2, y2, color, width = item
                draw.line([x1 * PX, y1 * PX, x2 * PX, y2 * PX], fill="#" + color, width=max(1, round(width)))
            elif kind == "image":
                _, path, x, y, w, h = item
                figure = Image.open(path).convert("RGB").resize((round(w * PX), round(h * PX)))
                image.paste(figure, (round(x * PX), round(y * PX)))
            else:
                _, x, y, w, h, paragraphs, size, color, bold, align, anchor, space_after = item
                line_h = size * 2.54 / 72 * PX * 1.2
                laid = []
                for p, runs in enumerate(paragraphs):
                    for line in wrap(runs, size, bold, w * PX):
                        laid.append(line)
                    laid.append(None)                     # paragraph break
                laid = laid[:-1]
                breaks = sum(1 for line in laid if line is None)
                height = sum(1 for line in laid if line) * line_h + breaks * space_after * 2.54 / 72 * PX
                if height > h * PX + 2:
                    text = "".join(t for runs in paragraphs for t, _ in runs)
                    problems.append(f"slide {number}: text taller than its box ({height / PX:.2f} cm > {h:.2f} cm): {text[:60]!r}")
                for line in laid:
                    if line and sum(font(size, b).getlength(word.rstrip()) for word, b in line[-1:]) > w * PX:
                        problems.append(f"slide {number}: a word is wider than its box: {line[-1][0]!r}")
                top = y * PX + {"t": 0, "m": (h * PX - height) / 2, "b": h * PX - height}[anchor]
                for line in laid:
                    if line is None:
                        top += space_after * 2.54 / 72 * PX
                        continue
                    widths = [font(size, b).getlength(word) for word, b in line]
                    total = sum(widths) - (font(size, line[-1][1]).getlength(" ") if line[-1][0].endswith(" ") else 0)
                    left = x * PX + {"l": 0, "c": (w * PX - total) / 2, "r": w * PX - total}[align]
                    for (word, b), width in zip(line, widths):
                        draw.text((left, top), word, font=font(size, b), fill="#" + color)
                        left += width
                    top += line_h
        image.save(PREVIEW / f"slide_{number:02d}.png")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--preview", action="store_true", help="also draw PNG previews and check that text fits")
    args = parser.parse_args()
    if not TEMPLATE.is_file():
        sys.exit(f"ERROR: the template {TEMPLATE.name} is missing")
    plan = read_plan()
    if sorted(plan) != list(range(1, 17)):
        sys.exit(f"ERROR: slides.md should have slides 1 to 16, found {sorted(plan)}")
    deck = Deck()
    build(deck, plan)
    deck.prs.save(str(OUTPUT))
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(deck.prs.slides)} slides, "
          f"{OUTPUT.stat().st_size // 1024} KB)")
    if args.preview:
        problems = preview(deck.previews)
        print(f"Previews in {PREVIEW}/")
        print("\n".join(problems) if problems else "All text fits its boxes.")


if __name__ == "__main__":
    main()
