
from PIL import Image, ImageDraw, ImageFont, ImageOps
import time, json, os, textwrap, random
from pathlib import Path

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
PHOTO_FOLDER = "static/uploads"
ICON_FOLDER = "static/icons"

# Font setup
font_path = "static/fonts/Pacifico-Regular.ttf"
if not os.path.exists(font_path):
    font_path = None

font_large = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
font_medium = ImageFont.truetype(font_path, 26) if font_path else ImageFont.load_default()
font_small = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()

# Pastel Graduation Theme Colors
themes = {
    "pastel_graduation": {
        "backgrounds": [
            (255, 240, 245),
            (240, 255, 250),
            (245, 240, 255),
            (255, 250, 240),
        ],
        "text": (40, 30, 60),
        "bubble": (255, 255, 255, 240),
        "overlay_icons": ["heart.png", "sparkle.png", "gradcap.png"]
    }
}

active_theme = themes["pastel_graduation"]

def draw_message(msg, theme=active_theme):
    bg_color = random.choice(theme["backgrounds"])
    overlay_icons = theme.get("overlay_icons", [])

    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw polaroid photo
    if msg.get("photo"):
        photo_path = os.path.join(PHOTO_FOLDER, msg["photo"])
        if os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path).convert("RGB")
                photo.thumbnail((280, 200))
                polaroid_height = photo.height + 50
                polaroid = Image.new("RGB", (photo.width + 20, polaroid_height), "white")
                polaroid.paste(photo, (10, 10))

                shadow = Image.new("RGB", (polaroid.width + 6, polaroid.height + 6), (220, 220, 220))
                shadow_offset = ((DISPLAY_WIDTH - polaroid.width) // 2 + 4, 22)
                img.paste(shadow, shadow_offset)
                img.paste(polaroid, ((DISPLAY_WIDTH - polaroid.width) // 2, 20))
            except Exception as e:
                print("Photo error:", e)

    # Message setup
    message_text = msg.get("message", "")
    message_lines = textwrap.wrap(message_text, width=28)
    bubble_height = 16 + len(message_lines) * 28
    bubble_width = DISPLAY_WIDTH - 80  # tighter bubble with more padding
    bubble_x0 = 40
    bubble_y0 = DISPLAY_HEIGHT - bubble_height - 30

    # Name label above the bubble
    name_text = f"{msg.get('name', 'Someone')} says:"
    name_x = bubble_x0
    name_y = bubble_y0 - 34  # above the bubble
    draw.text((name_x, name_y), name_text, fill=theme["text"], font=font_medium)

    # Draw message bubble with better padding
    bubble_rect = Image.new("RGBA", (bubble_width, bubble_height), theme["bubble"])
    draw_bubble = ImageDraw.Draw(bubble_rect)
    for i, line in enumerate(message_lines):
        draw_bubble.text((20, 8 + i * 28), line, font=font_small, fill=theme["text"])

    img.paste(bubble_rect, (bubble_x0, bubble_y0), bubble_rect)

    # Overlay icons, avoid center-top
    for icon_name in overlay_icons:
        icon_path = os.path.join(ICON_FOLDER, icon_name)
        if os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((32, 32))
                for _ in range(3):
                    x = random.randint(10, DISPLAY_WIDTH - 42)
                    y = random.randint(10, DISPLAY_HEIGHT - 42)
                    if not (180 < x < 300 and y < 110):
                        break
                img.paste(icon, (x, y), icon)
            except Exception as e:
                print("Icon error:", e)

    return img
