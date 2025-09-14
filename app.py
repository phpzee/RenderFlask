from flask import Flask, render_template, request, send_file, jsonify
from gtts import gTTS
from pydub import AudioSegment, effects
from io import BytesIO
import html
import re
import os

app = Flask(__name__)

# Background studio audio (looped)
BACKGROUND_AUDIO = "static/studio_bg.mp3"

# Multi-voice mapping
VOICES = {
    "hi_female_normal": {"lang":"hi","slow":False},
    "hi_female_slow": {"lang":"hi","slow":True},
    "hi_male_normal": {"lang":"hi-in","slow":False},
    "hi_male_slow": {"lang":"hi-in","slow":True}
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

def apply_studio_effects(tts_audio_fp):
    """
    Normalize, apply simple echo/reverb, and overlay background
    """
    try:
        tts_audio = AudioSegment.from_file(tts_audio_fp, format="mp3")
        tts_audio = effects.normalize(tts_audio)
        # Simulated echo: overlay delayed copy at low volume
        echo = tts_audio - 12
        echo = echo.fade_in(50).fade_out(50)
        combined = tts_audio.overlay(echo, delay=100)
        # Add background if exists
        if os.path.exists(BACKGROUND_AUDIO):
            bg_audio = AudioSegment.from_file(BACKGROUND_AUDIO, format="mp3")
            bg_audio = bg_audio * ((len(combined)//len(bg_audio))+1)
            bg_audio = bg_audio[:len(combined)] - 18
            combined = combined.overlay(bg_audio)
        out_fp = BytesIO()
        combined.export(out_fp, format="mp3")
        out_fp.seek(0)
        return out_fp
    except Exception as e:
        tts_audio_fp.seek(0)
        return tts_audio_fp

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

        final_audio = apply_studio_effects(tts_fp)
        return send_file(final_audio, mimetype="audio/mpeg")
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

        final_audio = apply_studio_effects(tts_fp)
        return send_file(final_audio, mimetype="audio/mpeg",
                         as_attachment=True,
                         download_name="ultimate_tv_news_anchor.mp3")
    except Exception as e:
        return f"त्रुटि: {str(e)}",500

if __name__=="__main__":
    app.run(debug=True)
