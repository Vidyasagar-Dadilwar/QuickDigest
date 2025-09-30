from gtts import gTTS
import os
from pathlib import Path
import uuid

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def text_to_speech(text: str, lang: str = "en"):
    filename = f"{uuid.uuid4().hex}.mp3"
    path = OUTPUT_DIR / filename
    tts = gTTS(text=text, lang=lang)
    tts.save(str(path))
    return str(path)