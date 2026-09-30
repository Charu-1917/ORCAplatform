"""
Marine news headlines for Indian fishermen and coastal communities.

Pulls real headlines from the public Google News RSS search feed (no key).
Headlines link to the original publisher's article.
"""

import re
import time
import logging
import threading
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import Dict, Any

import requests

logger = logging.getLogger("orca.news")

RSS_URL = "https://news.google.com/rss/search"

QUERIES = {
    "en": {
        "q": '(fishermen OR "sea warning" OR cyclone OR INCOIS OR "high waves" OR "coast guard" OR "Bay of Bengal" OR "Arabian Sea") India when:7d',
        "hl": "en-IN", "gl": "IN", "ceid": "IN:en",
    },
    "ta": {
        "q": '(மீனவர்கள் OR "புயல் எச்சரிக்கை" OR "புயல் சின்னம்" OR "கடல் சீற்றம்" OR மீன்பிடி OR "கடலோர காவல்" OR "காற்றழுத்த தாழ்வு") when:7d',
        "hl": "ta", "gl": "IN", "ceid": "IN:ta",
    },
}

CACHE_SECONDS = 1800
MAX_ITEMS = 20
_cache: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def _words(title: str) -> set:
    return {w for w in re.findall(r"\w+", title.lower()) if len(w) > 2}


def _dedupe_stories(items: list) -> list:
    """Keeps one headline per story: many outlets publish the same event with similar titles."""
    kept, kept_words = [], []
    for item in items:
        words = _words(item["title"])
        duplicate = any(
            words and other and len(words & other) / min(len(words), len(other)) >= 0.5
            for other in kept_words
        )
        if not duplicate:
            kept.append(item)
            kept_words.append(words)
    return kept


def _fetch(lang: str) -> Dict[str, Any]:
    params = QUERIES[lang]
    resp = requests.get(RSS_URL, params=params, timeout=15, headers={"User-Agent": "Mozilla/5.0 (ORCA Ocean Intelligence)"})
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source_el = item.find("source")
        source = source_el.text.strip() if source_el is not None and source_el.text else ""
        # Google News titles end with " - Publisher"; keep the publisher separately
        if source and title.endswith(f" - {source}"):
            title = title[: -len(f" - {source}")]
        published = None
        try:
            published = parsedate_to_datetime(item.findtext("pubDate")).isoformat()
        except Exception:
            pass
        if title and link.startswith("http"):
            items.append({"title": title, "link": link, "source": source, "published": published})

    items.sort(key=lambda x: x["published"] or "", reverse=True)
    items = _dedupe_stories(items)
    return {
        "status": "success",
        "language": lang,
        "source": "Google News RSS (public headlines, links to original publishers)",
        "items": items[:MAX_ITEMS],
    }


def get_marine_news(lang: str = "en") -> Dict[str, Any]:
    lang = lang if lang in QUERIES else "en"
    with _lock:
        cached = _cache.get(lang)
        if cached and time.time() - cached["at"] < CACHE_SECONDS:
            return cached["data"]
        try:
            data = _fetch(lang)
            _cache[lang] = {"at": time.time(), "data": data}
            return data
        except Exception as exc:
            logger.warning(f"News fetch failed ({lang}): {exc}")
            if cached:
                return {**cached["data"], "stale": True}
            return {"status": "error", "language": lang, "error": f"News feed unavailable: {exc}", "items": []}
