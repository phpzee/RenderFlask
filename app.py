from flask import Flask, request, send_file, jsonify, Response
from gtts import gTTS
from io import BytesIO
import html, re

app = Flask(__name__)

VOICES = {
    "hi_female_normal": {"lang":"hi","slow":False},
    "hi_female_slow": {"lang":"hi","slow":True},
    "hi_female_cheerful": {"lang":"hi","slow":False},
    "hi_female_calm": {"lang":"hi","slow":False},
    "hi_female_urgent": {"lang":"hi","slow":False},
    "hi_female_soft": {"lang":"hi","slow":False}
}

def process_text_for_anchor(text):
    text = text.strip()
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[।!?]', '', text)
    sentences = re.split(r'(?<=,)|(?<=\.)', text)
    processed = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        s = re.sub(r'(मुख्य|ताज़ा|ब्रेकिंग|विशेष|सूचना)', r'\1 ..', s)
        processed.append(s)
    return " ".join(processed)

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")

@app.route("/preview", methods=["POST"])
def preview():
    try:
        text = request.form.get("text","").strip()
        voice = request.form.get("voice","hi_female_normal")
        speed = float(request.form.get("speed","1.0"))
        pitch = request.form.get("pitch","1.0")   # not used
        volume = request.form.get("volume","1.0") # not used

        if not text:
            return jsonify({"error":"Please enter text."}),400

        voice_settings = VOICES.get(voice, {"lang":"hi","slow":False})
        processed_text = process_text_for_anchor(html.unescape(text))

        # gTTS only supports slow=True/False
        slow_mode = True if speed < 1.0 else voice_settings["slow"]

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=slow_mode)
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
        speed = float(request.form.get("speed","1.0"))
        pitch = request.form.get("pitch","1.0")   # not used
        volume = request.form.get("volume","1.0") # not used

        if not text:
            return "Error: Please enter text.",400

        voice_settings = VOICES.get(voice, {"lang":"hi","slow":False})
        processed_text = process_text_for_anchor(html.unescape(text))
        slow_mode = True if speed < 1.0 else voice_settings["slow"]

        tts_fp = BytesIO()
        tts = gTTS(text=processed_text, lang=voice_settings["lang"], slow=slow_mode)
        tts.write_to_fp(tts_fp)
        tts_fp.seek(0)

        return send_file(tts_fp, mimetype="audio/mpeg",
                         as_attachment=True,
                         download_name="Hindi_News_Anchor.mp3")
    except Exception as e:
        return f"Error: {str(e)}",500

if __name__=="__main__":
    app.run(debug=True)
