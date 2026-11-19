#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news image (1024x1024 PNG).

Broadsheet layout: a navy masthead with the date, then six story panels in
a 2x3 grid, one per verified story of the day, each with a simple geometric
icon, a region tag, a short headline and one factual line. Flat colours only,
so the file stays small and every word stays legible when the image is shrunk.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (246, 241, 231)
NAVY = (20, 38, 62)
NAVY_LIGHT = (168, 192, 220)
INK = (20, 38, 62)
GREY = (74, 85, 104)
CARD = (255, 255, 255)
BORDER = (216, 210, 196)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, size, max_w):
    """Largest font size at or below `size` that fits `max_w`."""
    while size > 12:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, 12)


def wrap(draw, text, f, max_w, max_lines=3):
    """Split text into lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:max_lines]


# --- icons: simple geometric drawings, one per story -----------------------

def icon_drone(d, x, y, s, color):
    # quadcopter: body, arms, four rotors
    cx, cy = x + s // 2, y + s // 2
    d.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], fill=color)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + dx * 34, cy + dy * 30
        d.line([(cx, cy), (px, py)], fill=color, width=5)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=color)
        d.line([(px - 20, py), (px + 20, py)], fill=color, width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))


def icon_bridge_broken(d, x, y, s, color):
    # deck with a collapsed middle span, two towers, water
    d.line([(x, y + 56), (x + 34, y + 56)], fill=color, width=6)
    d.line([(x + s - 34, y + 56), (x + s, y + 56)], fill=color, width=6)
    d.line([(x + 34, y + 56), (x + s // 2, y + 82)], fill=color, width=6)
    d.line([(x + s // 2, y + 82), (x + s - 34, y + 56)], fill=color, width=6)
    d.rectangle([x + 14, y + 12, x + 22, y + 56], fill=color)
    d.rectangle([x + s - 22, y + 12, x + s - 14, y + 56], fill=color)
    d.line([(x + 18, y + 12), (x + s // 2, y + 56)], fill=color, width=3)
    d.line([(x + s - 18, y + 12), (x + s // 2, y + 56)], fill=color, width=3)
    for wy in (92, 102):
        d.line([(x, y + wy), (x + s, y + wy)], fill=color, width=3)


def icon_summit(d, x, y, s, color):
    # three flags over a table with three seats
    flags = [(200, 60, 50), (40, 90, 160), (180, 140, 40)]
    for i, fc in enumerate(flags):
        px = x + 14 + i * 34
        d.line([(px, y + 12), (px, y + 66)], fill=color, width=4)
        d.polygon([(px, y + 12), (px + 26, y + 20), (px, y + 28)], fill=fc)
    d.rectangle([x + 6, y + 72, x + s - 6, y + 80], fill=color)
    for i in range(3):
        cx = x + 26 + i * 34
        d.ellipse([cx - 8, y + 84, cx + 8, y + 100], fill=color)


def icon_ballot(d, x, y, s, color):
    # ballot box with a slot and a checked paper
    d.rectangle([x + 14, y + 52, x + s - 14, y + 100], fill=color)
    d.rectangle([x + 34, y + 60, x + s - 34, y + 66], fill=(255, 255, 255))
    d.polygon([(x + 30, y + 52), (x + 48, y + 16), (x + 78, y + 16),
               (x + 64, y + 52)], fill=(255, 255, 255), outline=color)
    d.line([(x + 38, y + 34), (x + 46, y + 42), (x + 60, y + 24)],
           fill=(39, 103, 73), width=5)


def icon_virus(d, x, y, s, color):
    # spiked disc with a cross inside
    cx, cy, r = x + s // 2, y + s // 2 - 4, 32
    for k in range(8):
        a = math.pi * k / 4
        d.line([(cx + int(r * 0.9 * math.cos(a)), cy + int(r * 0.9 * math.sin(a))),
                (cx + int((r + 14) * math.cos(a)), cy + int((r + 14) * math.sin(a)))],
               fill=color, width=5)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.rectangle([cx - 5, cy - 16, cx + 5, cy + 16], fill=(255, 255, 255))
    d.rectangle([cx - 16, cy - 5, cx + 16, cy + 5], fill=(255, 255, 255))


def icon_cyclone(d, x, y, s, color):
    # spiral storm: concentric arcs tightening to the eye
    cx, cy = x + s // 2, y + s // 2
    for i, r in enumerate((46, 36, 26, 16)):
        start = 20 + i * 55
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + 300,
              fill=color, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=color)


STORIES = [
    ("MIDDLE EAST · WAR", (192, 57, 43), "IRAN STRIKES GULF BASES",
     "Drones target Kuwait and Bahrain after a US strike on Qeshm Island.",
     icon_drone),
    ("EUROPE · WAR", (150, 80, 30), "KERCH BRIDGE SPAN FALLS",
     "Ukraine hits the Crimea bridge a second day; part of the road falls.",
     icon_bridge_broken),
    ("ASIA · DIPLOMACY", (40, 90, 160), "XI AND PUTIN MEET IN SHENZHEN",
     "Leaders talk ahead of Thursday's trilateral summit with Trump.",
     icon_summit),
    ("AMERICAS · POLITICS", (39, 103, 73), "PELTOLA WINS ALASKA SENATE SEAT",
     "Democrats take a 56-44 Senate majority in the incoming chamber.",
     icon_ballot),
    ("AFRICA · HEALTH", (107, 70, 193), "EBOLA PASSES 11,000 CASES",
     "DR Congo outbreak doubles in three months; 5,400 deaths, UN says.",
     icon_virus),
    ("PACIFIC · DISASTER", (14, 124, 123), "CYCLONE XAVIER HITS COOK ISLANDS",
     "Category 5 storm strikes the northern islands; damage unclear.",
     icon_cyclone),
]


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 140], fill=NAVY)
    f_date = fit(d, "18 NOVEMBER 2026", BOLD, 72, W - 60)
    d.text((W // 2, 22), "18 NOVEMBER 2026", font=f_date, fill=(255, 255, 255),
           anchor="ma")
    f_sub = font(REG, 25)
    d.text((W // 2, 100), "W E D N E S D A Y   ·   T H E   W O R L D   I N   O N E   I M A G E",
           font=f_sub, fill=NAVY_LIGHT, anchor="ma")

    # story panels: 2 columns x 3 rows
    margin, gap = 16, 12
    pw = (W - 2 * margin - gap) // 2
    ph = 262
    y0 = 156
    for i, (tag, color, head, sub, icon) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (pw + gap)
        y = y0 + row * (ph + gap)
        d.rectangle([x, y, x + pw, y + ph], fill=CARD, outline=BORDER, width=2)
        d.rectangle([x, y, x + pw, y + 10], fill=color)
        icon(d, x + 18, y + 30, 108, color)
        tx = x + 140
        tw = pw - 140 - 18
        f_tag = font(BOLD, 21)
        d.text((tx, y + 26), tag, font=f_tag, fill=color)
        # shrink the headline until it wraps into at most two lines (never truncate)
        f_head = font(BOLD, 36)
        head_lines = wrap(d, head, f_head, tw, max_lines=2)
        size = 36
        while len(wrap(d, head, font(BOLD, size), tw, max_lines=99)) > 2 and size > 20:
            size -= 2
        f_head = font(BOLD, size)
        head_lines = wrap(d, head, f_head, tw, max_lines=2)
        for j, line in enumerate(head_lines):
            d.text((tx, y + 56 + j * 40), line, font=f_head, fill=INK)
        f_sub2 = font(REG, 24)
        sub_lines = wrap(d, sub, f_sub2, tw, max_lines=3)
        sy = y + 56 + len(head_lines) * 40 + 8
        for j, line in enumerate(sub_lines):
            d.text((tx, sy + j * 28), line, font=f_sub2, fill=GREY)

    # footer
    f_foot = font(REG, 21)
    d.text((W // 2, 984),
           "Every story above happened or was first reported on 18 November 2026.",
           font=f_foot, fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
