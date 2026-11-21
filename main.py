#!/usr/bin/env python3
"""Render '21 November 2026 in One Picture' — a 1024x1024 broadsheet-style
news infographic. Pure Pillow, fully deterministic: same code, same bytes.

News verified 2026-11-21 (UTC) against AP, Reuters, AFP, Al Jazeera,
Scientific American, The Hindu and The Times.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 243, 234)   # warm newsprint
INK = (24, 24, 22)
RED = (178, 34, 28)
DARK = (31, 41, 55)       # slate panel
GREY = (96, 96, 90)
LIGHT_GREY = (214, 210, 200)
GOLD = (176, 132, 34)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

# ---------------------------------------------------------------- stories
HEADLINE = {
    "kicker": "NATO ON EDGE",
    "title": ["RUSSIAN MISSILES", "LAND IN POLAND"],
    "deck": ("Tusk calls it a deliberate provocation as NATO jets scramble "
             "\u2014 a Kh-101 cruise missile crashes 60 km from the border. "
             "No one hurt."),
}

SECONDARY = [
    {
        "tag": "DENMARK",
        "color": RED,
        "title": "EXPELLED OVER RAPPER HIT PLOT",
        "body": ("Copenhagen expels Russia's defence attach\u00e9: its spies "
                 "say Moscow plotted to kill rapper Kyivstoner."),
    },
    {
        "tag": "SCIENCE",
        "color": (34, 110, 72),
        "title": "CLAUDE 'CRACKS' MATHS' GREATEST RIDDLE",
        "body": ("Anthropic's Alp\u00f6ge claims a proof of the 167-year-old "
                 "Riemann hypothesis; independent mathematicians call it "
                 "\u2018almost certainly\u2019 true."),
    },
    {
        "tag": "WASHINGTON",
        "color": (28, 68, 140),
        "title": "TRUMP FLOATS MILLER FOR 2028",
        "body": ("\u2018Do you wanna run for president?\u2019 Trump asks new "
                 "chief of staff Stephen Miller \u2014 as Vance and Rubio "
                 "look on."),
    },
    {
        "tag": "BRAZIL",
        "color": GOLD,
        "title": "BOLSONARO IN HOSPITAL",
        "body": ("Former president Jair Bolsonaro is hospitalised with "
                 "abdominal pain, his aides say."),
    },
]

ALSO_TODAY = [
    "US court jails Nikhil Gupta 19\u00bd years over Sikh murder plot",
    "Fresh arson attacks rock Bangladesh amid unrest",
    "Europe's cost-of-living protests spread",
    "US sanctions four Iranians over oil revenues",
]

FOOTER_SOURCES = ("Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 Al Jazeera \u00b7 "
                  "Scientific American \u00b7 The Hindu")
FOOTER_CREDIT = "Rendered by code for make.fun news-image-20261121"


# ---------------------------------------------------------------- helpers
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_center(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def rule(draw, x0, x1, y, fill=INK, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 48  # margin

    # ---- masthead ------------------------------------------------------
    rule(d, m, W - m, 30, width=4)
    draw_center(d, W // 2, 42, "THE WORLD IN ONE PICTURE", SERIF_B(40), INK)
    rule(d, m, W - m, 98, width=2)
    d.text((m, 106), "SATURDAY \u00b7 21 NOVEMBER 2026", font=SANS_B(19), fill=INK)
    right = "No. 21 \u00b7 WORLD NEWS"
    d.text((W - m - d.textlength(right, font=SANS_B(19)), 106), right,
           font=SANS_B(19), fill=GREY)
    rule(d, m, W - m, 134, width=4)

    # ---- headline ------------------------------------------------------
    y = 150
    # kicker chip
    kick = HEADLINE["kicker"]
    kf = SANS_B(21)
    kw = d.textlength(kick, font=kf) + 28
    d.rectangle([m, y, m + kw, y + 34], fill=RED)
    d.text((m + 14, y + 5), kick, font=kf, fill=(255, 255, 255))
    y += 46
    for line in HEADLINE["title"]:
        d.text((m, y), line, font=SERIF_B(70), fill=INK)
        y += 74
    y += 4
    deck_lines = wrap(d, HEADLINE["deck"], SERIF(24), W - 2 * m)
    for line in deck_lines:
        d.text((m, y), line, font=SERIF(24), fill=(58, 58, 54))
        y += 31
    y += 12
    rule(d, m, W - m, y, width=3)
    y += 14

    # ---- 2x2 secondary grid (row heights measured, never overlapping) ---
    col_w = (W - 2 * m - 28) // 2

    def cell_height(s):
        size = 28
        while size > 22:
            if len(wrap(d, s["title"], SANS_B(size), col_w)) <= 2:
                break
            size -= 2
        title_lines = wrap(d, s["title"], SANS_B(size), col_w)
        body_lines = wrap(d, s["body"], SANS(19), col_w)
        return 32 + len(title_lines) * (size + 5) + 4 + len(body_lines) * 25, size

    heights = [cell_height(s) for s in SECONDARY]
    hh = [h for h, _ in heights]
    grid_top = y
    row_tops = [grid_top, grid_top + max(hh[0], hh[1]) + 14]
    for idx, s in enumerate(SECONDARY):
        cx = m + (idx % 2) * (col_w + 28)
        cy = row_tops[idx // 2]
        _, size = heights[idx]
        # tag
        d.text((cx, cy), s["tag"], font=SANS_B(19), fill=s["color"])
        d.line([(cx, cy + 30), (cx + col_w, cy + 30)], fill=LIGHT_GREY, width=2)
        # title
        tfnt = SANS_B(size)
        ty = cy + 42
        for line in wrap(d, s["title"], tfnt, col_w):
            d.text((cx, ty), line, font=tfnt, fill=INK)
            ty += size + 6
        # body
        bf = SANS(19)
        by = ty + 4
        for line in wrap(d, s["body"], bf, col_w):
            d.text((cx, by), line, font=bf, fill=(74, 74, 70))
            by += 25

    y = row_tops[1] + max(hh[2], hh[3]) + 10
    rule(d, m, W - m, y, width=3)
    y += 10

    # ---- also today ----------------------------------------------------
    d.text((m, y), "ALSO TODAY", font=SANS_B(21), fill=RED)
    y += 28
    af = SANS(19)
    for item in ALSO_TODAY:
        d.text((m, y), "\u25aa", font=SANS_B(19), fill=RED)
        d.text((m + 26, y), item, font=af, fill=INK)
        y += 23
    y += 6
    rule(d, m, W - m, y, width=2)

    # ---- footer ---------------------------------------------------------
    fy = y + 8
    d.text((m, fy), FOOTER_SOURCES, font=SANS(15), fill=GREY)
    d.text((m, fy + 18), FOOTER_CREDIT, font=SANS(15), fill=GREY)
    print(f"layout: grid_top={grid_top} row2={row_tops[1]} grid_bottom={y} "
          f"footer_bottom={fy + 34}")

    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {img.size}")


if __name__ == "__main__":
    render()
