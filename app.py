
from flask import Flask, request, redirect, render_template, send_from_directory
import os, json, time
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
MESSAGE_FILE = 'messages.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('form.html')

from PIL import Image, ImageOps

@app.route('/submit', methods=['POST'])
def submit_message():
    name = request.form['name']
    message = request.form['message']
    photo = request.files.get('photo')

    filename = None
    if photo and photo.filename:
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{secure_filename(photo.filename)}"
        photo_path = os.path.join(UPLOAD_FOLDER, filename)

        # ✅ Load, auto-orient, and save
        image = Image.open(photo.stream)
        image = ImageOps.exif_transpose(image)
        image.save(photo_path)

    # New message dictionary
    new_message = {
        "name": name,
        "message": message,
        "photo": filename,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Append to messages.json
    if os.path.exists(MESSAGE_FILE):
        try:
            with open(MESSAGE_FILE, 'r') as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = [existing]
        except Exception:
            existing = []
    else:
        existing = []

    existing.append(new_message)

    with open(MESSAGE_FILE, 'w') as f:
        json.dump(existing, f, indent=2)

    return render_template("thankyou.html")



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(port=5250)
