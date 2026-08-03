"""
IG Growth Engine - Phase 3: Slide Image Prompts
Trend: AI za automatizaciju
Date: 2026-08-03
Handle: @Goran015

Visual design system for carousel post with 7 slides + cover + CTA
"""

DESIGN_SYSTEM = {
    "brand_colors": {
        "primary": "#6366F1",      # Indigo (AI/tech)
        "accent": "#EC4899",       # Pink (energy)
        "success": "#10B981",      # Green (automation works)
        "background": "#0F172A",   # Dark navy
        "text": "#F1F5F9"          # Light
    },
    "typography": {
        "headline": "Inter Bold 48px",
        "subheading": "Inter Semibold 28px",
        "body": "Inter Regular 18px"
    },
    "layout": {
        "padding": "40px",
        "border_radius": "12px",
        "aspect_ratio": "1080x1350"
    }
}

SLIDES = [
    {
        "slide": "COVER",
        "title": "7 Poslova koje AI može za tebe",
        "subtitle": "Automatizacija do 35 sati mesečno",
        "visual_prompt": """
        Create a bold, modern Instagram carousel cover slide with:
        - Dark navy background (#0F172A)
        - Large glowing number "7" in neon indigo with motion blur
        - Laptop screen showing automation happening (arrows, checkmarks flowing)
        - Sleeping person silhouette in corner (represents passive income)
        - Floating icons: email, calendar, chat bubble, spreadsheet, cloud
        - Text: "7 Poslova koje AI može za tebe" in white/indigo gradient
        - Glow effects around icons
        - Modern, clean, minimalist design
        - Mobile screenshot style borders
        """,
        "design_notes": "Hero slide - grab attention, create curiosity",
        "cta_placement": "Bottom center"
    },
    {
        "slide": 1,
        "title": "Email Management",
        "subtitle": "Automatski odgovori + kategorizacija",
        "tool": "Gmail + Make",
        "visual_prompt": """
        Instagram carousel slide for Email Automation:
        - Split screen: Left = messy inbox (red notifications), Right = organized inbox (green checkmarks)
        - Laptop with Gmail open, showing automation flow arrows
        - Tool logos: Gmail icon + Make.com gears spinning
        - Left side: chaos (100+ unread emails, angry face emoji)
        - Right side: peace (organized folders, happy face emoji)
        - Timeline showing: Before (5 hours) vs After (15 minutes)
        - Color scheme: Red → Green, Indigo accents
        - Text overlay: "From Chaos to Zen in 2 minutes"
        - Small code snippet showing "IF new email → THEN auto-sort"
        """,
        "design_notes": "Show transformation through visual contrast",
        "cta_text": "Save this setup in bio 👆"
    },
    {
        "slide": 2,
        "title": "Social Media Posting",
        "subtitle": "Automatski objavljivanje po rasporedu",
        "tool": "Buffer",
        "visual_prompt": """
        Instagram carousel slide for Social Media Automation:
        - Calendar view showing automated posts scheduled throughout the week
        - Phone screens showing Instagram posts going live at scheduled times
        - Buffer logo prominent, spinning gears
        - Monday-Sunday timeline at bottom
        - Posts appearing with sparkle/magical animations
        - Clock showing different times: 9am, 1pm, 6pm, 9pm
        - Person sleeping with Z's while posts are publishing (passive activity)
        - Green checkmarks appearing as posts go live
        - Color: Indigo, green, white on dark background
        - Text: "Never miss a post again"
        """,
        "design_notes": "Emphasize passive income/automation aspect",
        "cta_text": "Free plan includes 3 posts/day"
    },
    {
        "slide": 3,
        "title": "Kalendar Organizacija",
        "subtitle": "Automatski zakazivanje + reminders",
        "tool": "Google Calendar + Zapier",
        "visual_prompt": """
        Instagram carousel slide for Calendar Automation:
        - Google Calendar showing densely packed schedule
        - Zapier flow diagram: meeting scheduled → auto-add to calendar → send reminder
        - Laptop with three monitor setup showing different time zones
        - Meeting blocks in different colors (client calls, deep work, breaks)
        - Notification popups appearing in sequence
        - Clock and timezone indicators (multiple time zones)
        - Brain relief visual (simplified workflow = less stress)
        - Zapier wizard logo
        - Before/After: messy paper calendar vs digital organized version
        - Text: "Never miss a meeting again"
        """,
        "design_notes": "Show complexity reduction",
        "cta_text": "Timezone automation = 🎯"
    },
    {
        "slide": 4,
        "title": "AI Content Writing",
        "subtitle": "Drafts sa ChatGPT",
        "tool": "Make + ChatGPT API",
        "visual_prompt": """
        Instagram carousel slide for AI Content Writing:
        - Split screen: Left = blank page (writer's block, frustrated face)
        - Right = overflowing with text, ChatGPT generating text in real-time
        - Typing cursor moving fast with text appearing letter by letter
        - ChatGPT logo glowing
        - Make.com automation flow showing: trigger → ChatGPT → output document
        - Different content types shown: email drafts, social posts, blog paragraphs
        - Lightbulb emoji for ideas
        - Person at desk with coffee looking happy while text generates
        - Green progress bar filling up with "5 minutes → ready to edit"
        - Text: "From blank page to 1000 words in minutes"
        """,
        "design_notes": "Relatable writer's block to productivity",
        "cta_text": "This is #4 = my favorite 👆"
    },
    {
        "slide": 5,
        "title": "Data Organization",
        "subtitle": "Automatic spreadsheet updates",
        "tool": "Google Sheets + Zapier",
        "visual_prompt": """
        Instagram carousel slide for Data Organization:
        - Google Sheets with multiple tabs visible
        - Data flowing in (arrows, animated data points)
        - Spreadsheet cells auto-filling with data
        - Before: manual data entry (person typing slowly, frustrated)
        - After: automatic updates (data columns filling instantly)
        - Zapier connection showing data pipeline
        - Charts and graphs updating in real-time
        - Database icons showing data sources (CRM, email, forms)
        - Green checkmarks as rows complete
        - Time saved visual: "40 hours/month → 2 hours manual review"
        - Text: "Stop copying and pasting data"
        """,
        "design_notes": "Show data accuracy + time savings",
        "cta_text": "Free for small teams"
    },
    {
        "slide": 6,
        "title": "Customer Support",
        "subtitle": "AI chatbots odgovori",
        "tool": "Tidio (besplatno) ili Manychat",
        "visual_prompt": """
        Instagram carousel slide for Customer Support Automation:
        - Chat bubble interface showing customer messages coming in
        - AI chatbot responding instantly (lightning bolt emoji)
        - Tidio/Manychat logo
        - Multiple chat windows open (showing bot handling many customers simultaneously)
        - Response time: 0.2 seconds vs human: 30 minutes
        - Customer satisfaction indicators (stars, happy faces increasing)
        - Handoff to human agent when needed (smooth transition arrow)
        - Night mode showing bot working while you sleep
        - Green online indicator
        - Text: "24/7 support without 24/7 work"
        - Dashboard showing customer happiness metrics
        """,
        "design_notes": "Show scale and 24/7 capability",
        "cta_text": "Frees you from customer support"
    },
    {
        "slide": 7,
        "title": "Backup & Archiving",
        "subtitle": "Auto cloud backup",
        "tool": "Google Drive + Make",
        "visual_prompt": """
        Instagram carousel slide for Backup Automation:
        - Data flowing into cloud with arrows
        - Multiple backup layers shown (redundancy)
        - Google Drive icon with cloud storage visualization
        - Before: single laptop (vulnerable, scary red X)
        - After: cloud + multiple backups (secure green checkmarks)
        - Shield icon representing protection
        - Disaster recovery scenario (lightning strike, computer failure)
        - Files safely backed up despite disaster
        - Timeline showing backup schedule (daily/hourly)
        - Progress indicators for backup completion
        - Peace of mind visual (person relaxed)
        - Text: "Never lose data again"
        - Storage gauge showing capacity used
        """,
        "design_notes": "Security and peace of mind",
        "cta_text": "Essential protection"
    },
    {
        "slide": "CTA_FINAL",
        "title": "Šta je sleće?",
        "subtitle": "Odaberi jedan i kreni SADA",
        "visual_prompt": """
        Final CTA slide for carousel ending:
        - Bold background with motion blur effect
        - All 7 tool logos arranged in circle around center
        - Question in center: "Koji od ovih 7 bi ti dao najveću slobodu?"
        - Three action buttons:
          1. "Setup guide u bio 👆" (link arrow)
          2. "Save for later" (bookmark icon)
          3. "Pošalji prijatelju" (share icon)
        - Goran015 handle @Goran015
        - Color: Indigo primary with all accent colors
        - Motion: Subtle pulsing effect on logos
        - Text: "Zahteva 30 minuta setup = 35 sati/mesec štednje"
        """,
        "design_notes": "Strong call-to-action, create urgency",
        "cta_text": "Tag 3 prijatelja koji trebaju ovo 👇"
    }
]

PRODUCTION_NOTES = {
    "tools_needed": [
        "Figma or Canva Pro (recommended for consistency)",
        "Midjourney or DALL-E 3 for illustrations",
        "Mobile phone for final preview"
    ],
    "timeline": "2-3 hours for all 9 slides",
    "export_settings": {
        "format": "PNG",
        "resolution": "1080x1350px",
        "quality": "95%"
    },
    "carousel_order": [
        "COVER",
        "Slide 1: Email",
        "Slide 2: Social Media",
        "Slide 3: Calendar",
        "Slide 4: Content Writing",
        "Slide 5: Data Organization",
        "Slide 6: Customer Support",
        "Slide 7: Backup",
        "CTA_FINAL"
    ],
    "posting_strategy": {
        "best_time": "Tuesday-Thursday, 6-9 PM (peak engagement)",
        "caption_style": "Conversational, pattern-interrupt hook",
        "hashtag_strategy": "Mix of trending + niche-specific",
        "engagement_loop": "Respond to comments in first 2 hours"
    }
}

ACCESSIBILITY_NOTES = {
    "alt_text_strategy": "Describe each slide for visually impaired followers",
    "color_contrast": "WCAG AA compliant (7+ ratio)",
    "text_size": "Minimum 24px for readability on mobile",
    "emoji_usage": "Strategic - max 3 per slide"
}

if __name__ == "__main__":
    print(f"Phase 3: Slide Image Prompts Generated")
    print(f"Total slides: {len(SLIDES)}")
    print(f"Brand colors: {len(DESIGN_SYSTEM['brand_colors'])} colors")
    print(f"Estimated creation time: 2-3 hours")
    print(f"\nNext step: Phase 4 - Comment + DM Flow automation")
