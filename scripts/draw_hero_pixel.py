"""Pixel-art version of the home-page illustration -> app/static/hero-pixel.png

Same scene as draw_hero.py (apartment, car, orange NFC stickers, tap bubbles),
drawn on a tiny canvas with hard edges (no anti-aliasing), then enlarged 4x with
nearest-neighbour scaling so every pixel stays a crisp square.
"""
from PIL import Image, ImageDraw

SCALE_UP = 4
S = 9                       # pixels per grid unit (x/y); 2:1 isometric
Z = 9                       # pixels per unit of height
CX, CY = 200, 90

INK = (46, 42, 38, 255)
ORANGE = (255, 106, 61, 255)
WHITE = (255, 255, 255, 255)

img = Image.new("RGBA", (420, 300), (0, 0, 0, 0))
d = ImageDraw.Draw(img)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def P(x, y, z=0):
    return (round(CX + (x - y) * S), round(CY + (x + y) * S / 2 - z * Z))


def poly(pts, fill, outline=INK):
    d.polygon([P(*p) for p in pts], fill=hexc(fill) if isinstance(fill, str) else fill, outline=outline)


def box(x0, y0, z0, x1, y1, z1, top, left, right):
    poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], left)
    poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], right)
    poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top)


def disc(cx, cy, r, fill, outline=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline)


def sticker(x, y, z):
    cx, cy = P(x, y, z)
    disc(cx, cy, 2, ORANGE, INK)
    img.putpixel((cx - 1, cy - 1), (255, 220, 205, 255))
    return cx, cy


ICONS = {
    "timer": ["...###...", "....#....", "..#####..", ".#.....#.", ".#..#..#.", ".#..##.#.", ".#.....#.", "..#####.."],
    "check": [".......#.", "......##.", ".....##..", "#...##...", "##.##....", ".###.....", "..#......"],
    "bulb":  ["#.#####..", ".#.....#.", ".##....#.", ".#.#...#.", "..#.#.#..", "...###...", "...####..", "....#..#."],
    "wifi":  ["..#####..", ".#.....#.", "#..###..#", "..#...#..", "....#....", "....#...."],
    "moon":  ["..####...", ".###.....", "###......", "###......", "###......", ".###.....", "..####..."],
    "pin":   ["..####...", ".######..", "##....##.", "##....##.", ".######..", "..####...", "...##....", "...##...."],
}


def bubble(sx, sy, icon, dx, dy):
    bx, by = sx + dx, sy + dy
    # dotted leader line
    steps = max(abs(dx), abs(dy + 8))
    for i in range(0, steps, 2):
        t = i / steps
        img.putpixel((round(sx + dx * t), round(sy - 3 + (dy + 8) * t)), ORANGE)
    disc(bx, by, 8, WHITE, ORANGE)
    rows = ICONS[icon]
    ox, oy = bx - 4, by - len(rows) // 2
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#":
                img.putpixel((ox + c, oy + r), INK)


# ------------------------------------------------------------------ outside + car
poly([(10.6, 1, 0), (18, 1, 0), (18, 9.5, 0), (10.6, 9.5, 0)], "#E4EBE3")
poly([(11.5, 3.3, 0), (17.5, 3.3, 0), (17.5, 7.3, 0), (11.5, 7.3, 0)], "#D8D4CC")
for wx, wy in ((12.9, 6.6), (15.9, 6.6)):
    cx, cy = P(wx, wy, 0.3)
    d.ellipse([cx - 3, cy - 2, cx + 3, cy + 3], fill=INK)
box(12.2, 4, 0.35, 16.8, 6.6, 1.35, "#A9BCC4", "#8FA4AD", "#7D939C")
box(13.3, 4.25, 1.35, 15.6, 6.35, 2.2, "#C9D8DE", "#A9BCC4", "#96ABB4")
car_s = sticker(14.4, 6.35, 1.8)

# ------------------------------------------------------------------ room
poly([(0, 0, 0), (10, 0, 0), (10, 8, 0), (0, 8, 0)], "#EFE5D6")
poly([(0, 0, 0), (10, 0, 0), (10, 0, 6), (0, 0, 6)], "#F5EEE3")
poly([(0, 0, 0), (0, 8, 0), (0, 8, 6), (0, 0, 6)], "#EAE0D0")
poly([(2.2, 3.2, 0), (6.4, 3.2, 0), (6.4, 6.6, 0), (2.2, 6.6, 0)], "#F6D9CC")
poly([(0, 4.8, 2.6), (0, 7, 2.6), (0, 7, 4.8), (0, 4.8, 4.8)], "#DCE7EA")
poly([(1.2, 0, 0), (3.4, 0, 0), (3.4, 0, 4.4), (1.2, 0, 4.4)], "#C9AE8B")
poly([(1.5, 0, 0), (3.1, 0, 0), (3.1, 0, 4.1), (1.5, 0, 4.1)], "#D9C3A5")
img.putpixel(P(2.85, 0, 2.1), INK)
door_s = sticker(3.62, 0, 3.0)

# kitchen counter, kettle, pills, plant
box(5, 0, 0, 9.6, 1.7, 2.3, "#F9F5EE", "#D9C3A5", "#C9AE8B")
box(8.1, 0.35, 2.3, 9.1, 1.25, 3.3, "#FFFFFF", "#E7E0D6", "#D6CEC2")
poly([(8.35, 0.55, 3.3), (8.85, 0.55, 3.3), (8.85, 1.05, 3.3), (8.35, 1.05, 3.3)], INK)
kettle_s = sticker(8.6, 1.25, 2.85)
box(5.3, 0.4, 2.3, 5.9, 1.0, 2.8, "#C9AE8B", "#B89A74", "#A88964")
cx, cy = P(5.6, 0.7, 3.3)
d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=hexc("#9CB38F"), outline=INK)
box(6.1, 0.6, 2.3, 6.6, 1.1, 3.0, "#FFE0D3", "#F7C8B6", "#EDB39E")
box(6.05, 0.55, 3.0, 6.65, 1.15, 3.2, "#FFFFFF", "#E7E0D6", "#D6CEC2")
pill_s = sticker(6.35, 1.1, 2.62)

# desk + laptop
box(0, 0.8, 0, 1.9, 3.0, 2.0, "#E3CFB2", "#C9AE8B", "#B89A74")
poly([(0.35, 1.3, 2.0), (1.35, 1.3, 2.0), (1.35, 2.5, 2.0), (0.35, 2.5, 2.0)], "#6E7B82")
poly([(0.35, 1.3, 2.0), (0.35, 2.5, 2.0), (0.35, 2.5, 2.9), (0.35, 1.3, 2.9)], "#8FA4AD")
desk_s = sticker(1.9, 2.55, 1.35)

# bed + nightstand + lamp
box(0, 5.0, 0, 3.0, 8.0, 1.0, "#FFFFFF", "#D6CEC2", "#C8BFB2")
box(0, 5.0, 1.0, 0.9, 8.0, 1.5, "#F6D9CC", "#EDC4B3", "#E2B5A2")
box(0, 3.6, 0, 1.2, 4.7, 1.5, "#E3CFB2", "#C9AE8B", "#B89A74")
box(0.35, 3.9, 1.5, 0.8, 4.35, 2.4, "#FFE9A8", "#F6D77E", "#EBC662")
night_s = sticker(1.2, 4.15, 0.8)

# ripples around the kettle sticker (dithered rings)
kx, ky = kettle_s
for r in (5, 8):
    for a in range(0, 360, 12 if r == 5 else 9):
        import math
        px, py = round(kx + r * math.cos(math.radians(a))), round(ky + r * math.sin(math.radians(a)) * 0.8)
        img.putpixel((px, py), ORANGE)

# hand + phone
hx, hy = kx + 12, ky - 12
SKIN, SKIN_D, SLEEVE = hexc("#F1C7A8"), hexc("#D9A987"), hexc("#6E7B82")
d.polygon([(hx + 8, hy + 16), (hx + 18, hy + 10), (hx + 26, hy + 14), (hx + 24, hy + 26), (hx + 12, hy + 28)], fill=SKIN, outline=INK)
d.polygon([(hx + 22, hy + 20), (hx + 34, hy + 16), (hx + 36, hy + 26), (hx + 26, hy + 30)], fill=SLEEVE, outline=INK)
d.rectangle([hx, hy, hx + 11, hy + 20], fill=INK)
d.rectangle([hx + 1, hy + 2, hx + 10, hy + 18], fill=hexc("#FFF4EE"))
disc(hx + 5, hy + 9, 3, ORANGE)
for p in ((hx + 4, hy + 9), (hx + 5, hy + 10), (hx + 6, hy + 9), (hx + 7, hy + 8)):
    img.putpixel(p, WHITE)
d.polygon([(hx + 8, hy + 15), (hx + 13, hy + 14), (hx + 14, hy + 20), (hx + 9, hy + 21)], fill=SKIN_D, outline=INK)   # thumb

# ------------------------------------------------------------------ bubbles
bubble(*kettle_s, "timer", -2, -20)
bubble(*pill_s, "check", -4, -19)
bubble(*door_s, "bulb", 2, -17)
bubble(*desk_s, "wifi", -13, -19)
bubble(*night_s, "moon", -17, -10)
bubble(*car_s, "pin", 3, -17)

# crop to content, enlarge with hard pixels
bbox = img.getbbox()
pad = 4
img = img.crop((bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad))
img = img.resize((img.width * SCALE_UP, img.height * SCALE_UP), Image.NEAREST)
img.save("app/static/hero-pixel.png", optimize=True)
print("saved", img.size)
