#!/usr/bin/env python3
"""
Instagram Carousel Generator - Futuristic Premium Edition
Generise 9 slajdova 1080x1350px u neon cyber estetici.

Dizajn sistem:
  - Vertikalni gradijent + radijalni glow umesto ravne pozadine
  - Tehnicka mreza (grid) i vinjeta za dubinu
  - HUD uglovi na svakom slajdu
  - Neonski glow na fokalnom tekstu (blur layer ispod ostrog teksta)
  - Staklene ploce (glassmorphism) za sadrzaj
  - Progress indikator umesto tekstualnog "2 / 9"
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

# ============================================================================
# DIZAJN TOKENI
# ============================================================================

BG_TOP = "#02101F"        # gornji deo gradijenta
BG_BOTTOM = "#01070E"     # donji deo gradijenta - dublji
NEON_CYAN = "#30D1F5"
CYAN_DEEP = "#1DA9DF"
WHITE = "#FFFFFF"
RED_ALERT = "#FF4D5A"     # posvetljeno u odnosu na #8B2E3A radi kontrasta
GRAY_TEXT = "#8A94A6"
GRID_LINE = "#123048"

WIDTH, HEIGHT = 1080, 1350
MARGIN = 64

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
OUTPUT_DIR = Path(__file__).parent / "carousel_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def load_fonts():
    def bold(size):
        return ImageFont.truetype(f"{FONT_DIR}/DejaVuSans-Bold.ttf", size)

    def regular(size):
        return ImageFont.truetype(f"{FONT_DIR}/DejaVuSans.ttf", size)

    return {
        "hero": bold(300),      # veliki broj na coveru
        "badge": bold(88),      # broj u badge-u
        "title": bold(62),
        "subtitle": bold(44),
        "body": regular(34),
        "chip": bold(28),
        "kicker": bold(22),     # letterspaced sitne verzalne
        "meta": regular(24),
    }


# ============================================================================
# POZADINSKI SLOJEVI
# ============================================================================

def vertical_gradient(top_hex, bottom_hex):
    """Gradijent se crta kao kolona 1px pa razvlaci - brzo i glatko."""
    c_top, c_bottom = hex_to_rgb(top_hex), hex_to_rgb(bottom_hex)
    column = Image.new("RGB", (1, HEIGHT))
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        column.putpixel((0, y), tuple(
            int(c_top[i] * (1 - t) + c_bottom[i] * t) for i in range(3)
        ))
    return column.resize((WIDTH, HEIGHT), Image.BILINEAR).convert("RGBA")


def radial_glow(center, radius, hex_color, max_alpha=70):
    """Meki radijalni sjaj. Gradi se na 1/4 rezolucije pa uvecava - jeftino."""
    scale = 4
    w, h = WIDTH // scale, HEIGHT // scale
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    cx, cy, r = center[0] // scale, center[1] // scale, radius // scale
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=max_alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(r * 0.55))
    mask = mask.resize((WIDTH, HEIGHT), Image.BILINEAR)

    layer = Image.new("RGBA", (WIDTH, HEIGHT), hex_to_rgb(hex_color) + (0,))
    layer.putalpha(mask)
    return layer


def draw_grid(img, spacing=90, alpha=16):
    """Tehnicka mreza - daje osecaj interfejsa, ne sme da se namece."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    color = hex_to_rgb(GRID_LINE) + (alpha,)
    for x in range(0, WIDTH, spacing):
        d.line([(x, 0), (x, HEIGHT)], fill=color, width=1)
    for y in range(0, HEIGHT, spacing):
        d.line([(0, y), (WIDTH, y)], fill=color, width=1)
    img.alpha_composite(layer)


def add_vignette(img, strength=110):
    """Zatamnjuje ivice da sadrzaj u centru izadje napred."""
    scale = 4
    w, h = WIDTH // scale, HEIGHT // scale
    mask = Image.new("L", (w, h), strength)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.15, -h * 0.10, w * 1.15, h * 1.10], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.18))
    mask = mask.resize((WIDTH, HEIGHT), Image.BILINEAR)

    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shade.putalpha(mask)
    img.alpha_composite(shade)


def build_backdrop(glow_center=None, glow_radius=560):
    img = vertical_gradient(BG_TOP, BG_BOTTOM)
    draw_grid(img)
    if glow_center:
        img.alpha_composite(radial_glow(glow_center, glow_radius, NEON_CYAN))
    add_vignette(img)
    return img


# ============================================================================
# HUD ELEMENTI
# ============================================================================

def draw_corner_brackets(img, length=64, width=3, inset=MARGIN, alpha=150):
    """Uglovi u stilu HUD-a - okvir bez pravog okvira."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = hex_to_rgb(NEON_CYAN) + (alpha,)
    l, t, r, b = inset, inset, WIDTH - inset, HEIGHT - inset

    for (x, y, dx, dy) in [(l, t, 1, 1), (r, t, -1, 1), (l, b, 1, -1), (r, b, -1, -1)]:
        d.line([(x, y), (x + dx * length, y)], fill=c, width=width)
        d.line([(x, y), (x, y + dy * length)], fill=c, width=width)

    img.alpha_composite(layer)


def draw_progress(img, active_index, total=9, y=1258):
    """Aktivni slajd je izduzena pilula, ostali su tacke."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    dot, active_w, gap, h = 8, 34, 14, 8
    total_w = sum(active_w if i == active_index else dot for i in range(total))
    total_w += gap * (total - 1)
    x = (WIDTH - total_w) / 2

    for i in range(total):
        w = active_w if i == active_index else dot
        fill = hex_to_rgb(NEON_CYAN) + (255,) if i == active_index else hex_to_rgb(GRAY_TEXT) + (110,)
        d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
        x += w + gap

    img.alpha_composite(layer)


def draw_accent_line(img, y, width=560, thickness=4):
    """Linija koja bledi ka krajevima - gradi se od segmenata."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0 = (WIDTH - width) / 2
    steps = 60
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(255 * (1 - abs(t - 0.5) * 2) ** 0.6)
        sx = x0 + width * t
        d.rectangle([sx, y, sx + width / steps + 1, y + thickness],
                    fill=hex_to_rgb(NEON_CYAN) + (alpha,))
    img.alpha_composite(layer)


def draw_glass_panel(img, box, radius=28, fill_alpha=16, border_alpha=64):
    """Poluprozirna ploca sa tankim ramom - nosi telo teksta."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=radius,
                        fill=hex_to_rgb(NEON_CYAN) + (fill_alpha,),
                        outline=hex_to_rgb(NEON_CYAN) + (border_alpha,), width=2)
    img.alpha_composite(layer)


def draw_chip(img, text, center, font, text_hex, border_hex, pad_x=34, pad_y=16):
    """Pilula sa ramom - za istaknute metrike."""
    tmp = ImageDraw.Draw(img)
    tw = tmp.textlength(text, font=font)
    th = font.size
    cx, cy = center
    box = [cx - tw / 2 - pad_x, cy - th / 2 - pad_y,
           cx + tw / 2 + pad_x, cy + th / 2 + pad_y]

    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=(th + pad_y * 2) // 2,
                        fill=hex_to_rgb(border_hex) + (26,),
                        outline=hex_to_rgb(border_hex) + (150,), width=2)
    img.alpha_composite(layer)

    ImageDraw.Draw(img).text((cx, cy), text, font=font,
                             fill=hex_to_rgb(text_hex), anchor="mm")


# ============================================================================
# TEKST
# ============================================================================

def glow_text(img, text, xy, font, hex_color, blur=22, passes=3, anchor="mm"):
    """Neonski sjaj: zamucena kopija ispod, ostar tekst se crta posle."""
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=font,
                               fill=hex_to_rgb(hex_color) + (255,), anchor=anchor)
    blurred = layer.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(passes):
        img.alpha_composite(blurred)


def draw_tracked(img, text, xy, font, hex_color, tracking=9, alpha=255):
    """Razmaknuta verzalna slova - signalizira 'tehnicki' registar."""
    d = ImageDraw.Draw(img)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(text, widths):
        d.text((x, xy[1]), ch, font=font, fill=hex_to_rgb(hex_color) + (alpha,), anchor="lm")
        x += w + tracking


def draw_wrapped(img, text, xy, font, hex_color, max_width=None, line_height=1.4):
    """Postuje eksplicitni \\n, pa tek onda prelama po sirini."""
    d = ImageDraw.Draw(img)
    lines = []
    for paragraph in text.split("\n"):
        if not max_width:
            lines.append(paragraph)
            continue
        current = []
        for word in paragraph.split():
            trial = " ".join(current + [word])
            if d.textlength(trial, font=font) > max_width and current:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        lines.append(" ".join(current))

    step = font.size * line_height
    start_y = xy[1] - (len(lines) - 1) * step / 2
    for i, line in enumerate(lines):
        d.text((xy[0], start_y + i * step), line, font=font,
               fill=hex_to_rgb(hex_color), anchor="mm")


# ============================================================================
# SADRZAJ SLAJDOVA
# ============================================================================

SLIDES = [
    {
        "type": "cover",
        "kicker": "OD NULE DO AI",
        "hero": "7",
        "title": "AI ALATA",
        "subtitle": "koja štede 35h mesečno",
        "chips": ["BEZ KODA", "BESPLATNO", "ZA POČETNIKE"],
    },
    {
        "type": "tool", "index": 1,
        "title": "Email Automatizacija",
        "time_saved": "3h mesečno",
        "stack": "ChatGPT + Make.com",
        "description": "Automatski odgovori na česte upite.\nPostaviš jednom, radi zauvek.",
    },
    {
        "type": "tool", "index": 2,
        "title": "AI Slike",
        "time_saved": "2h mesečno",
        "stack": "Midjourney / Canva",
        "description": "Gotova grafika za 30 sekundi.\nBez dizajnera i bez stock fotografija.",
    },
    {
        "type": "tool", "index": 3,
        "title": "Transkripcija",
        "time_saved": "1.5h mesečno",
        "stack": "Opus.pro",
        "description": "Video pretvoriš u tekst za 2 minuta.\nSpremno za blog, post ili karusel.",
    },
    {
        "type": "tool", "index": 4,
        "title": "Ideje za Sadržaj",
        "time_saved": "1h mesečno",
        "stack": "ChatGPT",
        "description": "Deset ideja za trideset sekundi.\nNikad više prazan ekran.",
    },
    {
        "type": "tool", "index": 5,
        "title": "Zakazivanje Objava",
        "time_saved": "1h mesečno",
        "stack": "Buffer / Zapier",
        "description": "Nedelja objava zakazana odjednom.\nObjavljuje se dok ti spavaš.",
    },
    {
        "type": "tool", "index": 6,
        "title": "Analitika",
        "time_saved": "1h mesečno",
        "stack": "Google Analytics",
        "description": "Sve metrike na jednom mestu.\nPregled za pet minuta, ne za sat.",
    },
    {
        "type": "tool", "index": 7,
        "title": "Praćenje Kontakata",
        "time_saved": "0.5h mesečno",
        "stack": "Linktree + Zapier",
        "description": "Svaki klik i kontakt se beleži sam.\nNema ručnog prepisivanja.",
    },
    {
        "type": "cta",
        "kicker": "SLEDEĆI KORAK",
        "title": "POČNI SADA",
        "subtitle": "Besplatan setup paket",
        "items": [
            "Checklist svih 7 alata",
            "Uputstva korak po korak",
            "Gotovi šabloni za start",
        ],
        "link": "linktr.ee/goran015",
        "footer": "Komentariši SETUP i šaljem ti odmah",
    },
]


# ============================================================================
# RENDER
# ============================================================================

def render_cover(data, f):
    img = build_backdrop(glow_center=(WIDTH // 2, 430), glow_radius=620)
    draw_corner_brackets(img)

    draw_tracked(img, data["kicker"], (WIDTH // 2, 190), f["kicker"], NEON_CYAN, tracking=14)

    glow_text(img, data["hero"], (WIDTH // 2, 450), f["hero"], NEON_CYAN, blur=40, passes=4)
    ImageDraw.Draw(img).text((WIDTH // 2, 450), data["hero"], font=f["hero"],
                             fill=hex_to_rgb(WHITE), anchor="mm")

    glow_text(img, data["title"], (WIDTH // 2, 730), f["title"], NEON_CYAN, blur=26, passes=2)
    ImageDraw.Draw(img).text((WIDTH // 2, 730), data["title"], font=f["title"],
                             fill=hex_to_rgb(WHITE), anchor="mm")

    ImageDraw.Draw(img).text((WIDTH // 2, 820), data["subtitle"], font=f["subtitle"],
                             fill=hex_to_rgb(NEON_CYAN), anchor="mm")

    draw_accent_line(img, 910)

    # Tri metrike u redu
    positions = [WIDTH // 2 - 320, WIDTH // 2, WIDTH // 2 + 320]
    for chip, x in zip(data["chips"], positions):
        draw_chip(img, chip, (x, 1020), f["chip"], NEON_CYAN, CYAN_DEEP, pad_x=22, pad_y=14)

    d = ImageDraw.Draw(img)
    d.text((MARGIN + 24, HEIGHT - MARGIN - 40), "@goran015", font=f["meta"],
           fill=hex_to_rgb(GRAY_TEXT), anchor="lm")
    d.text((WIDTH - MARGIN - 24, HEIGHT - MARGIN - 40), "PREVUCI  →", font=f["meta"],
           fill=hex_to_rgb(NEON_CYAN), anchor="rm")
    return img


def render_tool(data, f):
    img = build_backdrop(glow_center=(WIDTH // 2, 330), glow_radius=430)
    draw_corner_brackets(img)

    draw_tracked(img, f"ALAT {data['index']:02d} — OD 07", (WIDTH // 2, 175),
                 f["kicker"], GRAY_TEXT, tracking=12)

    # Badge sa brojem alata - zamena za emoji, ne zavisi od fonta
    cx, cy, r = WIDTH // 2, 335, 92
    glow_text(img, str(data["index"]), (cx, cy), f["badge"], NEON_CYAN, blur=28, passes=2)
    ring = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([cx - r, cy - r, cx + r, cy + r],
                                 outline=hex_to_rgb(NEON_CYAN) + (220,), width=4)
    img.alpha_composite(ring)
    ImageDraw.Draw(img).text((cx, cy), str(data["index"]), font=f["badge"],
                             fill=hex_to_rgb(WHITE), anchor="mm")

    draw_wrapped(img, data["title"], (WIDTH // 2, 540), f["title"], WHITE, max_width=900)
    draw_accent_line(img, 630, width=420, thickness=3)

    draw_chip(img, f"ŠTEDI {data['time_saved'].upper()}", (WIDTH // 2, 720),
              f["chip"], RED_ALERT, RED_ALERT)

    draw_glass_panel(img, [MARGIN + 56, 830, WIDTH - MARGIN - 56, 1080])
    ImageDraw.Draw(img).text((WIDTH // 2, 892), data["stack"], font=f["chip"],
                             fill=hex_to_rgb(NEON_CYAN), anchor="mm")
    draw_wrapped(img, data["description"], (WIDTH // 2, 995), f["body"], WHITE,
                 max_width=800, line_height=1.45)

    # Tacke iznad handle-a - inace se preklapaju na dnu
    draw_progress(img, data["index"], y=1192)
    ImageDraw.Draw(img).text((WIDTH // 2, 1268), "@goran015",
                             font=f["meta"], fill=hex_to_rgb(GRAY_TEXT), anchor="mm")
    return img


def render_cta(data, f):
    img = build_backdrop(glow_center=(WIDTH // 2, 380), glow_radius=560)
    draw_corner_brackets(img)

    draw_tracked(img, data["kicker"], (WIDTH // 2, 190), f["kicker"], GRAY_TEXT, tracking=14)

    glow_text(img, data["title"], (WIDTH // 2, 330), f["title"], NEON_CYAN, blur=32, passes=3)
    ImageDraw.Draw(img).text((WIDTH // 2, 330), data["title"], font=f["title"],
                             fill=hex_to_rgb(WHITE), anchor="mm")

    ImageDraw.Draw(img).text((WIDTH // 2, 425), data["subtitle"], font=f["subtitle"],
                             fill=hex_to_rgb(NEON_CYAN), anchor="mm")

    draw_glass_panel(img, [MARGIN + 40, 530, WIDTH - MARGIN - 40, 830])
    d = ImageDraw.Draw(img)
    for i, item in enumerate(data["items"]):
        y = 610 + i * 78
        d.ellipse([MARGIN + 100, y - 9, MARGIN + 118, y + 9],
                  outline=hex_to_rgb(NEON_CYAN), width=3)
        d.text((MARGIN + 152, y), item, font=f["body"], fill=hex_to_rgb(WHITE), anchor="lm")

    glow_text(img, data["link"], (WIDTH // 2, 990), f["subtitle"], NEON_CYAN, blur=26, passes=2)
    draw_chip(img, data["link"], (WIDTH // 2, 990), f["subtitle"], WHITE, NEON_CYAN,
              pad_x=48, pad_y=22)

    draw_accent_line(img, 1105, width=460, thickness=3)
    ImageDraw.Draw(img).text((WIDTH // 2, 1180), data["footer"], font=f["body"],
                             fill=hex_to_rgb(GRAY_TEXT), anchor="mm")

    draw_progress(img, 8)
    return img


RENDERERS = {"cover": render_cover, "tool": render_tool, "cta": render_cta}


def main():
    fonts = load_fonts()
    print(f"Generisem {len(SLIDES)} slajdova -> {OUTPUT_DIR}\n")

    for i, data in enumerate(SLIDES, start=1):
        label = data.get("title", "cover")
        print(f"  {i:02d}/09  {label:.<34}", end="", flush=True)
        img = RENDERERS[data["type"]](data, fonts)
        img.convert("RGB").save(OUTPUT_DIR / f"slide_{i:02d}.png", "PNG")
        print(" ok")

    print(f"\nGotovo. 9 slajdova 1080x1350px u {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
