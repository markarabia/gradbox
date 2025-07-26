from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        photo_file = request.files.get("photo")

        photo_filename = ""
        if photo_file and photo_file.filename:
            safe_name = secure_filename(photo_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            photo_filename = f"{timestamp}_{safe_name}"
            photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        new_entry = {
            "name": name,
            "message": message,
            "photo": photo_filename,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open("messages.json", "a") as f:
            f.write(json.dumps(new_entry) + "\n")

        return redirect("/thanks")

    return render_template("form.html")

@app.route("/thanks")
def thanks():
    return "<h1>Thanks for your message! 🎓</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5250)