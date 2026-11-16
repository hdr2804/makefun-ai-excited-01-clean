#!/usr/bin/env python3
"""Draw the ai-excited-01 entry: 'One small leap becomes a universe'.

A goldfish leaps from its bowl (bottom-left); its splash becomes a curling
wave that spirals up into a galaxy of stars and confetti (top-right).
Deterministic: seed 20261116. 2x supersample, Lanczos downscale to 1024.
Translucent effects live on separate RGBA layers merged with
Image.alpha_composite (ImageDraw on RGBA replaces pixels instead of
blending, so glow/streaks must never be drawn directly on the base).
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SEED = 20261116
S = 2                      # supersample factor
W = H = 1024 * S
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)

INDIGO_TOP = (11, 11, 42)
INDIGO_BOT = (30, 16, 64)
ORANGE = (255, 122, 26)
ORANGE_DEEP = (230, 74, 10)
GOLD = (255, 176, 32)
MAGENTA = (255, 45, 149)
PINK = (255, 110, 199)
YELLOW = (255, 226, 40)
WHITE = (255, 255, 255)
WAVE_BLUE = (64, 170, 255)
WAVE_LIGHT = (150, 225, 255)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def composite(base, *layers):
    for lay in layers:
        base.alpha_composite(lay)
    return base


def soft_disc(lay, cx, cy, r, color, alpha):
    """A soft radial glow disc on its own layer."""
    d = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(d)
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    d = d.filter(ImageFilter.GaussianBlur(r * 0.45))
    lay.alpha_composite(d)


def star(d, cx, cy, r, color, alpha=255):
    """4-point sparkle star."""
    pts = []
    for i in range(8):
        ang = math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color + (alpha,))


# ---------------------------------------------------------------- background
base = Image.new("RGBA", (W, H), INDIGO_TOP + (255,))
bd = ImageDraw.Draw(base)
for y in range(H):
    t = y / H
    c = tuple(int(INDIGO_TOP[i] + (INDIGO_BOT[i] - INDIGO_TOP[i]) * t) for i in range(3))
    bd.line([(0, y), (W, y)], fill=c + (255,))
# faint nebula mottling
for _ in range(120):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    r = rng.uniform(4, 18)
    col = rng.choice([(80, 40, 160), (140, 40, 120), (40, 60, 160)])
    a = rng.randint(8, 16)
    bd.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))

glow = layer()
soft_disc(glow, int(0.78 * W), int(0.20 * H), int(0.42 * W), (150, 30, 120), 110)
soft_disc(glow, int(0.16 * W), int(0.86 * H), int(0.34 * W), (200, 80, 10), 90)
soft_disc(glow, int(0.55 * W), int(0.55 * H), int(0.30 * W), (255, 120, 40), 55)
base = composite(base, glow)

# ---------------------------------------------------------------- wave
# Diagonal path from the bowl up to the galaxy: quadratic bezier.
def bez(p0, p1, p2, t):
    return (
        (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
        (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
    )


p0 = (int(0.17 * W), int(0.86 * H))
p1 = (int(0.30 * W), int(0.38 * H))
p2 = (int(0.68 * W), int(0.32 * H))
wave = layer()
wd = ImageDraw.Draw(wave)
pts = [bez(p0, p1, p2, t / 60) for t in range(61)]
# body: tapering overlapping discs, wide at the bowl, thin at the crest
for i, (x, y) in enumerate(pts):
    t = i / 60
    r = int(130 * (1 - t) + 26 * t)
    wd.ellipse([x - r, y - r, x + r, y + r], fill=(35, 125, 230, 255))
# inner highlight ribbon, offset toward the upper edge
hl = layer()
hd = ImageDraw.Draw(hl)
for i, (x, y) in enumerate(pts):
    t = i / 60
    r = int((40 - 30 * t))
    hd.ellipse([x - r - 20, y - r - 26, x + r - 20, y + r - 26],
               fill=WAVE_LIGHT + (235,))
hl = hl.filter(ImageFilter.GaussianBlur(5))
wave = composite(wave, hl)
# foam: white caps along the crest edge
foam = layer()
fd = ImageDraw.Draw(foam)
for i, (x, y) in enumerate(pts):
    t = i / 60
    if i % 2 == 0:
        r = int((30 - 20 * t) * rng.uniform(0.7, 1.3))
        fd.ellipse([x - r - 8, y - r - 40, x + r - 8, y + r - 40],
                   fill=WHITE + (225,))
foam = foam.filter(ImageFilter.GaussianBlur(4))
wave = composite(wave, foam)
# crest hook: a curling tip where the wave breaks into the galaxy
curl = layer()
cd = ImageDraw.Draw(curl)
cx, cy = p2
cd.arc([cx - 95, cy - 95, cx + 95, cy + 95], 250, 80,
       fill=(150, 225, 255, 255), width=26)
cd.arc([cx - 95, cy - 95, cx + 95, cy + 95], 300, 60,
       fill=WHITE + (235,), width=10)
cd.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(35, 125, 230, 255))
curl = curl.filter(ImageFilter.GaussianBlur(3))
wave = composite(wave, curl)
base = composite(base, wave)

# ---------------------------------------------------------------- galaxy (top-right)
gx, gy = int(0.80 * W), int(0.17 * H)
gal = layer()
gd = ImageDraw.Draw(gal)
# dense core glow
soft_disc(gal, gx, gy, int(0.16 * W), (255, 190, 90), 150)
soft_disc(gal, gx, gy, int(0.08 * W), (255, 240, 200), 200)
# three spiral arms, many stars each + dust motes
for arm in range(3):
    base_ang = arm * (2 * math.pi / 3) + 0.5
    for i in range(140):
        t = i / 140
        ang = base_ang + t * 4.4
        rad = 18 + t * int(0.30 * W)
        spread = rng.gauss(0, 12 + t * 52)
        x = gx + (rad + spread * 0.4) * math.cos(ang) - spread * 0.3 * math.sin(ang)
        y = gy + (rad + spread * 0.4) * math.sin(ang) * 0.85 + spread * 0.3 * math.cos(ang)
        r = rng.uniform(2.5, 10) * (1 - t * 0.5)
        col = rng.choice([WHITE, GOLD, PINK, WAVE_LIGHT, (255, 200, 120)])
        a = rng.randint(150, 255)
        if r > 5.5:
            star(gd, x, y, r * 2.2, col, a)
        else:
            gd.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
# dust motes
for _ in range(400):
    ang = rng.uniform(0, 2 * math.pi)
    rad = rng.uniform(0, int(0.32 * W))
    x = gx + rad * math.cos(ang)
    y = gy + rad * math.sin(ang) * 0.85
    r = rng.uniform(1, 3.2)
    col = rng.choice([WHITE, GOLD, PINK])
    gd.ellipse([x - r, y - r, x + r, y + r], fill=col + (rng.randint(90, 200),))
# confetti around the galaxy
for _ in range(70):
    ang = rng.uniform(0, 2 * math.pi)
    rad = rng.uniform(int(0.10 * W), int(0.36 * W))
    x = gx + rad * math.cos(ang)
    y = gy + rad * math.sin(ang) * 0.9
    w, h = rng.uniform(6, 16), rng.uniform(3, 7)
    col = rng.choice([ORANGE, MAGENTA, GOLD, (0, 220, 200), WHITE])
    piece = Image.new("RGBA", (int(w * 3), int(h * 3)), (0, 0, 0, 0))
    pd = ImageDraw.Draw(piece)
    pd.rectangle([w, h, 2 * w, 2 * h], fill=col + (235,))
    piece = piece.rotate(rng.uniform(0, 180), expand=True, resample=Image.BICUBIC)
    gal.alpha_composite(piece, (int(x - piece.width / 2), int(y - piece.height / 2)))
base = composite(base, gal)


# ---------------------------------------------------------------- burst rays (<=9, soft)
rays = layer()
rd = ImageDraw.Draw(rays)
rx, ry = int(0.55 * W), int(0.40 * H)
for k in range(7):
    ang = -2.2 + k * 0.45 + rng.uniform(-0.08, 0.08)
    ln = int(0.34 * W) * rng.uniform(0.7, 1.0)
    wdt = int(0.022 * W)
    x2, y2 = rx + ln * math.cos(ang), ry + ln * math.sin(ang)
    px, py = -math.sin(ang) * wdt, math.cos(ang) * wdt
    col = rng.choice([GOLD, ORANGE, PINK])
    rd.polygon([(rx, ry), (x2 + px, y2 + py), (x2 - px, y2 - py)],
               fill=col + (45,))
rays = rays.filter(ImageFilter.GaussianBlur(20))
base = composite(base, rays)

# ---------------------------------------------------------------- leaping goldfish (nose-up-right)
fish = Image.new("RGBA", (900, 620), (0, 0, 0, 0))
fd = ImageDraw.Draw(fish)
# tail (left, flowing two-lobe fan)
fd.polygon([(250, 300), (40, 110), (110, 260), (60, 300)], fill=(255, 90, 40, 255))
fd.polygon([(250, 300), (40, 490), (110, 340), (60, 300)], fill=(255, 110, 50, 255))
fd.polygon([(250, 300), (70, 200), (120, 300), (70, 400)], fill=(255, 140, 60, 255))
# body: plump ellipse, head right
fd.ellipse([230, 150, 700, 450], fill=(255, 140, 26, 255))
fd.ellipse([230, 150, 700, 360], fill=(255, 176, 60, 255))
# belly
fd.ellipse([300, 330, 640, 450], fill=(255, 205, 110, 255))
# scales hint
for row in range(3):
    for col_i in range(6):
        sx = 330 + col_i * 52 + (row % 2) * 26
        sy = 210 + row * 55
        fd.arc([sx - 26, sy - 22, sx + 26, sy + 22], 10, 170, fill=(230, 90, 10, 160), width=5)
# dorsal + pectoral fins
fd.polygon([(380, 165), (470, 70), (560, 160)], fill=(255, 90, 40, 255))
fd.polygon([(420, 380), (480, 470), (540, 375)], fill=(255, 110, 50, 255))
# eye: big, excited
fd.ellipse([585, 225, 655, 295], fill=WHITE + (255,))
fd.ellipse([605, 240, 645, 280], fill=(20, 20, 40, 255))
fd.ellipse([620, 248, 638, 266], fill=WHITE + (255,))
# open smiling mouth
fd.pieslice([640, 300, 720, 380], 0, 120, fill=(120, 20, 40, 255))
fd.arc([640, 300, 720, 380], 0, 120, fill=(255, 90, 40, 255), width=6)
# motion arcs behind the fish
fish = fish.rotate(38, expand=True, resample=Image.BICUBIC)
base.alpha_composite(fish, (int(0.36 * W), int(0.24 * H)))

# motion arcs (translucent, own layer)
arcs = layer()
ad = ImageDraw.Draw(arcs)
for k, rad in enumerate([int(0.30 * W), int(0.34 * W), int(0.38 * W)]):
    ad.arc([int(0.55 * W) - rad, int(0.42 * H) - rad,
            int(0.55 * W) + rad, int(0.42 * H) + rad],
           100, 170, fill=WAVE_LIGHT + ((110 - k * 25),), width=14)
arcs = arcs.filter(ImageFilter.GaussianBlur(3))
base = composite(base, arcs)

# ---------------------------------------------------------------- bowl + cheering fish (bottom-left)
bowl = layer()
bd2 = ImageDraw.Draw(bowl)
bx, by = int(0.19 * W), int(0.88 * H)
# water
bd2.ellipse([bx - 210, by - 130, bx + 210, by + 130], fill=(40, 140, 230, 235))
bd2.ellipse([bx - 210, by - 130, bx + 210, by - 20], fill=(90, 190, 250, 235))
# second fish inside, cheering (fins up)
fx, fy = bx - 10, by - 40
bd2.polygon([(fx - 60, fy), (fx - 130, fy - 55), (fx - 105, fy), (fx - 130, fy + 55)],
            fill=(255, 90, 40, 255))
bd2.ellipse([fx - 70, fy - 48, fx + 70, fy + 48], fill=(255, 150, 40, 255))
bd2.ellipse([fx - 70, fy - 48, fx + 70, fy + 5], fill=(255, 185, 70, 255))
bd2.polygon([(fx - 10, fy - 45), (fx + 5, fy - 105), (fx + 35, fy - 45)],
            fill=(255, 90, 40, 255))  # raised fin = cheering
bd2.ellipse([fx + 28, fy - 28, fx + 58, fy + 2], fill=WHITE + (255,))
bd2.ellipse([fx + 38, fy - 20, fx + 54, fy - 4], fill=(20, 20, 40, 255))
bd2.arc([fx + 30, fy + 5, fx + 62, fy + 32], 0, 180, fill=(120, 20, 40, 255), width=5)
# glass rim + shine
bd2.ellipse([bx - 215, by - 135, bx + 215, by + 135], outline=WHITE + (230,), width=10)
bd2.arc([bx - 200, by - 120, bx + 200, by + 120], 200, 330, fill=WHITE + (160,), width=12)
# bubbles rising from the bowl
for _ in range(26):
    bxx = bx + rng.uniform(-140, 160)
    byy = by - 140 - rng.uniform(0, 320)
    br = rng.uniform(5, 16)
    bd2.ellipse([bxx - br, byy - br, bxx + br, byy + br],
                outline=WHITE + (200,), width=4)
base = composite(base, bowl)

# ---------------------------------------------------------------- WOW! (tilted, yellow + orange outline)
wow = Image.new("RGBA", (1300, 520), (0, 0, 0, 0))
wfd = ImageDraw.Draw(wow)
font = ImageFont.truetype(FONT_BOLD, 300)
text = "WOW!"
# orange outline by stamping the text in a ring of offsets
for ox in range(-14, 15, 4):
    for oy in range(-14, 15, 4):
        if ox * ox + oy * oy > 200:
            continue
        wfd.text((60 + ox, 40 + oy), text, font=font, fill=ORANGE_DEEP + (255,))
wfd.text((60, 40), text, font=font, fill=YELLOW + (255,))
wow = wow.rotate(-12, expand=True, resample=Image.BICUBIC)
base.alpha_composite(wow, (int(0.06 * W), int(0.05 * H)))

# ---------------------------------------------------------------- sparkles + final bubbles
spark = layer()
sd = ImageDraw.Draw(spark)
for _ in range(60):
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    r = rng.uniform(4, 12)
    star(sd, x, y, r, rng.choice([WHITE, GOLD, PINK]), rng.randint(140, 230))
base = composite(base, spark)

out = base.convert("RGB").resize((1024, 1024), Image.LANCZOS)
out.save("entry.png", optimize=True)
print("saved entry.png")
