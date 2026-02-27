#!/usr/bin/env python3
"""「完了」チェックマーク バウンスアニメーション GIF"""

import sys
import math

sys.path.insert(0, "/Users/nobita2041/.claude/plugins/cache/anthropic-agent-skills/document-skills/1ed29a03dc85/skills/slack-gif-creator")

from core.gif_builder import GIFBuilder
from core.easing import interpolate, ease_out_bounce
from core.frame_composer import create_gradient_background
from PIL import Image, ImageDraw

SIZE = 128
FPS = 15
TOTAL_FRAMES = 20  # ~1.3s

# Colors
BG_TOP = (230, 255, 230)       # light green
BG_BOTTOM = (180, 230, 180)    # slightly deeper green
CHECK_COLOR = (34, 170, 60)    # vivid green
CIRCLE_COLOR = (34, 170, 60)
CIRCLE_BG = (255, 255, 255)
SPARKLE_COLOR = (255, 215, 0)  # gold sparkles


def draw_checkmark(draw, cx, cy, scale, alpha_img=None):
    """Draw a thick checkmark centered at (cx, cy) with given scale."""
    # Checkmark points (relative to center, normalized to ~40px)
    # Short arm: goes down-left to bottom
    # Long arm: goes up-right from bottom
    thickness = max(2, int(6 * scale))

    # Define checkmark as a polygon for thick appearance
    s = scale
    # Bottom point of check
    bx, by = cx - 2 * s, cy + 8 * s
    # Left tip
    lx, ly = cx - 18 * s, cy - 6 * s
    # Right tip (top)
    rx, ry = cx + 20 * s, cy - 18 * s

    # Draw as thick lines
    draw.line([(lx, ly), (bx, by)], fill=CHECK_COLOR, width=max(3, int(8 * scale)))
    draw.line([(bx, by), (rx, ry)], fill=CHECK_COLOR, width=max(3, int(8 * scale)))

    # Round caps at endpoints
    cap_r = max(1, int(4 * scale))
    for px, py in [(lx, ly), (bx, by), (rx, ry)]:
        draw.ellipse([px - cap_r, py - cap_r, px + cap_r, py + cap_r], fill=CHECK_COLOR)


def draw_circle_outline(draw, cx, cy, radius, width=3):
    """Draw a circle outline."""
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=CIRCLE_BG,
        outline=CIRCLE_COLOR,
        width=width,
    )


def draw_sparkle(draw, x, y, size, color):
    """Draw a small 4-pointed sparkle."""
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)


builder = GIFBuilder(width=SIZE, height=SIZE, fps=FPS)

for i in range(TOTAL_FRAMES):
    t = i / (TOTAL_FRAMES - 1)  # 0.0 -> 1.0

    # Create background
    frame = create_gradient_background(SIZE, SIZE, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(frame)

    cx, cy_target = SIZE // 2, SIZE // 2 + 4

    # Phase 1: Bounce in from top (frames 0-14)
    if t <= 0.75:
        bounce_t = t / 0.75
        eased = ease_out_bounce(bounce_t)
        cy = interpolate(-30, cy_target, bounce_t, easing='bounce_out')
        scale = interpolate(0.5, 1.0, bounce_t, easing='ease_out')
        circle_radius = int(38 * scale)

        # Draw circle
        draw_circle_outline(draw, cx, int(cy), circle_radius, width=max(2, int(3 * scale)))
        # Draw checkmark
        draw_checkmark(draw, cx, int(cy), scale)

    # Phase 2: Settle + sparkles (frames 15-19)
    else:
        settle_t = (t - 0.75) / 0.25
        cy = cy_target
        scale = 1.0

        # Subtle pulse
        pulse = 1.0 + 0.05 * math.sin(settle_t * math.pi * 2)
        circle_radius = int(38 * pulse)

        # Draw circle
        draw_circle_outline(draw, cx, int(cy), circle_radius, width=3)
        # Draw checkmark
        draw_checkmark(draw, cx, int(cy), pulse)

        # Sparkles appear and fade
        sparkle_alpha = 1.0 - settle_t * 0.5
        sparkle_size = int(6 * sparkle_alpha)
        if sparkle_size > 1:
            # 4 sparkles around the circle
            offsets = [
                (cx - 45, cy - 35),
                (cx + 42, cy - 30),
                (cx - 35, cy + 38),
                (cx + 40, cy + 35),
            ]
            for j, (sx, sy) in enumerate(offsets):
                # Stagger sparkle appearance
                if settle_t > j * 0.15:
                    local_t = min(1.0, (settle_t - j * 0.15) / 0.4)
                    s = int(sparkle_size * (1 - local_t * 0.5))
                    if s > 1:
                        draw_sparkle(draw, sx, sy, s, SPARKLE_COLOR)

    builder.add_frame(frame)

# Add a few static hold frames at the end for looping feel
for _ in range(5):
    frame = create_gradient_background(SIZE, SIZE, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(frame)
    cx, cy = SIZE // 2, SIZE // 2 + 4
    draw_circle_outline(draw, cx, cy, 38, width=3)
    draw_checkmark(draw, cx, cy, 1.0)
    builder.add_frame(frame)

info = builder.save(
    'done_check.gif',
    num_colors=48,
    optimize_for_emoji=True,
    remove_duplicates=True,
)
