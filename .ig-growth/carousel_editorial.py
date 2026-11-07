"""Large-type editorial carousel theme with alternating light and dark pages."""
from PIL import Image, ImageDraw, ImageOps

from carousel_visuals import _text, prepared_asset, render_visual

NAVY = "#081321"
IVORY = "#F5F2E9"
CYAN = "#4BDBDE"
CORAL = "#F28165"
MUTED = "#87969F"


def editorial_diagram(image, kind, box, dark, font_path):
    """Illustrative examples, intentionally distinct from a real Gmail screenshot."""
    x, y, w, h = box
    d = ImageDraw.Draw(image)
    ink = IVORY if dark else NAVY
    panel = "#122437" if dark else "#FFFFFF"
    quiet = "#9DAFBA" if dark else "#536575"

    def label(text, px, py, size=30, color=None, bold=False, anchor=None):
        _text(d, text, (px, py), size, color or ink, font_path, bold, anchor)

    def envelope(px, py, ew=180, eh=125, fill=panel, stroke=ink):
        d.rounded_rectangle((px, py, px + ew, py + eh), radius=18, fill=fill, outline=stroke, width=3)
        d.line((px + 10, py + 15, px + ew // 2, py + eh // 2 + 10, px + ew - 10, py + 15), fill=stroke, width=3)

    label("PRIMJER · SHEMATSKI PRIKAZ", x, y + 6, 22, quiet, bold=True)
    y += 74
    h -= 74
    if kind == "search":
        d.rounded_rectangle((x, y, x + w, y + 340), radius=30, fill=panel)
        label("POŠILJALAC", x + 38, y + 40, 24, quiet, True)
        d.rounded_rectangle((x + 32, y + 103, x + w - 32, y + 199), radius=16, fill=IVORY, outline=NAVY, width=2)
        label("newsletter@example.com", x + 55, y + 134, 38, NAVY)
        d.rounded_rectangle((x + 32, y + 235, x + 340, y + 306), radius=35, fill=CYAN)
        label("Pronađi poruke →", x + 185, y + 270, 29, NAVY, True, "mm")
        d.line((x + 90, y + 388, x + 90, y + 420), fill=CORAL, width=5)
        d.polygon([(x + 90, y + 427), (x + 78, y + 409), (x + 102, y + 409)], fill=CORAL)
        label("Prvo pogledaj rezultate.", x + 126, y + 394, 34, ink, True)
    elif kind == "before_after":
        gap = 28
        cw = (w - gap) // 2
        for index, (heading, rows) in enumerate((("PREŠIROKO", ("Newsletter", "Račun", "Potvrda")),
                                                 ("PRECIZNIJE", ("Newsletter", "Newsletter", "Newsletter")))):
            left = x + index * (cw + gap)
            d.rounded_rectangle((left, y, left + cw, y + 430), radius=26, fill=panel)
            label(heading, left + 28, y + 34, 25, CORAL if index == 0 else CYAN, True)
            for row, value in enumerate(rows):
                ry = y + 113 + row * 96
                envelope(left + 25, ry, 54, 40, stroke=quiet)
                label(value, left + 99, ry + 5, 29)
                if index == 0 and row > 0:
                    d.line((left + 95, ry + 23, left + cw - 26, ry + 23), fill=CORAL, width=3)
        label("Zadrži samo poruke koje želiš označiti.", x, y + 455, 31, ink)
    elif kind == "filter":
        d.rounded_rectangle((x, y, x + w, y + 150), radius=26, fill=panel)
        envelope(x + 30, y + 38, 100, 70, stroke=NAVY if not dark else IVORY)
        label("ODABRANI POŠILJALAC", x + 165, y + 41, 27, quiet, True)
        label("Newsletter", x + 165, y + 88, 35, ink, True)
        d.line((x + w // 2, y + 168, x + w // 2, y + 237), fill=CORAL, width=5)
        d.polygon([(x + w // 2, y + 245), (x + w // 2 - 12, y + 225), (x + w // 2 + 12, y + 225)], fill=CORAL)
        d.rounded_rectangle((x, y + 268, x + w, y + 428), radius=26, fill=CYAN)
        label("DODIJELI OZNAKU", x + 40, y + 300, 25, NAVY, True)
        label("Newsletteri", x + 40, y + 353, 47, NAVY, True)
    elif kind == "label":
        d.polygon([(x + 60, y + 85), (x + 690, y + 85), (x + 865, y + 240),
                   (x + 690, y + 395), (x + 60, y + 395)], fill=CYAN)
        d.ellipse((x + 735, y + 219, x + 777, y + 261), fill=image.getpixel((0, 0)))
        label("NEWSLETTERI", x + 112, y + 206, 66, NAVY, True)
        label("Oznaku i pravilo možeš promijeniti.", x + 60, y + 453, 33, ink)
    elif kind == "inbox":
        for index in range(3):
            envelope(x + 40 + index * 100, y + 45 + index * 92, 390, 230, fill=panel, stroke=CYAN)
        d.rounded_rectangle((x + 490, y + 325, x + w, y + 435), radius=30, fill=CYAN)
        label("U REDU.", x + 530, y + 360, 40, NAVY, True)
    else:
        for index, text in enumerate(("Odaberi zadatak.", "Provjeri rezultat.", "Primijeni korak.")):
            py = y + index * 145
            d.ellipse((x, py, x + 72, py + 72), fill=CYAN if dark else NAVY)
            d.line((x + 19, py + 36, x + 31, py + 49, x + 54, py + 23), fill=NAVY if dark else IVORY, width=5)
            label(text, x + 105, py + 17, 37, ink, True)


def render_editorial(slide, visual, brand, catalogue, number, total, font_path, fit):
    cover = number == 1
    closing = number == total
    dark = cover or (number % 3 == 0 and not closing)
    background = CYAN if closing else NAVY if dark else IVORY
    ink = IVORY if dark else NAVY
    quiet = "#9DAFBA" if dark else "#536575"
    image = Image.new("RGB", (1080, 1350), background)
    d = ImageDraw.Draw(image)

    def copy(value, box, size, minimum=34, bold=False, color=ink):
        text, font = fit(d, value, box, bold=bold, minimum=minimum, maximum=size)
        d.multiline_text(box[:2], text, font=font, fill=color, spacing=14)

    _text(d, brand["name"], (68, 58), 25, ink, font_path, True)
    _text(d, "PRAKTIČNI VODIČ", (1012, 58), 23, quiet, font_path, anchor="ra")
    d.line((68, 114, 1012, 114), fill=quiet, width=1)
    if not cover:
        d.rounded_rectangle((68, 159, 172, 208), radius=24, fill=CORAL if dark else NAVY)
        _text(d, f"{number - 1:02d}", (120, 184), 25, NAVY if dark else IVORY, font_path, True, "mm")

    title_box = (68, 174 if cover else 246, 944, 315 if cover else 260)
    copy(slide["title"], title_box, 118 if cover else 96, minimum=58, bold=True)

    if visual["kind"] == "image":
        asset = catalogue[visual["asset_id"]]
        if cover and asset["type"] == "illustration" and not asset.get("annotations"):
            # Art fills the cover; captions remain typeset separately for sharp, correct text.
            art = prepared_asset(asset, font_path)
            art = ImageOps.fit(art, (1080, 620), method=Image.Resampling.LANCZOS, centering=(.5, .7))
            image.paste(art, (0, 505))
            _text(d, "KONCEPTUALNA ILUSTRACIJA", (68, 1090), 18, quiet, font_path)
        else:
            palette = {"panel": "#122437" if dark else "#FFFFFF", "accent": CYAN if dark else NAVY,
                       "text": ink, "background": background}
            render_visual(image, visual, (68, 520, 944, 600), palette, catalogue, font_path, fit)
    elif visual["kind"] != "none":
        editorial_diagram(image, visual["kind"], (68, 565, 944, 530), dark, font_path)

    copy(slide["body"], (68, 1134, 944, 123), 42, minimum=32)
    d.line((68, 1287, 1012, 1287), fill=quiet, width=1)
    _text(d, brand["handle"], (68, 1305), 22, ink, font_path)
    _text(d, f"{number:02d} / {total:02d}", (1012, 1305), 22, ink, font_path, anchor="ra")
    return image
