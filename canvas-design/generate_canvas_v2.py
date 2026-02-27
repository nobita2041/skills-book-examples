#!/usr/bin/env python3
"""
Fluorescent Pulse — Variant B: Wave Interference
Three signal sources create overlapping chromatic fields.
Diagonal corridors replace the cross intersection.
Concentric diamonds instead of circles.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

random.seed(2003)

W, H = 2400, 3200
FONT_DIR = "/Users/nobita2041/.claude/plugins/cache/anthropic-agent-skills/document-skills/1ed29a03dc85/skills/canvas-design/canvas-fonts"

# === PALETTE (identical to v1) ===
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

# Three signal sources — triangular layout
SOURCES = [
    (600, 700, [HOT_PINK, VIVID_MAGENTA, DEEP_ORANGE]),
    (1800, 700, [ELECTRIC_BLUE, CYAN, ULTRA_VIOLET]),
    (1200, 2200, [NEON_GREEN, ACID_YELLOW, CYAN]),
]

def font(name, size):
    try:
        return ImageFont.truetype(f"{FONT_DIR}/{name}", size)
    except:
        return ImageFont.load_default()

def blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def wave_value(px, py, sx, sy, wavelength=180):
    """Sine wave emanating from source (sx, sy)."""
    dist = math.sqrt((px - sx) ** 2 + (py - sy) ** 2)
    return (math.sin(dist / wavelength * 2 * math.pi) + 1) / 2


img = Image.new("RGBA", (W, H), (*NEAR_BLACK, 255))
draw = ImageDraw.Draw(img)

# Title bar boundary
BAR_TOP = H - 225


# ============================================================
# LAYER 1: WAVE INTERFERENCE MOSAIC
# ============================================================
cell = 24
for ry in range(0, BAR_TOP, cell):
    for rx in range(0, W, cell):
        px, py = rx + cell // 2, ry + cell // 2

        # Check diagonal corridor exclusion
        d1 = abs((py - 0) - (px - 0)) / math.sqrt(2)
        d2 = abs((py - 0) - (W - px - 0)) / math.sqrt(2)
        in_diag1 = d1 < 38
        in_diag2 = d2 < 38

        if in_diag1 or in_diag2:
            draw.rectangle([rx, ry, rx + cell, ry + cell], fill=(*NEAR_BLACK, 255))
            continue

        # Compute wave interference from three sources
        waves = []
        for sx, sy, _ in SOURCES:
            waves.append(wave_value(px, py, sx, sy, 160))

        # Interference: sum of waves normalized
        interference = sum(waves) / len(waves)

        # Dominant source determines color family
        dists = [math.sqrt((px - sx) ** 2 + (py - sy) ** 2) for sx, sy, _ in SOURCES]
        min_idx = dists.index(min(dists))
        source_colors = SOURCES[min_idx][2]

        # Secondary source for blending at boundaries
        sorted_idx = sorted(range(3), key=lambda i: dists[i])
        ratio = dists[sorted_idx[0]] / (dists[sorted_idx[0]] + dists[sorted_idx[1]] + 1)

        # Brightness from interference pattern
        bright = 0.3 + interference * 0.7

        # Dark cell probability — higher far from all sources
        min_dist = min(dists)
        max_reach = 1400
        norm = min(min_dist / max_reach, 1.0)

        dark_p = norm * 0.75

        if random.random() < dark_p:
            color = random.choice(DARKS)
        else:
            base = random.choice(source_colors)
            if ratio > 0.35:
                secondary = random.choice(SOURCES[sorted_idx[1]][2])
                base = blend(base, secondary, random.uniform(0.1, 0.4))
            mix = random.choice(BRIGHTS)
            color = blend(base, mix, random.uniform(0.0, 0.15))
            color = tuple(max(0, min(255, int(c * bright + random.randint(-8, 8)))) for c in color)

        draw.rectangle([rx, ry, rx + cell, ry + cell], fill=(*color, 255))


# ============================================================
# LAYER 2: DIAGONAL CORRIDORS (replacing cross channels)
# ============================================================
diag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(diag)

stripe_w, stripe_gap = 30, 20

# Diagonal 1: top-left to bottom-right
for offset in range(-max(W, H), max(W, H), stripe_w + stripe_gap):
    x1 = offset
    y1 = 0
    x2 = offset + BAR_TOP
    y2 = BAR_TOP
    # Check we're near the main diagonal
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    d = abs(mid_y - mid_x) / math.sqrt(2)
    if d < 42:
        continue  # skip the corridor itself, fill with zebra later
    # Perpendicular distance from main diagonal: y = x
    for t_step in range(0, BAR_TOP, 8):
        tx = x1 + t_step
        ty = y1 + t_step
        if 0 <= tx < W and 0 <= ty < BAR_TOP:
            d_to_diag = abs(ty - tx) / math.sqrt(2)
            if abs(d_to_diag - 38) < 5:
                dd.rectangle([tx - 2, ty - 2, tx + 2, ty + 2], fill=(*ACID_YELLOW, 40))

# Zebra stripes along diagonal 1 (y = x direction)
for s in range(-W, W + H, stripe_w + stripe_gap):
    for t in range(0, max(W, H) * 2, 6):
        x = int(s / math.sqrt(2) + t * math.cos(math.pi / 4))
        y = int(s / math.sqrt(2) + t * math.sin(math.pi / 4))
        if 0 <= x < W and 0 <= y < BAR_TOP:
            d1 = abs(y - x) / math.sqrt(2)
            if d1 < 36:
                stripe_phase = ((x + y) // (stripe_w + stripe_gap)) % 2
                if stripe_phase == 0:
                    dd.rectangle([x, y, x + 3, y + 3], fill=(255, 255, 255, 35))

# Zebra stripes along diagonal 2 (y = -x + W direction)
for s in range(-W, W + H, stripe_w + stripe_gap):
    for t in range(0, max(W, H) * 2, 6):
        x = int(W / 2 + s / math.sqrt(2) + t * math.cos(-math.pi / 4))
        y = int(s / math.sqrt(2) + t * math.sin(math.pi / 4))
        if 0 <= x < W and 0 <= y < BAR_TOP:
            d2 = abs(y - (W - x)) / math.sqrt(2)
            if d2 < 36:
                stripe_phase = ((x - y + W) // (stripe_w + stripe_gap)) % 2
                if stripe_phase == 0:
                    dd.rectangle([x, y, x + 3, y + 3], fill=(255, 255, 255, 35))

img = Image.alpha_composite(img, diag)


# ============================================================
# LAYER 3: DIAGONAL EDGE GLOW LINES
# ============================================================
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)

# Diagonal 1 edges (y = x ± offset)
offset = 38
for sign in [-1, 1]:
    pts = []
    for t in range(0, max(W, H) * 2, 4):
        x = t
        y = t + sign * int(offset * math.sqrt(2))
        if 0 <= x < W and 0 <= y < BAR_TOP:
            pts.append((x, y))
    if len(pts) > 1:
        gd.line(pts, fill=(*HOT_PINK, 140), width=2)

# Diagonal 2 edges (y = -x + W ± offset)
for sign in [-1, 1]:
    pts = []
    for t in range(0, W, 4):
        x = t
        y = (W - t) + sign * int(offset * math.sqrt(2))
        if 0 <= x < W and 0 <= y < BAR_TOP:
            pts.append((x, y))
    if len(pts) > 1:
        gd.line(pts, fill=(*ELECTRIC_BLUE, 140), width=2)

# Subtle horizontal + vertical grid hints
gd.line([(0, BAR_TOP // 2), (W, BAR_TOP // 2)], fill=(*ACID_YELLOW, 25), width=1)
gd.line([(W // 2, 0), (W // 2, BAR_TOP)], fill=(*CYAN, 25), width=1)

img = Image.alpha_composite(img, glow)


# ============================================================
# LAYER 4: PEDESTRIAN DOTS ALONG DIAGONALS
# ============================================================
dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dtd = ImageDraw.Draw(dots)

# Dots flowing along diagonal 1
for _ in range(400):
    t = random.uniform(0.05, 0.95)
    base_x = int(t * W)
    base_y = int(t * W)  # y = x
    x = base_x + random.randint(-30, 30)
    y = base_y + random.randint(-30, 30)
    if 0 <= x < W and 0 <= y < BAR_TOP:
        r = random.randint(2, 5)
        c = random.choice([WHITE, ACID_YELLOW, HOT_PINK, VIVID_MAGENTA])
        dtd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(150, 240)))

# Dots flowing along diagonal 2
for _ in range(400):
    t = random.uniform(0.05, 0.95)
    base_x = int(t * W)
    base_y = int(W - t * W)
    x = base_x + random.randint(-30, 30)
    y = base_y + random.randint(-30, 30)
    if 0 <= x < W and 0 <= y < BAR_TOP:
        r = random.randint(2, 5)
        c = random.choice([WHITE, CYAN, ELECTRIC_BLUE, NEON_GREEN])
        dtd.ellipse([x - r, y - r, x + r, y + r], fill=(*c, random.randint(150, 240)))

# Dots at the X intersection center
ix, iy = W // 2, W // 2  # where diagonals cross
if iy < BAR_TOP:
    for _ in range(80):
        angle = random.uniform(0, 2 * math.pi)
        r = random.gauss(0, 20)
        x = ix + int(r * math.cos(angle))
        y = iy + int(r * math.sin(angle))
        sz = random.randint(2, 6)
        c = random.choice([WHITE, HOT_PINK, ACID_YELLOW, CYAN, NEON_GREEN])
        dtd.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(*c, random.randint(180, 255)))

img = Image.alpha_composite(img, dots)


# ============================================================
# LAYER 5: CONCENTRIC DIAMONDS (replacing circles)
# ============================================================
diamonds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dmd = ImageDraw.Draw(diamonds)

dcx, dcy = W // 2, BAR_TOP // 2

diamond_rings = [
    (100, HOT_PINK, 90, 3),
    (200, CYAN, 60, 2),
    (340, ACID_YELLOW, 45, 2),
    (500, NEON_GREEN, 35, 2),
    (700, ELECTRIC_BLUE, 25, 1),
    (920, VIVID_MAGENTA, 18, 1),
    (1160, DEEP_ORANGE, 12, 1),
]

for size, color, alpha, w in diamond_rings:
    pts = [
        (dcx, dcy - size),       # top
        (dcx + size, dcy),       # right
        (dcx, dcy + size),       # bottom
        (dcx - size, dcy),       # left
        (dcx, dcy - size),       # close
    ]
    # Clip to canvas
    clipped = [(max(0, min(W - 1, x)), max(0, min(BAR_TOP - 1, y))) for x, y in pts]
    dmd.line(clipped, fill=(*color, alpha), width=w)

img = Image.alpha_composite(img, diamonds)


# ============================================================
# LAYER 6: SIGNAL LIGHTS (at source positions + intersection)
# ============================================================
sig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sig)

signal_positions = [
    (SOURCES[0][0] - 14, SOURCES[0][1] - 38, 0),   # source A
    (SOURCES[1][0] - 14, SOURCES[1][1] - 38, 2),   # source B
    (SOURCES[2][0] - 14, SOURCES[2][1] - 38, 1),   # source C
    (W // 2 - 14, W // 2 - 38, 0),                  # intersection
    (W // 2 + 80, W // 2 - 38, 2),
    (W // 2 - 100, W // 2 - 38, 1),
    (200, 400, 2),
    (W - 230, 400, 0),
    (200, BAR_TOP - 300, 1),
    (W - 230, BAR_TOP - 300, 0),
]

for sx, sy, on in signal_positions:
    if sy + 76 >= BAR_TOP:
        continue
    sd.rounded_rectangle([sx, sy, sx + 28, sy + 76], radius=5, fill=(25, 25, 25, 200))
    for i, sc in enumerate([SIGNAL_RED, ACID_YELLOW, NEON_GREEN]):
        ly = sy + 6 + i * 22
        a = 230 if i == on else 40
        sd.ellipse([sx + 5, ly, sx + 23, ly + 18], fill=(*sc, a))

img = Image.alpha_composite(img, sig)


# ============================================================
# LAYER 7: SOURCE HALOS
# ============================================================
halos = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halos)

for sx, sy, colors in SOURCES:
    if sy >= BAR_TOP:
        continue
    for r_off, alpha_mult in [(60, 1.0), (45, 0.7), (30, 0.5)]:
        c = colors[0]
        a = int(50 * alpha_mult)
        hd.ellipse([sx - r_off, sy - r_off, sx + r_off, sy + r_off],
                   outline=(*c, a), width=3)
    # Center bright dot
    for _ in range(30):
        angle = random.uniform(0, 2 * math.pi)
        r = random.gauss(0, 12)
        x = sx + int(r * math.cos(angle))
        y = sy + int(r * math.sin(angle))
        sz = random.randint(2, 4)
        c = random.choice(colors + [WHITE])
        hd.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(*c, random.randint(160, 240)))

img = Image.alpha_composite(img, halos)


# ============================================================
# LAYER 8: CORNER ACCENT BLOCKS (triangular zones)
# ============================================================
corners = Image.new("RGBA", (W, H), (0, 0, 0, 0))
crd = ImageDraw.Draw(corners)

bsz = 12
# Top-left triangle
for y in range(40, 320, bsz + 2):
    max_x = 40 + int((320 - y) * 1.2)
    for x in range(40, min(max_x, W - 40), bsz + 2):
        if random.random() < 0.78:
            c = random.choice(BRIGHTS)
            a = random.randint(130, 245)
            crd.rectangle([x, y, x + bsz, y + bsz], fill=(*c, a))

# Top-right triangle
for y in range(40, 320, bsz + 2):
    min_x = W - 40 - int((320 - y) * 1.2)
    for x in range(max(min_x, 40), W - 40, bsz + 2):
        if random.random() < 0.78:
            c = random.choice(BRIGHTS)
            a = random.randint(130, 245)
            crd.rectangle([x, y, x + bsz, y + bsz], fill=(*c, a))

# Bottom-left zone (above bar)
for y in range(BAR_TOP - 280, BAR_TOP - 60, bsz + 2):
    max_x = 40 + int((y - (BAR_TOP - 280)) * 0.9)
    for x in range(40, min(max_x, 360), bsz + 2):
        if random.random() < 0.72:
            c = random.choice(BRIGHTS)
            a = random.randint(120, 235)
            crd.rectangle([x, y, x + bsz, y + bsz], fill=(*c, a))

# Bottom-right zone (above bar)
for y in range(BAR_TOP - 280, BAR_TOP - 60, bsz + 2):
    min_x = W - 40 - int((y - (BAR_TOP - 280)) * 0.9)
    for x in range(max(min_x, W - 360), W - 40, bsz + 2):
        if random.random() < 0.72:
            c = random.choice(BRIGHTS)
            a = random.randint(120, 235)
            crd.rectangle([x, y, x + bsz, y + bsz], fill=(*c, a))

img = Image.alpha_composite(img, corners)


# ============================================================
# LAYER 9: "渋" WATERMARK (replacing "109")
# ============================================================
wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
wd = ImageDraw.Draw(wm)

f_wm = font("BigShoulders-Bold.ttf", 520)
bbox = wd.textbbox((0, 0), "FP", font=f_wm)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
wmx = W // 2 - tw // 2
wmy = BAR_TOP // 2 - th // 2 - 20
wd.text((wmx, wmy), "FP", fill=(*ULTRA_VIOLET, 22), font=f_wm)

img = Image.alpha_composite(img, wm)


# ============================================================
# LAYER 10: FINE GRID (rotated 45 degrees — diamond grid)
# ============================================================
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
grd = ImageDraw.Draw(grid)

spacing = 160
# Diagonal lines: top-left to bottom-right
for offset in range(-max(W, H), max(W, H) * 2, spacing):
    pts = [(offset + t, t) for t in range(0, BAR_TOP, 4)]
    pts = [(x, y) for x, y in pts if 0 <= x < W and 0 <= y < BAR_TOP]
    if len(pts) > 1:
        grd.line(pts, fill=(255, 255, 255, 10), width=1)

# Diagonal lines: top-right to bottom-left
for offset in range(-max(W, H), max(W, H) * 2, spacing):
    pts = [(W - offset - t, t) for t in range(0, BAR_TOP, 4)]
    pts = [(x, y) for x, y in pts if 0 <= x < W and 0 <= y < BAR_TOP]
    if len(pts) > 1:
        grd.line(pts, fill=(255, 255, 255, 10), width=1)

img = Image.alpha_composite(img, grid)


# ============================================================
# LAYER 11: TYPOGRAPHY
# ============================================================
txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)

# Vertical label left: "WAVE"
f_vert = font("BigShoulders-Bold.ttf", 44)
for i, ch in enumerate("INTERFERENCE"):
    td.text((20, 340 + i * 48), ch, fill=(*HOT_PINK, 130), font=f_vert)

# Vertical label right: "FIELD"
for i, ch in enumerate("FIELD"):
    td.text((W - 52, 340 + i * 48), ch, fill=(*NEON_GREEN, 110), font=f_vert)

# Ghost year — different position
f_yr = font("EricaOne-Regular.ttf", 260)
td.text((80, 60), "03", fill=(*ELECTRIC_BLUE, 30), font=f_yr)

# Environmental text fragments
f_m = font("Tektur-Medium.ttf", 36)
f_s = font("GeistMono-Regular.ttf", 18)

frags = [
    ("SOURCE.A", f_s, (SOURCES[0][0] - 40, SOURCES[0][1] + 70), (*HOT_PINK, 70)),
    ("SOURCE.B", f_s, (SOURCES[1][0] - 40, SOURCES[1][1] + 70), (*ELECTRIC_BLUE, 70)),
    ("SOURCE.C", f_s, (SOURCES[2][0] - 40, SOURCES[2][1] + 70), (*NEON_GREEN, 70)),
    ("WAVE", f_m, (W // 2 + 60, 60), (*CYAN, 80)),
    ("λ=160", f_s, (W // 2 + 60, 100), (*ACID_YELLOW, 60)),
    ("NODES", f_s, (W - 130, BAR_TOP // 2 - 10), (*WHITE, 55)),
    ("35.6595N", f_s, (50, BAR_TOP - 60), (*CYAN, 55)),
    ("139.7004E", f_s, (50, BAR_TOP - 40), (*CYAN, 55)),
    ("FREQ.003", f_s, (W - 180, 70), (*VIVID_MAGENTA, 55)),
]
for text, f, pos, color in frags:
    if pos[1] < BAR_TOP - 20:
        td.text(pos, text, fill=color, font=f)

# Coordinate indices along diamond grid intersections
f_idx = font("GeistMono-Regular.ttf", 11)
for i in range(12):
    x = spacing * (i + 1)
    if x < W:
        td.text((x + 2, BAR_TOP - 22), f"{i:02d}", fill=(255, 255, 255, 28), font=f_idx)

img = Image.alpha_composite(img, txt)


# ============================================================
# LAYER 12: BOTTOM TITLE BAR
# ============================================================
bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bar)

bt = BAR_TOP
bd.rectangle([0, bt, W, H], fill=(8, 4, 18, 235))
bd.line([(0, bt), (W, bt)], fill=(*ELECTRIC_BLUE, 230), width=4)
bd.line([(0, bt + 5), (W, bt + 5)], fill=(*NEON_GREEN, 50), width=1)

f_title = font("BigShoulders-Bold.ttf", 100)
f_sub = font("Tektur-Regular.ttf", 26)
f_det = font("GeistMono-Regular.ttf", 14)

bd.text((55, bt + 28), "FLUORESCENT PULSE", fill=(*ELECTRIC_BLUE, 255), font=f_title)
bd.text((59, bt + 132), "WAVE INTERFERENCE STUDY  //  FIELD OBSERVATION NO.003",
        fill=(*WHITE, 110), font=f_sub)

# Right detail block
bd.text((W - 340, bt + 30), "SOURCES:     3 / ACTIVE", fill=(*NEON_GREEN, 85), font=f_det)
bd.text((W - 340, bt + 48), "WAVELENGTH:  160 px", fill=(*CYAN, 85), font=f_det)
bd.text((W - 340, bt + 72), "INTERFERENCE: CONSTRUCTIVE", fill=(*ACID_YELLOW, 100), font=f_det)
bd.text((W - 340, bt + 90), "EPOCH: 2003.08.15", fill=(*VIVID_MAGENTA, 75), font=f_det)
bd.text((W - 340, bt + 108), "SECTOR: TRI-NODE", fill=(*HOT_PINK, 65), font=f_det)

# Color palette swatches
sx_start = 59
sy_start = bt + 175
for i, c in enumerate([HOT_PINK, ELECTRIC_BLUE, NEON_GREEN, ACID_YELLOW,
                        DEEP_ORANGE, CYAN, ULTRA_VIOLET, SIGNAL_RED, VIVID_MAGENTA]):
    bd.rectangle([sx_start + i * 26, sy_start, sx_start + i * 26 + 18, sy_start + 9], fill=(*c, 235))

# Small footer text
f_tiny = font("GeistMono-Regular.ttf", 11)
bd.text((sx_start, bt + 200), "FLUORESCENT PULSE SERIES  |  WAVE INTERFERENCE FIELD RESEARCH",
        fill=(*WHITE, 50), font=f_tiny)

img = Image.alpha_composite(img, bar)


# ============================================================
# LAYER 13: VIGNETTE EFFECT
# ============================================================
vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)

for i in range(40):
    alpha = int((40 - i) * 1.8)
    vd.line([(0, i), (W, i)], fill=(0, 0, 0, alpha), width=1)
    vd.line([(0, bt - 1 - i), (W, bt - 1 - i)], fill=(0, 0, 0, alpha), width=1)
    vd.line([(i, 0), (i, H)], fill=(0, 0, 0, alpha), width=1)
    vd.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=(0, 0, 0, alpha), width=1)

img = Image.alpha_composite(img, vig)


# ============================================================
# SAVE
# ============================================================
final = img.convert("RGB")
out = "/Users/nobita2041/repos/skills_book/examples/canvas-design/fluorescent-pulse-v2.png"
final.save(out, "PNG")
print(f"Saved: {out} ({final.size[0]}x{final.size[1]})")
