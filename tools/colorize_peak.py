"""Colorize the B&W scout cutout into the front-sprite palette.

Each pixel gets a region label by geometry; colour = palette * luminance shading.
Then builds 3 frames: f1 straight, f2 tilt left + squash, f3 tilt right + squash.
"""
from PIL import Image
import numpy as np

SRC = 'app/assets/char-peak-back2.png'
OUTS = ['app/assets/char-peak-r1.png',
        'app/assets/char-peak-r2.png',
        'app/assets/char-peak-r3.png']

PAL = {
    'skin':   (246, 168, 50),
    'shirt':  (243, 238, 217),
    'shorts': (111, 168, 176),
    'sash':   (122, 104, 176),
    'shoe':   (156, 95, 60),
    'sock':   (248, 248, 248),
    'cap':    (169, 212, 228),
}

im = Image.open(SRC).convert('RGBA')
a = np.array(im).astype(float)
H, W = a.shape[:2]
alpha = a[..., 3] > 10
gray = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])

yy, xx = np.mgrid[0:H, 0:W]

# --- region masks (geometry of the 440x517 cutout) ---
head = ((xx - 222) / 108) ** 2 + ((yy - 88) / 82) ** 2 <= 1
cap = head & (yy < 58)
shirt = (xx > 140) & (xx < 310) & (yy > 135) & (yy < 268)
shorts = (xx > 100) & (xx < 340) & (yy > 248) & (yy < 305 + np.where(xx > 260, 25, 0))
sock_l = (xx > 55) & (xx < 142) & (yy > 302) & (yy < 352)
sock_r = (xx > 273) & (xx < 347) & (yy > 343) & (yy < 412)
shoe_l = (xx > 8) & (xx < 170) & (yy > 348) & (yy < 470)
shoe_r = (xx > 290) & (xx < 430) & (yy > 400) & (yy < 510)
# sash: band around segment (285,120)-(185,300), half-width 26
p1 = np.array([285.0, 120.0]); p2 = np.array([185.0, 300.0])
d = p2 - p1
t = ((xx - p1[0]) * d[0] + (yy - p1[1]) * d[1]) / (d @ d)
t = np.clip(t, 0, 1)
dist = np.sqrt((xx - (p1[0] + t * d[0])) ** 2 + (yy - (p1[1] + t * d[1])) ** 2)
sash = dist < 26

labels = np.full((H, W), '', dtype=object)
labels[alpha] = 'skin'
for name, m in [('shorts', shorts), ('shirt', shirt), ('skin', head), ('cap', cap),
                ('sock', sock_l | sock_r), ('shoe', shoe_l | shoe_r), ('sash', sash)]:
    labels[m & alpha] = name

out = np.zeros_like(a[..., :3])
for name, col in PAL.items():
    m = labels == name
    if m.any():
        lo, hi = np.percentile(gray[m], [5, 95])
        shade = np.clip((gray[m] - lo) / max(1.0, hi - lo), 0, 1)
        shade = 0.28 + 0.72 * shade  # тени не проваливаем в чёрный
        out[m] = np.array(col) * shade[:, None]

res = np.dstack([out, a[..., 3]]).astype(np.uint8)
col_img = Image.fromarray(res, 'RGBA')

# --- frames ---
def frame(angle, squash):
    fr = col_img.resize((W, int(H * squash)), Image.BICUBIC)
    canvas = Image.new('RGBA', (W + 40, H + 30), (0, 0, 0, 0))
    canvas.paste(fr, (20, 15 + (H - fr.height)), fr)
    return canvas.rotate(angle, resample=Image.BICUBIC, center=(canvas.width // 2, int(canvas.height * 0.55)), expand=False)

frame(0, 1.0).save(OUTS[0])
frame(-2.6, 0.97).save(OUTS[1])
frame(2.6, 0.97).save(OUTS[2])
print('saved', OUTS)
