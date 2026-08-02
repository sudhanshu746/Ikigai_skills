#!/usr/bin/env python3
"""Render an Ikigai Venn diagram as a standalone SVG.

Takes the four quadrants plus a centre statement and produces the classic
four-circle diagram: LOVE on top, GOOD AT left, WORLD NEEDS right, PAID FOR
bottom, with passion/mission/profession/vocation in the lenses and the person's
ikigai in the middle.

Usage:
    python3 make_ikigai_svg.py --input data.json --output ikigai.svg
    cat data.json | python3 make_ikigai_svg.py --output ikigai.svg

Input JSON:
    {
      "name": "Priya",                    // optional, used in the title
      "love":        ["...", "..."],      // 2-4 short items each
      "good_at":     ["...", "..."],
      "world_needs": ["...", "..."],
      "paid_for":    ["...", "..."],
      "ikigai": "the concise centre statement",
      "headings": {...},                  // optional overrides
      "overlaps": {...}                   // optional overrides
    }

Geometry is derived from R/D/CX/CY below, so the layout stays correct if those
are retuned — nothing is hardcoded to a particular canvas size.
"""

import argparse
import json
import math
import sys

# --- Geometry -------------------------------------------------------------
# Four circles of radius R, each offset D from the diagram centre along an axis.
# D < R, so all four overlap in the middle.
R = 400.0
D = 225.0
CX, CY = 700.0, 830.0
W, H = 1400.0, 1480.0

TITLE_Y = 66.0
SUBTITLE_Y = 104.0

# Text block widths. The left/right caps are geometrically narrower than the
# top/bottom ones -- that asymmetry is inherent to the shape, not a mistake.
WIDE_W = 540.0
NARROW_W = 300.0
CENTRE_W = 250.0

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
INK = "#1a2028"
MUTED = "#4a5563"

QUADRANTS = [
    # key, heading default, accent colour, position, text width
    ("love", "What do you LOVE to do?", "#e07a5f", "top", WIDE_W),
    ("good_at", "What are you GOOD AT?", "#3d82ab", "left", NARROW_W),
    ("world_needs", "What does the WORLD NEED?", "#6a994e", "right", NARROW_W),
    ("paid_for", "What can you be PAID FOR?", "#d4a017", "bottom", WIDE_W),
]

OVERLAP_DEFAULTS = {
    "passion": "Passion",
    "mission": "Mission",
    "profession": "Profession",
    "vocation": "Vocation",
}


def circle_centre(position):
    return {
        "top": (CX, CY - D),
        "bottom": (CX, CY + D),
        "left": (CX - D, CY),
        "right": (CX + D, CY),
    }[position]


def text_anchor(position):
    """Centre point of the outer cap of each circle, where its content sits."""
    reach = math.sqrt(R * R - D * D)  # how far the perpendicular circles intrude
    outer = {
        "top": (CX, ((CY - D - R) + (CY - reach)) / 2),
        "bottom": (CX, ((CY + D + R) + (CY + reach)) / 2),
        "left": (((CX - D - R) + (CX - reach)) / 2, CY),
        "right": (((CX + D + R) + (CX + reach)) / 2, CY),
    }
    return outer[position]


def centre_region_path():
    """Path for the four-way overlap: a curved square bounded by four arcs.

    Each corner is where two circle boundaries cross while sitting inside the
    other two. Solving for the top/left pair and mirroring gives all four.
    """
    tx, ty = circle_centre("top")
    lx, ly = circle_centre("left")
    mx, my = (tx + lx) / 2, (ty + ly) / 2
    sep = math.hypot(lx - tx, ly - ty)
    half = sep / 2
    h = math.sqrt(R * R - half * half)
    # Unit perpendicular to the line joining the two centres.
    px, py = -(ly - ty) / sep, (lx - tx) / sep
    candidates = [(mx + h * px, my + h * py), (mx - h * px, my - h * py)]
    # The corner we want is the one nearest the diagram centre.
    corner = min(candidates, key=lambda p: math.hypot(p[0] - CX, p[1] - CY))
    sx, sy = abs(corner[0] - CX), abs(corner[1] - CY)

    tl, tr = (CX - sx, CY - sy), (CX + sx, CY - sy)
    br, bl = (CX + sx, CY + sy), (CX - sx, CY + sy)
    a = f"A {R:.1f} {R:.1f} 0 0 1"
    return (
        f"M {tl[0]:.1f},{tl[1]:.1f} "
        f"{a} {tr[0]:.1f},{tr[1]:.1f} "
        f"{a} {br[0]:.1f},{br[1]:.1f} "
        f"{a} {bl[0]:.1f},{bl[1]:.1f} "
        f"{a} {tl[0]:.1f},{tl[1]:.1f} Z"
    ), (sx, sy)


def overlap_points():
    """Label positions for the four two-way lenses, on the diagonals."""
    k = D * 1.16
    return {
        "passion": (CX - k, CY - k),
        "mission": (CX + k, CY - k),
        "profession": (CX - k, CY + k),
        "vocation": (CX + k, CY + k),
    }


# --- Text -----------------------------------------------------------------

def text_width(s, size):
    """Approximate rendered width. Caps and wide glyphs cost more than an
    average character, so weight them rather than assuming a uniform em."""
    w = 0.0
    for ch in s:
        if ch in "iljI.,:;'!|":
            w += 0.28
        elif ch in "mwMW":
            w += 0.90
        elif ch.isupper():
            w += 0.66
        else:
            w += 0.52
    return w * size


def wrap(s, size, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit(blocks, max_w, max_h, sizes):
    """Shrink the font until the wrapped block fits the space available.

    Returns (size, laid_out_lines). Falls back to the smallest size rather than
    failing -- a slightly cramped diagram beats no diagram.
    """
    for size in sizes:
        laid, total = [], 0.0
        for text, weight, scale, gap in blocks:
            s = size * scale
            lines = wrap(text, s, max_w)
            laid.append((lines, s, weight))
            total += len(lines) * s * 1.32 + gap
        if total <= max_h:
            return laid
    return laid


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_block(cx, cy_centre, laid):
    """Emit centred lines, vertically centred on cy_centre."""
    total = sum(len(l) * s * 1.32 for l, s, _ in laid)
    y = cy_centre - total / 2
    out = []
    for lines, size, weight in laid:
        for line in lines:
            y += size * 1.32
            out.append(
                f'<text x="{cx:.1f}" y="{y:.1f}" font-size="{size:.1f}" '
                f'font-weight="{weight}" text-anchor="middle" '
                f'fill="{INK if weight != "400" else MUTED}">{esc(line)}</text>'
            )
    return out


def build(data):
    headings = dict((k, h) for k, h, _, _, _ in QUADRANTS)
    headings.update(data.get("headings", {}))
    overlaps = dict(OVERLAP_DEFAULTS)
    overlaps.update(data.get("overlaps", {}))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
        f'width="{W:.0f}" height="{H:.0f}" font-family="{FONT}">',
        f'<rect width="{W:.0f}" height="{H:.0f}" fill="#ffffff"/>',
    ]

    name = data.get("name", "").strip()
    title = f"Ikigai — {name}" if name else "Ikigai"
    parts.append(
        f'<text x="{CX:.1f}" y="{TITLE_Y}" font-size="34" font-weight="700" '
        f'text-anchor="middle" fill="{INK}">{esc(title)}</text>'
    )
    if data.get("subtitle"):
        parts.append(
            f'<text x="{CX:.1f}" y="{SUBTITLE_Y}" font-size="17" '
            f'text-anchor="middle" fill="{MUTED}">{esc(data["subtitle"])}</text>'
        )

    # Circles. Multiply blending darkens the overlaps the way the classic
    # diagram does; browsers that ignore it still get sane alpha compositing.
    parts.append('<g style="mix-blend-mode:multiply">')
    for key, _, colour, position, _ in QUADRANTS:
        ccx, ccy = circle_centre(position)
        parts.append(
            f'<circle cx="{ccx:.1f}" cy="{ccy:.1f}" r="{R:.1f}" fill="{colour}" '
            f'fill-opacity="0.30" stroke="{colour}" stroke-width="2.5"/>'
        )
    parts.append("</g>")

    # Quadrant content in the outer caps.
    for key, _, _, position, max_w in QUADRANTS:
        tx, ty = text_anchor(position)
        items = data.get(key) or []
        if isinstance(items, str):
            items = [items]
        blocks = [(headings[key], "700", 1.0, 10.0)]
        for item in items[:5]:
            blocks.append((f"• {item}", "400", 0.80, 0.0))
        max_h = 250.0 if position in ("top", "bottom") else 300.0
        laid = fit(blocks, max_w, max_h, [23, 21, 19, 17, 15, 14])
        parts.extend(render_block(tx, ty, laid))

    # Two-way overlap labels.
    for key, (ox, oy) in overlap_points().items():
        parts.append(
            f'<text x="{ox:.1f}" y="{oy:.1f}" font-size="21" font-weight="700" '
            f'text-anchor="middle" fill="{INK}">{esc(overlaps[key])}</text>'
        )

    # Centre: white curved square holding the ikigai statement.
    path, (sx, sy) = centre_region_path()
    parts.append(
        f'<path d="{path}" fill="#ffffff" stroke="{INK}" stroke-width="2.5"/>'
    )
    statement = (data.get("ikigai") or "").strip()
    if statement:
        blocks = [("ikigai", "700", 1.0, 8.0), (statement, "400", 0.82, 0.0)]
        laid = fit(blocks, CENTRE_W, sy * 1.75, [22, 20, 18, 16, 15, 14, 13])
        parts.extend(render_block(CX, CY, laid))

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Render an Ikigai Venn diagram to SVG.")
    ap.add_argument("--input", help="JSON file; reads stdin when omitted")
    ap.add_argument("--output", required=True, help="path to write the .svg")
    args = ap.parse_args()

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    data = json.loads(raw)

    missing = [k for k, _, _, _, _ in QUADRANTS if not data.get(k)]
    if missing:
        print(f"warning: no content for {', '.join(missing)}", file=sys.stderr)
    if not (data.get("ikigai") or "").strip():
        print("warning: no centre statement -- the middle will be empty", file=sys.stderr)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(build(data))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
