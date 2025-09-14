from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
from io import BytesIO
import html
import re

app = Flask(__name__)

# Only female Hindi voices
VOICES = {
    "hi_female_normal": {"lang": "hi", "slow": False},
    "hi_female_slow": {"lang": "hi", "slow": True},
    "hi_female_cheerful": {"lang": "hi", "slow": False},
    "hi_female_calm": {"lang": "hi", "slow": False},
    "hi_female_urgent": {"lang": "hi", "slow": False},
    "hi_female_soft": {"lang": "hi", "slow": False}
}

# Keywords for emphasis
KEYWORDS = ["Breaking", "Exclusive", "Update", "Alert", "News", "Report"]

def process_text_for_anchor(text):
    """
    Anchor-style text processing:
    - Ignores punctuation when reading
    - Adds emphasis on keywords
    - Natural pause after sentences
    """
    text = html.unescape(text.strip())
    if not text:
        return ""
    # Replace punctuation with period for splitting
    text_clean = re.sub(r"[।!?]", ".", text)
    sentences = [s.strip() for s in text_clean.split(".") if s.strip()]
    processed = []
    for s in sentences:
        # Add emphasis to keywords
        for kw in KEYWORDS:
            s = re.sub(fr"\b{kw}\b", f"{kw} ...", s, flags=re.IGNORECASE)
        processed.append(s)
    return " . ".join(processed)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/preview", methods=["POST"])
def preview():
    try:
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "hi_female_normal")
        if not text:
            return jsonify({"error": "Please enter text."}), 400

        processed_text = process_text_for_anchor(text)
        voice_settings = VOICES.get(voice, {"lang": "hi", "slow": False})

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=voice_settings["slow"])
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(tts_fp, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/convert", methods=["POST"])
def convert():
    try:
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "hi_female_normal")
        if not text:
            return "Error: Please enter text.", 400

        processed_text = process_text_for_anchor(text)
        voice_settings = VOICES.get(voice, {"lang": "hi", "slow": False})

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=voice_settings["slow"])
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(
            tts_fp,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="Hindi_News_Anchor.mp3"
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
