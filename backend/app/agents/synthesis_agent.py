"""Synthesis Agent.

Aggregates all upstream agent outputs into a single markdown response,
prepares map/chart payloads, and generates the regional-language advisory
text used for the text-to-speech widget.
"""
from __future__ import annotations
from app.data.mock_data import (
    LANGUAGES,
    ADVISORY_TEMPLATES,
    ALERT_LEVEL_LABELS,
    HAZARD_NOTE_TEMPLATES,
)
from app.models import AgentStep

ALERT_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

MARKDOWN_LABELS = {
    "en": {"advisory": "Marine Advisory", "question": "Your question", "answer": "Answer", "status": "Overall Sea Safety Status", "pfz": "Potential Fishing Zones (PFZ)", "safety": "Safety Advisories", "trend": "SST & Chlorophyll-a Trend (7 days)", "no_pfz": "No high-confidence PFZ candidates were found for this window.", "no_hazards": "No active hazards reported."},
    "hi": {"advisory": "समुद्री सलाह", "question": "आपका प्रश्न", "answer": "उत्तर", "status": "समुद्र की कुल सुरक्षा स्थिति", "pfz": "संभावित मत्स्य क्षेत्र (PFZ)", "safety": "सुरक्षा सलाह", "trend": "SST और क्लोरोफिल-a रुझान (7 दिन)", "no_pfz": "इस अवधि के लिए कोई उच्च-विश्वसनीयता PFZ नहीं मिला।", "no_hazards": "कोई सक्रिय खतरा रिपोर्ट नहीं हुआ।"},
    "ta": {"advisory": "கடல் ஆலோசனை", "question": "உங்கள் கேள்வி", "answer": "பதில்", "status": "மொத்த கடல் பாதுகாப்பு நிலை", "pfz": "சாத்தியமான மீன்பிடி மண்டலங்கள் (PFZ)", "safety": "பாதுகாப்பு ஆலோசனைகள்", "trend": "SST மற்றும் குளோரோபில்-a போக்கு (7 நாட்கள்)", "no_pfz": "இந்த காலத்திற்கு அதிக நம்பகத்தன்மையுள்ள PFZ எதுவும் கிடைக்கவில்லை.", "no_hazards": "செயலில் உள்ள அபாயங்கள் எதுவும் தெரிவிக்கப்படவில்லை."},
    "te": {"advisory": "సముద్ర సలహా", "question": "మీ ప్రశ్న", "answer": "సమాధానం", "status": "మొత్తం సముద్ర భద్రత స్థితి", "pfz": "సంభావ్య మత్స్య మండలాలు (PFZ)", "safety": "భద్రతా సలహాలు", "trend": "SST మరియు క్లోరోఫిల్-a ధోరణి (7 రోజులు)", "no_pfz": "ఈ కాలానికి అధిక విశ్వసనీయత కలిగిన PFZ ఏదీ కనుగొనబడలేదు.", "no_hazards": "క్రియాశీల ప్రమాదాలు ఏవీ నివేదించబడలేదు."},
    "ml": {"advisory": "സമുദ്ര ഉപദേശം", "question": "നിങ്ങളുടെ ചോദ്യം", "answer": "ഉത്തരം", "status": "മൊത്തത്തിലുള്ള സമുദ്ര സുരക്ഷാ നില", "pfz": "സാധ്യതയുള്ള മത്സ്യബന്ധന മേഖലകൾ (PFZ)", "safety": "സുരക്ഷാ നിർദേശങ്ങൾ", "trend": "SST, ക്ലോറോഫിൽ-a പ്രവണത (7 ദിവസം)", "no_pfz": "ഈ കാലയളവിൽ ഉയർന്ന വിശ്വാസ്യതയുള്ള PFZ കണ്ടെത്തിയില്ല.", "no_hazards": "സജീവമായ അപകടങ്ങളൊന്നും റിപ്പോർട്ട് ചെയ്തിട്ടില്ല."},
    "bn": {"advisory": "সামুদ্রিক পরামর্শ", "question": "আপনার প্রশ্ন", "answer": "উত্তর", "status": "সামগ্রিক সমুদ্র নিরাপত্তা অবস্থা", "pfz": "সম্ভাব্য মৎস্য অঞ্চল (PFZ)", "safety": "নিরাপত্তা পরামর্শ", "trend": "SST ও ক্লোরোফিল-a প্রবণতা (৭ দিন)", "no_pfz": "এই সময়ের জন্য উচ্চ-নির্ভরযোগ্য PFZ পাওয়া যায়নি।", "no_hazards": "কোনও সক্রিয় বিপদ রিপোর্ট করা হয়নি।"},
    "gu": {"advisory": "દરિયાઈ સલાહ", "question": "તમારો પ્રશ્ન", "answer": "જવાબ", "status": "દરિયાઈ સલામતીની એકંદર સ્થિતિ", "pfz": "સંભવિત મત્સ્ય ઝોન (PFZ)", "safety": "સલામતી સલાહ", "trend": "SST અને ક્લોરોફિલ-a વલણ (7 દિવસ)", "no_pfz": "આ સમયગાળા માટે ઉચ્ચ-વિશ્વસનીય PFZ મળ્યો નથી.", "no_hazards": "કોઈ સક્રિય જોખમ નોંધાયું નથી."},
    "mr": {"advisory": "सागरी सल्ला", "question": "तुमचा प्रश्न", "answer": "उत्तर", "status": "एकूण सागरी सुरक्षितता स्थिती", "pfz": "संभाव्य मासेमारी क्षेत्रे (PFZ)", "safety": "सुरक्षितता सल्ले", "trend": "SST आणि क्लोरोफिल-a कल (७ दिवस)", "no_pfz": "या कालावधीसाठी उच्च-विश्वसनीय PFZ आढळले नाही.", "no_hazards": "कोणताही सक्रिय धोका नोंदवला नाही."},
}

ANSWER_TEMPLATES = {
    "en": {"hazard": "For {location}, the current marine safety status is **{alert}**. The most relevant advisory is **{title}**: {description}", "analytics": "For {location}, the latest readings are **{sst} °C** SST and **{chlorophyll} mg/m³** chlorophyll-a, with a 7-day SST↔Chlorophyll correlation of **{correlation}**.", "pfz": "The strongest nearby PFZ for {location} is **{zone}** at {lat}, {lng}, with a productivity score of **{score}** and depth **{depth} m**.", "no_hazard": "No active marine hazards are reported for {location}.", "no_pfz": "No high-confidence PFZ candidates were found near {location}."},
    "hi": {"hazard": "{location} के लिए वर्तमान समुद्री सुरक्षा स्थिति **{alert}** है। सबसे महत्वपूर्ण सलाह **{title}** है: {description}", "analytics": "{location} के नवीनतम माप में SST **{sst} °C** और क्लोरोफिल-a **{chlorophyll} mg/m³** है। 7-दिन का SST↔क्लोरोफिल सहसंबंध **{correlation}** है।", "pfz": "{location} के पास सबसे मजबूत PFZ **{zone}** है: {lat}, {lng}; उत्पादकता स्कोर **{score}** और गहराई **{depth} m**।", "no_hazard": "{location} के लिए कोई सक्रिय समुद्री खतरा रिपोर्ट नहीं हुआ।", "no_pfz": "{location} के पास कोई उच्च-विश्वसनीय PFZ नहीं मिला।"},
    "ta": {"hazard": "{location} பகுதியில் தற்போதைய கடல் பாதுகாப்பு நிலை **{alert}**. முக்கியமான ஆலோசனை **{title}**: {description}", "analytics": "{location} பகுதியில் சமீபத்திய அளவுகள் SST **{sst} °C**, குளோரோபில்-a **{chlorophyll} mg/m³**. 7 நாள் SST↔குளோரோபில் தொடர்பு **{correlation}**.", "pfz": "{location} அருகிலுள்ள வலுவான PFZ **{zone}**: {lat}, {lng}; உற்பத்தித்திறன் மதிப்பெண் **{score}**, ஆழம் **{depth} m**.", "no_hazard": "{location} பகுதியில் செயல்படும் கடல் அபாயங்கள் எதுவும் தெரிவிக்கப்படவில்லை.", "no_pfz": "{location} அருகில் அதிக நம்பகத்தன்மையுள்ள PFZ எதுவும் கிடைக்கவில்லை."},
    "te": {"hazard": "{location}లో ప్రస్తుత సముద్ర భద్రత స్థితి **{alert}**. ముఖ్యమైన సలహా **{title}**: {description}", "analytics": "{location}లో తాజా కొలతలు SST **{sst} °C**, క్లోరోఫిల్-a **{chlorophyll} mg/m³**. 7 రోజుల SST↔క్లోరోఫిల్ సంబంధం **{correlation}**.", "pfz": "{location} సమీపంలోని బలమైన PFZ **{zone}**: {lat}, {lng}; ఉత్పాదకత స్కోర్ **{score}**, లోతు **{depth} m**.", "no_hazard": "{location}లో క్రియాశీల సముద్ర ప్రమాదాలు ఏవీ నివేదించబడలేదు.", "no_pfz": "{location} సమీపంలో అధిక విశ్వసనీయత కలిగిన PFZ ఏదీ కనుగొనబడలేదు."},
    "ml": {"hazard": "{location}ൽ നിലവിലെ സമുദ്ര സുരക്ഷാ നില **{alert}** ആണ്. പ്രധാന ഉപദേശം **{title}**: {description}", "analytics": "{location}ലെ ഏറ്റവും പുതിയ അളവുകൾ SST **{sst} °C**, ക്ലോറോഫിൽ-a **{chlorophyll} mg/m³** ആണ്. 7 ദിവസത്തെ SST↔ക്ലോറോഫിൽ ബന്ധം **{correlation}** ആണ്.", "pfz": "{location}ന് സമീപമുള്ള മികച്ച PFZ **{zone}** ആണ്: {lat}, {lng}; ഉൽപ്പാദന സ്കോർ **{score}**, ആഴം **{depth} m**.", "no_hazard": "{location}ൽ സജീവമായ സമുദ്ര അപകടങ്ങളൊന്നും റിപ്പോർട്ട് ചെയ്തിട്ടില്ല.", "no_pfz": "{location}ന് സമീപം ഉയർന്ന വിശ്വാസ്യതയുള്ള PFZ കണ്ടെത്തിയില്ല."},
}


def build_markdown(
    query: str,
    language: str,
    location_name: str,
    location_state: str,
    intent: str,
    ranked_zones: list[dict],
    hazards: list[dict],
    alert_level: str,
    correlation: float,
    chart_data: list[dict],
) -> str:
    labels = MARKDOWN_LABELS.get(language, MARKDOWN_LABELS["en"])
    answers = ANSWER_TEMPLATES.get(language, ANSWER_TEMPLATES["en"])
    lines = [f"## {labels['advisory']} — {location_name}, {location_state}"]
    lines.append(f"**{labels['question']}:** {query}")
    lines.append("")
    lines.append(f"### {labels['answer']}")
    if intent == "hazard":
        if hazards:
            hazard = hazards[0]
            lines.append(answers["hazard"].format(
                location=location_name,
                alert=ALERT_LEVEL_LABELS[alert_level].get(language, alert_level.upper()),
                title=hazard["title"],
                description=hazard["description"],
            ))
        else:
            lines.append(answers["no_hazard"].format(location=location_name))
    elif intent == "analytics":
        latest = chart_data[-1]
        lines.append(answers["analytics"].format(
            location=location_name,
            sst=latest["sst"],
            chlorophyll=latest["chlorophyll"],
            correlation=correlation,
        ))
    elif ranked_zones:
        best_zone = ranked_zones[0]
        lines.append(answers["pfz"].format(
            location=location_name,
            zone=best_zone["name"],
            lat=f"{best_zone['lat']:.3f}",
            lng=f"{best_zone['lng']:.3f}",
            score=f"{best_zone['score']:.2f}",
            depth=best_zone["depth_m"],
        ))
    else:
        lines.append(answers["no_pfz"].format(location=location_name))
    lines.append("")
    lines.append(
        f"**{labels['status']}:** {ALERT_EMOJI[alert_level]} "
        f"{ALERT_LEVEL_LABELS[alert_level].get(language, alert_level.upper())}"
    )
    lines.append("")
    lines.append(f"### 🎣 {labels['pfz']}")
    if ranked_zones:
        for z in ranked_zones:
            lines.append(
                f"- **{z['name']}** — {z['lat']:.3f}, {z['lng']:.3f} "
                f"(radius {z['radius_km']} km, depth {z['depth_m']} m, "
                f"productivity score **{z['score']:.2f}**)"
            )
    else:
        lines.append(f"- {labels['no_pfz']}")

    lines.append("")
    lines.append(f"### ⚠️ {labels['safety']}")
    if hazards:
        for h in hazards:
            lines.append(
                f"- {ALERT_EMOJI[h['level']]} **{h['title']}** ({h['region_name']}): "
                f"{h['description']}"
            )
    else:
        lines.append(f"- {labels['no_hazards']}")

    lines.append("")
    lines.append(f"### 🌡️ {labels['trend']}")
    latest = chart_data[-1]
    lines.append(
        f"- Latest SST: **{latest['sst']} °C**, Chlorophyll-a: "
        f"**{latest['chlorophyll']} mg/m³**"
    )
    lines.append(f"- 7-day SST↔Chlorophyll correlation coefficient: **{correlation}**")

    lines.append("")
    lines.append(
        "> ORCA combines simulated ISRO Oceansat-3 / SCATSAT-1 imagery with "
        "INCOIS-style advisory logic. This is a hackathon prototype using mock data."
    )
    return "\n".join(lines)


def build_audio_text(
    language: str,
    location_name: str,
    zone_count: int,
    alert_level: str,
    hazards: list[dict],
) -> str:
    template = ADVISORY_TEMPLATES.get(language, ADVISORY_TEMPLATES["en"])
    alert_label = ALERT_LEVEL_LABELS[alert_level].get(
        language, ALERT_LEVEL_LABELS[alert_level]["en"]
    )
    if hazards:
        note_template = HAZARD_NOTE_TEMPLATES.get(language, HAZARD_NOTE_TEMPLATES["en"])
        top_hazard = hazards[0]
        hazard_note = note_template.format(
            title=top_hazard["title"], description=top_hazard["description"]
        )
    else:
        hazard_note = ""
    return template.format(
        location=location_name,
        zone_count=zone_count,
        alert_level=alert_label,
        hazard_note=hazard_note,
    ).strip()


def run(
    query: str,
    location_name: str,
    location_state: str,
    intent: str,
    language: str,
    ranked_zones: list[dict],
    hazards: list[dict],
    alert_level: str,
    correlation: float,
    chart_data: list[dict],
    deep_reasoning: bool,
) -> tuple[dict, AgentStep]:
    markdown = build_markdown(
        query, language, location_name, location_state, intent, ranked_zones, hazards,
        alert_level, correlation, chart_data,
    )
    audio_text = build_audio_text(language, location_name, len(ranked_zones), alert_level, hazards)

    detail_lines = [
        f"Composed markdown advisory ({len(markdown)} chars) covering PFZ, safety "
        "and environmental sections.",
        f"Translated spoken advisory into **{LANGUAGES[language]}** for the TTS widget.",
    ]
    if deep_reasoning:
        detail_lines.append(
            "Applied template-based neural-machine-translation simulation with "
            "domain-specific marine vocabulary substitution for regional dialects."
        )

    step = AgentStep(
        agent="Synthesis & Translation Agent",
        icon="sparkles",
        status="done",
        summary=f"Generated final advisory in {LANGUAGES[language]}",
        detail="\n\n".join(detail_lines),
        duration_ms=210 if deep_reasoning else 140,
    )
    context = {"markdown": markdown, "audio_text": audio_text}
    return context, step
