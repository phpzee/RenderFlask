from flask import Flask, render_template, request, send_file
from gtts import gTTS
import os
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    try:
        text = request.form["text"]
        lang = request.form.get("lang", "hi")
        if not text.strip():
            return "Error: Text is empty", 400

        tts = gTTS(text=text, lang=lang, slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return send_file(
            mp3_fp,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="output.mp3"
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
