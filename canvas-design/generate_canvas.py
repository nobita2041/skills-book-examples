#!/usr/bin/env python3
"""
Fluorescent Pulse — 90s Shibuya Pop Art Poster (Final Polish)
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

random.seed(1997)

W, H = 2400, 3200
FONT_DIR = "/Users/nobita2041/.claude/plugins/cache/anthropic-agent-skills/document-skills/1ed29a03dc85/skills/canvas-design/canvas-fonts"

# === PALETTE ===
HOT_PINK = (255, 20, 147)
ELECTRIC_BLUE = (0, 120, 255)
NEON_GREEN = (0, 255, 120)
ACID_YELLOW = (255, 240, 0)
DEEP_ORANGE = (255, 80, 0)
VIVID_MAGENTA = (230, 0, 120)
CYAN = (0, 230, 240)
ULTRA_VIOLET = (100, 0, 220)
SIGNAL_RED = (255, 40, 40)
WHITE = (255, 255, 255)
NEAR_BLACK = (8, 4, 18)

BRIGHTS = [HOT_PINK, ELECTRIC_BLUE, NEON_GREEN, ACID_YELLOW, DEEP_ORANGE,
           VIVID_MAGENTA, CYAN, ULTRA_VIOLET, SIGNAL_RED]
DARKS = [NEAR_BLACK, (12, 6, 28), (20, 0, 40), (5, 10, 30), (15, 5, 35)]

def font(name, size):
    try:
        return ImageFont.truetype(f"{FONT_DIR}/{name}", size)
    except:
        return ImageFont.load_default()

def blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


img = Image.new("RGBA", (W, H), (*NEAR_BLACK, 255))
draw = ImageDraw.Draw(img)

cx, cy = W // 2, H // 2 - 100
BAND = 64
HALF = BAND // 2

sector_colors = [
    HOT_PINK, ELECTRIC_BLUE, NEON_GREEN, ACID_YELLOW,
    DEEP_ORANGE, CYAN, ULTRA_VIOLET, VIVID_MAGENTA
]

# ============================================================
# LAYER 1: STRUCTURED MOSAIC
# ============================================================
cell = 26
for ry in range(0, H, cell):
    for rx in range(0, W, cell):
        px, py = rx + cell // 2, ry + cell // 2
        dx, dy = px - cx, py - cy
        dist = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)
        norm = min(dist / 1700, 1.0)

        sector = int((angle + math.pi) / (2 * math.pi) * 8) % 8
        base = sector_colors[sector]

        # Skip crossing channels
        if abs(py - cy) < HALF + 6 or abs(px - cx) < HALF + 6:
            draw.rectangle([rx, ry, rx + cell, ry + cell], fill=(*NEAR_BLACK, 255))
            continue

        if norm < 0.1:
            bright, dark_p = 1.0, 0.01
        elif norm < 0.25:
            bright, dark_p = 0.92 - (norm - 0.1) * 3.0, 0.08
        elif norm < 0.45:
            bright, dark_p = 0.65 - (norm - 0.25) * 1.8, 0.25
        elif norm < 0.65:
            bright, dark_p = 0.30, 0.48
        else:
            bright, dark_p = 0.10, 0.78

        if random.random() < dark_p:
            color = random.choice(DARKS)
        else:
            mix = random.choice(BRIGHTS)
            color = blend(base, mix, random.uniform(0.0, 0.3))
            color = tuple(max(0, min(255, int(c * bright + random.randint(-6, 6)))) for c in color)

        draw.rectangle([rx, ry, rx + cell, ry + cell], fill=(*color, 255))


# ============================================================
# LAYER 2: ZEBRA CROSSINGS (more visible)
# ============================================================
zebra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
zd = ImageDraw.Draw(zebra)

zw, zgap = 36, 18
# Horizontal zebra
for x in range(0, W, zw + zgap):
    if abs(x + zw // 2 - cx) > 180:
        zd.rectangle([x, cy - HALF + 6, x + zw, cy + HALF - 6], fill=(255, 255, 255, 50))
# Vertical zebra
for y in range(0, H - 240, zw + zgap):
    if abs(y + zw // 2 - cy) > 180:
        zd.rectangle([cx - HALF + 6, y, cx + HALF - 6, y + zw], fill=(255, 255, 255, 50))

img = Image.alpha_composite(img, zebra)


# ============================================================
# LAYER 3: CHANNEL EDGE GLOW + DIAGONAL HINTS
# ============================================================
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)

# H edges
gd.line([(0, cy - HALF), (W, cy - HALF)], fill=(*ACID_YELLOW, 180), width=3)
gd.line([(0, cy + HALF), (W, cy + HALF)], fill=(*ACID_YELLOW, 180), width=3)
# V edges
gd.line([(cx - HALF, 0), (cx - HALF, H)], fill=(*CYAN, 160), width=3)
gd.line([(cx + HALF, 0), (cx + HALF, H)], fill=(*CYAN, 160), width=3)

# Subtle diagonal crossings
gd.line([(0, 0), (W, H)], fill=(*HOT_PINK, 35), width=2)
gd.line([(W, 0), (0, H)], fill=(*NEON_GREEN, 35), width=2)

img = Image.alpha_composite(img, glow)


# ============================================================
# LAYER 4: PEDESTRIAN DOTS (denser, more structured)
# ============================================================
dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dots)

# Horizontal flow
for _ in range(350):
    x = random.randint(10, W - 10)
    y = cy + random.randint(-HALF + 8, HALF - 8)
    r = random.randint(2, 5)
    c = random.choice([WHITE, ACID_YELLOW, CYAN, HOT_PINK, NEON_GREEN])
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(160, 250)))

# Vertical flow
for _ in range(280):
    x = cx + random.randint(-HALF + 8, HALF - 8)
    y = random.randint(10, H - 250)
    r = random.randint(2, 5)
    c = random.choice([WHITE, NEON_GREEN, ELECTRIC_BLUE, SIGNAL_RED, CYAN])
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(160, 250)))

# Diagonal flows (sparser)
for _ in range(80):
    t = random.uniform(0.05, 0.95)
    x = int(t * W) + random.randint(-25, 25)
    y = int(t * H) + random.randint(-25, 25)
    r = random.randint(1, 3)
    c = random.choice([HOT_PINK, DEEP_ORANGE])
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(80, 150)))

for _ in range(80):
    t = random.uniform(0.05, 0.95)
    x = int((1 - t) * W) + random.randint(-25, 25)
    y = int(t * H) + random.randint(-25, 25)
    r = random.randint(1, 3)
    c = random.choice([NEON_GREEN, CYAN])
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(80, 150)))

img = Image.alpha_composite(img, dots)


# ============================================================
# LAYER 5: CENTER INTERSECTION — FOCAL POINT
# ============================================================
center = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ctd = ImageDraw.Draw(center)

# Central bright ring
for radius, color, alpha, w in [
    (45, HOT_PINK, 130, 5),
    (35, ACID_YELLOW, 100, 3),
    (25, WHITE, 80, 2),
]:
    ctd.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=(*color, alpha), width=w
    )

# Central dot cluster — the absolute epicenter
for _ in range(60):
    angle = random.uniform(0, 2 * math.pi)
    r = random.gauss(0, 15)
    x = cx + int(r * math.cos(angle))
    y = cy + int(r * math.sin(angle))
    sz = random.randint(2, 5)
    c = random.choice([WHITE, HOT_PINK, ACID_YELLOW, CYAN])
    ctd.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(*c, random.randint(180, 255)))

# Countdown display at center
f_countdown = font("PixelifySans-Medium.ttf", 44)
ctd.text((cx - 38, cy - 24), "00:00", fill=(*SIGNAL_RED, 200), font=f_countdown)

img = Image.alpha_composite(img, center)


# ============================================================
# LAYER 6: SIGNAL LIGHTS
# ============================================================
sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sig)

signal_pos = [
    (cx - 180, cy - 180, 0), (cx + 130, cy - 180, 2),
    (cx - 180, cy + 120, 1), (cx + 130, cy + 120, 2),
    (180, cy - 90, 0), (W - 220, cy - 90, 2),
    (cx - 90, 280, 1), (cx - 90, H - 480, 0),
]

for sx, sy, on in signal_pos:
    sd.rounded_rectangle([sx, sy, sx + 28, sy + 76], radius=5, fill=(25, 25, 25, 200))
    for i, sc in enumerate([SIGNAL_RED, ACID_YELLOW, NEON_GREEN]):
        ly = sy + 6 + i * 22
        a = 230 if i == on else 40
        sd.ellipse([sx + 5, ly, sx + 23, ly + 18], fill=(*sc, a))

img = Image.alpha_composite(img, sig)


# ============================================================
# LAYER 7: CONCENTRIC RINGS
# ============================================================
rings = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rings)

for radius, color, alpha, w in [
    (80, HOT_PINK, 80, 3), (160, CYAN, 55, 2),
    (260, ACID_YELLOW, 40, 2), (380, NEON_GREEN, 30, 2),
    (520, ELECTRIC_BLUE, 22, 1), (680, VIVID_MAGENTA, 16, 1),
    (860, DEEP_ORANGE, 12, 1),
]:
    rd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
               outline=(*color, alpha), width=w)

img = Image.alpha_composite(img, rings)


# ============================================================
# LAYER 8: CORNER ACCENT BLOCKS
# ============================================================
corners = Image.new("RGBA", (W, H), (0, 0, 0, 0))
crd = ImageDraw.Draw(corners)

bsz = 14
zones = [
    (50, 50, 440, 340),
    (W - 440, 50, W - 50, 340),
    (50, H - 460, 340, H - 260),
    (W - 340, H - 460, W - 50, H - 260),
]

for x1, y1, x2, y2 in zones:
    for y in range(y1, y2, bsz + 2):
        for x in range(x1, x2, bsz + 2):
            if random.random() < 0.75:
                c = random.choice(BRIGHTS)
                a = random.randint(120, 245)
                crd.rectangle([x, y, x + bsz, y + bsz], fill=(*c, a))

img = Image.alpha_composite(img, corners)


# ============================================================
# LAYER 9: "109" WATERMARK
# ============================================================
wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
wd = ImageDraw.Draw(wm)

f_109 = font("BigShoulders-Bold.ttf", 480)
bbox = wd.textbbox((0, 0), "109", font=f_109)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
wd.text((cx - tw // 2, cy - th // 2 - 10), "109", fill=(*HOT_PINK, 28), font=f_109)

img = Image.alpha_composite(img, wm)


# ============================================================
# LAYER 10: FINE GRID
# ============================================================
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
grd = ImageDraw.Draw(grid)

for x in range(0, W, 200):
    grd.line([(x, 0), (x, H)], fill=(255, 255, 255, 12), width=1)
for y in range(0, H, 200):
    grd.line([(0, y), (W, y)], fill=(255, 255, 255, 12), width=1)

img = Image.alpha_composite(img, grid)


# ============================================================
# LAYER 11: TYPOGRAPHY
# ============================================================
txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)

# Vertical side labels
f_vert = font("BigShoulders-Bold.ttf", 42)
for i, ch in enumerate("FLUORESCENT"):
    td.text((24, 380 + i * 52), ch, fill=(*ACID_YELLOW, 140), font=f_vert)

for i, ch in enumerate("PULSE"):
    td.text((W - 52, 380 + i * 52), ch, fill=(*CYAN, 120), font=f_vert)

# Ghost year
f_yr = font("EricaOne-Regular.ttf", 240)
td.text((W - 440, 55), "97", fill=(*NEON_GREEN, 35), font=f_yr)

# Environmental text
f_m = font("Tektur-Medium.ttf", 38)
f_s = font("GeistMono-Regular.ttf", 18)

frags = [
    ("SIGNAL", f_m, (cx + 50, 60), (*CYAN, 85)),
    ("CROSS", f_m, (cx + 50, cy + 55), (*VIVID_MAGENTA, 75)),
    ("Hz", f_s, (W - 110, cy - 70), (*WHITE, 65)),
    ("FREQ.097", f_s, (160, cy + 55), (*ACID_YELLOW, 60)),
    ("35.6595N", f_s, (50, H - 265), (*CYAN, 55)),
    ("139.7004E", f_s, (50, H - 245), (*CYAN, 55)),
]
for text, f, pos, color in frags:
    td.text(pos, text, fill=color, font=f)

# Edge coordinate indices
f_idx = font("GeistMono-Regular.ttf", 11)
for i, x in enumerate(range(200, W, 200)):
    td.text((x + 2, H - 242), f"{i:02d}", fill=(255, 255, 255, 30), font=f_idx)
for i, y in enumerate(range(200, H - 240, 200)):
    td.text((W - 26, y + 2), f"{i:02d}", fill=(255, 255, 255, 30), font=f_idx)

img = Image.alpha_composite(img, txt)


# ============================================================
# LAYER 12: BOTTOM TITLE BAR
# ============================================================
bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bar)

bt = H - 225
bd.rectangle([0, bt, W, H], fill=(8, 4, 18, 235))
bd.line([(0, bt), (W, bt)], fill=(*HOT_PINK, 230), width=4)
bd.line([(0, bt + 5), (W, bt + 5)], fill=(*ACID_YELLOW, 50), width=1)

f_title = font("BigShoulders-Bold.ttf", 100)
f_sub = font("Tektur-Regular.ttf", 26)
f_det = font("GeistMono-Regular.ttf", 14)

bd.text((55, bt + 28), "FLUORESCENT PULSE", fill=(*HOT_PINK, 255), font=f_title)
bd.text((59, bt + 132), "CHROMATIC DENSITY STUDY  //  FIELD OBSERVATION NO.097",
        fill=(*WHITE, 110), font=f_sub)

# Right detail block
bd.text((W - 310, bt + 30), "LATITUDE  35.6595 N", fill=(*CYAN, 85), font=f_det)
bd.text((W - 310, bt + 48), "LONGITUDE 139.7004 E", fill=(*CYAN, 85), font=f_det)
bd.text((W - 310, bt + 72), "DENSITY: CRITICAL", fill=(*SIGNAL_RED, 100), font=f_det)
bd.text((W - 310, bt + 90), "EPOCH: 1997.04.12", fill=(*ACID_YELLOW, 75), font=f_det)
bd.text((W - 310, bt + 108), "SECTOR: NW-CROSSING", fill=(*NEON_GREEN, 65), font=f_det)

# Color palette swatches
sx_start = 59
sy_start = bt + 175
for i, c in enumerate([HOT_PINK, ELECTRIC_BLUE, NEON_GREEN, ACID_YELLOW,
                        DEEP_ORANGE, CYAN, ULTRA_VIOLET, SIGNAL_RED, VIVID_MAGENTA]):
    bd.rectangle([sx_start + i * 26, sy_start, sx_start + i * 26 + 18, sy_start + 9], fill=(*c, 235))

# Small copyright-style text
f_tiny = font("GeistMono-Regular.ttf", 11)
bd.text((sx_start, bt + 200), "FLUORESCENT PULSE SERIES  |  CHROMATIC FIELD RESEARCH",
        fill=(*WHITE, 50), font=f_tiny)

img = Image.alpha_composite(img, bar)


# ============================================================
# LAYER 13: VIGNETTE EFFECT
# ============================================================
vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)

# Darken edges subtly
for i in range(40):
    alpha = int((40 - i) * 1.8)
    # Top
    vd.line([(0, i), (W, i)], fill=(0, 0, 0, alpha), width=1)
    # Bottom (above bar)
    vd.line([(0, bt - 1 - i), (W, bt - 1 - i)], fill=(0, 0, 0, alpha), width=1)
    # Left
    vd.line([(i, 0), (i, H)], fill=(0, 0, 0, alpha), width=1)
    # Right
    vd.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=(0, 0, 0, alpha), width=1)

img = Image.alpha_composite(img, vig)


# ============================================================
# SAVE
# ============================================================
final = img.convert("RGB")
out = "/Users/nobita2041/repos/skills_book/examples/canvas-design/fluorescent-pulse.png"
final.save(out, "PNG")
print(f"Saved: {out} ({final.size[0]}x{final.size[1]})")
