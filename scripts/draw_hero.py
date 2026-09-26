"""Draws the home-page illustration (docs/img + app/static/hero.svg).

Isometric cutaway of a small apartment + car. Orange NFC stickers on everyday
objects, each with a small bubble showing what a tap does. A hand with a phone
taps the kettle. Pure SVG, drawn from simple boxes in an isometric projection.
"""
import math

S = 26                       # size of one grid unit
CX, CY = 300, 215            # screen position of grid point (0,0,0)
C30, S30 = math.cos(math.pi / 6), 0.5

INK = "#2E2A26"
ORANGE = "#FF6A3D"
out = []


def P(x, y, z=0):
    return (CX + (x - y) * C30 * S, CY + (x + y) * S30 * S - z * S)


def poly(points, fill, stroke=INK, sw=1.4, extra=""):
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in points)
    out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>')


def box(x0, y0, z0, x1, y1, z1, top, left, right, sw=1.4):
    """Axis-aligned box: draws the 3 faces the viewer can see."""
    poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], top, sw=sw)              # top
    poly([P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)], left, sw=sw)             # front-left (y = y1)
    poly([P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], right, sw=sw)            # front-right (x = x1)


def sticker(x, y, z, r=7):
    a, b = P(x, y, z)
    out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r}" fill="{ORANGE}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{a - r * .3:.1f}" cy="{b - r * .3:.1f}" r="{r * .3:.1f}" fill="#fff" opacity=".55"/>')
    return a, b


ICONS = {
    "timer": '<circle cx="0" cy="1.5" r="8" fill="none"/><path d="M0 1.5V-3M0 1.5L3.5 4M-2.5 -9.5H2.5M0 -9.5V-6.5"/>',
    "check": '<path d="M-8 0L-2.5 6L8.5 -6"/>',
    "bulb": '<path d="M-4 5.5H4M-3 8.5H3M-4 3C-7 0 -7.5 -3 -6 -5.5C-4 -9 4 -9 6 -5.5C7.5 -3 7 0 4 3Z" fill="none"/><path d="M-9 -9L9 9"/>',
    "wifi": '<path d="M-9 -2C-4 -7 4 -7 9 -2M-5.5 1.5C-2.5 -1.5 2.5 -1.5 5.5 1.5M-2.2 5C-1 3.8 1 3.8 2.2 5" fill="none"/><circle cx="0" cy="7.5" r="1.3" fill="' + INK + '"/>',
    "moon": '<path d="M3 -8A8.5 8.5 0 1 0 8 5A7 7 0 0 1 3 -8Z" fill="none"/>',
    "pin": '<path d="M0 9C-6 2 -7 -1 -7 -3A7 7 0 0 1 7 -3C7 -1 6 2 0 9Z" fill="none"/><circle cx="0" cy="-3" r="2.5" fill="none"/>',
}


def bubble(sx, sy, icon, dx=0, dy=-46):
    bx, by = sx + dx, sy + dy
    out.append(f'<path d="M{sx:.1f} {sy - 8:.1f} L{bx:.1f} {by + 17:.1f}" stroke="{ORANGE}" stroke-width="1.5" stroke-dasharray="3 3" fill="none"/>')
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="17" fill="#fff" stroke="{ORANGE}" stroke-width="2"/>')
    out.append(f'<g transform="translate({bx:.1f} {by:.1f})" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>')


# ------------------------------------------------------------------ outside ground + car
poly([P(10.6, 1, 0), P(18, 1, 0), P(18, 9.5, 0), P(10.6, 9.5, 0)], "#E4EBE3", sw=1)           # grass
poly([P(11.5, 3.3, 0.01), P(17.5, 3.3, 0.01), P(17.5, 7.3, 0.01), P(11.5, 7.3, 0.01)], "#D8D4CC", sw=1)  # driveway
box(12.2, 4, 0.35, 16.8, 6.6, 1.35, "#A9BCC4", "#8FA4AD", "#7D939C")                           # car body
box(13.3, 4.25, 1.35, 15.6, 6.35, 2.2, "#C9D8DE", "#A9BCC4", "#96ABB4")                        # car cabin
for wx, wy in ((12.9, 6.6), (15.9, 6.6)):                                                        # wheels (front side)
    a, b = P(wx, wy, 0.35)
    out.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="10" ry="8" fill="{INK}"/>')
car_sticker = sticker(14.4, 6.35, 1.8, r=6)

# ------------------------------------------------------------------ room shell
poly([P(0, 0, 0), P(10, 0, 0), P(10, 8, 0), P(0, 8, 0)], "#EFE5D6")                            # floor
poly([P(0, 0, 0), P(10, 0, 0), P(10, 0, 6), P(0, 0, 6)], "#F5EEE3")                             # back-right wall
poly([P(0, 0, 0), P(0, 8, 0), P(0, 8, 6), P(0, 0, 6)], "#EAE0D0")                               # back-left wall
poly([P(2.2, 3.2, 0.01), P(6.4, 3.2, 0.01), P(6.4, 6.6, 0.01), P(2.2, 6.6, 0.01)], "#F6D9CC", sw=1)  # rug

# window on the back-left wall
poly([P(0, 4.8, 2.6), P(0, 7, 2.6), P(0, 7, 4.8), P(0, 4.8, 4.8)], "#DCE7EA")
# front door on the back-right wall
poly([P(1.2, 0, 0), P(3.4, 0, 0), P(3.4, 0, 4.4), P(1.2, 0, 4.4)], "#C9AE8B")
poly([P(1.45, 0, 0), P(3.15, 0, 0), P(3.15, 0, 4.15), P(1.45, 0, 4.15)], "#D9C3A5", sw=1)
a, b = P(2.9, 0, 2.1)
out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="2.2" fill="{INK}"/>')
door_sticker = sticker(3.62, 0, 3.0, r=6)

# ------------------------------------------------------------------ kitchen counter + kettle + pill bottle
box(5, 0, 0, 9.6, 1.7, 2.3, "#F9F5EE", "#D9C3A5", "#C9AE8B")
box(8.1, 0.35, 2.3, 9.1, 1.25, 3.3, "#FFFFFF", "#E7E0D6", "#D6CEC2")                            # kettle
poly([P(8.35, 0.55, 3.3), P(8.85, 0.55, 3.3), P(8.85, 1.05, 3.3), P(8.35, 1.05, 3.3)], INK, sw=1)  # kettle lid
kettle_sticker = sticker(8.6, 1.25, 2.85, r=6.5)
box(6.1, 0.6, 2.3, 6.6, 1.1, 3.0, "#FFE0D3", "#F7C8B6", "#EDB39E")                              # pill bottle
box(6.05, 0.55, 3.0, 6.65, 1.15, 3.2, "#FFFFFF", "#E7E0D6", "#D6CEC2")                          # cap
pill_sticker = sticker(6.35, 1.1, 2.62, r=5)
# plant on the counter
box(5.3, 0.4, 2.3, 5.9, 1.0, 2.8, "#C9AE8B", "#B89A74", "#A88964")
a, b = P(5.6, 0.7, 3.25)
out.append(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="13" ry="11" fill="#9CB38F" stroke="{INK}" stroke-width="1.2"/>')

# ------------------------------------------------------------------ desk + laptop (against the back-left wall)
box(0, 0.8, 0, 1.9, 3.0, 2.0, "#E3CFB2", "#C9AE8B", "#B89A74")
poly([P(0.35, 1.3, 2.0), P(1.35, 1.3, 2.0), P(1.35, 2.5, 2.0), P(0.35, 2.5, 2.0)], "#6E7B82", sw=1.2)   # laptop base
poly([P(0.35, 1.3, 2.0), P(0.35, 2.5, 2.0), P(0.35, 2.5, 2.9), P(0.35, 1.3, 2.9)], "#8FA4AD", sw=1.2)   # laptop screen
desk_sticker = sticker(1.9, 2.55, 1.35, r=6)

# ------------------------------------------------------------------ bed + nightstand
box(0, 5.0, 0, 3.0, 8.0, 1.0, "#FFFFFF", "#D6CEC2", "#C8BFB2")
box(0, 5.0, 1.0, 0.9, 8.0, 1.5, "#F6D9CC", "#EDC4B3", "#E2B5A2")                                 # pillow/headboard area
box(0, 3.6, 0, 1.2, 4.7, 1.5, "#E3CFB2", "#C9AE8B", "#B89A74")                                   # nightstand
box(0.35, 3.9, 1.5, 0.8, 4.35, 2.4, "#FFE9A8", "#F6D77E", "#EBC662")                             # lamp
night_sticker = sticker(1.2, 4.15, 0.8, r=5.5)

# ------------------------------------------------------------------ ripples + hand with phone (near the kettle)
kx, ky = kettle_sticker
for r, op in ((16, .55), (26, .35), (36, .18)):
    out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r}" fill="none" stroke="{ORANGE}" stroke-width="2" opacity="{op}"/>')
hx, hy = kx + 40, ky - 4
out.append(f'''<g transform="translate({hx:.1f} {hy:.1f}) rotate(-24)">
  <path d="M34 60 C44 40 58 36 72 44 L90 58 L78 92 L40 96 Z" fill="#F1C7A8" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M70 84 L112 76 L118 104 L78 116 Z" fill="#6E7B82" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>
  <rect x="-2" y="-8" width="44" height="80" rx="9" fill="{INK}"/>
  <rect x="2" y="-3" width="36" height="70" rx="6" fill="#FFF4EE"/>
  <circle cx="20" cy="30" r="10" fill="{ORANGE}"/>
  <path d="M15 30 L19 34 L26 25" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M28 50 C22 58 26 70 36 72 L46 70 C52 62 50 52 44 48 Z" fill="#F1C7A8" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>
</g>''')

# ------------------------------------------------------------------ bubbles (what each tap does)
bubble(*kettle_sticker, "timer", dx=-6, dy=-62)
bubble(*pill_sticker, "check", dx=-12, dy=-58)
bubble(*door_sticker, "bulb", dx=6, dy=-52)
bubble(*desk_sticker, "wifi", dx=-40, dy=-58)
bubble(*night_sticker, "moon", dx=-52, dy=-30)
bubble(*car_sticker, "pin", dx=10, dy=-50)

import re as _re
_nums = [(float(a), float(b)) for a, b in _re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", " ".join(out))]
_xs = [a for a, b in _nums]; _ys = [b for a, b in _nums]
VB = f"{min(_xs) - 30:.0f} {min(_ys) - 60:.0f} {max(max(_xs) - min(_xs) + 95, 0):.0f} {max(_ys) - min(_ys) + 110:.0f}"
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB}" role="img" aria-labelledby="t d">
<title id="t">NFC stickers around a home</title>
<desc id="d">An apartment and a car with small orange NFC stickers on a kettle, a pill bottle, the front door, a desk, a nightstand and the car dashboard. Bubbles show what each tap does: a timer, a checkmark, lights off, wifi, sleep mode and a map pin. A hand taps the kettle sticker with a phone.</desc>
{chr(10).join(out)}
</svg>'''
open("app/static/hero.svg", "w").write(svg)
print("written", len(svg), "bytes")
