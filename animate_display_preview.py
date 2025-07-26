
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import time, json, os
from show_messages import draw_message
import random

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320
MESSAGE_FILE = "messages.json"
SPLASH_DURATION = 3  # seconds
DISPLAY_DURATION = 5  # seconds
ICON_FOLDER = "static/icons/"

# Define theme (same as draw_message uses)
theme = {
    "backgrounds": [(255, 240, 245), (240, 255, 250), (245, 240, 255), (255, 250, 240)],
    "text": (40, 30, 60),
    "bubble": (255, 255, 255, 240),
    "overlay_icons": ["heart.png", "sparkle.png", "gradcap.png", "diploma.png", "sparkle2.png", "heart2.png", "books.png", "gradcap2.png"]
    
}




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



def fade_transition(display_func, frames=10, delay=0.05):
    for i in range(frames):
        alpha = i / frames
        img = display_func()
        enhancer = ImageEnhance.Brightness(img)
        faded = enhancer.enhance(alpha)
        faded.show()
        time.sleep(delay)

def main_loop():
    # Load messages
    if not os.path.exists(MESSAGE_FILE):
        print(f"Message file {MESSAGE_FILE} not found.")
        return

    with open(MESSAGE_FILE, "r") as f:
        messages = json.load(f)

    if not messages:
        print("No messages to display.")
        return

 
    splash = draw_splash_screen(
        photo_path="static/uploads/grad-splash.jpg",
        title_text="Congratulations Hailie!!",
        subtitle_text="We love you so much!!",
        theme=theme
    )
    fade_transition(lambda: splash)
    splash.show()
    time.sleep(SPLASH_DURATION)



    index = 0
    while True:
        msg = messages[index % len(messages)]

        def display_current():
            return draw_message(msg)

        fade_transition(display_current)  # fade in
        img = display_current()
        img.show(title="GradBox Display"); time.sleep(0.1)
        time.sleep(DISPLAY_DURATION)

        index += 1

if __name__ == "__main__":
    main_loop()
