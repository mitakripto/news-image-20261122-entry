#!/usr/bin/env python3
"""Draw the 22 November 2026 front page (1024x1024) for the make.fun
news-image-20261122 bounty.

Same pipeline as the 17/18/19 Nov entries: deterministic Pillow drawing,
fixed fonts, fixed layout, no randomness, no network. 60 stories across
7 regions, colour-coded by continent: a continent bar with counts under
the masthead, region-coloured number badges on every story, and matching
map pins. New this day, borrowed from the top-10 scan: a status tag on
every drawn story (CONFIRMED / REPORTED / CLAIM, with a legend) and a
"THE DAY IN UTC" timeline strip under the stats.

Run:  python3 draw.py   -> writes entry.png next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (240, 233, 214)
INK = (18, 28, 30)
GRAY = (74, 82, 80)
RED = (158, 43, 37)
TEAL_DARK = (14, 42, 51)
TEAL = (31, 111, 107)
GOLD = (201, 162, 39)
GOLD_LT = (226, 190, 96)
CREAM = (247, 242, 230)
SKY = (213, 228, 226)
WATER = (140, 178, 176)
CARD_BG = (233, 226, 200)
MAP_BG = (216, 230, 224)
MAP_DOT = (96, 128, 124)

# Continent colours (muted deco): badges, kickers, map pins, bar.
ASIA = TEAL
EUROPE = (70, 100, 140)
MIDDLE_EAST = (178, 102, 32)
N_AMERICA = RED
S_AMERICA = (90, 130, 80)
AFRICA = (146, 96, 48)
OCEANIA = (110, 90, 130)

# Status-tag colours: how sure the page is of each drawn story.
TAG_CONFIRMED = TEAL
TAG_REPORTED = MIDDLE_EAST
TAG_CLAIM = RED

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def SERIF_F(n):
    return ImageFont.truetype(SERIF, n)


def SERIF_B(n):
    return ImageFont.truetype(SERIFB, n)


def SANS_F(n):
    return ImageFont.truetype(SANS, n)


def SANS_B(n):
    return ImageFont.truetype(SANSB, n)


def wrap(draw, s, font, max_w):
    """Greedy word wrap; asserts no single word exceeds the width."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            assert draw.textlength(word, font=font) <= max_w, \
                f"word too wide: {word!r}"
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, font, fill=INK, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def diamond(draw, x, y, r, color):
    draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)],
                 fill=color)


def badge(draw, x, y, n, size, color=INK):
    """Black (or continent-coloured) stamp-square with a cream number:
    the Orwell numbering device, now colour-coded by continent."""
    draw.rectangle([x, y, x + size, y + size], fill=color)
    draw.rectangle([x + 1, y + 1, x + size - 1, y + size - 1],
                   outline=GOLD_LT, width=1)
    fnt = SANS_B(11 if size >= 20 else 8)
    text(draw, (x + size / 2, y + size / 2), str(n), fnt, CREAM,
         anchor="mm")


def tag_chip(draw, x_right, y_center, label, color, fsize=8):
    """Small solid status chip, right-aligned: CONFIRMED / REPORTED /
    CLAIM. Returns the chip's left edge so callers can keep clear."""
    fnt = SANS_B(fsize)
    tw = draw.textlength(label, font=fnt)
    w, h = tw + 10, 14
    x0 = x_right - w
    y0 = y_center - h // 2
    draw.rectangle([x0, y0, x_right, y0 + h], fill=color)
    text(draw, (x0 + w / 2, y_center), label, fnt, CREAM, anchor="mm")
    return x0


def kicker(draw, x, y, n, label, color, size=20, max_w=None, fsize=None):
    badge(draw, x, y, n, size, color)
    fnt = SANS_B(fsize if fsize else (12 if size >= 20 else 9))
    if max_w is not None:
        assert draw.textlength(label, font=fnt) <= max_w - size - 6, \
            f"kicker overflows: {label!r}"
    text(draw, (x + size + 6, y + size // 2), label, fnt, color, anchor="lm")


def draw_eye(draw, x, y, w=34, h=20):
    """One small watching eye for the masthead."""
    draw.ellipse([x, y, x + w, y + h], outline=GOLD, width=2, fill=CREAM)
    cx, cy = x + w // 2, y + h // 2
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=RED, width=2)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK)


def caption_bar(draw, x0, y1, x1, label):
    draw.rectangle([x0, y1 - 14, x1, y1], fill=INK)
    text(draw, ((x0 + x1) // 2, y1 - 7), label, SANS_B(8), GOLD_LT,
         anchor="mm")


def draw_capitol(draw, x0, y0, x1, y1):
    """The US Capitol at dusk, with the 258-seat figure in gold.
    Art area is 60px tall; the caption bar takes the bottom 14."""
    draw.rectangle([x0, y0, x1, y1], fill=(30, 58, 74))
    draw.ellipse([x0 + 8, y0 + 4, x0 + 28, y0 + 24], fill=GOLD)
    base = y1 - 14
    cx = (x0 + x1) // 2 - 30
    # Dome: drum, cupola, statue spike (top stays inside the art)
    draw.rectangle([cx - 26, base - 22, cx + 26, base], fill=CREAM)
    draw.pieslice([cx - 26, base - 38, cx + 26, base - 6], 180, 360,
                  fill=CREAM)
    draw.rectangle([cx - 4, base - 42, cx + 4, base - 38], fill=CREAM)
    draw.ellipse([cx - 2, base - 45, cx + 2, base - 42], fill=GOLD)
    # Wings and columns
    draw.rectangle([x0 + 14, base - 16, cx - 26, base], fill=(200, 192, 168))
    draw.rectangle([cx + 26, base - 16, x1 - 96, base], fill=(200, 192, 168))
    for px in range(cx - 20, cx + 21, 8):
        draw.line([px, base - 20, px, base - 4], fill=(30, 58, 74), width=2)
    text(draw, (x1 - 12, y0 + 2), "258", SERIF_B(30), GOLD_LT, anchor="ra")
    text(draw, (x1 - 12, y0 + 33), "SEATS", SANS_B(9), CREAM, anchor="ra")
    caption_bar(draw, x0, y1, x1, "WASHINGTON  \u00b7  258 SEATS")


def draw_tanker(draw, x0, y0, x1, y1):
    """A supertanker burning east of Hormuz: dusk sky, fire burst,
    mine dots in dark water. Art area is 60px tall; the caption bar
    takes the bottom 14, so the sea is a 10px strip above it."""
    draw.rectangle([x0, y0, x1, y1 - 14], fill=(224, 178, 120))
    draw.rectangle([x0, y1 - 24, x1, y1 - 14], fill=(16, 44, 54))
    for wx in range(10, (x1 - x0) - 10, 30):
        draw.line([x0 + wx, y1 - 19, x0 + wx + 16, y1 - 19],
                  fill=WATER, width=2)
    # Hull and superstructure, silhouetted; base sits on the caption
    hx0, hx1 = x0 + 30, x1 - 30
    hy = y1 - 14
    draw.polygon([(hx0, hy - 12), (hx1, hy - 12), (hx1 - 10, hy),
                  (hx0 + 10, hy)], fill=INK)
    draw.rectangle([hx1 - 52, hy - 26, hx1 - 28, hy - 12], fill=INK)
    draw.line([hx1 - 40, hy - 32, hx1 - 40, hy - 26], fill=INK, width=2)
    # Fire burst above the bow, touching the hull
    fx, fy = hx0 + 34, y0 + 22
    for r, col in ((10, (222, 120, 40)), (7, (240, 180, 60)),
                   (4, (252, 236, 180))):
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=col)
    for a in (200, 250, 290, 340):
        rad = math.radians(a)
        ex = fx + 14 * math.cos(rad)
        ey = fy + 9 * math.sin(rad)
        draw.line([fx, fy, ex, ey], fill=(222, 120, 40), width=2)
    # Smoke trailing up and to the left of the fire
    for sx, sy, r in ((fx - 12, fy - 10, 4), (fx - 18, fy - 15, 5)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(90, 90, 88))
    # Two naval mines in the water strip
    for mx in (x0 + 18, x1 - 18):
        my = y1 - 19
        draw.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=INK)
        for a in (45, 135, 225, 315):
            rad = math.radians(a)
            draw.line([mx, my, mx + 5 * math.cos(rad),
                       my + 5 * math.sin(rad)], fill=INK, width=1)
    caption_bar(draw, x0, y1, x1, "HORMUZ  \u00b7  DAY 130")


def draw_cop31(draw, x0, y0, x1, y1):
    """Antalya plenary: flags over a red NO DEAL stamp. Art area is
    60px tall; the caption bar takes the bottom 14."""
    draw.rectangle([x0, y0, x1, y1], fill=TEAL_DARK)
    # Row of small flags
    fw, gap = 26, 10
    total = 7 * fw + 6 * gap
    fx = x0 + ((x1 - x0) - total) // 2
    flag_cols = [(60, 59, 110), (222, 41, 16), (0, 57, 166),
                 (0, 122, 60), (255, 205, 0), (178, 34, 52),
                 (255, 255, 255)]
    for i, col in enumerate(flag_cols):
        bx = fx + i * (fw + gap)
        draw.rectangle([bx, y0 + 4, bx + fw, y0 + 15], fill=col)
    # Red NO DEAL stamp
    sx0, sx1 = x0 + 78, x1 - 78
    sy0, sy1 = y0 + 19, y1 - 17
    draw.rectangle([sx0, sy0, sx1, sy1], outline=RED, width=3)
    draw.rectangle([sx0 + 3, sy0 + 3, sx1 - 3, sy1 - 3], outline=RED,
                   width=1)
    text(draw, ((sx0 + sx1) // 2, (sy0 + sy1) // 2), "NO DEAL",
         SANS_B(15), (232, 90, 80), anchor="mm")
    caption_bar(draw, x0, y1, x1, "ANTALYA  \u00b7  COP31")


# --- small icons for the cards (30x30 glyphs) ---

def icon_scales(draw, x, y, s, color):
    cx = x + s // 2
    draw.line([cx, y + 4, cx, y + s - 4], fill=color, width=3)
    draw.line([cx - 11, y + 7, cx + 11, y + 7], fill=color, width=3)
    for px in (cx - 11, cx + 11):
        draw.line([px, y + 7, px - 5, y + 16], fill=color, width=2)
        draw.line([px, y + 7, px + 5, y + 16], fill=color, width=2)
        draw.arc([px - 5, y + 14, px + 5, y + 24], 0, 180, fill=color,
                 width=2)
    draw.line([cx - 8, y + s - 4, cx + 8, y + s - 4], fill=color, width=3)


def icon_missile(draw, x, y, s, color):
    draw.polygon([(x + 20, y + 4), (x + 26, y + 10), (x + 18, y + 20),
                  (x + 12, y + 14)], fill=color)
    draw.line([x + 12, y + 14, x + 6, y + 24], fill=color, width=3)
    draw.line([x + 6, y + 24, x + 4, y + 28], fill=RED, width=3)
    draw.line([x + 18, y + 20, x + 24, y + 24], fill=color, width=2)
    draw.line([x + 18, y + 20, x + 14, y + 26], fill=color, width=2)


def icon_pencil(draw, x, y, s, color):
    draw.polygon([(x + 8, y + 20), (x + 20, y + 8), (x + 24, y + 12),
                  (x + 12, y + 24)], fill=color)
    draw.polygon([(x + 8, y + 20), (x + 5, y + 25), (x + 12, y + 24)],
                 fill=RED)
    draw.line([x + 5, y + 25, x + 25, y + 25], fill=color, width=2)


def icon_tower(draw, x, y, s, color):
    cx = x + s // 2
    draw.rectangle([cx - 7, y + 8, cx + 7, y + s - 4], fill=color)
    draw.polygon([(cx - 7, y + 8), (cx, y + 2), (cx + 7, y + 8)], fill=color)
    for wy in range(y + 12, y + s - 6, 6):
        draw.rectangle([cx - 4, wy, cx - 1, wy + 2], fill=GOLD_LT)
        draw.rectangle([cx + 1, wy, cx + 4, wy + 2], fill=GOLD_LT)


def icon_ballot(draw, x, y, s, color):
    draw.rectangle([x + 5, y + 12, x + 25, y + 26], outline=color, width=2)
    draw.line([x + 11, y + 12, x + 19, y + 12], fill=color, width=2)
    draw.polygon([(x + 9, y + 5), (x + 15, y + 3), (x + 21, y + 5),
                  (x + 19, y + 12), (x + 11, y + 12)], fill=CARD_BG,
                 outline=color)
    draw.line([x + 9, y + 21, x + 13, y + 24], fill=RED, width=2)
    draw.line([x + 13, y + 24, x + 21, y + 15], fill=RED, width=2)


def icon_drone(draw, x, y, s, color):
    cx, cy = x + s // 2, y + s // 2
    draw.rectangle([cx - 5, cy - 4, cx + 5, cy + 4], fill=color)
    for dx, dy in ((-9, -8), (9, -8), (-9, 8), (9, 8)):
        draw.line([cx, cy, cx + dx, cy + dy], fill=color, width=2)
        draw.ellipse([cx + dx - 4, cy + dy - 2, cx + dx + 4, cy + dy + 2],
                     outline=color, width=2)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)


def icon_soccer(draw, x, y, s, color):
    cx, cy = x + s // 2, y + s // 2
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=color,
                 width=2)
    draw.polygon([(cx, cy - 5), (cx + 5, cy - 2), (cx + 3, cy + 4),
                  (cx - 3, cy + 4), (cx - 5, cy - 2)], fill=color)
    for a in (90, 162, 234, 306, 18):
        rad = math.radians(a)
        draw.line([cx + 5 * math.cos(rad), cy + 5 * math.sin(rad),
                   cx + 10 * math.cos(rad), cy + 10 * math.sin(rad)],
                  fill=color, width=1)


def icon_tennis(draw, x, y, s, color):
    cx, cy = x + s // 2, y + s // 2
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=color,
                 width=2)
    draw.arc([cx - 16, cy - 8, cx + 2, cy + 8], 270, 90, fill=color,
             width=2)
    draw.arc([cx - 2, cy - 8, cx + 16, cy + 8], 90, 270, fill=color,
             width=2)


def icon_plane(draw, x, y, s, color):
    draw.polygon([(x + 4, y + 18), (x + 24, y + 8), (x + 26, y + 11),
                  (x + 12, y + 20), (x + 10, y + 24), (x + 7, y + 22)],
                 fill=color)
    draw.polygon([(x + 14, y + 15), (x + 22, y + 17), (x + 22, y + 20),
                  (x + 13, y + 18)], fill=color)
    draw.line([x + 4, y + 26, x + 26, y + 26], fill=RED, width=2)
    draw.line([x + 8, y + 26, x + 6, y + 22], fill=RED, width=2)
    draw.line([x + 22, y + 26, x + 24, y + 22], fill=RED, width=2)


def icon_flame(draw, x, y, s, color):
    cx = x + s // 2
    draw.polygon([(cx, y + 3), (cx + 9, y + 16), (cx + 6, y + 24),
                  (cx - 6, y + 24), (cx - 9, y + 16)], fill=(222, 120, 40))
    draw.polygon([(cx, y + 10), (cx + 5, y + 18), (cx + 3, y + 23),
                  (cx - 3, y + 23), (cx - 5, y + 18)], fill=GOLD)
    draw.line([cx - 10, y + 26, cx + 10, y + 26], fill=color, width=2)


def _in_poly(lon, lat, poly):
    """Ray-casting point-in-polygon test for a lon/lat point."""
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = (x2 - x1) * (lat - y1) / (y2 - y1) + x1
            if lon < xin:
                inside = not inside
    return inside


# Simplified continent outlines (lon/lat rings) for a realistic
# dotted map: real coastlines, not blobs. Drawn from geography.
POLYS = [
    # North America, incl. Central America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
     (-135, 57), (-130, 54), (-125, 49), (-124, 42), (-120, 34),
     (-114, 29), (-110, 23), (-105, 20), (-97, 16), (-94, 17),
     (-90, 14), (-87, 13), (-83, 9), (-79, 9), (-81, 13),
     (-83, 16), (-87, 21), (-90, 21), (-91, 19), (-97, 26),
     (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32),
     (-76, 35), (-74, 40), (-70, 42), (-68, 44), (-65, 45),
     (-60, 47), (-65, 50), (-60, 52), (-64, 58), (-68, 58),
     (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69),
     (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 65), (-32, 68),
     (-22, 70), (-20, 76), (-30, 80), (-45, 80), (-58, 76),
     (-62, 70)],
    # South America
    [(-79, 9), (-75, 11), (-72, 12), (-64, 10), (-60, 8),
     (-52, 5), (-50, 0), (-44, -3), (-35, -8), (-35, -15),
     (-39, -22), (-48, -28), (-52, -32), (-58, -38), (-62, -41),
     (-65, -45), (-68, -50), (-69, -54), (-72, -54), (-73, -45),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-77, -12),
     (-81, -6), (-81, 0), (-80, 5)],
    # Europe, with Italy's boot suggested
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 50), (3, 53),
     (5, 58), (5, 62), (10, 64), (12, 66), (18, 69), (25, 71),
     (30, 70), (32, 66), (28, 61), (24, 58), (21, 55), (24, 52),
     (28, 50), (30, 46), (29, 44), (23, 40), (22, 37), (26, 38),
     (28, 41), (30, 42), (28, 45), (24, 46), (19, 46), (18, 42),
     (16, 40), (18, 39), (15, 38), (16, 41), (14, 42), (10, 44),
     (8, 44), (3, 42), (0, 39), (-2, 37), (-6, 36), (-9, 37)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 25), (-17, 15), (-16, 12),
     (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4),
     (9, -1), (12, -6), (13, -12), (12, -18), (14, -22),
     (16, -28), (18, -34), (20, -35), (26, -34), (28, -32),
     (32, -28), (35, -23), (36, -18), (35, -12), (40, -10),
     (40, -5), (42, -2), (46, 0), (51, 2), (51, 10), (44, 11),
     (40, 15), (38, 18), (35, 22), (32, 28), (30, 31), (25, 32),
     (20, 32), (15, 32), (10, 34), (5, 35), (0, 36)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
     (45, -25), (44, -20)],
    # Asia: Levant around to Chukotka, back along the Arctic coast
    [(30, 36), (35, 36), (36, 33), (42, 30), (48, 30), (50, 26),
     (54, 26), (57, 25), (61, 25), (66, 25), (70, 23), (72, 20),
     (75, 15), (77, 8), (80, 10), (80, 16), (84, 19), (88, 22),
     (91, 22), (92, 16), (94, 17), (97, 16), (98, 10), (100, 8),
     (103, 1), (104, 8), (105, 10), (109, 13), (109, 15),
     (106, 20), (108, 22), (110, 21), (114, 22), (118, 25),
     (120, 28), (122, 32), (120, 35), (122, 38), (126, 40),
     (130, 42), (135, 44), (140, 48), (142, 54), (140, 60),
     (142, 63), (145, 68), (150, 70), (158, 70), (165, 68),
     (170, 67), (178, 65), (178, 68), (170, 70), (160, 70),
     (150, 72), (140, 72), (130, 72), (120, 73), (110, 74),
     (100, 77), (90, 75), (80, 73), (72, 72), (68, 69),
     (60, 69), (55, 68), (50, 68), (45, 67), (40, 66),
     (35, 65), (32, 62), (30, 58), (28, 55), (30, 50),
     (32, 46), (30, 42), (35, 42), (38, 40), (40, 38),
     (35, 38), (32, 36)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 36),
     (141, 39), (141, 42), (143, 43), (145, 44), (142, 45),
     (140, 40), (138, 37), (135, 34), (132, 33)],
    # Philippines
    [(117, 16), (120, 18), (122, 18), (122, 14), (124, 12),
     (126, 10), (126, 6), (124, 6), (122, 8), (120, 10),
     (119, 12), (118, 14)],
    # Sumatra, Java, Borneo, New Guinea
    [(95, 5), (100, 0), (105, -5), (106, -6), (103, -4), (99, 2)],
    [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8)],
    [(109, 1), (113, 4), (118, 2), (119, -2), (117, -4), (112, -3)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -10),
     (147, -9), (142, -8), (136, -6), (131, -3)],
    # Australia
    [(114, -22), (114, -28), (115, -33), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (151, -24),
     (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
     (135, -12), (132, -11), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # New Zealand
    [(167, -45), (170, -42), (173, -39), (175, -38), (178, -38),
     (175, -41), (172, -44)],
]


def draw_map(draw, x0, y0, x1, y1, spots):
    draw.rectangle([x0, y0, x1, y1], fill=MAP_BG)
    draw.rectangle([x0, y0, x1, y1], outline=GOLD, width=2)
    # The panel is nearly square but the world is wide: stretching the
    # map to fill the panel pulled every continent tall. Draw it at the
    # reference front page's dotted-region ratio, 1.71:1, letterboxed
    # and centred vertically in the panel instead.
    map_w = x1 - x0
    map_h = map_w / 1.71
    mx0, mx1 = x0, x1
    my0 = y0 + (y1 - y0 - map_h) / 2
    my1 = my0 + map_h

    def to_xy(lon, lat):
        return (mx0 + (lon + 180) / 360 * (mx1 - mx0),
                my0 + (75 - lat) / 135 * (my1 - my0))

    step = 5
    yy = my0 + 3
    while yy < my1 - 2:
        xx = mx0 + 3
        while xx < mx1 - 2:
            lon = (xx - mx0) / (mx1 - mx0) * 360 - 180
            lat = 75 - (yy - my0) / (my1 - my0) * 135
            for poly in POLYS:
                if _in_poly(lon, lat, poly):
                    draw.ellipse([xx - 1.3, yy - 1.3, xx + 1.3, yy + 1.3],
                                 fill=MAP_DOT)
                    break
            xx += step
        yy += step
    for n, lon, lat, dx, dy, color in spots:
        px, py = to_xy(lon, lat)
        px += dx
        py += dy
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=color,
                     outline=CREAM, width=1)
        text(draw, (px, py), str(n), SANS_B(8), CREAM, anchor="mm")
    text(draw, ((x0 + x1) // 2, y1 - 10),
         "Dots mark stories 1\u201313; pin colour = continent.", SANS_F(9),
         GRAY, anchor="mm")


def lead(draw, x, y, w, n, kick, color, headline, sub, art, tag, tag_color):
    art(draw, x, y, x + w, y + 60)
    draw.rectangle([x, y, x + w, y + 60], outline=GOLD, width=1)
    chip_left = tag_chip(draw, x + w, y + 78, tag, tag_color)
    kicker(draw, x, y + 68, n, kick, color, max_w=chip_left - x - 4)
    lines = wrap(draw, headline, SERIF_B(20), w)
    assert len(lines) <= 3, f"lead headline overflows: {headline!r}"
    yy = y + 94
    for line in lines:
        text(draw, (x, yy), line, SERIF_B(20))
        yy += 24
    slines = wrap(draw, sub, SANS_F(12.5), w)
    assert len(slines) <= 3, f"lead sub overflows: {sub!r}"
    for line in slines:
        text(draw, (x, yy + 3), line, SANS_F(12.5), GRAY)
        yy += 16


def card(draw, x, y, w, n, region, color, headline, sub, icon, tag,
         tag_color):
    draw.rectangle([x, y, x + w, y + 30], fill=CARD_BG)
    draw.rectangle([x, y + 30, x + w, y + 32], fill=GOLD)
    icon(draw, x + 3, y, 30, color)
    chip_left = tag_chip(draw, x + w - 3, y + 15, tag, tag_color, fsize=7)
    kicker(draw, x + 36, y + 7, n, region, color, size=16,
           max_w=chip_left - (x + 36) - 4, fsize=8)
    lines = wrap(draw, headline, SERIF_B(14), w)
    assert len(lines) <= 2, f"card headline overflows: {headline!r}"
    yy = y + 38
    for line in lines:
        text(draw, (x, yy), line, SERIF_B(14))
        yy += 17
    slines = wrap(draw, sub, SANS_F(10), w)
    assert len(slines) <= 2, f"card sub overflows: {sub!r}"
    for line in slines:
        text(draw, (x, yy + 2), line, SANS_F(10), GRAY)
        yy += 13


def numbers_strip(draw, x, y, w, stats):
    text(draw, (x, y + 2), "BY THE", SANS_B(12), RED)
    text(draw, (x, y + 16), "NUMBERS", SANS_B(12), RED)
    col_w = (w - 92) // 6
    for i, (num, cap) in enumerate(stats):
        cx = x + 92 + i * col_w
        if i:
            draw.line([cx - 8, y, cx - 8, y + 36], fill=GOLD, width=1)
        text(draw, (cx, y), num, SERIF_B(22), INK)
        lines = wrap(draw, cap, SANS_F(9.5), col_w - 12)
        assert len(lines) <= 1, f"stat caption overflows: {cap!r}"
        yy = y + 26
        for line in lines:
            text(draw, (cx, yy), line, SANS_F(9.5), GRAY)
            yy += 12


def timeline_strip(draw, x, y, w, beats):
    """One-line UTC timeline: the day's arc, dawn to night."""
    draw.line([x, y, x + w, y], fill=GOLD, width=1)
    draw.line([x, y + 18, x + w, y + 18], fill=GOLD, width=1)
    label = "THE DAY IN UTC  "
    lfnt, bfnt = SANS_B(10), SANS_F(9.5)
    text(draw, (x, y + 9), label, lfnt, RED, anchor="lm")
    lx = x + draw.textlength(label, font=lfnt)
    body = "  \u00b7  ".join(f"{t}  {s}" for t, s in beats)
    assert draw.textlength(body, font=bfnt) <= w - (lx - x), \
        f"timeline overflows: {body!r}"
    text(draw, (lx, y + 9), body, bfnt, INK, anchor="lm")


def continent_bar(draw, x0, y0, x1, y1, segments):
    """Colour bar under the masthead: one segment per continent with its
    story count. The bar is the legend for badges and map pins."""
    n = len(segments)
    total = x1 - x0
    for i, (label, count, color) in enumerate(segments):
        sx0 = x0 + i * total // n
        sx1 = x0 + (i + 1) * total // n
        draw.rectangle([sx0, y0, sx1, y1], fill=color)
        if i:
            draw.line([sx0, y0, sx0, y1], fill=PAPER, width=2)
        text(draw, ((sx0 + sx1) // 2, (y0 + y1) // 2),
             f"{label} \u00b7 {count}", SANS_B(11), CREAM, anchor="mm")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- art-deco frame: gold outer rule, ink inner rule, stepped corners ---
    d.rectangle([5, 5, W - 6, H - 6], outline=GOLD, width=3)
    d.rectangle([11, 11, W - 12, H - 12], outline=INK, width=1)
    # Stepped corners on the top only: the bottom ones crossed the footer.
    for cx, cy, sx, sy in ((11, 11, 1, 1), (W - 12, 11, -1, 1)):
        for k in range(3):
            o = 18 + k * 6
            d.line([cx + sx * o, cy, cx + sx * o, cy + sy * 10],
                   fill=GOLD, width=2)
            d.line([cx, cy + sy * o, cx + sx * 10, cy + sy * o],
                   fill=GOLD, width=2)

    # --- masthead: deep-sea teal, gold lettering, one watching eye ---
    d.rectangle([14, 14, 1010, 124], fill=TEAL_DARK)
    draw_eye(d, 512 - 17, 18)
    text(d, (24, 22), "THE DAY IN WORLD NEWS", SANS_B(13), GOLD_LT)
    text(d, (1000, 22), "60 STORIES  \u00b7  7 REGIONS  \u00b7  ONE PAGE",
         SANS_B(13), GOLD_LT, anchor="ra")
    date = "Sunday 22 November 2026"
    dfnt = SERIF_B(54)
    assert d.textlength(date, font=dfnt) <= 976, "masthead date too wide"
    text(d, (24, 42), date, dfnt, CREAM)
    text(d, (24, 100),
         "Every story on this page happened, or was first reported, on this day.",
         SERIF_F(16), CREAM)
    diamond(d, 990, 106, 5, GOLD)
    d.rectangle([14, 124, 1010, 126], fill=GOLD)
    d.rectangle([14, 127, 1010, 129], fill=RED)

    # --- continent bar: colour-coding legend with counts ---
    continent_bar(d, 14, 132, 1010, 156, [
        ("ASIA", 11, ASIA),
        ("EUROPE", 13, EUROPE),
        ("MIDDLE EAST", 8, MIDDLE_EAST),
        ("N. AMERICA", 14, N_AMERICA),
        ("AFRICA", 8, AFRICA),
        ("OCEANIA", 4, OCEANIA),
        ("S. AMERICA", 2, S_AMERICA),
    ])

    # --- by the numbers ---
    numbers_strip(d, 24, 160, 976, [
        ("258", "House seats, Democrats"),
        ("$450m", "Skubal's Mets deal"),
        ("1,600+", "Delta flights delayed"),
        ("186", "Drones over Ukraine"),
        ("130 DAYS", "Of Hormuz blockade"),
        ("44 HRS", "COP31 overtime record"),
    ])

    # --- the day in UTC ---
    timeline_strip(d, 24, 198, 976, [
        ("01:00", "HK polls open"),
        ("08:07", "186 drones, 161 downed"),
        ("16:00", "COP31: no deal"),
        ("17:25", "Tankers hit mines"),
        ("18:20", "Liverpool 4\u20130 Utd"),
        ("20:43", "Alcaraz wins in Turin"),
    ])

    # --- top row: three illustrated leads ---
    lead(d, 24, 222, 317, 1, "N. AMERICA  \u00b7  POLITICS", N_AMERICA,
         "Democrats win 258 House seats, biggest majority since 1992",
         "North Carolina recount: Hubbard beats 11-term Foxx by 330 "
         "votes; Foxx concedes. Full control of Congress from Jan 3.",
         draw_capitol, "CONFIRMED", TAG_CONFIRMED)
    lead(d, 353, 222, 317, 2, "MIDDLE EAST  \u00b7  WAR", MIDDLE_EAST,
         "Iran says two supertankers hit mines near Hormuz",
         "IRGC navy: both vessels caught fire east of the Strait after "
         "switching off detection systems. No ships named, no outside "
         "confirmation.", draw_tanker, "CLAIM", TAG_CLAIM)
    lead(d, 682, 222, 317, 3, "EUROPE  \u00b7  CLIMATE", EUROPE,
         "COP31 collapses with no deal",
         "Antalya ends 44 hours into overtime \u2014 the longest summit "
         "on record \u2014 after the EU and 130+ countries reject a "
         "text with no fossil fuels.", draw_cop31, "CONFIRMED",
         TAG_CONFIRMED)
    d.line([24, 444, 1000, 444], fill=INK, width=2)

    # --- middle rows: ten cards, five per row ---
    xs = [24, 221, 418, 615, 812]
    row1 = [
        (4, "ASIA", ASIA,
         "Hong Kong poll: record 98.79% turnout",
         "856 candidates for 723 seats; 5,640 voters cast ballots.",
         icon_ballot, "CONFIRMED", TAG_CONFIRMED),
        (5, "AFRICA", AFRICA,
         "Ukraine drones hit Russian corvette",
         "Suspected sea drones strike the Merkury at Benghazi naval base.",
         icon_missile, "REPORTED", TAG_REPORTED),
        (6, "EUROPE", EUROPE,
         "186 drones over Ukraine in the night",
         "161 downed or jammed; Dymer block hit, 14 missing in the rubble.",
         icon_drone, "CONFIRMED", TAG_CONFIRMED),
        (7, "ASIA", ASIA,
         "Seoul minister quits over AI cheating",
         "Education chief Choi resigns after a Suneung top scorer confesses.",
         icon_pencil, "CONFIRMED", TAG_CONFIRMED),
        (8, "EUROPE", EUROPE,
         "Liverpool rout 10-man Man Utd 4\u20130",
         "Yoro sent off after 8'; Pochettino's debut unravels at Anfield.",
         icon_soccer, "CONFIRMED", TAG_CONFIRMED),
    ]
    for (n, region, col, head, sub, icon, tag, tcol), x in zip(row1, xs):
        card(d, x, 448, 187, n, region, col, head, sub, icon, tag, tcol)
    row2 = [
        (9, "EUROPE", EUROPE,
         "Alcaraz wins first ATP Finals title",
         "Beats Zverev 6\u20132, 7\u20136(7) in Turin; a perfect 5\u20130 week.",
         icon_tennis, "CONFIRMED", TAG_CONFIRMED),
        (10, "N. AMERICA", N_AMERICA,
         "Delta outage delays 1,600+ flights",
         "System failure grounds Atlanta flights; crews count by hand.",
         icon_plane, "CONFIRMED", TAG_CONFIRMED),
        (11, "AFRICA", AFRICA,
         "Sudan drones kill 4, hit UN building",
         "Omdurman home strike kills 3; a child killed south of Khartoum.",
         icon_tower, "REPORTED", TAG_REPORTED),
        (12, "ASIA", ASIA,
         "Candy factory fire: 3 dead, 36 missing",
         "Serang sweets plant blaze, first reported Sunday; 15 rescued alive.",
         icon_flame, "REPORTED", TAG_REPORTED),
        (13, "N. AMERICA", N_AMERICA,
         "ICE detains father and daughter",
         "Masked agents board a Seattle flight; pair bound for a baptism.",
         icon_scales, "REPORTED", TAG_REPORTED),
    ]
    for (n, region, col, head, sub, icon, tag, tcol), x in zip(row2, xs):
        card(d, x, 552, 187, n, region, col, head, sub, icon, tag, tcol)
    d.line([24, 656, 1000, 656], fill=INK, width=2)

    # --- bottom left: where the news happened ---
    text(d, (24, 660), "WHERE THE NEWS HAPPENED", SANS_B(13), INK)
    draw_map(d, 24, 678, 300, 928, [
        (1, -77, 38.9, 6, -6, N_AMERICA),
        (2, 56.5, 26.6, 0, 0, MIDDLE_EAST),
        (3, 30.7, 36.9, 8, -4, EUROPE),
        (4, 114.2, 22.3, 0, 0, ASIA),
        (5, 20.1, 32.1, -8, 4, AFRICA),
        (6, 30.3, 50.8, 0, -6, EUROPE),
        (7, 127, 37.5, 0, 0, ASIA),
        (8, -2.96, 53.4, -6, -4, EUROPE),
        (9, 7.7, 45.1, 6, 4, EUROPE),
        (10, -84.4, 33.7, -6, 6, N_AMERICA),
        (11, 32.5, 15.6, 0, 0, AFRICA),
        (12, 106.1, -6.1, 0, 0, ASIA),
        (13, -122.3, 47.6, 0, 0, N_AMERICA),
    ])

    # --- bottom right: 47 more stories, numbered, colour-coded ---
    text(d, (312, 660),
         "ALSO ON SUNDAY 22 NOVEMBER  \u2014  47 MORE STORIES",
         SANS_B(13), INK)
    briefs = [
        (14, "Thailand \u2014 Royal insult verdict kept.", ASIA),
        (15, "Nepal \u2014 PM Shah visits New Delhi.", ASIA),
        (16, "China \u2014 Margin rules eased to 80%.", ASIA),
        (17, "Nvidia \u2014 US presses on China chips.", ASIA),
        (18, "China \u2014 Spy drive for AI chips: NYT.", ASIA),
        (19, "China \u2014 CXMT, YMTC gain ground.", ASIA),
        (20, "Taiwan \u2014 Warns Canada on China ties.", ASIA),
        (21, "Japan \u2014 Carmakers to share parts.", ASIA),
        (22, "Italy \u2014 Ex-police chief found dead.", EUROPE),
        (23, "Poland \u2014 Friday jets were Kh-101s.", EUROPE),
        (24, "Finland \u2014 Sparta II still burning.", EUROPE),
        (25, "Poland \u2014 Russia 'tried to kill rapper'.", EUROPE),
        (26, "Europe \u2014 Cost protests, third day.", EUROPE),
        (27, "UK \u2014 May 'aghast' at EU plans.", EUROPE),
        (28, "UK \u2014 Next fighter may be last crewed.", EUROPE),
        (29, "Germany \u2014 Arrest call for IDF soldier.", EUROPE),
        (30, "Italy \u2014 Paolo Bulgari dies at 89.", EUROPE),
        (31, "Iran \u2014 New missile city unveiled.", MIDDLE_EAST),
        (32, "Yemen \u2014 Houthis claim refinery hit.", MIDDLE_EAST),
        (33, "Bahrain \u2014 Iran claims US base strikes.", MIDDLE_EAST),
        (34, "West Bank \u2014 Settlers burn 12 vehicles.", MIDDLE_EAST),
        (35, "Israel \u2014 Unity government talks open.", MIDDLE_EAST),
        (36, "Gaza \u2014 Food-van dead 'not our team'.", MIDDLE_EAST),
        (37, "Iran \u2014 Pezeshkian cites 'silent war'.", MIDDLE_EAST),
        (38, "Baseball \u2014 Skubal's $450m Mets deal.", N_AMERICA),
        (39, "NFL \u2014 49ers beat Vikings 35\u201310.", N_AMERICA),
        (40, "Miley Cyrus marries in Palm Springs.", N_AMERICA),
        (41, "Film \u2014 Hunger Games tops box office.", N_AMERICA),
        (42, "US courts \u2014 Pregnancy law voided.", N_AMERICA),
        (43, "Cyber \u2014 FBI probes NCIC hack.", N_AMERICA),
        (44, "US \u2014 Army to detonate lead azide.", N_AMERICA),
        (45, "US \u2014 Jeffries vows stock-trading ban.", N_AMERICA),
        (46, "US \u2014 Bessent warns Fed on tightening.", N_AMERICA),
        (47, "US \u2014 Schumer faces leadership fight.", N_AMERICA),
        (48, "Markets \u2014 Bitcoin back above $61,000.", N_AMERICA),
        (49, "Libya \u2014 Blast at Benghazi naval base.", AFRICA),
        (50, "Nigeria \u2014 Boat toll rises to 24.", AFRICA),
        (51, "S. Sudan \u2014 Rebels kill 15+ civilians.", AFRICA),
        (52, "DRC \u2014 Fighting disrupts Ebola fight.", AFRICA),
        (53, "Botswana \u2014 Visa-free pledge for Africa.", AFRICA),
        (54, "S. Africa \u2014 Mlambo-Ngcuka dies at 71.", AFRICA),
        (55, "Australia \u2014 Fred Nile dies at 92.", OCEANIA),
        (56, "Australia \u2014 US\u2013China gap narrowest.", OCEANIA),
        (57, "Australia \u2014 AI a security priority.", OCEANIA),
        (58, "Cricket \u2014 India set NZ Test record.", OCEANIA),
        (59, "Peru \u2014 Quake: 1 dead, 850 displaced.", S_AMERICA),
        (60, "Brazil \u2014 Storm toll rises to 5.", S_AMERICA),
    ]
    assert len(briefs) == 47, f"expected 47 briefs, got {len(briefs)}"
    bfnt = SANS_F(10)
    for i, (n, s, col) in enumerate(briefs):
        col_i = i // 16
        row = i % 16
        bx = 312 + col_i * 229
        by = 678 + row * 16
        assert d.textlength(s, font=bfnt) <= 205, f"brief too wide: {s!r}"
        badge(d, bx, by, n, size=12, color=col)
        text(d, (bx + 17, by), s, bfnt)

    # --- date check: what was deliberately left out ---
    d.rectangle([24, 932, 1000, 976], outline=RED, width=2)
    text(d, (32, 938), "DATE CHECK \u2014 NOT SUNDAY NEWS", SANS_B(11), RED)
    text(d, (992, 938),
         "TAGS: CONFIRMED = 2+ outlets \u00b7 REPORTED = one outlet \u00b7 "
         "CLAIM = one side's account", SANS_F(9), GRAY, anchor="ra")
    text(d, (32, 954),
         "Left out on purpose: 'El Chapo Isidro' captured (Fri) \u00b7 "
         "Geneva AI-weapons talks (Sat) \u00b7 BepiColombo Mercury orbit "
         "(Sat) \u00b7 EU\u2013Indonesia deal (Sat)", SANS_F(10), INK)
    text(d, (32, 968),
         "England 37\u201312 All Blacks (Sat) \u00b7 Wembanyama 50 pts "
         "(Sat) \u00b7 KC Current NWSL title (Sat) \u00b7 Verstappen Las "
         "Vegas GP (Sat night) \u00b7 400-drone barrage (Thu\u2013Fri) \u00b7 "
         "148-drone night (Fri\u2013Sat)", SANS_F(10), INK)

    # --- footer ---
    d.line([24, 982, 1000, 982], fill=INK, width=1)
    text(d, (24, 986),
         "Every story on this page happened, or was first reported, on "
         "Sunday 22 November 2026. Claims are attributed, not stated as "
         "fact. Wires read to 14:30 UTC, Mon 23 Nov 2026.", SANS_F(10), GRAY)
    text(d, (24, 1000),
         "Sources: Reuters, AP, BBC, CNN, AFP, SCMP, UN, COP31, Ukrainian "
         "Air Force. Original drawings.", SANS_F(10), GRAY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
