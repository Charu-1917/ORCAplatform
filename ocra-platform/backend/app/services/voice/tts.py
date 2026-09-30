"""
Text-to-speech for ORCA's voice assistant.

Uses Microsoft Edge's online neural voices (via the `edge-tts` package, no API
key) because browsers on Windows ship no Tamil / most Indian-language voices.
Needs internet. If it fails, the frontend falls back to the browser's voices.
"""

import re
import logging

import edge_tts

logger = logging.getLogger("orca.tts")

VOICES = {
    "en": "en-IN-NeerjaNeural",
    "ta": "ta-IN-PallaviNeural",
    "hi": "hi-IN-SwaraNeural",
    "te": "te-IN-ShrutiNeural",
    "ml": "ml-IN-SobhanaNeural",
    "kn": "kn-IN-SapnaNeural",
    "gu": "gu-IN-DhwaniNeural",
    "mr": "mr-IN-AarohiNeural",
    "bn": "bn-IN-TanishaaNeural",
}

MAX_CHARS = 1500

# Emoji and symbol ranges that should not be read aloud
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")


def clean_for_speech(text: str) -> str:
    text = _EMOJI.sub("", text)
    text = re.sub(r"[*#_`>|]", " ", text)      # stray markdown
    text = re.sub(r"^\s*-\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_CHARS]


async def synthesize(text: str, lang: str = "en") -> bytes:
    """Returns MP3 audio bytes for `text` spoken in `lang`."""
    voice = VOICES.get(lang, VOICES["en"])
    clean = clean_for_speech(text)
    if not clean:
        raise ValueError("Nothing to speak.")
    audio = bytearray()
    async for chunk in edge_tts.Communicate(clean, voice).stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    if not audio:
        raise RuntimeError("TTS service returned no audio.")
    return bytes(audio)
