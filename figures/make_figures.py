"""
Draw the concept diagrams used in the lessons as SVG files.

The diagrams are original drawings made for this course; they are not copies of
figures from any textbook. Re-run after editing:  python figures/make_figures.py
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent

NAVY, INK, MUTED = "#1f3a5f", "#1b1f24", "#7a8291"
REAL_FILL, GHOST_FILL, GHOST_LINE = "#dbe7f5", "#f6f8fa", "#9fb0c3"
RES_FILL, RES_LINE = "#fbf1e3", "#c8862b"
FONT = "Segoe UI, system-ui, -apple-system, Roboto, Arial, sans-serif"
MONO = "Consolas, Menlo, monospace"
C = 36  # cell size


def text(x, y, s, size=13, fill=INK, anchor="middle", family=FONT, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-family="{family}" font-weight="{weight}">{s}</text>')


def cell(x, y, value, kind="real"):
    if kind == "real":
        box = f'<rect x="{x}" y="{y}" width="{C}" height="{C}" fill="{REAL_FILL}" stroke="{NAVY}" stroke-width="1.4"/>'
        col = INK
    elif kind == "ghost":
        box = (f'<rect x="{x}" y="{y}" width="{C}" height="{C}" fill="{GHOST_FILL}" stroke="{GHOST_LINE}" '
               f'stroke-width="1.2" stroke-dasharray="4 3"/>')
        col = MUTED
    else:  # result
        box = f'<rect x="{x}" y="{y}" width="{C}" height="{C}" fill="{RES_FILL}" stroke="{RES_LINE}" stroke-width="1.4"/>'
        col = INK
    return box + text(x + C / 2, y + C / 2 + 5, value, size=13, fill=col, family=MONO)


def grid(x, y, values, kinds):
    """values / kinds: lists of rows."""
    out = []
    for r, (vrow, krow) in enumerate(zip(values, kinds)):
        for c, (v, k) in enumerate(zip(vrow, krow)):
            out.append(cell(x + c * C, y + r * C, v, k))
    return "".join(out)


def broadcasting():
    W, H = 640, 520
    xa, xb, xr = 40, 240, 470          # left edges of the three blocks
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
             f'aria-labelledby="t d"><title id="t">How broadcasting stretches arrays</title>'
             f'<desc id="d">Three additions. A scalar is stretched along a row. A row is copied down the rows of a '
             f'table. A column and a row are both stretched into a table.</desc>'
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    def op(y, sym_y):
        return (text(xb - 46, sym_y, "+", size=22, fill=NAVY, weight="600")
                + text(xr - 46, sym_y, "=", size=22, fill=NAVY, weight="600"))

    # ---- case 1: row + scalar
    y = 56
    parts.append(text(20, y - 26, "1 · array + single number", size=14, fill=NAVY, anchor="start", weight="600"))
    parts.append(grid(xa, y, [["70", "80", "90"]], [["real"] * 3]))
    parts.append(grid(xb, y, [["5", "5", "5"]], [["real", "ghost", "ghost"]]))
    parts.append(grid(xr, y, [["75", "85", "95"]], [["res"] * 3]))
    parts.append(op(y, y + C / 2 + 7))
    for x, s in ((xa, "shape (3,)"), (xb, "a scalar → stretched to (3,)"), (xr, "shape (3,)")):
        parts.append(text(x, y + C + 18, s, size=12, fill=MUTED, anchor="start"))

    # ---- case 2: table + row
    y = 176
    parts.append(text(20, y - 26, "2 · table + row", size=14, fill=NAVY, anchor="start", weight="600"))
    parts.append(grid(xa, y, [["70", "80", "90"], ["60", "85", "95"], ["75", "65", "80"]], [["real"] * 3] * 3))
    parts.append(grid(xb, y, [["5", "0", "10"]] * 3, [["real"] * 3, ["ghost"] * 3, ["ghost"] * 3]))
    parts.append(grid(xr, y, [["75", "80", "100"], ["65", "85", "105"], ["80", "65", "90"]], [["res"] * 3] * 3))
    parts.append(op(y, y + 1.5 * C + 7))
    for x, s in ((xa, "shape (3, 3)"), (xb, "shape (3,) → copied down"), (xr, "shape (3, 3)")):
        parts.append(text(x, y + 3 * C + 18, s, size=12, fill=MUTED, anchor="start"))

    # ---- case 3: column + row
    y = 366
    parts.append(text(20, y - 26, "3 · column + row (both are stretched)", size=14, fill=NAVY, anchor="start",
                      weight="600"))
    parts.append(grid(xa, y, [["0", "0", "0"], ["10", "10", "10"], ["20", "20", "20"]],
                      [["real", "ghost", "ghost"]] * 3))
    parts.append(grid(xb, y, [["1", "2", "3"]] * 3, [["real"] * 3, ["ghost"] * 3, ["ghost"] * 3]))
    parts.append(grid(xr, y, [["1", "2", "3"], ["11", "12", "13"], ["21", "22", "23"]], [["res"] * 3] * 3))
    parts.append(op(y, y + 1.5 * C + 7))
    for x, s in ((xa, "shape (3, 1) → copied across"), (xb, "shape (3,) → copied down"), (xr, "shape (3, 3)")):
        parts.append(text(x, y + 3 * C + 18, s, size=12, fill=MUTED, anchor="start"))

    # ---- legend
    ly = H - 16
    parts.append(f'<rect x="20" y="{ly - 12}" width="14" height="14" fill="{REAL_FILL}" stroke="{NAVY}" stroke-width="1.2"/>')
    parts.append(text(40, ly, "value stored in memory", size=12, fill=INK, anchor="start"))
    parts.append(f'<rect x="210" y="{ly - 12}" width="14" height="14" fill="{GHOST_FILL}" stroke="{GHOST_LINE}" '
                 f'stroke-width="1.2" stroke-dasharray="4 3"/>')
    parts.append(text(230, ly, "virtual copy made by broadcasting (not stored)", size=12, fill=INK, anchor="start"))
    parts.append("</svg>")
    (OUT / "broadcasting.svg").write_text("".join(parts), encoding="utf-8")


def split_apply_combine():
    W, H = 700, 330
    key_fill = {"DS": "#dbe7f5", "CS": "#e6f4ec", "AI": "#fbf1e3"}
    key_line = {"DS": NAVY, "CS": "#1e7f4f", "AI": "#c8862b"}
    rows = [("DS", "3.0"), ("CS", "2.0"), ("AI", "3.5"), ("DS", "4.0"), ("CS", "3.0"), ("AI", "2.5")]
    rh, kw, vw = 28, 56, 50
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">'
         f'<title id="t">Split, apply, combine</title>'
         f'<desc id="d">A table of majors and GPAs is split into one small table per major, the mean is applied '
         f'to each, and the three means are combined into one result table.</desc>'
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>'
         f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>']

    def row(x, y, k, v, head=False):
        if head:
            f, s, col = "#eef1f5", "#c9d0da", MUTED
        else:
            f, s, col = key_fill[k], key_line[k], INK
        out = (f'<rect x="{x}" y="{y}" width="{kw}" height="{rh}" fill="{f}" stroke="{s}" stroke-width="1.2"/>'
               f'<rect x="{x + kw}" y="{y}" width="{vw}" height="{rh}" fill="{f}" stroke="{s}" stroke-width="1.2"/>')
        out += text(x + kw / 2, y + rh / 2 + 5, k if not head else "major", size=12, fill=col, family=MONO)
        out += text(x + kw + vw / 2, y + rh / 2 + 5, v if not head else "gpa", size=12, fill=col, family=MONO)
        return out

    def arrow(x1, y1, x2, y2):
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="1.3" '
                f'marker-end="url(#a)"/>')

    for x, s in ((20 + (kw + vw) / 2, "1 · the table"), (250, "2 · split by major"),
                 (455, "3 · apply mean()"), (610, "4 · combine")):
        p.append(text(x, 26, s, size=13, fill=NAVY, weight="600"))

    # original table
    x0, y0 = 20, 70
    p.append(row(x0, y0 - rh, "", "", head=True))
    for i, (k, v) in enumerate(rows):
        p.append(row(x0, y0 + i * rh, k, v))

    # split groups, apply, combine
    xs, xm, xc = 197, 420, 557
    p.append(row(xc, 118 - rh, "", "", head=True))
    for gi, k in enumerate(("DS", "CS", "AI")):
        gy = 52 + gi * 92
        vals = [v for kk, v in rows if kk == k]
        for j, v in enumerate(vals):
            p.append(row(xs, gy + j * rh, k, v))
        mean = sum(map(float, vals)) / len(vals)
        cy = gy + rh
        p.append(arrow(x0 + kw + vw + 8, y0 + 3 * rh, xs - 8, cy))
        p.append(arrow(xs + kw + vw + 8, cy, xm - 8, cy))
        p.append(f'<rect x="{xm}" y="{cy - 15}" width="70" height="30" rx="15" fill="{key_fill[k]}" '
                 f'stroke="{key_line[k]}" stroke-width="1.2"/>')
        p.append(text(xm + 35, cy + 5, f"{mean:.2f}", size=12, family=MONO))
        ry = 118 + gi * rh
        p.append(arrow(xm + 78, cy, xc - 8, ry + rh / 2))
        p.append(row(xc, ry, k, f"{mean:.2f}"))

    p.append(text(W / 2, H - 12, 'df.groupby("major")["gpa"].mean()', size=13, fill=NAVY, family=MONO))
    p.append("</svg>")
    (OUT / "split-apply-combine.svg").write_text("".join(p), encoding="utf-8")


# --------------------------------------------------------------------------- generic helpers for the later figures
def svg_open(W, H, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc><rect width="{W}" height="{H}" fill="#ffffff"/>'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{NAVY}"/></marker></defs>')


def arrow(x1, y1, x2, y2, color=NAVY, width=1.6):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" '
            f'marker-end="url(#a)"/>')


HEAD_FILL, HEAD_LINE = "#eef1f5", "#c9d0da"
GREEN_FILL, GREEN_LINE = "#e6f4ec", "#1e7f4f"


def table(x, y, header, rows, widths, rh=28, styles=None, head_style=None):
    """Draw a table. styles: dict {(row, col): 'real'|'res'|'ghost'|'green'|'head'} (default 'plain')."""
    look = {"plain": ("#ffffff", HEAD_LINE, INK), "real": (REAL_FILL, NAVY, INK), "res": (RES_FILL, RES_LINE, INK),
            "ghost": (GHOST_FILL, GHOST_LINE, MUTED), "green": (GREEN_FILL, GREEN_LINE, INK),
            "head": (HEAD_FILL, HEAD_LINE, MUTED)}
    styles = styles or {}
    out = []

    def cells(yy, values, r):
        xx = x
        for c, (v, w) in enumerate(zip(values, widths)):
            kind = "head" if r == -1 else styles.get((r, c), styles.get((r, None), styles.get((None, c), "plain")))
            if r == -1 and head_style:
                kind = head_style.get(c, "head")
            f, st, col = look[kind]
            dash = ' stroke-dasharray="4 3"' if kind == "ghost" else ""
            out.append(f'<rect x="{xx}" y="{yy}" width="{w}" height="{rh}" fill="{f}" stroke="{st}" '
                       f'stroke-width="1.2"{dash}/>')
            out.append(text(xx + w / 2, yy + rh / 2 + 4.5, v, size=12, fill=col, family=MONO))
            xx += w

    if header:
        cells(y, header, -1)
        y += rh
    for r, row in enumerate(rows):
        cells(y + r * rh, row, r)
    return "".join(out)


def axis_figure():
    W, H = 640, 330
    p = [svg_open(W, H, "The axis argument",
                  "A table of three students by four exams. Axis 0 collapses the rows and gives one result per "
                  "column. Axis 1 collapses the columns and gives one result per row.")]
    vals = [[70, 80, 90, 60], [60, 85, 95, 80], [75, 65, 80, 100]]
    x0, y0 = 150, 70
    p.append(text(x0 + 2 * C, 30, "scores  ·  shape (3, 4)", size=14, fill=NAVY, weight="600"))
    p.append(text(x0 - 10, y0 - 10, "exam", size=11, fill=MUTED, anchor="end"))
    for j in range(4):
        p.append(text(x0 + j * C + C / 2, y0 - 10, str(j), size=11, fill=MUTED))
    for i in range(3):
        p.append(text(x0 - 10, y0 + i * C + C / 2 + 4, f"student {i}", size=11, fill=MUTED, anchor="end"))
    p.append(grid(x0, y0, [[str(v) for v in r] for r in vals], [["real"] * 4] * 3))
    # axis=1 → per row, to the right
    xr = x0 + 4 * C + 70
    for i in range(3):
        p.append(arrow(x0 + 4 * C + 8, y0 + i * C + C / 2, xr - 8, y0 + i * C + C / 2))
        m = sum(vals[i]) / 4
        p.append(cell(xr, y0 + i * C, f"{m:g}", "res"))
    p.append(text(xr + C + 14, y0 + C + 2, "scores.mean(axis=1)", size=12.5, fill=NAVY, anchor="start", family=MONO))
    p.append(text(xr + C + 14, y0 + C + 22, "across the columns:", size=12, fill=INK, anchor="start"))
    p.append(text(xr + C + 14, y0 + C + 39, "one result per row, shape (3,)", size=12, fill=INK, anchor="start"))
    # axis=0 → per column, below
    yb = y0 + 3 * C + 60
    for j in range(4):
        p.append(arrow(x0 + j * C + C / 2, y0 + 3 * C + 8, x0 + j * C + C / 2, yb - 8))
        m = sum(vals[i][j] for i in range(3)) / 3
        label = f"{m:.0f}" if abs(m - round(m)) < 1e-9 else f"{m:.1f}"
        p.append(f'<rect x="{x0 + j * C}" y="{yb}" width="{C}" height="{C}" fill="{RES_FILL}" stroke="{RES_LINE}" '
                 f'stroke-width="1.4"/>')
        p.append(text(x0 + j * C + C / 2, yb + C / 2 + 4, label, size=11, family=MONO))
    p.append(text(x0 + 4 * C + 20, yb + 14, "scores.mean(axis=0)", size=12.5, fill=NAVY, anchor="start", family=MONO))
    p.append(text(x0 + 4 * C + 20, yb + 32, "down the rows: one result per column, shape (4,)", size=12, fill=INK,
                  anchor="start"))
    p.append("</svg>")
    (OUT / "axis.svg").write_text("".join(p), encoding="utf-8")


def mask_figure():
    W, H = 700, 250
    p = [svg_open(W, H, "Selecting with a mask",
                  "Five scores, the true or false result of testing each against 60, and the three scores kept.")]
    x0 = 190
    vals = [55, 82, 47, 91, 68]
    keep = [v > 60 for v in vals]
    p.append(text(x0 - 16, 48 + C / 2 + 4, "x", size=13, fill=NAVY, anchor="end", family=MONO, weight="600"))
    p.append(grid(x0, 48, [[str(v) for v in vals]], [["real"] * 5]))
    p.append(text(x0 - 16, 118 + C / 2 + 4, "x &gt; 60", size=13, fill=NAVY, anchor="end", family=MONO, weight="600"))
    for j, k in enumerate(keep):
        xx = x0 + j * C
        f, st = (GREEN_FILL, GREEN_LINE) if k else (GHOST_FILL, GHOST_LINE)
        p.append(f'<rect x="{xx}" y="118" width="{C}" height="{C}" fill="{f}" stroke="{st}" stroke-width="1.3"/>')
        p.append(text(xx + C / 2, 118 + C / 2 + 5, "T" if k else "F", size=13, fill=INK if k else MUTED, family=MONO))
        p.append(arrow(xx + C / 2, 48 + C + 4, xx + C / 2, 118 - 6, color=MUTED, width=1.1))
    p.append(text(x0 - 16, 188 + C / 2 + 4, "x[x &gt; 60]", size=13, fill=NAVY, anchor="end", family=MONO, weight="600"))
    kept = [v for v in vals if v > 60]
    p.append(grid(x0, 188, [[str(v) for v in kept]], [["res"] * len(kept)]))
    n = 0
    for j, k in enumerate(keep):
        if k:
            p.append(arrow(x0 + j * C + C / 2, 118 + C + 4, x0 + n * C + C / 2, 188 - 6, color=GREEN_LINE, width=1.3))
            n += 1
    p.append(text(x0 + 5 * C + 22, 118 + C / 2 + 4, "the mask: one True or False per element", size=12, fill=INK,
                  anchor="start"))
    p.append(text(x0 + 3 * C + 22, 188 + C / 2 + 4, "only the elements under a True", size=12, fill=INK, anchor="start"))
    p.append("</svg>")
    (OUT / "mask.svg").write_text("".join(p), encoding="utf-8")


def dataframe_figure():
    W, H = 640, 270
    p = [svg_open(W, H, "The parts of a DataFrame",
                  "A table of four students. The row labels on the left are the index, the names along the top are "
                  "the columns, the cells are the values, and the gpa column alone is a Series.")]
    x0, y0, rh = 190, 78, 30
    widths = [80, 70, 70, 70]
    rows = [["Ahmad", "DS", "2", "3.4"], ["Sara", "CS", "4", "2.1"], ["Omar", "DS", "1", "3.9"], ["Lina", "AI", "3", "3.2"]]
    styles = {(None, 0): "green", (None, 3): "res"}
    p.append(table(x0, y0, ["", "major", "year", "gpa"], rows, widths, rh=rh, styles=styles,
                   head_style={0: "plain", 1: "real", 2: "real", 3: "real"}))
    # labels
    p.append(text(x0 + 80 + 105, 34, "columns  (df.columns)", size=13, fill=NAVY, weight="600"))
    p.append(arrow(x0 + 80 + 105, 42, x0 + 80 + 105, y0 - 6))
    p.append(text(30, y0 + rh + 2 * rh + 4, "index", size=13, fill=GREEN_LINE, anchor="start", weight="600"))
    p.append(text(30, y0 + rh + 2 * rh + 22, "(df.index)", size=12, fill=GREEN_LINE, anchor="start"))
    p.append(f'<line x1="118" y1="{y0 + 3 * rh}" x2="{x0 - 8}" y2="{y0 + 3 * rh}" stroke="{GREEN_LINE}" '
             f'stroke-width="1.6" marker-end="url(#a)"/>')
    xr = x0 + sum(widths) + 60
    p.append(text(xr, y0 + 2 * rh, "one column", size=13, fill=RES_LINE, anchor="start", weight="600"))
    p.append(text(xr, y0 + 2 * rh + 18, 'df["gpa"]', size=12.5, fill=RES_LINE, anchor="start", family=MONO))
    p.append(text(xr, y0 + 2 * rh + 36, "is a Series", size=12, fill=INK, anchor="start"))
    p.append(f'<line x1="{xr - 6}" y1="{y0 + 2 * rh + 8}" x2="{x0 + sum(widths) + 8}" y2="{y0 + 2 * rh + 8}" '
             f'stroke="{RES_LINE}" stroke-width="1.6" marker-end="url(#a)"/>')
    p.append(text(x0 + 80 + 70, y0 + 5 * rh + 26, "values: the cells in the middle  (df.values)", size=12.5, fill=INK))
    p.append("</svg>")
    (OUT / "dataframe.svg").write_text("".join(p), encoding="utf-8")


def alignment_figure():
    W, H = 640, 240
    p = [svg_open(W, H, "Index alignment",
                  "Quiz 1 has marks for Ahmad, Sara and Omar. Quiz 2 has marks for Sara, Omar and Lina. In the sum, "
                  "Sara and Omar have totals, and Ahmad and Lina are missing.")]
    rh, w = 28, [70, 50]
    y0 = 62
    p.append(text(40 + 60, 34, "quiz1", size=13, fill=NAVY, family=MONO, weight="600"))
    p.append(table(40, y0, None, [["Ahmad", "8"], ["Sara", "6"], ["Omar", "9"]], w, rh=rh,
                   styles={(1, None): "real", (2, None): "real"}))
    p.append(text(190, y0 + 1.5 * rh + 6, "+", size=22, fill=NAVY, weight="600"))
    p.append(text(240 + 60, 34, "quiz2", size=13, fill=NAVY, family=MONO, weight="600"))
    p.append(table(240, y0, None, [["Sara", "7"], ["Omar", "10"], ["Lina", "5"]], w, rh=rh,
                   styles={(0, None): "real", (1, None): "real"}))
    p.append(text(395, y0 + 1.5 * rh + 6, "=", size=22, fill=NAVY, weight="600"))
    p.append(text(440 + 60, 34, "quiz1 + quiz2", size=13, fill=NAVY, family=MONO, weight="600"))
    p.append(table(440, y0 - rh / 2, None, [["Ahmad", "NaN"], ["Lina", "NaN"], ["Omar", "19"], ["Sara", "13"]], w,
                   rh=rh, styles={(0, None): "ghost", (1, None): "ghost", (2, None): "res", (3, None): "res"}))
    p.append(text(W / 2, H - 46, "Values are matched by label, wherever the label sits in each column.", size=12.5,
                  fill=INK))
    p.append(text(W / 2, H - 26, "A label found on one side only has no partner, so its result is NaN (missing).",
                  size=12.5, fill=INK))
    p.append("</svg>")
    (OUT / "alignment.svg").write_text("".join(p), encoding="utf-8")


def merge_figure():
    W, H = 700, 400
    p = [svg_open(W, H, "Three ways to join two tables",
                  "A table of names and majors and a table of names and grades are joined on name. The inner join "
                  "has Sara and Omar. The left join adds Ahmad with a missing grade. The outer join also adds Lina "
                  "with a missing major.")]
    rh = 26
    p.append(text(40 + 65, 30, "majors (left)", size=13, fill=NAVY, weight="600"))
    p.append(table(40, 42, ["name", "major"], [["Ahmad", "DS"], ["Sara", "CS"], ["Omar", "DS"]], [70, 60], rh=rh,
                   styles={(1, None): "real", (2, None): "real"}))
    p.append(text(250 + 65, 30, "grades (right)", size=13, fill=NAVY, weight="600"))
    p.append(table(250, 42, ["name", "grade"], [["Sara", "65"], ["Omar", "92"], ["Lina", "71"]], [70, 60], rh=rh,
                   styles={(0, None): "real", (1, None): "real"}))
    p.append(text(430, 78, "Sara and Omar are in both tables.", size=12.5, fill=INK, anchor="start"))
    p.append(text(430, 98, "Ahmad is only in the left table.", size=12.5, fill=INK, anchor="start"))
    p.append(text(430, 118, "Lina is only in the right table.", size=12.5, fill=INK, anchor="start"))
    y = 215
    w3 = [66, 56, 56]
    cols = ["name", "major", "grade"]
    specs = [
        (30, 'how="inner"', "names found in both", [["Sara", "CS", "65"], ["Omar", "DS", "92"]], {}),
        (255, 'how="left"', "every row of the left table",
         [["Ahmad", "DS", "NaN"], ["Sara", "CS", "65"], ["Omar", "DS", "92"]], {(0, 2): "ghost"}),
        (480, 'how="outer"', "every row of both tables",
         [["Ahmad", "DS", "NaN"], ["Lina", "NaN", "71"], ["Omar", "DS", "92"], ["Sara", "CS", "65"]],
         {(0, 2): "ghost", (1, 1): "ghost"}),
    ]
    for x, title, sub, rows, ghosts in specs:
        st = {(r, None): "res" for r in range(len(rows))}
        st.update(ghosts)
        p.append(text(x + sum(w3) / 2, y - 30, title, size=13, fill=NAVY, family=MONO, weight="600"))
        p.append(text(x + sum(w3) / 2, y - 12, sub, size=11.5, fill=MUTED))
        p.append(table(x, y, cols, rows, w3, rh=rh, styles=st))
    p.append(text(W / 2, H - 14, "NaN marks a cell that has no value because the row had no partner.", size=12.5,
                  fill=INK))
    p.append("</svg>")
    (OUT / "merge.svg").write_text("".join(p), encoding="utf-8")


def pivot_figure():
    W, H = 680, 300
    p = [svg_open(W, H, "From a long table to a pivot table",
                  "Six rows of city, product and units are turned into a grid with Amman and Irbid as rows and Laptop "
                  "and Phone as columns. Amman Laptop is 4 because two rows are added.")]
    rh = 27
    rows = [["Amman", "Laptop", "3"], ["Amman", "Phone", "5"], ["Irbid", "Laptop", "2"], ["Irbid", "Phone", "4"],
            ["Amman", "Laptop", "1"], ["Irbid", "Phone", "6"]]
    st = {(0, None): "real", (4, None): "real"}
    p.append(text(40 + 100, 30, "long: one row per sale", size=13, fill=NAVY, weight="600"))
    p.append(table(40, 44, ["city", "product", "units"], rows, [70, 76, 54], rh=rh, styles=st))
    p.append(arrow(262, 140, 352, 140))
    p.append(text(307, 128, "pivot_table", size=11.5, fill=NAVY, family=MONO))
    p.append(text(390 + 110, 74, "wide: city by product", size=13, fill=NAVY, weight="600"))
    p.append(table(390, 90, ["city", "Laptop", "Phone"], [["Amman", "4", "5"], ["Irbid", "2", "10"]], [76, 72, 72],
                   rh=rh, styles={(0, 1): "real", (0, 0): "green", (1, 0): "green"},
                   head_style={0: "head", 1: "res", 2: "res"}))
    p.append(text(390, 196, "index=\"city\" gives the rows", size=12, fill=GREEN_LINE, anchor="start"))
    p.append(text(390, 215, "columns=\"product\" gives the columns", size=12, fill=RES_LINE, anchor="start"))
    p.append(text(390, 234, "aggfunc=\"sum\" fills each cell:", size=12, fill=INK, anchor="start"))
    p.append(text(390, 253, "Amman + Laptop = 3 + 1 = 4", size=12, fill=NAVY, anchor="start", weight="600"))
    p.append("</svg>")
    (OUT / "pivot.svg").write_text("".join(p), encoding="utf-8")


if __name__ == "__main__":
    broadcasting()
    split_apply_combine()
    axis_figure()
    mask_figure()
    dataframe_figure()
    alignment_figure()
    merge_figure()
    pivot_figure()
    print("wrote", ", ".join(sorted(f.name for f in OUT.glob("*.svg"))))
