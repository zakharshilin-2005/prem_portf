"""Pixel-art scout from behind, 3 climb frames (drawn programmatically).

Reference: the user's in-game screenshot (red cap scout) restyled to match the
front sprite palette (char-peak.png): orange skin, cream shirt, purple sash,
teal shorts, white socks, brown shoes, light-blue cap.

Grid 36x52, exported x4 NEAREST => 144x208 crisp pixel PNG.
Frames: b1 hang (both arms up), b2 left reach + right step, b3 mirrored.
"""
from PIL import Image

W, H = 36, 52
SCALE = 4
OUT = 'app/assets/char-peak-b{}.png'

SKIN = '#f6a832'
SHIRT = '#f3eed9'
SHORTS = '#6fa8b0'
SASH = '#7a68b0'
SHOE = '#9c5f3c'
SOCK = '#f8f8f8'
CAP = '#a9d4e4'
CAP_D = '#7fb2c8'
OUTLINE = '#4a2f22'


def draw_frame(hy_l, hy_r, raise_l=0, raise_r=0):
    """hy_l/hy_r: hand top y. raise_*: leg lift px."""
    g = {}  # (x,y) -> color

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[(x, y)] = c

    def arm(mx, hy):
        # mx: -1 left arm, +1 right arm; arms run clear of the head silhouette
        bx = 4 if mx < 0 else 29            # arm bar x range bx..bx+2
        rect(bx, hy + 5, bx + 2, 20, SKIN)               # forearm bar
        rect(bx - 1, hy, bx + 3, hy + 4, SKIN)           # hand
        rect(bx - 1, 17, bx + 3, 21, SHIRT)              # sleeve

    def leg(cx, lift):
        # cx: left leg x12-15, right x20-23; lift raises+extends the leg
        out = 2 if lift else 0
        cx = cx - out if cx < 18 else cx + out
        y0 = 37 - lift
        rect(cx, y0, cx + 3, y0 + 3, SKIN)               # thigh/knee
        rect(cx, y0 + 4, cx + 3, y0 + 7, SOCK)           # sock
        rect(cx - 1, y0 + 8, cx + 4, y0 + 12, SHOE)      # shoe

    # far limbs first (body overlaps their roots)
    arm(-1, hy_l)
    arm(1, hy_r)
    leg(12, raise_l)
    leg(20, raise_r)

    # torso
    rect(11, 18, 24, 18, SHIRT)
    rect(10, 19, 25, 29, SHIRT)
    # sash: right shoulder -> left hip
    for i, y in enumerate(range(19, 30)):
        xc = 22 - i
        rect(xc - 1, y, xc + 1, y, SASH)
    # shorts
    rect(11, 30, 24, 36, SHORTS)
    # head (back of the head)
    rect(13, 4, 22, 4, SKIN)
    rect(11, 5, 24, 5, SKIN)
    rect(10, 6, 25, 15, SKIN)
    rect(11, 16, 24, 16, SKIN)
    rect(13, 17, 22, 17, SKIN)
    # cap (seen from behind) + strap
    rect(13, 2, 22, 3, CAP)
    rect(12, 3, 23, 3, CAP)
    rect(15, 4, 20, 4, CAP_D)

    # outline pass: dark pixels on empty cells next to colour
    out = dict(g)
    for (x, y), c in g.items():
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (x + dx, y + dy) not in g:
                    out.setdefault((x + dx, y + dy), OUTLINE)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    def rgb(c):
        return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16), 255)
    for (x, y), c in out.items():
        if 0 <= x < W and 0 <= y < H:
            im.putpixel((x, y), rgb(c))
    return im.resize((W * SCALE, H * SCALE), Image.NEAREST)


frames = [
    draw_frame(4, 4),                    # b1: hang, both arms up
    draw_frame(1, 9, raise_r=9),         # b2: left reach, right step
    draw_frame(9, 1, raise_l=9),         # b3: right reach, left step
]
for i, fr in enumerate(frames, 1):
    fr.save(OUT.format(i))
    print('saved', OUT.format(i), fr.size)
