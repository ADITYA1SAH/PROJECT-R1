"""
Internet Search Module for PROJECT R1
Phase 5 — Web search capability
"""

import requests
import json
import re
from modules.llm.llm import generate_response
from modules.internet.browser_search import search_duckduckgo
from modules.internet.searxng_search import searxng_search

# Try to use PyEnchant (real dictionary) first
try:
    import enchant
    ENGLISH_DICT = enchant.Dict("en_US")
    DICT_AVAILABLE = True
    print("✅ PyEnchant loaded — using real English dictionary")
except ImportError:
    DICT_AVAILABLE = False
    print("⚠️ PyEnchant not installed. Install with: pip install pyenchant")
    try:
        from spellchecker import SpellChecker
        spell = SpellChecker()
        SPELL_CHECK_AVAILABLE = True
        print("⚠️ Using pyspellchecker as fallback")
    except ImportError:
        SPELL_CHECK_AVAILABLE = False
        print("⚠️ SpellChecker not installed. Install with: pip install pyspellchecker")

# Simple cache to avoid repeated searches
_search_cache = {}

# DuckDuckGo's API (free, no API key required)
SEARCH_URL = "https://api.duckduckgo.com/"


def get_weather(city):
    """Get current weather using wttr.in (free, no API key) — short format."""
    try:
        original_city = city.strip()
        city_encoded = original_city.replace(" ", "%20")
        url = f"https://wttr.in/{city_encoded}?format=%C+%t"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather_text = response.text.strip()
            # Check if wttr.in returned a valid response (not an error)
            if weather_text and "Unknown location" not in weather_text and "Sorry" not in weather_text:
                return f"Weather in {original_city}: {weather_text}."
        
        # Retry with country hint if city not found
        city_with_country = f"{original_city},India"
        city_encoded = city_with_country.replace(" ", "%20").replace(",", "%2C")
        url = f"https://wttr.in/{city_encoded}?format=%C+%t"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather_text = response.text.strip()
            if weather_text and "Unknown location" not in weather_text and "Sorry" not in weather_text:
                return f"Weather in {original_city}: {weather_text}."
        
        return None
    except:
        return None


def correct_spelling(query):
    """Correct spelling errors using PyEnchant (real dictionary)."""
    if DICT_AVAILABLE:
        words = query.split()
        corrected = []
        for word in words:
            if len(word) > 2:
                if ENGLISH_DICT.check(word):
                    corrected.append(word)
                else:
                    suggestions = ENGLISH_DICT.suggest(word)
                    if suggestions:
                        corrected.append(suggestions[0])
                    else:
                        corrected.append(word)
            else:
                corrected.append(word)
        return " ".join(corrected)
    
    elif SPELL_CHECK_AVAILABLE:
        words = query.split()
        corrected = []
        for word in words:
            if len(word) > 2:
                if word in spell.unknown([word]):
                    correction = spell.correction(word)
                    if correction:
                        corrected.append(correction)
                    else:
                        corrected.append(word)
                else:
                    corrected.append(word)
            else:
                corrected.append(word)
        return " ".join(corrected)
    
    return query


def search(query):
    """Search the web and return a short, direct answer."""
    # Check cache first
    if query in _search_cache:
        return _search_cache[query]

    # Don't spellcheck weather queries (city names aren't in dictionary)
    if "weather" not in query.lower() and "temperature" not in query.lower():
        query = correct_spelling(query)

    # =========================
    # WEATHER QUERIES
    # =========================
    if "weather" in query.lower() or "temperature" in query.lower():
        city = query.lower()
        # Remove question words
        for word in ["what is the", "what's the", "whats the", "what is", "whats", "what's",
                     "how is the", "how's the", "hows the", "how is", "hows",
                     "tell me the", "tell me", "give me the", "give me"]:
            city = city.replace(word, "")
        # Remove weather-related words
        for word in ["weather", "temperature", "in", "of", "for", "?", "today"]:
            city = city.replace(word, " ")
        city = " ".join(city.split()).strip()
        
        # If city is empty, try to extract from "in X" pattern
        if not city:
            import re
            match = re.search(r'in\s+([a-z\s]+)', query.lower())
            if match:
                city = match.group(1).strip()
        
        if not city:
            city = "London"
        result = get_weather(city)
        if result:
            _search_cache[query] = result
            return result
        else:
            _search_cache[query] = "I couldn't get the weather for that location."
            return _search_cache[query]

    # =========================
    # CALENDAR / FESTIVAL QUERIES
    # =========================
    if any(keyword in query.lower() for keyword in ["diwali", "holiday", "festival", "when is", "date of"]):
        result = search_duckduckgo(query)
        _search_cache[query] = result
        return result

    # =========================
    # GENERAL KNOWLEDGE — SearXNG FIRST (best results)
    # =========================
    try:
        searxng_result = searxng_search(query)
        if searxng_result:
            _search_cache[query] = searxng_result
            return searxng_result
    except Exception:
        pass

    # =========================
    # FALLBACK — DuckDuckGo HTML
    # =========================
    try:
        result = search_duckduckgo(query)
        if result and "No results found" not in result and "Search error" not in result:
            _search_cache[query] = result
            return result
    except Exception:
        pass

    # =========================
    # FALLBACK — DuckDuckGo API
    # =========================
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
        data = response.json()

        raw_result = None
        if data.get("Answer"):
            raw_result = data["Answer"]
        elif data.get("Abstract"):
            raw_result = data["Abstract"]
        elif data.get("Definition"):
            raw_result = data["Definition"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if "Text" in topic:
                    raw_result = topic["Text"]
                    break

        if not raw_result:
            raw_result = search_wikipedia(query)

        if raw_result:
            if len(raw_result.split(".")) == 1:
                _search_cache[query] = raw_result
                return raw_result
            first_sentence = raw_result.split(".")[0] + "."
            _search_cache[query] = first_sentence
            return first_sentence

        result = f"I searched for '{query}' but couldn't find a clear answer. Try rephrasing your question."
        _search_cache[query] = result
        return result

    except requests.Timeout:
        error_msg = "The search is taking too long. Please try again later."
        _search_cache[query] = error_msg
        return error_msg
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        _search_cache[query] = error_msg
        return error_msg


def search_wikipedia(query):
    """Fallback search using Wikipedia search API."""
    try:
        headers = {
            "User-Agent": "PROJECT R1/1.0 (https://github.com/your-repo; aditya@example.com)"
        }

        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        data = response.json()

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return None

        page_title = search_results[0]["title"]

        summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        response = requests.get(summary_url + page_title.replace(" ", "_"), headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()

            if data.get("extract"):
                extract = data["extract"]
                first_sentence = extract.split(".")[0] + "."
                return first_sentence
            
        return None
    except Exception as e:
        return None


def is_available():
    """Check if internet search is available."""
    try:
        # Check SearXNG first
        response = requests.get("http://localhost:8080", timeout=3)
        if response.status_code == 200:
            return True
        # Fallback to DuckDuckGo
        response = requests.get("https://duckduckgo.com", timeout=3)
        return response.status_code == 200
    except:
        return False