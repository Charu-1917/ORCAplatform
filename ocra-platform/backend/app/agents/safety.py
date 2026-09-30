import re

# High-priority acute distress indicators (cannot be dismissed by casual safe-context)
ACUTE_DISTRESS_PATTERNS = [
    r"\bsos\b",
    r"\bmayday\b",
    r"\bsinking\b",
    r"\bcapsiz(?:ing|ed)\b",
    r"\bneed emergency\b",
    r"\bneed rescue\b",
    r"\bsend rescue\b",
    r"\bsend help\b",
    r"\bemergency help\b",
]

# Standard maritime hazard and emergency keywords
EMERGENCY_PATTERNS = [
    r"\bdanger\b",
    r"\bcyclone\b",
    r"\bstorm\b",
    r"\bhigh waves?\b",
]

# Regional language emergency terms and phrases
REGIONAL_TRIGGERS = [
    # Tamil
    "அபாயம்",
    "புயல்",
    "உதவி தேவை",
    # Telugu
    "ప్రమాదం",
    "తుఫాను",
    "తుపాను",
    "సహాయం కావాలి",
    # Malayalam
    "അപകടം",
    "ചുഴലിക്കാറ്റ്",
    "സഹായം വേണം",
    # Gujarati
    "ખતરો",
    "વાવાઝોડું",
    "મદદ જોઈએ",
    # Hindi
    "खतरा",
    "तूफान",
    "तूफ़ान",
    "मदद चाहिए",
    "बचाओ",
    # Marathi
    "धोका",
    "वादळ",
    "मदत हवी",
    # Kannada
    "ಅಪಾಯ",
    "ಚಂಡಮಾರುತ",
    "ಸಹಾಯ ಬೇಕು",
    # Bengali
    "বিপদ",
    "ঘূর্ণিঝড়",
    "সাহায্য দরকার",
    "বাঁচাও",
]

# Contextual phrases indicating user is currently safe / not in danger
SAFE_CONTEXT_PATTERNS = [
    r"\bsafe now\b",
    r"\bi am safe\b",
    r"\bwe are safe\b",
    r"\breached safe\b",
    r"\bno danger\b",
    r"\bnot in danger\b",
]


def run_safety_agent(user_message: str) -> dict:
    msg_lower = user_message.lower()

    has_acute = any(re.search(pat, msg_lower) for pat in ACUTE_DISTRESS_PATTERNS)
    has_general_emergency = any(re.search(pat, msg_lower) for pat in EMERGENCY_PATTERNS)
    has_regional_emergency = any(trigger in user_message for trigger in REGIONAL_TRIGGERS)
    has_safe_context = any(re.search(pat, msg_lower) for pat in SAFE_CONTEXT_PATTERNS)
    # "Is there a storm near Chennai?" asks about hazards; it is not a distress report.
    # Real sea-state risk for questions comes from the live sea-alert data instead.
    is_question = user_message.strip().endswith(("?", "？"))
    if is_question:
        has_safe_context = True

    # Acute distress (SOS, sinking, send help) always triggers emergency.
    # General hazard terms (cyclone, storm, danger) trigger emergency unless explicit safe context overrides.
    if has_acute:
        is_emergency = True
    elif (has_general_emergency or has_regional_emergency) and not has_safe_context:
        is_emergency = True
    else:
        is_emergency = False

    if is_emergency:
        return {
            "agent_name": "Safety & Disaster Agent",
            "has_warning": True,
            "warning_text": "High risk detected in area! Severe weather or sea conditions reported.",
            "trigger_peer_call": True,
        }

    return {
        "agent_name": "Safety & Disaster Agent",
        "has_warning": False,
        "warning_text": "Mild wave swell expected in afternoon.",
        "trigger_peer_call": False,
    }
