from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
from io import BytesIO
import html
import re

app = Flask(__name__)

# Female-only voice mapping (multi-style)
VOICES = {
    "hi_female_normal": {"lang":"hi","slow":False},
    "hi_female_slow": {"lang":"hi","slow":True},
    "hi_female_cheerful": {"lang":"hi","slow":False},
    "hi_female_calm": {"lang":"hi","slow":False},
    "hi_female_urgent": {"lang":"hi","slow":False},
    "hi_female_soft": {"lang":"hi","slow":False}
}

def process_text_for_anchor(text):
    """Anchor-style emphasis, sentence-wise modulation"""
    text = text.strip()
    if not text:
        return ""
    text = re.sub(r'[।!?]', '.', text)
    sentences = text.split(".")
    processed = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Emphasize keywords
        s = re.sub(r'(मुख्य|ताज़ा|ब्रेकिंग|विशेष|सूचना)', r'\1 ..', s)
        processed.append(s)
    return " . ".join(processed)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/preview", methods=["POST"])
def preview():
    try:
        text = request.form.get("text","").strip()
        voice = request.form.get("voice","hi_female_normal")
        if not text:
            return jsonify({"error":"कृपया टेक्स्ट डालें।"}),400

        voice_settings = VOICES.get(voice, {"lang":"hi","slow":False})
        processed_text = process_text_for_anchor(html.unescape(text))

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=voice_settings["slow"])
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(tts_fp, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/convert", methods=["POST"])
def convert():
    try:
        text = request.form.get("text","").strip()
        voice = request.form.get("voice","hi_female_normal")
        if not text:
            return "त्रुटि: कृपया टेक्स्ट डालें।",400

        voice_settings = VOICES.get(voice, {"lang":"hi","slow":False})
        processed_text = process_text_for_anchor(html.unescape(text))

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=voice_settings["slow"])
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(tts_fp, mimetype="audio/mpeg",
                         as_attachment=True,
                         download_name="ultimate_tv_news_anchor.mp3")
    except Exception as e:
        return f"त्रुटि: {str(e)}",500

if __name__=="__main__":
    app.run(debug=True)
