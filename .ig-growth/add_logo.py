#!/usr/bin/env python3
"""
Utiskuje brend logo na slajdove karusela.

Logo dolazi kao tamni kvadrat sa neonskim znakom. Da ne bi ostavljao vidljiv
pravougaonik preko slajda, pozadina se skida po svetlini: tamno postaje
providno, znak i sjaj oko njega ostaju. To cuva glow bolje nego tvrdo
izrezivanje po ivici.

Upotreba:
    python3 add_logo.py <logo.png> <folder_sa_slajdovima> [izlazni_folder]
"""

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageStat

# Mali potpis na svakom slajdu
MARK_SIZE = 104        # px na 1080 sirine
MARK_MARGIN = 46
MARK_OPACITY = 0.92

# Istaknuta verzija na zavrsnom CTA slajdu
HERO_MAX = 300         # gornja granica; stvarna velicina se bira prema slobodnom pojasu
HERO_MIN = 150
EDGE_GUARD = 28       # najmanji razmak hero logoa od ivice kadra

# Prag svetline: ispod donjeg je providno, iznad gornjeg puna nepovidnost
DARK_CUT = 14
LIGHT_FULL = 64


def prepare_logo(path):
    """Skida tamnu podlogu preko alfe izvedene iz svetline i sece na sadrzaj."""
    logo = Image.open(path).convert("RGBA")

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


def quiet_band(slide):
    """
    Najduzi vodoravni pojas bez sadrzaja. Red bez sadrzaja ima nisko odstupanje
    piksela - pozadina je ujednacena, tekst i grafika je razbijaju. Tako hero
    logo nalazi prazninu sam, umesto da mu koordinate stelujemo po decku.
    """
    gray = slide.convert("L")
    w, h = gray.size
    energy = [ImageStat.Stat(gray.crop((0, y, w, y + 1))).stddev[0] for y in range(h)]

    ordered = sorted(energy)
    limit = ordered[int(len(ordered) * 0.35)]

    best = (0, 0)
    start = None
    for y, e in enumerate(energy + [float("inf")]):
        if e <= limit:
            if start is None:
                start = y
        elif start is not None:
            if y - start > best[1] - best[0]:
                best = (start, y)
            start = None
    return best


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
            # Krupno i centrirano - zavrsni slajd nosi poziv na akciju
            top, bottom = quiet_band(slide)
            size = max(HERO_MIN, min(HERO_MAX, int((bottom - top) * 0.72)))
            hero = fit(logo, size)
            y = top + (bottom - top - hero.height) // 2
            # Ne sme da dodiruje ivicu kadra ni kad je pojas uz sam rub
            y = max(EDGE_GUARD, min(y, slide.height - hero.height - EDGE_GUARD))
            stamp(slide, logo, size, ((slide.width - hero.width) // 2, y), 1.0)
            where = f"krupno {size}px, pojas {top}-{bottom}px"
        else:
            stamp(slide, logo, MARK_SIZE, (MARK_MARGIN, MARK_MARGIN), MARK_OPACITY)
            where = "malo, gore levo"

        out = out_dir / path.name
        slide.convert("RGB").save(out, "PNG")
        print(f"  {path.name:<18} {where}")

    print(f"\nGotovo: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
