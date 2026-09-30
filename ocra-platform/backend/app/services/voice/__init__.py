"""
Voice services (text-to-speech) for ORCA's voice assistant.
"""
from app.services.voice.tts import synthesize, VOICES

__all__ = ["synthesize", "VOICES"]
