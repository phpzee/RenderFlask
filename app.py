from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
import os
import time

app = Flask(__name__)

OUTPUT_DIR = "static/tts_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        lang = data.get("lang", "hi")

        if not text:
            return jsonify({"error": "Please enter some text!"}), 400

        # unique filename
        filename = f"tts_{int(time.time())}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)

        return jsonify({
            "success": True,
            "file_url": f"/{filepath}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
