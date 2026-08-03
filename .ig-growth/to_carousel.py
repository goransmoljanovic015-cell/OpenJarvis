#!/usr/bin/env python3
"""
Pretvara renderovane 16:9 slajdove u Instagram karusel format 1080x1350 (4:5).

Deck je landscape, karusel je portrait, pa se radi dvoje:
  1. Horizontalni isecak sirine 8.0" - dovoljno usko da tekst bude krupan,
     dovoljno siroko da staklena kartica ostane cela u kadru.
  2. Vertikalna dopuna do 4:5 zamucenom kopijom iste slike, umesto crnih
     traka - nastavlja se atmosfera pozadine.
"""

from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

SRC = Path("native")
OUT = Path("carousel")
OUT.mkdir(exist_ok=True)

SLIDE_W_IN = 13.3333          # sirina slajda u incima
CROP_W_IN = 8.0               # siroko taman da obuhvati karticu (2.73"-10.60")
TARGET = (1080, 1350)


def to_carousel(path):
    img = Image.open(path).convert("RGB")
    W, H = img.size

    crop_w = int(round(W * CROP_W_IN / SLIDE_W_IN))
    x0 = (W - crop_w) // 2
    content = img.crop((x0, 0, x0 + crop_w, H))

    canvas_h = int(round(crop_w * TARGET[1] / TARGET[0]))

    # Pozadina: ista slika razvucena da pokrije ceo kadar, pa zamucena i
    # zatamnjena - dopuna gore/dole deluje kao produzetak scene.
    scale = max(crop_w / content.width, canvas_h / content.height)
    bg = content.resize(
        (int(content.width * scale) + 2, int(content.height * scale) + 2),
        Image.LANCZOS,
    )
    bx = (bg.width - crop_w) // 2
    by = (bg.height - canvas_h) // 2
    bg = bg.crop((bx, by, bx + crop_w, by + canvas_h))
    bg = bg.filter(ImageFilter.GaussianBlur(crop_w * 0.035))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)

    bg.paste(content, (0, (canvas_h - content.height) // 2))
    return bg.resize(TARGET, Image.LANCZOS)


def main():
    files = sorted(SRC.glob("native_*.png"))
    print(f"Pretvaram {len(files)} slajdova u {TARGET[0]}x{TARGET[1]}\n")
    for i, f in enumerate(files, 1):
        out = OUT / f"slajd_{i:02d}.png"
        to_carousel(f).save(out, "PNG")
        print(f"  {f.name}  ->  {out.name}")
    print(f"\nGotovo: {OUT.resolve()}")


if __name__ == "__main__":
    main()
