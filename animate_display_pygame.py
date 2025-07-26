import os, time, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import pygame

# Config
DISPLAY_WIDTH, DISPLAY_HEIGHT = 480, 320
MESSAGE_FILE = "messages.json"
SPLASH_IMAGE = "static/uploads/grad-splash.jpg"
ICON_FOLDER = "static/icons"
PHOTO_FOLDER = "static/uploads"
FONT_NAME = "static/fonts/Pacifico-Regular.ttf"
FONT_MSG = "static/fonts/Quicksand.ttf"

# Theme
theme = {
    "backgrounds": [(255, 240, 245), (240, 255, 250), (245, 240, 255), (255, 250, 240)],
    "text": (40, 30, 60),
    "bubble": (255, 255, 255, 240),
    "overlay_icons": ["heart.png", "sparkle.png", "gradcap.png", "diploma.png", "sparkle2.png", "heart2.png", "books.png", "gradcap2.png"]
}

# Fonts
font_title = ImageFont.truetype(FONT_NAME, 32) if Path(FONT_NAME).exists() else ImageFont.load_default()
font_sub = ImageFont.truetype(FONT_MSG, 22) if Path(FONT_MSG).exists() else ImageFont.load_default()
font_small = ImageFont.truetype(FONT_MSG, 18)

def display_image(img: Image.Image):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    img = img.resize(screen.get_size())
    mode = img.mode
    data = img.tobytes()
    surface = pygame.image.fromstring(data, img.size, mode)
    screen.blit(surface, (0, 0))
    pygame.display.flip()

def draw_message(msg):
    bg = random.choice(theme["backgrounds"])
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=bg)
    draw = ImageDraw.Draw(img)

    # Icons
    for icon_name in theme["overlay_icons"]:
        icon_path = os.path.join(ICON_FOLDER, icon_name)
        if os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((32, 32))
                x = random.randint(10, DISPLAY_WIDTH - 42)
                y = random.randint(10, DISPLAY_HEIGHT - 42)
                img.paste(icon, (x, y), icon)
            except: continue

    # Polaroid photo
    if msg.get("photo"):
        path = os.path.join(PHOTO_FOLDER, msg["photo"])
        if os.path.exists(path):
            try:
                photo = Image.open(path)
                photo = ImageOps.exif_transpose(photo)
                photo.thumbnail((280, 200))
                polaroid = Image.new("RGB", (photo.width+20, photo.height+50), "white")
                polaroid.paste(photo, (10, 10))
                shadow = Image.new("RGB", (polaroid.width+6, polaroid.height+6), (220,220,220))
                img.paste(shadow, ((DISPLAY_WIDTH-polaroid.width)//2+4, 22))
                img.paste(polaroid, ((DISPLAY_WIDTH-polaroid.width)//2, 20))
            except: pass

    # Message bubble
    text = msg.get("message", "")
    lines = text.split("\n")
    wrapped = []
    for l in lines:
        wrapped += l.split() if len(l) < 40 else [l[i:i+28] for i in range(0, len(l), 28)]

    bubble_h = 16 + len(wrapped) * 26
    bubble_w = DISPLAY_WIDTH - 80
    bubble = Image.new("RGBA", (bubble_w, bubble_h), theme["bubble"])
    draw_bubble = ImageDraw.Draw(bubble)
    for i, line in enumerate(wrapped):
        draw_bubble.text((20, 6 + i * 26), line, font=font_small, fill=theme["text"])
    bubble_x = 40
    bubble_y = DISPLAY_HEIGHT - bubble_h - 30
    img.paste(bubble, (bubble_x, bubble_y), bubble)

    # Name label
    name = f"{msg.get('name', 'Someone')} says:"
    draw.text((bubble_x, bubble_y - 34), name, fill=theme["text"], font=font_sub)


    return img

def draw_splash_screen(photo_path, title_text, subtitle_text, theme):
    from PIL import Image, ImageDraw, ImageFont

    # Pastel background
    bg_color = random.choice(theme["backgrounds"])
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    overlay_icons = theme.get("overlay_icons", [])

    # Overlay icons
    for i, icon_name in enumerate(overlay_icons):
        icon_path = os.path.join(ICON_FOLDER, icon_name)
        if os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon.thumbnail((40, 40))
                for _ in range(3):
                    x = random.randint(10, DISPLAY_WIDTH - 42)
                    y = random.randint(10, DISPLAY_HEIGHT - 42)
                    if not (180 < x < 300 and y < 110):
                        break
                img.paste(icon, (x, y), icon)
            except Exception as e:
                print("Icon error:", e)

    

    # Load and thumbnail the photo
    photo = Image.open(photo_path).convert("RGB")
    photo.thumbnail((280, 200))  # max photo size

    # Create polaroid-style frame
    polaroid_height = photo.height + 50
    polaroid = Image.new("RGB", (photo.width + 20, polaroid_height), "white")
    polaroid.paste(photo, (10, 10))

    # Optional drop shadow
    shadow = Image.new("RGB", (polaroid.width + 6, polaroid_height + 6), (220, 220, 220))
    shadow_x = (DISPLAY_WIDTH - polaroid.width) // 2 + 4
    shadow_y = 20 + 4
    img.paste(shadow, (shadow_x, shadow_y))

    # Paste polaroid centered
    photo_x = (DISPLAY_WIDTH - polaroid.width) // 2
    photo_y = 20
    img.paste(polaroid, (photo_x, photo_y))


    # Fonts
    name_font_path = "static/fonts/Pacifico-Regular.ttf"
    msg_font_path = "static/fonts/Quicksand.ttf"
    font_title = ImageFont.truetype(name_font_path, 32) if os.path.exists(name_font_path) else ImageFont.load_default()
    font_sub = ImageFont.truetype(msg_font_path, 24) if os.path.exists(msg_font_path) else ImageFont.load_default()

    # Text Positions
    text_color = theme["text"]
    

    # Draw title centered
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_w = bbox[2] - bbox[0]
    title_h = bbox[3] - bbox[1]

    draw.text(((DISPLAY_WIDTH - title_w) // 2, 220), title_text, font=font_title, fill=text_color)

    # Draw subtitle
    bbox = draw.textbbox((0, 0), subtitle_text, font=font_sub)
    sub_w = bbox[2] - bbox[0]
    sub_h = bbox[3] - bbox[1]

    draw.text(((DISPLAY_WIDTH - sub_w) // 2, 220 + title_h + 10), subtitle_text, font=font_sub, fill=text_color)

    return img

def load_messages():
    if not os.path.exists(MESSAGE_FILE):
        return []
    with open(MESSAGE_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def main_loop():
    messages = load_messages()
    if not messages:
        print("No messages to display.")
        return

    while True:
        random.shuffle(messages)
        for msg in messages:
            if random.randint(1, 4) == 1:
                img = draw_splash_screen(
                        photo_path="static/uploads/grad-splash.jpg",
                        title_text="Congratulations Hailie!!",
                        subtitle_text="We love you so much!!",
                        theme=theme
                )
            else:
                img = draw_message(msg)
            display_image(img)

if __name__ == "__main__":
    main_loop()
