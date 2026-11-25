"""Вырезание фона + пикселизация силуэта (альфа-канал сохраняется)."""
import random
from rembg import remove
from PIL import Image, ImageEnhance, ImageChops

random.seed(12)

SRC = r"C:\portfolio\my_website\app\assets\ya.jpg"
CUTOUT = r"C:\portfolio\my_website\app\assets\photo-cutout.png"
CUTPIX = r"C:\portfolio\my_website\app\assets\photo-cutout-pixel.png"

img = Image.open(SRC).convert("RGB")

# 1. Вырезаем фон
cut = remove(img)  # RGBA
cut.save(CUTOUT)
print("cutout saved", cut.size)

w, h = cut.size
rgb = cut.convert("RGB")
alpha = cut.split()[3]

# 2. Пикселизация только фигуры
factor = 9
small = rgb.resize((max(1, w // factor), max(1, h // factor)), Image.BILINEAR)
pix = small.resize((w, h), Image.NEAREST)

# 3. Глитч-полосы по фигуре (не трогаем зону лица)
FACE_Y0, FACE_Y1 = int(h * 0.36), int(h * 0.54)

def strip_y():
    for _ in range(20):
        y = random.randint(int(h * 0.3), h - 40)
        if not (FACE_Y0 - 30 < y < FACE_Y1):
            return y
    return h - 60

for _ in range(6):
    y0 = strip_y()
    sh = random.randint(6, 30)
    dx = random.choice([-1, 1]) * random.randint(12, 48)
    strip = pix.crop((0, y0, w, y0 + sh))
    pix.paste(strip, (dx, y0))
    r, g, b = pix.crop((0, y0, w, y0 + sh)).split()
    r = ImageChops.offset(r, random.choice([-1, 1]) * random.randint(2, 4), 0)
    b = ImageChops.offset(b, random.choice([-1, 1]) * random.randint(2, 4), 0)
    pix.paste(Image.merge("RGB", (r, g, b)), (0, y0))

pix = ImageEnhance.Color(pix).enhance(1.1)
pix = ImageEnhance.Contrast(pix).enhance(1.05)

# 4. Возвращаем альфа-канал (фон прозрачный)
out = pix.convert("RGBA")
out.putalpha(alpha)
out.save(CUTPIX)
print("pixel cutout saved", out.size)
