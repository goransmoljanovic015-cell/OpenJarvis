"""Deterministic infographic layouts and real image assets for carousel slides.

Illustrations are explicitly marked as schematics, never presented as screenshots.
Image files come from an editor-owned catalogue; the model can only choose IDs.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

KINDS = ("inbox", "search", "filter", "label", "before_after", "checklist", "image", "none")
LAYOUTS = ("auto", "cover", "split", "stacked", "comparison", "text")
VERSION = 3


def valid_box(box):
    return (isinstance(box, list) and len(box) == 4
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in box)
            and all(0 <= v <= 1 for v in box)
            and box[2] > 0 and box[3] > 0
            and box[0] + box[2] <= 1 and box[1] + box[3] <= 1)


def validate_visual(visual, asset_ids=()):
    if not isinstance(visual, dict):
        return ["visual mora biti objekt."]
    errors = []
    if visual.get("kind") not in KINDS:
        errors.append("Nepoznata vrsta vizuala.")
    if visual.get("layout", "auto") not in LAYOUTS:
        errors.append("Nepoznat raspored slajda.")
    if visual.get("kind") == "image" and (not isinstance(visual.get("asset_id"), str) or visual["asset_id"] not in asset_ids):
        errors.append("Vizual traži nepoznat asset_id; registruj stvarnu sliku u katalogu.")
    if visual.get("asset_id") and visual.get("kind") != "image":
        errors.append("asset_id se koristi samo uz kind=image.")
    caption = visual.get("caption", "")
    if not isinstance(caption, str) or len(caption) > 100:
        errors.append("Opis vizuala mora imati najviše 100 znakova.")
    if visual.get("kind") != "none" and visual.get("layout") == "text":
        errors.append("Raspored text ne može sakriti odabrani vizual.")
    if visual.get("kind") == "none" and visual.get("layout") in ("cover", "split", "comparison"):
        errors.append("Odabrani raspored zahtijeva vizual.")
    return errors


def load_catalogue(path):
    if path is None:
        return {}
    path = Path(path).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise ValueError("Katalog mora sadržavati listu assets.")
    assets = {}
    for item in data["assets"]:
        if not isinstance(item, dict):
            raise ValueError("Stavka kataloga mora biti objekt.")
        aid = item.get("id")
        if not isinstance(aid, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", aid) or aid in assets:
            raise ValueError("Neispravan ili dupli ID vizualnog resursa.")
        filename = item.get("file")
        if not isinstance(filename, str) or not filename:
            raise ValueError(f"Vizual {aid}: nedostaje datoteka.")
        file = (path.parent / filename).resolve()
        if not file.is_relative_to(path.parent):
            raise ValueError("Slike moraju biti unutar foldera kataloga.")
        if item.get("type") not in ("screenshot", "illustration"):
            raise ValueError(f"Vizual {aid}: type mora biti screenshot ili illustration.")
        if not isinstance(item.get("description"), str) or not item["description"].strip() or len(item["description"]) > 250:
            raise ValueError(f"Vizual {aid}: potreban je opis do 250 znakova za izbor i ALT tekst.")
        if not isinstance(item.get("redactions", []), list) or not isinstance(item.get("annotations", []), list):
            raise ValueError(f"Vizual {aid}: redactions i annotations moraju biti liste.")
        if len(item.get("annotations", [])) > 3:
            raise ValueError(f"Vizual {aid}: koristi najviše tri oznake po slici.")
        if "crop" in item and not valid_box(item["crop"]):
            raise ValueError(f"Vizual {aid}: neispravan izrez slike.")
        minimum = item.get("min_display_width", 640)
        if not isinstance(minimum, int) or isinstance(minimum, bool) or not 320 <= minimum <= 1000:
            raise ValueError(f"Vizual {aid}: min_display_width mora biti između 320 i 1000.")
        for redaction in item.get("redactions", []):
            if not valid_box(redaction):
                raise ValueError(f"Vizual {aid}: neispravna zona za skrivanje podataka.")
        for mark in item.get("annotations", []):
            if (not isinstance(mark, dict) or not valid_box(mark.get("box"))
                    or not isinstance(mark.get("label"), str) or not mark["label"].strip()
                    or len(mark["label"]) > 60):
                raise ValueError(f"Vizual {aid}: neispravna oznaka ili koordinata.")
            arrow = mark.get("arrow_from")
            if arrow is not None and (not isinstance(arrow, list) or len(arrow) != 2
                    or any(not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1 for v in arrow)):
                raise ValueError(f"Vizual {aid}: neispravan početak strelice.")
        # Verify image decoding before any API request; reject unsupported formats.
        with Image.open(file) as image:
            if image.format not in ("PNG", "JPEG", "WEBP"):
                raise ValueError("Podržane su PNG, JPEG i WEBP slike.")
            image.verify()
        assets[aid] = {**item, "path": file, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
    return assets


def catalogue_snapshot(catalogue):
    return {aid: {k: v for k, v in item.items() if k != "path"}
            for aid, item in sorted(catalogue.items())}


def choose_visual(slide, number, total, topic=None):
    """Explicit instructions win. Generic posts get a non-product-specific diagram."""
    if "visual" in slide:
        return slide["visual"]
    if number == 1:
        return {"kind": "inbox" if "gmail" in str(topic).lower() else "checklist", "layout": "cover"}
    if number == total:
        return {"kind": "checklist", "layout": "stacked"}
    return {"kind": "checklist", "layout": "split" if number % 2 == 0 else "stacked"}


def pixels(box, size):
    x, y, w, h = box
    return (round(x * size[0]), round(y * size[1]), round((x + w) * size[0]), round((y + h) * size[1]))


def prepared_asset(item, font_path):
    with Image.open(item["path"]) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    if "crop" in item:
        image = image.crop(pixels(item["crop"], image.size))
    # Redact BEFORE drawing overlays or exporting. Raw source images are never bundled.
    draw = ImageDraw.Draw(image)
    for box in item.get("redactions", []):
        draw.rectangle(pixels(box, image.size), fill="#142033")
    if max(image.size) > 1800:
        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path(True), max(16, min(36, image.width // 28)))
    for index, mark in enumerate(item.get("annotations", []), 1):
        x0, y0, x1, y1 = pixels(mark["box"], image.size)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=8, outline="#FF654F", width=max(3, image.width // 200))
        if "arrow_from" in mark:
            sx, sy = (round(mark["arrow_from"][0] * image.width), round(mark["arrow_from"][1] * image.height))
            tx, ty = x0, (y0 + y1) // 2
            draw.line((sx, sy, tx, ty), fill="#FF654F", width=max(3, image.width // 200))
            angle = math.atan2(ty - sy, tx - sx)
            length = max(12, image.width // 65)
            draw.polygon([(tx, ty), (tx - length * math.cos(angle - .5), ty - length * math.sin(angle - .5)),
                          (tx - length * math.cos(angle + .5), ty - length * math.sin(angle + .5))], fill="#FF654F")
        radius = max(14, image.width // 55)
        cx, cy = min(image.width - radius, max(radius, x0)), min(image.height - radius, max(radius, y0))
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill="#FF654F")
        draw.text((cx, cy), str(index), fill="white", font=font, anchor="mm")
    return image


def _text(draw, value, position, size, color, font_path, bold=False, anchor=None):
    font = ImageFont.truetype(font_path(bold), size)
    draw.text(position, value, fill=color, font=font, anchor=anchor)


def schematic(kind, size, palette, font_path):
    """Render explanatory vector-style diagrams at a stable internal resolution."""
    image = Image.new("RGB", (900, 620), palette["panel"])
    d = ImageDraw.Draw(image)
    accent, text = palette["accent"], palette["text"]
    muted, border, orange = "#A6B6C9", "#24445F", "#FF8569"

    if size[0] < 600:
        # Narrow layouts use fewer, much larger elements instead of shrinking UI labels.
        if kind in ("inbox", "label", "before_after"):
            d.rounded_rectangle((200, 80, 700, 330), radius=30, fill="#103853", outline=accent, width=7)
            d.line((210, 100, 450, 245, 690, 100), fill=accent, width=7)
            d.rounded_rectangle((140, 410, 760, 535), radius=30, fill=accent)
            _text(d, "OZNAKA", (450, 473), 62, palette["background"], font_path, bold=True, anchor="mm")
        elif kind == "filter":
            d.polygon([(110, 90), (790, 90), (540, 340), (540, 470), (360, 530), (360, 340)], fill="#103853", outline=accent, width=7)
            _text(d, "PRAVILO", (450, 218), 65, text, font_path, bold=True, anchor="mm")
        elif kind == "search":
            d.ellipse((220, 90, 570, 440), outline=accent, width=14)
            d.line((525, 390, 700, 550), fill=accent, width=20)
        else:
            for index, label in enumerate(("Odaberi", "Provjeri", "Primijeni")):
                y = 65 + index * 185
                d.ellipse((70, y, 185, y + 115), fill=accent)
                d.line((96, y + 57, 119, y + 80, 158, y + 36), fill=palette["background"], width=9)
                _text(d, label, (230, y + 24), 60, text, font_path, bold=True)
        return ImageOps.contain(image, size, Image.Resampling.LANCZOS)

    def mail(box, fill="#102E49", marked=False):
        x0, y0, x1, y1 = box
        d.rounded_rectangle(box, radius=12, fill=fill, outline=accent if marked else border, width=3)
        d.line((x0 + 5, y0 + 8, (x0 + x1) // 2, (y0 + y1) // 2, x1 - 5, y0 + 8), fill=accent if marked else muted, width=3)

    def line(y, label, selected=False, x=66, width=768):
        d.rounded_rectangle((x, y, x + width, y + 82), radius=16, fill="#113049" if selected else "#0A2238",
                            outline=accent if selected else border, width=2)
        mail((x + 19, y + 23, x + 69, y + 60), marked=selected)
        _text(d, label, (x + 93, y + 22), 28, text, font_path)

    if kind == "inbox":
        for index in range(4):
            mail((75 + index * 18, 110 + index * 65, 255 + index * 18, 215 + index * 65), marked=index == 3)
        d.line((390, 285, 495, 285), fill=accent, width=8)
        d.polygon([(495, 285), (466, 265), (466, 305)], fill=accent)
        for index, label in enumerate(("Newsletteri", "Važne poruke", "Za kasnije")):
            line(120 + index * 124, label, selected=index == 0, x=545, width=310)
        _text(d, "MANJE TRAŽENJA. VIŠE REDA.", (450, 540), 25, muted, font_path, anchor="mm")
    elif kind == "search":
        d.rounded_rectangle((55, 85, 845, 175), radius=25, fill="#113049", outline=accent, width=3)
        d.ellipse((84, 110, 113, 139), outline=accent, width=4)
        d.line((110, 136, 124, 150), fill=accent, width=4)
        _text(d, "Pronađi poruke po pošiljaocu", (150, 113), 31, text, font_path)
        for index, label in enumerate(("Pošiljalac", "Predmet poruke", "Sadrži riječi")):
            _text(d, label, (80, 238 + index * 99), 26, muted, font_path)
            d.rounded_rectangle((340, 223 + index * 99, 810, 285 + index * 99), radius=12, fill="#113049", outline=accent if index == 0 else border, width=2)
        _text(d, "newsletter@example.com", (360, 240), 25, text, font_path)
        d.line((290, 257, 326, 257), fill=orange, width=5)
        d.polygon([(332, 257), (316, 246), (316, 268)], fill=orange)
    elif kind == "filter":
        _text(d, "AKO PORUKA ODGOVARA…", (450, 92), 27, muted, font_path, anchor="mm")
        d.polygon([(165, 150), (735, 150), (525, 345), (525, 405), (375, 445), (375, 345)], fill="#103853", outline=accent, width=4)
        _text(d, "ODABRANI POŠILJALAC", (450, 228), 30, text, font_path, bold=True, anchor="mm")
        d.line((450, 450, 450, 485), fill=accent, width=5)
        d.rounded_rectangle((180, 490, 720, 578), radius=20, fill=accent)
        _text(d, "DODIJELI OZNAKU", (450, 534), 32, palette["background"], font_path, bold=True, anchor="mm")
    elif kind == "label":
        for index, label in enumerate(("Važna poruka", "Newsletter", "Još jedan newsletter")):
            line(85 + index * 125, label, selected=index > 0)
        d.rounded_rectangle((510, 475, 820, 555), radius=22, fill=accent)
        _text(d, "Newsletteri", (665, 515), 32, palette["background"], font_path, bold=True, anchor="mm")
        d.line((655, 450, 655, 475), fill=accent, width=5)
    elif kind == "before_after":
        for x, label, color in ((35, "PRIJE", orange), (475, "POSLIJE", accent)):
            d.rounded_rectangle((x, 50, x + 390, 560), radius=24, fill="#0A2238", outline=border, width=2)
            _text(d, label, (x + 195, 99), 29, color, font_path, bold=True, anchor="mm")
            for i in range(4):
                y = 165 + i * 86
                mail((x + 28, y, x + 90, y + 47), marked=x > 40)
                d.rounded_rectangle((x + 114, y + 8, x + 350, y + 24), radius=7,
                                    fill=accent if x > 40 and i % 2 == 0 else border)
                d.rounded_rectangle((x + 114, y + 36, x + 275, y + 45), radius=4, fill=border)
    else:
        for index, label in enumerate(("Odaberi zadatak", "Provjeri rezultat", "Primijeni korak")):
            y = 100 + index * 150
            d.rounded_rectangle((65, y, 835, y + 106), radius=22, fill="#113049", outline=border, width=2)
            d.ellipse((92, y + 22, 154, y + 84), fill=accent)
            d.line((108, y + 53, 119, y + 65, 139, y + 42), fill=palette["background"], width=6)
            _text(d, label, (190, y + 34), 34, text, font_path, bold=True)
    return ImageOps.contain(image, size, Image.Resampling.LANCZOS)


def render_visual(image, visual, box, palette, catalogue, font_path, fit):
    """Paste a contained graphic, with truthful provenance and optional callout legend."""
    x, y, width, height = box
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=28, fill=palette["panel"], outline="#24445F", width=2)
    asset = catalogue.get(visual.get("asset_id")) if visual["kind"] == "image" else None
    label = "SNIMAK EKRANA" if asset and asset["type"] == "screenshot" else "ILUSTRACIJA" if asset else "SHEMATSKI PRIKAZ"
    _text(draw, label, (x + 24, y + 22), 20, palette["accent"], font_path, bold=True)
    legend = " · ".join(f"{i}. {mark['label']}" for i, mark in enumerate(asset.get("annotations", []), 1)) if asset else ""
    caption = visual.get("caption", "")
    note = "\n".join(t for t in (caption, legend) if t)
    note_height = 115 if note else 0
    inner_size = (width - 40, height - 85 - note_height)
    if min(inner_size) < 60:
        raise ValueError("Vizual nema dovoljno prostora u odabranom rasporedu.")
    graphic = prepared_asset(asset, font_path) if asset else schematic(visual["kind"], inner_size, palette, font_path)
    graphic = ImageOps.contain(graphic, inner_size, Image.Resampling.LANCZOS)
    if asset and asset["type"] == "screenshot" and graphic.width < asset.get("min_display_width", 640):
        raise ValueError("Screenshot je premalen za čitanje. Koristi stacked raspored ili uži izrez slike.")
    image.paste(graphic, (x + (width - graphic.width) // 2, y + 65 + (inner_size[1] - graphic.height) // 2))
    if note:
        wrapped, font = fit(draw, note, (x + 24, y + height - note_height, width - 48, note_height - 16), minimum=24, maximum=28)
        draw.multiline_text((x + 24, y + height - note_height), wrapped, fill="#A6B6C9", font=font, spacing=14)


def render_slide(slide, visual, brand, catalogue, number, total, font_path, fit):
    if brand.get("layout_style") == "editorial":
        from carousel_editorial import render_editorial
        return render_editorial(slide, visual, brand, catalogue, number, total, font_path, fit)
    palette = brand["design"]
    image = Image.new("RGB", (1080, 1350), palette["background"])
    draw = ImageDraw.Draw(image)
    for x in range(0, 1080, 90):
        draw.line((x, 0, x, 1350), fill=palette["grid"])
    for y in range(0, 1350, 90):
        draw.line((0, y, 1080, y), fill=palette["grid"])
    _text(draw, brand["name"], (64, 56), 26, palette["accent"], font_path, bold=True)
    _text(draw, f"{number:02d} / {total:02d}", (1016, 56), 26, "#A6B6C9", font_path, anchor="ra")
    draw.line((64, 112, 1016, 112), fill="#24445F", width=2)
    draw.line((64, 112, 64 + round(952 * number / total), 112), fill=palette["accent"], width=4)
    layout = visual.get("layout", "auto")
    if visual["kind"] == "none":
        layout = "text"
    elif layout == "auto":
        layout = "cover" if number == 1 else "stacked"
    if layout == "cover":
        title_box, body_box, visual_box = (64, 174, 952, 240), (72, 1035, 936, 180), (64, 445, 952, 550)
    elif layout == "split":
        title_box, body_box, visual_box = (64, 170, 952, 230), (64, 490, 398, 710), (505, 465, 511, 740)
    elif layout == "comparison":
        title_box, body_box, visual_box = (64, 170, 952, 200), (64, 1010, 952, 205), (64, 405, 952, 565)
    elif layout == "stacked":
        title_box, body_box, visual_box = (64, 170, 952, 200), (64, 397, 952, 185), (64, 610, 952, 595)
    else:
        title_box, body_box, visual_box = (80, 245, 920, 300), (80, 655, 920, 530), None
    for key, box, max_size, minimum, bold in (("title", title_box, 78 if layout == "cover" else 66, 42, True),
                                               ("body", body_box, 44 if layout != "split" else 40, 32, False)):
        value, font = fit(draw, slide[key], box, bold=bold, minimum=minimum, maximum=max_size)
        draw.multiline_text(box[:2], value, font=font, fill=palette["text"], spacing=14)
    if visual_box:
        render_visual(image, visual, visual_box, palette, catalogue, font_path, fit)
    _text(draw, brand["handle"], (64, 1278), 26, palette["accent"], font_path)
    _text(draw, "SAČUVAJ ZA KASNIJE" if number == total else "PREVUCI  →",
          (1016, 1278), 22, "#A6B6C9", font_path, anchor="ra")
    return image
