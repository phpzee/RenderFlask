from flask import Flask, render_template, request, send_file
from gtts import gTTS
import os
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        text = request.form["text"]
        language = request.form["language"]
        speed = request.form["speed"]

        slow_audio = True if speed == "slow" else False
        tts = gTTS(text=text, lang=language, slow=slow_audio)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        audio_file = f"static/audio_{timestamp}.mp3"
        tts.save(audio_file)

    return render_template("index.html", audio_file=audio_file)

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join("static", filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
