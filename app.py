from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
from io import BytesIO
import html
import re

app = Flask(__name__)

# Female Hindi voices only
VOICES = {
    "hi_female_normal": {"lang":"hi","slow":False},
    "hi_female_slow": {"lang":"hi","slow":True},
    "hi_female_cheerful": {"lang":"hi","slow":False},
    "hi_female_calm": {"lang":"hi","slow":False},
    "hi_female_urgent": {"lang":"hi","slow":False},
    "hi_female_soft": {"lang":"hi","slow":False}
}

# Process text for anchor style
def process_text_for_anchor(text):
    text = text.strip()
    if not text:
        return ""
    # Remove all punctuation for speaking
    text = re.sub(r'[।!?,;:"\'\(\)\[\]\{\}]', '', text)
    sentences = text.split(".")
    processed = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Add anchor emphasis keywords
        s = re.sub(r'(Breaking|Update|Alert|Special|Information|मुख्य|ताज़ा|ब्रेकिंग|विशेष|सूचना)', r'\1 ..', s, flags=re.I)
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
            return jsonify({"error":"Please enter some text."}),400

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
            return "Error: Please enter some text.",400

        voice_settings = VOICES.get(voice, {"lang":"hi","slow":False})
        processed_text = process_text_for_anchor(html.unescape(text))

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=voice_settings["slow"])
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(tts_fp, mimetype="audio/mpeg",
                         as_attachment=True,
                         download_name="news_anchor.mp3")
    except Exception as e:
        return f"Error: {str(e)}",500

if __name__=="__main__":
    app.run(debug=True)
