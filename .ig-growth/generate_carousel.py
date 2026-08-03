#!/usr/bin/env python3
"""
Instagram Carousel Generator - 9 Neon Cyber Slides
Generiše 1080x1350px PNG slike za karuzel post
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# ============================================================================
# KONSTANTE - BOJE I DIMENZIJE
# ============================================================================

# Neon Cyber Paleta (iz paleta_hex.txt)
DARK_BG = "#010B18"           # Tamna navy - pozadina
NEON_CYAN = "#30D1F5"         # Neon cyan - akcentu
WHITE = "#FFFFFF"              # Bela - tekst
RED_ALERT = "#8B2E3A"         # Crvena - akcenti
GRAY_TEXT = "#BDC2CA"         # Light gray - secondary tekst

# Instagram Carousel Standard
WIDTH = 1080
HEIGHT = 1350

# Output direktorijum
OUTPUT_DIR = Path(__file__).parent / "carousel_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# SLIDE DEFINICIJE
# ============================================================================

SLIDES = [
    {
        "number": 1,
        "type": "cover",
        "title": "7 AI Alata",
        "subtitle": "Koja Štede 35h/Mesec",
        "detail": "Bez programiranja | Besplatno | Početak: Sada",
    },
    {
        "number": 2,
        "type": "tool",
        "title": "#1 Email Automatizacija",
        "emoji": "📧",
        "time_saved": "3h/mesec",
        "description": "Chat GPT + Make.com\nAutomatski odgovori na česte email-e",
    },
    {
        "number": 3,
        "type": "tool",
        "title": "#2 AI Slike",
        "emoji": "🎨",
        "time_saved": "2h/mesec",
        "description": "Midjourney / Canva\n30 sekundi za gotovu sliku",
    },
    {
        "number": 4,
        "type": "tool",
        "title": "#3 Transkripcija",
        "emoji": "🎤",
        "time_saved": "1.5h/mesec",
        "description": "Opus.pro\nVideo → Tekst u 2 minuta",
    },
    {
        "number": 5,
        "type": "tool",
        "title": "#4 Content Ideation",
        "emoji": "💡",
        "time_saved": "1h/mesec",
        "description": "Chat GPT\n10 ideju za 30 sekundi",
    },
    {
        "number": 6,
        "type": "tool",
        "title": "#5 Social Scheduling",
        "emoji": "📅",
        "time_saved": "1h/mesec",
        "description": "Buffer / Zapier\nAutomatski post-ovi",
    },
    {
        "number": 7,
        "type": "tool",
        "title": "#6 Analitika",
        "emoji": "📊",
        "time_saved": "1h/mesec",
        "description": "Google Analytics\nSve metrike na jednom mestu",
    },
    {
        "number": 8,
        "type": "tool",
        "title": "#7 CRM / Lead Capture",
        "emoji": "🎯",
        "time_saved": "0.5h/mesec",
        "description": "Linktree + Zapier\nAutomatski lead tracking",
    },
    {
        "number": 9,
        "type": "cta",
        "title": "Počni Sada",
        "subtitle": "Besplatan Checklist",
        "detail": "linktr.ee/goran015",
        "cta": "Sve 7 Alata Sa Setup Guide-om",
    },
]

# ============================================================================
# HELPER FUNKCIJE
# ============================================================================

def hex_to_rgb(hex_color):
    """Konvertuj hex boju u RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def draw_text_centered(draw, text, xy, font, fill, max_width=None, line_height=1.2):
    """Crta tekst centrirano. Poštuje eksplicitni \\n, pa tek onda word-wrap."""
    x, y = xy

    # Eksplicitni prelomi reda su uvek prvi - word-wrap se primenjuje unutar njih
    lines = []
    for paragraph in text.split('\n'):
        if not max_width:
            lines.append(paragraph)
            continue

        current_line = []
        for word in paragraph.split():
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        lines.append(' '.join(current_line))

    # Crta svaki red
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_x = x - line_width // 2
        line_y = y + i * int(font.size * line_height)
        draw.text((line_x, line_y), line, font=font, fill=fill)

def create_slide(slide_data):
    """Kreiraj jednu sliku slide-a"""
    # Kreiraj nova slika
    img = Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(DARK_BG))
    draw = ImageDraw.Draw(img)

    # Pokušaj da učita font, ako ne uspe koristi default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        detail_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        badge_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
    except:
        # Fallback ako font ne postoji
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        detail_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()

    # ========== COVER SLIDE (Slide 1) ==========
    if slide_data["type"] == "cover":
        # Veliki "7" u centru
        try:
            big_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 280)
        except:
            big_font = title_font

        draw.text((WIDTH//2, 350), "7", font=big_font, fill=hex_to_rgb(NEON_CYAN), anchor="mm")

        # Naslov
        draw_text_centered(draw, slide_data["title"], (WIDTH//2, 650), title_font, hex_to_rgb(WHITE))

        # Podnaslov
        draw_text_centered(draw, slide_data["subtitle"], (WIDTH//2, 750), subtitle_font, hex_to_rgb(NEON_CYAN))

        # Detalj na dnu
        draw_text_centered(draw, slide_data["detail"], (WIDTH//2, 1250), detail_font, hex_to_rgb(GRAY_TEXT))

        # Dekorativna linija
        draw.rectangle([(100, 900), (WIDTH-100, 910)], fill=hex_to_rgb(NEON_CYAN))

    # ========== TOOL SLIDE (Slides 2-8) ==========
    elif slide_data["type"] == "tool":
        # Kruzni badge sa rednim brojem alata - zamena za emoji
        # (emoji se ne renderuje jer DejaVu font nema glifove za njih)
        tool_num = str(slide_data["number"] - 1)
        badge_r = 90
        badge_cx, badge_cy = WIDTH // 2, 280
        draw.ellipse(
            [(badge_cx - badge_r, badge_cy - badge_r), (badge_cx + badge_r, badge_cy + badge_r)],
            outline=hex_to_rgb(NEON_CYAN), width=6
        )
        draw.text((badge_cx, badge_cy), tool_num, font=badge_font,
                  fill=hex_to_rgb(NEON_CYAN), anchor="mm")

        # Naziv alata (bez "#N" prefiksa - broj je vec u badge-u)
        clean_title = slide_data["title"].split(" ", 1)[1]
        draw_text_centered(draw, clean_title, (WIDTH//2, 470), title_font,
                           hex_to_rgb(WHITE), max_width=920)

        # Dekorativna linija
        draw.rectangle([(240, 640), (WIDTH-240, 648)], fill=hex_to_rgb(NEON_CYAN))

        # Vreme stednje - istaknuto
        draw_text_centered(draw, f"Štedi {slide_data['time_saved']}", (WIDTH//2, 720),
                           subtitle_font, hex_to_rgb(RED_ALERT))

        # Opis - eksplicitni prelomi reda se sada postuju
        draw_text_centered(draw, slide_data["description"], (WIDTH//2, 900), body_font,
                           hex_to_rgb(WHITE), max_width=880, line_height=1.45)

        # Footer sa brojem slide-a
        draw_text_centered(draw, f"{slide_data['number']} / 9", (WIDTH//2, 1270), small_font, hex_to_rgb(GRAY_TEXT))

    # ========== CTA SLIDE (Slide 9) ==========
    elif slide_data["type"] == "cta":
        # Naslov
        draw_text_centered(draw, slide_data["title"], (WIDTH//2, 300), title_font, hex_to_rgb(NEON_CYAN))

        # Podnaslov
        draw_text_centered(draw, slide_data["subtitle"], (WIDTH//2, 450), subtitle_font, hex_to_rgb(WHITE))

        # CTA box (visoko vidljiv)
        box_y_top = 600
        box_y_bottom = 800
        draw.rectangle([(100, box_y_top), (WIDTH-100, box_y_bottom)], outline=hex_to_rgb(NEON_CYAN), width=3)
        draw_text_centered(draw, slide_data["cta"], (WIDTH//2, (box_y_top + box_y_bottom)//2), body_font, hex_to_rgb(NEON_CYAN), max_width=800)

        # Link na dnu
        draw_text_centered(draw, slide_data["detail"], (WIDTH//2, 1100), subtitle_font, hex_to_rgb(NEON_CYAN))

        # Footer
        draw_text_centered(draw, "Besplatan Setup Guide + Templates", (WIDTH//2, 1250), detail_font, hex_to_rgb(GRAY_TEXT))

    return img

# ============================================================================
# MAIN - GENERIŠI SVE SLIDES
# ============================================================================

def main():
    print(f"🎨 Generiše {len(SLIDES)} slide-ova za Instagram karuzel...")
    print(f"📁 Output direktorijum: {OUTPUT_DIR}")
    print()

    for slide_data in SLIDES:
        print(f"  Slide {slide_data['number']:02d}/09 - {slide_data.get('title', 'Unknown')}...", end="", flush=True)

        try:
            # Kreiraj sliku
            img = create_slide(slide_data)

            # Spremi PNG
            output_path = OUTPUT_DIR / f"slide_{slide_data['number']:02d}.png"
            img.save(output_path, 'PNG', quality=95)

            print(" ✅")
        except Exception as e:
            print(f" ❌ GREŠKA: {e}")

    print()
    print("✨ Karuzel je Gotov!")
    print(f"📸 9 PNG slika sprema za Instagram carousel upload")
    print(f"📁 Lokacija: {OUTPUT_DIR}")
    print()
    print("🚀 Sledeće korake:")
    print("  1. Otvori Instagram")
    print("  2. Kreiraj novi post")
    print("  3. Odaberi sve 9 PNG slika (u redu: slide_01 do slide_09)")
    print("  4. Upload kao carousel post")
    print("  5. Dodaj caption i hashtagi (vidi STEP_4_MONDAY_POSTING.md)")

if __name__ == "__main__":
    main()
