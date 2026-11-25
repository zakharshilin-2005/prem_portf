"""Пикселизация фото в стиле референса с котиком:
умеренная пикселизация + глитч-полосы со сдвигом и хроматической аберрацией.
"""
import random
from PIL import Image, ImageEnhance

random.seed(12)

SRC = r"C:\portfolio\my_website\app\assets\ya.jpg"
DST = r"C:\portfolio\my_website\app\assets\photo-pixel.png"

img = Image.open(SRC).convert("RGB")
w, h = img.size

# 1. Базовая пикселизация (блоки ~9px, как у котика)
factor = 9
small = img.resize((max(1, w // factor), max(1, h // factor)), Image.BILINEAR)
pix = small.resize((w, h), Image.NEAREST)

# 2. Отдельные зоны с более крупной пикселизацией (фрагменты по краям)
for _ in range(4):
    bw = random.randint(w // 6, w // 3)
    bh = random.randint(h // 10, h // 5)
    x0 = random.choice([random.randint(0, w // 8), random.randint(w - w // 8 - bw, w - bw)])
    y0 = random.randint(0, h - bh)
    region = img.crop((x0, y0, x0 + bw, y0 + bh))
    f2 = factor * 3
    r_small = region.resize((max(1, bw // f2), max(1, bh // f2)), Image.BILINEAR)
    pix.paste(r_small.resize((bw, bh), Image.NEAREST), (x0, y0))

# 3. Глитч-полосы: горизонтальные сдвиги + расщепление каналов
# (лицо ~37–53% высоты стараемся не пересекать)
FACE_Y0, FACE_Y1 = int(h * 0.36), int(h * 0.54)
def strip_y():
    for _ in range(20):
        y = random.randint(0, h - 40)
        if not (FACE_Y0 - 30 < y < FACE_Y1):
            return y
    return random.randint(0, int(h * 0.2))
for _ in range(8):
    y0 = strip_y()
    sh = random.randint(6, 34)
    dx = random.choice([-1, 1]) * random.randint(14, 64)
    strip = pix.crop((0, y0, w, y0 + sh))
    pix.paste(strip, (dx, y0))
    # хроматический сдвиг на полосе
    r, g, b = pix.crop((0, y0, w, y0 + sh)).split()
    from PIL import ImageChops
    r = ImageChops.offset(r, random.choice([-1, 1]) * random.randint(2, 5), 0)
    b = ImageChops.offset(b, random.choice([-1, 1]) * random.randint(2, 5), 0)
    pix.paste(Image.merge("RGB", (r, g, b)), (0, y0))

# 4. Лёгкий буст цвета, чтобы пиксели читались сочнее
pix = ImageEnhance.Color(pix).enhance(1.12)
pix = ImageEnhance.Contrast(pix).enhance(1.05)

pix.save(DST)
print("saved", DST, pix.size)
