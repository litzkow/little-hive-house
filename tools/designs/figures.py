"""Painted human figures for the travel posters (flat-gouache poster style).

    person(x, base_y, height_px, pose="walk", facing=1, palette=None, seed=0, rim=None, light=1, ...)

returns an SVG fragment. x, base_y = where the feet touch the ground (for seated poses: the seat surface,
for "surf_ride" the board, for "cyclist" the ground under the wheels). height_px = standing height of the
person. facing = 1 (to the right / toward +x) or -1. light = side the key light comes from (1 right,
-1 left, in poster coordinates); rim = colour of a rim light catching the edges on that side.

Figures are built on a 100-unit skeleton (feet at 0, crown at -100) from tapered limbs with rounded joints,
then dressed (sleeves, trousers, shorts, skirts, dresses, jackets, coats, swimsuits, hats, hair) and
painted with three tones per surface: base, a shadow side away from the light and a light edge.
Below ~24 px the figure is drawn as a simpler but still proportioned far-distance silhouette.

palette: None (random outfit from the seed), a dict overriding any of
    skin, hair, top, bottom, shoes, hat, bag, accent, board, dog,
    top_kind (tee, long, tank, jacket, coat, dress, swim, sweater),
    bottom_kind (trousers, shorts, skirt, swim, none), hair_style (short, buzz, long, bob, ponytail, bun, curly,
    afro, bald), hat_kind (cap, sunhat, beanie, cowboy, tricorn, helmet, None), form ("f"/"m"),
    season ("summer", "beach", "winter", "any")
or the string "silhouette:#RRGGBB" for a backlit figure in one colour (still shaded and rim-lit).
tint=(color, amount) pushes every colour toward an ambient light (dusk, neon night).
"""
import math
import random

# ------------------------------------------------------------------ colour helpers

def _rgb(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(round(v)))):02X}" for v in rgb)


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


SKINS = ["#F3CDAE", "#E8B48E", "#D49A72", "#B87A52", "#8E5A3A", "#6A4028", "#4E2E1E"]
HAIRS = ["#1C1412", "#2E1E16", "#4A2E1E", "#6E4426", "#9A6634", "#C8964E", "#A4462A", "#B8B0A6"]
TOPS = ["#C8573E", "#E3A43E", "#3E6A8A", "#4A7A5A", "#F2E6D0", "#B85A7A", "#2E3A58", "#7A5A9A", "#E07A5A",
        "#4E9AA2", "#D8C8A0", "#8A3A3A", "#F0D46A", "#5A8AC0", "#E8E2D8"]
BOTTOMS = ["#2E3A58", "#3E5274", "#4A4038", "#CDBB94", "#26242C", "#E6DCC8", "#5A6A4A", "#6A4A3A"]
SHOES = ["#2A2228", "#5A3A2A", "#E6E0D6", "#8A3A2A", "#3A3A44", "#C8A070"]
DRESSES = ["#C8573E", "#E3A43E", "#4E9AA2", "#B85A7A", "#F2E6D0", "#5A8AC0", "#E07A5A", "#7A5A9A", "#F0D46A"]
SWIMS = ["#D8443A", "#2E6AA8", "#F0B43A", "#1E8A8A", "#E86A8A", "#2A2A3A"]
COATS = ["#8A3A3A", "#3A4A6A", "#6A5A4A", "#C8A070", "#2E3A3A", "#7A4A5A", "#B85A3E"]

SEATED = ("sit", "sit_side", "sit_back", "sit_front", "read", "paddle", "surf_sit", "guitar")
SHADOW = "#24183A"   # cool shadow the shade tones lean toward
LIGHT = "#FFF4DE"    # warm light the highlight tones lean toward


def tones(c, sh=0.32, hi=0.3, light=LIGHT):
    return c, mix(c, SHADOW, sh), mix(c, light, hi)


# ------------------------------------------------------------------ geometry helpers

def _f(v):
    return f"{v:.1f}"


def _pts(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _norm(x, y):
    d = math.hypot(x, y) or 1.0
    return x / d, y / d


def _smooth(pts, closed=True):
    """Path through the midpoints of pts using pts as quadratic controls -> soft corners."""
    n = len(pts)
    if n < 3:
        return "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + (" Z" if closed else "")
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    d = [f"M {_f(mids[-1][0])} {_f(mids[-1][1])}"]
    for i in range(n):
        d.append(f"Q {_f(pts[i][0])} {_f(pts[i][1])} {_f(mids[i][0])} {_f(mids[i][1])}")
    return " ".join(d) + " Z"


def _chain_frames(pts):
    """Unit tangents and left normals at each point of a polyline."""
    n = len(pts)
    tans = []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        tans.append(_norm(b[0] - a[0], b[1] - a[1]))
    norms = [(-ty, tx) for tx, ty in tans]
    return tans, norms


def _resample(pts, ws, step=4.0):
    """Insert points along the chain so long segments bend smoothly when offset."""
    P, W = [pts[0]], [ws[0]]
    for (a, wa), (b, wb) in zip(zip(pts, ws), zip(pts[1:], ws[1:])):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        for j in range(1, k + 1):
            t = j / k
            P.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            W.append(wa + (wb - wa) * t)
    return P, W


def cut(pts, ws, t):
    """First fraction t (0..1, by length) of a chain."""
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    tot = sum(seg) or 1
    goal = tot * max(0.0, min(1.0, t))
    P, W, acc = [pts[0]], [ws[0]], 0.0
    for i, L in enumerate(seg):
        if acc + L >= goal:
            u = (goal - acc) / (L or 1)
            a, b = pts[i], pts[i + 1]
            P.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            W.append(ws[i] + (ws[i + 1] - ws[i]) * u)
            return P, W
        acc += L
        P.append(pts[i + 1])
        W.append(ws[i + 1])
    return P, W


def tube(pts, ws, cap0=True, cap1=True):
    """Outline (list of points) of a tapered tube with rounded ends."""
    pts, ws = _resample(pts, ws)
    tans, norms = _chain_frames(pts)
    L = [(p[0] + n[0] * w / 2, p[1] + n[1] * w / 2) for p, n, w in zip(pts, norms, ws)]
    R = [(p[0] - n[0] * w / 2, p[1] - n[1] * w / 2) for p, n, w in zip(pts, norms, ws)]
    out = list(L)
    if cap1:
        p, t, n, w = pts[-1], tans[-1], norms[-1], ws[-1]
        for a in (60, 30, 0, -30, -60):
            r = math.radians(a)
            out.append((p[0] + (t[0] * math.cos(r) + n[0] * math.sin(r)) * w / 2,
                        p[1] + (t[1] * math.cos(r) + n[1] * math.sin(r)) * w / 2))
    out += R[::-1]
    if cap0:
        p, t, n, w = pts[0], tans[0], norms[0], ws[0]
        for a in (-60, -30, 0, 30, 60):
            r = math.radians(a)
            out.append((p[0] + (-t[0] * math.cos(r) + n[0] * math.sin(r)) * w / 2,
                        p[1] + (-t[1] * math.cos(r) + n[1] * math.sin(r)) * w / 2))
    return out


def tube_side(pts, ws, L, frac=0.5, lit=False, cap1=True):
    """The strip of a tube on its shadow side (or lit side): from the edge in to frac of the width."""
    pts, ws = _resample(pts, ws)
    tans, norms = _chain_frames(pts)
    avg = sum(n[0] * L[0] + n[1] * L[1] for n in norms)
    s = -1 if avg > 0 else 1          # sign of the normal pointing away from the light
    if lit:
        s = -s
    edge = [(p[0] + s * n[0] * w / 2, p[1] + s * n[1] * w / 2) for p, n, w in zip(pts, norms, ws)]
    inner = [(p[0] + s * n[0] * w * (0.5 - frac), p[1] + s * n[1] * w * (0.5 - frac)) for p, n, w in zip(pts, norms, ws)]
    out = list(edge)
    if cap1:
        p, t, n, w = pts[-1], tans[-1], norms[-1], ws[-1]
        for a in (60, 30, 0):
            r = math.radians(a)
            out.append((p[0] + (t[0] * math.cos(r) + s * n[0] * math.sin(r)) * w / 2,
                        p[1] + (t[1] * math.cos(r) + s * n[1] * math.sin(r)) * w / 2))
    return out + inner[::-1]


def ell_pts(cx, cy, rx, ry, a0, a1, n=14, rot=0.0):
    out = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


# ------------------------------------------------------------------ painter

class Painter:
    """Collects shapes in local units; knows the light, rim, scale and detail level."""

    def __init__(self, k, lx, rim, tint, detail):
        self.k = k                          # px per unit
        self.lx = lx                        # light direction in local x (+1 / -1)
        self.L = _norm(lx * 0.85, -0.55)    # light vector (from above, to the side)
        self.rim = rim
        self.tint = tint
        self.detail = detail                # 0 tiny, 1 small, 2 full
        self.out = []
        self.rim_d = min(3.2, max(0.9, 0.6 / k)) if rim else 0
        # body mass grows as the figure shrinks, so small people read as painted bodies, not stick lines:
        # limbs (bulk), torso (tbulk) and head (hbulk) widen smoothly below ~70 px of standing height.
        s = max(0.0, min(1.0, (70.0 - 100.0 * k) / 46.0))
        self.small = s
        self.bulk = 1.1 + 0.5 * s
        self.tbulk = 1.05 + 0.22 * s
        self.hbulk = 1.0 + 0.16 * s

    def c(self, col):
        if self.tint and col:
            return mix(col, self.tint[0], self.tint[1])
        return col

    def add(self, s):
        self.out.append(s)

    def fill(self, pts, col, op=None, smooth=True, rim=True):
        d = _smooth(pts) if smooth else "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + " Z"
        o = f' opacity="{op}"' if op is not None else ""
        if rim and self.rim:
            dx, dy = self.lx * self.rim_d, -self.rim_d * 0.35
            self.out.append(f'<path transform="translate({_f(dx)} {_f(dy)})" d="{d}" fill="{self.rim}"/>')
        self.out.append(f'<path d="{d}" fill="{self.c(col)}"{o}/>')

    def shape(self, pts, col, op=None, smooth=True):
        self.fill(pts, col, op, smooth, rim=False)

    def tube(self, pts, ws, col, shade=True, cap0=True, cap1=True, rim=True, sh=0.3, hi=0.26):
        base, dk, lt = tones(col, sh, hi)
        self.fill(tube(pts, ws, cap0, cap1), base, rim=rim)
        if shade:
            self.shape(tube_side(pts, ws, self.L, 0.42, cap1=cap1), dk)
            if self.detail >= 2:
                self.shape(tube_side(pts, ws, self.L, 0.13, lit=True, cap1=cap1), lt, op=0.6)

    def ellipse(self, cx, cy, rx, ry, col, shade=True, rot=0.0, rim=True, sh=0.3, hi=0.3):
        base, dk, lt = tones(col, sh, hi)
        pts = ell_pts(cx, cy, rx, ry, 0, 360, 24, rot)[:-1]
        self.fill(pts, base, rim=rim)
        if shade:
            self.shape(self.crescent(cx, cy, rx, ry, 0.7, rot), dk)

    def crescent(self, cx, cy, rx, ry, k=0.42, rot=0.0, lit=False):
        """Half-moon of an ellipse on the side away from the light (or toward it)."""
        ang = math.degrees(math.atan2(-self.L[1], -self.L[0]))
        if lit:
            ang += 180
        outer = ell_pts(cx, cy, rx, ry, ang - 90, ang + 90, 12, rot)
        # inner arc: squash the ellipse along the light axis
        inner = []
        for x, y in outer[::-1]:
            dx, dy = x - cx, y - cy
            ax, ay = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            along = dx * ax + dy * ay
            inner.append((x - ax * along * k, y - ay * along * k))
        return outer + inner


# ------------------------------------------------------------------ outfits

def _palette(palette, seed, form=None, child=False):
    rnd = random.Random(seed * 7919 + 13)
    if isinstance(palette, str) and palette.startswith("silhouette"):
        col = palette.split(":")[1] if ":" in palette else "#2A2230"
        pal = {k: col for k in ("skin", "hair", "top", "bottom", "shoes", "hat", "bag", "accent", "dog", "board")}
        pal.update(top_kind="tee", bottom_kind="trousers", hair_style=rnd.choice(["short", "ponytail", "bob", "long", "curly"]),
                   hat_kind=None, form=form or rnd.choice("fm"), silhouette=True)
        return pal
    pal = dict(palette or {})
    form = pal.get("form") or form or rnd.choice("fm")
    season = pal.get("season", "any")
    skin = rnd.choice(SKINS)
    hair = rnd.choice(HAIRS[:7] if child else HAIRS)
    if form == "f":
        style = rnd.choice(["long", "long", "ponytail", "bob", "bun", "curly", "afro", "short"])
    else:
        style = rnd.choice(["short", "short", "short", "buzz", "curly", "afro", "bald", "ponytail"])
    if child:
        style = rnd.choice(["short", "ponytail", "curly", "bob"])
    if season == "beach":
        top_kind = rnd.choice(["swim", "tank", "tee", "swim"])
        bottom_kind = "swim" if top_kind == "swim" else "shorts"
    elif season == "winter":
        top_kind = rnd.choice(["coat", "jacket", "sweater", "coat"])
        bottom_kind = "trousers"
    elif season == "summer":
        top_kind = rnd.choice(["tee", "tee", "tank", "dress" if form == "f" else "tee", "long"])
        bottom_kind = rnd.choice(["shorts", "trousers", "skirt" if form == "f" else "shorts"])
    else:
        top_kind = rnd.choice(["tee", "long", "jacket", "sweater", "dress" if form == "f" else "tee", "tee"])
        bottom_kind = rnd.choice(["trousers", "trousers", "shorts", "skirt" if form == "f" else "trousers"])
    if top_kind == "dress":
        bottom_kind = "none"
    top = rnd.choice(DRESSES if top_kind == "dress" else SWIMS if top_kind == "swim" else COATS if top_kind == "coat" else TOPS)
    bottom = rnd.choice(SWIMS if bottom_kind == "swim" else BOTTOMS)
    if bottom == top:
        bottom = BOTTOMS[0]
    out = dict(skin=skin, hair=hair, top=top, bottom=bottom, shoes=rnd.choice(SHOES), hat=rnd.choice(["#E8D8B0", "#C8573E", "#2E3A58", "#D8B070", "#F2E6D0"]),
               bag=rnd.choice(["#6A4A3A", "#C8573E", "#2E3A58", "#D8B070"]), accent=rnd.choice(TOPS), board=rnd.choice(["#F4E8D0", "#F0B040", "#E8604A", "#7AC8C8"]),
               dog=rnd.choice(["#C8964E", "#3A2A22", "#E8DCC8", "#8A5A34", "#2A2228"]),
               top_kind=top_kind, bottom_kind=bottom_kind, hair_style=style, hat_kind=None, form=form, inner=rnd.choice(["#F2E6D0", "#E8E2D8", "#D8C8A0"]))
    out.update(pal)
    out["form"] = form
    return out


# ------------------------------------------------------------------ poses (local units, facing +x)

def _torso_side(hip, lean, form, child=False, slouch=0.0):
    """Spine chain neck-top .. hip for a side view; lean in degrees (forward = +)."""
    a = math.radians(lean)
    sx, sy = math.sin(a), -math.cos(a)
    def at(t):          # t units up the spine from the hip
        bend = slouch * (t / 35) ** 2
        return (hip[0] + sx * t + bend, hip[1] + sy * t)
    f = form == "f"
    c = at(24)
    w = at(12)
    return [at(35) + (7.5,), at(31) + (12.5,), (c[0] + 1.1, c[1], 14 if f else 14.5), (w[0] - 0.2, w[1], 11 if f else 12), at(1) + (13.5 if f else 13,)]


def _torso_front(hip, form, squeeze=1.0, lean=0.0):
    f = form == "f"
    x, y = hip
    s = squeeze
    return [(x + lean * 0.9, y - 35, 9.5 * s), (x + lean * 0.8, y - 31, (19.5 if f else 22.5) * s), (x + lean * 0.6, y - 24, (18 if f else 20.5) * s),
            (x + lean * 0.3, y - 12, (14.5 if f else 17) * s), (x, y - 1, (20 if f else 19) * s)]


def pose_joints(pose, form, rnd, child=False):
    """Skeleton for a pose: view, head, torso chain, arms, legs (all facing +x)."""
    f = form == "f"
    J = dict(view="side", tilt=0, extra=[])
    j = rnd.uniform(-1, 1)

    if pose in ("stand", "front", "stand_front", "wave", "stand_back", "back", "stand_34", "34"):
        view = "back" if pose in ("stand_back", "back") else "34" if pose in ("stand_34", "34") else "front"
        sq = 0.86 if view == "34" else 1.0
        hip = (0, -49)
        J["view"] = view
        J["torso"] = _torso_front(hip, form, sq)
        sh = 7.6 if f else 8.8
        sh *= sq
        hands = rnd.choice(["down", "down", "hip", "pocket"])
        arms = []
        for s in (-1, 1):
            shp = (s * sh, -79.2)
            if pose == "wave" and s == 1:
                arms.append(("R", [shp, (s * (sh + 8), -88), (s * (sh + 9), -103)], "front"))
                continue
            if hands == "hip" and s == -1:
                arms.append(("L", [shp, (s * (sh + 8), -67), (s * (sh + 1.5), -56)], "front"))
            else:
                arms.append(("LR"[s > 0], [shp, (s * (sh + 3.0 + j * 0.5), -64), (s * (sh + 4.6), -50)], "front"))
        J["arms"] = arms
        spread = rnd.uniform(3.6, 5.6)
        J["legs"] = [([(s * 4.6, -49), (s * (spread - 0.2), -26), (s * spread, -4)], None, "front") for s in (-1, 1)]
        J["head"] = (0.8 if view == "34" else 0, -92.5)
        J["foot"] = "front"
        return J

    if pose in ("walk", "hiker", "dog_walker", "surfer", "photo_walk", "walk_point"):
        st = rnd.uniform(0.8, 1.05)
        hip = (0, -48.5)
        J["torso"] = _torso_side(hip, 3, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.6, -92.4)
        # near leg forward (heel strike), far leg back (push off)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-5 * st, -26), (-14 * st, -7)], 38, "back"),
                     ([(hip[0] + 1, hip[1]), (8 * st, -27), (9.5 * st, -3.6)], -14, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 4.5 * st, -66), (sh[0] + 10 * st, -54)], "back"),
                     ("near", [sh, (sh[0] - 4 * st, -66), (sh[0] - 8.5 * st, -54.5)], "front")]
        if pose == "dog_walker":
            J["arms"][1] = ("near", [sh, (sh[0] + 1.5, -66), (sh[0] + 9, -57)], "front")
        if pose == "surfer":    # board under the near arm: the arm wraps over the top rail, hand under the bottom rail
            J["arms"][1] = ("near", [sh, (sh[0] - 3, -62), (sh[0] + 4.5, -46.5)], "front")
            J["arms"][0] = ("far", [sh, (sh[0] + 5, -66), (sh[0] + 9.5, -55)], "back")
        if pose == "walk_point":
            J["arms"][1] = ("near", [sh, (sh[0] + 9, -84), (sh[0] + 20, -92)], "front")
        J["foot"] = "side"
        return J

    if pose == "jog":
        hip = (0, -51)
        J["torso"] = _torso_side(hip, 11, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 2.8, -94)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-8, -32), (-21, -22)], 50, "back"),
                     ([(hip[0] + 1, hip[1]), (13, -36), (10, -12)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 7, -70), (sh[0] + 14, -78)], "back"),
                     ("near", [sh, (sh[0] - 8, -70), (sh[0] - 4, -60)], "front")]
        J["foot"] = "side"
        J["lift"] = 6
        return J

    if pose in ("sit", "sit_side"):
        hip = (0, -4.5)
        J["torso"] = _torso_side(hip, -4 + j * 2, form, slouch=1.2)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.4, -48)
        J["legs"] = [([(hip[0] + 1, hip[1]), (19, -6), (22.5, 15)], 0, "back"),
                     ([(hip[0] + 2, hip[1] + 0.5), (20, -5), (19, 17)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] - 3, -22), (sh[0] - 4, -6)], "back"),
                     ("near", [sh, (sh[0] + 3, -22), (sh[0] + 13, -10)], "front")]
        J["foot"] = "side"
        return J

    if pose == "read":
        hip = (0, -4.5)
        J["torso"] = _torso_side(hip, 4, form, slouch=1.5)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 2.0, -47.5)
        J["tilt"] = 18
        J["legs"] = [([(hip[0] + 1, hip[1]), (19, -7), (21, 15)], 0, "back"),
                     ([(hip[0] + 2, hip[1] + 0.5), (20, -6), (19.5, 17)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 1, -22), (sh[0] + 10, -27)], "back"),
                     ("near", [sh, (sh[0] + 2, -21), (sh[0] + 10.5, -25)], "front")]
        J["extra"].append(("book", (sh[0] + 13, -29)))
        J["foot"] = "side"
        return J

    if pose == "paddle":
        hip = (0, -4.5)
        J["torso"] = _torso_side(hip, 14, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 2.4, J["torso"][0][1] - 7)
        J["legs"] = [([(hip[0] + 1, hip[1]), (20, -8), (30, -2)], 0, "back"), ([(hip[0] + 2, hip[1]), (21, -7), (31, -1)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] - 4, -18), (-4, -8)], "back"),
                     ("near", [sh, (sh[0] + 9, -36), (11, -27)], "front")]
        J["foot"] = "side"
        return J

    if pose == "guitar":       # seated on a crate / step, guitar across the lap (front view)
        hip = (0, -5)
        J["view"] = "front"
        J["torso"] = _torso_front(hip, form, lean=-1.0)
        J["arms"] = [("L", [(-8.8, -36.5), (-13, -22), (-1, -16)], "front"), ("R", [(8.8, -36.5), (18, -31), (24.5, -27)], "front")]
        J["legs"] = [([(-5, -4), (-8, 1), (-9, 25)], None, "front"), ([(5, -4), (8, 1), (9.5, 25)], None, "front")]
        J["head"] = (-0.6, -48.5)
        J["tilt"] = -6
        J["foot"] = "front"
        J["extra"].append(("guitar", (3, -14)))
        return J

    if pose == "cyclist_front":   # riding straight toward the viewer
        hip = (0, -58)
        J["view"] = "front"
        J["torso"] = _torso_front(hip, form)
        J["torso"] = [(x, hip[1] + (y - hip[1]) * 0.9, w) for x, y, w in J["torso"]]
        top = J["torso"][1][1]
        J["arms"] = [("L", [(-8.8, top + 1.5), (-13, -76), (-13.5, -66)], "front"), ("R", [(8.8, top + 1.5), (13, -76), (13.5, -66)], "front")]
        ph = rnd.uniform(-1, 1)
        J["legs"] = [([(-4.6, -58), (-6.5, -40 + 4 * ph), (-4, -20 + 6 * ph)], None, "front"), ([(4.6, -58), (6.5, -40 - 4 * ph), (4, -20 - 6 * ph)], None, "front")]
        J["head"] = (0, top - 13)
        J["foot"] = "front"
        J["extra"].append(("front_bike", (0, 0)))
        return J

    if pose in ("sit_back", "sit_front"):
        view = "back" if pose == "sit_back" else "front"
        hip = (0, -5)
        J["view"] = view
        J["torso"] = _torso_front(hip, form)
        sh = 7.6 if f else 8.8
        J["arms"] = [("L", [(-sh, -36.5), (-sh - 3, -21), (-sh - 3, -6)], "front"), ("R", [(sh, -36.5), (sh + 3, -21), (sh + 2.5, -6)], "front")]
        # thighs run toward/away from us, so they read short; shins hang
        J["legs"] = [([(s * 5, -4), (s * 6.5, 1), (s * 6.5, 18)], None, "front") for s in (-1, 1)] if view == "front" else []
        J["head"] = (0, -48.5)
        J["foot"] = "front"
        J["seat_w"] = 22
        return J

    if pose in ("lean", "lean_side"):
        hip = (-4, -49)
        J["torso"] = _torso_side(hip, 17, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 3.0, J["torso"][0][1] - 7.2)
        J["legs"] = [([(hip[0], hip[1]), (-3, -26), (-5, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (0, -27), (-7, -4.5)], 0, "front")]
        rail = -58
        J["arms"] = [("far", [sh, (sh[0] + 3, rail - 1), (sh[0] + 14, rail - 2)], "back"),
                     ("near", [sh, (sh[0] + 1.5, rail + 0.5), (sh[0] + 13, rail - 1)], "front")]
        J["foot"] = "side"
        return J

    if pose == "lean_back":
        hip = (0, -49)
        J["view"] = "back"
        J["torso"] = _torso_front(hip, form)
        J["torso"][0] = (0, -82, 12)
        J["torso"][1] = (0, -78.5, J["torso"][1][2])
        sh = 7.6 if f else 8.8
        rail = -58
        J["arms"] = [("L", [(-sh, -76.5), (-sh - 6.5, rail + 1), (-5, rail - 2)], "back"), ("R", [(sh, -76.5), (sh + 6.5, rail + 1), (5, rail - 2)], "back")]
        J["legs"] = [([(-4.6, -49), (-4.2, -26), (-4, -4)], None, "front"), ([(4.6, -49), (6, -26), (8, -4)], None, "front")]
        J["head"] = (0, -88.5)
        J["foot"] = "front"
        return J

    if pose == "trumpet":
        hip = (0, -49)
        J["torso"] = _torso_side(hip, -6, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.0, -92.8)
        J["tilt"] = -14
        J["legs"] = [([(hip[0] - 1, hip[1]), (-3, -26), (-7, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (5, -26), (6, -4)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 6, -70), (sh[0] + 13, -86)], "back"),
                     ("near", [sh, (sh[0] + 3, -68), (sh[0] + 9, -84)], "front")]
        J["extra"].append(("trumpet", (J["head"][0] + 5.5, J["head"][1] + 2.5)))
        J["foot"] = "side"
        return J

    if pose == "photo":
        hip = (0, -49)
        J["torso"] = _torso_side(hip, -2, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.4, -92.5)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-3, -26), (-7, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (4, -26), (5, -4)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 4, -68), (sh[0] + 10.5, -88)], "back"),
                     ("near", [sh, (sh[0] + 2, -67), (sh[0] + 10, -86)], "front")]
        J["extra"].append(("camera", (sh[0] + 11.5, -91)))
        J["foot"] = "side"
        return J

    if pose == "point":
        hip = (0, -49)
        J["torso"] = _torso_side(hip, -1, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.2, -92.6)
        J["tilt"] = -12
        J["legs"] = [([(hip[0] - 1, hip[1]), (-3, -26), (-7, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (4, -26), (5, -4)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] - 1, -64), (sh[0] + 1, -50)], "back"),
                     ("near", [sh, (sh[0] + 9, -88), (sh[0] + 17, -101)], "front")]
        J["foot"] = "side"
        return J

    if pose == "skate":       # riding a skateboard, knees bent, arms out for balance
        hip = (0, -47)
        J["torso"] = _torso_side(hip, 8, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 2.0, J["torso"][0][1] - 7.4)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-6, -28), (-10, -10.5)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (9, -29), (8, -10.5)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 9, -72), (sh[0] + 18, -70)], "back"),
                     ("near", [sh, (sh[0] - 9, -70), (sh[0] - 17, -64)], "front")]
        J["extra"].append(("skateboard", (-1, -2)))
        J["foot"] = "side"
        return J

    if pose == "stand_side":
        hip = (0, -49)
        J["torso"] = _torso_side(hip, -1, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.2, -92.5)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-2, -26), (-4, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (3, -26), (3.5, -4)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 1, -64), (sh[0] + 3, -50)], "back"),
                     ("near", [sh, (sh[0] - 1, -64), (sh[0] + 1, -50)], "front")]
        J["foot"] = "side"
        return J

    if pose == "cyclist":
        hip = (-12, -55)
        J["torso"] = _torso_side(hip, 52, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 6.5, J["torso"][0][1] - 5.5)
        J["tilt"] = 15
        crank = (-3, -19)
        a1, a2 = math.radians(rnd.uniform(-60, 60)), None
        p1 = (crank[0] + 8 * math.cos(a1), crank[1] + 8 * math.sin(a1))
        p2 = (crank[0] - 8 * math.cos(a1), crank[1] - 8 * math.sin(a1))
        def knee(hp, ft):
            mx, my = (hp[0] + ft[0]) / 2, (hp[1] + ft[1]) / 2
            d = math.hypot(ft[0] - hp[0], ft[1] - hp[1])
            L = 23.5
            h = math.sqrt(max(0, L * L - (d / 2) ** 2))
            nx, ny = _norm(-(ft[1] - hp[1]), ft[0] - hp[0])
            c1, c2 = (mx - nx * h, my - ny * h), (mx + nx * h, my + ny * h)
            return c1 if c1[0] > c2[0] else c2
        J["legs"] = [([hip, knee(hip, p2), p2], 8, "back"), ([hip, knee(hip, p1), p1], 8, "front")]
        bar = (24, -58)
        J["arms"] = [("far", [sh, (sh[0] + 9, -68), (bar[0] + 1, bar[1])], "back"),
                     ("near", [sh, (sh[0] + 8, -67), bar], "front")]
        J["bike"] = dict(crank=crank, pedals=(p1, p2), bar=bar, seat=(hip[0] - 1, hip[1] + 4))
        J["foot"] = "side"
        return J

    if pose == "surf_ride":
        hip = (0, -38)
        J["torso"] = _torso_side(hip, 22, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 3, J["torso"][0][1] - 7)
        J["legs"] = [([(hip[0] - 1, hip[1]), (-10, -20), (-16, -4)], 0, "back"),
                     ([(hip[0] + 1, hip[1]), (13, -22), (14, -4)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] + 10, -60), (sh[0] + 20, -64)], "back"),
                     ("near", [sh, (sh[0] - 10, -58), (sh[0] - 20, -60)], "front")]
        J["foot"] = "side"
        return J

    if pose == "surf_sit":
        hip = (0, -6)
        J["torso"] = _torso_side(hip, -2, form)
        sh = (J["torso"][1][0], J["torso"][1][1] + 1.2)
        J["head"] = (J["torso"][0][0] + 1.4, -49.5)
        J["legs"] = [([(hip[0] + 1, hip[1]), (18, -5), (20, 10)], 0, "back"),
                     ([(hip[0] + 2, hip[1]), (19, -4), (18, 11)], 0, "front")]
        J["arms"] = [("far", [sh, (sh[0] - 1, -22), (sh[0] + 4, -7)], "back"),
                     ("near", [sh, (sh[0] + 1, -22), (sh[0] + 7, -6)], "front")]
        J["foot"] = "side"
        return J

    if pose == "carry_child":   # parent seen from the front/back with a child on the shoulders
        hip = (0, -49)
        J["view"] = "front"
        J["torso"] = _torso_front(hip, form)
        sh = 7.6 if f else 8.8
        J["arms"] = [("L", [(-sh, -80.5), (-sh - 6, -88), (-6.5, -94)], "front"), ("R", [(sh, -80.5), (sh + 6, -88), (6.5, -94)], "front")]
        J["legs"] = [([(s * 4.6, -49), (s * 5, -26), (s * 5.3, -4)], None, "front") for s in (-1, 1)]
        J["head"] = (0, -92.5)
        J["foot"] = "front"
        return J

    raise ValueError(f"unknown pose {pose}")


# ------------------------------------------------------------------ the body renderer

def _hair(Pt, view, hx, hy, rx, ry, style, col, layer, facing_tilt=0.0):
    """Hair shapes. layer 'back' = long hair behind the body (front view) / 'over' = on top of the head."""
    if style == "bald":
        return
    if layer == "back":
        if style in ("long",) and view in ("front", "34"):
            Pt.tube([(hx - rx * 0.8, hy - ry * 0.3), (hx - rx * 1.05, hy + ry * 1.2), (hx - rx * 0.95, hy + ry * 2.1)], [rx * 0.9, rx * 0.95, rx * 0.7], col, rim=True)
            Pt.tube([(hx + rx * 0.8, hy - ry * 0.3), (hx + rx * 1.05, hy + ry * 1.2), (hx + rx * 0.95, hy + ry * 2.1)], [rx * 0.9, rx * 0.95, rx * 0.7], col, rim=True)
        if style == "afro" and view in ("front", "34", "back"):
            Pt.ellipse(hx, hy - ry * 0.25, rx * 1.55, ry * 1.25, col)
        return
    base, dk, lt = tones(col, 0.3, 0.32)
    if view == "side":
        if style in ("afro",):
            Pt.ellipse(hx - rx * 0.35, hy - ry * 0.3, rx * 1.4, ry * 1.2, col)
            return
        outer = ell_pts(hx - rx * 0.05, hy - ry * 0.03, rx * 1.1, ry * 1.08, -48, -230, 14)
        nape = (hx - rx * 0.55, hy + ry * (0.75 if style in ("short", "buzz", "curly") else 0.85))
        inner = [nape, (hx - rx * 0.1, hy + ry * 0.05), (hx + rx * 0.15, hy - ry * 0.35), (hx + rx * 0.62, hy - ry * 0.55)]
        cap = outer + inner
        if style == "buzz":
            cap = ell_pts(hx - rx * 0.05, hy - ry * 0.02, rx * 1.03, ry * 1.03, -40, -220, 14) + [(hx - rx * 0.3, hy + ry * 0.2), (hx + rx * 0.4, hy - ry * 0.5)]
        if style == "curly":
            Pt.fill(cap, col)
            for a in range(-200, -40, 26):
                r = math.radians(a)
                Pt.ellipse(hx + rx * 1.02 * math.cos(r), hy + ry * 1.0 * math.sin(r), rx * 0.36, ry * 0.32, col, shade=False)
        else:
            Pt.fill(cap, col)
        Pt.shape(Pt.crescent(hx - rx * 0.05, hy - ry * 0.03, rx * 1.1, ry * 1.08, 0.5), dk, op=0.6)
        if style in ("long", "bob"):
            L = 2.15 if style == "long" else 1.05
            Pt.fill([(hx - rx * 0.35, hy - ry * 0.7), (hx - rx * 1.12, hy - ry * 0.1), (hx - rx * 1.15, hy + ry * L), (hx - rx * 0.7, hy + ry * (L + 0.18)),
                     (hx - rx * 0.25, hy + ry * L * 0.8), (hx - rx * 0.2, hy + ry * 0.3)], col)
            Pt.shape([(hx - rx * 1.1, hy), (hx - rx * 1.13, hy + ry * L), (hx - rx * 0.8, hy + ry * (L + 0.1)), (hx - rx * 0.75, hy + ry * 0.4)], dk, op=0.8)
        if style == "ponytail":
            Pt.tube([(hx - rx * 0.9, hy - ry * 0.45), (hx - rx * 1.55, hy + ry * 0.2), (hx - rx * 1.45, hy + ry * 1.25)], [rx * 0.55, rx * 0.62, rx * 0.25], col)
        if style == "bun":
            Pt.ellipse(hx - rx * 0.75, hy - ry * 0.75, rx * 0.5, ry * 0.45, col)
        if Pt.detail >= 2:
            Pt.shape([(hx - rx * 0.3, hy - ry * 0.98), (hx + rx * 0.35, hy - ry * 0.85), (hx - rx * 0.1, hy - ry * 0.8)], lt, op=0.7)
        return
    # front / 34 / back
    sx = 0.35 if view == "34" else 0.0
    if style == "afro":
        if view == "back":
            Pt.ellipse(hx, hy - ry * 0.2, rx * 1.5, ry * 1.25, col)
        else:
            Pt.shape(ell_pts(hx + sx, hy - ry * 0.1, rx * 1.02, ry * 1.0, 190, 350, 10) + [(hx + rx * 0.7, hy - ry * 0.45), (hx, hy - ry * 0.62), (hx - rx * 0.7, hy - ry * 0.45)], col)
        return
    if view == "back":
        cap = ell_pts(hx, hy - ry * 0.03, rx * 1.08, ry * 1.06, 160, 380, 18) + [(hx + rx * 0.7, hy + ry * 0.7), (hx, hy + ry * (0.95 if style != "buzz" else 0.6)), (hx - rx * 0.7, hy + ry * 0.7)]
        Pt.fill(cap, col)
        Pt.shape(Pt.crescent(hx, hy - ry * 0.03, rx * 1.08, ry * 1.06, 0.55), dk, op=0.7)
        if style in ("long", "bob"):
            L = 2.4 if style == "long" else 1.2
            Pt.fill([(hx - rx * 1.05, hy - ry * 0.2), (hx - rx * 1.12, hy + ry * L), (hx, hy + ry * (L + 0.2)), (hx + rx * 1.12, hy + ry * L), (hx + rx * 1.05, hy - ry * 0.2)], col)
            Pt.shape(tube_side([(hx, hy), (hx, hy + ry * L)], [rx * 2.2, rx * 2.2], Pt.L, 0.4, cap1=False), dk, op=0.6)
        if style == "ponytail":
            Pt.tube([(hx, hy - ry * 0.3), (hx + rx * 0.15, hy + ry * 0.9), (hx, hy + ry * 1.8)], [rx * 0.7, rx * 0.65, rx * 0.25], col)
        if style == "bun":
            Pt.ellipse(hx, hy - ry * 0.75, rx * 0.55, ry * 0.45, col)
        if style == "curly":
            for a in range(160, 381, 30):
                r = math.radians(a)
                Pt.ellipse(hx + rx * 1.02 * math.cos(r), hy + ry * math.sin(r), rx * 0.36, ry * 0.32, col, shade=False)
        return
    # front, 3/4
    top = ell_pts(hx + sx, hy - ry * 0.04, rx * 1.08, ry * 1.07, 165 if style != "buzz" else 180, 375 if style != "buzz" else 360, 16)
    part = 0.45 if style in ("long", "bob", "ponytail", "bun") else 0.6
    hairline = [(hx + rx * 0.98 + sx, hy - ry * 0.05), (hx + rx * 0.55 + sx, hy - ry * part), (hx + sx * 2, hy - ry * (part + 0.12)), (hx - rx * 0.55 + sx, hy - ry * part),
                (hx - rx * 0.98 + sx, hy - ry * 0.05)]
    if style == "buzz":
        hairline = [(hx + rx * 0.9, hy - ry * 0.35), (hx, hy - ry * 0.72), (hx - rx * 0.9, hy - ry * 0.35)]
    Pt.fill(top + hairline, col)
    if style in ("long", "bob"):
        L = 1.9 if style == "long" else 0.95
        for s in (-1, 1):
            Pt.fill([(hx + s * rx * 0.55 + sx, hy - ry * 0.6), (hx + s * rx * 1.12 + sx, hy - ry * 0.1), (hx + s * rx * 1.12 + sx, hy + ry * L),
                     (hx + s * rx * 0.75 + sx, hy + ry * L), (hx + s * rx * 0.72 + sx, hy + ry * 0.1)], col)
    if style == "curly":
        for a in range(170, 371, 25):
            r = math.radians(a)
            Pt.ellipse(hx + sx + rx * 1.02 * math.cos(r), hy + ry * 1.0 * math.sin(r), rx * 0.34, ry * 0.3, col, shade=False)
    if style == "bun":
        Pt.ellipse(hx + sx, hy - ry * 1.12, rx * 0.5, ry * 0.4, col)
    Pt.shape(Pt.crescent(hx + sx, hy - ry * 0.04, rx * 1.08, ry * 1.07, 0.4), dk, op=0.55)


def pal_band(col):
    return mix(col, "#B8503E", 0.6)


def _hat(Pt, view, hx, hy, rx, ry, kind, col):
    if not kind:
        return
    base, dk, lt = tones(col)
    if kind == "cap":
        if view == "side":
            Pt.fill(ell_pts(hx - rx * 0.05, hy - ry * 0.25, rx * 1.12, ry * 0.85, 180, 360, 12), col)
            Pt.fill([(hx + rx * 0.5, hy - ry * 0.32), (hx + rx * 1.75, hy - ry * 0.18), (hx + rx * 1.7, hy - ry * 0.05), (hx + rx * 0.6, hy - ry * 0.12)], dk)
        else:
            Pt.fill(ell_pts(hx, hy - ry * 0.3, rx * 1.12, ry * 0.85, 180, 360, 12), col)
            if view != "back":
                Pt.ellipse(hx, hy - ry * 0.32, rx * 0.95, ry * 0.22, mix(col, SHADOW, 0.25), shade=False)
        return
    if kind == "sunhat":
        Pt.ellipse(hx, hy - ry * 0.45, rx * (2.2 if view != "side" else 2.1), ry * 0.36, col, rot=0)
        Pt.fill(ell_pts(hx - (rx * 0.1 if view == "side" else 0), hy - ry * 0.5, rx * 1.05, ry * 0.9, 180, 360, 12), col)
        Pt.shape([(hx - rx * 1.0, hy - ry * 0.58), (hx + rx * 1.0, hy - ry * 0.58), (hx + rx * 1.02, hy - ry * 0.75), (hx - rx * 1.02, hy - ry * 0.75)], mix(col, "#8A3A2A", 0.5))
        return
    if kind == "cowboy":
        Pt.fill([(hx - rx * 2.0, hy - ry * 0.45), (hx - rx * 1.2, hy - ry * 0.75), (hx + rx * 1.2, hy - ry * 0.75), (hx + rx * 2.0, hy - ry * 0.45), (hx + rx * 1.5, hy - ry * 0.5), (hx - rx * 1.5, hy - ry * 0.5)], col)
        Pt.fill([(hx - rx * 0.95, hy - ry * 0.7), (hx - rx * 0.85, hy - ry * 1.35), (hx, hy - ry * 1.2), (hx + rx * 0.85, hy - ry * 1.35), (hx + rx * 0.95, hy - ry * 0.7)], col)
        return
    if kind == "tricorn":
        Pt.fill([(hx - rx * 1.7, hy - ry * 0.55), (hx - rx * 1.1, hy - ry * 1.35), (hx, hy - ry * 1.1), (hx + rx * 1.1, hy - ry * 1.35), (hx + rx * 1.7, hy - ry * 0.55), (hx, hy - ry * 0.75)], col)
        Pt.shape([(hx - rx * 1.6, hy - ry * 0.6), (hx, hy - ry * 0.8), (hx + rx * 1.6, hy - ry * 0.6), (hx, hy - ry * 0.68)], "#D8B04A", op=0.8)
        return
    if kind == "fedora":
        Pt.fill([(hx - rx * 1.75, hy - ry * 0.48), (hx - rx * 1.0, hy - ry * 0.62), (hx + rx * 1.0, hy - ry * 0.62), (hx + rx * 1.75, hy - ry * 0.48), (hx + rx * 1.1, hy - ry * 0.4), (hx - rx * 1.1, hy - ry * 0.4)], col)
        Pt.fill([(hx - rx * 0.95, hy - ry * 0.55), (hx - rx * 0.85, hy - ry * 1.25), (hx, hy - ry * 1.12), (hx + rx * 0.85, hy - ry * 1.25), (hx + rx * 0.95, hy - ry * 0.55)], col)
        Pt.shape([(hx - rx * 0.95, hy - ry * 0.6), (hx + rx * 0.95, hy - ry * 0.6), (hx + rx * 0.93, hy - ry * 0.75), (hx - rx * 0.93, hy - ry * 0.75)], pal_band(col))
        return
    if kind == "beanie":
        Pt.fill(ell_pts(hx, hy - ry * 0.25, rx * 1.1, ry * 0.95, 180, 360, 12) + [(hx + rx * 1.1, hy - ry * 0.12), (hx - rx * 1.1, hy - ry * 0.12)], col)
        Pt.shape([(hx - rx * 1.1, hy - ry * 0.3), (hx + rx * 1.1, hy - ry * 0.3), (hx + rx * 1.1, hy - ry * 0.08), (hx - rx * 1.1, hy - ry * 0.08)], dk)
        return
    if kind == "helmet":
        Pt.fill(ell_pts(hx - rx * 0.1, hy - ry * 0.3, rx * 1.25, ry * 0.95, 175, 365, 12), col)
        Pt.shape([(hx - rx * 0.6, hy - ry * 1.05), (hx + rx * 0.5, hy - ry * 1.1)], lt)
        return


def _shoe(Pt, an, angle, col, view, s=1.0, side_sign=0):
    if view == "side":
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(-2.6, -2.2), (-2.8, 0.8), (6.8, 1.0), (7.6, -0.4), (5.2, -2.6), (1.2, -3.2)]
        pts = [(an[0] + (x * ca - y * sa) * s, an[1] + 2.2 * s + (x * sa + y * ca) * s) for x, y in pts]
        Pt.fill(pts, col)
        if Pt.detail >= 1:
            sole = [pts[1], pts[2], (pts[2][0] - 0.2 * s, pts[2][1] - 0.9 * s), (pts[1][0], pts[1][1] - 0.9 * s)]
            Pt.shape(sole, mix(col, SHADOW, 0.45))
    else:
        Pt.ellipse(an[0] + side_sign * 0.9 * s, an[1] + 2.4 * s, 3.0 * s, 2.1 * s, col)


def _dog(Pt, x, base, s, col, facing=1):
    """Medium dog trotting toward +x (local units of the walker)."""
    d = []
    def p(px, py):
        return (x + px * s * facing, base + py * s)
    body = [p(-11, -21), p(-6, -24), p(4, -24.5), p(9, -24), p(11, -19), p(8, -15.5), p(-2, -16), p(-10, -16)]
    leg_cols = mix(col, SHADOW, 0.3)
    Pt.tube([p(-8, -18), p(-11, -9), p(-12, -1)], [3.4 * s, 2.4 * s, 2 * s], leg_cols, shade=False)
    Pt.tube([p(7, -18), p(9, -9), p(12, -1.5)], [3.4 * s, 2.4 * s, 2 * s], leg_cols, shade=False)
    Pt.tube([p(-12, -21), p(-17, -26), p(-19, -30)], [2.6 * s, 2 * s, 1.2 * s], col, shade=False)
    Pt.fill(body, col)
    Pt.shape(tube_side([p(-10, -19.5), p(9, -19.5)], [8 * s, 8 * s], Pt.L, 0.45, cap1=False), mix(col, SHADOW, 0.3))
    Pt.tube([p(-6, -18), p(-4, -9), p(-5, -1)], [3.6 * s, 2.5 * s, 2 * s], col, shade=False)
    Pt.tube([p(5, -18), p(5, -9), p(6, -1)], [3.6 * s, 2.5 * s, 2 * s], col, shade=False)
    Pt.tube([p(9, -22), p(12, -27)], [6 * s, 5 * s], col, shade=False, cap1=False)
    Pt.ellipse(*p(13.5, -29), 4.2 * s, 3.4 * s, col)
    Pt.fill([p(15, -31), p(20.5, -29.5), p(20.5, -27), p(15.5, -26.5)], col)
    Pt.ellipse(*p(20.4, -28.7), 1.0 * s, 0.9 * s, "#1A1418", shade=False, rim=False)
    Pt.fill([p(11, -31.5), p(12.5, -34.5), p(14, -30.5), p(13, -27)], mix(col, SHADOW, 0.4))
    return p(11.5, -26)


def _board(Pt, cx, cy, col, stripe, L=54.0, H=7.4, tilt=-5.0):
    """A longboard carried under the arm, seen from below at an angle: a long lens with a pointed, lifted nose,
    a rounded tail, a fin, the stringer and shaded rails."""
    a = math.radians(tilt)
    def r(px, py):
        return (cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a))
    top, bot = [], []
    for i in range(25):
        t = -1 + 2 * i / 24                     # -1 tail .. +1 nose
        w = H * (1 - abs(t) ** 2.6) ** 0.55 if t > 0 else H * (1 - abs(t) ** 4) ** 0.45
        lift = 3.2 * max(0.0, t) ** 3          # nose rocker
        top.append(r(t * L, -w - lift))
        bot.append(r(t * L, w * 0.8 - lift))
    outline = top + bot[::-1]
    Pt.fill(outline, col, smooth=False)
    # lower rail in shade, a lit band along the upper rail
    Pt.shape(bot[2:-2] + [(x, y - H * 0.45) for x, y in bot[2:-2][::-1]], mix(col, SHADOW, 0.3), smooth=False)
    Pt.shape(top[2:-3] + [(x, y + H * 0.28) for x, y in top[2:-3][::-1]], mix(col, LIGHT, 0.45), op=0.8, smooth=False)
    # stringer and a coloured stripe near the nose
    Pt.add(f'<path d="M {_f(r(-L * 0.96, 0)[0])} {_f(r(-L * 0.96, 0)[1])} L {_f(r(L * 0.93, -2.4)[0])} {_f(r(L * 0.93, -2.4)[1])}" '
           f'stroke="{Pt.c(mix(col, "#8A6A4A", 0.45))}" stroke-width="0.8" fill="none" opacity="0.8"/>')
    Pt.shape([r(L * 0.55, -H * 0.8), r(L * 0.62, -H * 0.75), r(L * 0.62, H * 0.6), r(L * 0.55, H * 0.68)], stripe, smooth=False)
    # fin under the tail
    Pt.fill([r(-L * 0.86, H * 0.55), r(-L * 0.78, H * 0.6), r(-L * 0.86, H * 1.75), r(-L * 0.92, H * 1.55)], mix(col, SHADOW, 0.5), smooth=False, rim=False)


def _bike(Pt, b, col, k):
    frame = col
    rr, fr = (-30, -19), (31, -19)
    R = 18.5
    sw = max(1.6, 1.1 / k)
    tw = max(2.0, 1.5 / k)
    for c in (rr, fr):
        Pt.add(f'<circle cx="{_f(c[0])}" cy="{_f(c[1])}" r="{R}" fill="none" stroke="{Pt.c("#1E1A20")}" stroke-width="{_f(tw)}"/>')
        Pt.add(f'<circle cx="{_f(c[0])}" cy="{_f(c[1])}" r="{R - 3.5}" fill="none" stroke="{Pt.c("#B8B4B0")}" stroke-width="{_f(sw * 0.35)}" opacity="0.7"/>')
        if Pt.rim:
            Pt.add(f'<path d="M {_f(c[0] + Pt.lx * R * 0.2)} {_f(c[1] - R * 0.98)} A {R} {R} 0 0 {1 if Pt.lx > 0 else 0} {_f(c[0] + Pt.lx * R)} {_f(c[1])}" fill="none" stroke="{Pt.rim}" stroke-width="{_f(sw * 0.7)}" opacity="0.8"/>')
    cr = b["crank"]
    seat = b["seat"]
    bar = b["bar"]
    head = (bar[0] - 2, bar[1] + 6)
    lines = [(rr, cr), (cr, seat), (rr, (seat[0] + 1, seat[1] + 3)), (cr, (head[0] - 1, head[1] + 4)), ((seat[0] + 1, seat[1] + 3), (head[0], head[1] + 1)), (head, fr), (head, bar)]
    d = " ".join(f"M {_f(a[0])} {_f(a[1])} L {_f(c[0])} {_f(c[1])}" for a, c in lines)
    Pt.add(f'<path d="{d}" fill="none" stroke="{Pt.c(frame)}" stroke-width="{_f(sw)}" stroke-linecap="round" stroke-linejoin="round"/>')
    Pt.add(f'<path d="M {_f(seat[0] - 4)} {_f(seat[1])} L {_f(seat[0] + 4)} {_f(seat[1] + 0.6)}" stroke="{Pt.c("#1E1A20")}" stroke-width="{_f(sw * 1.4)}" stroke-linecap="round"/>')
    Pt.add(f'<path d="M {_f(bar[0])} {_f(bar[1])} q 3 -0.5 3.5 2.5" fill="none" stroke="{Pt.c("#1E1A20")}" stroke-width="{_f(sw)}" stroke-linecap="round"/>')
    Pt.add(f'<circle cx="{_f(cr[0])}" cy="{_f(cr[1])}" r="2.6" fill="{Pt.c("#3A3638")}"/>')


def _render(Pt, J, pal, child=False, pose="", parts=None):
    f = pal["form"] == "f"
    sil = pal.get("silhouette")
    view = J["view"]
    skin, hair = pal["skin"], pal["hair"]
    top, bottom, shoes = pal["top"], pal["bottom"], pal["shoes"]
    tk, bk = pal["top_kind"], pal["bottom_kind"]
    if tk == "dress":
        bk = "none"
    if tk == "swim" and bk not in ("swim", "shorts"):
        bk = "swim"
    sleeve = {"tee": 0.42, "tank": 0.0, "long": 1.0, "jacket": 1.0, "coat": 1.0, "sweater": 1.0, "dress": 0.22 if f else 0.4, "swim": 0.0}.get(tk, 0.42)
    hx, hy = J["head"]
    rx, ry = (7.6, 8.6) if child else (5.9, 6.9)
    # body mass for the figure's size (see Painter): wider torso, thicker limbs, a slightly bigger head
    tb, hb = Pt.tbulk, Pt.hbulk
    J = dict(J)
    J["torso"] = [(x_, y_, w_ * tb) for x_, y_, w_ in J["torso"]]
    if view != "side" and tb != 1.0:
        def spread(pts, k):
            return [(p[0] * k,) + tuple(p[1:]) for p in pts]
        J["arms"] = [(n, spread(pts, tb), lay) for n, pts, lay in J["arms"]]
        J["legs"] = [(spread(pts, 0.5 + 0.5 * tb), fa, lay) for pts, fa, lay in J["legs"]]
    if hb != 1.0:
        hy -= ry * (hb - 1.0) * 0.8
        rx, ry = rx * hb, ry * hb
        J["head"] = (hx, hy)
    # child: bigger head, compress body below the chin toward the feet
    darker = lambda c, t=0.22: mix(c, SHADOW, t)

    def legs_layer(layer):
        if pal.get("no_legs"):
            return
        for pts, fa, lay in J["legs"]:
            if lay != layer:
                continue
            dim = (lambda c: darker(c, 0.2)) if (lay == "back" and view == "side") else (lambda c: c)
            ws = [w * Pt.bulk for w in (9.2 if f else 9.8, 6.4 if f else 6.8, 4.2)]
            if child:
                ws = [w * 1.05 for w in ws]
            trousers = bk == "trousers"
            Pt.tube(pts, ws, dim(skin) if not trousers else dim(bottom), cap0=False)
            if not trousers:
                t = {"shorts": 0.42, "swim": 0.18, "skirt": 0.0, "none": 0.0}.get(bk, 0.0)
                if t > 0:
                    cp, cw = cut(pts, [w + 1.0 for w in ws], t)
                    Pt.tube(cp, cw, dim(bottom), cap0=False, cap1=False)
            ss = 0.5 + 0.5 * Pt.bulk
            if J.get("foot") == "side":
                _shoe(Pt, pts[-1], fa or 0, dim(shoes), "side", s=ss)
            elif not pose.startswith("sit_back"):
                side = -1 if pts[-1][0] < 0 else 1
                _shoe(Pt, pts[-1], 0, dim(shoes), "front", s=ss, side_sign=side)

    def arm(name, pts, lay):
        dim = (lambda c: darker(c, 0.2)) if (lay == "back" and view == "side") else (lambda c: c)
        ws = [w * Pt.bulk for w in (5.8 if f else 6.6, 4.7 if f else 5.3, 3.5 if f else 3.9)]
        if child:
            ws = [w * 1.05 for w in ws]
        Pt.tube(pts, ws, dim(skin), cap0=True)
        if sleeve > 0:
            sw = [w + (1.6 if tk in ("jacket", "coat", "sweater") else 1.0) for w in ws]
            cp, cw = cut(pts, sw, sleeve)
            Pt.tube(cp, cw, dim(top), cap1=sleeve < 1.0 or True)
        # hand
        hp = pts[-1]
        d = _norm(hp[0] - pts[-2][0], hp[1] - pts[-2][1])
        hk = 0.55 + 0.45 * Pt.bulk
        Pt.ellipse(hp[0] + d[0] * 2.2 * hk, hp[1] + d[1] * 2.2 * hk, (2.3 if f else 2.6) * hk, (2.7 if f else 3.0) * hk, dim(skin), rot=math.degrees(math.atan2(d[1], d[0])) + 90, shade=Pt.detail >= 2)

    def torso_layer():
        T = J["torso"]
        pts = [(x, y) for x, y, w in T]
        ws = [w for x, y, w in T]
        bottom_col = bottom if bk not in ("none", "skirt") else (top if tk == "dress" else bottom)
        if tk == "swim":
            # skin torso + swimsuit
            Pt.tube(pts, ws, skin)
            lerp = lambda a_, b_, t: tuple(u + (v - u) * t for u, v in zip(a_, b_))
            if f:
                # bikini top: a band across the chest, slightly wider than the ribcage
                c0, c1 = lerp(T[1], T[2], 0.3), lerp(T[2], T[3], 0.3)
                Pt.tube([c0[:2], c1[:2]], [c0[2] + 0.8, c1[2] + 0.8], top, cap0=False, cap1=False, rim=False)
            # trunks / bikini bottom: from below the waist over the hips, a soft V between the legs
            a_, b_ = lerp(T[3], T[4], 0.35 if bk == "swim" else 0.1), T[4]
            low = 5.5 if bk == "swim" else 9.0
            band = [(a_[0] - a_[2] / 2 - 0.3, a_[1]), (a_[0] + a_[2] / 2 + 0.3, a_[1]), (b_[0] + b_[2] / 2 + 0.6, b_[1] + low * 0.7),
                    (b_[0] + b_[2] * 0.12, b_[1] + low), (b_[0] - b_[2] * 0.12, b_[1] + low), (b_[0] - b_[2] / 2 - 0.6, b_[1] + low * 0.7)]
            Pt.fill(band, bottom, smooth=False)
            Pt.shape(tube_side([a_[:2], (b_[0], b_[1] + low * 0.6)], [a_[2] + 0.6, b_[2] + 1.2], Pt.L, 0.4, cap1=False), darker(bottom, 0.3))
            return
        Pt.tube(pts[2:], ws[2:], bottom_col, cap0=False)
        hem = 1.0 if tk in ("tee", "long", "tank", "sweater") else 1.0
        tp, tw = cut(pts, ws, 0.86 if tk in ("tee", "long", "tank", "sweater", "dress") else 1.0)
        if tk in ("jacket", "coat"):
            tw = [w + 1.2 for w in tw]
        Pt.tube(tp, tw, top, cap1=False)
        if tk in ("tee", "long", "tank", "sweater") and Pt.detail >= 2 and not sil:
            # hem line
            a, b = tp[-1], tw[-1]
            Pt.add(f'<path d="M {_f(a[0] - b / 2)} {_f(a[1])} L {_f(a[0] + b / 2)} {_f(a[1])}" stroke="{Pt.c(darker(top, 0.35))}" stroke-width="0.9" opacity="0.6"/>')
        if tk == "tank" and view != "back" and not sil:
            x0, y0, w0 = T[0]
            Pt.shape([(x0 - w0 * 0.35, y0 - 0.5), (x0 + w0 * 0.35, y0 - 0.5), (x0 + w0 * 0.3, y0 + 4.5), (x0 - w0 * 0.3, y0 + 4.5)], skin)
        if tk in ("tee", "dress", "sweater") and view in ("front", "34") and not sil:
            x0, y0, w0 = T[0]
            Pt.shape(ell_pts(x0 + (0.8 if view == "34" else 0), y0 - 0.6, w0 * 0.34, 3.0, 0, 180, 8), skin)
        if tk == "jacket" and view in ("front", "34") and not sil:
            x0, y0, w0 = T[0]
            x3, y3, w3 = T[4]
            Pt.shape([(x0 - 2.4, y0 - 0.2), (x0 + 2.4, y0 - 0.2), (x3 + 1.2, y3 - 6), (x3 - 1.2, y3 - 6)], pal.get("inner", "#F2E6D0"))
            Pt.add(f'<path d="M {_f(x0 - 2.4)} {_f(y0)} L {_f(x0 - 5)} {_f(y0 + 9)} M {_f(x0 + 2.4)} {_f(y0)} L {_f(x0 + 5)} {_f(y0 + 9)}" stroke="{Pt.c(darker(top, 0.4))}" stroke-width="0.9" fill="none"/>')
        if tk == "jacket" and view == "side" and not sil:
            x0, y0, w0 = T[0]
            x3, y3, w3 = T[3]
            Pt.add(f'<path d="M {_f(x0 + w0 * 0.25)} {_f(y0 + 1)} L {_f(x3 + w3 * 0.42)} {_f(y3 + 8)}" stroke="{Pt.c(darker(top, 0.4))}" stroke-width="0.9" fill="none" opacity="0.8"/>')
        if bk in ("trousers", "shorts") and Pt.detail >= 2 and tk not in ("jacket", "coat") and not sil:
            x3, y3, w3 = T[3]
            # belt
            Pt.add(f'<path d="M {_f(x3 - w3 / 2)} {_f(y3 + 3.2)} L {_f(x3 + w3 / 2)} {_f(y3 + 3.2)}" stroke="{Pt.c(darker(bottom, 0.45))}" stroke-width="1.3" opacity="0.7"/>')

    def skirt_layer():
        T = J["torso"]
        x3, y3, w3 = T[3]
        x4, y4, w4 = T[4]
        if tk == "dress" or bk == "skirt":
            col = top if tk == "dress" else bottom
            sit = (pose in SEATED)
            if sit and view == "side":
                # skirt drapes over the thighs
                kn = J["legs"][-1][0][1]
                pts = [(x3 - w3 / 2, y3 + 2), (x3 + w3 / 2, y3 + 2), (x4 + w4 / 2, y4 - 4.5), (kn[0] + 1.5, kn[1] - 4.8), (kn[0] + 3.8, kn[1] - 2),
                       (kn[0] + 3.2, kn[1] + 5), (kn[0] - 3, kn[1] + 5.5), (x4 - w4 / 2 - 0.5, y4 + 4)]
                Pt.fill(pts, col, smooth=False)
                Pt.shape([(x4 - w4 / 2 - 0.5, y4 + 4), (kn[0] - 3, kn[1] + 5.5), (kn[0] + 3.2, kn[1] + 5), (kn[0] + 2.5, kn[1] + 1.5), (x4, y4 + 1)], darker(col, 0.3), smooth=False)
                return
            hem = 22 if tk == "dress" else 26
            if sit:
                hem = y4 + 8
            flare = 1.55 if f else 1.4
            # legs in side view swing: follow the knees
            if view == "side":
                kf = J["legs"][-1][0][1]
                kb = J["legs"][0][0][1]
                lo = min(kf[0], kb[0], x4 - w4 / 2) - 3
                hi = max(kf[0], kb[0], x4 + w4 / 2) + 3
                yh = -hem if not sit else hem
                pts = [(x3 - w3 / 2, y3 + 1), (x3 + w3 / 2, y3 + 1), (x4 + w4 / 2 + 1, y4), (hi, yh), ((hi + lo) / 2, yh + 1.5), (lo, yh)]
            else:
                yh = -hem if not sit else hem
                pts = [(x3 - w3 / 2, y3 + 1), (x3 + w3 / 2, y3 + 1), (x4 + w4 / 2 + 1, y4), (x4 + w4 / 2 * flare + 2, yh), (x4, yh + 1.8), (x4 - w4 / 2 * flare - 2, yh)]
            base, dk, lt = tones(col)
            Pt.fill(pts, col, smooth=True)
            if not sil:
                # folds
                cx = (pts[3][0] + pts[5][0]) / 2
                Pt.shape(tube_side([(x3, y3 + 1), (cx, yh)], [w3, abs(pts[3][0] - pts[5][0])], Pt.L, 0.4, cap1=False), dk)
                if Pt.detail >= 2:
                    for t in (0.35, 0.65):
                        xa = x3 - w3 / 2 + w3 * t
                        xb = pts[5][0] + (pts[3][0] - pts[5][0]) * t
                        Pt.add(f'<path d="M {_f(xa)} {_f(y3 + 6)} Q {_f((xa + xb) / 2 + 0.6)} {_f((y3 + yh) / 2)} {_f(xb)} {_f(yh)}" stroke="{Pt.c(dk)}" stroke-width="0.9" fill="none" opacity="0.7"/>')
        if tk == "coat":
            # long coat skirt over the thighs
            pts_l = [l[0] for l in J["legs"]]
            if view == "side":
                kf = pts_l[-1][1]
                kb = pts_l[0][1]
                lo = min(kf[0], kb[0], x4 - w4 / 2) - 2
                hi = max(kf[0], kb[0], x4 + w4 / 2) + 2
                yh = max(kf[1], kb[1]) - 4 if not (pose in SEATED) else y4 + 4
                pts = [(x3 - w3 / 2 - 0.6, y3), (x3 + w3 / 2 + 0.6, y3), (x4 + w4 / 2 + 1.2, y4), (hi, yh), (lo, yh)]
            else:
                yh = -30 if not (pose in SEATED) else y4 + 4
                pts = [(x3 - w3 / 2 - 0.6, y3), (x3 + w3 / 2 + 0.6, y3), (x4 + w4 / 2 + 1.5, y4), (x4 + w4 / 2 + 3, yh), (x4 - w4 / 2 - 3, yh), (x4 - w4 / 2 - 1.5, y4)]
            base, dk, lt = tones(top)
            Pt.fill(pts, top, smooth=False)
            Pt.shape(tube_side([(x3, y3), (x4, yh)], [w3 + 1.2, w4 + 5], Pt.L, 0.45, cap1=False), dk)
            if view in ("front", "34") and not sil:
                Pt.add(f'<path d="M {_f(x3)} {_f(y3 - 18)} L {_f(x4)} {_f(yh)}" stroke="{Pt.c(darker(top, 0.45))}" stroke-width="0.9"/>')

    def neck_head():
        nx, ny = J["torso"][0][0], J["torso"][0][1]
        Pt.tube([(nx, ny + 1), ((nx + hx) / 2, (ny + hy) / 2 + 2.5)], [(4.8 if f else 5.4) * tb, (4.4 if f else 5.0) * tb], darker(skin, 0.12) if view != "back" else skin, cap1=False, cap0=False)
        if view == "back":
            Pt.ellipse(hx, hy, rx, ry, skin, rot=J["tilt"])
            if Pt.detail >= 1 and pal["hair_style"] not in ("afro",):
                Pt.ellipse(hx - rx * 0.98, hy + 0.5, 1.2, 1.9, skin, shade=False)
                Pt.ellipse(hx + rx * 0.98, hy + 0.5, 1.2, 1.9, skin, shade=False)
        elif view == "side":
            pts = ell_pts(hx, hy, rx, ry, 0, 360, 28, J["tilt"])[:-1]
            Pt.fill(pts, skin)
            if Pt.detail >= 1:
                # nose and chin
                a = math.radians(J["tilt"])
                def rot(px, py):
                    return (hx + px * math.cos(a) - py * math.sin(a), hy + px * math.sin(a) + py * math.cos(a))
                Pt.fill([rot(rx * 0.86, -ry * 0.12), rot(rx * 1.2, ry * 0.2), rot(rx * 0.86, ry * 0.32)], skin, smooth=False, rim=False)
                Pt.fill([rot(rx * 0.3, ry * 0.75), rot(rx * 0.78, ry * 0.62), rot(rx * 0.6, ry * 0.95), rot(rx * 0.1, ry * 0.98)], skin, rim=False)
            Pt.shape(Pt.crescent(hx, hy, rx, ry, 0.75, J["tilt"]), darker(skin, 0.22))
            if Pt.detail >= 2 and pal["hair_style"] not in ("long", "afro"):
                Pt.ellipse(hx - rx * 0.12, hy + ry * 0.08, 1.2, 1.7, darker(skin, 0.18), shade=False)
        else:
            Pt.ellipse(hx, hy, rx, ry, skin, rot=J["tilt"], sh=0.2)
            if Pt.detail >= 1 and pal["hair_style"] not in ("long", "afro", "bob"):
                Pt.ellipse(hx - rx * 0.98, hy + 0.6, 1.2, 1.8, skin, shade=False)
                Pt.ellipse(hx + rx * 0.98, hy + 0.6, 1.2, 1.8, skin, shade=False)
        _hair(Pt, view, hx, hy, rx, ry, pal["hair_style"], hair, "over")
        _hat(Pt, view, hx, hy, rx, ry, pal.get("hat_kind"), pal["hat"])

    if parts == "legs":
        legs_layer("back")
        legs_layer("front")
        return
    if parts == "arms":
        for name, pts, lay in J["arms"]:
            arm(name, pts, lay)
        return
    # ---- props behind
    pack_side = (pose == "hiker" or pal.get("pack")) and view == "side"
    if pack_side:
        T = J["torso"]
        x0, y0, _ = T[1]
        x3, y3, _ = T[3]
        cx, cy = (x0 + x3) / 2 - 8.5, (y0 + y3) / 2 + 1
        Pt.fill([(cx - 5, cy - 14), (cx + 5, cy - 15), (cx + 6.5, cy + 12), (cx - 6, cy + 14)], pal["bag"])
        Pt.shape(tube_side([(cx, cy - 14), (cx, cy + 13)], [11, 13], Pt.L, 0.45, cap1=False), darker(pal["bag"], 0.35))
        Pt.ellipse(cx - 1, cy + 16, 5.5, 2.5, darker(pal["bag"], 0.1))
    if view in ("front", "34"):
        _hair(Pt, view, hx, hy, rx, ry, pal["hair_style"], hair, "back")
    if view == "back":
        _hair(Pt, view, hx, hy, rx, ry, pal["hair_style"], hair, "back")
    # ---- body
    side = view == "side"
    for name, pts, lay in J["arms"]:
        if lay == "back":
            arm(name, pts, lay)
    legs_layer("back")
    legs_layer("front")
    if (pose in SEATED) and view != "side":
        pass
    if pose == "lean_back" or view == "back":
        torso_layer()
        skirt_layer()
        if pal.get("pack") and view == "back":
            T = J["torso"]
            x1, y1, w1 = T[1]
            x3, y3, w3 = T[3]
            pw = w1 * 0.36
            Pt.fill([(x1 - pw, y1 + 2), (x1 + pw, y1 + 2), (x3 + pw * 1.1, y3 + 5), (x3 - pw * 1.1, y3 + 5)], pal["bag"])
            Pt.shape(tube_side([(x1, y1 + 2), (x3, y3 + 5)], [pw * 2, pw * 2.2], Pt.L, 0.4, cap1=False), darker(pal["bag"], 0.35))
            Pt.shape([(x1 - pw * 0.8, y3 - 3), (x1 + pw * 0.8, y3 - 3), (x1 + pw * 0.8, y3 + 1), (x1 - pw * 0.8, y3 + 1)], darker(pal["bag"], 0.2))
        neck_head()
        for name, pts, lay in J["arms"]:
            if lay == "front":
                arm(name, pts, lay)
    else:
        torso_layer()
        skirt_layer()
        if pack_side:
            T = J["torso"]
            x0, y0, w0 = T[0]
            Pt.add(f'<path d="M {_f(x0 - 2)} {_f(y0 + 1)} Q {_f(x0 + 4)} {_f(y0 + 6)} {_f(T[2][0] - 1)} {_f(T[2][1] + 6)}" stroke="{Pt.c(darker(pal["bag"], 0.3))}" stroke-width="1.8" fill="none"/>')
        neck_head()
        if pose == "surfer":
            _board(Pt, J["torso"][2][0] + 3, -53, pal["board"], pal.get("accent", "#E2603E"))
        for name, pts, lay in J["arms"]:
            if lay == "front":
                arm(name, pts, lay)
    if pose == "hiker" and view == "side":
        hp = J["arms"][1][1][-1]
        Pt.add(f'<path d="M {_f(hp[0] + 0.5)} {_f(hp[1] - 4)} L {_f(hp[0] + 9)} {_f(0)}" stroke="{Pt.c("#3A3036")}" stroke-width="{_f(max(1.3, 0.9 / Pt.k))}" stroke-linecap="round"/>')
    for kind, at in J["extra"]:
        if kind == "book":
            Pt.fill([(at[0] - 1, at[1] - 5), (at[0] + 4.5, at[1] - 3.5), (at[0] + 4, at[1] + 4), (at[0] - 1.5, at[1] + 2.5)], pal.get("accent", "#C8573E"), smooth=False)
            Pt.shape([(at[0] - 0.4, at[1] - 4.2), (at[0] + 3.6, at[1] - 3), (at[0] + 3.2, at[1] + 2.8), (at[0] - 0.8, at[1] + 1.8)], "#F4ECDC", smooth=False)
        if kind == "trumpet":
            a = math.radians(-16)
            def r(px, py):
                return (at[0] + px * math.cos(a) - py * math.sin(a), at[1] + px * math.sin(a) + py * math.cos(a))
            brass = pal.get("brass", "#E8B64A")
            Pt.add(f'<path d="M {_f(r(0, 0)[0])} {_f(r(0, 0)[1])} L {_f(r(22, 0)[0])} {_f(r(22, 0)[1])}" stroke="{Pt.c(brass)}" stroke-width="2.2" stroke-linecap="round"/>')
            Pt.fill([r(6, 0), r(14, 0), r(14, 5), r(6, 5)], mix(brass, SHADOW, 0.2), smooth=False)
            Pt.fill([r(20, -1.2), r(29, -6.5), r(29, 6.5), r(20, 1.2)], brass, smooth=False)
            Pt.ellipse(*r(29, 0), 1.6, 6.5, mix(brass, "#FFFFFF", 0.55), shade=False, rot=-16, rim=False)
        if kind == "guitar":
            g = pal.get("guitar", "#C8783A")
            a = math.radians(-24)
            def r(px, py):
                return (at[0] + px * math.cos(a) - py * math.sin(a), at[1] + px * math.sin(a) + py * math.cos(a))
            Pt.fill([r(12, -1.3), r(33, -1.1), r(33, 1.1), r(12, 1.3)], "#3A2A22", smooth=False)
            Pt.fill([r(32, -2.0), r(37.5, -2.3), r(37.5, 2.3), r(32, 2.0)], "#2A1E1A", smooth=False)
            Pt.ellipse(*r(-7, 0), 9.5, 8.5, g, rot=-24)
            Pt.ellipse(*r(5, 0), 7.5, 6.6, g, rot=-24)
            Pt.ellipse(*r(1, 0), 2.4, 2.4, "#2A1E1A", shade=False, rim=False)
            Pt.fill([r(-12, -1.2), r(-10, -1.2), r(-10, 1.2), r(-12, 1.2)], "#2A1E1A", smooth=False, rim=False)
            # strumming hand over the body
            ln = J["arms"][0][1]
            Pt.tube(ln[1:], [4.8, 3.8], pal["skin"])
            Pt.ellipse(ln[-1][0] + 1.2, ln[-1][1] + 0.6, 2.4, 2.8, pal["skin"], shade=False)
        if kind == "front_bike":
            dk = "#1A1620"
            Pt.add(f'<ellipse cx="0" cy="-17" rx="4.2" ry="17" fill="none" stroke="{Pt.c(dk)}" stroke-width="5"/>')
            Pt.add(f'<path d="M -3 -34 L -2.4 -60 M 3 -34 L 2.4 -60" stroke="{Pt.c("#8A8690")}" stroke-width="2"/>')
            Pt.add(f'<path d="M -15 -66 Q 0 -63 15 -66" stroke="{Pt.c("#2A2430")}" stroke-width="3.4" fill="none" stroke-linecap="round"/>')
            Pt.add(f'<circle cx="0" cy="-50" r="4" fill="#FFF4D0"/>')
            for s_ in (-1, 1):
                Pt.ellipse(s_ * 13.8, -65.5, 2.6, 2.6, pal["skin"], shade=False)
        if kind == "skateboard":
            Pt.fill([(at[0] - 19, at[1] - 3.5), (at[0] + 19, at[1] - 3.5), (at[0] + 21, at[1] - 5.5), (at[0] + 21, at[1] - 2), (at[0] - 21, at[1] - 2), (at[0] - 21, at[1] - 5.5)],
                    pal.get("board", "#C8573E"), smooth=False)
            for wx in (-13, 13):
                Pt.ellipse(at[0] + wx, at[1] + 0.2, 2.2, 2.2, "#2A2228", shade=False, rim=False)
        if kind == "camera":
            Pt.fill([(at[0] - 3, at[1] - 2.8), (at[0] + 3.5, at[1] - 2.8), (at[0] + 3.5, at[1] + 2.8), (at[0] - 3, at[1] + 2.8)], "#26222A", smooth=False)
            Pt.ellipse(at[0] + 3.8, at[1], 1.4, 2.0, "#3E3A44", shade=False)


def _tiny(x, base, h, facing, pal, seed, rim, light, tint, walk=True):
    """Far-distance figure, 8..20 px: a small painted body, not a stick figure. Chunky proportions (about six
    heads tall) so every part keeps real width at print size: a shaped torso with shoulders, waist and hips, thick
    tapered legs with shoes, arms that hug the body, a head with hair, and three tones (shadow side, base, lit edge)
    plus a soft contact shadow."""
    rnd = random.Random(seed)
    k = h / 100.0
    Pt = Painter(k, light * facing, rim, tint, 0)
    Pt.rim_d = min(4.0, max(1.5, 0.55 / k)) if rim else 0
    sil = pal.get("silhouette")
    top, bottom, skin, hair, shoes = pal["top"], pal["bottom"], pal["skin"], pal["hair"], pal["shoes"]
    tk, bk = pal["top_kind"], pal["bottom_kind"]
    f = pal["form"] == "f"
    if tk == "dress":
        bk = "none"
    dark = lambda c, t=0.3: mix(c, SHADOW, t)
    out = [f'<ellipse cx="{_f(-Pt.lx * 4)}" cy="0.8" rx="20" ry="3.6" fill="#140C1A" opacity="0.22"/>']
    stride = rnd.uniform(9, 12) if walk else 3.2
    legcol = bottom if bk == "trousers" else skin
    hip_y = -46
    # legs: far leg (darker) then near leg, thick tapered tubes ending in shoes
    legs = [([(-1.5, hip_y), (-stride * 0.45, -24), (-stride, -3)], True), ([(1.5, hip_y), (stride * 0.55, -24), (stride * 0.8, -3)], False)]
    if not walk:
        legs = [([(-5, hip_y), (-5.5, -24), (-6, -3)], True), ([(5, hip_y), (5.5, -24), (6, -3)], False)]
    for pts, far in legs:
        c = dark(legcol, 0.22) if far else legcol
        Pt.tube(pts, [15, 11.5, 9], c, shade=not far, cap0=False, sh=0.32, hi=0)
        if bk in ("shorts", "swim") and not sil:
            cp, cw = cut(pts, [16.5, 13, 10], 0.45 if bk == "shorts" else 0.2)
            Pt.tube(cp, cw, dark(bottom, 0.22) if far else bottom, shade=False, cap0=False, cap1=False)
        ax, ay = pts[-1]
        Pt.fill(ell_pts(ax + (2.5 if walk else 0), ay + 1.5, 6.5, 3.6, 0, 360, 12)[:-1], dark(shoes, 0.15) if far else shoes, rim=False)
    # skirt / dress / coat over the thighs
    if (tk in ("dress", "coat") or bk == "skirt") and not sil:
        c = bottom if bk == "skirt" else top
        hem = -24 if tk == "coat" else -27
        Pt.fill([(-11, -58), (11, -58), (16 + stride * 0.25, hem), (0, hem + 2), (-16 - stride * 0.15, hem)], c, smooth=False)
        Pt.shape(tube_side([(0, -58), (0, hem)], [22, 32], Pt.L, 0.42, cap1=False), dark(c))
    # far arm, tucked behind the body
    sw = stride * 0.35 if walk else 0
    sleeve_col = skin if tk in ("tank", "swim") else top
    Pt.tube([(-1, -79), (3 + sw, -63), (5 + sw * 1.4, -52)], [10, 8.5, 7.5], dark(sleeve_col, 0.3), shade=False, cap0=True)
    # torso: shoulders, chest, waist, hips
    tcol = skin if tk == "swim" else top
    sh_w = 15.5 if not f else 13.5
    body = [(-6, -86), (6, -86), (sh_w, -80), (sh_w - 1, -70), (11.5, -58), (12.5, hip_y - 1), (-12.5, hip_y - 1), (-11.5, -58), (-sh_w + 1, -70), (-sh_w, -80)]
    Pt.fill(body, tcol)
    if bk in ("trousers", "shorts", "swim") and tk not in ("coat", "dress"):
        Pt.fill([(-12, -55), (12, -55), (12.5, hip_y + 2), (-12.5, hip_y + 2)], bottom, smooth=False, rim=False)
    if tk == "swim" and f and not sil:
        Pt.fill([(-sh_w + 1.5, -76), (sh_w - 1.5, -76), (sh_w - 2, -67), (-sh_w + 2, -67)], top, smooth=False, rim=False)
    Pt.shape(tube_side([(0, -84), (0, hip_y)], [sh_w * 2, 25], Pt.L, 0.42, cap1=False), dark(tcol, 0.32))
    Pt.shape(tube_side([(0, -82), (0, hip_y + 4)], [sh_w * 2 - 2, 23], Pt.L, 0.14, lit=True, cap1=False), mix(tcol, LIGHT, 0.35), op=0.7)
    # near arm swinging back a little, hand in skin tone
    Pt.tube([(1, -79), (-2 - sw, -64), (-3 - sw * 1.3, -53)], [10.5, 9, 8], sleeve_col, shade=True, cap0=True, sh=0.3, hi=0)
    if tk in ("tee", "dress") and not sil:
        cp, cw = cut([(-2 - sw, -64), (-3 - sw * 1.3, -53)], [9, 8], 1.0)
        Pt.tube(cp, cw, skin, shade=False, cap0=False)
    Pt.fill(ell_pts(-3 - sw * 1.3, -50, 4.4, 4.8, 0, 360, 10)[:-1], skin, rim=False)
    # neck and head
    Pt.tube([(0, -86), (0.8, -90)], [8, 7.5], dark(skin, 0.15), shade=False, cap0=False, cap1=False, rim=False)
    hx, hy, hr = 1.2, -94, 9.0
    if pal["hair_style"] in ("long", "bob"):
        L = -80 if pal["hair_style"] == "long" else -86
        Pt.fill([(hx - 9, hy - 2), (hx - 10.5, L), (hx - 1, L + 1), (hx + 1, hy)], hair)
    Pt.fill(ell_pts(hx, hy, hr * 0.9, hr, 0, 360, 16)[:-1], skin)
    if pal["hair_style"] != "bald":
        cap = ell_pts(hx - 0.6, hy - 0.8, hr * 0.98, hr * 1.06, 160, 380, 12) + [(hx + 5, hy - 3.5), (hx - 2, hy - 2), (hx - 6, hy + 4)]
        if pal["hair_style"] == "afro":
            cap = ell_pts(hx - 1, hy - 2, hr * 1.35, hr * 1.25, 0, 360, 16)[:-1]
        Pt.fill(cap, hair)
        if pal["hair_style"] in ("ponytail", "bun"):
            Pt.fill(ell_pts(hx - 9, hy - 4, 4.2, 4.6, 0, 360, 10)[:-1], hair)
    Pt.shape(Pt.crescent(hx, hy, hr * 0.9, hr, 0.55), dark(skin, 0.3), op=0.8)
    hk = pal.get("hat_kind")
    if hk and not sil:
        hc = pal["hat"]
        if hk in ("sunhat", "cowboy"):
            Pt.fill(ell_pts(hx, hy - 4, 16, 3.6, 0, 360, 14)[:-1], hc)
            Pt.fill(ell_pts(hx, hy - 5, 9, 7.5, 180, 360, 10), hc)
        else:
            Pt.fill(ell_pts(hx - 0.5, hy - 3, 9.6, 8, 180, 360, 10) + ([(hx + 15, hy - 3)] if hk == "cap" else []), hc)
    return f'<g transform="translate({_f(x)} {_f(base)}) scale({k * facing:.4f} {k:.4f})">' + "".join(out + Pt.out) + "</g>"


def person(x, base_y, height_px, pose="walk", facing=1, palette=None, seed=0, rim=None, light=1, tint=None,
           shadow=0.22, form=None, child=False, detail=None):
    """One painted figure (or a couple / parent+child / dog walker / cyclist group). See module doc."""
    rnd = random.Random(seed)
    pal = _palette(palette, seed, form, child)
    h = float(height_px)
    if pose == "couple" or pose == "couple_front":
        return couple(x, base_y, h, view="back" if pose == "couple" else "front", palette=palette, seed=seed, rim=rim, light=light, tint=tint, shadow=shadow)
    if pose == "child_on_shoulders" or pose == "parent_child":
        return parent_child(x, base_y, h, facing, palette, seed, rim, light, tint, shadow)
    if pose in ("child", "child_back", "child_walk", "child_34"):
        sub = {"child": "stand", "child_back": "stand_back", "child_walk": "walk", "child_34": "stand_34"}[pose]
        return person(x, base_y, h, sub, facing, palette, seed, rim, light, tint, shadow, form, True, detail)
    if pose == "tiny" or (h < 16 and pose in ("walk", "stand", "stand_back", "front", "back", "stand_34", "stand_side", "lean_back")):
        return _tiny(x, base_y, h, facing, pal, seed, rim, light, tint, walk=pose not in ("stand", "stand_back", "front", "back", "stand_34", "lean_back"))
    if pose == "jog" and not (isinstance(palette, dict) and "top_kind" in palette) and not pal.get("silhouette"):
        pal.update(top_kind="tank" if pal["form"] == "f" else "tee", bottom_kind="shorts")
    k = h / 100.0
    if detail is None:
        detail = 2 if h >= 56 else 1
    Pt = Painter(k, light * facing, rim, tint, detail)
    J = pose_joints(pose, pal["form"], rnd, child)
    if child:
        _childify(J)
    out = []
    # ground contact shadow
    if shadow and not (pose in SEATED) and pose not in ("surf_ride", "surf_sit", "read", "paddle", "guitar"):
        w = 16 if pose not in ("cyclist",) else 44
        out.append(f'<ellipse cx="{_f(-light * facing * 3)}" cy="0.6" rx="{w}" ry="2.6" fill="#140C1A" opacity="{shadow}"/>')
    if pose in ("surf_ride", "surf_sit"):
        b = pal["board"]
        Pt.fill(ell_pts(2, 1.5, 34 if pose == "surf_ride" else 38, 3.0, 0, 360, 30, -4 if pose == "surf_ride" else 2)[:-1], b)
        Pt.shape(ell_pts(2, 2.4, 33, 1.6, 0, 180, 16, -4), mix(b, SHADOW, 0.35))
    if pose == "cyclist":
        _bike(Pt, J["bike"], pal["accent"], k)
    lift = J.get("lift", 0)
    if pose == "dog_walker":
        sub = Painter(k, Pt.lx, rim, tint, detail)
        collar = _dog(sub, 24, 0, 1.05, pal["dog"])
        hand = (J["arms"][1][1][-1][0] + 2.5, J["arms"][1][1][-1][1] + 1.5)
        Pt.out += sub.out
        Pt.add(f'<path d="M {_f(hand[0])} {_f(hand[1])} Q {_f((hand[0] + collar[0]) / 2)} {_f(max(hand[1], collar[1]) + 6)} {_f(collar[0])} {_f(collar[1])}" '
               f'fill="none" stroke="{Pt.c("#2A2226")}" stroke-width="{_f(max(0.8, 0.7 / k))}"/>')
    body = Painter(k, Pt.lx, rim, tint, detail)
    _render(body, J, pal, child, pose)
    g = "".join(Pt.out) + (f'<g transform="translate(0 {-lift})">' + "".join(body.out) + "</g>" if lift else "".join(body.out))
    return (f'<g transform="translate({_f(x)} {_f(base_y)}) scale({k * facing:.4f} {k:.4f})">' + "".join(out) + g + "</g>")


def _childify(J):
    """Child proportions: bigger head relative to the body, shorter limbs (body squashed toward the feet)."""
    def sq(p):
        x, y = p[0], p[1]
        return (x * 0.94, y * 0.9) + tuple(p[2:])
    J["torso"] = [(x * 0.94, y * 0.9 + 0.0, w * 0.92) for x, y, w in J["torso"]]
    J["arms"] = [(n, [sq(p) for p in pts], lay) for n, pts, lay in J["arms"]]
    J["legs"] = [([sq(p) for p in pts], fa, lay) for pts, fa, lay in J["legs"]]
    hx, hy = J["head"]
    J["head"] = (hx * 0.94, J["torso"][0][1] - 9.4)


def couple(x, base_y, h, view="back", palette=None, seed=0, rim=None, light=1, tint=None, shadow=0.22, gap=None):
    """Two people side by side holding hands (seen from behind by default)."""
    rnd = random.Random(seed)
    p1 = dict(palette or {}) if isinstance(palette, dict) else palette
    pals = []
    for i, form in enumerate("mf" if rnd.random() < 0.6 else "ff" if rnd.random() < 0.5 else "mm"):
        pal = _palette(p1 if not isinstance(p1, dict) else {**p1, "form": form}, seed + i * 31, form)
        pals.append(pal)
    k = h / 100.0
    g = gap if gap is not None else 34
    hs = [1.0, 0.94] if pals[1]["form"] == "f" and pals[0]["form"] == "m" else [1.0, 0.97]
    out = []
    joints = []
    for i, pal in enumerate(pals):
        J = pose_joints("stand_back" if view == "back" else "stand", pal["form"], random.Random(seed + i), False)
        s = -1 if i == 0 else 1
        # inner arm reaches down to the joined hands in the middle
        for a in range(len(J["arms"])):
            n, pts, lay = J["arms"][a]
            if (pts[0][0] > 0) == (i == 0):   # the inner arm
                sx = pts[0]
                tx = -s * g / 2 / hs[i]
                J["arms"][a] = (n, [sx, (sx[0] + (tx - sx[0]) * 0.35, -65), (tx - s * 2.0, -54)], lay)
        joints.append(J)
    for i, (pal, J) in enumerate(zip(pals, joints)):
        s = -1 if i == 0 else 1
        kk = k * hs[i]
        Pt = Painter(kk, light, rim, tint, 2 if h >= 56 else 1)
        if shadow:
            out.append(f'<g transform="translate({_f(x + s * g / 2 * k)} {_f(base_y)}) scale({kk:.4f})"><ellipse cx="{_f(-light * 3)}" cy="0.6" rx="15" ry="2.6" fill="#140C1A" opacity="{shadow}"/></g>')
        _render(Pt, J, pal, False, "stand_back" if view == "back" else "stand")
        out.append(f'<g transform="translate({_f(x + s * g / 2 * k)} {_f(base_y)}) scale({kk:.4f})">' + "".join(Pt.out) + "</g>")
    return "".join(out)


def parent_child(x, base_y, h, facing=1, palette=None, seed=0, rim=None, light=1, tint=None, shadow=0.22, view="front"):
    """Adult with a child riding on the shoulders, hands holding the child's legs."""
    rnd = random.Random(seed)
    pal = _palette(palette, seed, None)
    cpal = _palette(None, seed + 77, None, child=True)
    k = h / 100.0
    det = 2 if h >= 56 else 1
    Pt = Painter(k, light * facing, rim, tint, det)
    if shadow:
        Pt.add(f'<ellipse cx="{_f(-light * 3)}" cy="0.6" rx="16" ry="2.6" fill="#140C1A" opacity="{shadow}"/>')
    J = pose_joints("carry_child", pal["form"], rnd)
    if view == "back":
        J["view"] = "back"
    # the child sits astride the neck (seat ~ the parent's shoulder line), about half the parent's size
    cs = 0.6
    C = Painter(k * cs, light * facing, rim, tint, det)
    CJ = pose_joints("sit_front", cpal["form"], random.Random(seed + 5))
    _childify(CJ)
    CJ["view"] = view
    CJ["legs"] = [([(s * 5.5, -3), (s * 15.5, 0), (s * 15.5, 19)], None, "front") for s in (-1, 1)]
    if rnd.random() < 0.5:
        CJ["arms"] = [("L", [(-7, -31), (-15, -38), (-17, -50)], "front"), ("R", [(7, -31), (15, -38), (17, -50)], "front")]
    else:
        CJ["arms"] = [("L", [(-7, -31), (-12, -20), (-7, -12)], "front"), ("R", [(7, -31), (16, -38), (19, -51)], "front")]
    body_only = dict(CJ, legs=[])
    _render(C, body_only, cpal, True, "sit_front")
    L = Painter(k * cs, light * facing, rim, tint, det)
    _render(L, CJ, cpal, True, "sit_front", parts="legs")
    place = f'<g transform="translate(0 -84.5) scale({cs})">'
    if view == "back":
        J["arms"] = [("L", [(-8.8, -79.2), (-15.5, -72), (-11, -77)], "front"), ("R", [(8.8, -79.2), (15.5, -72), (11, -77)], "front")]
        _render(Pt, J, pal, False, "carry_child")
        g = "".join(Pt.out) + place + "".join(C.out) + "</g>"
    else:
        J["arms"] = [("L", [(-8.8, -79.2), (-16, -69), (-10.5, -75)], "front"), ("R", [(8.8, -79.2), (16, -69), (10.5, -75)], "front")]
        arms = J["arms"]
        J["arms"] = []
        _render(Pt, J, pal, False, "carry_child")
        A = Painter(k, light * facing, rim, tint, det)
        J["arms"] = arms
        _render(A, dict(J, legs=[], torso=J["torso"]), pal, False, "carry_child", parts="arms")
        g = place + "".join(C.out) + "</g>" + "".join(Pt.out) + place + "".join(L.out) + "</g>" + "".join(A.out)
    return f'<g transform="translate({_f(x)} {_f(base_y)}) scale({k * facing:.4f} {k:.4f})">' + g + "</g>"


def crowd(spec, **common):
    """spec: iterable of (x, base_y, h, pose, facing, seed[, palette]) -> joined SVG."""
    out = []
    for s in spec:
        x, b, h, pose, facing, seed = s[:6]
        pal = s[6] if len(s) > 6 else common.get("palette")
        kw = {k: v for k, v in common.items() if k != "palette"}
        out.append(person(x, b, h, pose, facing, pal, seed, **kw))
    return "".join(out)
