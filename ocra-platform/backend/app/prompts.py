# app/prompts.py
from typing import Dict, List

LANGUAGE_NAMES = {
    "en": "simple English",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "ml": "Malayalam (മലയാളം)",
    "gu": "Gujarati (ગુજરાતી)",
    "hi": "Hindi (हिन्दी)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
}

FISHERMAN_SYSTEM_PROMPT = """
You are ORCA, an AI assistant for ISRO providing real-time ocean intelligence to Indian marine stakeholders.

Rules:
1. Speak in simple, practical, fisherman-friendly language. Avoid complex scientific jargon.
2. Provide concise actionable advice regarding safety, weather, route, and potential fishing zones.
3. Base every number you mention ONLY on the "Live Agent Data" given with the question. Never invent measurements.
   Prefer the live observed Weather / Satellite values; treat SciDL values as model estimates and say so if you use them.
   If a value is missing or marked as offline fallback, say that the live data is unavailable.
   Copy every number with exactly the unit it has in the data (m, m/s, km/h, °C, mg/m3). Never convert or change units.
   Do not describe wind or waves as "strong" or "high" unless the data values show it.
4. Write plain text only: no markdown, no asterisks, no '#' headings, no tables. Short paragraphs or simple '-' lines are fine.
5. Keep the answer under about 150 words unless the user asks for more detail.
6. CRITICAL: You must answer in the requested language specified with each question:
   - If language is 'ta', reply strictly in Tamil (தமிழ்).
   - If language is 'te', reply strictly in Telugu (తెలుగు).
   - If language is 'ml', reply strictly in Malayalam (മലയാളം).
   - If language is 'gu', reply strictly in Gujarati (ગુજરાતી).
   - If language is 'hi', reply strictly in Hindi (हिन्दी).
   - If language is 'kn', reply strictly in Kannada (ಕನ್ನಡ).
   - If language is 'mr', reply strictly in Marathi (मराठी).
   - If language is 'bn', reply strictly in Bengali (বাংলা).
   - If language is 'en' or unknown, reply in simple English.
7. If the Safety Status indicates high risk or the Emergency Flag is true, start by instructing the fisherman
   to seek shelter or return to shore immediately, and advise contacting the Coast Guard (dial 1554) if in distress.
"""


def build_agent_context(
    user_message: str,
    target_language: str,
    lat,
    lon,
    sat_info: str,
    weather_info: str,
    scidl_info: str,
    routing_info: str,
    safety_warning: str,
    has_warning: bool,
    wind_speed_ms=None,
    location_name: str = None,
    alert_info: str = None,
    voice: bool = False,
) -> str:
    """
    Wraps the user's question with live agent telemetry for the current turn.
    """
    location = f"{lat}° N, {lon}° E" if lat is not None and lon is not None else "not provided"
    if location_name:
        location = f"offshore {location_name} ({location})"
    lang_name = LANGUAGE_NAMES.get(target_language, "simple English")
    # Pre-converted so the small local model never has to convert units itself
    wind_line = ""
    if wind_speed_ms is not None:
        wind_line = (f"\n- Wind speed (SciDL model estimate): {wind_speed_ms} m/s = "
                     f"{round(wind_speed_ms * 3.6, 1)} km/h = {round(wind_speed_ms * 1.944, 1)} knots")
    voice_rule = ""
    if voice:
        # The reply is read aloud by text-to-speech, so it must sound natural when spoken
        voice_rule = (f"\nVOICE MODE: this answer will be SPOKEN aloud. Answer in 2 to 4 short, natural sentences in {lang_name}. "
                      "No lists, no symbols, no brackets, no coordinates. Say units as words (metres, kilometres per hour, degrees). "
                      "Give only the most important facts and one clear safety advice.")
    return f"""Live Agent Data (location {location}):
- Weather (live observed; "wave" = total wave height, "swell" and "wind wave" are its parts, NOT wind speed): {weather_info}
- Satellite (live observed): {sat_info}
- Live wind & 24 h coastal sea alert (Open-Meteo forecast, use this for wind and safety): {alert_info or 'not available for this location'}
- SciDL model estimate: {scidl_info}{wind_line}
- Route: {routing_info}
- Safety Status: {safety_warning or 'No hazard keywords detected.'} (Emergency Flag: {has_warning})

Target Output Language Code: {target_language} -> reply in {lang_name}.{voice_rule}

User Question: {user_message}"""


def build_chat_messages(history: List[Dict[str, str]], context_block: str) -> List[Dict[str, str]]:
    """
    Builds the Ollama /api/chat message list: system rules, recent conversation, current turn.
    Past turns are kept without their telemetry to save context window on small local models.
    """
    messages = [{"role": "system", "content": FISHERMAN_SYSTEM_PROMPT.strip()}]
    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})
    messages.append({"role": "user", "content": context_block})
    return messages
