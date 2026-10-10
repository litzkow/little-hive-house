"""Seasonal collections: Fall, Halloween, Christmas, Summer, the all-year Holidays & Dates, and Bumper Stickers."""
import math
from common import (save, ftext, text, heart, star_points, mug, measure, fit_size,
                    SERIF_IT, BEBAS, MONO, JOS, JOST)


def P(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


# ---------------------------------------------------------------- shapes
MAPLE_R = [(0, -1.0), (0.12, -0.62), (0.32, -0.74), (0.28, -0.40), (0.62, -0.60), (0.56, -0.30), (0.96, -0.32),
           (0.78, -0.08), (0.92, 0.06), (0.50, 0.22), (0.56, 0.42), (0.18, 0.32), (0.05, 0.46)]


def maple(cx, cy, s, fill, rot=0, stem=None):
    pts = [(x, y) for x, y in MAPLE_R] + [(-x, y) for x, y in reversed(MAPLE_R[1:])]
    poly = P([(cx + x * s, cy + y * s) for x, y in pts])
    st = stem or fill
    return (f'<g transform="rotate({rot} {cx} {cy})"><polygon points="{poly}" fill="{fill}"/>'
            f'<line x1="{cx}" y1="{cy + 0.4 * s:.1f}" x2="{cx}" y2="{cy + 0.95 * s:.1f}" stroke="{st}" stroke-width="{max(2, s * 0.06):.1f}" stroke-linecap="round"/></g>')


def pumpkin(cx, cy, s, fill, line, stem="#5A6B2E", face=None):
    out = [f'<rect x="{cx - 0.07 * s:.1f}" y="{cy - 0.62 * s:.1f}" width="{0.14 * s:.1f}" height="{0.26 * s:.1f}" rx="{0.04 * s:.1f}" fill="{stem}"/>',
           f'<path d="M {cx + 0.05 * s:.1f} {cy - 0.52 * s:.1f} Q {cx + 0.3 * s:.1f} {cy - 0.7 * s:.1f} {cx + 0.36 * s:.1f} {cy - 0.48 * s:.1f} Q {cx + 0.2 * s:.1f} {cy - 0.4 * s:.1f} {cx + 0.05 * s:.1f} {cy - 0.48 * s:.1f} Z" fill="{stem}"/>',
           f'<g fill="{fill}" stroke="{line}" stroke-width="{max(2, 0.035 * s):.1f}">',
           f'<ellipse cx="{cx - 0.36 * s:.1f}" cy="{cy}" rx="{0.42 * s:.1f}" ry="{0.46 * s:.1f}"/>',
           f'<ellipse cx="{cx + 0.36 * s:.1f}" cy="{cy}" rx="{0.42 * s:.1f}" ry="{0.46 * s:.1f}"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{0.44 * s:.1f}" ry="{0.5 * s:.1f}"/></g>']
    if face:
        k = s / 100
        out.append(f'<g fill="{face}"><polygon points="{P([(cx - 26 * k, cy - 14 * k), (cx - 12 * k, cy - 14 * k), (cx - 19 * k, cy - 30 * k)])}"/>'
                   f'<polygon points="{P([(cx + 26 * k, cy - 14 * k), (cx + 12 * k, cy - 14 * k), (cx + 19 * k, cy - 30 * k)])}"/>'
                   f'<path d="M {cx - 30 * k:.1f} {cy + 6 * k:.1f} Q {cx} {cy + 40 * k:.1f} {cx + 30 * k:.1f} {cy + 6 * k:.1f} L {cx + 18 * k:.1f} {cy + 14 * k:.1f} L {cx + 8 * k:.1f} {cy + 6 * k:.1f} L {cx - 4 * k:.1f} {cy + 16 * k:.1f} L {cx - 16 * k:.1f} {cy + 8 * k:.1f} Z"/></g>')
    return "\n".join(out)


def wheat(x, y0, y1, ink, sw=4):
    out = [f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round"/>']
    for i in range(6):
        yy = y1 + 14 + i * 16
        for side in (-1, 1):
            out.append(f'<ellipse cx="{x + side * 9}" cy="{yy}" rx="6" ry="12" transform="rotate({side * 28} {x + side * 9} {yy})" fill="{ink}"/>')
    out.append(f'<ellipse cx="{x}" cy="{y1}" rx="5.5" ry="12" fill="{ink}"/>')
    return "\n".join(out)


def bat(cx, cy, s, fill):
    k = s / 50
    d = (f"M {cx} {cy - 6 * k:.1f} L {cx - 6 * k:.1f} {cy - 14 * k:.1f} L {cx - 8 * k:.1f} {cy - 4 * k:.1f} "
         f"Q {cx - 24 * k:.1f} {cy - 22 * k:.1f} {cx - 50 * k:.1f} {cy - 10 * k:.1f} Q {cx - 38 * k:.1f} {cy - 2 * k:.1f} {cx - 40 * k:.1f} {cy + 10 * k:.1f} "
         f"Q {cx - 28 * k:.1f} {cy} {cx - 22 * k:.1f} {cy + 12 * k:.1f} Q {cx - 12 * k:.1f} {cy + 2 * k:.1f} {cx} {cy + 14 * k:.1f} "
         f"Q {cx + 12 * k:.1f} {cy + 2 * k:.1f} {cx + 22 * k:.1f} {cy + 12 * k:.1f} Q {cx + 28 * k:.1f} {cy} {cx + 40 * k:.1f} {cy + 10 * k:.1f} "
         f"Q {cx + 38 * k:.1f} {cy - 2 * k:.1f} {cx + 50 * k:.1f} {cy - 10 * k:.1f} Q {cx + 24 * k:.1f} {cy - 22 * k:.1f} {cx + 8 * k:.1f} {cy - 4 * k:.1f} "
         f"L {cx + 6 * k:.1f} {cy - 14 * k:.1f} Z")
    return f'<path d="{d}" fill="{fill}"/>'


def cat_sitting(cx, base, s, fill):
    k = s / 100
    return (f'<g fill="{fill}">'
            f'<path d="M {cx - 46 * k:.1f} {base} Q {cx - 56 * k:.1f} {base - 90 * k:.1f} {cx - 20 * k:.1f} {base - 120 * k:.1f} L {cx + 20 * k:.1f} {base - 120 * k:.1f} Q {cx + 56 * k:.1f} {base - 90 * k:.1f} {cx + 46 * k:.1f} {base} Z"/>'
            f'<circle cx="{cx}" cy="{base - 140 * k:.1f}" r="{36 * k:.1f}"/>'
            f'<polygon points="{P([(cx - 34 * k, base - 152 * k), (cx - 30 * k, base - 196 * k), (cx - 6 * k, base - 172 * k)])}"/>'
            f'<polygon points="{P([(cx + 34 * k, base - 152 * k), (cx + 30 * k, base - 196 * k), (cx + 6 * k, base - 172 * k)])}"/>'
            f'</g><path d="M {cx + 40 * k:.1f} {base - 8 * k:.1f} Q {cx + 110 * k:.1f} {base - 10 * k:.1f} {cx + 96 * k:.1f} {base - 80 * k:.1f}" '
            f'fill="none" stroke="{fill}" stroke-width="{14 * k:.1f}" stroke-linecap="round"/>')


def snowflake(cx, cy, r, ink, sw=3):
    out = []
    for i in range(6):
        a = math.radians(i * 60 - 90)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        mx, my = cx + 0.6 * r * math.cos(a), cy + 0.6 * r * math.sin(a)
        for d in (-40, 40):
            b = a + math.radians(d)
            out.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx + 0.3 * r * math.cos(b):.1f}" y2="{my + 0.3 * r * math.sin(b):.1f}"/>')
    return f'<g stroke="{ink}" stroke-width="{sw}" stroke-linecap="round">' + "".join(out) + "</g>"


def tree(cx, top, s, green, trunk, star, balls):
    k = s / 100
    tiers = [(top + 30 * k, 56 * k, 70 * k), (top + 80 * k, 80 * k, 80 * k), (top + 136 * k, 104 * k, 86 * k)]
    out = [f'<rect x="{cx - 12 * k:.1f}" y="{top + 200 * k:.1f}" width="{24 * k:.1f}" height="{30 * k:.1f}" fill="{trunk}"/>']
    for y, hw, h in reversed(tiers):
        out.append(f'<polygon points="{P([(cx, y - h * 0.4), (cx + hw, y + h * 0.75), (cx - hw, y + h * 0.75)])}" fill="{green}"/>')
    out.append(f'<polygon points="{star_points(cx, top, 22 * k, 9 * k)}" fill="{star}"/>')
    for (dx, dy), col in zip([(-30, 70), (26, 96), (-44, 150), (10, 140), (54, 176), (-14, 196), (40, 52)], balls * 3):
        out.append(f'<circle cx="{cx + dx * k:.1f}" cy="{top + dy * k:.1f}" r="{8 * k:.1f}" fill="{col}"/>')
    return "\n".join(out)


def clover(cx, cy, s, fill):
    out = [f'<path d="M {cx} {cy} Q {cx + 0.1 * s:.1f} {cy + 0.6 * s:.1f} {cx + 0.4 * s:.1f} {cy + 0.9 * s:.1f}" fill="none" stroke="{fill}" stroke-width="{0.09 * s:.1f}" stroke-linecap="round"/>']
    for a in (0, 90, 180, 270):
        out.append(f'<g transform="rotate({a} {cx} {cy})">{heart(cx, cy - 0.36 * s, 0.27 * s, fill)}</g>')
    return "\n".join(out)


def stripes_sun(cx, cy, r, colors, clip_id, bg):
    rows = []
    h = 2 * r / len(colors)
    for i, c in enumerate(colors):
        rows.append(f'<rect x="{cx - r}" y="{cy - r + i * h:.1f}" width="{2 * r}" height="{h + 0.5:.1f}" fill="{c}"/>')
    gaps = "".join(f'<rect x="{cx - r}" y="{cy - r + i * h + h * 0.78:.1f}" width="{2 * r}" height="{h * 0.22:.1f}" fill="{bg}"/>'
                   for i in range(len(colors) // 2, len(colors)))
    return (f'<defs><clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>'
            f'<g clip-path="url(#{clip_id})">{"".join(rows)}{gaps}</g>')


def palm(x, base, s, fill, flip=False):
    k = s / 100
    sx = -1 if flip else 1
    trunk = f'<path d="M {x - 6 * k:.1f} {base} Q {x + sx * 10 * k:.1f} {base - 100 * k:.1f} {x + sx * 40 * k:.1f} {base - 190 * k:.1f} L {x + sx * 50 * k:.1f} {base - 186 * k:.1f} Q {x + sx * 24 * k:.1f} {base - 100 * k:.1f} {x + 10 * k:.1f} {base} Z" fill="{fill}"/>'
    tx, ty = x + sx * 45 * k, base - 190 * k
    fronds = []
    for ang, ln in ((-170, 80), (-140, 90), (-100, 70), (-60, 88), (-20, 84), (10, 64)):
        a = math.radians(ang if not flip else 180 - ang)
        ex, ey = tx + ln * k * math.cos(a), ty + ln * k * math.sin(a)
        mx, my = tx + 0.5 * ln * k * math.cos(a) - 14 * k * math.sin(a), ty + 0.5 * ln * k * math.sin(a) + 14 * k * math.cos(a)
        nx, ny = tx + 0.5 * ln * k * math.cos(a) + 6 * k * math.sin(a), ty + 0.5 * ln * k * math.sin(a) - 6 * k * math.cos(a)
        fronds.append(f'<path d="M {tx:.1f} {ty:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey + 18 * k:.1f} Q {nx:.1f} {ny:.1f} {tx:.1f} {ty:.1f} Z" fill="{fill}"/>')
    return trunk + "".join(fronds)


def waves(y, x0, x1, ink, sw=5, amp=10, step=40):
    d = f"M {x0} {y}"
    x = x0
    while x < x1:
        d += f" q {step / 4} {-amp} {step / 2} 0 t {step / 2} 0"
        x += step
    return f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round"/>'


def two_line(lines, y0, font, size, fill, gap, max_w=500, ls=0):
    """Stack lines, all sized to fit the widest."""
    sz = min(fit_size(t, font, size, max_w, ls) for t in lines)
    return "\n".join(text(300, y0 + i * gap, t, font, sz, fill, ls=ls) for i, t in enumerate(lines)), sz


# ---------------------------------------------------------------- Fall
def build_fall():
    rust, mustard, olive, cream, brown, plum = "#B4532A", "#D9A23B", "#5E6B34", "#F6EDE0", "#4A2F1E", "#6B2E3A"
    save("fall", "hello-fall", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>',
        maple(300, 160, 92, rust),
        maple(150, 120, 34, mustard, rot=-30), maple(460, 250, 28, olive, rot=24),
        ftext(300, 372, "hello", SERIF_IT, 100, brown),
        ftext(300, 512, "FALL", BEBAS, 170, rust, ls=12),
    ]))
    save("fall", "pumpkin-spice", "\n".join([
        f'<rect width="600" height="600" fill="{mustard}"/>',
        pumpkin(300, 186, 150, "#E37B33", brown),
        ftext(300, 362, "pumpkin spice", SERIF_IT, 76, brown),
        ftext(300, 446, "& EVERYTHING", BEBAS, 72, brown, ls=6),
        ftext(300, 522, "NICE", BEBAS, 80, cream, ls=10),
    ]))
    knit = "".join(f'<path d="M {x} 120 l 14 16 l 14 -16" fill="none" stroke="{cream}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<path d="M {x} 470 l 14 16 l 14 -16" fill="none" stroke="{cream}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                   for x in range(62, 540, 36))
    save("fall", "sweater-weather", "\n".join([
        f'<rect width="600" height="600" fill="{olive}"/>', knit,
        ftext(300, 302, "SWEATER", BEBAS, 150, cream, ls=8),
        ftext(300, 404, "weather", SERIF_IT, 96, mustard),
    ]))
    save("fall", "cozy-season", "\n".join([
        f'<rect width="600" height="600" fill="{brown}"/>',
        mug(290, 128, cream, heart_fill=rust),
        maple(470, 110, 26, mustard, rot=20), maple(120, 300, 22, rust, rot=-20),
        ftext(300, 416, "COZY", BEBAS, 150, cream, ls=10),
        ftext(300, 498, "season", SERIF_IT, 82, mustard),
    ]))
    save("fall", "falling-for-you", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>',
        maple(180, 120, 50, rust, rot=-25), maple(310, 190, 42, mustard, rot=18), maple(430, 110, 46, plum, rot=-8),
        f'<path d="M 120 250 q 30 -30 60 0 t 60 0" fill="none" stroke="{brown}" stroke-width="2" stroke-dasharray="3 8"/>',
        ftext(300, 376, "falling", SERIF_IT, 104, brown),
        ftext(300, 474, "FOR YOU", BEBAS, 110, rust, ls=10),
        heart(300, 520, 16, rust),
    ]))
    save("fall", "harvest", "\n".join([
        f'<rect width="600" height="600" fill="{rust}"/>',
        wheat(236, 300, 110, cream), wheat(300, 300, 90, cream), wheat(364, 300, 110, cream),
        f'<path d="M 230 270 Q 300 290 370 270" fill="none" stroke="{mustard}" stroke-width="8" stroke-linecap="round"/>',
        ftext(300, 440, "HARVEST", BEBAS, 140, cream, ls=10),
        ftext(300, 500, "gather & give thanks", SERIF_IT, 46, mustard),
    ]))
    save("fall", "oh-my-gourd", "\n".join([
        f'<rect width="600" height="600" fill="{plum}"/>',
        pumpkin(220, 210, 110, "#E37B33", brown), pumpkin(380, 222, 90, mustard, brown), pumpkin(300, 250, 70, cream, brown),
        ftext(300, 410, "oh my", SERIF_IT, 90, cream),
        ftext(300, 520, "GOURD!", BEBAS, 140, mustard, ls=10),
    ]))
    save("fall", "autumn-is-calling", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>',
        f'<rect x="30" y="30" width="540" height="540" rx="4" fill="none" stroke="{brown}" stroke-width="2"/>',
        ftext(300, 170, "leaves are falling,", SERIF_IT, 62, brown),
        ftext(300, 300, "AUTUMN", BEBAS, 150, rust, ls=12),
        ftext(300, 380, "is calling", SERIF_IT, 70, brown),
        maple(220, 470, 36, mustard, rot=-20), maple(300, 460, 40, rust), maple(380, 470, 36, olive, rot=20),
    ]))


# ---------------------------------------------------------------- Halloween
def build_halloween():
    black, orange, purple, green, cream, moon = "#151515", "#E8833A", "#4B2C64", "#7BA05B", "#F6EFE0", "#F3D27A"
    candy = (f'<g transform="rotate(-18 300 190)"><polygon points="232,190 196,160 196,220" fill="{purple}"/>'
             f'<polygon points="368,190 404,160 404,220" fill="{purple}"/><ellipse cx="300" cy="190" rx="74" ry="52" fill="{purple}"/>'
             f'<path d="M 256 160 Q 300 190 268 228" fill="none" stroke="{cream}" stroke-width="8"/>'
             f'<path d="M 304 142 Q 340 190 312 238" fill="none" stroke="{cream}" stroke-width="8"/></g>')
    save("halloween", "trick-or-treat", "\n".join([
        f'<rect width="600" height="600" fill="{orange}"/>', candy,
        ftext(300, 396, "TRICK", BEBAS, 120, black, ls=10),
        ftext(300, 442, "or", SERIF_IT, 52, black),
        ftext(300, 540, "TREAT", BEBAS, 120, black, ls=10),
    ]))
    save("halloween", "spooky-season", "\n".join([
        f'<rect width="600" height="600" fill="{purple}"/>',
        f'<circle cx="300" cy="190" r="96" fill="{moon}"/><circle cx="342" cy="168" r="84" fill="{purple}"/>',
        bat(420, 120, 46, black), bat(160, 230, 34, black), bat(470, 270, 26, black),
        ftext(300, 410, "spooky", SERIF_IT, 110, cream),
        ftext(300, 512, "SEASON", BEBAS, 120, orange, ls=12),
    ]))
    save("halloween", "happy-halloween", "\n".join([
        f'<rect width="600" height="600" fill="{black}"/>',
        pumpkin(300, 210, 180, orange, "#B5541C", face=black),
        ftext(300, 430, "HAPPY", BEBAS, 100, cream, ls=12),
        ftext(300, 510, "halloween", SERIF_IT, 86, orange),
    ]))
    save("halloween", "here-for-the-boos", "\n".join([
        f'<rect width="600" height="600" fill="{orange}"/>',
        cat_sitting(300, 300, 120, black),
        f'<g fill="{orange}"><ellipse cx="288" cy="128" rx="5" ry="8"/><ellipse cx="312" cy="128" rx="5" ry="8"/></g>',
        ftext(300, 404, "here for the", SERIF_IT, 66, black),
        ftext(300, 520, "BOOS", BEBAS, 140, black, ls=12),
    ]))
    hat = (f'<ellipse cx="300" cy="250" rx="150" ry="26" fill="{black}"/>'
           f'<path d="M 214 246 L 300 70 Q 330 60 352 96 Q 330 90 322 110 L 386 246 Z" fill="{black}"/>'
           f'<rect x="232" y="214" width="138" height="22" fill="{green}" transform="skewX(-4)"/>'
           f'<rect x="282" y="212" width="26" height="26" fill="none" stroke="{moon}" stroke-width="5"/>')
    save("halloween", "witch-please", "\n".join([
        f'<rect width="600" height="600" fill="{green}"/>', hat,
        ftext(300, 420, "WITCH", BEBAS, 150, black, ls=12),
        ftext(300, 504, "please", SERIF_IT, 86, cream),
    ]))
    web = []
    for i in range(9):
        a = math.radians(i * 22.5 - 180)
        web.append(f'<line x1="300" y1="40" x2="{300 + 280 * math.cos(a):.1f}" y2="{40 - 280 * math.sin(a) * -1:.1f}"/>')
    for r in (60, 120, 180, 240):
        pts = []
        for i in range(9):
            a = math.radians(i * 22.5 - 180)
            pts.append((300 + r * math.cos(a), 40 + r * abs(math.sin(a))))
        d = "M " + " ".join(f"{x:.1f} {y:.1f}" if j == 0 else f"Q {300 + (pts[j - 1][0] + x) / 2 - 300:.1f} {(pts[j - 1][1] + y) / 2 - 8:.1f} {x:.1f} {y:.1f}"
                            for j, (x, y) in enumerate(pts))
        web.append(f'<path d="{d}" fill="none"/>')
    save("halloween", "creep-it-real", "\n".join([
        f'<rect width="600" height="600" fill="{black}"/>',
        f'<g stroke="{cream}" stroke-width="2" opacity="0.55">{"".join(web)}</g>',
        f'<line x1="430" y1="40" x2="430" y2="186" stroke="{cream}" stroke-width="2"/>',
        f'<circle cx="430" cy="196" r="14" fill="{orange}"/><circle cx="430" cy="178" r="9" fill="{orange}"/>',
        f'<g stroke="{orange}" stroke-width="3" stroke-linecap="round"><path d="M 418 190 l -16 -8 M 418 198 l -18 2 M 418 206 l -14 10 M 442 190 l 16 -8 M 442 198 l 18 2 M 442 206 l 14 10"/></g>',
        ftext(300, 410, "creep it", SERIF_IT, 92, cream),
        ftext(300, 520, "REAL", BEBAS, 150, orange, ls=14),
    ]))
    ghost = ("M -64 104 L -64 -6 Q -64 -84 0 -84 Q 64 -84 64 -6 L 64 104 "
             "q -10.7 -18 -21.3 0 t -21.3 0 t -21.3 0 t -21.3 0 t -21.3 0 t -21.5 0 Z")
    ghosts = "".join(f'<g transform="translate({x} {y}) scale({s})"><path d="{ghost}" fill="{cream}"/>'
                     f'<ellipse cx="-20" cy="-8" rx="9" ry="14" fill="{purple}"/><ellipse cx="20" cy="-8" rx="9" ry="14" fill="{purple}"/></g>'
                     for x, y, s in ((180, 200, 0.6), (300, 180, 0.8), (420, 206, 0.55)))
    save("halloween", "stay-spooky", "\n".join([
        f'<rect width="600" height="600" fill="{purple}"/>', ghosts,
        ftext(300, 412, "STAY", BEBAS, 130, orange, ls=12),
        ftext(300, 500, "spooky", SERIF_IT, 96, cream),
    ]))


# ---------------------------------------------------------------- Christmas
def build_christmas():
    red, green, cream, gold, night, cocoa = "#B8312F", "#1E4D3A", "#F6EFE0", "#E9B949", "#1F3550", "#5A3A22"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                   ((70, 90, 5), (140, 160, 4), (520, 80, 4), (470, 180, 6), (90, 260, 3), (530, 300, 4), (220, 70, 3), (380, 60, 4)))
    save("christmas", "ho-ho-ho", "\n".join([
        f'<rect width="600" height="600" fill="{red}"/>',
        f'<g fill="{cream}" opacity="0.5">{dots}</g>',
        ftext(300, 236, "HO", BEBAS, 150, cream, ls=14),
        ftext(300, 376, "HO", BEBAS, 150, cream, ls=14),
        ftext(300, 516, "HO!", BEBAS, 150, gold, ls=14),
    ]))
    save("christmas", "let-it-snow", "\n".join([
        f'<rect width="600" height="600" fill="{night}"/>',
        snowflake(300, 170, 80, cream, 6), snowflake(130, 110, 30, cream, 3), snowflake(470, 120, 36, cream, 3),
        snowflake(110, 300, 22, cream, 3), snowflake(500, 290, 26, cream, 3),
        ftext(300, 408, "let it", SERIF_IT, 90, cream),
        ftext(300, 520, "SNOW", BEBAS, 150, cream, ls=14),
    ]))
    box = lambda y, checked: (f'<rect x="150" y="{y - 46}" width="54" height="54" rx="6" fill="none" stroke="{green}" stroke-width="6"/>' +
                              (f'<path d="M 160 {y - 20} L 176 {y - 2} L 214 {y - 58}" fill="none" stroke="{red}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>' if checked else ""))
    save("christmas", "naughty-or-nice", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>',
        f'<rect x="30" y="30" width="540" height="540" rx="4" fill="none" stroke="{green}" stroke-width="2"/>',
        ftext(300, 150, "DEAR SANTA,", MONO, 26, green, ls=6),
        box(286, False), text(236, 286, "NAUGHTY", BEBAS, 92, green, anchor="start"),
        box(406, True), text(236, 406, "NICE", BEBAS, 92, red, anchor="start"),
        ftext(300, 500, "(mostly)", SERIF_IT, 48, green),
    ]))
    save("christmas", "merry-christmas", "\n".join([
        f'<rect width="600" height="600" fill="{green}"/>',
        tree(300, 62, 108, "#2F7A57", cocoa, gold, [red, gold, cream]),
        ftext(300, 448, "merry", SERIF_IT, 86, cream),
        ftext(300, 536, "CHRISTMAS", BEBAS, 104, gold, ls=8),
    ]))
    marsh = "".join(f'<rect x="{x}" y="{y}" width="24" height="20" rx="5" fill="{cream}" transform="rotate({r} {x + 12} {y + 10})"/>'
                    for x, y, r in ((238, 112, -12), (268, 104, 8), (298, 112, -4), (326, 106, 14)))
    save("christmas", "hot-cocoa-season", "\n".join([
        f'<rect width="600" height="600" fill="{red}"/>',
        mug(290, 128, cream, sw=6, steam=False), marsh,
        ftext(300, 404, "hot cocoa", SERIF_IT, 90, cream),
        ftext(300, 512, "SEASON", BEBAS, 120, gold, ls=12),
    ]))
    save("christmas", "joy-to-the-world", "\n".join([
        f'<rect width="600" height="600" fill="{night}"/>',
        f'<g fill="{cream}" opacity="0.45">{dots}</g>',
        f'<polygon points="{star_points(300, 150, 70, 28)}" fill="{gold}"/>',
        ftext(300, 404, "JOY", BEBAS, 200, cream, ls=16),
        ftext(300, 494, "to the world", SERIF_IT, 66, gold),
    ]))
    save("christmas", "feliz-natal", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>',
        f'<g fill="{red}" opacity="0.18">{dots}</g>',
        f'<polygon points="{star_points(300, 156, 66, 26)}" fill="{gold}"/>',
        f'<g stroke="{green}" stroke-width="4" stroke-linecap="round"><line x1="190" y1="250" x2="260" y2="250"/><line x1="340" y1="250" x2="410" y2="250"/></g>',
        heart(300, 252, 14, red),
        ftext(300, 384, "feliz", SERIF_IT, 100, green),
        ftext(300, 510, "NATAL", BEBAS, 150, red, ls=14),
    ]))


# ---------------------------------------------------------------- Holidays & Dates (all year)
def build_dates():
    cream, green, red, navy = "#F6EFE0", "#2E7D4F", "#C2343A", "#1F2F4D"
    save("holidays", "lucky", "\n".join([
        f'<rect width="600" height="600" fill="{green}"/>',
        clover(300, 170, 120, cream),
        ftext(300, 420, "LUCKY", BEBAS, 160, cream, ls=14),
        ftext(300, 500, "happy st. patrick's day", SERIF_IT, 44, "#F3D27A"),
    ]))
    pink, lav, mint = "#F8D7DD", "#B9A6E0", "#BFE3CF"
    ears = (f'<ellipse cx="256" cy="150" rx="34" ry="96" fill="{cream}" transform="rotate(-10 256 150)"/>'
            f'<ellipse cx="256" cy="156" rx="16" ry="70" fill="#F2A6B4" transform="rotate(-10 256 156)"/>'
            f'<ellipse cx="344" cy="150" rx="34" ry="96" fill="{cream}" transform="rotate(10 344 150)"/>'
            f'<ellipse cx="344" cy="156" rx="16" ry="70" fill="#F2A6B4" transform="rotate(10 344 156)"/>'
            f'<path d="M 190 300 Q 300 214 410 300 Z" fill="{cream}"/>')
    save("holidays", "hoppy-easter", "\n".join([
        f'<rect width="600" height="600" fill="{lav}"/>', ears,
        ftext(300, 410, "hoppy", SERIF_IT, 104, navy),
        ftext(300, 516, "EASTER", BEBAS, 130, cream, ls=12),
    ]))
    save("holidays", "best-mom-ever", "\n".join([
        f'<rect width="600" height="600" fill="{pink}"/>',
        heart(300, 160, 70, red),
        ftext(300, 340, "best", SERIF_IT, 86, navy),
        ftext(300, 460, "MOM EVER", BEBAS, 126, navy, ls=10),
        ftext(300, 516, "HAPPY MOTHER'S DAY", MONO, 18, red, ls=5),
    ]))
    tie = (f'<path d="M 280 110 L 320 110 L 310 136 L 336 260 L 300 300 L 264 260 L 290 136 Z" fill="{cream}"/>'
           f'<path d="M 280 110 L 320 110 L 310 136 L 290 136 Z" fill="#E9B949"/>')
    save("holidays", "best-dad-ever", "\n".join([
        f'<rect width="600" height="600" fill="{navy}"/>', tie,
        ftext(300, 400, "best", SERIF_IT, 86, "#E9B949"),
        ftext(300, 500, "DAD EVER", BEBAS, 126, cream, ls=10),
        ftext(300, 548, "HAPPY FATHER'S DAY", MONO, 18, cream, ls=5),
    ]))
    cap = (f'<polygon points="300,90 440,146 300,202 160,146" fill="{navy}"/>'
           f'<path d="M 214 168 L 214 230 Q 300 270 386 230 L 386 168 L 300 202 Z" fill="{navy}"/>'
           f'<path d="M 300 146 L 410 160 L 410 236" fill="none" stroke="#E9B949" stroke-width="5"/>'
           f'<rect x="402" y="232" width="16" height="34" rx="4" fill="#E9B949"/>')
    save("holidays", "congrats-grad", "\n".join([
        f'<rect width="600" height="600" fill="{cream}"/>', cap,
        ftext(300, 404, "congrats", SERIF_IT, 96, navy),
        ftext(300, 512, "GRAD!", BEBAS, 140, red, ls=12),
    ]))
    candles = "".join(f'<rect x="{x - 6}" y="104" width="12" height="44" rx="3" fill="{c}"/>'
                      f'<path d="M {x} 76 Q {x + 12} 92 {x} 102 Q {x - 12} 92 {x} 76 Z" fill="#E9B949"/>'
                      for x, c in ((256, cream), (300, "#F2A6B4"), (344, cream)))
    sprinkles = "".join(f'<rect x="{x}" y="{y}" width="12" height="4" rx="2" fill="{c}" transform="rotate({r} {x} {y})"/>'
                        for x, y, r, c in ((240, 214, 30, "#E9B949"), (290, 230, -20, cream), (340, 210, 60, "#F2A6B4"),
                                           (370, 236, -40, "#E9B949"), (226, 248, 10, "#F2A6B4"), (316, 252, 40, cream)))
    save("holidays", "happy-birthday", "\n".join([
        f'<rect width="600" height="600" fill="{mint}"/>', candles,
        f'<rect x="200" y="148" width="200" height="130" rx="12" fill="{red}"/>',
        f'<path d="M 200 172 q 12.5 20 25 0 t 25 0 t 25 0 t 25 0 t 25 0 t 25 0 t 25 0 t 25 0 L 400 160 Q 400 148 388 148 L 212 148 Q 200 148 200 160 Z" fill="{cream}"/>',
        sprinkles,
        f'<rect x="180" y="278" width="240" height="12" rx="6" fill="{navy}"/>',
        ftext(300, 412, "happy", SERIF_IT, 96, navy),
        ftext(300, 516, "BIRTHDAY", BEBAS, 130, red, ls=10),
    ]))


# ---------------------------------------------------------------- Summer
def build_summer():
    teal, coral, sun, pink, navy, sand, white = "#1FA6A6", "#FF6F59", "#FFC93C", "#FF8FB1", "#163A5C", "#F7E3C3", "#FFFFFF"
    rays = "".join(f'<line x1="{300 + 70 * math.cos(math.radians(a)):.1f}" y1="{170 + 70 * math.sin(math.radians(a)):.1f}" '
                   f'x2="{300 + 100 * math.cos(math.radians(a)):.1f}" y2="{170 + 100 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 30))
    save("summer", "beach-please", "\n".join([
        f'<rect width="600" height="600" fill="{coral}"/>',
        f'<circle cx="300" cy="170" r="54" fill="{sun}"/><g stroke="{sun}" stroke-width="9" stroke-linecap="round">{rays}</g>',
        ftext(300, 406, "beach", SERIF_IT, 120, white),
        ftext(300, 516, "PLEASE", BEBAS, 140, navy, ls=12),
    ]))
    save("summer", "vitamin-sea", "\n".join([
        f'<rect width="600" height="600" fill="{teal}"/>',
        waves(120, 70, 530, white, 6), waves(160, 90, 510, sand, 6), waves(200, 70, 530, white, 6),
        ftext(300, 340, "VITAMIN", BEBAS, 150, white, ls=12),
        ftext(300, 484, "SEA", BEBAS, 170, sun, ls=18),
    ]))
    save("summer", "good-vibes-only", "\n".join([
        f'<rect width="600" height="600" fill="{sand}"/>',
        stripes_sun(300, 190, 120, [sun, sun, "#FFA94D", "#FFA94D", coral, coral, pink, pink], "gv-sun", sand),
        f'<rect x="150" y="300" width="300" height="12" fill="{navy}"/>',
        ftext(300, 420, "good vibes", SERIF_IT, 96, navy),
        ftext(300, 512, "ONLY", BEBAS, 120, coral, ls=16),
    ]))
    save("summer", "lifes-a-beach", "\n".join([
        f'<rect width="600" height="600" fill="#BFE8E6"/>',
        f'<circle cx="400" cy="150" r="56" fill="{sun}"/>',
        f'<path d="M 0 300 Q 150 270 300 296 Q 450 322 600 290 L 600 340 L 0 340 Z" fill="{sand}"/>',
        palm(210, 316, 100, navy),
        waves(300, 300, 560, white, 4, 6, 30),
        ftext(300, 440, "life's a", SERIF_IT, 90, navy),
        ftext(300, 540, "BEACH", BEBAS, 130, coral, ls=14),
    ]))
    save("summer", "endless-summer", "\n".join([
        f'<rect width="600" height="600" fill="{navy}"/>',
        stripes_sun(300, 200, 130, [sun, "#FFA94D", coral, pink, pink, coral], "es-sun", navy),
        f'<rect x="0" y="300" width="600" height="300" fill="{navy}"/>',
        palm(140, 316, 92, "#0E2238"), palm(470, 316, 80, "#0E2238", flip=True),
        waves(330, 90, 510, teal, 5, 6, 30),
        ftext(300, 446, "endless", SERIF_IT, 100, white),
        ftext(300, 540, "SUMMER", BEBAS, 120, sun, ls=14),
    ]))
    save("summer", "sunshine-state-of-mind", "\n".join([
        f'<rect width="600" height="600" fill="{sun}"/>',
        f'<circle cx="300" cy="150" r="70" fill="{coral}"/>',
        f'<g stroke="{coral}" stroke-width="10" stroke-linecap="round">' +
        "".join(f'<line x1="{300 + 86 * math.cos(math.radians(a)):.1f}" y1="{150 + 86 * math.sin(math.radians(a)):.1f}" x2="{300 + 110 * math.cos(math.radians(a)):.1f}" y2="{150 + 110 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 30)) + "</g>",
        ftext(300, 352, "SUNSHINE", BEBAS, 130, navy, ls=10),
        ftext(300, 440, "state of mind", SERIF_IT, 76, navy),
        ftext(300, 512, "FLORIDA · GEORGIA · EVERYWHERE", MONO, 16, navy, ls=4),
    ]))
    save("summer", "chill-out", "\n".join([
        f'<rect width="600" height="600" fill="{pink}"/>',
        f'<rect x="286" y="236" width="28" height="80" rx="12" fill="#E9C99A"/>',
        f'<path d="M 230 250 L 230 120 Q 230 70 300 70 Q 370 70 370 120 L 370 250 Z" fill="{coral}"/>',
        f'<path d="M 230 120 Q 230 70 300 70 Q 370 70 370 120 L 370 150 Q 300 132 230 150 Z" fill="{sun}"/>',
        f'<circle cx="350" cy="84" r="22" fill="{pink}"/>',
        ftext(300, 430, "CHILL", BEBAS, 150, navy, ls=14),
        ftext(300, 512, "out", SERIF_IT, 96, white),
    ]))
    save("summer", "salty-air-sandy-hair", "\n".join([
        f'<rect width="600" height="600" fill="{sand}"/>',
        f'<rect x="30" y="30" width="540" height="540" rx="4" fill="none" stroke="{teal}" stroke-width="3"/>',
        waves(130, 90, 510, teal, 6), waves(170, 110, 490, coral, 6),
        ftext(300, 300, "salty air", SERIF_IT, 96, navy),
        ftext(300, 430, "SANDY HAIR", BEBAS, 120, teal, ls=10),
        heart(300, 494, 16, coral),
    ]))


# ---------------------------------------------------------------- Bumper Stickers
STICKERS = [
    ("i-brake-for-coffee", ["I BRAKE", "FOR COFFEE"], "#F6EFE0", "#B8312F", "#F6EFE0", "since forever"),
    ("honk-if-youre-happy", ["HONK IF", "YOU'RE HAPPY"], "#FFC93C", "#163A5C", "#FFC93C", "beep beep"),
    ("my-other-car-is-a-broom", ["MY OTHER CAR", "IS A BROOM"], "#151515", "#E8833A", "#151515", "witchy & proud"),
    ("moms-taxi", ["MOM'S", "TAXI"], "#F8D7DD", "#1F2F4D", "#F8D7DD", "no refunds · no tips needed"),
    ("powered-by-coffee", ["POWERED BY", "COFFEE & CHAOS"], "#1F5E3B", "#F2C230", "#1F5E3B", "100% fully charged"),
    ("normal-is-boring", ["NORMAL", "IS BORING"], "#4B2C64", "#FF8FB1", "#4B2C64", "stay weird"),
    ("good-things-take-time", ["GOOD THINGS", "TAKE TIME"], "#F6EDE0", "#5E6B34", "#F6EDE0", "slow down, friend"),
    ("work-hard-nap-harder", ["WORK HARD", "NAP HARDER"], "#163A5C", "#F6EFE0", "#163A5C", "zzz"),
    ("do-more-of-what-makes-you-happy", ["DO MORE OF WHAT", "MAKES YOU HAPPY"], "#FF6F59", "#F6EFE0", "#FF6F59", "doctor's orders"),
    ("be-the-good", ["BE THE", "GOOD"], "#1FA6A6", "#F6EFE0", "#1FA6A6", "pass it on"),
]


def build_stickers():
    for slug, lines, bg, panel, ink, small in STICKERS:
        stars = "".join(f'<polygon points="{star_points(x, 128, 12, 5)}"/>' for x in (240, 270, 300, 330, 360))
        body, sz = two_line(lines, 0, BEBAS, 120, ink, 0, max_w=440, ls=4)
        gap = sz * 0.95
        total = gap + sz * 0.7
        y0 = 300 - total / 2 + sz * 0.7
        lines_svg = "\n".join(text(300, y0 + i * gap, t, BEBAS, sz, ink, ls=4) for i, t in enumerate(lines))
        save("bumper-stickers", slug, "\n".join([
            f'<rect width="600" height="600" fill="{bg}"/>',
            f'<g fill="{panel}">{stars}</g>',
            f'<rect x="40" y="170" width="520" height="260" rx="22" fill="{panel}"/>',
            f'<rect x="54" y="184" width="492" height="232" rx="14" fill="none" stroke="{ink}" stroke-width="3" stroke-dasharray="2 10" stroke-linecap="round"/>',
            lines_svg,
            ftext(300, 500, small, SERIF_IT, 50, panel, max_w=480),
        ]))


if __name__ == "__main__":
    # Legacy: superseded by the painted/gouache/ink generators (kitchen_ink.py, holidays_gouache.py, summer_gouache.py, ...).
    # Only the builds below that no newer generator replaces are kept.
    # build_dates()
    # build_summer()
    build_stickers()
