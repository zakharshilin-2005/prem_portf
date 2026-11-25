"""Build 2 climbing frames for the Peak scout (box surgery, collision-safe).

Sprite facts (alpha scans):
- forearm+hand: left x6-61 y255-419, right x185-240 y255-419; below y280 the hand
  narrows to x6-46 (left) / x201-240 (right), so a two-box erase avoids the legs
- legs: left x41-121 y340-442, right x128-208 y340-446
- tiny collisions (<=6 px slivers) are saved before each op and restored after.
Outputs: char-peak-c1.png, char-peak-c2.png (same 247x447 canvas).
"""
from PIL import Image

SRC = 'app/assets/char-peak.png'
OUT1 = 'app/assets/char-peak-c1.png'
OUT2 = 'app/assets/char-peak-c2.png'


def erase(img, box):
    l, t, r, b = box
    px = img.load()
    for y in range(t, b):
        for x in range(l, r):
            px[x, y] = (0, 0, 0, 0)


def cut(img, boxes, pivot=None, angle=0, dx=0, dy=0):
    """Erase the union of boxes, transform the cut content, paste back."""
    full = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for box in boxes:
        piece = img.crop(box)
        full.paste(piece, box[:2], piece)
    saved = {}
    for box in boxes:
        saved[box] = img.crop(box)
        erase(img, box)
    if angle:
        full = full.rotate(angle, resample=Image.BICUBIC, center=pivot, expand=False)
    img.paste(full, (dx, dy), full)
    return saved  # original content, in case a sliver must be restored


def restore(img, saved, box):
    l, t = box[:2]
    img.paste(saved[box], (l, t), saved[box])


def restore_skin(img, saved, box):
    """Restore only skin-coloured pixels (hand interior), leaving dark outlines."""
    import numpy as np
    l, t = box[:2]
    patch = np.array(saved[box])
    r, g, b, a = patch[..., 0], patch[..., 1], patch[..., 2], patch[..., 3]
    skin = (a > 10) & (r > 180) & (g > 120) & (b < 150)
    out = np.zeros_like(patch)
    out[skin] = patch[skin]
    img.paste(Image.fromarray(out, 'RGBA'), (l, t), Image.fromarray(out, 'RGBA'))


def tilt(canvas, angle, dy=0):
    rot = canvas.rotate(angle, resample=Image.BICUBIC,
                        center=(canvas.width // 2, int(canvas.height * 0.55)),
                        expand=False)
    out = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    out.paste(rot, (0, dy), rot)
    return out


# limb boxes
FORE_L = [(0, 256, 62, 285), (0, 285, 53, 421)]
FORE_R = [(185, 256, 247, 285), (194, 285, 247, 421)]
LEG_L = [(41, 350, 122, 447)]
LEG_R = [(128, 350, 209, 447)]
# slivers that legs leave behind (outline edges outside the erase box)
SLIVER_L = (41, 350, 47, 447)
SLIVER_R = (203, 350, 209, 447)

base = Image.open(SRC).convert('RGBA')

# ---- C1: left reach + right leg step ----
c1 = base.copy()
clip_l = {(41, 340, 53, 447): c1.crop((41, 340, 53, 447))}
hand_r_strip = {(201, 340, 209, 421): c1.crop((201, 340, 209, 421))}
cut(c1, FORE_L, pivot=(30, 272), angle=-42)          # left hand reaches up-left
restore(c1, clip_l, (41, 340, 53, 447))               # static left leg edge
leg_saved = cut(c1, LEG_R, pivot=(168, 356), angle=10, dx=6, dy=-28)
restore_skin(c1, hand_r_strip, (201, 340, 209, 421))  # hand interior only
c1 = tilt(c1, -1.4, dy=-3)
c1.save(OUT1)

# ---- C2: right reach + left leg step ----
c2 = base.copy()
clip_r = {(194, 340, 209, 447): c2.crop((194, 340, 209, 447))}
hand_l_strip = {(41, 340, 49, 421): c2.crop((41, 340, 49, 421))}
cut(c2, FORE_R, pivot=(217, 272), angle=42)          # right hand reaches up-right
restore(c2, clip_r, (194, 340, 209, 447))             # static right leg edge
leg_saved = cut(c2, LEG_L, pivot=(80, 356), angle=-10, dx=-6, dy=-28)
restore_skin(c2, hand_l_strip, (41, 340, 49, 421))    # hand interior only
c2 = tilt(c2, 1.4, dy=-3)
c2.save(OUT2)

print('saved', OUT1, OUT2)
