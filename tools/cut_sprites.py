"""برش سه نمای خرگوش (جلو، بغل، پشت) از برگهٔ شخصیت و حذف پس‌زمینهٔ سفید.
تصویر اصلی دست نمی‌خورد؛ خروجی در assets/fixed می‌رود."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from collections import deque

src, outdir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.int16)

ROWS = {"plain": (0, 474), "goggles": (499, 972)}
COLS = {"front": (130, 450), "side": (590, 880), "back": (1060, 1350)}


def cutout(cell):
    h, w, _ = cell.shape
    # پیکسل نزدیک به سفید
    whiteish = (cell.min(axis=2) > 225) & ((cell.max(axis=2) - cell.min(axis=2)) < 22)
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if whiteish[y, x]:
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if whiteish[y, x]:
                q.append((y, x))
    while q:
        y, x = q.popleft()
        if bg[y, x] or not whiteish[y, x]:
            continue
        bg[y, x] = True
        if y > 0: q.append((y - 1, x))
        if y < h - 1: q.append((y + 1, x))
        if x > 0: q.append((y, x - 1))
        if x < w - 1: q.append((y, x + 1))
    alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
    # لبهٔ نرم: یک پیکسل کوچک کردن و کمی محو کردن
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    rgba = Image.fromarray(cell.astype(np.uint8)).convert("RGBA")
    rgba.putalpha(alpha)
    return rgba.crop(rgba.getbbox())


for rname, (y0, y1) in ROWS.items():
    for cname, (x0, x1) in COLS.items():
        spr = cutout(a[y0:y1, x0:x1])
        spr.save(f"{outdir}/bunny_{rname}_{cname}.png")
        # بوم ۵۱۲×۵۱۲ برای بازی (پا روی لبهٔ پایین، وسط)
        canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        s = min(500 / spr.height, 500 / spr.width)
        spr2 = spr.resize((round(spr.width * s), round(spr.height * s)), Image.LANCZOS) if s < 1 else spr
        canvas.paste(spr2, ((512 - spr2.width) // 2, 512 - spr2.height - 2), spr2)
        canvas.save(f"{outdir}/game_{rname}_{cname}.png")
        print(rname, cname, spr.size)
