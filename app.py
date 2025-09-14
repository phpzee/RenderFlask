from flask import Flask, render_template, request, send_file
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# TTS Route
@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = request.form.get("text")
        lang = request.form.get("lang", "hi")  # default Hindi

        if not text.strip():
            return "Error: No text provided", 400

        filename = f"static/{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    # For local testing (Render will override with gunicorn)
    app.run(host="0.0.0.0", port=8000, debug=True)
