#!/usr/bin/env python3
"""
Utiskuje brend logo na slajdove karusela.

Logo se lepi netaknut - onakav kakav je u fajlu, bez diranja piksela.
Posto dolazi kao neonski znak na tamnom kvadratu, ta podloga ostaje vidljiva
kao pravougaonik preko slajda. KNOCKOUT_BACKDROP = True je skida po svetlini
(tamno -> providno, znak i sjaj ostaju) ako to ikad zatreba.

Upotreba:
    python3 add_logo.py <logo.png> <folder_sa_slajdovima> [izlazni_folder]
"""

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance

# Mali potpis na svakom slajdu
MARK_SIZE = 104        # px na 1080 sirine
MARK_MARGIN = 46
MARK_OPACITY = 0.92

# Istaknuta verzija na zavrsnom CTA slajdu - dole, centrirano
HERO_SIZE = 250
HERO_BOTTOM_MARGIN = 52

# Logo se ne dira. Prebaci na True ako tamna podloga treba da nestane.
KNOCKOUT_BACKDROP = False
DARK_CUT = 14
LIGHT_FULL = 64


def prepare_logo(path):
    """Ucitava logo. Podrazumevano ga ostavlja netaknutim."""
    logo = Image.open(path).convert("RGBA")
    if not KNOCKOUT_BACKDROP:
        return logo

    span = max(1, LIGHT_FULL - DARK_CUT)
    lum_alpha = logo.convert("L").point(
        lambda v: 0 if v <= DARK_CUT
        else (255 if v >= LIGHT_FULL else int((v - DARK_CUT) * 255 / span))
    )

    # Ako fajl vec nosi providnost, obe maske vaze - mnozimo ih
    existing = logo.getchannel("A")
    if existing.getextrema()[0] < 255:
        lum_alpha = ImageChops.multiply(lum_alpha, existing)

    logo.putalpha(lum_alpha)
    bbox = logo.getbbox()
    return logo.crop(bbox) if bbox else logo


def fit(logo, size):
    """Skalira po duzoj stranici na zadatu velicinu."""
    ratio = size / max(logo.size)
    return logo.resize(
        (max(1, round(logo.width * ratio)), max(1, round(logo.height * ratio))),
        Image.LANCZOS,
    )


def stamp(slide, logo, box_size, xy, opacity):
    mark = fit(logo, box_size)
    if opacity < 1.0:
        mark.putalpha(ImageEnhance.Brightness(mark.getchannel("A")).enhance(opacity))
    slide.alpha_composite(mark, xy)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    logo_path, slides_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else slides_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    logo = prepare_logo(logo_path)
    slides = sorted(p for p in slides_dir.glob("*.png"))
    if not slides:
        sys.exit(f"Nema PNG slajdova u {slides_dir}")

    print(f"Logo {logo.size[0]}x{logo.size[1]} -> {len(slides)} slajdova\n")

    for i, path in enumerate(slides, 1):
        slide = Image.open(path).convert("RGBA")
        last = i == len(slides)

        if last:
            # Zavrsni slajd: krupno, uz donju ivicu, centrirano
            hero = fit(logo, HERO_SIZE)
            stamp(slide, logo, HERO_SIZE,
                  ((slide.width - hero.width) // 2,
                   slide.height - hero.height - HERO_BOTTOM_MARGIN), 1.0)
            where = f"krupno {HERO_SIZE}px, dole centrirano"
        else:
            stamp(slide, logo, MARK_SIZE, (MARK_MARGIN, MARK_MARGIN), MARK_OPACITY)
            where = "malo, gore levo"

        out = out_dir / path.name
        slide.convert("RGB").save(out, "PNG")
        print(f"  {path.name:<18} {where}")

    print(f"\nGotovo: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
