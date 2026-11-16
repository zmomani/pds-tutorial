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


if __name__ == "__main__":
    broadcasting()
    split_apply_combine()
    print("wrote", ", ".join(sorted(f.name for f in OUT.glob("*.svg"))))
