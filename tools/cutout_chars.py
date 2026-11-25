"""Вырезание фона у спрайтов персонажей + подготовка хука Пуджа."""
from rembg import remove
from PIL import Image

A = r"C:\portfolio\my_website\app\assets"

for name in ["pudge", "repo_i_love", "peak"]:
    src = Image.open(f"{A}\\{name}.jpg").convert("RGB")
    cut = remove(src)
    # обрезаем по альфа-каналу с небольшим полем
    bbox = cut.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox()
    if bbox:
        pad = 6
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(cut.width, bbox[2] + pad), min(cut.height, bbox[3] + pad))
        cut = cut.crop(bbox)
    out = f"{A}\\char-{name.replace('repo_i_love', 'repo')}.png"
    cut.save(out)
    print("saved", out, cut.size)

# Хук Пуджа отдельным спрайтом: левая часть картинки (красный серп + звенья)
pudge = Image.open(f"{A}\\char-pudge.png")
w, h = pudge.size
hook = pudge.crop((0, 0, int(w * 0.24), int(h * 0.62)))
hook.save(f"{A}\\char-pudge-hook.png")
print("hook saved", hook.size)
