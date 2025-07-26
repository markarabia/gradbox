from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os, json, zipfile
from io import BytesIO
from dotenv import load_dotenv

# Load admin PIN from .env
load_dotenv()
ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session security

MESSAGE_FILE = "messages.json"
UPLOAD_FOLDER = "static/uploads"

def load_messages():
    if os.path.exists(MESSAGE_FILE):
        with open(MESSAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_messages(messages):
    with open(MESSAGE_FILE, "w") as f:
        json.dump(messages, f, indent=2)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pin = request.form.get("pin")
        if pin == ADMIN_PIN:
            session["admin"] = True
            return redirect("/admin")
        return "Invalid PIN", 403
    return """
    <form method='POST'>
        <h2>Admin Login</h2>
        <input type='password' name='pin' placeholder='Enter PIN' required>
        <button type='submit'>Login</button>
    </form>
    """

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    raw = load_messages()
    if isinstance(raw, list):
        messages = {i: m for i, m in enumerate(raw)}
    else:
        messages = raw

    return render_template("admin.html", messages=messages)

@app.route("/delete/<int:msg_id>", methods=["POST"])
def delete_message(msg_id):
    if not session.get("admin"):
        return redirect("/login")
    messages = load_messages()
    
    # Handle list-based messages
    if isinstance(messages, list):
        if 0 <= msg_id < len(messages):
            photo = messages[msg_id].get("photo")
            if photo:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, photo))
                except:
                    pass
            del messages[msg_id]

    # Handle dict-based messages (older logic)
    elif isinstance(messages, dict) and str(msg_id) in messages:
        photo = messages[str(msg_id)].get("photo")
        if photo:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, photo))
            except:
                pass
        del messages[str(msg_id)]

    save_messages(messages)
    return redirect("/admin")


@app.route("/export")
def export_messages():
    if not session.get("admin"):
        return redirect("/login")
    return send_file(MESSAGE_FILE, as_attachment=True)

@app.route("/export_images")
def export_images():
    if not session.get("admin"):
        return redirect("/login")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            zipf.write(filepath, arcname=filename)
    zip_buffer.seek(0)
    return send_file(zip_buffer, download_name="uploads.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
